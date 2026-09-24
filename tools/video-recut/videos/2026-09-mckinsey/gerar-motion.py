"""Cards animados deste vídeo (arte própria, sem material de terceiro).

scroll.mov -> página de relatório rolando dentro da moldura, com um trecho que acende
lupa.mov   -> o card do 80% com uma lupa deslizando até o número e ampliando

Saem em 900x510 com alpha (qtrle), para entrarem como card no topo pelo `camadas`.
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 900, 510, 30
PAPEL = (244, 245, 247)
TINTA = (15, 26, 43)
CINZA = (120, 128, 140)
AZUL = (43, 108, 232)
F = r"C:\Windows\Fonts\seguisb.ttf"
FL = r"C:\Windows\Fonts\segoeui.ttf"


def encoder(nome):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "qtrle",
                             os.path.join(AQUI, nome)], stdin=subprocess.PIPE)


def pagina_longa(altura=1320):
    """Uma 'página de relatório' comprida: título, parágrafos falsos, gráfico e um bloco destacado."""
    im = Image.new("RGB", (W, altura), PAPEL)
    d = ImageDraw.Draw(im)
    f_tit = ImageFont.truetype(F, 46)
    f_sub = ImageFont.truetype(F, 26)
    d.text((40, 40), "The state of AI", font=f_tit, fill=TINTA)
    d.text((40, 100), "pesquisa global · 2026", font=f_sub, fill=CINZA)
    y = 160
    for bloco in range(3):                       # parágrafos como linhas cinzas
        for i in range(5):
            larg = W - 80 - (60 if i == 4 else 0)
            d.rounded_rectangle([40, y, larg, y + 12], 6, fill=(214, 218, 226))
            y += 26
        y += 24
    d.rounded_rectangle([40, y, W - 40, y + 300], 10, fill=(255, 255, 255))   # gráfico
    d.text((60, y + 20), "Impacto declarado por área", font=f_sub, fill=TINTA)
    base = y + 270
    for i, alt in enumerate((60, 95, 130, 170, 205, 240)):
        x = 70 + i * 130
        d.rectangle([x, base - alt, x + 80, base], fill=AZUL if i == 5 else (178, 200, 244))
    y += 340
    d.rounded_rectangle([40, y, W - 40, y + 150], 10, fill=(225, 234, 252))   # bloco destacado
    d.text((64, y + 30), "8 em cada 10 relatam", font=ImageFont.truetype(F, 40), fill=TINTA)
    d.text((64, y + 84), "ganho de produtividade", font=ImageFont.truetype(F, 40), fill=AZUL)
    return im, y


def scroll(dur=5.0):
    pag, y_destaque = pagina_longa()
    proc = encoder("scroll.mov")
    total = int(dur * FPS)
    fim = pag.height - H
    for f in range(total):
        p = f / max(1, total - 1)
        desloc = int(fim * min(1.0, p / 0.78) ** 0.8)           # desacelera e para no destaque
        quadro = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        quadro.paste(pag.crop((0, desloc, W, desloc + H)), (0, 0))
        d = ImageDraw.Draw(quadro)
        d.rectangle([0, 0, W, 30], fill=TINTA)
        d.text((16, 4), "RELATÓRIO", font=ImageFont.truetype(F, 18), fill=(235, 238, 245))
        if desloc > y_destaque - H + 60:                        # moldura acende no destaque
            d.rounded_rectangle([38, y_destaque - desloc - 2, W - 38, y_destaque - desloc + 152], 10,
                                outline=AZUL, width=5)
        a = min(1.0, f / 6) * min(1.0, (total - f) / 8)
        quadro.putalpha(quadro.getchannel("A").point(lambda v: int(v * a)))
        proc.stdin.write(quadro.tobytes())
    proc.stdin.close(); proc.wait()
    print("scroll.mov ok")


def lupa(dur=4.7):
    fundo = Image.open(os.path.join(AQUI, "n80.png")).convert("RGB").resize((W, H), Image.LANCZOS)
    proc = encoder("lupa.mov")
    total = int(dur * FPS)
    alvo = (int(W * 0.17), int(H * 0.30))                        # onde está o "80%"
    inicio = (int(W * 0.78), int(H * 0.72))
    r = 110
    for f in range(total):
        p = min(1.0, f / (total * 0.45))
        e = 1 - (1 - p) ** 3
        cx = int(inicio[0] + (alvo[0] - inicio[0]) * e)
        cy = int(inicio[1] + (alvo[1] - inicio[1]) * e)
        escuro = Image.eval(fundo, lambda v: int(v * 0.72))     # escurece fora da lupa
        quadro = Image.blend(fundo, escuro, min(1.0, f / 10)).convert("RGBA")
        j = int(r * 1.25)                                        # 1,6x de aumento (antes era 2x e embolava)
        zoom = fundo.crop((cx - j, cy - j, cx + j, cy + j)).resize((2 * r, 2 * r), Image.LANCZOS)
        mask = Image.new("L", (2 * r, 2 * r), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
        sombra = Image.new("RGBA", quadro.size, (0, 0, 0, 0))
        ImageDraw.Draw(sombra).ellipse([cx - r, cy - r + 8, cx + r, cy + r + 8], fill=(0, 0, 0, 110))
        quadro = Image.alpha_composite(quadro, sombra.filter(ImageFilter.GaussianBlur(12)))
        quadro.paste(zoom, (cx - r, cy - r), mask)
        d = ImageDraw.Draw(quadro)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(28, 36, 52), width=8)
        d.line([(cx + int(r * 0.72), cy + int(r * 0.72)), (cx + r + 48, cy + r + 48)], fill=(28, 36, 52), width=14)
        a = min(1.0, f / 6) * min(1.0, (total - f) / 8)
        quadro.putalpha(quadro.getchannel("A").point(lambda v: int(v * a)))
        proc.stdin.write(quadro.tobytes())
    proc.stdin.close(); proc.wait()
    print("lupa.mov ok")


if __name__ == "__main__":
    scroll(); lupa()
