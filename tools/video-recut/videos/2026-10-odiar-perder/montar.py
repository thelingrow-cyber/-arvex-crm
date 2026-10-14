"""Odiar perder ("a lorota do bom perdedor") — ref. Christopher Speltz DbhL2pnETSV, texto v3 do Vitor.

Molde do chatgpt-cerebro: fotos REAIS flutuando acima da cabeça, sem borda (canto arredondado + sombra),
respiro entre elas, últimos segundos limpos. Abertura com card no topo: foto + título + frase curta.
Entrada = bruto já limpo pelo limpar.cjs (Downloads\\2026-10-odiar-perder-limpo.mp4). Sem música (o Vitor põe no app).
Fotos: Wikimedia Commons (licenças em CREDITOS.txt — colar na legenda do post).

uso: python -I montar.py [cards legenda compor]
"""
import json, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "work", "2026-10-odiar-perder")
ORIG = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "2026-10-odiar-perder-limpo.mp4")
SAIDA = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "2026-10-odiar-perder.mp4")
DUR = 27.27
SEMI = r"C:\Windows\Fonts\seguisb.ttf"
BLACK = r"C:\Windows\Fonts\seguibl.ttf"
OURO = (221, 184, 112)

# boné a partir de y ~720 → topo livre até ~690
# v2 (pedido do Vitor): card do topo PARADO o vídeo todo (sem entrar/sair), headline em cima da foto;
# as outras fotos vão para as laterais (TV à esquerda, parede à direita), sem cobrir o rosto (x ~400–800).
ESQ, DIR = (185, 1010), (895, 960)
# (arquivo em work/cand, entra, sai, lugar, largura)
CARDS = [
    ("jordan.jpg", 7.55, 9.25, ESQ, 300),    # "nunca conheci alguém que construiu algo grande"
    ("senna.jpg", 9.25, 10.75, DIR, 300),    # "e aceitava perder numa boa. Isso é lorota."
    ("boxe.jpg", 14.15, 16.35, ESQ, 300),    # "usa essa raiva pra voltar mais forte. Isso é lei."
    ("podio.jpg", 23.85, 25.85, DIR, 300),   # "É a raiva de perder que faz você voltar mais forte." — depois, rosto limpo
]

CREDITOS = """Fotos: Wikimedia Commons — "At the net" (CC BY-SA 2.0) · "Michael Jordan" (CC BY-SA 2.0) · "Ayrton Senna in 1988" (CC BY 2.0) ·
"Ike Williams and punching bag" (CC BY 4.0) · "Podium celebration at the 2026 Australian Grand Prix" (CC BY-SA 4.0)"""


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


def abertura():
    """Headline em cima (faixa escura: frase curta dourada + título) e a foto da rede embaixo. Fica parado o vídeo todo."""
    L, FT, FA = 680, 150, 380
    card = Image.new("RGBA", (L, FT + FA), (20, 20, 26, 255))
    card.alpha_composite(recorte(Image.open(w("cand/net3.jpg")), L, FA), (0, FT))
    d = ImageDraw.Draw(card)
    fk, tam = ImageFont.truetype(SEMI, 30), 52
    while d.textlength("A LOROTA DO BOM PERDEDOR", font=ImageFont.truetype(BLACK, tam)) > L - 68:
        tam -= 1
    d.rectangle([36, 30, 44, 62], fill=OURO)
    d.text((58, 24), "perder bem é bonito?", font=fk, fill=OURO)
    d.text((34, 68), "A LOROTA DO BOM PERDEDOR", font=ImageFont.truetype(BLACK, tam), fill=(255, 255, 255))
    return sombra(arredondar(card))


def cards():
    abertura().save(w("abre.png"))
    for i, (arq, *_r, larg) in enumerate(CARDS):
        moldura(Image.open(os.path.join(WORK, "cand", arq)), larg).save(w(f"card{i}.png"))
    open(os.path.join(AQUI, "CREDITOS.txt"), "w", encoding="utf-8").write(CREDITOS)


def palavras():
    ws = json.load(open(w("limpeza/palavras-editado.json"), encoding="utf-8"))
    ws = [[x["word"].strip(), x["start"]] for x in ws]
    i = next(k for k, x in enumerate(ws) if x[0].startswith("sincero"))
    ws.insert(i, ["Sendo", ws[i][1] - 0.25])       # o limpar.cjs perdeu a palavra na emenda (o áudio tem)
    out = []
    for k, (p, a) in enumerate(ws):
        b = ws[k + 1][1] if k + 1 < len(ws) else DUR
        out.append([p, a, min(b, a + 0.6)])
    return out


def legenda():
    """Segoe Semibold branca com sombra, até 3 palavras, no peito (receita aprovada da tela dividida)."""
    ws = palavras()
    trocar = {"conheceu": "conheceu?"}
    grupos, atual = [], []
    for i, x in enumerate(ws):
        atual.append(x)
        pausa = i + 1 < len(ws) and ws[i + 1][1] - x[2] > 0.3
        if len(atual) >= 3 or x[0][-1] in ".,?!" or pausa or i == len(ws) - 1 or x[0] in trocar:
            grupos.append([" ".join(trocar.get(y[0], y[0]) for y in atual).rstrip(".,"), atual[0][1], x[2]])
            atual = []
    fonte = ImageFont.truetype(SEMI, 64)
    pasta = w("leg"); shutil.rmtree(pasta, ignore_errors=True); os.makedirs(pasta)
    vazio = os.path.join(pasta, "vazio.png"); Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
    linhas, t = [], 0.0
    for i, (txt, a, b) in enumerate(grupos):
        nxt = grupos[i + 1][1] if i + 1 < len(grupos) else DUR
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


def compor():
    ins = ["-i", ORIG]
    fc = ["[0:v]fps=30,scale=1080:1920,format=yuv420p[b0]"]
    ult, n = "b0", 1

    def pos(lugar, wpx, hpx, e):
        cx, cy = lugar
        return f"x={cx}-{wpx}/2:y='{cy}-{hpx}/2+28*max(0,1-(t-{e})/0.22)'"

    ins += ["-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", w("abre.png")]
    fc.append(f"[{ult}][{n}:v]overlay=x=(W-w)/2:y=40[oab]")   # parado do início ao fim
    ult, n = "oab", n + 1
    for i, (arq, e, s, lugar, larg) in enumerate(CARDS):
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
