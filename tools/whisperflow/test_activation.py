"""test_activation.py — activation-mode state machine, with a fake mic.

Runs `run_hotkey_loop` against a stubbed Recorder and key tracker, so the
toggle/auto-stop logic is verifiable without a microphone, without the
network, and without loading a Whisper model.

    .venv/Scripts/python.exe test_activation.py     (also works under pytest)
"""

from __future__ import annotations

import sys
import threading
import time

import numpy as np

sys.path.insert(0, ".")

import main as main_mod
import recorder as recorder_mod


class FakeRecorder:
    """Stands in for recorder.Recorder. `level` is driven by the test."""

    def __init__(self, max_seconds: int = 120):
        self.max_seconds = max_seconds
        self.level = 0.0
        self.capped = False
        self.running = False
        self.starts = 0

    def start(self) -> None:
        self.running = True
        self.starts += 1

    def stop(self) -> np.ndarray:
        self.running = False
        return np.zeros(16000, dtype=np.float32)

    def get_level(self) -> float:
        return self.level

    def is_capped(self) -> bool:
        return self.capped


class FakeTracker:
    """combo_down() reads a flag the test flips to simulate key presses."""

    def __init__(self):
        self.down = False

    def combo_down(self, required) -> bool:
        return self.down

    def tap(self) -> None:
        """One press+release, long enough for the 20ms poll to see it."""
        self.down = True
        time.sleep(0.08)
        self.down = False
        time.sleep(0.08)


def _run(config, tracker, rec, seconds=3.0):
    """Run the loop on a daemon thread; return the list of finished takes."""
    finished = []
    main_mod._transcribe_and_paste = lambda audio, *a, **k: finished.append(len(audio))
    main_mod._save_debug_wav = lambda *a, **k: None
    for name in ("beep_start", "beep_stop", "beep_cap", "beep_error"):
        setattr(main_mod.feedback, name, lambda *a, **k: None)
    recorder_mod.Recorder = lambda max_seconds=120: rec
    main_mod.recorder_mod.Recorder = lambda max_seconds=120: rec

    class Logger:
        def info(self, *a, **k): pass
        def error(self, *a, **k): pass
        def warning(self, *a, **k): pass
        def exception(self, *a, **k): pass

    t = threading.Thread(
        target=main_mod.run_hotkey_loop,
        args=(config, Logger(), tracker, None),
        daemon=True,
    )
    t.start()
    return finished


BASE = {"hotkey": "ctrl+windows", "max_seconds": 120, "beeps": False}


def test_toggle_starts_and_stops_on_two_taps():
    rec, tracker = FakeRecorder(), FakeTracker()
    finished = _run({**BASE, "activation_mode": "toggle"}, tracker, rec)
    time.sleep(0.1)

    tracker.tap()
    assert rec.running, "1o tap deveria iniciar a gravacao"
    assert not finished, "nao deveria ter finalizado ainda"

    tracker.tap()
    time.sleep(0.1)
    assert not rec.running, "2o tap deveria parar a gravacao"
    assert len(finished) == 1, f"esperava 1 take, veio {len(finished)}"
    print("OK  toggle: tap inicia, tap para")


def test_auto_stop_after_silence_but_only_once_speech_happened():
    rec, tracker = FakeRecorder(), FakeTracker()
    finished = _run(
        {**BASE, "activation_mode": "toggle", "auto_stop_silence_ms": 300, "speech_level": 0.015},
        tracker, rec,
    )
    time.sleep(0.1)

    tracker.tap()
    assert rec.running

    # Pensando antes de falar: 1s em silencio NAO pode encerrar a tomada.
    rec.level = 0.001
    time.sleep(1.0)
    assert rec.running, "silencio antes de qualquer fala nao deveria encerrar"
    assert not finished

    # Fala, com uma pausa curta no meio (nao pode cortar).
    rec.level = 0.09
    time.sleep(0.15)
    rec.level = 0.002
    time.sleep(0.15)          # pausa < 300ms
    rec.level = 0.09
    time.sleep(0.15)
    assert rec.running, "pausa curta no meio da fala nao deveria encerrar"

    # Agora cala de vez.
    rec.level = 0.001
    time.sleep(0.65)
    assert not rec.running, "300ms de silencio apos falar deveriam encerrar"
    assert len(finished) == 1, f"esperava 1 take, veio {len(finished)}"
    print("OK  auto-stop: arma so depois da fala, ignora pausa curta")


def test_hold_mode_still_discards_taps():
    rec, tracker = FakeRecorder(), FakeTracker()
    finished = _run({**BASE, "activation_mode": "hold"}, tracker, rec)
    time.sleep(0.1)

    tracker.tap()  # ~80ms, abaixo do limiar de 300ms
    time.sleep(0.1)
    assert not rec.running
    assert not finished, "tap curto deveria ser descartado no modo hold"

    tracker.down = True
    time.sleep(0.45)
    assert rec.running, "segurar deveria gravar"
    tracker.down = False
    time.sleep(0.15)
    assert not rec.running
    assert len(finished) == 1, f"esperava 1 take, veio {len(finished)}"
    print("OK  hold: tap descartado, hold grava (comportamento original)")


if __name__ == "__main__":
    test_toggle_starts_and_stops_on_two_taps()
    test_auto_stop_after_silence_but_only_once_speech_happened()
    test_hold_mode_still_discards_taps()
    print("\n3/3 passaram")
