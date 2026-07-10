"""transcriber.py — faster-whisper resident model (AD-1, AD-2, AD-3).

Loaded exactly once (at daemon boot); transcribe(np_array) is then called
repeatedly with zero reload cost. int8 quantization — this machine is
CPU-only (no NVIDIA GPU), confirmed in ARCHITECTURE.md section 0.
"""

from __future__ import annotations

import os
import time
from typing import Optional

import numpy as np
from faster_whisper import WhisperModel

import config as cfg

# AD-2: induces punctuation in PT-BR output.
INITIAL_PROMPT_PT = "Transcrição em português brasileiro, com pontuação correta."


class Transcriber:
    def __init__(
        self,
        model_size: str = "small",
        language: str = "pt",
        device: str = "cpu",
        compute_type: str = "int8",
        cpu_threads: Optional[int] = None,
    ) -> None:
        self.model_size = model_size
        self.language = language
        # CPU-only target machine (ARCHITECTURE.md sec. 0) — use all logical
        # cores by default instead of CTranslate2's conservative default,
        # since this daemon isn't sharing the CPU with anything heavy during
        # the brief transcription burst.
        if cpu_threads is None:
            cpu_threads = os.cpu_count() or 4
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
            cpu_threads=cpu_threads,
            download_root=str(cfg.get_models_dir()),
        )

    def transcribe(self, audio: np.ndarray) -> str:
        """audio: 1D float32 mono @ 16kHz (recorder.py's native output)."""
        if audio is None or len(audio) == 0:
            return ""
        segments, _info = self.model.transcribe(
            audio,
            language=self.language,
            vad_filter=True,
            initial_prompt=INITIAL_PROMPT_PT,
        )
        return "".join(seg.text for seg in segments).strip()


if __name__ == "__main__":
    # Manual test: python transcriber.py [wav_path] [model_size]
    import sys
    from pathlib import Path

    import recorder as recorder_mod

    wav_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("bench/frase-padrao.wav")
    model_size = sys.argv[2] if len(sys.argv) > 2 else "small"

    audio = recorder_mod.load_wav_as_float32(wav_path)
    print(f"audio: {wav_path} ({len(audio) / recorder_mod.SAMPLE_RATE:.2f}s)")

    print(f"carregando modelo ({model_size}, int8)...")
    t0 = time.time()
    tr = Transcriber(model_size=model_size)
    print(f"modelo carregado em {time.time() - t0:.2f}s")

    t0 = time.time()
    text = tr.transcribe(audio)
    elapsed = time.time() - t0
    print(f"transcricao #1 ({elapsed:.2f}s): {text}")

    # Second call on the *same* Transcriber instance — must NOT reload the model.
    t0 = time.time()
    text2 = tr.transcribe(audio)
    elapsed2 = time.time() - t0
    print(f"transcricao #2 ({elapsed2:.2f}s, sem reload): {text2}")
