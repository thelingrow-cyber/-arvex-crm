import sys
import wave
from pathlib import Path

import av
import numpy as np

sys.path.insert(0, r"C:\Users\Vitor Simões\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Lib\site-packages")
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parent
source = root / "COFFEE-IA-amazon-muse-final-v9.mp4"

def contact(start: float, end: float, step: float, out: Path):
    with av.open(str(source)) as container:
        video = container.streams.video[0]
        container.seek(int(max(0, start - 0.5) * av.time_base), backward=True)
        targets = np.arange(start, end, step)
        images = []
        idx = 0
        for frame in container.decode(video):
            t = float(frame.time or 0)
            if t + 0.016 < targets[idx]:
                continue
            im = Image.fromarray(frame.to_ndarray(format="rgb24")).resize((216, 384), Image.Resampling.LANCZOS)
            images.append((targets[idx], im))
            idx += 1
            if idx >= len(targets):
                break
        cols = 5
        rows = (len(images) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 226, rows * 416), "#111111")
        d = ImageDraw.Draw(sheet)
        f = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 18)
        for n, (t, im) in enumerate(images):
            x = (n % cols) * 226 + 5
            y = (n // cols) * 416 + 27
            sheet.paste(im, (x, y))
            d.text((x, y - 24), f"{t:.2f}s", font=f, fill="white")
        sheet.save(out)
        print(out)

def wav(start: float, end: float, out: Path):
    with av.open(str(source)) as container:
        audio = container.streams.audio[0]
        chunks = []
        resampler = av.AudioResampler(format="s16", layout="mono", rate=16000)
        for frame in container.decode(audio):
            t = float(frame.time or 0)
            if t > end:
                break
            for new in resampler.resample(frame):
                if new.time is None:
                    continue
                ts = float(new.time)
                raw = new.to_ndarray().reshape(-1)
                left = max(0, round((start - ts) * 16000))
                right = min(len(raw), round((end - ts) * 16000))
                if right > left:
                    chunks.append(raw[left:right].astype(np.int16))
        data = np.concatenate(chunks)
        with wave.open(str(out), "wb") as file:
            file.setnchannels(1)
            file.setsampwidth(2)
            file.setframerate(16000)
            file.writeframes(data.tobytes())
        print(out, len(data) / 16000)

if __name__ == "__main__":
    contact(33.0, 39.7, 0.3, root / "review-v9-return.jpg")
    contact(6.4, 9.0, 0.25, root / "review-v9-logo.jpg")
    wav(10.5, 15.6, root / "review-v9-repeat.wav")
