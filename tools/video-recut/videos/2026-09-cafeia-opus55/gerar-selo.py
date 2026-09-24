"""Selo do CAFEIA — assinatura do formato. Arte própria, sóbria, sem cara de template.

Entrada: as letras sobem sob máscara, uma a uma, e a régua se abre por baixo.
Sai em 760x300 com alpha (qtrle), para entrar como card pelo `camadas`.
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, DUR = 820, 330, 30, 2.4
CREME = (243, 238, 230)
CAFE = (168, 124, 76)
ESCURO = (26, 22, 19)
F = r"C:\Windows\Fonts\seguisb.ttf"
FL = r"C:\Windows\Fonts\segoeui.ttf"


def selo():
    fonte = ImageFont.truetype(F, 112)
    f_sub = ImageFont.truetype(FL, 26)
    letras = list("COFFEE IA")
    medida = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tracking = 14
    largs = [medida.textlength(c, font=fonte) for c in letras]
    total = sum(largs) + tracking * (len(letras) - 1)
    x0 = (W - total) / 2
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "qtrle",
                             os.path.join(AQUI, "cafeia-selo.mov")], stdin=subprocess.PIPE)
    suave = lambda p: 1 - (1 - p) ** 3
    for f in range(int(DUR * FPS)):
        t = f / FPS
        quadro = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fundo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(fundo).rounded_rectangle([20, 20, W - 20, H - 20], 22, fill=(20, 16, 13, 205))
        quadro = Image.alpha_composite(quadro, fundo.filter(ImageFilter.GaussianBlur(0.6)))
        x = x0
        for i, c in enumerate(letras):
            p = suave(min(1.0, max(0.0, (t - i * 0.055) / 0.30)))
            if p > 0:
                faixa = Image.new("RGBA", (int(largs[i]) + 20, 160), (0, 0, 0, 0))
                dl = ImageDraw.Draw(faixa)
                dl.text((10, 8 + 4), c, font=fonte, fill=(0, 0, 0, 150))     # sombra discreta
                dl.text((10, 8), c, font=fonte, fill=CREME)
                quadro.alpha_composite(faixa, (int(x) - 10, int(40 + (1 - p) * 150)))
            x += largs[i] + tracking
        d = ImageDraw.Draw(quadro)
        pr = suave(min(1.0, max(0.0, (t - 0.55) / 0.45)))                    # régua cor de café
        if pr > 0:
            lw = total * pr
            d.rounded_rectangle([(W - lw) / 2, 205, (W + lw) / 2, 212], 4, fill=CAFE)
        ps = min(1.0, max(0.0, (t - 0.95) / 0.5))                            # assinatura embaixo
        if ps > 0:
            sub = "notícia de IA para quem tem empresa"
            tr = 9 - 4 * suave(ps)
            larg_sub = sum(medida.textlength(c, font=f_sub) + tr for c in sub) - tr
            xs = (W - larg_sub) / 2
            for c in sub:
                d.text((xs, 246), c, font=f_sub, fill=(232, 226, 216, int(215 * ps)))
                xs += medida.textlength(c, font=f_sub) + tr
        a = min(1.0, t / 0.15) * min(1.0, (DUR - t) / 0.35)
        quadro.putalpha(quadro.getchannel("A").point(lambda v: int(v * a)))
        proc.stdin.write(quadro.tobytes())
    proc.stdin.close(); proc.wait()
    print("cafeia-selo.mov ok")


if __name__ == "__main__":
    selo()
