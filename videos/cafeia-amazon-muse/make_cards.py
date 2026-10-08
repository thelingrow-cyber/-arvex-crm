from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "cards"
OUT.mkdir(exist_ok=True)

W, H = 1080, 880
BG = "#0B0D12"
WHITE = "#F6F7FB"
MUTED = "#9AA3B2"
ORANGE = "#FF9900"
BLUE = "#1684FF"
GREEN = "#52E29A"
RED = "#FF4D5E"

FONT = Path(r"C:\Windows\Fonts\segoeui.ttf")
BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")


def font(size, bold=False):
    return ImageFont.truetype(str(BOLD if bold else FONT), size)


def base(kicker):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((54, 48, 280, 106), radius=25, fill="#171B25")
    d.text((80, 61), kicker, font=font(24, True), fill=WHITE)
    return im, d


def centered(d, text, y, f, fill=WHITE):
    box = d.textbbox((0, 0), text, font=f)
    d.text(((W - (box[2] - box[0])) / 2, y), text, font=f, fill=fill)


im, d = base("COFFEE IA  •  AGORA")
d.rounded_rectangle((70, 165, 505, 590), radius=42, fill="#18130B", outline=ORANGE, width=5)
d.rounded_rectangle((575, 165, 1010, 590), radius=42, fill="#0B1625", outline=BLUE, width=5)
d.text((155, 315), "amazon", font=font(70, True), fill=ORANGE)
d.text((690, 310), "Meta", font=font(78, True), fill=BLUE)
centered(d, "BLOQUEOU", 645, font(82, True), WHITE)
centered(d, "A COMPRA DO MUSE", 748, font(42, True), MUTED)
im.save(OUT / "01-amazon-meta.png", quality=95)

im, d = base("10 DIAS APÓS O LANÇAMENTO")
centered(d, "#1", 180, font(240, True), BLUE)
centered(d, "APLICATIVO GRATUITO", 520, font(54, True), WHITE)
centered(d, "NOS ESTADOS UNIDOS", 598, font(54, True), WHITE)
d.rounded_rectangle((170, 715, 910, 725), radius=5, fill=BLUE)
im.save(OUT / "02-numero-um.png", quality=95)

im, d = base("AMAZON  ×  MUSE")
centered(d, "ACESSO", 215, font(84, True), MUTED)
centered(d, "BLOQUEADO", 330, font(108, True), RED)
d.rounded_rectangle((210, 545, 870, 690), radius=34, fill="#221116", outline=RED, width=4)
centered(d, "COMPRA INTERROMPIDA", 585, font(38, True), WHITE)
im.save(OUT / "03-bloqueado.png", quality=95)

im, d = base("QUEM CONTROLA A DECISÃO?")
d.rounded_rectangle((75, 205, 430, 455), radius=36, fill="#0E2138", outline=BLUE, width=4)
d.rounded_rectangle((650, 205, 1005, 455), radius=36, fill="#251A0A", outline=ORANGE, width=4)
d.text((155, 270), "MUSE", font=font(64, True), fill=BLUE)
d.text((705, 275), "AMAZON", font=font(54, True), fill=ORANGE)
d.line((445, 330, 635, 330), fill=WHITE, width=10)
d.polygon([(635, 330), (590, 300), (590, 360)], fill=WHITE)
centered(d, "ESCOLHE", 535, font(68, True), WHITE)
centered(d, "ESTOCA  •  ENTREGA", 645, font(46, True), MUTED)
im.save(OUT / "04-decisao.png", quality=95)

im, d = base("O AGENTE COMPARA")
items = [("PREÇO", ORANGE), ("PRAZO", BLUE), ("REPUTAÇÃO", GREEN), ("CONDIÇÕES", WHITE)]
for i, (label, color) in enumerate(items):
    y = 175 + i * 150
    d.rounded_rectangle((90, y, 990, y + 112), radius=30, fill="#151923", outline=color, width=3)
    d.ellipse((125, y + 35, 165, y + 75), fill=color)
    d.text((205, y + 25), label, font=font(52, True), fill=WHITE)
    d.text((820, y + 31), "OK", font=font(40, True), fill=color)
im.save(OUT / "05-comparacao.png", quality=95)

print(OUT)
