"""Se eu fosse presidente — montagem (take único 100,97 s).

Base: faixa presidencial (faixa.py, 0–5,10 s) → corte com zoom em "Em usar" (5,10–12,55) → plano normal.
Topo (teto vazio, centro y≈330): 13 inserções com RESPIRO entre elas (plano em PLANO-EDICAO.md, v2).
Peito: legenda nativa (branca, contorno escuro, até 3 palavras).
Imagens: geradas no Kie.ai (Nano Banana) — originais, em output/midia/2026-10-07/.

uso: python montar.py [base cards legenda compor]
"""
import functools, json, math, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(AQUI))))
WORK = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "work", "2026-10-presidente-ia")
ORIG = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "FE55C986-B422-4E8F-86E1-7ACC24B82C9F.mp4")
SAIDA = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "2026-10-presidente-ia.mp4")
IMG = os.path.join(RAIZ, "output", "midia", "2026-10-07")
DUR = 100.97
CORTE_FAIXA, CORTE_ZOOM = 5.10, 12.55

BLACK = r"C:\Windows\Fonts\seguibl.ttf"
BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
SEMI = r"C:\Windows\Fonts\seguisb.ttf"
VERDE, AMARELO, VERMELHO = (25, 170, 95), (245, 197, 40), (232, 72, 77)
CINZA, FUNDO = (150, 155, 165), (14, 16, 22)
CW, CH, PAD = 900, 520, 30          # card
TOPO_Y = 340                          # centro vertical dos cards


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def w(n):
    return os.path.join(WORK, n)


def F(path, size):
    return ImageFont.truetype(path, size)


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def centro(d, txt, fonte, y, cor, x0=0, x1=CW):
    larg = d.textlength(txt, font=fonte)
    d.text((x0 + (x1 - x0 - larg) / 2, y), txt, font=fonte, fill=cor)


# ---------------- base: faixa + corte com zoom ----------------
def base():
    z = 1.10
    fc = [f"[0:v]trim=0:{CORTE_FAIXA},setpts=PTS-STARTPTS,fps=30,format=yuv420p[a]",
          f"[1:v]trim={CORTE_FAIXA}:{CORTE_ZOOM},setpts=PTS-STARTPTS,fps=30,scale={int(1080*z)}:{int(1920*z)},"
          f"crop=1080:1920:{int(1080*(z-1)/2)}:{int(1920*(z-1)*0.30)},format=yuv420p[b]",
          f"[1:v]trim={CORTE_ZOOM}:{DUR},setpts=PTS-STARTPTS,fps=30,scale=1080:1920,format=yuv420p[c]",
          "[a][b][c]concat=n=3:v=1:a=0[v]"]
    run(["-threads", "2", "-i", w("faixa.mp4"), "-i", ORIG, "-filter_complex", ";".join(fc), "-map", "[v]",
         "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-g", "30", "-pix_fmt", "yuv420p", w("base.mp4")])


# ---------------- cards ----------------
def painel(t_in=0.0):
    c = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    ImageDraw.Draw(c).rounded_rectangle([0, 0, CW - 1, CH - 1], 30, fill=FUNDO + (236,))
    return c


def rodape(d, txt):
    centro(d, txt, F(SEMI, 22), CH - 46, CINZA)


def kicker(d, txt, cor=AMARELO, y=34):
    centro(d, txt, F(BLACK, 30), y, cor)


def emoldurar(c):
    out = Image.new("RGBA", (CW + 2 * PAD, CH + 2 * PAD), (0, 0, 0, 0))
    s = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([PAD, PAD + 10, PAD + CW, PAD + CH + 10], 30, fill=(0, 0, 0, 150))
    out = Image.alpha_composite(s.filter(ImageFilter.GaussianBlur(16)), out)
    out.alpha_composite(c, (PAD, PAD))
    return out


def c_rank(t):                        # 6,30 → 12,30
    c = painel(); d = ImageDraw.Draw(c)
    kicker(d, "QUEM MAIS USA O CHATGPT NO MUNDO")
    linhas = [("1º", "ESTADOS UNIDOS", 11.10 - 6.30), ("2º", "ÍNDIA", 11.98 - 6.30), ("3º", "BRASIL", 0.5)]
    for k, (pos, nome, acende) in enumerate(linhas):
        y = 110 + k * 112
        on = ease((t - acende) / 0.35)
        br = k == 2
        cor_bar = VERDE if br else (70, 75, 88)
        base_cor = (40, 44, 54)
        d.rounded_rectangle([60, y, CW - 60, y + 92], 18, fill=base_cor)
        if on > 0:
            d.rounded_rectangle([60, y, 60 + int((CW - 120) * on), y + 92], 18, fill=cor_bar)
        txt = (255, 255, 255) if on > 0.5 else (120, 125, 135)
        d.text((92, y + 14), pos, font=F(BLACK, 54), fill=txt)
        d.text((210, y + 14), nome, font=F(BLACK, 54), fill=txt)
    rodape(d, "Fonte: OpenAI, estudo de uso no Brasil (ago/2025)")
    return c


def c_3x35(t):                        # 12,60 → 19,30
    c = painel(); d = ImageDraw.Draw(c)
    meio = CW // 2
    d.line([(meio, 60), (meio, CH - 90)], fill=(60, 64, 76), width=3)
    centro(d, "EM USAR", F(BLACK, 34), 50, VERDE, 0, meio)
    centro(d, "3º", F(BLACK, 190), 95, (255, 255, 255), 0, meio)
    centro(d, "EM CRIAR", F(BLACK, 34), 50, VERMELHO, meio, CW)
    n = 3 + int(round(32 * ease((t - (14.85 - 12.60)) / 0.55)))
    centro(d, f"{n}º", F(BLACK, 190), 95, (255, 255, 255) if n < 35 else VERMELHO, meio, CW)
    for (txt, cor, quando, x0, x1) in (("CLIENTE", VERDE, 17.24 - 12.60, 0, meio),
                                       ("FABRICANTE", VERMELHO, 18.56 - 12.60, meio, CW)):
        a = ease((t - quando) / 0.25)
        if a > 0:
            fz = F(BLACK, 40)
            larg = d.textlength(txt, font=fz)
            xx = x0 + (x1 - x0 - larg) / 2
            d.rounded_rectangle([xx - 22, 345 - 6, xx + larg + 22, 345 + 54], 14, fill=cor)
            d.text((xx, 345), txt, font=fz, fill=(255, 255, 255))
    rodape(d, "Fontes: OpenAI (2025) · Global AI Index, Tortoise (2023)")
    return c


def boneco(d, x, y, cor, esc=1.0):
    r = 18 * esc
    d.ellipse([x - r, y, x + r, y + 2 * r], fill=cor)
    d.rounded_rectangle([x - 30 * esc, y + 2 * r + 8, x + 30 * esc, y + 2 * r + 90 * esc], int(24 * esc), fill=cor)


def c_70(t):                          # 23,30 → 30,90
    c = painel(); d = ImageDraw.Draw(c)
    kicker(d, "CIENTISTAS BRASILEIROS QUE MORAM FORA")
    sai = ease((t - (26.56 - 23.30)) / 0.9)
    for k in range(10):
        x = 95 + k * 79
        if k >= 3:                     # 7 de 10: ficam vermelhos e desbotam
            cor = tuple(int(a + (b - a) * min(1, sai * 1.6)) for a, b in zip((235, 235, 240), VERMELHO))
            alpha = int(255 * (1 - 0.55 * sai))
            boneco(d, x + 18 * sai, 105, cor + (alpha,))
        else:
            boneco(d, x, 105, (235, 235, 240))
    a = ease((t - (26.56 - 23.30)) / 0.3)
    if a > 0:
        centro(d, "70%", F(BLACK, 120), 250, VERMELHO)
        centro(d, "NÃO PENSAM EM VOLTAR", F(BLACK, 38), 395, (255, 255, 255))
    rodape(d, "Fonte: Revista Pesquisa FAPESP (mai/2026)")
    return c


def capitulo(t, marco, frase, quando, sub=None, sub_quando=None):
    c = painel(); d = ImageDraw.Draw(c)
    centro(d, marco, F(BLACK, 40), 60, AMARELO)
    d.line([(CW / 2 - 60, 122), (CW / 2 + 60, 122)], fill=AMARELO, width=4)
    a = ease((t - quando) / 0.3)
    if a > 0:
        y = 175 + 25 * (1 - a)
        for k, linha in enumerate(frase):
            centro(d, linha, F(BLACK, 72), y + k * 88, (255, 255, 255))
    if sub and t >= sub_quando:
        b = ease((t - sub_quando) / 0.3)
        centro(d, sub, F(BLACK, 46), 390, VERDE if b > 0.5 else CINZA)
    return c


def c_dia(t):                         # 31,00 → 37,60
    return capitulo(t, "PRIMEIRO DIA", ["IMPOSTO DE RENDA", "ZERO"], 33.02 - 31.00, "POR 10 ANOS", 34.20 - 31.00)


def c_mes(t):                         # 41,70 → 44,90
    return capitulo(t, "PRIMEIRO MÊS", ["DINHEIRO PRA", "QUEM FABRICA"], 43.58 - 41.70)


def c_ano(t):                         # 68,10 → 70,90
    return capitulo(t, "PRIMEIRO ANO", ["A MÁQUINA"], 70.30 - 68.10, "CHIP · DATA CENTER · ENERGIA", 70.60 - 68.10)


def cadeado(d, x, y, aberto, cor):
    d.rounded_rectangle([x - 34, y, x + 34, y + 54], 10, fill=cor)
    dx = 22 if aberto else 0
    d.arc([x - 24 + dx, y - 40 - (14 if aberto else 0), x + 24 + dx, y + 10 - (14 if aberto else 0)], 180, 360, fill=cor, width=9)


def c_cofre(t):                       # 51,80 → 58,30
    c = painel(); d = ImageDraw.Draw(c)
    kicker(d, "ESTADOS UNIDOS · 1979")
    abre = 57.42 - 51.80
    aberto = t >= abre
    for (x0, x1, titulo) in ((50, 380, ["APOSENTADORIA", "DO TRABALHADOR"]), (CW - 380, CW - 50, ["EMPRESA", "NOVA"])):
        d.rounded_rectangle([x0, 110, x1, 330], 22, outline=(90, 96, 110), width=4, fill=(30, 33, 42))
        for k, l in enumerate(titulo):
            centro(d, l, F(BLACK, 28), 250 + k * 36 - (18 if len(titulo) > 1 else 0), (255, 255, 255), x0, x1)
    cadeado(d, 215, 150, aberto, VERDE if aberto else VERMELHO)
    # seta
    cor = VERDE if aberto else VERMELHO
    d.line([(400, 220), (CW - 400, 220)], fill=cor, width=10)
    d.polygon([(CW - 400, 200), (CW - 372, 220), (CW - 400, 240)], fill=cor)
    if not aberto and t > (53.36 - 51.80):
        d.line([(430, 190), (470, 250)], fill=VERMELHO, width=9)
        d.line([(470, 190), (430, 250)], fill=VERMELHO, width=9)
    if aberto:                         # moeda "um pedaço" viaja
        p = ease((t - abre) / 0.8)
        x = 230 + (CW - 215 - 230) * p
        d.ellipse([x - 26, 150, x + 26, 202], fill=AMARELO)
        centro(d, "LIBERARAM UM PEDAÇO", F(BLACK, 38), 380, VERDE)
    elif t > (55.0 - 51.80):
        centro(d, "ARRISCADO DEMAIS", F(BLACK, 38), 380, VERMELHO)
    return c


@functools.lru_cache(None)
def abrir(arquivo):
    return Image.open(os.path.join(IMG, arquivo)).convert("RGB")


def foto(t, arquivo, dur, legenda=None, extra=None):
    """Imagem com Ken Burns lento, canto arredondado."""
    im = abrir(arquivo)
    z = 1.0 + 0.08 * (t / max(dur, 0.1))
    e = max(CW / im.width, CH / im.height) * z
    im2 = im.resize((int(im.width * e) + 1, int(im.height * e) + 1), Image.BILINEAR)
    x0, y0 = (im2.width - CW) // 2, (im2.height - CH) // 2
    c = im2.crop((x0, y0, x0 + CW, y0 + CH)).convert("RGBA")
    if extra:
        extra(c, t)
    if legenda:
        d = ImageDraw.Draw(c)
        fz = F(BLACK, 32)
        larg = d.textlength(legenda, font=fz)
        d.rounded_rectangle([28, CH - 82, 28 + larg + 40, CH - 28], 14, fill=FUNDO + (220,))
        d.text((48, CH - 78), legenda, font=fz, fill=(255, 255, 255))
    m = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, CW - 1, CH - 1], 30, fill=255)
    c.putalpha(m)
    return c


def solar_extra(c, t):
    q = ease((t - (80.30 - 78.90)) / 0.7)        # "um terço" — escurece 1/3 da usina
    if q > 0:
        ov = Image.new("RGBA", c.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).rectangle([int(CW * (1 - q / 3)), 0, CW, CH], fill=(0, 0, 0, 175))
        c.alpha_composite(ov)
        d = ImageDraw.Draw(c)
        if q > 0.6:
            d.text((int(CW * 2 / 3) + 26, 40), "34%", font=F(BLACK, 96), fill=VERMELHO)
            d.text((int(CW * 2 / 3) + 30, 150), "DESLIGADA", font=F(BLACK, 34), fill=(255, 255, 255))
            d.text((int(CW * 2 / 3) + 30, 192), "3º tri 2025", font=F(SEMI, 26), fill=(220, 220, 220))
    d = ImageDraw.Draw(c)
    d.text((CW - 300, CH - 36), "Fonte: ONS/BTG via NeoFeed", font=F(SEMI, 20), fill=(235, 235, 235))


def c_cta(t):                         # 97,20 → 100,97
    c = painel(); d = ImageDraw.Draw(c)
    centro(d, "QUAL DESSAS VOCÊ", F(BLACK, 66), 110, (255, 255, 255))
    centro(d, "APROVARIA?", F(BLACK, 66), 190, AMARELO)
    a = ease((t - (100.46 - 97.20)) / 0.3) if t > 2.0 else ease((t - 0.3) / 0.3)
    yb = 330 + 12 * math.sin(t * 6)
    centro(d, "COMENTA", F(BLACK, 46), yb, VERDE)
    x = CW / 2
    d.polygon([(x - 26, yb + 70), (x + 26, yb + 70), (x, yb + 102)], fill=VERDE)
    return c


# (nome, inicio, fim, funcao(t)->RGBA)
INSERCOES = [
    ("rank", 6.30, 12.30, c_rank),
    ("x35", 12.60, 19.30, c_3x35),
    ("setenta", 23.30, 30.90, c_70),
    ("dia", 31.00, 37.60, c_dia),
    ("mes", 41.70, 44.90, c_mes),
    ("cofre", 51.80, 58.30, c_cofre),
    ("vale", 58.30, 63.90, lambda t: foto(t, "001558-pres-vale.jpg", 5.6, "Vale do Silício")),
    ("ano", 68.10, 70.90, c_ano),
    ("chip", 70.90, 75.50, lambda t: foto(t, "001624-pres-chip.jpg", 4.6, "Chip de IA")),
    ("solar", 78.90, 82.90, lambda t: foto(t, "001558-pres-solar.jpg", 4.0, None, solar_extra)),
    ("dc", 86.70, 92.90, lambda t: foto(t, "001558-pres-datacenter.jpg", 6.2, "Data center + sol e vento · Nordeste")),
    ("cta", 97.20, DUR, c_cta),
]


def cards():
    for nome, e, s, fn in INSERCOES:
        tmp = w("_frames"); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
        for i in range(int((s - e) * 30) + 1):
            emoldurar(fn(i / 30)).save(os.path.join(tmp, f"{i:04d}.png"), compress_level=1)
        run(["-framerate", "30", "-i", os.path.join(tmp, "%04d.png"), "-c:v", "qtrle", w(f"ins-{nome}.mov")])
        shutil.rmtree(tmp)
        print("  card", nome, flush=True)
    # fecho: frase sozinha no topo, sem painel
    img = Image.new("RGBA", (1080, 700), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    linhas = [("SÓ CLIENTE", (255, 255, 255)), ("NÃO ENTRA", (255, 255, 255)), ("NO TOP 3", AMARELO)]
    for k, (l, cor) in enumerate(linhas):
        fz = F(BLACK, 118)
        larg = ImageDraw.Draw(img).textlength(l, font=fz)
        ImageDraw.Draw(sh).text(((1080 - larg) / 2, 120 + k * 140 + 6), l, font=fz, fill=(0, 0, 0, 230))
        ImageDraw.Draw(img).text(((1080 - larg) / 2, 120 + k * 140), l, font=fz, fill=cor)
    img = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), img)
    img.save(w("fecho.png"))


# ---------------- legenda nativa ----------------
TROCA = {15: "três", 37: "ChatGPT,", 38: "", 243: "faço", 248: "IA", 270: "", 271: "IA", 351: "vira IA"}


def legenda():
    ws = json.load(open(w("words.json"), encoding="utf-8"))["words"]
    pal = []
    for i, x in enumerate(ws):
        t = TROCA.get(i, x["word"].strip())
        if t:
            pal.append([t, x["start"], x["end"]])
    pal.sort(key=lambda p: p[1])
    grupos, atual = [], []
    for i, x in enumerate(pal):
        atual.append(x)
        pausa = i + 1 < len(pal) and pal[i + 1][1] - x[2] > 0.3
        if len(atual) >= 3 or x[0][-1] in ".,?!" or pausa or i == len(pal) - 1:
            grupos.append([" ".join(y[0] for y in atual).rstrip(".,"), atual[0][1], x[2]])
            atual = []
    fonte = F(BOLD, 52)
    pasta = w("leg"); shutil.rmtree(pasta, ignore_errors=True); os.makedirs(pasta)
    vazio = os.path.join(pasta, "vazio.png"); Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
    seq, t = [], 0.0
    for i, (txt, a, b) in enumerate(grupos):
        nxt = grupos[i + 1][1] if i + 1 < len(grupos) else DUR
        b = min(max(b, a + 0.35) + 0.3, nxt)
        if a > t:
            seq.append((vazio, a - t))
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        larg = dr.textlength(txt, font=fonte)
        x, y = (1080 - larg) / 2, 1395
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((x, y + 4), txt, font=fonte, fill=(0, 0, 0, 170))
        img = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)), img)
        ImageDraw.Draw(img).text((x, y), txt, font=fonte, fill="white", stroke_width=4, stroke_fill=(10, 10, 12))
        p = os.path.join(pasta, f"{i:03d}.png"); img.save(p, compress_level=1)
        seq.append((p, b - a)); t = b
    seq.append((vazio, DUR - t + 0.5))
    lista = os.path.join(pasta, "lista.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for p, dd in seq:
            f.write(f"file '{p}'\nduration {dd:.3f}\n")
        f.write(f"file '{vazio}'\n")
    run(["-f", "concat", "-safe", "0", "-i", lista, "-vf", "fps=30,format=rgba", "-c:v", "qtrle", w("legenda.mov")])
    shutil.rmtree(pasta)


# ---------------- composição ----------------
def compor():
    ins = ["-i", w("base.mp4"), "-i", ORIG]
    fc = []
    ult, n = "0:v", 2
    for j, (nome, e, s, _) in enumerate(INSERCOES):
        ins += ["-i", w(f"ins-{nome}.mov")]
        fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{e}/TB,format=rgba,fade=t=in:st={e}:d=0.18:alpha=1,"
                  f"fade=t=out:st={s - 0.18}:d=0.18:alpha=1[i{j}]")
        y = f"'{TOPO_Y}-{(CH + 2 * PAD) // 2}+36*max(0,1-(t-{e})/0.25)'"
        fc.append(f"[{ult}][i{j}]overlay=x=(W-w)/2:y={y}:enable='between(t,{e},{s})':eof_action=pass[o{j}]")
        ult, n = f"o{j}", n + 1
    ins += ["-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", w("fecho.png")]
    fc.append(f"[{n}:v]format=rgba,fade=t=in:st=93.20:d=0.2:alpha=1,fade=t=out:st=95.25:d=0.2:alpha=1[fe]")
    fc.append(f"[{ult}][fe]overlay=x=0:y=0:enable='between(t,93.2,95.45)'[of]")
    n += 1
    ins += ["-i", w("legenda.mov")]
    fc.append(f"[of][{n}:v]overlay=format=auto[v]")
    fc.append("[1:a]loudnorm=I=-15:TP=-1.5[aud]")
    run(["-threads", "2"] + ins + ["-filter_complex", ";".join(fc), "-filter_threads", "2", "-map", "[v]",
         "-map", "[aud]", "-t", str(DUR), "-c:v", "libx264", "-crf", "19", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", SAIDA])
    print("saída:", SAIDA)


if __name__ == "__main__":
    for etapa in sys.argv[1:] or ["base", "cards", "legenda", "compor"]:
        print(f"[{etapa}]", flush=True)
        globals()[etapa]()
