"""ChatGPT × cérebro ("e se pensar for chutar e corrigir?") — edição no molde Vitor M. Guerrero.

Take único, sem corte, sem zoom, sem trilha. CARTÃO ILUSTRATIVO FLUTUANTE (~1/3 da largura) com a coisa literal
que está sendo dita, trocando de lugar (acima da cabeça / esquerda / direita) sem cobrir o rosto.
Legenda serifada branca pequena, 2–3 palavras, na linha do peito.
Fotos: Wikimedia Commons (licenças em CREDITOS — colar na legenda do post). Dois cartões desenhados aqui:
o pico do sinal de surpresa (N400) e o "chute da próxima palavra" com as probabilidades.

uso: python montar.py [cards legenda compor]
"""
import json, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "work", "2026-10-chatgpt-cerebro")
ORIG = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "13A51DC7-D5A9-41DF-9E0C-465B21D4D8EA.mp4")
SAIDA = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "2026-10-chatgpt-cerebro.mp4")
DUR = 50.8
SERIF = r"C:\Windows\Fonts\georgia.ttf"
SEMI = r"C:\Windows\Fonts\seguisb.ttf"
BLACK = r"C:\Windows\Fonts\seguibl.ttf"

# lugares: centro do cartão. Rosto em x 375–675, y 750–1100 (cap a partir de ~650)
TOPO, ESQ, DIR = (540, 400), (195, 860), (885, 860)
# (arquivo em work/cand, entra, sai, lugar, largura)
# v3 + pedido do Vitor: posições variadas (topo/esquerda/direita) e imagem desde o 1º segundo. (conferido quadro a quadro no 4D dele: ~10 inserções em 80 s, quase todas ACIMA DA CABEÇA, 2–15 s cada,
# respiros longos e os últimos segundos limpos). v2 tinha 24 trocando a cada ~2 s — agitado demais.
CARDS = [
    ("datacenter2.jpg", 0.0, 2.45, TOPO, 420),   # gancho: "se você entendesse como a IA funciona por dentro"
    ("cerebro2.jpg", 2.45, 5.0, DIR, 340),      # gancho: "…como o seu cérebro funciona" (o 4D dele também abre com imagem)
    ("livrob2.jpg", 5.1, 9.2, ESQ, 360),        # "Era uma vez… terminou essa frase antes de mim"
    ("modelo2.jpg", 11.0, 14.65, TOPO, 400),     # "neurocientista… o cérebro não espera o mundo"
    ("eeg0.jpg", 19.0, 22.6, DIR, 360),         # "1980, eletrodos na cabeça"
    ("paob1.jpg", 23.6, 25.75, ESQ, 340),       # "manteiga no pão com meia"
    ("pensador2.jpg", 39.3, 44.6, DIR, 340),    # "e se a gente não pensa… ideia, decisão"
    ("espelhob0.jpg", 48.4, 50.3, TOPO, 400),    # "se vendo no espelho" — depois, rosto limpo
]
ANIM = [("onda", 25.9, 27.9, TOPO), ("chute", 29.2, 34.4, TOPO)]   # cartões desenhados (mov)

CREDITOS = """Imagens: Wikimedia Commons — data center (CC BY-SA 4.0) · ressonância do cérebro (CC BY-SA 2.0) · livro antigo (CC BY 2.0) · cérebro (CC BY 4.0) · touca de EEG (CC BY 2.0) ·
pão com manteiga (CC BY-SA 4.0) · O Pensador, Rodin (CC0) · espelho (CC BY 2.0)"""


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def w(n):
    return os.path.join(WORK, n)


def moldura(im, larg, raio=18, pad=30):
    """Foto com canto arredondado e sombra suave (sem borda, sem texto — como o Guerrero)."""
    im = im.convert("RGB")
    alt = min(int(im.height * larg / im.width), int(larg * 1.15))
    e = max(larg / im.width, alt / im.height)
    im = im.resize((int(im.width * e) + 1, int(im.height * e) + 1), Image.LANCZOS)
    x0, y0 = (im.width - larg) // 2, (im.height - alt) // 2
    im = im.crop((x0, y0, x0 + larg, y0 + alt)).convert("RGBA")
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, larg - 1, alt - 1], raio, fill=255)
    im.putalpha(m)
    out = Image.new("RGBA", (larg + 2 * pad, alt + 2 * pad), (0, 0, 0, 0))
    s = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([pad, pad + 8, pad + larg, pad + alt + 8], raio, fill=(0, 0, 0, 140))
    out = Image.alpha_composite(s.filter(ImageFilter.GaussianBlur(14)), out)
    out.alpha_composite(im, (pad, pad))
    return out


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def onda(t, larg=420, alt=230):
    """Traço de EEG correndo; o pico de surpresa (N400) estoura em t≈0,4 s ("pico")."""
    import math
    c = Image.new("RGBA", (larg, alt), (250, 250, 248, 255))
    d = ImageDraw.Draw(c)
    for y in range(40, alt, 40):
        d.line([(0, y), (larg, y)], fill=(225, 225, 222), width=1)
    d.text((16, 10), "EEG · palavra inesperada", font=ImageFont.truetype(SEMI, 20), fill=(110, 110, 110))
    vis = min(1.0, t / 0.9)                      # o traço vai sendo desenhado
    pts = []
    for x in range(0, int(larg * vis)):
        u = x / larg
        y = alt * 0.62 + 7 * math.sin(u * 40) + 4 * math.sin(u * 97)
        y -= 95 * math.exp(-((u - 0.62) / 0.05) ** 2)   # o pico
        pts.append((x, y))
    if len(pts) > 1:
        d.line(pts, fill=(205, 40, 40), width=4)
    if vis >= 0.66:
        d.text((larg * 0.62 + 18, 40), "surpresa!", font=ImageFont.truetype(BLACK, 26), fill=(205, 40, 40))
    return c


def chute(t, larg=480, alt=300):
    """Janela de chat: a frase cresce palavra por palavra; antes de cada palavra aparecem os chutes com %."""
    c = Image.new("RGBA", (larg, alt), (255, 255, 255, 255))
    d = ImageDraw.Draw(c)
    d.text((18, 12), "IA · próxima palavra", font=ImageFont.truetype(SEMI, 20), fill=(120, 120, 120))
    passos = [("Era uma vez um", [("rei", 38), ("menino", 21), ("lugar", 9)]),
              ("Era uma vez um rei", [("que", 44), ("muito", 17), ("sem", 6)]),
              ("Era uma vez um rei que", [("vivia", 52), ("tinha", 19), ("não", 8)])]
    i = min(int(t / 1.7), len(passos) - 1)
    frase, ops = passos[i]
    tl = t - i * 1.7
    f = ImageFont.truetype(SERIF, 32)
    d.text((18, 50), frase + (" ▌" if int(t * 3) % 2 == 0 else ""), font=f, fill=(20, 20, 24))
    fo = ImageFont.truetype(SEMI, 24)
    for k, (pal, pct) in enumerate(ops):
        a = ease((tl - 0.15 * k) / 0.25)
        if a <= 0:
            continue
        y = 112 + k * 58
        cor = (16, 163, 127) if k == 0 and tl > 1.0 else (90, 90, 96)
        fundo = (208, 240, 228) if cor[1] == 163 else (232, 232, 236)   # tom claro opaco (alpha some no RGB)
        d.rounded_rectangle([18, y, 18 + max(16, int(330 * pct / 60 * a)), y + 40], 8, fill=fundo)
        d.text((30, y + 6), pal, font=fo, fill=cor)
        d.text((360, y + 6), f"{pct}%", font=fo, fill=cor)
    return c


def mov(nome, func, dur, larg):
    tmp = w("_frames"); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    for i in range(int(dur * 30)):
        moldura(func(i / 30), larg).save(os.path.join(tmp, f"{i:04d}.png"))
    run(["-framerate", "30", "-i", os.path.join(tmp, "%04d.png"), "-c:v", "qtrle", w(nome)])
    shutil.rmtree(tmp)


def cards():
    for i, (arq, *_r, larg) in enumerate(CARDS):
        moldura(Image.open(os.path.join(WORK, "cand", arq)), larg).save(w(f"card{i}.png"))
    mov("onda.mov", onda, ANIM[0][2] - ANIM[0][1], 420)
    mov("chute.mov", chute, ANIM[1][2] - ANIM[1][1], 480)
    open(os.path.join(AQUI, "CREDITOS.txt"), "w", encoding="utf-8").write(CREDITOS)


def legenda():
    """Serifada branca pequena, até 3 palavras, no peito (y 1430)."""
    ws = [[x["word"].strip(), x["start"], x["end"]] for x in json.load(open(w("words.json"), encoding="utf-8"))["words"]]
    trocar = {"IA,": "IA,"}
    grupos, atual = [], []
    for i, x in enumerate(ws):
        atual.append(x)
        pausa = i + 1 < len(ws) and ws[i + 1][1] - x[2] > 0.3
        if len(atual) >= 3 or x[0][-1] in ".,?!" or pausa or i == len(ws) - 1:
            grupos.append([" ".join(trocar.get(y[0], y[0]) for y in atual).rstrip(".,"), atual[0][1], x[2]])
            atual = []
    fonte = ImageFont.truetype(SERIF, 54)
    pasta = w("leg"); shutil.rmtree(pasta, ignore_errors=True); os.makedirs(pasta)
    vazio = os.path.join(pasta, "vazio.png"); Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
    linhas, t = [], 0.0
    for i, (txt, a, b) in enumerate(grupos):
        nxt = grupos[i + 1][1] if i + 1 < len(grupos) else DUR
        b = min(max(b, a + 0.3) + 0.4, nxt)
        if a > t:
            linhas.append((vazio, a - t))
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        larg = ImageDraw.Draw(img).textlength(txt, font=fonte)
        ImageDraw.Draw(sh).text(((1080 - larg) / 2, 1433), txt, font=fonte, fill=(0, 0, 0, 200))
        img = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)), img)
        ImageDraw.Draw(img).text(((1080 - larg) / 2, 1430), txt, font=fonte, fill="white")
        p = os.path.join(pasta, f"{i:03d}.png"); img.save(p)
        linhas.append((p, b - a)); t = b
    linhas.append((vazio, DUR - t + 0.5))
    lista = os.path.join(pasta, "lista.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for p, d in linhas:
            f.write(f"file '{p}'\nduration {d:.3f}\n")
        f.write(f"file '{vazio}'\n")
    run(["-f", "concat", "-safe", "0", "-i", lista, "-vf", "fps=30,format=rgba", "-c:v", "qtrle", w("legenda.mov")])
    shutil.rmtree(pasta)


def compor():
    ins = ["-i", ORIG]
    fc = ["[0:v]fps=30,scale=1080:1920,format=yuv420p[b0]"]
    ult, n = "b0", 1

    def pos(lugar, wpx, hpx, e):
        cx, cy = lugar
        return f"x={cx}-{wpx}/2:y='{cy}-{hpx}/2+28*max(0,1-(t-{e})/0.22)'"

    for i, (arq, e, s, lugar, larg) in enumerate(CARDS):
        im = Image.open(w(f"card{i}.png"))
        ins += ["-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", w(f"card{i}.png")]
        fc.append(f"[{n}:v]format=rgba,fade=t=in:st={e}:d=0.15:alpha=1,fade=t=out:st={s - 0.15}:d=0.15:alpha=1[c{i}]")
        fc.append(f"[{ult}][c{i}]overlay={pos(lugar, im.width, im.height, e)}:enable='between(t,{e},{s})'[o{i}]")
        ult, n = f"o{i}", n + 1
    for j, (nome, e, s, lugar) in enumerate(ANIM):
        larg = 420 if nome == "onda" else 480
        hpx = (230 if nome == "onda" else 300) + 60
        ins += ["-i", w(f"{nome}.mov")]
        fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{e}/TB,format=rgba,fade=t=in:st={e}:d=0.15:alpha=1[a{j}]")
        fc.append(f"[{ult}][a{j}]overlay={pos(lugar, larg + 60, hpx, e)}:enable='between(t,{e},{s})':eof_action=pass[p{j}]")
        ult, n = f"p{j}", n + 1
    ins += ["-i", w("legenda.mov")]
    fc.append(f"[{ult}][{n}:v]overlay=format=auto[v]")
    fc.append("[0:a]loudnorm=I=-15:TP=-1.5[aud]")
    run(["-threads", "2"] + ins + ["-filter_complex", ";".join(fc), "-filter_threads", "2", "-map", "[v]",
         "-map", "[aud]", "-t", str(DUR), "-c:v", "libx264", "-crf", "20", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", SAIDA])
    print("saída:", SAIDA)


if __name__ == "__main__":
    for etapa in sys.argv[1:] or ["cards", "legenda", "compor"]:
        print(f"[{etapa}]", flush=True)
        globals()[etapa]()
