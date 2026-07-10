"""recorder.py — push-to-talk audio capture via sounddevice (AD-4, AD-7).

16kHz mono float32 is Whisper's native input format — no ffmpeg, no temp
files, numpy array straight into faster-whisper (AD-2).
"""

from __future__ import annotations

import threading
import time
import wave
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "float32"


class MicUnavailableError(RuntimeError):
    """Raised when the input stream can't be opened (mic absent/busy)."""


class Recorder:
    """One recording session at a time. Not thread-safe across sessions —
    main.py serializes press/release, which matches push-to-talk semantics.
    """

    def __init__(self, max_seconds: int = 120):
        self.max_seconds = max_seconds
        self._frames: list[np.ndarray] = []
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()
        self._start_time: Optional[float] = None
        self._capped = False

    def _callback(self, indata, frames, time_info, status) -> None:
        # status can carry overflow/underflow flags — not fatal, just noise.
        with self._lock:
            self._frames.append(indata.copy())
            if self._start_time is not None:
                elapsed = time.time() - self._start_time
                if elapsed >= self.max_seconds:
                    self._capped = True

    def start(self) -> None:
        """Open the input stream and begin buffering. Raises
        MicUnavailableError if the device can't be opened (AD-7/AD-10:
        caller beeps triple and keeps the daemon alive)."""
        self._frames = []
        self._capped = False
        try:
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                callback=self._callback,
            )
            self._stream.start()
        except Exception as exc:
            self._stream = None
            raise MicUnavailableError(str(exc)) from exc
        self._start_time = time.time()

    def is_capped(self) -> bool:
        with self._lock:
            return self._capped

    def elapsed(self) -> float:
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    def stop(self) -> np.ndarray:
        """Stop capture and return the buffered audio as 1D float32."""
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        with self._lock:
            frames, self._frames = self._frames, []
        self._start_time = None
        if not frames:
            return np.array([], dtype=np.float32)
        audio = np.concatenate(frames, axis=0)
        return audio.reshape(-1).astype(np.float32)


def save_wav(path: Path, audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> None:
    """Write a float32 [-1, 1] mono buffer as a standard 16-bit PCM WAV so
    any player can open it (raw float32 WAV isn't universally supported)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    clipped = np.clip(audio, -1.0, 1.0)
    pcm16 = (clipped * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm16.tobytes())


def load_wav_as_float32(path: Path) -> np.ndarray:
    """Read a 16-bit PCM mono WAV back into the float32 [-1, 1] array shape
    the transcriber expects. Used to feed synthetic/test audio through the
    real pipeline without a live mic session."""
    with wave.open(str(path), "rb") as wf:
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
        sampwidth = wf.getsampwidth()
    if sampwidth != 2:
        raise ValueError(f"expected 16-bit PCM WAV, got sampwidth={sampwidth}")
    pcm16 = np.frombuffer(raw, dtype=np.int16)
    return (pcm16.astype(np.float32) / 32768.0).reshape(-1)


if __name__ == "__main__":
    # Manual test: python recorder.py — records 3s, saves to debug\test.wav
    import config as cfg

    rec = Recorder(max_seconds=10)
    print("gravando 3s...")
    rec.start()
    time.sleep(3)
    audio = rec.stop()
    out = cfg.get_debug_dir() / "test.wav"
    save_wav(out, audio)
    print(f"salvo em {out} ({len(audio)} amostras, {len(audio) / SAMPLE_RATE:.2f}s)")
