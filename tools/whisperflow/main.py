"""main.py — WhisperFlow daemon entrypoint.

S0: instance lock (AD-6) + config load + logging.
S1: push-to-talk hotkey (AD-7) wired to recorder.py + feedback.py.
S2: transcriber.py (faster-whisper, loaded once at boot) plugged in —
    release -> transcribe -> log text + latency.
S3: paster.py plugged in — transcribed text is pasted at the cursor
    (AD-5); empty transcription (silence) pastes nothing (AD-7).

Hotkey detection note (S1 implementation detail, not an architecture
change — AD-4 still says use the `keyboard` lib): `keyboard.is_pressed()`
turned out unreliable in this environment for extended keys (ctrl,
windows) — its internal scan-code name-resolution doesn't match the
scan codes reported for those keys, so it always read False even while
the key was demonstrably down. `keyboard.hook()`'s raw down/up event
stream IS reliable (verified against both raw WinAPI keybd_event and the
library's own send functions). So combo hold/release is tracked from the
hook's event stream into a small held-keys set, polled by the main loop
— hook callback stays cheap (just set add/discard), all the heavyweight
work (recording, beeps) happens in the polling loop, not the callback.
"""

from __future__ import annotations

import socket
import sys
import threading
import time
from datetime import datetime
from typing import Optional

import keyboard

import config as cfg
import feedback
import paster
import recorder as recorder_mod
from transcriber import Transcriber

INSTANCE_LOCK_PORT = 52700
TAP_THRESHOLD_SECONDS = 0.3


def acquire_instance_lock() -> Optional[socket.socket]:
    """AD-6 — exclusive bind on 127.0.0.1:52700.

    Returns the bound+listening socket (caller must keep a reference alive
    for the whole process lifetime — closing/GC'ing it releases the lock),
    or None if the port is already taken by another WhisperFlow instance.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", INSTANCE_LOCK_PORT))
        sock.listen(1)
    except OSError:
        sock.close()
        return None
    return sock


def parse_hotkey(hotkey: str) -> set:
    return {k.strip().lower() for k in hotkey.split("+") if k.strip()}


class HeldKeysTracker:
    """Tracks currently-held keys via keyboard.hook(), normalized so
    'left ctrl'/'right ctrl' both collapse to 'ctrl' (same for windows/alt/
    shift). Thread-safe; the hook callback only touches a set — cheap, so
    it won't stall the low-level hook."""

    def __init__(self) -> None:
        self._pressed: set = set()
        self._lock = threading.Lock()

    @staticmethod
    def _normalize(name: str) -> str:
        name = name.lower()
        for prefix in ("left ", "right "):
            if name.startswith(prefix):
                return name[len(prefix):]
        return name

    def _on_event(self, event) -> None:
        name = self._normalize(event.name or "")
        with self._lock:
            if event.event_type == "down":
                self._pressed.add(name)
            elif event.event_type == "up":
                self._pressed.discard(name)

    def start(self) -> None:
        keyboard.hook(self._on_event)

    def combo_down(self, required: set) -> bool:
        with self._lock:
            return required <= self._pressed


def _save_debug_wav(audio, config: dict, logger) -> None:
    if not config.get("debug_save_wav"):
        return
    if len(audio) == 0:
        logger.info("buffer vazio, nada salvo em debug")
        return
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    path = cfg.get_debug_dir() / f"rec-{ts}.wav"
    recorder_mod.save_wav(path, audio)
    logger.info(
        "debug wav salvo em %s (%d amostras, %.2fs)",
        path, len(audio), len(audio) / recorder_mod.SAMPLE_RATE,
    )


def _transcribe_and_paste(audio, transcriber: Transcriber, config: dict, logger) -> str:
    """S2+S3: soltar tecla -> transcrever -> log do texto + latencia medida
    -> colar no cursor (AD-5). Texto vazio/silencio (AD-7) nao cola nada."""
    if len(audio) == 0:
        logger.info("buffer vazio, nada para transcrever")
        return ""
    try:
        t0 = time.time()
        text = transcriber.transcribe(audio)
        elapsed = time.time() - t0
        if text:
            logger.info("transcricao (%.2fs): %s", elapsed, text)
        else:
            logger.info("transcricao (%.2fs): <vazio/silencio>", elapsed)
    except Exception:
        # AD-10: a transcription failure must not take the daemon down.
        logger.exception("erro ao transcrever")
        feedback.beep_error(config.get("beeps", True))
        return ""

    if not text:
        return ""  # AD-7: silence/no speech -> neutral no-op, nothing pasted

    try:
        paster.paste(text, mode=config.get("paste_mode", "clipboard"))
        logger.info("texto colado no cursor (mode=%s)", config.get("paste_mode", "clipboard"))
    except Exception:
        # AD-10: a paste failure must not take the daemon down either.
        logger.exception("erro ao colar no cursor")
        feedback.beep_error(config.get("beeps", True))

    return text


def run_hotkey_loop(
    config: dict, logger, tracker: HeldKeysTracker, transcriber: Transcriber
) -> None:
    """Push-to-talk main loop (AD-7):
    - hold >= 300ms: beep start -> record -> (release) beep stop -> transcribe -> log
    - tap  < 300ms: discarded silently, no beep
    - held >= max_seconds: auto-stops itself, beep double (stuck-key protection) -> transcribe -> log
    - mic unavailable at press time: beep triple, daemon keeps listening
    """
    required = parse_hotkey(config["hotkey"])
    max_seconds = config["max_seconds"]
    beeps_enabled = config["beeps"]

    rec = recorder_mod.Recorder(max_seconds=max_seconds)
    held = False
    press_time: Optional[float] = None
    capped_already_stopped = False

    logger.info("ouvindo hotkey '%s' (segurar para gravar)...", "+".join(sorted(required)))

    while True:
        try:
            down = tracker.combo_down(required)

            if down and not held:
                held = True
                press_time = time.time()
                capped_already_stopped = False
                try:
                    rec.start()
                    feedback.beep_start(beeps_enabled)
                    logger.info("gravacao iniciada")
                except recorder_mod.MicUnavailableError as exc:
                    logger.error("microfone indisponivel: %s", exc)
                    feedback.beep_error(beeps_enabled)
                    held = False  # allow retry on next press attempt

            elif down and held and not capped_already_stopped:
                if rec.is_capped():
                    audio = rec.stop()
                    capped_already_stopped = True
                    feedback.beep_cap(beeps_enabled)
                    logger.info(
                        "gravacao parou sozinha (cap %ss atingido), %d amostras",
                        max_seconds, len(audio),
                    )
                    _save_debug_wav(audio, config, logger)
                    _transcribe_and_paste(audio, transcriber, config, logger)

            elif not down and held:
                held = False
                hold_duration = (time.time() - press_time) if press_time else 0.0
                if capped_already_stopped:
                    pass  # already stopped+beeped when the cap was hit
                elif hold_duration < TAP_THRESHOLD_SECONDS:
                    rec.stop()  # discard silently, no beep (AD-7)
                    logger.info("tap descartado (%.3fs < %.1fs)", hold_duration, TAP_THRESHOLD_SECONDS)
                else:
                    audio = rec.stop()
                    feedback.beep_stop(beeps_enabled)
                    logger.info(
                        "gravacao finalizada (%.2fs seguradas, %d amostras)",
                        hold_duration, len(audio),
                    )
                    _save_debug_wav(audio, config, logger)
                    _transcribe_and_paste(audio, transcriber, config, logger)

            time.sleep(0.02)
        except Exception:
            # AD-10: never let an exception in this loop kill the daemon.
            logger.exception("erro no loop de hotkey")
            feedback.beep_error(beeps_enabled)
            held = False
            time.sleep(0.5)


def main() -> int:
    config = cfg.load_config()
    logger = cfg.setup_logging(console=True)

    lock = acquire_instance_lock()
    if lock is None:
        logger.info("instância já ativa — encerrando em silêncio")
        return 0

    logger.info(
        "daemon iniciado (hotkey=%s, model=%s, language=%s, paste_mode=%s, "
        "max_seconds=%s, beeps=%s)",
        config["hotkey"],
        config["model"],
        config["language"],
        config["paste_mode"],
        config["max_seconds"],
        config["beeps"],
    )

    logger.info("carregando modelo faster-whisper (%s, int8)...", config["model"])
    t0 = time.time()
    transcriber = Transcriber(model_size=config["model"], language=config["language"])
    logger.info("modelo carregado em %.2fs (1x no boot — AD-1)", time.time() - t0)

    tracker = HeldKeysTracker()
    tracker.start()

    try:
        run_hotkey_loop(config, logger, tracker, transcriber)
    except KeyboardInterrupt:
        logger.info("daemon encerrado (Ctrl+C)")
    finally:
        keyboard.unhook_all()
        lock.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
