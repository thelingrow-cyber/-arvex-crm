"""Três leituras de IA — edição no molde do Alex Sidhu (@alexbsidhu, ref Dd50M91xspO).

v2 (pedido do Vitor): recortado DESDE O INÍCIO e se movendo — muda de lugar a cada texto (smoothstep) e deriva
devagar. Gancho = grade 2x2 (Altman, Musk, Jensen, Dario) + Vitor RECORTADO no centro (v4; v3 era retângulo) + título em caixa preta. Depois o Vitor aparece RECORTADO e menor (80%) na frente da página REAL do texto que ele está citando, rolando devagar:
  AI 2027 (ai-2027.com) · Dwarkesh "Why I don't think AGI is right around the corner" · Situational Awareness.
Legenda de UMA palavra no peito (branca, contorno preto) e card "manda um DIRECT" no fim.
Páginas capturadas com Chrome headless a 540 px css × 2 (p-*.png). Máscara: camadas/recorte.py (mask0 0–5,4 s + mask 5,4 s → fim = mask-full.mp4).

uso: python montar.py [fundo legenda card compor]   (sem argumento = tudo)
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
WORK = os.path.join(RAIZ, "work", "2026-10-tres-leituras-ia")
ORIG = os.path.join(WORK, "original.mp4")
SAIDA = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "2026-10-tres-leituras-ia.mp4")
DUR = 61.66
INI = 5.4            # onde começa o recorte (fim do gancho)
ESC = 0.80           # tamanho da pessoa recortada
BLACK = r"C:\Windows\Fonts\seguibl.ttf"
SEMI = r"C:\Windows\Fonts\seguisb.ttf"

# [página, entra (s do vídeo), sai, y inicial, y final] — a página rola de y0 até y1 no trecho
PAGINAS = [
    ("p-ai2027.png", INI, 21.4, 0, 1100),
    ("p-dwarkesh.png", 21.4, 41.0, 0, 2000),
    ("p-sa.png", 41.0, DUR, 0, 1900),
]


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def w(n):
    return os.path.join(WORK, n)


# Gancho no molde do Alex: grade 2x2 de rostos da IA + o take num retângulo menor no meio + título em caixa preta.
# Fotos do Wikimedia Commons (licença livre; créditos em letra pequena no rodapé e na legenda do post):
# (arquivo, rosto x, rosto y em fração da foto, zoom, onde o rosto cai na célula 540x960) — longe do título e do retângulo
FOTOS = [("f-altman.jpg", .54, .36, 1.6, 170, 250), ("f-musk.jpg", .5, .32, 1.1, 340, 300),
         ("f-jensen.jpg", .5, .34, 1.3, 190, 430), ("f-dario.jpg", .5, .27, 1.5, 360, 430)]
CREDITOS = ("Fotos: Village Global (CC BY 2.0) · U.S. Air Force/T. Cokley (domínio público) · "
            "Anderseidesvik (CC BY-SA 4.0) · UK Prime Minister (CC BY 2.0) — Wikimedia Commons")
TITULO = ["dominando IA", "em 2026..."]
RET = (290, 600, 500, 680)          # x, y, largura, altura do take no meio
CORTE = (180, 500, 720, 980)        # recorte do take original que vai no retângulo


def gancho():
    out = Image.new("RGB", (1080, 1920))
    for k, (f, fx, fy, z, cx, cy) in enumerate(FOTOS):
        im = Image.open(os.path.join(AQUI, f)).convert("RGB")
        e = max(540 / im.width, 960 / im.height) * z
        im = im.resize((int(im.width * e), int(im.height * e)), Image.LANCZOS)
        x0 = min(max(0, int(im.width * fx - cx)), im.width - 540)
        y0 = min(max(0, int(im.height * fy - cy)), im.height - 960)
        out.paste(im.crop((x0, y0, x0 + 540, y0 + 960)), ((k % 2) * 540, (k // 2) * 960))
    d = ImageDraw.Draw(out)
    fc = ImageFont.truetype(SEMI, 13)
    d.text((540 - d.textlength(CREDITOS, font=fc) / 2, 1896), CREDITOS, font=fc, fill=(235, 235, 235))
    out.save(w("gancho.png"))
    # título: caixa preta arredondada, texto branco
    t = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    f = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 64)
    larg = max(d.textlength(l, font=f) for l in TITULO)
    d.rounded_rectangle([540 - larg / 2 - 34, 300, 540 + larg / 2 + 34, 300 + 2 * 78 + 40], 22, fill=(0, 0, 0, 235))
    for i, l in enumerate(TITULO):
        d.text((540 - d.textlength(l, font=f) / 2, 314 + i * 78), l, font=f, fill="white")
    t.save(w("titulo.png"))
    run(["-loop", "1", "-framerate", "30", "-t", f"{INI:.3f}", "-i", w("gancho.png"), "-vf",
         "format=yuv420p", "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-g", "30", "-r", "30", w("pag-g.mp4")])
    return w("pag-g.mp4")


def fundo():
    partes = [gancho()]
    for i, (png, a, b, y0, y1) in enumerate(PAGINAS):
        d = b - a
        p = w(f"pag{i}.mp4")
        # margem de 260 px em cima (fora da UI do Instagram) e 1,2 s parado no título antes de rolar
        im = Image.open(os.path.join(AQUI, png)).convert("RGB")
        cor = "0x%02X%02X%02X" % im.getpixel((5, 5))
        run(["-loop", "1", "-framerate", "30", "-t", f"{d:.3f}", "-i", os.path.join(AQUI, png), "-vf",
             f"pad=1080:ih+260:0:260:{cor},crop=1080:1920:0:'{y0}+({y1}-{y0})*clip((t-1.2)/{d - 1.2:.3f}\,0\,1)',format=yuv420p", "-c:v", "libx264", "-crf", "18",
             "-preset", "fast", "-g", "30", "-r", "30", p])
        partes.append(p)
    lista = w("pag.txt")
    with open(lista, "w", encoding="utf-8") as f:
        f.write("".join(f"file '{p}'\n" for p in partes))
    run(["-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", w("fundo.mp4")])
    for p in partes:
        os.remove(p)


def palavras():
    a = json.load(open(w("orig-words.json"), encoding="utf-8"))["words"]
    b = json.load(open(w("fim-words.json"), encoding="utf-8"))["words"]
    ws = [[x["word"].strip(), x["start"], x["end"]] for x in a if x["start"] < 53.0]
    ws += [[x["word"].strip(), x["start"] + 53, x["end"] + 53] for x in b if x["start"] + 53 >= 53.0]
    trocar = {"Darkvash": "Dwarkesh"}
    return [[trocar.get(t, t).strip(".,"), s, e] for t, s, e in ws]


def legenda():
    """Uma palavra por vez, fica até a próxima (máx. +0,6 s)."""
    fonte = ImageFont.truetype(BLACK, 76)
    pasta = w("leg"); os.makedirs(pasta, exist_ok=True)
    vazio = os.path.join(pasta, "vazio.png")
    Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
    ws = palavras()
    linhas, t = [], 0.0
    for i, (txt, a, b) in enumerate(ws):
        nxt = ws[i + 1][1] if i + 1 < len(ws) else DUR
        b = min(max(b, a + 0.25) + 0.6, nxt)
        if a > t:
            linhas.append((vazio, a - t))
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        larg = d.textlength(txt, font=fonte)
        d.text(((1080 - larg) / 2, 1440), txt, font=fonte, fill="white", stroke_width=7, stroke_fill="black")
        p = os.path.join(pasta, f"{i:03d}.png"); img.save(p)
        linhas.append((p, b - a)); t = b
    linhas.append((vazio, DUR - t + 0.5))
    lista = os.path.join(pasta, "lista.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for p, d in linhas:
            f.write(f"file '{p}'\nduration {d:.3f}\n")
        f.write(f"file '{vazio}'\n")
    run(["-f", "concat", "-safe", "0", "-i", lista, "-vf", "fps=30,format=rgba", "-c:v", "qtrle", w("legenda.mov")])


def card():
    """Card do CTA: 'Manda um DIRECT' com aviãozinho, papel creme como nos outros cards."""
    W, H, pad = 820, 230, 36
    c = Image.new("RGBA", (W, H), (246, 242, 234, 255))
    d = ImageDraw.Draw(c)
    # aviãozinho de papel (ícone do direct)
    cx, cy = 115, 115
    d.ellipse([cx - 78, cy - 78, cx + 78, cy + 78], fill=(18, 18, 22))
    d.polygon([(cx - 40, cy - 6), (cx + 42, cy - 40), (cx + 14, cy + 42), (cx + 2, cy + 8)], fill=(246, 242, 234))
    d.line([(cx + 2, cy + 8), (cx + 42, cy - 40)], fill=(18, 18, 22), width=5)
    d.text((228, 44), "Manda um DIRECT", font=ImageFont.truetype(BLACK, 62), fill=(18, 18, 22))
    d.text((230, 128), "e receba os 3 textos", font=ImageFont.truetype(SEMI, 40), fill=(196, 140, 52))
    m = Image.new("L", c.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, W - 1, H - 1], 24, fill=255)
    c.putalpha(m)
    out = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    s = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([pad, pad + 10, pad + W, pad + H + 10], 24, fill=(0, 0, 0, 150))
    out = Image.alpha_composite(s.filter(ImageFilter.GaussianBlur(16)), out)
    out.alpha_composite(c, (pad, pad))
    out.save(os.path.join(AQUI, "c-direct.png"))


# (tempo, x, y) da pessoa recortada: muda de lugar a cada texto, como o Alex. y >= 1920-ph (nunca mostra o corte de baixo)
POS = [(0.0, 108, 470), (INI, -110, 470), (21.4, 300, 430), (41.0, -90, 440), (57.9, 108, 480)]


def trilha(i):
    """Expressão ffmpeg: posição base + passos suaves (smoothstep 0,6 s) em cada troca."""
    e = str(POS[0][i])
    for k in range(1, len(POS)):
        dv = POS[k][i] - POS[k - 1][i]
        u = f"clip((t-{POS[k][0]})/0.6,0,1)"
        e += f"+({dv})*{u}*{u}*(3-2*{u})"
    return e


def compor():
    pw, ph = int(1080 * ESC), int(1920 * ESC)
    x = trilha(1) + "+28*sin(t*0.55)"        # deriva lenta enquanto fala
    y = trilha(2) + "+14*sin(t*0.8+1)+14"
    e = 57.9   # "Se você quiser todos esses artigos"
    fc = [
        "[0:v]fps=30,format=yuv420p,curves=all='0/0.03 0.35/0.42 0.7/0.76 1/0.98',eq=contrast=1.06:saturation=1.05,format=rgba[p]",
        "[2:v]setpts=PTS-STARTPTS,scale=1080:1920:flags=bicubic,gblur=sigma=2.2,format=gray[mk]",
        f"[p][mk]alphamerge,scale={pw}:{ph}[pa]",
        "[1:v]setpts=PTS-STARTPTS,format=yuv420p[bg]",
        f"[bg][pa]overlay=x='{x}':y='{y}':eval=frame[b1]",
        f"[b1][5:v]overlay=0:0:enable='lt(t,{INI})'[b2]",   # título por cima de tudo no gancho
        f"[3:v]format=rgba,fade=t=in:st={e}:d=0.25:alpha=1[cd]",
        f"[b2][cd]overlay=x=(W-w)/2:y='150+50*max(0,1-(t-{e})/0.3)':enable='gte(t,{e})'[b3]",
        f"[b3][4:v]overlay=x='{x}-{(1080 - pw) // 2}':y='{y}-{1920 - ph}':eval=frame:format=auto[v]",   # legenda acompanha o peito
        "[0:a]loudnorm=I=-15:TP=-1.5[aud]",
    ]
    run(["-threads", "2", "-i", ORIG, "-i", w("fundo.mp4"), "-i", w("mask-full.mp4"),
         "-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", os.path.join(AQUI, "c-direct.png"),
         "-i", w("legenda.mov"), "-loop", "1", "-framerate", "30", "-t", str(INI), "-i", w("titulo.png"), "-filter_complex", ";".join(fc), "-filter_threads", "2",
         "-map", "[v]", "-map", "[aud]", "-t", str(DUR), "-c:v", "libx264", "-crf", "19", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", SAIDA])
    print("saída:", SAIDA)


if __name__ == "__main__":
    for etapa in sys.argv[1:] or ["fundo", "legenda", "card", "compor"]:
        print(f"[{etapa}]", flush=True)
        globals()[etapa]()
