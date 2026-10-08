"""Transcribe the selected podcast excerpt using the installed local model."""
from __future__ import annotations

import json
import os
from pathlib import Path
import time

from faster_whisper import WhisperModel


def main() -> None:
    root = Path(__file__).resolve().parent
    models = Path(os.environ["LOCALAPPDATA"]) / "WhisperFlow" / "models"
    snapshots = models / "models--Systran--faster-whisper-small" / "snapshots"
    installed = sorted(path.parent for path in snapshots.glob("*/model.bin"))
    if not installed:
        raise RuntimeError("No installed local small model found")
    started = time.monotonic()
    model = WhisperModel(str(installed[-1]), device="cpu", compute_type="int8", cpu_threads=4, local_files_only=True)
    segments, info = model.transcribe(
        str(root / "source.wav"),
        language="pt",
        beam_size=5,
        word_timestamps=True,
        vad_filter=False,
        condition_on_previous_text=True,
        initial_prompt="Entrevista de podcast sobre negócios, tecnologia e inteligência artificial.",
    )
    output_segments = []
    all_words = []
    for segment in segments:
        words = [
            {"word": word.word, "start": word.start, "end": word.end, "probability": word.probability}
            for word in (segment.words or [])
        ]
        item = {"start": segment.start, "end": segment.end, "text": segment.text, "words": words}
        output_segments.append(item)
        all_words.extend(words)
        print(f"{segment.start:6.2f} - {segment.end:6.2f}: {segment.text}", flush=True)
    payload = {
        "source_start_seconds": 1404,
        "source_end_seconds": 1451,
        "timestamp_basis": "seconds relative to selected excerpt",
        "model": "faster-whisper-small",
        "language": info.language,
        "duration": info.duration,
        "elapsed_seconds": round(time.monotonic() - started, 2),
        "text": " ".join(item["text"].strip() for item in output_segments),
        "segments": output_segments,
        "words": all_words,
    }
    (root / "transcript.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "transcript.txt").write_text("\n".join(f"[{item['start']:06.2f}-{item['end']:06.2f}] {item['text'].strip()}" for item in output_segments) + "\n", encoding="utf-8")
    print(f"Elapsed seconds: {payload['elapsed_seconds']}", flush=True)


if __name__ == "__main__":
    main()
