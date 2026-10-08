import json
import os
import sys
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

root = Path(__file__).resolve().parent
model = WhisperModel(os.environ.get("FW_MODEL", "base"), device="cpu", compute_type="int8", cpu_threads=6,
                     download_root=str(root / "models"))
for media in sys.argv[1:]:
    segments, _ = model.transcribe(media, language="pt", vad_filter=False,
                                   word_timestamps=True, beam_size=5,
                                   condition_on_previous_text=False)
    print(f"\n{media}", flush=True)
    for segment in segments:
        print(f"{segment.start:.2f}-{segment.end:.2f} {segment.text}", flush=True)
        for word in segment.words or []:
            print(f"  {word.start:.2f}-{word.end:.2f} {word.word}", flush=True)
