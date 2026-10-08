from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "opener-assets"
OUT.mkdir(exist_ok=True)
W, H = 1080, 880
FONT = Path(r"C:\Windows\Fonts\segoeui.ttf")
BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")

def font(size, bold=False):
    return ImageFont.truetype(str(BOLD if bold else FONT), size)

def layer(name):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im), OUT / name

# Fine editorial grid and series identifier.
im, d, p = layer("frame.png")
d.line((58, 64, 1022, 64), fill=(255, 255, 255, 85), width=2)
d.line((58, 810, 1022, 810), fill=(255, 255, 255, 55), width=2)
d.text((58, 82), "COFFEE IA  /  02", font=font(25, True), fill=(255, 255, 255, 230))
d.text((840, 82), "AGORA", font=font(25, True), fill=(255, 255, 255, 150))
im.save(p)

im, d, p = layer("amazon.png")
d.text((60, 240), "amazon", font=font(112, True), fill=(255, 153, 0, 255))
d.line((67, 365, 415, 365), fill=(255, 153, 0, 230), width=7)
im.save(p)

im, d, p = layer("meta.png")
d.text((690, 240), "Meta", font=font(118, True), fill=(81, 156, 255, 255))
d.line((692, 365, 1000, 365), fill=(81, 156, 255, 230), width=7)
im.save(p)

im, d, p = layer("tension.png")
d.line((450, 320, 630, 320), fill=(255, 255, 255, 170), width=3)
d.ellipse((526, 306, 554, 334), fill=(255, 255, 255, 245))
d.text((500, 350), "×", font=font(48, True), fill=(255, 255, 255, 235))
im.save(p)

im, d, p = layer("headline.png")
d.text((58, 535), "ACESSO", font=font(55, True), fill=(255, 255, 255, 205))
d.text((58, 590), "BLOQUEADO", font=font(105, True), fill=(255, 255, 255, 255))
d.rounded_rectangle((60, 725, 465, 778), radius=24, fill=(10, 12, 18, 190))
d.text((83, 735), "A DISPUTA PELA COMPRA", font=font(25, True), fill=(255, 255, 255, 220))
im.save(p)

# Branded sting used when the presenter says the series name.
im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle((240, 1120, 840, 1295), radius=54, fill=(8, 11, 17, 225), outline=(255, 255, 255, 65), width=2)
d.ellipse((285, 1160, 365, 1240), outline=(255, 255, 255, 235), width=5)
d.arc((300, 1178, 386, 1240), start=270, end=90, fill=(255, 255, 255, 210), width=5)
d.arc((302, 1124, 326, 1170), start=80, end=265, fill=(81, 156, 255, 220), width=4)
d.arc((330, 1115, 354, 1165), start=80, end=265, fill=(255, 153, 0, 220), width=4)
d.text((405, 1150), "COFFEE", font=font(58, True), fill=(255, 255, 255, 255))
d.text((664, 1150), "IA", font=font(58, True), fill=(81, 156, 255, 255))
d.text((407, 1220), "NEGÓCIOS EM MOVIMENTO", font=font(21, True), fill=(255, 255, 255, 155))
im.save(OUT / "brand-sting.png")

print(OUT)
