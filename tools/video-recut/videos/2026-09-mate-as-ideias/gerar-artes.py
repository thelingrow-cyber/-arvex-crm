"""Artes originais dos cards deste vídeo (nada de imagem de terceiro além da foto de domínio público).

- cofre.jpg  -> recorte fechado na porta do cofre (foto 1914, domínio público, Library of Congress)
- tumulo.png -> desenho original: lápides ao anoitecer
- mate.png   -> card tipográfico "MATE TODAS AS IDEIAS"

uso: python gerar-artes.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H = 1520, 950         # card horizontal no topo (o dobro do tamanho na tela, fica nítido)
FONTE = r"C:\Windows\Fonts\seguisb.ttf"
VERDE = (37, 211, 102)


def cofre():
    origem = os.path.join(AQUI, "cofre-original.jpg")
    im = Image.open(origem).convert("RGB")
    w, h = im.size
    # a porta do cofre fica na metade direita; recorte fechado e um pouco mais de contraste
    cx, cy = int(w * 0.58), int(h * 0.52)
    lado = int(min(w, h) * 0.62)
    im = im.crop((cx - lado // 2, cy - int(lado * 0.62), cx + lado // 2, cy + int(lado * 0.62)))
    im = im.resize((W, H), Image.LANCZOS)
    im.point(lambda v: min(255, int(18 + v * 1.12))).save(os.path.join(AQUI, "cofre.jpg"), quality=92)


def patente():
    """Desenho da patente da lâmpada (1880, NARA, domínio público) encaixado num card 'papel'."""
    im = Image.open(os.path.join(AQUI, "patente-original.jpg")).convert("RGB")
    im.thumbnail((int(W * 0.42), int(H * 0.94)), Image.LANCZOS)
    fundo = Image.new("RGB", (W, H), (233, 228, 216))
    fundo.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    d = ImageDraw.Draw(fundo)
    f = ImageFont.truetype(FONTE, int(H * 0.05))
    d.text((int(W * 0.06), int(H * 0.08)), "NA SUA CABEÇA", font=f, fill=(28, 30, 34))
    d.text((int(W * 0.06), int(H * 0.16)), "ELA É PERFEITA", font=f, fill=(20, 120, 60))
    d.text((int(W * 0.06), int(H * 0.86)), "PATENTE DA LÂMPADA · 1880", font=ImageFont.truetype(FONTE, int(H * 0.032)),
           fill=(110, 108, 100))
    fundo.save(os.path.join(AQUI, "patente.png"))


def tumulo():
    im = Image.new("RGB", (W, H), (12, 16, 26))
    d = ImageDraw.Draw(im)
    for y in range(H):                                   # céu de anoitecer
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(18 + 44 * t), int(22 + 40 * t), int(40 + 46 * t)))
    r = int(W * 0.045)
    d.ellipse([int(W * 0.80), int(H * 0.12), int(W * 0.80) + 2 * r, int(H * 0.12) + 2 * r], fill=(232, 232, 214))
    d.ellipse([-W // 6, int(H * 0.70), W + W // 6, H + int(H * 0.3)], fill=(9, 12, 18))   # colina
    for fx, esc in ((0.16, 1.0), (0.34, 0.8), (0.50, 0.64), (0.66, 0.5)):
        x, larg, alt = int(W * fx), int(W * 0.10 * esc), int(H * 0.34 * esc)
        topo = int(H * 0.80) - alt
        d.rounded_rectangle([x - larg // 2, topo, x + larg // 2, int(H * 0.82)], larg // 2, fill=(26, 30, 40))
        g = max(3, int(W * 0.007 * esc))
        d.line([(x - larg // 4, topo + int(alt * 0.30)), (x + larg // 4, topo + int(alt * 0.30))], fill=(48, 54, 66), width=g)
        d.line([(x, topo + int(alt * 0.14)), (x, topo + int(alt * 0.55))], fill=(48, 54, 66), width=g)
    im.filter(ImageFilter.GaussianBlur(0.4)).save(os.path.join(AQUI, "tumulo.png"))


def mate():
    im = Image.new("RGB", (W, H), (10, 10, 12))
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(FONTE, int(H * 0.21))
    f2 = ImageFont.truetype(FONTE, int(H * 0.055))
    d.text((W / 2, H * 0.34), "MATE TODAS", font=f1, fill=(255, 255, 255), anchor="mm")
    d.text((W / 2, H * 0.57), "AS IDEIAS", font=f1, fill=VERDE, anchor="mm")
    d.text((W / 2, H * 0.84), "UMA VAI SOBREVIVER", font=f2, fill=(150, 156, 166), anchor="mm")
    d.rectangle([W / 2 - W * 0.06, H * 0.73, W / 2 + W * 0.06, H * 0.735], fill=VERDE)
    im.save(os.path.join(AQUI, "mate.png"))


if __name__ == "__main__":
    if os.path.exists(os.path.join(AQUI, "cofre-original.jpg")):
        cofre()
    if os.path.exists(os.path.join(AQUI, "patente-original.jpg")):
        patente()
    tumulo(); mate()
    print("artes geradas em", AQUI)
