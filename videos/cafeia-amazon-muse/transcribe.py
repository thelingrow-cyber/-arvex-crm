import json
import argparse
from pathlib import Path

from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("input", nargs="?", default=str(ROOT / "input.mp4"))
parser.add_argument("--output", default=str(ROOT / "transcript.json"))
args = parser.parse_args()
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8",
    cpu_threads=6,
    download_root=str(ROOT / "models"),
)

segments, info = model.transcribe(
    args.input,
    language="pt",
    vad_filter=True,
    word_timestamps=True,
    initial_prompt=(
        "Transcrição em português brasileiro. Nomes: Amazon, Meta, Muse, "
        "COFFEE IA, café com inteligência artificial e negócios."
    ),
)

result = {
    "language": info.language,
    "duration": info.duration,
    "segments": [],
    "words": [],
}

for segment in segments:
    seg = {
        "start": segment.start,
        "end": segment.end,
        "text": segment.text.strip(),
        "words": [],
    }
    for word in segment.words or []:
        item = {
            "start": word.start,
            "end": word.end,
            "text": word.word.strip(),
            "probability": word.probability,
        }
        seg["words"].append(item)
        result["words"].append(item)
    result["segments"].append(seg)

Path(args.output).write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
)

for seg in result["segments"]:
    print(f"[{seg['start']:7.2f} - {seg['end']:7.2f}] {seg['text']}")
