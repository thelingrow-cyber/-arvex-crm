"""Cards animados do vídeo "Reagan — o sócio que não trabalha" (eleição 04/10/2026).

c-dado.mov  — "de cada 3 reais, quase 1 fica com ele": três notas de R$1 entram; a terceira vira vermelha.
              Dado: carga tributária bruta 2025 = 32,40% do PIB, maior da série (Tesouro Nacional, boletim 10/04/2026).
c-urna.mov  — "domingo o voto é 22": tela de urna, os dígitos 2 e 2 entram e o CONFIRMA acende.
Mesmo acabamento dos cards do três-livros (papel creme, Segoe Black/Semibold, dourado, sombra).
"""
import os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(AQUI, "_frames")
BLACK = r"C:\Windows\Fonts\seguibl.ttf"
SEMI = r"C:\Windows\Fonts\seguisb.ttf"
OURO = (196, 140, 52)
TINTA = (18, 18, 22)
PAPEL = (246, 242, 234)
VERDE = (46, 125, 50)
VERM = (198, 40, 40)
FPS = 30


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def sombra(card, pad=36):
    out = Image.new("RGBA", (card.width + 2 * pad, card.height + 2 * pad), (0, 0, 0, 0))
    s = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([pad, pad + 10, pad + card.width, pad + card.height + 10], 18, fill=(0, 0, 0, 150))
    out = Image.alpha_composite(s.filter(ImageFilter.GaussianBlur(16)), out)
    out.alpha_composite(card, (pad, pad))
    return out


def arredondar(card, r=20):
    m = Image.new("L", card.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, card.width - 1, card.height - 1], r, fill=255)
    card.putalpha(m)
    return card


def nota(cor, rotulo, w=230, h=120):
    n = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(n)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 14, fill=cor)
    d.rounded_rectangle([8, 8, w - 9, h - 9], 10, outline=(255, 255, 255, 120), width=2)
    f = ImageFont.truetype(BLACK, 54)
    tw = d.textlength(rotulo, font=f)
    d.text(((w - tw) / 2, 22), rotulo, font=f, fill=(255, 255, 255))
    return n


def dado(t, falar=1.95):
    """t = segundos desde a entrada do card; `falar` = quando ele diz "quase 1 fica com ele"."""
    W, H = 900, 420
    card = Image.new("RGBA", (W, H), PAPEL + (255,))
    d = ImageDraw.Draw(card)
    fk, fs = ImageFont.truetype(SEMI, 28), ImageFont.truetype(SEMI, 26)
    d.rectangle([48, 46, 58, 76], fill=OURO)
    d.text((74, 40), "DE CADA R$ 3 QUE O BRASIL PRODUZ", font=fk, fill=OURO)
    vira = ease((t - falar) / 0.25)
    for i in range(3):
        k = ease((t - 0.12 * i) / 0.3)
        if k <= 0:
            continue
        cor = VERDE + (255,)
        if i == 2 and vira > 0:
            cor = tuple(int(VERDE[j] + (VERM[j] - VERDE[j]) * vira) for j in range(3)) + (255,)
        n = nota(cor, "R$ 1")
        y = 104 + int(40 * (1 - k))
        n.putalpha(n.getchannel("A").point(lambda a: int(a * k)))
        card.alpha_composite(n, (48 + i * 278, y))
    if vira > 0:   # carimbo "FICA COM ELE" na terceira nota
        f = ImageFont.truetype(BLACK, 30)
        sel = Image.new("RGBA", (250, 60), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sel)
        sd.rounded_rectangle([0, 0, 249, 59], 10, fill=(255, 255, 255, 255), outline=VERM, width=4)
        tw = sd.textlength("FICA COM ELE", font=f)
        sd.text(((250 - tw) / 2, 9), "FICA COM ELE", font=f, fill=VERM)
        esc = 1.6 - 0.6 * vira
        sel = sel.resize((int(250 * esc), int(60 * esc)), Image.LANCZOS).rotate(-8, resample=Image.BICUBIC, expand=True)
        sel.putalpha(sel.getchannel("A").point(lambda a: int(a * vira)))
        card.alpha_composite(sel, (48 + 2 * 278 + 115 - sel.width // 2, 200 - sel.height // 2 + 10))
    d.line([48, 290, W - 48, 290], fill=(214, 208, 196), width=2)
    fb = ImageFont.truetype(BLACK, 40)
    d.text((48, 304), "Carga tributária: 32,4% do PIB", font=fb, fill=TINTA)
    d.text((48, 358), "2025 · maior da série · fonte: Tesouro Nacional", font=fs, fill=(112, 112, 108))
    return sombra(arredondar(card))


def urna(t, digitos=1.15):
    """Tela de urna. `digitos` = quando ele fala "22" (desde a entrada do card)."""
    W, H = 760, 400
    card = Image.new("RGBA", (W, H), (226, 222, 212, 255))
    d = ImageDraw.Draw(card)
    # tela
    d.rounded_rectangle([28, 28, 460, 372], 12, fill=(250, 250, 248), outline=(150, 146, 138), width=3)
    fk = ImageFont.truetype(SEMI, 26)
    d.text((52, 48), "SEU VOTO PARA", font=fk, fill=(90, 90, 90))
    d.text((52, 80), "PRESIDENTE", font=ImageFont.truetype(BLACK, 46), fill=TINTA)
    fd = ImageFont.truetype(BLACK, 110)
    for i in range(2):
        x0 = 60 + i * 150
        d.rectangle([x0, 160, x0 + 120, 320], outline=TINTA, width=4)
        k = ease((t - digitos - 0.18 * i) / 0.15)
        if k > 0:
            tw = d.textlength("2", font=fd)
            d.text((x0 + (120 - tw) / 2, 168 - int(20 * (1 - k))), "2", font=fd, fill=TINTA + (int(255 * k),))
    # teclado
    ft = ImageFont.truetype(BLACK, 30)
    for n, (cx, cy) in zip("123456789", [(500 + 80 * (j % 3), 40 + 66 * (j // 3)) for j in range(9)]):
        aceso = n == "2" and any(0 <= t - digitos - 0.18 * i < 0.15 for i in range(2))
        d.rounded_rectangle([cx, cy, cx + 66, cy + 54], 8, fill=(255, 210, 120) if aceso else (40, 40, 44))
        d.text((cx + 24, cy + 8), n, font=ft, fill=TINTA if aceso else (240, 240, 240))
    conf = ease((t - digitos - 0.55) / 0.2)
    verde = tuple(int(c * (0.55 + 0.45 * conf)) for c in (40, 180, 70))
    d.rounded_rectangle([500, 250, 726, 330], 10, fill=verde)
    fc = ImageFont.truetype(BLACK, 34)
    tw = d.textlength("CONFIRMA", font=fc)
    d.text((613 - tw / 2, 268), "CONFIRMA", font=fc, fill=(255, 255, 255))
    if conf > 0:   # brilho do confirma
        g = Image.new("RGBA", card.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).rounded_rectangle([490, 240, 736, 340], 16, fill=(120, 255, 140, int(120 * conf)))
        card = Image.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)), card)
    d = ImageDraw.Draw(card)
    d.text((500, 348), "DOMINGO · 04/10", font=ImageFont.truetype(SEMI, 22), fill=(90, 90, 90))
    return sombra(arredondar(card))


def lula(t, xis=0.3):
    """Foto oficial (Ricardo Stuckert/PR, CC BY 2.0, Wikimedia Commons) + X vermelho desenhado em 2 traços."""
    W, H = 440, 540
    im = Image.open(os.path.join(AQUI, "foto-lula.jpg")).convert("RGB")
    esc = W / im.width
    im = im.resize((W, int(im.height * esc)), Image.LANCZOS).crop((0, 0, W, H))
    card = im.convert("RGBA")
    d = ImageDraw.Draw(card)
    m, larg = 60, 30
    for i, (a, b) in enumerate((((m, m + 20), (W - m, H - m - 40)), ((W - m, m + 20), (m, H - m - 40)))):
        k = ease((t - xis - 0.18 * i) / 0.16)
        if k > 0:
            fim = (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
            d.line([a, fim], fill=(225, 30, 30), width=larg)
            for p in (a, fim):
                d.ellipse([p[0] - larg / 2, p[1] - larg / 2, p[0] + larg / 2, p[1] + larg / 2], fill=(225, 30, 30))
    fc = ImageFont.truetype(SEMI, 16)
    d.text((W - 10 - d.textlength("Foto: Ricardo Stuckert/PR · CC BY 2.0", font=fc), H - 26),
           "Foto: Ricardo Stuckert/PR · CC BY 2.0", font=fc, fill=(255, 255, 255, 200))
    return sombra(arredondar(card))


def mov(nome, func, dur):
    shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
    for i in range(int(dur * FPS)):
        func(i / FPS).save(os.path.join(TMP, f"{i:04d}.png"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(TMP, "%04d.png"),
                    "-c:v", "qtrle", os.path.join(AQUI, nome)], check=True)
    func(dur - 0.05).save(os.path.join(AQUI, nome.replace(".mov", ".png")))
    shutil.rmtree(TMP)


if __name__ == "__main__":
    mov("c-dado.mov", dado, 3.9)   # entra 23.5 (original) -> "quase 1" em 25.45
    mov("c-urna.mov", urna, 2.1)
    mov("c-lula.mov", lula, 2.5)   # entra 28.3 -> X em "demitir" (28.6)   # entra 34.3 -> "22" em 35.45
    print("ok")
