"""Cards de pesquisa do vídeo "11 leis da psicologia humana".

Um card por lei alternada (2, 4, 6, 8, 10): recorte de papel com o achado em uma frase e a fonte
original embaixo. Arte própria em PIL (sem print de matéria de baixa qualidade).
Fontes conferidas: ver o README do vídeo.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H = 1120, 630
PAPEL = (246, 242, 234)
TINTA = (26, 28, 32)
CINZA = (112, 112, 108)
OURO = (196, 140, 52)
F_BOLD = r"C:\Windows\Fonts\seguibl.ttf"
F_SEMI = r"C:\Windows\Fonts\seguisb.ttf"
F_REG = r"C:\Windows\Fonts\segoeui.ttf"

CARDS = [
    ("c-yerkes.png", "PESQUISA · 1908",
     "Pressão ajuda até um ponto. Passou dele, o desempenho cai.",
     "Yerkes & Dodson · Journal of Comparative Neurology and Psychology"),
    ("c-weber.png", "PESQUISA · 1860",
     "A gente não sente o valor. Sente a diferença.",
     "Gustav Fechner · Elemente der Psychophysik"),
    ("c-zipf.png", "LIVRO · 1949",
     "Entre dois caminhos, as pessoas escolhem o que dá menos trabalho.",
     "George K. Zipf · Human Behavior and the Principle of Least Effort"),
    ("c-picofim.png", "PESQUISA · 1993",
     "Na água gelada, 69% preferiram repetir a sessão mais longa. Ela terminava melhor.",
     "Kahneman, Fredrickson, Schreiber & Redelmeier · Psychological Science"),
    ("c-pigmaliao.png", "PESQUISA · 1968",
     "Alunos de quem o professor esperava mais passaram a render mais.",
     "Rosenthal & Jacobson · Pygmalion in the Classroom"),
]


def quebrar(d, texto, fonte, largura):
    linhas, atual = [], ""
    for p in texto.split():
        t = (atual + " " + p).strip()
        if d.textlength(t, font=fonte) <= largura:
            atual = t
        else:
            linhas.append(atual)
            atual = p
    return linhas + [atual]


def card(nome, kicker, frase, fonte_txt):
    im = Image.new("RGB", (W, H), PAPEL)
    # textura leve de papel
    ruido = Image.effect_noise((W, H), 14).convert("RGB").filter(ImageFilter.GaussianBlur(0.6))
    im = Image.blend(im, ruido, 0.035)
    d = ImageDraw.Draw(im)
    m = 64
    fk = ImageFont.truetype(F_SEMI, 30)
    d.rectangle([m, m + 6, m + 10, m + 36], fill=OURO)
    d.text((m + 26, m), kicker, font=fk, fill=OURO)
    tam = 68
    while True:
        ff = ImageFont.truetype(F_BOLD, tam)
        linhas = quebrar(d, frase, ff, W - 2 * m)
        if len(linhas) <= 3 or tam <= 50:
            break
        tam -= 4
    y = m + 78
    for ln in linhas:
        d.text((m, y), ln, font=ff, fill=TINTA)
        y += int(tam * 1.18)
    d.line([m, H - m - 58, W - m, H - m - 58], fill=(214, 208, 196), width=2)
    fs = ImageFont.truetype(F_REG, 28)
    fonte_linhas = quebrar(d, fonte_txt, fs, W - 2 * m)
    d.text((m, H - m - 40), fonte_linhas[0], font=fs, fill=CINZA)
    im.save(os.path.join(AQUI, nome))


if __name__ == "__main__":
    for c in CARDS:
        card(*c)
        print("ok", c[0])
