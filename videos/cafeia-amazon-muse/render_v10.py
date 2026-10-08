"""Rebuild the Coffee IA reel's speaker layer, captions and brand cue."""

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import av
import numpy as np

sys.path.insert(0, r"C:\Users\Vitor Simões\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Lib\site-packages")
from PIL import Image, ImageDraw, ImageFont

from timeline_map import raw_to_v9, v9_to_raw

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "input.mp4"
PREVIOUS = ROOT / "COFFEE-IA-amazon-muse-final-v9.mp4"
OUTPUT = ROOT / "COFFEE-IA-amazon-muse-final-v10.mp4"
FONT_PATH = r"C:\Windows\Fonts\segoeuib.ttf"
FONT = ImageFont.truetype(FONT_PATH, 57)
BRAND_BIG = ImageFont.truetype(FONT_PATH, 105)
BRAND_SMALL = ImageFont.truetype(FONT_PATH, 38)
FPS = 30
FULL_FROM = 33.03  # Last support visual ends on this spoken beat.


def mapped_span(start, end):
    # Some source words straddle a previous jump cut, so sample the retained part.
    samples = np.linspace(start, end, max(3, math.ceil((end-start)/0.02)))
    positions = [raw_to_v9(float(x)) for x in samples]
    positions = [x for x in positions if x is not None]
    return (min(positions), max(positions)) if positions else None


def word_timeline():
    source = json.loads((ROOT / "transcript.json").read_text(encoding="utf-8"))
    words = []
    for segment in source["segments"]:
        for item in segment["words"]:
            span = mapped_span(item["start"], item["end"])
            if span is None:
                continue
            start, end = span
            if end < 0 or start > 39.75:
                continue
            label = item["text"].strip().rstrip(",.")
            key = label.lower()
            replacements = {
                "cafeia": "COFFEE IA", "escorrer": "escolher",
                "stock": "estoque", "convestir": "convencer",
            }
            label = replacements.get(key, label)
            words.append({"start": start, "end": max(start+0.07, end), "text": label})

    # The original ASR merged the full repeated delivery into one long word.
    words = [w for w in words if w["text"].lower() != "compra" or not (12 < w["start"] < 14)]
    words.append({"start": 12.80, "end": 13.39, "text": "compra"})

    # Correct two ASR artefacts while retaining word-level timing.
    for i, w in enumerate(words):
        if w["text"].lower() == "e" and 12.4 < w["start"] < 12.6:
            w["start"] = 12.55
        if w["text"].lower() == "conta" and 21 < w["start"] < 23:
            w["text"] = "está"
        if w["text"].lower() == "um" and 22 < w["start"] < 23:
            w["text"] = "controlando"
            if i+1 < len(words) and words[i+1]["text"].lower() == "controlando":
                words[i+1]["text"] = ""
    words = [w for w in sorted(words, key=lambda x: x["start"]) if w["text"]]
    (ROOT / "captions-v10-words.json").write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")
    return words


def make_groups(words):
    groups = []
    current = []
    for w in words:
        editorial_boundary = any(current[0]["start"] < point <= w["start"] for point in (6.79,7.55,13.98,16.55,20.6,25.5,26.72,29.0,33.05,35.8,37.55)) if current else False
        if current and (editorial_boundary or len(current) >= 3 or w["start"]-current[-1]["end"] > 0.24 or w["end"]-current[0]["start"] > 1.25):
            groups.append(current)
            current = []
        current.append(w)
    if current:
        groups.append(current)
    return groups


def caption_overlay(group, active):
    layer = Image.new("RGBA", (1080, 210), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    tokens = [w["text"].upper() for w in group]
    space = draw.textlength(" ", font=FONT)
    widths = [draw.textlength(t, font=FONT) for t in tokens]
    if sum(widths) + space*(len(tokens)-1) > 960:
        # Font fallback for unusually long three-word phrases.
        font = ImageFont.truetype(FONT_PATH, 48)
        space = draw.textlength(" ", font=font)
        widths = [draw.textlength(t, font=font) for t in tokens]
    else:
        font = FONT
    total = sum(widths) + space*(len(tokens)-1)
    x = (1080-total)/2
    y = 66
    for i, (token, width) in enumerate(zip(tokens, widths)):
        draw.text((x, y+5), token, font=font, fill=(0,0,0,135), stroke_width=7, stroke_fill=(0,0,0,85))
        draw.text((x, y), token, font=font, fill=(250,198,58,255) if i == active else (255,255,255,255),
                  stroke_width=4, stroke_fill=(12,14,20,230))
        x += width+space
    return layer


def brand_overlay():
    image = Image.new("RGBA", (1080,1920), (5,7,12,96))
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((104,745,976,1115), radius=60, fill=(13,18,29,242), outline=(251,194,54,255), width=5)
    d.rounded_rectangle((435,780,645,794), radius=7, fill=(251,194,54,255))
    title = "COFFEE IA"
    width = d.textlength(title, font=BRAND_BIG)
    d.text(((1080-width)/2,826), title, font=BRAND_BIG, fill=(255,255,255,255))
    subtitle = "INTELIGÊNCIA PARA NEGÓCIOS"
    width = d.textlength(subtitle, font=BRAND_SMALL)
    d.text(((1080-width)/2,983), subtitle, font=BRAND_SMALL, fill=(251,194,54,255))
    return image


def main():
    words = word_timeline()
    groups = make_groups(words)
    caption_cache = {}
    brand = brand_overlay()
    with av.open(str(PREVIOUS)) as old, av.open(str(SOURCE)) as raw, av.open(str(PREVIOUS)) as old_audio, av.open(str(OUTPUT), "w") as output:
        old_video = old.streams.video[0]
        raw_video = raw.streams.video[0]
        source_audio = old_audio.streams.audio[0]
        video = output.add_stream("libx264", rate=FPS)
        video.width, video.height = 1080, 1920
        video.pix_fmt = "yuv420p"
        video.options = {"preset": "veryfast", "crf": "18"}
        audio = output.add_stream_from_template(source_audio)
        raw_frames = iter(raw.decode(raw_video))
        raw_current = next(raw_frames)
        raw_next = next(raw_frames)
        audio_packets = iter(old_audio.demux(source_audio))
        next_audio = next(audio_packets, None)
        group_idx = 0
        frame_idx = 0
        for old_frame in old.decode(old_video):
            t = float(old_frame.time or frame_idx/FPS)
            target = v9_to_raw(t)
            if target is None:
                # The last source trim is 0.2 s shorter than the muxed v9 tail.
                # Hold the final source frame so the video covers the full audio.
                target = 73.84
            while raw_next is not None and float(raw_next.time or 0) <= target:
                raw_current = raw_next
                raw_next = next(raw_frames, None)
            raw_img = Image.fromarray(raw_current.to_ndarray(format="rgb24"))
            if 0 <= t < 6.20 or 7.90 <= t < FULL_FROM:
                old_img = Image.fromarray(old_frame.to_ndarray(format="rgb24"))
                canvas = Image.new("RGB", (1080,1920))
                canvas.paste(old_img.crop((0,0,1080,880)), (0,0))
                canvas.paste(raw_img.crop((0,600,1080,1640)), (0,880))
            else:
                canvas = raw_img
            if 6.79 <= t <= 7.55:
                opacity = max(0.0, min(1.0, (t-6.79)/0.12, (7.55-t)/0.12))
                brand_frame = brand.copy()
                brand_frame.putalpha(brand.getchannel("A").point(lambda a: round(a*opacity)))
                canvas = Image.alpha_composite(canvas.convert("RGBA"),brand_frame)
            else:
                canvas = canvas.convert("RGBA")
            while group_idx < len(groups)-1 and t > groups[group_idx][-1]["end"] + 0.04:
                group_idx += 1
            if group_idx < len(groups):
                group = groups[group_idx]
                if group[0]["start"]-0.02 <= t <= group[-1]["end"]+0.06:
                    active = max(0, min(len(group)-1, sum(t >= w["start"] for w in group)-1))
                    key = (group_idx,active)
                    if key not in caption_cache:
                        caption_cache[key] = caption_overlay(group,active)
                    canvas.alpha_composite(caption_cache[key], (0,1435))
            vf = av.VideoFrame.from_image(canvas.convert("RGB"))
            vf.pts = frame_idx
            vf.time_base = Fraction(1,FPS)
            for packet in video.encode(vf):
                output.mux(packet)
            while next_audio is not None and (next_audio.pts is None or float(next_audio.pts*next_audio.time_base) <= t+0.12):
                if next_audio.size:
                    next_audio.stream = audio
                    output.mux(next_audio)
                next_audio = next(audio_packets,None)
            frame_idx += 1
            if frame_idx % 150 == 0:
                print(f"rendered {frame_idx/FPS:.1f}s", flush=True)
        for packet in video.encode():
            output.mux(packet)
        while next_audio is not None:
            if next_audio.size:
                next_audio.stream = audio
                output.mux(next_audio)
            next_audio = next(audio_packets,None)
    print(f"Wrote {OUTPUT} ({frame_idx/FPS:.2f}s)")


if __name__ == "__main__":
    main()
