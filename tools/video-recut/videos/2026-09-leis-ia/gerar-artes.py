"""Cards do vídeo das 11 leis — arte própria em PIL, mesma gramática do vídeo da água do mar.

Exceção: `c-universo.png` é FOTO REAL (Wikimedia Commons, Milky Way sobre Joshua tree,
domínio público) — tratada em `c_universo()`.
"""
import math
import os
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H = 1120, 630

FUNDO = (236, 231, 222)
GRAFITE = (62, 66, 72)
OURO = (214, 158, 66)
AZUL = (94, 128, 150)
CLARO = (186, 182, 174)
SOMBRA = (202, 196, 186)


def base():
    im = Image.new("RGB", (W, H), FUNDO)
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse([-W * 0.30, -H * 0.42, W * 1.30, H * 1.42], fill=60)
    v = v.filter(ImageFilter.GaussianBlur(120))
    return Image.composite(im, Image.new("RGB", (W, H), (212, 208, 200)), v)


def figura(d, x, y, alt, cor, invertida=False):
    rc = alt * 0.22
    s = -1 if invertida else 1
    topo = y + s * (2 * rc + alt * 0.06)
    larg = alt * 0.30
    y0, y1 = sorted([topo, y + s * alt])
    d.rounded_rectangle([x - larg, y0, x + larg, y1], radius=larg * 0.55, fill=cor)
    cy0, cy1 = sorted([y, y + s * 2 * rc])
    d.ellipse([x - rc, cy0, x + rc, cy1], fill=cor)


# ------------------------------------------------------------------ os cards

def c_universo():
    """Abertura em FOTO REAL. Domínio público, Wikimedia Commons."""
    src = Image.open(os.path.join(AQUI, "ceu2.jpg")).convert("RGB")
    lw, lh = src.size
    nh = int(lw / (W / H))
    topo = max(0, int((lh - nh) * 0.30))
    im = src.crop((0, topo, lw, min(lh, topo + nh))).resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(1.18)
    im = ImageEnhance.Contrast(im).enhance(1.10)
    im = ImageEnhance.Color(im).enhance(0.85)
    im.filter(ImageFilter.UnsharpMask(radius=2, percent=50, threshold=3)) \
      .save(os.path.join(AQUI, "c-universo.png"))


def c_espelho():
    """Lei do reflexo: você em cima, o mundo devolvendo embaixo."""
    im = base()
    d = ImageDraw.Draw(im)
    eixo, alt = H * 0.50, 216
    # a figura de cima TERMINA na linha do espelho; a de baixo é ela espelhada
    figura(d, int(W * 0.50), int(eixo - 26 - alt), alt, OURO)
    figura(d, int(W * 0.50), int(eixo + 26 + alt), alt, AZUL, invertida=True)
    d.line([(W * 0.13, eixo), (W * 0.87, eixo)], fill=SOMBRA, width=7)
    im.save(os.path.join(AQUI, "c-espelho.png"))


def c_soltar():
    """Lei do desapego: a mão abre e a coisa sobe."""
    im = base()
    d = ImageDraw.Draw(im)
    pm = (W * 0.50, H * 0.76)
    d.ellipse([pm[0] - 118, pm[1] - 44, pm[0] + 118, pm[1] + 62], fill=OURO)    # palma
    for i, a in enumerate((-64, -34, -6, 22)):                                   # dedos abrindo
        ang = math.radians(a - 90)
        x2, y2 = pm[0] + math.cos(ang) * 150, pm[1] - 26 + math.sin(ang) * 150
        d.line([(pm[0] + (i - 1.5) * 44, pm[1] - 30), (x2, y2)], fill=OURO, width=30)
        d.ellipse([x2 - 15, y2 - 15, x2 + 15, y2 + 15], fill=OURO)
    for k, (dy, r, c) in enumerate([(0, 40, AZUL), (86, 27, (150, 174, 190)), (152, 17, (186, 200, 210))]):
        cy = H * 0.34 - dy
        d.ellipse([W * 0.50 - r, cy - r, W * 0.50 + r, cy + r], fill=c)          # subindo e sumindo
    im.save(os.path.join(AQUI, "c-soltar.png"))


def c_ciclo():
    """Lei do hábito: o loop que se repete — e a brecha por onde se sai."""
    im = base()
    d = ImageDraw.Draw(im)
    cx, cy, r = W * 0.42, H * 0.50, 178
    d.arc([cx - r, cy - r, cx + r, cy + r], start=305, end=205, fill=CLARO, width=34)
    pa = math.radians(205)                                                        # ponta da seta
    px, py = cx + math.cos(pa) * r, cy + math.sin(pa) * r
    d.polygon([(px - 34, py + 6), (px + 26, py - 22), (px + 14, py + 40)], fill=CLARO)
    figura(d, int(W * 0.74), int(H * 0.30), 250, OURO)                            # quem saiu do loop
    d.line([(cx + r * 0.72, cy - 52), (W * 0.63, cy - 52)], fill=GRAFITE, width=11)
    d.polygon([(W * 0.655, cy - 52), (W * 0.625, cy - 74), (W * 0.625, cy - 30)], fill=GRAFITE)
    im.save(os.path.join(AQUI, "c-ciclo.png"))


def c_clareza():
    """Lei da clareza: o alvo vago não se acerta; o específico sim."""
    im = base()
    d = ImageDraw.Draw(im)
    # o alvo vago vai numa camada com alfa e é borrado inteiro — colar um recorte deixaria emenda
    camada = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    db = ImageDraw.Draw(camada)
    for i, r in enumerate((132, 90, 46)):
        db.ellipse([W * 0.27 - r, H * 0.50 - r, W * 0.27 + r, H * 0.50 + r],
                   fill=CLARO + (255,) if i % 2 == 0 else FUNDO + (255,))
    camada = camada.filter(ImageFilter.GaussianBlur(19))
    im = Image.alpha_composite(im.convert("RGBA"), camada).convert("RGB")
    d = ImageDraw.Draw(im)
    for i, r in enumerate((132, 90, 46)):                                          # o alvo nítido
        d.ellipse([W * 0.72 - r, H * 0.50 - r, W * 0.72 + r, H * 0.50 + r],
                  fill=OURO if i % 2 == 0 else FUNDO)
    d.ellipse([W * 0.72 - 17, H * 0.50 - 17, W * 0.72 + 17, H * 0.50 + 17], fill=GRAFITE)
    im.save(os.path.join(AQUI, "c-clareza.png"))


def c_foco():
    """Lei da atenção: o que entra no foco cresce."""
    im = base()
    d = ImageDraw.Draw(im)
    for x, alt in ((W * 0.16, 120), (W * 0.30, 120), (W * 0.84, 120)):
        figura(d, int(x), int(H * 0.56), alt, CLARO)
    cx, cy, r = W * 0.57, H * 0.46, 176
    d.ellipse([cx - r - 12, cy - r - 12, cx + r + 12, cy + r + 12], fill=(224, 219, 209))
    figura(d, int(cx), int(cy - 110), 290, OURO)                                   # o que cresceu
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GRAFITE, width=15)         # a lente
    ang = math.radians(48)
    d.line([(cx + math.cos(ang) * r, cy + math.sin(ang) * r),
            (cx + math.cos(ang) * (r + 92), cy + math.sin(ang) * (r + 92))], fill=GRAFITE, width=26)
    im.save(os.path.join(AQUI, "c-foco.png"))


if __name__ == "__main__":
    c_universo(); c_espelho(); c_soltar(); c_ciclo(); c_clareza(); c_foco()
    print("6 cards gerados")
