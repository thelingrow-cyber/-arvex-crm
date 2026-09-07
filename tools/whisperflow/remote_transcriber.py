"""remote_transcriber.py — optional Groq-hosted Whisper engine with local fallback.

Why this exists: the target machine is a Ryzen 5 3500U with 5.9 GB of RAM and
no CUDA GPU, so the biggest model that fits the latency budget locally is
`base` — which is the weakest Whisper tier and audibly struggles with real
Brazilian-Portuguese speech. Measured on the same 14.4s bench WAV
(2026-09-07):

    base local ............ 2.38s   (weakest quality)
    small local ........... 7.90s   (way over the 3s budget, BENCH.md)
    whisper-large-v3-turbo  0.93s   (best quality, over the network)

The hosted turbo model is both faster AND far more accurate here, because the
bottleneck is this CPU, not the network. So `engine: "groq"` becomes worth it
— at the cost of the audio leaving the machine, which is why it stays opt-in
per config and never becomes the silent default (config.default.json keeps
`"engine": "local"`, preserving the PRD's "R$0, 100% local" promise for
anyone who doesn't opt in).

Drop-in shaped: exposes the same `.transcribe(np.ndarray) -> str` as
`Transcriber`, so main.py's hot path is unchanged. Any remote failure
(no key, offline, timeout, API error) degrades to the local model instead of
raising — dictation must never break because the network did (AD-10).
"""

from __future__ import annotations

import io
import json
import logging
import os
import time
import urllib.error
import urllib.request
import uuid
import wave
from typing import Optional

import numpy as np

from transcriber import Transcriber

API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
DEFAULT_MODEL = "whisper-large-v3-turbo"
TIMEOUT_SECONDS = 15.0
SAMPLE_RATE = 16000


class RemoteUnavailable(RuntimeError):
    """Remote transcription could not run; caller falls back to local."""


def _encode_wav(audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> bytes:
    """float32 [-1,1] mono -> 16-bit PCM WAV bytes, in memory (no temp file)."""
    clipped = np.clip(audio, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype("<i2")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()


def _multipart(fields: dict[str, str], wav: bytes) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    parts = []
    for name, value in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode("utf-8")
        )
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="audio.wav"\r\n'
        f"Content-Type: audio/wav\r\n\r\n".encode("utf-8")
        + wav
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


class RemoteTranscriber:
    """Hosted Whisper with a local Transcriber as the safety net.

    `local` is the already-loaded resident model — it stays loaded even when
    the remote path is working, precisely so the fallback is instant when the
    network drops mid-dictation.
    """

    def __init__(
        self,
        local: Transcriber,
        model: str = DEFAULT_MODEL,
        language: str = "pt",
        prompt: str = "",
        timeout: float = TIMEOUT_SECONDS,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.local = local
        self.model = model
        self.language = language
        # Same soft-bias trick as the local initial_prompt (AD-2): the hosted
        # API takes a `prompt` field with identical semantics.
        self.prompt = prompt
        self.timeout = timeout
        self._logger = logger or logging.getLogger("whisperflow")

    def _remote(self, audio: np.ndarray) -> str:
        key = os.environ.get("GROQ_API_KEY", "")
        if not key:
            raise RemoteUnavailable("GROQ_API_KEY não está setada no ambiente")

        fields = {"model": self.model, "language": self.language, "response_format": "json"}
        if self.prompt:
            fields["prompt"] = self.prompt
        body, content_type = _multipart(fields, _encode_wav(audio))

        req = urllib.request.Request(
            API_URL,
            data=body,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": content_type,
                # Groq's edge 403s urllib's default UA as bot traffic (same
                # workaround as polish.py).
                "User-Agent": "Mozilla/5.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RemoteUnavailable(f"erro de rede/timeout: {exc}") from exc
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise RemoteUnavailable(f"resposta inválida da API: {exc}") from exc

        try:
            return str(payload["text"]).strip()
        except (KeyError, TypeError) as exc:
            raise RemoteUnavailable(f"formato de resposta inesperado: {exc}") from exc

    def transcribe(self, audio: np.ndarray) -> str:
        if audio is None or len(audio) == 0:
            return ""
        try:
            t0 = time.time()
            text = self._remote(audio)
            self._logger.info("transcricao remota (%s, %.2fs)", self.model, time.time() - t0)
            return text
        except RemoteUnavailable as exc:
            self._logger.warning("motor remoto indisponível, caindo pro modelo local: %s", exc)
            return self.local.transcribe(audio)


if __name__ == "__main__":
    # Manual test: python remote_transcriber.py [wav_path]
    import sys
    from pathlib import Path

    import recorder as recorder_mod

    wav_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("bench/frase-padrao.wav")
    audio = recorder_mod.load_wav_as_float32(wav_path)
    print(f"audio: {wav_path} ({len(audio) / SAMPLE_RATE:.2f}s)")

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    rt = RemoteTranscriber(local=Transcriber(model_size="base"), logger=logging.getLogger("whisperflow"))
    t0 = time.time()
    print(f"texto ({time.time() - t0:.2f}s): {rt.transcribe(audio)}")
