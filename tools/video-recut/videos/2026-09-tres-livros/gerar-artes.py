"""Cards do vídeo "três livros previram como você vai comprar".

Capas reais: Gates = Wikipedia (arquivo da página do livro, sem adesivo); Searls e Harari = Open Library. Mesmo acabamento nos três livros: etiqueta dourada
com o ano no canto de cima e faixa escura embaixo com o título em português. A etiqueta e a faixa também
cobrem o adesivo de preço e o selo de CD-ROM da capa escaneada do Gates, sem retoque na foto.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
BLACK = r"C:\Windows\Fonts\seguibl.ttf"
SEMI = r"C:\Windows\Fonts\seguisb.ttf"
OURO = (221, 184, 112)
TINTA = (18, 18, 22)

LIVROS = [
    ("capa-gates-wiki.jpg", "1995", "A Estrada do Futuro", "Bill Gates", 0.03),
    ("capa-searls.jpg", "2012", "A Economia da Intenção", "Doc Searls", 0.03),
    ("capa-harari.jpg", "2018", "21 Lições para o Século 21", "Yuval Noah Harari", 0.03),
]


def capa(arq, ano, titulo, autor, topo_ano=0.03, alt=560):
    im = Image.open(os.path.join(AQUI, arq)).convert("RGB")
    w = int(im.width * alt / im.height)
    im = im.resize((w, alt), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.4, percent=60, threshold=2))
    card = Image.new("RGBA", (w, alt), (0, 0, 0, 0))
    card.paste(im, (0, 0))
    d = ImageDraw.Draw(card, "RGBA")
    # faixa escura embaixo (degradê) com título e autor
    faixa = 220
    grad = Image.new("L", (1, faixa))
    for y in range(faixa):
        grad.putpixel((0, y), int(245 * min(1, (y / faixa) * 2.6)))
    grad = grad.resize((w, faixa))
    preto = Image.new("RGBA", (w, faixa), (10, 10, 14, 255))
    preto.putalpha(grad)
    card.alpha_composite(preto, (0, alt - faixa))
    tam = 36
    while ImageFont.truetype(BLACK, tam).getlength(titulo) > w - 44 and tam > 18:
        tam -= 1
    ft = ImageFont.truetype(BLACK, tam)
    fa = ImageFont.truetype(SEMI, 24)
    d.text((22, alt - 88), titulo, font=ft, fill=(255, 255, 255, 255))
    d.text((22, alt - 44), autor, font=fa, fill=OURO + (255,))
    # etiqueta do ano no canto de cima
    fy = ImageFont.truetype(BLACK, 46)
    tw = d.textlength(ano, font=fy)
    x1, y0 = w - 14, int(alt * topo_ano)
    x0 = x1 - tw - 40
    d.rounded_rectangle([x0, y0, x1, y0 + 72], 14, fill=OURO + (255,))
    d.text((x0 + 20, y0 + 4), ano, font=fy, fill=TINTA + (255,))
    # canto arredondado + sombra
    m = Image.new("L", card.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, alt - 1], 18, fill=255)
    card.putalpha(Image.composite(card.getchannel("A"), Image.new("L", card.size, 0), m))
    return sombra(card)


def sombra(card, pad=36):
    out = Image.new("RGBA", (card.width + 2 * pad, card.height + 2 * pad), (0, 0, 0, 0))
    s = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([pad, pad + 10, pad + card.width, pad + card.height + 10], 18, fill=(0, 0, 0, 150))
    out = Image.alpha_composite(s.filter(ImageFilter.GaussianBlur(16)), out)
    out.alpha_composite(card, (pad, pad))
    return out


def tres():
    """Os três lado a lado, em leque."""
    cs = [capa(*l, alt=430) for l in LIVROS]
    W, H = 1060, 620
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for c, ang, dx, dy in zip(cs, (7, 0, -7), (-300, 0, 300), (40, 0, 40)):
        r = c.rotate(ang, resample=Image.BICUBIC, expand=True)
        out.alpha_composite(r, ((W - r.width) // 2 + dx, (H - r.height) // 2 + dy))
    # o do meio por cima
    r = cs[1]
    out.alpha_composite(r, ((W - r.width) // 2, (H - r.height) // 2))
    return out


def noticia():
    """Recorte de notícia: Meta Muse compra sozinho nas lojas da Shopify."""
    W, H = 900, 330
    card = Image.new("RGBA", (W, H), (246, 242, 234, 255))
    d = ImageDraw.Draw(card)
    fk, ft, fs = ImageFont.truetype(SEMI, 28), ImageFont.truetype(BLACK, 50), ImageFont.truetype(SEMI, 26)
    d.rectangle([48, 50, 58, 80], fill=(196, 140, 52))
    d.text((74, 44), "NOTÍCIA · 21/09/2026", font=fk, fill=(196, 140, 52))
    d.text((48, 100), "Agente da Meta passa a", font=ft, fill=TINTA)
    d.text((48, 162), "comprar nas lojas da Shopify", font=ft, fill=TINTA)
    d.line([48, 250, W - 48, 250], fill=(214, 208, 196), width=2)
    d.text((48, 264), "Meta Muse + Shop Pay · fonte: PYMNTS", font=fs, fill=(112, 112, 108))
    m = Image.new("L", card.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, W - 1, H - 1], 20, fill=255)
    card.putalpha(m)
    return sombra(card)


if __name__ == "__main__":
    for i, l in enumerate(LIVROS):
        capa(*l).save(os.path.join(AQUI, f"c-livro{i + 1}.png"))
    tres().save(os.path.join(AQUI, "c-tres.png"))
    noticia().save(os.path.join(AQUI, "c-meta.png"))
    print("ok")
