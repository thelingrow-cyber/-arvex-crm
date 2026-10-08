"""Se eu fosse presidente — v2 (layout da referência + motions caprichados).

Layout: título fixo no topo o vídeo inteiro · inserção EMBAIXO do rosto (centro y=LOW_Y) desde o 1º quadro ·
4 momentos em TELA CHEIA (3º×35º, DIA 1, Vale do Silício, usina solar) · sem legenda corrida (o título faz o papel).
Base de vídeo: work/base.mp4 (faixa 0–5,10 + corte com zoom) — gerada por montar.py base.

uso: python montar2.py [titulo motions compor]
"""
import functools, math, os, random, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(AQUI))))
WORK = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "work", "2026-10-presidente-ia")
ORIG = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "FE55C986-B422-4E8F-86E1-7ACC24B82C9F.mp4")
SAIDA = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "2026-10-presidente-ia-v2.mp4")
IMG = os.path.join(RAIZ, "output", "midia", "2026-10-07")
DUR = 100.97

BLACK = r"C:\Windows\Fonts\seguibl.ttf"
BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
SEMI = r"C:\Windows\Fonts\seguisb.ttf"
VERDE, AMARELO, VERMELHO, AZUL = (22, 168, 90), (247, 200, 40), (232, 64, 70), (30, 60, 150)
BRANCO, CINZA, FUNDO = (255, 255, 255), (150, 155, 168), (12, 14, 20)
LW, LH, PAD = 860, 480, 34       # inserção de baixo
LOW_Y = 1395                      # centro vertical da inserção de baixo
FW, FH = 1080, 1920


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def w(n):
    return os.path.join(WORK, n)


@functools.lru_cache(None)
def F(path, size):
    return ImageFont.truetype(path, size)


def cl(x):
    return max(0.0, min(1.0, x))


def ease(x):
    return 1 - (1 - cl(x)) ** 3


def back(x, s=1.9):
    x = cl(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def lerp(a, b, x):
    return a + (b - a) * x


def mix(c1, c2, x):
    return tuple(int(lerp(a, b, cl(x))) for a, b in zip(c1, c2))


def texto(d, xy, txt, fonte, cor, anchor="mm", sombra=True, stroke=0):
    if sombra:
        d.text((xy[0] + 3, xy[1] + 5), txt, font=fonte, fill=(0, 0, 0, 150), anchor=anchor)
    d.text(xy, txt, font=fonte, fill=cor, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))


def escala_txt(img, xy, txt, fonte, cor, s, anchor="mm"):
    """Texto com escala s (para pops). Desenha em camada e redimensiona."""
    if s <= 0.01:
        return
    tmp = Image.new("RGBA", (1, 1)); dd = ImageDraw.Draw(tmp)
    bb = dd.textbbox((0, 0), txt, font=fonte)
    tw, th = bb[2] - bb[0] + 20, bb[3] - bb[1] + 30
    lay = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((10 - bb[0], 10 - bb[1]), txt, font=fonte, fill=cor)
    lay = lay.resize((max(1, int(tw * s)), max(1, int(th * s))), Image.BICUBIC)
    img.alpha_composite(lay, (int(xy[0] - lay.width / 2), int(xy[1] - lay.height / 2)))


@functools.lru_cache(None)
def abrir(nome):
    return Image.open(os.path.join(IMG, nome)).convert("RGB")


def cobrir(im, W, H, z=1.0, fx=0.5, fy=0.5):
    e = max(W / im.width, H / im.height) * z
    r = im.resize((int(im.width * e) + 2, int(im.height * e) + 2), Image.BILINEAR)
    x0 = int((r.width - W) * fx); y0 = int((r.height - H) * fy)
    return r.crop((x0, y0, x0 + W, y0 + H)).convert("RGBA")


@functools.lru_cache(None)
def grao(W, H):
    rnd = random.Random(7)
    g = Image.effect_noise((W, H), 22).convert("L")
    return Image.merge("RGBA", (g, g, g, Image.new("L", (W, H), 14)))


def fundo_escuro(W, H, c1=(26, 30, 44), c2=FUNDO):
    g = Image.radial_gradient("L").resize((W, H))
    a = Image.new("RGBA", (W, H), c1 + (255,)); b = Image.new("RGBA", (W, H), c2 + (255,))
    return Image.composite(b, a, g)


@functools.lru_cache(None)
def _fundo(W, H, c1, c2):
    return fundo_escuro(W, H, c1, c2)


def painel():
    c = _fundo(LW, LH, (30, 34, 50), FUNDO).copy()
    return c


def arredondar(c, r=30):
    m = Image.new("L", c.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, c.width - 1, c.height - 1], r, fill=255)
    c.putalpha(ImageChops.multiply(c.getchannel("A"), m))
    return c


def emoldurar(c):
    c = arredondar(c)
    out = Image.new("RGBA", (LW + 2 * PAD, LH + 2 * PAD), (0, 0, 0, 0))
    s = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([PAD, PAD + 12, PAD + LW, PAD + LH + 12], 30, fill=(0, 0, 0, 160))
    out = Image.alpha_composite(s.filter(ImageFilter.GaussianBlur(18)), out)
    out.alpha_composite(c, (PAD, PAD))
    return out


def rodape(d, txt, W=LW, H=LH):
    d.text((W / 2, H - 24), txt, font=F(SEMI, 20), fill=CINZA, anchor="mm")


def brilho_passando(c, t, t0, dur=0.9):
    """Faixa de luz diagonal atravessando (polimento)."""
    p = (t - t0) / dur
    if not 0 < p < 1:
        return
    W, H = c.size
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = lerp(-W * 0.4, W * 1.2, ease(p))
    ImageDraw.Draw(lay).polygon([(x, 0), (x + 90, 0), (x - 110, H), (x - 200, H)], fill=(255, 255, 255, 60))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))


# ---------------- bandeiras desenhadas ----------------
def bandeira(pais, w_, h_):
    b = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
    if pais == "BR":
        d.rectangle([0, 0, w_, h_], fill=(0, 151, 57))
        d.polygon([(w_ * .5, h_ * .1), (w_ * .92, h_ * .5), (w_ * .5, h_ * .9), (w_ * .08, h_ * .5)], fill=(254, 221, 0))
        r = h_ * .24; d.ellipse([w_ / 2 - r, h_ / 2 - r, w_ / 2 + r, h_ / 2 + r], fill=(0, 39, 118))
    elif pais == "US":
        for k in range(13):
            d.rectangle([0, k * h_ / 13, w_, (k + 1) * h_ / 13], fill=(178, 34, 52) if k % 2 == 0 else BRANCO)
        d.rectangle([0, 0, w_ * .42, h_ * 7 / 13], fill=(60, 59, 110))
    elif pais == "IN":
        d.rectangle([0, 0, w_, h_ / 3], fill=(255, 153, 51))
        d.rectangle([0, h_ / 3, w_, 2 * h_ / 3], fill=BRANCO)
        d.rectangle([0, 2 * h_ / 3, w_, h_], fill=(19, 136, 8))
        r = h_ * .13; d.ellipse([w_ / 2 - r, h_ / 2 - r, w_ / 2 + r, h_ / 2 + r], outline=(0, 0, 128), width=3)
    return arredondar(b, 8)


# ================= INSERÇÕES DE BAIXO =================
def m_abertura(t):                    # 0 → 6,25 — Planalto + rede de IA; selo "TOP 3?" no "três maiores"
    c = cobrir(abrir("003938-pres-abertura.png"), LW, LH, 1.04 + 0.07 * t / 6.25, 0.5, 0.45)
    brilho_passando(c, t, 0.25)
    a = back((t - 3.0) / 0.35)
    if t > 3.0:
        selo = Image.new("RGBA", (260, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(selo)
        d.ellipse([10, 10, 250, 250], fill=AMARELO + (255,), outline=(0, 0, 0, 90), width=4)
        d.text((130, 108), "TOP", font=F(BLACK, 60), fill=(20, 20, 20), anchor="mm")
        d.text((130, 172), "3", font=F(BLACK, 92), fill=(0, 120, 60), anchor="mm")
        s = 0.62 * a
        selo = selo.rotate(-12 + 12 * cl(t - 3.0), resample=Image.BICUBIC).resize((max(1, int(260 * s)), max(1, int(260 * s))))
        c.alpha_composite(selo, (LW - 40 - selo.width, 30))
    return c


def m_podio(t):                       # 6,30 → 12,30
    c = painel(); d = ImageDraw.Draw(c)
    d.text((LW / 2, 42), "QUEM MAIS USA O CHATGPT NO MUNDO", font=F(BLACK, 30), fill=AMARELO, anchor="mm")
    base_y = LH - 96
    cols = [("IN", "ÍNDIA", "2º", 230, 11.98 - 6.30, 190), ("US", "EUA", "1º", 430, 11.10 - 6.30, 250),
            ("BR", "BRASIL", "3º", 630, 0.55, 140)]
    for pais, nome, pos, cx, quando, alt in cols:
        p = back((t - quando) / 0.55, 1.4)
        h = alt * p
        br = pais == "BR"
        cor = VERDE if br else (64, 70, 90)
        if h > 2:
            if br:
                glow = Image.new("RGBA", c.size, (0, 0, 0, 0))
                ImageDraw.Draw(glow).rounded_rectangle([cx - 95, base_y - h - 10, cx + 95, base_y + 6], 18, fill=VERDE + (120,))
                c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)))
                d = ImageDraw.Draw(c)
            d.rounded_rectangle([cx - 80, base_y - h, cx + 80, base_y], 14, fill=cor)
            d.text((cx, base_y - h + 46), pos, font=F(BLACK, 56), fill=BRANCO, anchor="mm")
            fl = bandeira(pais, 96, 64)
            c.alpha_composite(fl, (cx - 48, int(base_y - h - 84)))
            d = ImageDraw.Draw(c)
            d.text((cx, base_y + 26), nome, font=F(BLACK, 30), fill=BRANCO if (br or p > 0.9) else CINZA, anchor="mm")
        else:
            d.text((cx, base_y - 30), "?", font=F(BLACK, 60), fill=(70, 74, 90), anchor="mm")
    d.line([(120, base_y), (LW - 120, base_y)], fill=(80, 86, 104), width=4)
    rodape(d, "Fonte: OpenAI, estudo de uso no Brasil (ago/2025)")
    return c


def m_carimbos(t):                    # 16,30 → 19,35
    c = painel(); d = ImageDraw.Draw(c)
    meio = LW // 2
    d.line([(meio, 40), (meio, LH - 40)], fill=(60, 64, 80), width=3)
    # carrinho
    x, y = meio / 2, 180
    d.line([(x - 120, y - 70), (x - 90, y - 70), (x - 60, y + 40), (x + 90, y + 40), (x + 115, y - 40), (x - 75, y - 40)], fill=BRANCO, width=12, joint="curve")
    for k in (-30, 70):
        d.ellipse([x + k - 16, y + 60, x + k + 16, y + 92], fill=BRANCO)
    # fábrica
    x2 = meio + meio / 2
    d.polygon([(x2 - 120, y + 90), (x2 - 120, y - 10), (x2 - 60, y + 25), (x2 - 60, y - 10), (x2, y + 25), (x2, y - 10),
               (x2 + 60, y + 25), (x2 + 60, y - 90), (x2 + 110, y - 90), (x2 + 110, y + 90)], fill=(110, 116, 132))
    for k, (txt, cor, quando, cx, ok) in enumerate((("CLIENTE", VERDE, 0.94, meio / 2, True),
                                                     ("FABRICANTE", VERMELHO, 2.26, meio + meio / 2, False))):
        p = (t - quando) / 0.22
        if p <= 0:
            continue
        s = lerp(2.2, 1.0, ease(p))
        st = Image.new("RGBA", (420, 130), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([6, 6, 414, 124], 18, outline=cor, width=10)
        sd.text((180, 66), txt, font=F(BLACK, 44), fill=cor, anchor="mm")
        if ok:
            sd.line([(352, 66), (370, 88), (400, 40)], fill=cor, width=12, joint="curve")
        else:
            sd.line([(356, 44), (398, 88)], fill=cor, width=12); sd.line([(398, 44), (356, 88)], fill=cor, width=12)
        st = st.rotate(-8 if ok else 8, resample=Image.BICUBIC, expand=True)
        st = st.resize((int(st.width * s), int(st.height * s)))
        st.putalpha(st.getchannel("A").point(lambda v: int(v * cl(p * 2))))
        c.alpha_composite(st, (int(cx - st.width / 2), int(345 - st.height / 2)))
        if not ok and p > 1:
            if 1 < p < 1.6:
                c = c.transform(c.size, Image.AFFINE, (1, 0, random.uniform(-6, 6), 0, 1, random.uniform(-4, 4)))
    return c


def silhueta(d, x, y, cor, passo=0.0, esc=1.0):
    r = 15 * esc
    d.ellipse([x - r, y, x + r, y + 2 * r], fill=cor)
    d.rounded_rectangle([x - 18 * esc, y + 2 * r + 4, x + 18 * esc, y + 2 * r + 62 * esc], int(14 * esc), fill=cor)
    sw = 14 * math.sin(passo) * esc
    d.line([(x - 7 * esc, y + 2 * r + 58 * esc), (x - 7 * esc + sw, y + 2 * r + 96 * esc)], fill=cor, width=int(11 * esc))
    d.line([(x + 7 * esc, y + 2 * r + 58 * esc), (x + 7 * esc - sw, y + 2 * r + 96 * esc)], fill=cor, width=int(11 * esc))


def aviao(d, x, y, s=1.0, cor=BRANCO, ang=0.0):
    pts = [(-70, 0), (60, -6), (80, 0), (60, 6), (-70, 6), (-10, 2), (-40, 40), (-25, 40), (20, 4), (-10, -2), (-40, -40), (-25, -40), (20, -4),
           (-60, -2), (-75, -22), (-65, -22), (-50, 0)]
    ca, sa = math.cos(ang), math.sin(ang)
    corpo = [(x + s * (px * ca - py * sa), y + s * (px * sa + py * ca)) for px, py in pts[:5]]
    asa1 = [(x + s * (px * ca - py * sa), y + s * (px * sa + py * ca)) for px, py in pts[5:9]]
    asa2 = [(x + s * (px * ca - py * sa), y + s * (px * sa + py * ca)) for px, py in pts[9:13]]
    cauda = [(x + s * (px * ca - py * sa), y + s * (px * sa + py * ca)) for px, py in pts[13:]]
    for poly in (corpo, asa1, asa2, cauda):
        d.polygon(poly, fill=cor)


def m_partida(t):                     # 23,30 → 30,90
    c = painel(); d = ImageDraw.Draw(c)
    chao = 400
    d.line([(30, chao + 2), (LW - 30, chao + 2)], fill=(70, 76, 94), width=4)
    t70 = 26.56 - 23.30
    sai = cl((t - t70) / 2.2)
    decola = cl((t - (28.62 - 23.30)) / 1.8)
    # avião na pista à direita
    ax = lerp(LW - 120, LW + 260, ease(decola) ** 1.6)
    ay = lerp(chao - 30, chao - 330, ease(decola) ** 1.3)
    if decola > 0:
        for k in range(14):
            q = k / 14
            d.ellipse([ax - 90 - q * 220 - 6, ay + 10 + q * 140 * decola - 6, ax - 90 - q * 220 + 6, ay + 10 + q * 140 * decola + 6],
                      fill=(255, 255, 255, int(110 * (1 - q))))
    aviao(d, ax, ay, 0.9, BRANCO, -0.35 * ease(decola))
    for k in range(10):
        x0 = 60 + k * 52
        if k >= 3:
            prog = cl(sai * 1.3 - (k - 3) * 0.06)
            x = lerp(x0, LW - 150, ease(prog))
            cor = mix((230, 232, 240), VERMELHO, prog * 2)
            alpha = int(255 * (1 - cl((decola - 0.1) * 3))) if prog >= 0.98 else 255
            silhueta(d, x, chao - 136, cor + (alpha,), passo=t * 12 + k if 0 < prog < 1 else 0, esc=1.0)
        else:
            silhueta(d, x0, chao - 136, (230, 232, 240))
    if t > t70:
        s = back((t - t70) / 0.35)
        escala_txt(c, (230, 105), "70%", F(BLACK, 120), VERMELHO + (255,), s)
        d = ImageDraw.Draw(c)
        if t > t70 + 0.35:
            d.text((470, 78), "NÃO PENSAM", font=F(BLACK, 40), fill=BRANCO, anchor="lm")
            d.text((470, 128), "EM VOLTAR", font=F(BLACK, 40), fill=BRANCO, anchor="lm")
    else:
        d.text((LW / 2, 70), "CIENTISTAS BRASILEIROS QUE MORAM FORA", font=F(BLACK, 30), fill=AMARELO, anchor="mm")
    rodape(d, "Fonte: Revista Pesquisa FAPESP (mai/2026)")
    return c


def calendario(c, cx, cy, topo, numero, s=1.0, rot=0.0):
    W_, H_ = int(300 * s), int(320 * s)
    pg = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(pg)
    d.rounded_rectangle([0, 0, W_ - 1, H_ - 1], int(26 * s), fill=(248, 248, 250))
    d.rounded_rectangle([0, 0, W_ - 1, int(92 * s)], int(26 * s), fill=VERMELHO)
    d.rectangle([0, int(60 * s), W_ - 1, int(92 * s)], fill=VERMELHO)
    d.text((W_ / 2, 48 * s), topo, font=F(BLACK, int(40 * s)), fill=BRANCO, anchor="mm")
    d.text((W_ / 2, 206 * s), numero, font=F(BLACK, int(130 * s)), fill=(20, 22, 30), anchor="mm")
    for k in (0.3, 0.7):
        d.ellipse([W_ * k - 12 * s, -10 * s, W_ * k + 12 * s, 14 * s], fill=(70, 70, 80))
    if rot:
        pg = pg.rotate(rot, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", (pg.width + 60, pg.height + 60), (0, 0, 0, 0))
    sh.alpha_composite(Image.new("RGBA", pg.size, (0, 0, 0, 140)), (30, 42))
    sh.putalpha(ImageChops.multiply(sh.getchannel("A"), Image.new("L", sh.size, 255)))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (int(cx - sh.width / 2), int(cy - sh.height / 2)))
    m = Image.new("RGBA", pg.size, (0, 0, 0, 0)); m.alpha_composite(pg)
    c.alpha_composite(m, (int(cx - pg.width / 2), int(cy - pg.height / 2)))


def capitulo_baixo(t, topo, numero, frase, quando, flips=0):
    c = painel(); d = ImageDraw.Draw(c)
    p = back(t / 0.45, 1.3)
    if flips and t < 0.9:              # páginas folheando antes de parar
        k = int(t / 0.12)
        num = ["1", "7", "14", "21", "30", numero][min(k, 5)] if numero.isdigit() else numero
        calendario(c, 190, LH / 2 + 10 + 40 * (1 - p), "DIA" if t < 0.6 else topo, num if t < 0.6 else numero, 0.95, rot=4 * math.sin(t * 20))
    else:
        calendario(c, 190, LH / 2 + 10 + 40 * (1 - p), topo, numero, 0.95, rot=-4)
    d = ImageDraw.Draw(c)
    a = ease((t - quando) / 0.3)
    if a > 0:
        lay = Image.new("RGBA", c.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for k, linha in enumerate(frase):
            ld.text((390 + 30 * (1 - a), 150 + k * 78), linha, font=F(BLACK, 58), fill=BRANCO if k < len(frase) - 1 else AMARELO)
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
        c.alpha_composite(lay)
    return c


def m_mes(t):                         # 41,70 → 44,95
    c = capitulo_baixo(t, "MÊS", "1", ["DINHEIRO PRA", "QUEM", "FABRICA"], 43.58 - 41.70, flips=1)
    if t > 43.58 - 41.70:              # moedas caindo
        d = ImageDraw.Draw(c)
        for k in range(9):
            q = (t - (43.58 - 41.70)) * 1.6 - k * 0.12
            if q > 0:
                x = 420 + (k * 53) % 380; y = -40 + (q % 1.2) * 520
                d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=AMARELO, outline=(190, 140, 0), width=4)
    return c


def m_ano(t):                         # 68,10 → 70,95
    return capitulo_baixo(t, "ANO", "1", ["A", "MÁQUINA"], 70.30 - 68.10, flips=1)


def m_cofre(t):                       # 51,80 → 58,30
    c = painel(); d = ImageDraw.Draw(c)
    d.text((LW / 2, 40), "ESTADOS UNIDOS · 1979", font=F(BLACK, 30), fill=AMARELO, anchor="mm")
    abre = 57.42 - 51.80
    cx, cy, R = 230, 265, 150
    d.rounded_rectangle([cx - R - 30, cy - R - 30, cx + R + 30, cy + R + 30], 30, fill=(70, 76, 92))
    d.ellipse([cx - R - 8, cy - R - 8, cx + R + 8, cy + R + 8], fill=(36, 40, 52))
    o = ease((t - abre) / 0.7)
    giro = (t * 40 if t < abre else abre * 40 + ease((t - abre) / 0.5) * 360)
    # porta (gira e "abre" achatando para a esquerda)
    pw = int(2 * R * (1 - 0.85 * o))
    porta = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0)); pd = ImageDraw.Draw(porta)
    pd.ellipse([0, 0, 2 * R - 1, 2 * R - 1], fill=(150, 158, 176), outline=(90, 96, 112), width=10)
    for k in range(6):
        ang = math.radians(giro + k * 60)
        pd.line([(R, R), (R + 0.62 * R * math.cos(ang), R + 0.62 * R * math.sin(ang))], fill=(60, 64, 78), width=14)
    pd.ellipse([R - 30, R - 30, R + 30, R + 30], fill=(60, 64, 78))
    pd.text((R, R + 92), "APOSENTADORIA", font=F(BLACK, 22), fill=(40, 44, 56), anchor="mm")
    porta = porta.resize((max(1, pw), 2 * R))
    if o > 0:                          # interior com moedas
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(20, 22, 30))
        for k in range(7):
            d.ellipse([cx - 60 + k * 18, cy + 60 - (k % 3) * 18, cx - 20 + k * 18, cy + 100 - (k % 3) * 18], fill=AMARELO)
    c.alpha_composite(porta, (cx - R, cy - R))
    d = ImageDraw.Draw(c)
    # destino
    bx = 650
    d.rounded_rectangle([bx - 140, cy - 95, bx + 140, cy + 95], 22, fill=(30, 34, 46), outline=VERDE if o > 0 else (90, 96, 112), width=6)
    d.text((bx, cy - 22), "EMPRESA", font=F(BLACK, 38), fill=BRANCO, anchor="mm")
    d.text((bx, cy + 26), "NOVA", font=F(BLACK, 38), fill=BRANCO, anchor="mm")
    if t < abre:
        if t > 53.36 - 51.80:
            d.line([(cx + R + 40, cy), (bx - 150, cy)], fill=VERMELHO, width=8)
            m = (cx + R + 40 + bx - 150) / 2
            d.line([(m - 26, cy - 26), (m + 26, cy + 26)], fill=VERMELHO, width=10)
            d.line([(m + 26, cy - 26), (m - 26, cy + 26)], fill=VERMELHO, width=10)
        if t > 55.0 - 51.80:
            d.text((LW / 2, LH - 50), "ARRISCADO DEMAIS", font=F(BLACK, 36), fill=VERMELHO, anchor="mm")
    else:
        for k in range(10):            # moedas voando em arco
            q = cl((t - abre) * 1.4 - k * 0.09)
            if 0 < q < 1:
                x = lerp(cx + 40, bx, q); y = cy - math.sin(q * math.pi) * 150
                d.ellipse([x - 18, y - 18, x + 18, y + 18], fill=AMARELO, outline=(190, 140, 0), width=4)
        d.text((LW / 2, LH - 50), "LIBERARAM UM PEDAÇO", font=F(BLACK, 36), fill=VERDE, anchor="mm")
    return c


@functools.lru_cache(None)
def trilhas():
    rnd = random.Random(3); out = []
    for _ in range(16):
        x, y = rnd.uniform(80, LW - 80), rnd.uniform(60, LH - 60); pts = [(x, y)]
        for _ in range(4):
            if rnd.random() < 0.5:
                x += rnd.choice([-1, 1]) * rnd.uniform(40, 140)
            else:
                y += rnd.choice([-1, 1]) * rnd.uniform(30, 100)
            pts.append((x, y))
        out.append(pts)
    return out


def ponto_em(pts, q):
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    L = [math.dist(a, b) for a, b in segs]; tot = sum(L); alvo = q * tot
    for (a, b), l in zip(segs, L):
        if alvo <= l:
            r = alvo / max(l, 1e-6); return (lerp(a[0], b[0], r), lerp(a[1], b[1], r))
        alvo -= l
    return pts[-1]


def m_chip(t):                        # 70,90 → 75,55
    c = cobrir(abrir("001624-pres-chip.jpg"), LW, LH, 1.05 + 0.06 * t / 4.6)
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k, pts in enumerate(trilhas()):
        q = (t * 0.55 + k * 0.137) % 1
        x, y = ponto_em(pts, q)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(120, 255, 190, 255))
        x2, y2 = ponto_em(pts, max(0, q - 0.06))
        d.line([(x2, y2), (x, y)], fill=(120, 255, 190, 160), width=5)
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(5))); c.alpha_composite(lay)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([26, LH - 84, 386, LH - 26], 14, fill=FUNDO + (225,))
    d.text((46, LH - 55), "CHIP DE IA", font=F(BLACK, 32), fill=BRANCO, anchor="lm")
    d.text((216, LH - 55), "· EUA", font=F(BLACK, 32), fill=AMARELO, anchor="lm")
    return c


def m_dc(t):                          # 86,70 → 92,95
    c = cobrir(abrir("001558-pres-datacenter.jpg"), LW, LH, 1.04 + 0.07 * t / 6.25, 0.5, 0.55)
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    alvo = (LW * 0.42, LH * 0.62)
    fontes = [(LW * 0.12, LH * 0.30), (LW * 0.30, LH * 0.25), (LW * 0.70, LH * 0.25), (LW * 0.88, LH * 0.32), (LW * 0.85, LH * 0.75), (LW * 0.65, LH * 0.85)]
    for k, f_ in enumerate(fontes):
        for j in range(5):
            q = (t * 0.7 + j / 5 + k * 0.11) % 1
            x, y = lerp(f_[0], alvo[0], q), lerp(f_[1], alvo[1], q)
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(255, 220, 60, int(255 * math.sin(q * math.pi))))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(4))); c.alpha_composite(lay)
    pulso = 0.5 + 0.5 * math.sin(t * 6)
    g = Image.new("RGBA", c.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([alvo[0] - 90, alvo[1] - 50, alvo[0] + 90, alvo[1] + 50], fill=(120, 255, 190, int(70 + 60 * pulso)))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(26)))
    d = ImageDraw.Draw(c)
    q = 90.58 - 86.70
    if t > q:
        a = ease((t - q) / 0.3)
        d.rounded_rectangle([26, LH - 84, 26 + int(620 * a), LH - 26], 14, fill=FUNDO + (230,))
        if a > 0.95:
            d.text((46, LH - 55), "ENERGIA QUE SOBRA", font=F(BLACK, 32), fill=AMARELO, anchor="lm")
            d.text((390, LH - 55), "→ IA AQUI", font=F(BLACK, 32), fill=VERDE, anchor="lm")
    else:
        d.rounded_rectangle([26, LH - 84, 446, LH - 26], 14, fill=FUNDO + (225,))
        d.text((46, LH - 55), "IMPOSTO ZERO · NORDESTE", font=F(BLACK, 30), fill=BRANCO, anchor="lm")
    return c


def m_cta(t):                         # 97,20 → 100,97
    c = painel(); d = ImageDraw.Draw(c)
    p = back(t / 0.4)
    bw, bh = int(640 * p), int(230 * p)
    if bw > 10:
        bx, by = LW / 2 - bw / 2, 60
        d.rounded_rectangle([bx, by, bx + bw, by + bh], 40, fill=BRANCO)
        d.polygon([(bx + 90, by + bh - 4), (bx + 70, by + bh + 50), (bx + 150, by + bh - 4)], fill=BRANCO)
        if t < 0.9:
            for k in range(3):
                yy = by + bh / 2 + 10 * math.sin(t * 14 + k)
                d.ellipse([LW / 2 - 70 + k * 60, yy - 16, LW / 2 - 38 + k * 60, yy + 16], fill=(140, 144, 156))
        else:
            d.text((LW / 2, by + bh / 2 - 34), "QUAL DESSAS", font=F(BLACK, 58), fill=(20, 22, 30), anchor="mm")
            d.text((LW / 2, by + bh / 2 + 40), "VOCÊ APROVARIA?", font=F(BLACK, 58), fill=VERDE, anchor="mm")
    yb = 375 + 12 * math.sin(t * 7)
    d.text((LW / 2, yb), "COMENTA", font=F(BLACK, 48), fill=AMARELO, anchor="mm")
    d.polygon([(LW / 2 - 28, yb + 38), (LW / 2 + 28, yb + 38), (LW / 2, yb + 72)], fill=AMARELO)
    return c


# ================= TELA CHEIA =================
def tremor(c, t, t0, forca=14, dur=0.35):
    if 0 < t - t0 < dur:
        k = 1 - (t - t0) / dur
        return c.transform(c.size, Image.AFFINE, (1, 0, random.uniform(-forca, forca) * k, 0, 1, random.uniform(-forca, forca) * k))
    return c


def flash(c, t, t0, dur=0.18):
    if 0 < t - t0 < dur:
        c.alpha_composite(Image.new("RGBA", c.size, (255, 255, 255, int(200 * (1 - (t - t0) / dur)))))


def f_3x35(t):                        # 12,60 → 16,25
    c = Image.new("RGBA", (FW, FH), (0, 0, 0, 255))
    abre = ease(t / 0.3)
    esq = _fundo(FW // 2, FH, (20, 120, 70), (6, 40, 24)); dir_ = _fundo(FW // 2, FH, (150, 30, 36), (50, 8, 12))
    c.alpha_composite(esq, (int(-FW / 2 * (1 - abre)), 0)); c.alpha_composite(dir_, (int(FW / 2 + FW / 2 * (1 - abre)), 0))
    d = ImageDraw.Draw(c)
    d.polygon([(FW / 2 - 6, 0), (FW / 2 + 6, 0), (FW / 2 + 6, FH), (FW / 2 - 6, FH)], fill=(0, 0, 0))
    yc = 1060
    texto(d, (FW / 4, yc - 230), "EM USAR", F(BLACK, 58), BRANCO)
    escala_txt(c, (FW / 4, yc), "3º", F(BLACK, 300), BRANCO + (255,), back((t - 0.15) / 0.4))
    d = ImageDraw.Draw(c)
    texto(d, (3 * FW / 4, yc - 230), "EM CRIAR", F(BLACK, 58), BRANCO)
    t_rola, t_para = 14.70 - 12.60, 15.20 - 12.60
    if t < t_rola:
        n = 3
    elif t < t_para:
        n = int(lerp(3, 35, ease((t - t_rola) / (t_para - t_rola))))
    else:
        n = 35
    if t_rola <= t < t_para:          # rolagem com desfoque vertical
        lay = Image.new("RGBA", (FW // 2, 420), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for dy, nn in ((-300, n + 1), (0, n), (300, max(3, n - 1))):
            ld.text((FW / 4, 210 + dy + (t * 3000) % 300), f"{nn}º", font=F(BLACK, 300), fill=BRANCO, anchor="mm")
        lay = lay.filter(ImageFilter.BoxBlur(6))
        c.alpha_composite(lay, (FW // 2, yc - 210))
    else:
        s = back((t - t_para) / 0.3, 2.4) if t >= t_para else 1
        escala_txt(c, (3 * FW / 4, yc), f"{n}º", F(BLACK, 300), (AMARELO if n == 35 else BRANCO) + (255,), s)
    d = ImageDraw.Draw(c)
    d.text((FW / 2, 1520), "Fontes: OpenAI (2025) · Global AI Index, Tortoise (2023)", font=F(SEMI, 26), fill=(220, 220, 220), anchor="mm")
    c.alpha_composite(grao(FW, FH))
    flash(c, t, t_para)
    return tremor(c, t, t_para, 18)


def f_dia1(t):                        # 31,00 → 35,05
    c = _fundo(FW, FH, (34, 40, 64), (8, 10, 16)).copy()
    p = back(t / 0.5, 1.5)
    calendario(c, FW / 2, 930 - 320 * (1 - p), "DIA", "1", 1.25, rot=-5 * (1 - p) + 3)
    d = ImageDraw.Draw(c)
    texto(d, (FW / 2, 640), "PRIMEIRO DIA", F(BLACK, 54), AMARELO)
    q = 33.02 - 31.00
    if t > q:
        d.text((FW / 2, 1230), "IMPOSTO DE RENDA", font=F(BLACK, 66), fill=BRANCO, anchor="mm")
        cai = ease((t - (33.68 - 31.00)) / 0.5)
        v = 27.5 * (1 - cai)
        txt = f"{v:.1f}%".replace(".", ",") if cai < 1 else "0%"
        escala_txt(c, (FW / 2, 1400), txt, F(BLACK, 200), (VERDE if cai >= 1 else BRANCO) + (255,), 1 + 0.15 * (1 - cl((t - 3.2) / 0.3)) if cai >= 1 else 1)
        d = ImageDraw.Draw(c)
    if t > 34.20 - 31.00:
        a = back((t - (34.20 - 31.00)) / 0.3)
        escala_txt(c, (FW / 2, 1570), "POR 10 ANOS", F(BLACK, 70), AMARELO + (255,), a)
    c.alpha_composite(grao(FW, FH))
    flash(c, t, 33.68 - 31.00 + 0.5)
    return c


def f_vale(t):                        # 58,30 → 63,95
    c = cobrir(abrir("001558-pres-vale.jpg"), FW, FH, 1.0 + 0.10 * t / 5.65, 0.42, 0.5)
    g = Image.linear_gradient("L").resize((FW, FH))
    c.alpha_composite(Image.merge("RGBA", (Image.new("L", (FW, FH), 0),) * 3 + (g.point(lambda v: int(v * 0.85)),)))
    q = 61.90 - 58.30
    if t > q:                         # chuva de notas (posição/velocidade aleatórias, fixas por semente)
        rnd = random.Random(11); d = ImageDraw.Draw(c)
        for k in range(16):
            x0, fase, vel, rot = rnd.uniform(60, FW - 60), rnd.uniform(0, 0.5), rnd.uniform(500, 820), rnd.uniform(-25, 25)
            y = 620 + (t - q - fase) * vel
            if t - q > fase and y < FH + 40:
                nota = Image.new("RGBA", (120, 60), (0, 0, 0, 0)); nd = ImageDraw.Draw(nota)
                nd.rounded_rectangle([2, 2, 118, 58], 8, fill=(46, 150, 84), outline=(200, 240, 200), width=3)
                nd.text((60, 30), "$", font=F(BLACK, 34), fill=(225, 255, 225), anchor="mm")
                nota = nota.rotate(rot + (t - q) * 90 * (1 if k % 2 else -1), resample=Image.BICUBIC, expand=True)
                c.alpha_composite(nota, (int(x0 - nota.width / 2), int(y)))
    a = ease((t - 0.2) / 0.5)
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.text((FW / 2 + 3, 1245 + 30 * (1 - a)), "VALE DO SILÍCIO", font=F(BLACK, 96), fill=(0, 0, 0, 170), anchor="mm")
    ld.text((FW / 2, 1240 + 30 * (1 - a)), "VALE DO SILÍCIO", font=F(BLACK, 96), fill=BRANCO, anchor="mm")
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    c.alpha_composite(lay)
    if t > q:
        escala_txt(c, (FW / 2, 1380), "ENCHEU DE DINHEIRO", F(BLACK, 70), AMARELO + (255,), back((t - q) / 0.35))
    c.alpha_composite(grao(FW, FH))
    return c


def f_solar(t):                       # 78,90 → 82,95
    c = cobrir(abrir("001558-pres-solar.jpg"), FW, FH, 1.0 + 0.08 * t / 4.05, 0.5, 0.6)
    q = 80.30 - 78.90
    if t > q:
        a = ease((t - q) / 0.6)
        x0 = int(FW * (1 - a / 3))
        ov = Image.new("RGBA", c.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).rectangle([x0, 0, FW, FH], fill=(0, 0, 0, 200))
        c.alpha_composite(ov)
        d = ImageDraw.Draw(c)
        d.line([(x0, 0), (x0, FH)], fill=(255, 255, 255, 180), width=4)
        n = int(34 * ease((t - q) / 0.8))
        escala_txt(c, (FW / 2, 1080), f"{n}%", F(BLACK, 260), VERMELHO + (255,), 1.0)
        d = ImageDraw.Draw(c)
        texto(d, (FW / 2, 1270), "DA ENERGIA SOLAR", F(BLACK, 62), BRANCO)
        texto(d, (FW / 2, 1350), "DESLIGADA", F(BLACK, 62), BRANCO)
        d.text((FW / 2, 1450), "3º tri 2025 · Fonte: ONS/BTG via NeoFeed", font=F(SEMI, 28), fill=(225, 225, 225), anchor="mm")
    c.alpha_composite(grao(FW, FH))
    return c


# (nome, inicio, fim, funcao, tela_cheia)
MOTIONS = [
    ("abertura", 0.00, 6.25, m_abertura, False),
    ("podio", 6.30, 12.45, m_podio, False),
    ("x35", 12.55, 16.25, f_3x35, True),
    ("carimbos", 16.30, 19.35, m_carimbos, False),
    ("partida", 23.30, 30.90, m_partida, False),
    ("dia1", 31.00, 35.05, f_dia1, True),
    ("mes", 41.70, 44.95, m_mes, False),
    ("cofre", 51.80, 58.25, m_cofre, False),
    ("vale", 58.30, 63.95, f_vale, True),
    ("ano", 68.10, 70.85, m_ano, False),
    ("chip", 70.90, 75.55, m_chip, False),
    ("solar", 78.90, 82.95, f_solar, True),
    ("dc", 86.70, 92.95, m_dc, False),
    ("cta", 97.20, DUR, m_cta, False),
]


def titulo():
    img = Image.new("RGBA", (FW, 700), (0, 0, 0, 0))
    linhas = ["se eu fosse presidente,", "é assim que eu colocaria", "o Brasil no top 3", "de IA do mundo"]
    fz = F(BOLD, 68)
    for k, l in enumerate(linhas):
        y = 228 + k * 84
        ImageDraw.Draw(img).text((FW / 2, y), l, font=fz, fill=BRANCO, anchor="mm", stroke_width=5, stroke_fill=(20, 20, 22))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.alpha_composite(img.point(lambda v: v), (0, 6))
    sh = Image.merge("RGBA", (Image.new("L", img.size, 0),) * 3 + (sh.getchannel("A").point(lambda v: int(v * 0.45)),))
    out = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), img)
    out.save(w("titulo.png"))
    # fecho: palavra por palavra, embaixo
    return out


FECHO = [("SÓ", 93.60), ("CLIENTE", 93.80), ("NÃO ENTRA", 94.30), ("NO TOP 3", 94.84)]


def m_fecho(t):                       # 93,20 → 95,45 (sem painel)
    c = Image.new("RGBA", (FW, 640), (0, 0, 0, 0))
    linhas = [("SÓ CLIENTE", 93.60), ("NÃO ENTRA", 94.30), ("NO TOP 3", 94.84)]
    for k, (l, q) in enumerate(linhas):
        s = back((t + 93.20 - q) / 0.25, 2.2)
        if s > 0.01:
            cor = AMARELO if k == 2 else BRANCO
            sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
            escala_txt(sh, (FW / 2, 120 + k * 150 + 6), l, F(BLACK, 128), (0, 0, 0, 200), s)
            c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
            escala_txt(c, (FW / 2, 120 + k * 150), l, F(BLACK, 128), cor + (255,), s)
    return c


def motions(so=None):
    lista = MOTIONS + [("fecho", 93.20, 95.45, m_fecho, "fecho")]
    if so:
        lista = [x for x in lista if x[0] in so]
    for nome, e, s, fn, tipo in lista:
        tmp = w("_frames"); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
        random.seed(1)
        for i in range(int(round((s - e) * 30)) + 1):
            fr = fn(i / 30)
            if tipo is False:
                fr = emoldurar(fr)
            fr.save(os.path.join(tmp, f"{i:04d}.png"), compress_level=1)
        if tipo is True:               # tela cheia é opaca: H.264 (qtrle de foto em 1080x1920 passa de 1 GB)
            run(["-framerate", "30", "-i", os.path.join(tmp, "%04d.png"), "-c:v", "libx264", "-crf", "14",
                 "-pix_fmt", "yuv420p", "-g", "30", w(f"m2-{nome}.mp4")])
        else:
            run(["-framerate", "30", "-i", os.path.join(tmp, "%04d.png"), "-c:v", "qtrle", w(f"m2-{nome}.mov")])
        shutil.rmtree(tmp)
        print("  motion", nome, flush=True)


def compor():
    ins = ["-i", w("base.mp4"), "-i", ORIG]
    fc, ult, n = [], "0:v", 2
    lista = MOTIONS + [("fecho", 93.20, 95.45, None, "fecho")]
    for j, (nome, e, s, _, tipo) in enumerate(lista):
        ins += ["-i", w(f"m2-{nome}.mp4" if tipo is True else f"m2-{nome}.mov")]
        if tipo is True:               # tela cheia: entra seco com micro-zoom
            fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{e}/TB,format=rgba,fade=t=out:st={s - 0.12}:d=0.12:alpha=1[i{j}]")
            pos = "x=0:y=0"
        elif tipo == "fecho":
            fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{e}/TB,format=rgba,fade=t=out:st={s - 0.2}:d=0.2:alpha=1[i{j}]")
            pos = f"x=0:y={LOW_Y - 330}"
        else:
            fi = "" if e == 0 else f"fade=t=in:st={e}:d=0.16:alpha=1,"
            fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{e}/TB,format=rgba,{fi}fade=t=out:st={s - 0.16}:d=0.16:alpha=1[i{j}]")
            sobe = "" if e == 0 else f"+40*max(0,1-(t-{e})/0.25)"
            pos = f"x=(W-w)/2:y='{LOW_Y}-h/2{sobe}'"
        fc.append(f"[{ult}][i{j}]overlay={pos}:enable='between(t,{e},{s})':eof_action=pass[o{j}]")
        ult, n = f"o{j}", n + 1
    ins += ["-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", w("titulo.png")]
    fc.append(f"[{ult}][{n}:v]overlay=x=0:y=0:shortest=1[v]")
    fc.append("[1:a]loudnorm=I=-15:TP=-1.5[aud]")
    run(["-threads", "2"] + ins + ["-filter_complex", ";".join(fc), "-filter_threads", "2", "-map", "[v]",
         "-map", "[aud]", "-t", str(DUR), "-c:v", "libx264", "-crf", "19", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", SAIDA])
    print("saída:", SAIDA)


if __name__ == "__main__":
    args = sys.argv[1:] or ["titulo", "motions", "compor"]
    if args[0] == "motions" and len(args) > 1 and args[1] not in ("compor", "titulo"):
        motions(set(args[1:])); sys.exit()
    for etapa in args:
        print(f"[{etapa}]", flush=True)
        globals()[etapa]()
