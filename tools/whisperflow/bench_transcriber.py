"""bench_transcriber.py — AD-3 decisive benchmark: base vs small, int8, CPU.

Not part of the daemon's runtime pipeline (main/recorder/transcriber/
paster/feedback/config) — a standalone utility to (re)produce BENCH.md
if the target machine or faster-whisper version ever changes. Run:

    python bench_transcriber.py
"""

from __future__ import annotations

import time
from pathlib import Path

import recorder as recorder_mod
from transcriber import Transcriber

PHRASE_PATH = Path("bench/frase-padrao.wav")
PHRASE_TEXT = (
    "Bom dia, tudo bem? Quero confirmar nossa reunião de amanhã às quinze "
    "horas, e aproveitar pra te mandar a proposta atualizada com os dois "
    "planos que a gente conversou."
)
RUNS_PER_MODEL = 3
MODELS = ["base", "small"]


def bench_model(model_size: str, audio) -> dict:
    print(f"\n=== {model_size} (int8) ===")
    t0 = time.time()
    tr = Transcriber(model_size=model_size)
    load_s = time.time() - t0
    print(f"load: {load_s:.2f}s")

    latencies = []
    last_text = ""
    for i in range(RUNS_PER_MODEL):
        t0 = time.time()
        text = tr.transcribe(audio)
        elapsed = time.time() - t0
        latencies.append(elapsed)
        last_text = text
        print(f"  run {i + 1}: {elapsed:.2f}s")

    avg = sum(latencies) / len(latencies)
    print(f"média: {avg:.2f}s")
    return {
        "model": model_size,
        "load_s": load_s,
        "latencies": latencies,
        "avg_s": avg,
        "text": last_text,
    }


def main() -> None:
    audio = recorder_mod.load_wav_as_float32(PHRASE_PATH)
    duration_s = len(audio) / recorder_mod.SAMPLE_RATE
    print(f"audio: {PHRASE_PATH} ({duration_s:.2f}s)")
    print(f"texto original: {PHRASE_TEXT}")

    results = [bench_model(m, audio) for m in MODELS]

    print("\n\n=== RESUMO ===")
    print(f"{'modelo':<8} {'load(s)':<10} {'média(s)':<10} {'runs(s)'}")
    for r in results:
        runs_str = ", ".join(f"{x:.2f}" for x in r["latencies"])
        print(f"{r['model']:<8} {r['load_s']:<10.2f} {r['avg_s']:<10.2f} [{runs_str}]")

    # AD-3 decision rule: maior modelo com média <= 3s vira default.
    # MODELS is ordered smallest->largest; walk in reverse to find the
    # largest that qualifies.
    winner = None
    for r in reversed(results):
        if r["avg_s"] <= 3.0:
            winner = r["model"]
            break
    if winner is None:
        winner = results[0]["model"]  # fallback: smallest tested model

    print(f"\nDecisão (AD-3): default = '{winner}'")


if __name__ == "__main__":
    main()
