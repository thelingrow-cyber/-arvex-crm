"""Map source speech timestamps to the current editorial timeline."""

STAGES = [
    [(0.45,11.70),(17.42,29.20),(32.65,52.98),(64.26,67.22),(68.18,70.30),(71.68,73.86)],
    [(0,5.86),(8.38,50.633)],
    [(0,7.72),(7.89,15.83),(16.05,17.61),(17.80,25.09),(25.48,28.85),(29.05,31.31),(31.66,35.66),(35.86,38.29),(38.56,48.116)],
    [(0,7.63),(7.77,10.02),(10.10,13.02),(13.16,13.54),(13.82,17.08),(17.28,19.94),(20.06,23.18),(23.32,24.42),(24.56,25.92),(26.22,31.54),(31.66,34.00),(34.18,35.15),(35.25,35.93),(36.07,36.47),(36.59,38.86),(39.00,41.92),(42.12,43.98),(44.08,46.167)],
    [(0,2.96),(3.06,27.03),(27.14,41.167)],
    [(0,5.13),(5.43,13.16),(14.13,40.967)],
]


def forward_stage(t, ranges):
    pos = 0
    for start, end in ranges:
        if start <= t < end:
            return pos + (t - start)
        pos += end - start
    return None


def reverse_stage(t, ranges):
    pos = 0
    for start, end in ranges:
        if pos <= t < pos + end - start:
            return start + t - pos
        pos += end - start
    return None


def raw_to_v9(t):
    for i, ranges in enumerate(STAGES):
        if i == 4:
            t /= 1.06
        t = forward_stage(t, ranges)
        if t is None:
            return None
    return t


def v9_to_raw(t):
    for i in reversed(range(len(STAGES))):
        t = reverse_stage(t, STAGES[i])
        if t is None:
            return None
        if i == 4:
            t *= 1.06
    return t


if __name__ == "__main__":
    import json
    from pathlib import Path
    root = Path(__file__).parent
    j = json.loads((root / "transcript.json").read_text(encoding="utf-8"))
    for seg in j["segments"]:
        for word in seg["words"]:
            t = raw_to_v9((word["start"] + word["end"]) / 2)
            if t is not None:
                print(f'{t:6.2f} {word["text"]}')
