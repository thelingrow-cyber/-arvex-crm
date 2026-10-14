"""Rei do gelo (Frederic Tudor) — "ser o melhor do jeito antigo não te protege do jeito novo".

Molde do "grandes homens dizem não" (pedido do Vitor, 14/10): imagem no topo, SEM borda redonda e sem sombra,
título condensado branco embaixo, parado o vídeo todo. As inserções trocam a imagem do topo (sempre uma só, em cima),
casadas com a fala. Só imagem histórica real que remete ao que ele fala; nada genérico, nada de fundo branco.
Entrada = bruto limpo (Downloads\\2026-10-video-2-limpo.mp4). Legenda da re-transcrição do limpo (work\\2026-10-video-2-chk).
Sem música (o Vitor põe no app).

uso: python -I montar.py [imagens legenda previa compor]
"""
import json, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
WORK = os.path.join(RAIZ, "work", "2026-10-video-2")
CHK = os.path.join(RAIZ, "work", "2026-10-video-2-chk", "limpeza", "transcricao.json")
ORIG = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "2026-10-video-2-limpo.mp4")
SAIDA = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "2026-10-rei-do-gelo.mp4")
DUR = 37.87
SEMI = r"C:\Windows\Fonts\seguisb.ttf"
COND = r"C:\Windows\Fonts\bahnschrift.ttf"

TITULO = "ATÉ OS MELHORES AFUNDAM."
FONTES = os.path.join(RAIZ, "assets", "fontes")
BEBAS = os.path.join(FONTES, "BebasNeue-Regular.ttf")      # título: a mesma da referência "grandes homens dizem não"
MONT = os.path.join(FONTES, "Montserrat.ttf")              # legenda: uma palavra por vez, como na referência
L, A, Y = 540, 400, 110          # imagem do topo (boné começa em y ~740)

# v2 (pedido do Vitor): UMA imagem fixa no topo o vídeo todo; as inserções entram nas laterais, uma de cada lado.
# (arquivo em work/cand, entra em, recorte relativo (x0, y0, x1, y1) antes de enquadrar)
TOPO = [
    ("cole.jpg", 0.00, (0.30, 0.02, 1.0, 0.86)),  # v4: Thomas Cole, "O Curso do Império: Destruição" (1836) — o herói de pedra sem cabeça, a cidade queimando
]
ESQ, DIR = (170, 985), (910, 985)   # rosto em x ~330–740
LARG, ALT = 310, 390                # vertical: ocupa a lateral inteira sem chegar no rosto
# (arquivo, entra, sai, lado, recorte)
LADOS = [
    ("tudor.jpg", 3.50, 6.10, ESQ, (0, 0.05, 1, 0.75)),           # "Frederic Tudor ficou milionário vendendo gelo"
    ("clearwater.jpg", 6.20, 8.05, DIR, (0.25, 0.05, 0.85, 0.95)),  # "cortava blocos dos lagos congelados"
    ("navio.jpg", 8.10, 9.60, ESQ, (0, 0, 1, 1)),                 # "e mandava de navio até o Caribe"
    ("indiana.jpg", 9.62, 11.50, DIR, (0, 0, 1, 1)),              # "chamavam ele de rei do gelo"
    ("fabrica2.jpg", 11.60, 16.70, ESQ, (0, 0.10, 1, 0.62)),      # "aí inventaram a fábrica de gelo"
    ("geladeira.jpg", 16.80, 21.90, DIR, (0, 0.1, 0.7, 1)),           # "depois veio a geladeira em casa"
    ("maranacook.jpg", 22.00, 26.65, ESQ, (0.40, 0.13, 0.96, 0.92)),  # "nenhum deles era ruim… os melhores do mundo"
    ("minnesota.jpg", 26.75, 31.40, DIR, (0.07, 0.11, 0.47, 0.84)),   # "continuaram cortando gelo enquanto o mundo mudava"
]

CREDITOS = """Imagens (Wikimedia Commons, domínio público salvo indicação): Thomas Cole, "The Course of Empire: Destruction" (New-York Historical Society) ·
Francis Alexander, "Frederic Tudor" (Museum of Fine Arts, Boston) · "Ice harvest on Clearwater Lake" (NARA) ·
James E. Buttersworth, "Clipper Ship at Cape Horn" · "Harvesting Ice in Indiana" · "Ice factory of Sträter, Esser & Co., Paramaribo, c.1900"
(KITLV) · "1929 General Electric Monitor Top" (Michael Rivera, CC BY-SA 4.0) ·
"Harvesting your ice supply at Maranacook Lodge" (Tichnor Brothers) · "Minnesota ice harvest" (Whitney & Zimmerman)."""


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def w(n):
    return os.path.join(WORK, n)


def enquadrar(im, larg, alt):
    im = im.convert("RGB")
    e = max(larg / im.width, alt / im.height)
    im = im.resize((int(im.width * e) + 1, int(im.height * e) + 1), Image.LANCZOS)
    x0, y0 = (im.width - larg) // 2, (im.height - alt) // 2
    return im.crop((x0, y0, x0 + larg, y0 + alt))


def imagens():
    for i, (arq, _t, (a, b, c, d)) in enumerate(TOPO):
        im = Image.open(w(f"cand/{arq}")).convert("RGB")
        im = im.crop((int(a * im.width), int(b * im.height), int(c * im.width), int(d * im.height)))
        ImageOps.autocontrast(enquadrar(im, L, A), cutoff=1).save(w(f"topo{i}.png"))   # foto antiga desbotada
    for i, (arq, _e, _s, _l, (a, b, c, d)) in enumerate(LADOS):    # cantos retos, sem sombra
        im = Image.open(w(f"cand/{arq}")).convert("RGB")
        im = im.crop((int(a * im.width), int(b * im.height), int(c * im.width), int(d * im.height)))
        ImageOps.autocontrast(enquadrar(im, LARG, ALT), cutoff=1).save(w(f"lado{i}.png"))
    # título: Bebas Neue branca, contorno escuro fino + sombra suave (referência "grandes homens dizem não")
    tam = 96
    while True:
        ft = ImageFont.truetype(BEBAS, tam)
        if ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(TITULO, font=ft) <= 800:
            break
        tam -= 2
    out = Image.new("RGBA", (1080, 150), (0, 0, 0, 0))
    x = (1080 - ImageDraw.Draw(out).textlength(TITULO, font=ft)) / 2
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((x, 24), TITULO, font=ft, fill=(0, 0, 0, 220), stroke_width=6, stroke_fill=(0, 0, 0, 220))
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(out).text((x, 20), TITULO, font=ft, fill=(255, 255, 255), stroke_width=2, stroke_fill=(20, 20, 20))
    out.save(w("titulo.png"))
    open(os.path.join(AQUI, "CREDITOS.txt"), "w", encoding="utf-8").write(CREDITOS)


def palavras():
    ws = [[x["word"].strip(), x["start"]] for x in json.load(open(CHK, encoding="utf-8"))["words"]]
    trocar = {"Enquanto": "enquanto", "lado": "lado.", "novo": "novo.", "ele": "ele.", "gelo": "gelo"}
    out = []
    for k, (p, a) in enumerate(ws):
        if k and a <= out[-1][1]:                 # início fora de ordem devolvido pelo Whisper
            prox = ws[k + 1][1] if k + 1 < len(ws) else a + 0.3
            a = max(out[-1][1] + 0.12, min(prox - 0.12, out[-1][1] + 0.3))
        out.append([p, a])
    out[0][0] = "Ser o" if out[0][0] == "Seu" else out[0][0]   # ele fala "Ser o melhor", o Whisper ouviu "Seu"
    out[-1][0] = "ele."
    for x in out:
        x[0] = trocar.get(x[0], x[0]) if x[0] != "ele" else x[0]
    return [[p, a, min(out[k + 1][1] if k + 1 < len(out) else DUR, a + 0.6)] for k, (p, a) in enumerate(out)]


def grupos():
    ws = palavras()
    gs, atual = [], []
    for i, x in enumerate(ws):
        atual.append(x)
        pausa = i + 1 < len(ws) and ws[i + 1][1] - x[2] > 0.3
        sobra1 = i == len(ws) - 2                 # não deixar a última palavra sozinha
        if (len(atual) >= 3 and not sobra1) or x[0][-1] in ".,?!" or pausa or i == len(ws) - 1:
            gs.append([" ".join(y[0] for y in atual).rstrip(".,"), atual[0][1], x[2]])
            atual = []
    return gs


def legenda():
    """v3: uma palavra por vez, Montserrat ExtraBold minúscula, branca com contorno preto (referência)."""
    ws = palavras()
    fonte = ImageFont.truetype(MONT, 54)
    fonte.set_variation_by_name("ExtraBold")
    pasta = w("leg"); shutil.rmtree(pasta, ignore_errors=True); os.makedirs(pasta)
    vazio = os.path.join(pasta, "vazio.png"); Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
    linhas, t = [], 0.0
    for i, (p, a, _b) in enumerate(ws):
        txt = p.lower().rstrip(".,?!") if p != "XIX," else "XIX"
        txt = "Frederic" if txt == "frederic" else "Tudor" if txt == "tudor" else "Caribe" if txt == "caribe" else txt
        b = ws[i + 1][1] if i + 1 < len(ws) else DUR
        if b - a > 0.8:                                   # pausa longa: a palavra não fica parada na tela
            b = a + 0.8
        if a > t:
            linhas.append((vazio, a - t))
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        larg = ImageDraw.Draw(img).textlength(txt, font=fonte)
        x, y = (1080 - larg) / 2, 1440
        ImageDraw.Draw(sh).text((x, y + 4), txt, font=fonte, fill=(0, 0, 0, 160), stroke_width=7, stroke_fill=(0, 0, 0, 160))
        img = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)), img)
        ImageDraw.Draw(img).text((x, y), txt, font=fonte, fill="white", stroke_width=5, stroke_fill=(15, 15, 15))
        q = os.path.join(pasta, f"{i:03d}.png"); img.save(q)
        linhas.append((q, b - a)); t = b
    linhas.append((vazio, DUR - t + 0.5))
    lista = os.path.join(pasta, "lista.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for q, d in linhas:
            f.write(f"file '{q}'\nduration {d:.3f}\n")
        f.write(f"file '{vazio}'\n")
    run(["-f", "concat", "-safe", "0", "-i", lista, "-vf", "fps=30,format=rgba", "-c:v", "qtrle", w("legenda.mov")])
    shutil.rmtree(pasta)
    print(" ".join(x[0] for x in ws))


def ativa(t):
    return max(i for i, (_a, e, _r) in enumerate(TOPO) if e <= t)


def previa():
    tempos = [1.0, 4.5, 7.0, 8.8, 10.5, 13.0, 18.0, 24.0, 29.0, 36.0]
    tiles = []
    for t in tempos:
        f = w("_q.png")
        run(["-ss", str(t), "-i", ORIG, "-frames:v", "1", "-vf", "scale=1080:1920", f])
        im = Image.open(f).convert("RGBA")
        im.paste(Image.open(w(f"topo{ativa(t)}.png")), ((1080 - L) // 2, Y))
        tt = Image.open(w("titulo.png")); im.alpha_composite(tt, (0, Y + A + 14))
        for i, (_a, e, s, (cx, cy), _r) in enumerate(LADOS):
            if e <= t <= s:
                c = Image.open(w(f"lado{i}.png")); im.paste(c, (cx - c.width // 2, cy - c.height // 2))
        tiles.append(im.convert("RGB").resize((270, 480)))
    os.remove(w("_q.png"))
    sh = Image.new("RGB", (270 * 5, 480 * 2))
    for i, tl in enumerate(tiles):
        sh.paste(tl, (270 * (i % 5), 480 * (i // 5)))
    sh.save(w("previa.jpg"), quality=82)


def compor():
    ins = ["-i", ORIG]
    fc = ["[0:v]fps=30,scale=1080:1920,format=yuv420p[b0]"]
    ult, n = "b0", 1
    for i, (_a, e, _r) in enumerate(TOPO):
        fim = TOPO[i + 1][1] + 0.2 if i + 1 < len(TOPO) else DUR
        ins += ["-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", w(f"topo{i}.png")]
        fade = f",fade=t=in:st={e}:d=0.2:alpha=1" if e > 0 else ""
        fc.append(f"[{n}:v]format=rgba{fade}[t{i}]")
        fc.append(f"[{ult}][t{i}]overlay=x={(1080 - L) // 2}:y={Y}:enable='between(t,{e},{fim})'[o{i}]")
        ult, n = f"o{i}", n + 1
    ins += ["-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", w("titulo.png")]
    fc.append(f"[{ult}][{n}:v]overlay=x=0:y={Y + A + 14}[ot]")
    ult, n = "ot", n + 1
    for i, (_a, e, s, (cx, cy), _r) in enumerate(LADOS):
        im = Image.open(w(f"lado{i}.png"))
        ins += ["-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", w(f"lado{i}.png")]
        fc.append(f"[{n}:v]format=rgba,fade=t=in:st={e}:d=0.15:alpha=1,fade=t=out:st={s - 0.15}:d=0.15:alpha=1[l{i}]")
        y = f"{cy - im.height // 2}+28*max(0,1-(t-{e})/0.22)"
        fc.append(f"[{ult}][l{i}]overlay=x={cx - im.width // 2}:y='{y}':enable='between(t,{e},{s})'[ol{i}]")
        ult, n = f"ol{i}", n + 1
    ins += ["-i", w("legenda.mov")]
    fc.append(f"[{ult}][{n}:v]overlay=format=auto[v]")
    fc.append("[0:a]loudnorm=I=-15:TP=-1.5[aud]")
    run(["-threads", "2"] + ins + ["-filter_complex", ";".join(fc), "-filter_threads", "2", "-map", "[v]",
         "-map", "[aud]", "-t", str(DUR), "-c:v", "libx264", "-crf", "20", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", SAIDA])
    print("saída:", SAIDA)


if __name__ == "__main__":
    for etapa in sys.argv[1:] or ["imagens", "legenda", "compor"]:
        print(f"[{etapa}]", flush=True)
        globals()[etapa]()
