"""Inserções do vídeo "isso precisa ser eu?" (VISÃO, 2026-09-30). Só 3 coisas, a pedido do Vitor:
card da pesquisa de Harvard (2 estados), card da notícia dos Dots, e a frase "ISSO PRECISA SER EU?".
Os cards vão no peito (camiseta preta) — o topo já tem o título dele e o meio é o rosto.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
F_BLACK = r"C:\Windows\Fonts\seguibl.ttf"
F_SEMI = r"C:\Windows\Fonts\seguisb.ttf"
F_REG = r"C:\Windows\Fonts\segoeui.ttf"
PAPEL, TINTA, CINZA = (246, 242, 234), (22, 22, 26), (112, 112, 108)
CRIMSON = (165, 28, 48)          # vermelho de Harvard
OURO = (226, 184, 88)


def sombra(card, pad=40, alpha=150):
    out = Image.new("RGBA", (card.width + 2 * pad, card.height + 2 * pad), (0, 0, 0, 0))
    s = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([pad, pad + 12, pad + card.width, pad + card.height + 12], 26,
                                        fill=(0, 0, 0, alpha))
    out = Image.alpha_composite(s.filter(ImageFilter.GaussianBlur(18)), out)
    out.alpha_composite(card, (pad, pad))
    return out


def arredondar(img, r=26):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, img.width - 1, img.height - 1], r, fill=255)
    img.putalpha(m)
    return img


def harvard(destaque):
    """Recorte de pesquisa. destaque=False: o achado. destaque=True: o achado + '2 em cada 100'."""
    W, H = 900, 400 if not destaque else 470
    c = Image.new("RGBA", (W, H), PAPEL + (255,))
    d = ImageDraw.Draw(c)
    m = 56
    d.rectangle([0, 0, W, 14], fill=CRIMSON)                       # faixa crimson no topo
    d.text((m, 46), "PESQUISA  ·  HARVARD  ·  2017", font=ImageFont.truetype(F_SEMI, 30), fill=CRIMSON)
    fh = ImageFont.truetype(F_BLACK, 58)
    d.text((m, 100), "Quem compra tempo", font=fh, fill=TINTA)
    d.text((m, 166), "vive mais satisfeito.", font=fh, fill=TINTA)
    y = 262
    if destaque:
        fn = ImageFont.truetype(F_BLACK, 58)
        d.text((m, y), "Só ", font=fn, fill=TINTA)
        x = m + d.textlength("Só ", font=fn)
        num = "2 em cada 100"
        wnum = d.textlength(num, font=fn)
        d.rounded_rectangle([x - 10, y + 8, x + wnum + 10, y + 74], 10, fill=CRIMSON)
        d.text((x, y), num, font=fn, fill=(255, 255, 255))
        d.text((x + wnum + 18, y), "fazem.", font=fn, fill=TINTA)
        y += 96
    else:
        y += 20
    d.line([m, y, W - m, y], fill=(214, 208, 196), width=2)
    d.text((m, y + 16), "Whillans et al. · PNAS, 2017 · 6.271 pessoas em 4 países",
           font=ImageFont.truetype(F_REG, 26), fill=CINZA)
    return sombra(arredondar(c))


def dots():
    """Card escuro de notícia."""
    W, H = 900, 360
    c = Image.new("RGBA", (W, H), (18, 18, 22, 255))
    d = ImageDraw.Draw(c)
    m = 56
    d.ellipse([m, 52, m + 18, 70], fill=(255, 70, 70))                  # "ao vivo"
    d.text((m + 32, 42), "NOTÍCIA  ·  29/09/2026", font=ImageFont.truetype(F_SEMI, 30), fill=(200, 200, 205))
    fh = ImageFont.truetype(F_BLACK, 62)
    d.text((m, 96), "OpenAI lança os Dots", font=fh, fill=(255, 255, 255))
    d.text((m, 176), "agentes que trabalham o dia inteiro por você",
           font=ImageFont.truetype(F_SEMI, 34), fill=OURO)
    d.line([m, 256, W - m, 256], fill=(60, 60, 68), width=2)
    d.text((m, 274), "DevDay 2026 · CNBC · TechCrunch", font=ImageFont.truetype(F_REG, 26), fill=(150, 150, 158))
    return sombra(arredondar(c), alpha=170)


def pergunta():
    """ISSO PRECISA / SER EU? — branco com 'EU?' dourado, sombra forte (fica sobre a camiseta preta e o fundo)."""
    W, H = 1000, 380
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(txt), ImageDraw.Draw(sh)
    f = ImageFont.truetype(F_BLACK, 132)
    l1 = "ISSO PRECISA"
    x1 = (W - d.textlength(l1, font=f)) / 2
    for dd, cor, off in ((ds, (0, 0, 0, 220), 6), (d, (255, 255, 255, 255), 0)):
        dd.text((x1, 20 + off), l1, font=f, fill=cor)
    a, b = "SER ", "EU?"
    wa, wb = d.textlength(a, font=f), d.textlength(b, font=f)
    x2 = (W - wa - wb) / 2
    for dd, off, c1, c2 in ((ds, 6, (0, 0, 0, 220), (0, 0, 0, 220)), (d, 0, (255, 255, 255, 255), OURO + (255,))):
        dd.text((x2, 180 + off), a, font=f, fill=c1)
        dd.text((x2 + wa, 180 + off), b, font=f, fill=c2)
    return Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), txt)


if __name__ == "__main__":
    harvard(False).save(os.path.join(AQUI, "c-harvard.png"))
    harvard(True).save(os.path.join(AQUI, "c-harvard2.png"))
    dots().save(os.path.join(AQUI, "c-dots.png"))
    pergunta().save(os.path.join(AQUI, "c-pergunta.png"))
    print("ok")
