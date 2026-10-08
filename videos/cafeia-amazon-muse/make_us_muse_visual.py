from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

root = Path(__file__).resolve().parent
w, h = 1080, 880
font_regular = r"C:\Windows\Fonts\segoeui.ttf"
font_bold = r"C:\Windows\Fonts\segoeuib.ttf"

background = Image.open(root / "us-map-background.png").convert("RGB")
scale = max(w / background.width, h / background.height)
background = background.resize((round(background.width * scale), round(background.height * scale)), Image.Resampling.LANCZOS)
background = background.crop(((background.width - w) // 2, (background.height - h) // 2,
                              (background.width + w) // 2, (background.height + h) // 2)).convert("RGBA")

# Darken the map behind the copy while leaving the geography visible.
shade = Image.new("RGBA", (w, h), (0, 0, 0, 0))
pixels = shade.load()
for x in range(w):
    alpha = int(160 - 85 * (x / w))
    for y in range(h):
        pixels[x, y] = (2, 8, 17, alpha)
background = Image.alpha_composite(background, shade)

phone = Image.open(root / "muse-phone-list.png").convert("RGBA")
phone = phone.resize((338, 751), Image.Resampling.LANCZOS)
shadow = Image.new("RGBA", (380, 790), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.rounded_rectangle((20, 14, 360, 768), radius=40, fill=(0, 0, 0, 170))
shadow = shadow.filter(ImageFilter.GaussianBlur(22))
background.alpha_composite(shadow, (682, 62))
background.alpha_composite(phone, (702, 80))

draw = ImageDraw.Draw(background)
regular = lambda size: ImageFont.truetype(font_regular, size)
bold = lambda size: ImageFont.truetype(font_bold, size)
draw.rounded_rectangle((56, 60, 210, 106), radius=19, fill=(255, 255, 255, 225))
draw.text((77, 69), "MUSE", font=bold(28), fill=(10, 17, 29, 255))
draw.text((56, 164), "O APP CHEGOU", font=bold(35), fill=(223, 235, 248, 255))
draw.text((56, 222), "AO TOPO", font=bold(74), fill=(255, 255, 255, 255))
draw.line((58, 326, 600, 326), fill=(95, 167, 255, 220), width=4)
draw.text((56, 365), "Nº 1", font=bold(158), fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(10, 18, 32, 255))
draw.text((60, 568), "EM APPS GRATUITOS", font=bold(40), fill=(255, 255, 255, 255))
draw.text((60, 625), "NOS ESTADOS UNIDOS", font=bold(36), fill=(255, 255, 255, 255))
draw.rounded_rectangle((56, 742, 626, 802), radius=20, fill=(14, 27, 43, 225), outline=(113, 183, 255, 175), width=2)
draw.text((79, 754), "10 DIAS APÓS O LANÇAMENTO", font=bold(27), fill=(237, 245, 255, 255))

out = root / "us-muse-rank.png"
background.convert("RGB").save(out, quality=95)
print(out)
