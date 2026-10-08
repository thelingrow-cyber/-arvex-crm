"""Cards dos 4 arquivos de contexto — arte própria em PIL.

Cada card é a "janela" de um arquivo: cabeçalho com o nome e as linhas que vão dentro.
Mesma paleta dos outros vídeos (off-white quente, ouro, azul-ardósia).
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H = 1120, 630

FUNDO = (236, 231, 222)
PAPEL = (250, 248, 244)
GRAFITE = (62, 66, 72)
OURO = (214, 158, 66)
AZUL = (94, 128, 150)
CLARO = (186, 182, 174)

F_NOME = ImageFont.truetype(r"C:\Windows\Fonts\seguisb.ttf", 46)
F_ITEM = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 38)


def base():
    im = Image.new("RGB", (W, H), FUNDO)
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse([-W * 0.30, -H * 0.42, W * 1.30, H * 1.42], fill=60)
    v = v.filter(ImageFilter.GaussianBlur(120))
    return Image.composite(im, Image.new("RGB", (W, H), (212, 208, 200)), v)


def arquivo(nome, itens, cor, saida):
    """Uma janela de arquivo: barra de título com o nome e as linhas de dentro."""
    im = base()
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, y0, x1, y1 = 74, 66, W - 74, H - 66
    ImageDraw.Draw(sombra).rounded_rectangle([x0, y0 + 12, x1, y1 + 12], 18, fill=(0, 0, 0, 70))
    im = Image.alpha_composite(im.convert("RGBA"), sombra.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x0, y0, x1, y1], 18, fill=PAPEL)
    d.rounded_rectangle([x0, y0, x1, y0 + 92], 18, fill=cor)
    d.rectangle([x0, y0 + 62, x1, y0 + 92], fill=cor)            # canto reto embaixo da barra
    d.text((x0 + 34, y0 + 46), nome, font=F_NOME, fill=PAPEL, anchor="lm")
    for i, it in enumerate(itens):
        yy = y0 + 92 + 54 + i * 62
        d.ellipse([x0 + 40, yy - 7, x0 + 54, yy + 7], fill=cor)   # marcador
        d.text((x0 + 78, yy), it, font=F_ITEM, fill=GRAFITE, anchor="lm")
    im.convert("RGB").save(os.path.join(AQUI, saida))


if __name__ == "__main__":
    arquivo("company.md", ["o que você faz", "quem você ajuda",
                           "de onde vem o dinheiro", "o que te torna diferente"],
            AZUL, "c-empresa.png")
    arquivo("customer.md", ["as dores dele", "os medos", "as objeções",
                            "a linguagem dele"], OURO, "c-cliente.png")
    arquivo("offer.md", ["pacotes", "entregáveis", "preço", "prova e promessa"],
            AZUL, "c-oferta.png")
    arquivo("voice.md", ["como você fala", "as palavras que usa",
                         "as palavras que recusa", "exemplos reais"], OURO, "c-voz.png")
    print("4 cards gerados")
