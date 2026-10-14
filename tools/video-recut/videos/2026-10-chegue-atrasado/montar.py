"""Chegue atrasado (Regra, molde Luana) — roteiro do Vitor de 13/10.

Molde do odiar-perder: card PARADO no topo (foto + título embaixo) e imagens reais nas laterais, SEM texto junto
(pedido do Vitor). Cada exemplo entra em par: o que chegou depois à esquerda, o que já existia à direita.
No trecho do repositório, a foto do topo troca pela página real do repositório (github.com/morluto/rea).
Entrada = bruto já limpo pelo limpar.cjs (Downloads\\2026-10-chegue-atrasado-limpo.mp4). Sem música (o Vitor põe no app).
Legenda sai da re-transcrição do limpo (work\\2026-10-chegue-atrasado-chk), que traz as palavras que a emenda comeu.

uso: python -I montar.py [cards legenda previa compor]
"""
import json, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "work", "2026-10-chegue-atrasado")
ORIG = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "2026-10-chegue-atrasado-limpo.mp4")
SAIDA = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "2026-10-chegue-atrasado.mp4")
DUR = 76.6
SEMI = r"C:\Windows\Fonts\seguisb.ttf"
BLACK = r"C:\Windows\Fonts\seguibl.ttf"

# boné a partir de y ~660; rosto em x ~320–775 → laterais livres: x 0–300 e 790–1080
ESQ, DIR = (160, 900), (922, 900)
# (arquivo em work/cand, entra, sai, lugar, largura, tipo)
CARDS = [
    ("iphone2.jpg", 26.55, 28.20, ESQ, 250, "foto"),     # "Quando o iPhone saiu,"
    ("nokia.jpg", 27.28, 28.20, DIR, 250, "foto"),       # "já existia celular."
    ("google.jpg", 28.36, 30.05, ESQ, 250, "logo"),      # "Quando o Google chegou,"
    ("altavista.jpg", 29.16, 30.05, DIR, 250, "logo"),   # "já tinha buscador."
    ("zoom.jpg", 30.34, 33.40, ESQ, 250, "logo"),        # "Quando o Zoom apareceu,"
    ("skype.jpg", 31.92, 33.40, DIR, 250, "logo"),       # "todo mundo já fazia chamada de vídeo no Skype."
]
# janelas em que a página do repositório ocupa o lugar da foto do topo
REPO = [(49.20, 57.75), (69.00, DUR)]

CREDITOS = """Fotos: Wikimedia Commons — "Track Cycling Women's Team Pursuit" (Sandro Halank, CC BY-SA 4.0) ·
"iPhone First Generation 8GB" (CC BY-SA 2.0) · "Nokia N95 8GB - Front (Open)" (Beamish4, CC BY-SA 4.0).
Logos Google, AltaVista, Zoom e Skype: domínio público (marca registrada dos donos). Tela: github.com/morluto/rea (MIT)."""


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def w(n):
    return os.path.join(WORK, n)


def sombra(im, raio=20, pad=30):
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    s = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([pad, pad + 8, pad + im.width, pad + im.height + 8], raio, fill=(0, 0, 0, 140))
    out = Image.alpha_composite(s.filter(ImageFilter.GaussianBlur(14)), out)
    out.alpha_composite(im, (pad, pad))
    return out


def recorte(im, larg, alt):
    im = im.convert("RGB")
    e = max(larg / im.width, alt / im.height)
    im = im.resize((int(im.width * e) + 1, int(im.height * e) + 1), Image.LANCZOS)
    x0, y0 = (im.width - larg) // 2, (im.height - alt) // 2
    return im.crop((x0, y0, x0 + larg, y0 + alt)).convert("RGBA")


def arredondar(im, raio=20):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], raio, fill=255)
    im.putalpha(m)
    return im


def moldura(im, larg):
    """Foto sem borda, canto arredondado e sombra suave."""
    alt = min(int(im.height * larg / im.width), int(larg * 1.15))
    return sombra(arredondar(recorte(im, larg, alt)))


def logo(im, larg):
    """Logo inteiro sobre cartão branco (sem recortar a marca)."""
    im = im.convert("RGBA")
    alt = int(larg * 0.58)
    base = Image.new("RGBA", (larg, alt), (255, 255, 255, 255))
    e = min((larg - 44) / im.width, (alt - 44) / im.height)
    im = im.resize((max(1, int(im.width * e)), max(1, int(im.height * e))), Image.LANCZOS)
    base.alpha_composite(im, ((larg - im.width) // 2, (alt - im.height) // 2))
    return sombra(arredondar(base))


L_TOPO, A_TOPO = 680, 400


def abertura():
    """Só a foto e o título escrito direto no vídeo, embaixo dela. Parado o vídeo todo."""
    TXT, tam = "CHEGUE ATRASADO", 64
    ft = ImageFont.truetype(BLACK, tam)
    foto = sombra(arredondar(recorte(Image.open(w("cand/pursuit0.jpg")), L_TOPO, A_TOPO)))
    yt = foto.height - 12
    out = Image.new("RGBA", (1080, yt + tam + 30), (0, 0, 0, 0))
    out.alpha_composite(foto, ((1080 - foto.width) // 2, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    x = (1080 - d.textlength(TXT, font=ft)) / 2
    d.text((x, yt + 4), TXT, font=ft, fill=(0, 0, 0, 200))
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(out).text((x, yt), TXT, font=ft, fill=(255, 255, 255))
    return out


def repo():
    """Página real do repositório (captura em largura de celular), do nome até a descrição."""
    im = Image.open(w("cand/repo.png")).convert("RGB")
    im = im.crop((0, 470, 1290, 470 + int(1290 * A_TOPO / L_TOPO)))
    return sombra(arredondar(recorte(im, L_TOPO, A_TOPO)))


def cards():
    abertura().save(w("abre.png"))
    repo().save(w("repo.png"))
    for i, (arq, _e, _s, _l, larg, tipo) in enumerate(CARDS):
        im = Image.open(os.path.join(WORK, "cand", arq))
        (logo if tipo == "logo" else moldura)(im, larg).save(w(f"card{i}.png"))
    open(os.path.join(AQUI, "CREDITOS.txt"), "w", encoding="utf-8").write(CREDITOS)


def palavras():
    j = json.load(open(os.path.join(os.path.dirname(WORK), "2026-10-chegue-atrasado-chk", "limpeza", "transcricao.json"),
                       encoding="utf-8"))
    ws = [[x["word"].strip(), x["start"]] for x in j["words"]]
    trocar = {"Ora,": "Agora,", "repositor": "repositório", "Querer": "querer", "Aqui": "aqui", "E": "e",
              "dela": "dela.", "replica": "replica.", "pegar": "pegar.", "DM": "DM.", "deixe": "deixei",
              "funciona": "funciona,", "também,": "também.", "agora": "Agora"}
    out = []
    for k, (p, a) in enumerate(ws):
        if k and a <= out[-1][1]:                 # o Whisper às vezes devolve o início fora de ordem
            prox = ws[k + 1][1] if k + 1 < len(ws) else a
            a = max(out[-1][1] + 0.12, min(prox - 0.12, out[-1][1] + 0.3))
        if p == "E" and not out[-1][0].endswith(","):
            p = "e"
        out.append([trocar.get(p, p), a])
    i = next(k for k, x in enumerate(out) if x[0] == "graça")      # "de graça pra você." — a re-transcrição pulou
    out[i + 1:i + 1] = [["pra", 66.20], ["você.", 66.36]]
    out[i + 3][1] = max(out[i + 3][1], 66.68)
    fim = []
    for k, (p, a) in enumerate(out):
        b = out[k + 1][1] if k + 1 < len(out) else DUR
        fim.append([p, a, min(b, a + 0.6)])
    return fim


def grupos():
    ws = palavras()
    gs, atual = [], []
    for i, x in enumerate(ws):
        atual.append(x)
        pausa = i + 1 < len(ws) and ws[i + 1][1] - x[2] > 0.3
        if len(atual) >= 3 or x[0][-1] in ".,?!" or pausa or i == len(ws) - 1:
            gs.append([" ".join(y[0] for y in atual).rstrip(".,"), atual[0][1], x[2]])
            atual = []
    return gs


def legenda():
    """Segoe Semibold branca com sombra, até 3 palavras, no peito (receita aprovada)."""
    gs = grupos()
    fonte = ImageFont.truetype(SEMI, 64)
    pasta = w("leg"); shutil.rmtree(pasta, ignore_errors=True); os.makedirs(pasta)
    vazio = os.path.join(pasta, "vazio.png"); Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
    linhas, t = [], 0.0
    for i, (txt, a, b) in enumerate(gs):
        nxt = gs[i + 1][1] if i + 1 < len(gs) else DUR
        b = min(max(b, a + 0.3) + 0.3, nxt)
        if a > t:
            linhas.append((vazio, a - t))
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        larg = ImageDraw.Draw(img).textlength(txt, font=fonte)
        ImageDraw.Draw(sh).text(((1080 - larg) / 2, 1473), txt, font=fonte, fill=(0, 0, 0, 210))
        img = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)), img)
        ImageDraw.Draw(img).text(((1080 - larg) / 2, 1470), txt, font=fonte, fill="white")
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
    print(" | ".join(g[0] for g in gs))


def previa():
    """Quadros montados no PIL (sem render) para conferir posição: work\\previa.jpg."""
    tempos = [3.0, 27.7, 29.6, 32.6, 52.0, 72.5]
    tiles = []
    for t in tempos:
        f = w("_q.png")
        run(["-ss", str(t), "-i", ORIG, "-frames:v", "1", "-vf", "scale=1080:1920", f])
        im = Image.open(f).convert("RGBA")
        im.alpha_composite(Image.open(w("abre.png")), (0, 30))
        if any(a <= t <= b for a, b in REPO):
            r = Image.open(w("repo.png")); im.alpha_composite(r, ((1080 - r.width) // 2, 30))
        for i, (_a, e, s, (cx, cy), _l, _t) in enumerate(CARDS):
            if e <= t <= s:
                c = Image.open(w(f"card{i}.png")); im.alpha_composite(c, (cx - c.width // 2, cy - c.height // 2))
        tiles.append(im.convert("RGB").resize((360, 640)))
    os.remove(w("_q.png"))
    sh = Image.new("RGB", (360 * len(tiles), 640))
    for i, tl in enumerate(tiles):
        sh.paste(tl, (360 * i, 0))
    sh.save(w("previa.jpg"), quality=82)


def compor():
    ins = ["-i", ORIG]
    fc = ["[0:v]fps=30,scale=1080:1920,format=yuv420p[b0]"]
    ult, n = "b0", 1

    def pos(lugar, wpx, hpx, e):
        cx, cy = lugar
        return f"x={cx}-{wpx}/2:y='{cy}-{hpx}/2+28*max(0,1-(t-{e})/0.22)'"

    ins += ["-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", w("abre.png")]
    fc.append(f"[{ult}][{n}:v]overlay=x=0:y=30[oab]")   # parado do início ao fim
    ult, n = "oab", n + 1
    rw = Image.open(w("repo.png")).width
    for k, (e, s) in enumerate(REPO):                   # página do repositório no lugar da foto do topo
        ins += ["-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", w("repo.png")]
        sai = f",fade=t=out:st={s - 0.3}:d=0.3:alpha=1" if s < DUR else ""
        fc.append(f"[{n}:v]format=rgba,fade=t=in:st={e}:d=0.3:alpha=1{sai}[r{k}]")
        fc.append(f"[{ult}][r{k}]overlay=x={(1080 - rw) // 2}:y=30:enable='between(t,{e},{s})'[or{k}]")
        ult, n = f"or{k}", n + 1
    for i, (arq, e, s, lugar, larg, _t) in enumerate(CARDS):
        im = Image.open(w(f"card{i}.png"))
        ins += ["-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", w(f"card{i}.png")]
        fc.append(f"[{n}:v]format=rgba,fade=t=in:st={e}:d=0.15:alpha=1,fade=t=out:st={s - 0.15}:d=0.15:alpha=1[c{i}]")
        fc.append(f"[{ult}][c{i}]overlay={pos(lugar, im.width, im.height, e)}:enable='between(t,{e},{s})'[o{i}]")
        ult, n = f"o{i}", n + 1
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
