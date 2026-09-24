"""Artes originais do vídeo "Quase" (nada de material de terceiro).

- gps.png   -> painel de navegação desenhado aqui (rota, pino, "destino: você decide")
- editor.png-> cartão com o log real do nosso editor de vídeo (prova própria)
"""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H = 1520, 950
FONTE = r"C:\Windows\Fonts\seguisb.ttf"
VERDE = (37, 211, 102)


def gps():
    im = Image.new("RGB", (W, H), (14, 18, 24))
    d = ImageDraw.Draw(im)
    for i in range(1, 7):                                   # malha de ruas
        y = int(H * i / 7)
        d.line([(0, y + (i % 2) * 18), (W, y - (i % 2) * 18)], fill=(30, 36, 46), width=6)
    for i in range(1, 6):
        x = int(W * i / 6)
        d.line([(x, 0), (x + 30, H)], fill=(30, 36, 46), width=6)
    rota = [(int(W * 0.12), int(H * 0.86)), (int(W * 0.30), int(H * 0.70)), (int(W * 0.30), int(H * 0.46)),
            (int(W * 0.58), int(H * 0.40)), (int(W * 0.58), int(H * 0.22)), (int(W * 0.80), int(H * 0.18))]
    d.line(rota, fill=(60, 130, 255), width=26, joint="curve")
    d.line(rota, fill=(120, 175, 255), width=8, joint="curve")
    x, y = rota[-1]
    d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=VERDE)   # destino
    f1 = ImageFont.truetype(FONTE, int(H * 0.075))
    f2 = ImageFont.truetype(FONTE, int(H * 0.05))
    d.text((int(W * 0.06), int(H * 0.06)), "ROTA CALCULADA", font=f1, fill=(235, 238, 245))
    d.text((int(W * 0.06), int(H * 0.16)), "chegada em 12 min", font=f2, fill=(150, 158, 170))
    d.text((int(W * 0.06), int(H * 0.88)), "DESTINO: definido por você", font=f2, fill=VERDE)
    im.save(os.path.join(AQUI, "gps.png"))


def editor():
    im = Image.new("RGB", (W, H), (10, 12, 16))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.12)], fill=(24, 28, 36))
    fc = ImageFont.truetype(FONTE, int(H * 0.055))
    fm = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", int(H * 0.045))
    d.text((int(W * 0.04), int(H * 0.03)), "camadas.py — render", font=fc, fill=(210, 216, 226))
    linhas = [("[cortar]", (110, 118, 130)), ("  corte: 14 trechos, 41.7s -> 37.2s", (235, 238, 245)),
              ("[legenda]", (110, 118, 130)), ("  108 grupos gerados", (235, 238, 245)),
              ("[compor]", (110, 118, 130)), ("  1080x1920 · 30fps · crf 18", (235, 238, 245)),
              ("[previa]", (110, 118, 130)), ("  ok", VERDE)]
    y = int(H * 0.20)
    for t, cor in linhas:
        d.text((int(W * 0.05), y), t, font=fm, fill=cor)
        y += int(H * 0.09)
    im.save(os.path.join(AQUI, "editor.png"))


if __name__ == "__main__":
    gps(); editor(); print("artes geradas")
