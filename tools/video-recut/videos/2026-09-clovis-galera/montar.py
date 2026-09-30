"""Voz de fundo (Clóvis de Barros Filho, "a galera gosta") + takes do Vitor sem fala + legenda da marca.

Formato: ref. Carlos Lehmann (DcWj_iKyyIX, 92k ❤) — só a ESTRUTURA (voz de fundo, takes sem fala,
frase no meio da tela, palavra-chave em destaque, 2 takes sem zoom). A IDENTIDADE é nossa:
  - serifada Fraunces (a ref usa Instrument Serif); palavra-chave em ITÁLICO DOURADO (a ref: caixa-alta vermelha)
  - off-white quente; dourado da marca
  - imagem quente e escura ("atelier"), não fria/azulada como a ref
  - cada frase entra com fade + subida curta (sem pipocar)
  - v1 (Inter) foi recusada: "as letras dele ficaram bem melhores" (2026-09-30)
Crédito do áudio na legenda do post.

uso:  python montar.py      →  Downloads/2026-09-clovis-galera.mp4
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(AQUI, "..", "..", "work", "2026-09-clovis-galera")
TAKES = os.path.join(AQUI, "takes")          # enviados em 2026-09-29 (WeTransfer)
SAIDA = os.path.join(os.environ["USERPROFILE"], "Downloads", "2026-09-clovis-galera.mp4")
SERIF = os.path.join(AQUI, "Fraunces.ttf")             # variável (opsz, wght, SOFT, WONK) — Google Fonts, OFL
SERIF_IT = os.path.join(AQUI, "Fraunces-Italic.ttf")
os.makedirs(WORK, exist_ok=True)

OFFWHITE = (244, 240, 230)
OURO = (214, 178, 102)   # dourado da marca, um tom mais claro para ler sobre imagem escura

# grade quente de "atelier": pretos em carvão quente, realces contidos, pouca saturação, grão fino
COR = ("curves=all='0/0.02 0.3/0.16 0.7/0.52 1/0.82',eq=saturation=0.7:contrast=1.08,"
       "colorbalance=rs=0.05:gs=0.015:bs=-0.035:rm=0.03:bm=-0.025:rh=0.015:bh=-0.03,"
       "vignette=PI/4,noise=alls=4:allf=t")

MESA = os.path.join(TAKES, "74C15A77-8FDB-4B26-AC84-FE7CB203E865.mp4")
ESTUDIO = os.path.join(TAKES, "C8D81249-B745-41EB-A3E8-86673BB24A85.mp4")
VARANDA = os.path.join(TAKES, "E3202855-2C0F-41A4-B3BA-DC5D1B9B1DDD.mp4")

# (arquivo, início no arquivo, duração no arquivo, velocidade, recorte antes do 9:16)
# Como a ref: só 2 takes, sem zoom. Troca na frase "de uma vontade genérica".
CENAS = [
    (MESA, 0.0, 19.17, 0.928, ""),       # mesa, plano inteiro
    (ESTUDIO, 0.0, 6.8, 0.806, ""),      # em pé no estúdio (câmera lenta leve)
]
CORTES = [0.0, 20.66, 29.1]

# (texto, início, fim, destaque)
LINHAS = [
    ("A galera gosta,", 0.00, 0.88, False),
    ("Foda-se", 0.88, 1.82, True),
    ("Se o que a galera\ngosta fosse bom,", 1.82, 4.54, False),
    ("não teríamos matado", 4.54, 5.64, False),
    ("Sócrates", 5.64, 6.36, True),
    ("não teríamos matado", 6.36, 7.24, False),
    ("Jesus", 7.24, 7.98, True),
    ("Gandhi", 7.98, 8.76, True),
    ("Martin Luther King", 8.76, 10.40, True),
    ("Todos os grandes foram\nmortos pela galera.", 10.40, 12.96, False),
    ("Então, foda-se o que\na galera acha bom.", 12.96, 15.70, False),
    ("Quem tem que achar\nbom sou eu.", 15.70, 17.36, False),
    ("Quando você é escravo\nde um número,", 17.36, 19.66, False),
    ("Algoritmo", 19.66, 20.66, True),
    ("de uma vontade\ngenérica,", 20.66, 22.40, False),
    ("nossa…", 22.40, 23.08, False),
    ("ela sempre\nte surpreende", 23.08, 24.88, False),
    ("e você fica\ndelirantemente", 24.88, 26.70, False),
    ("à mercê do que dá certo\ne do que dá errado.", 26.70, 29.10, False),
]

Y_CENTRO = 1000      # meio da tela, como a ref; abaixo do rosto nos 2 takes
FPS = 30


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


# ------------------------------------------------------------------ imagem

def cenas():
    partes = []
    for i, (arq, ini, dur, vel, crop) in enumerate(CENAS):
        alvo = CORTES[i + 1] - CORTES[i]
        out = os.path.join(WORK, f"cena{i}.mp4")
        vf = (f"{crop}scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
              f"crop=1080:1920,setsar=1,setpts=PTS/{vel},fps={FPS},{COR},"
              f"trim=0:{alvo:.3f},setpts=PTS-STARTPTS,format=yuv420p")
        run(["-ss", str(ini), "-t", str(dur), "-i", arq, "-an", "-vf", vf,
             "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-g", "30", out])
        partes.append(out)
    lista = os.path.join(WORK, "cenas.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for p in partes:
            f.write(f"file '{p}'\n".replace("\\", "/"))
    run(["-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", os.path.join(WORK, "imagem.mp4")])
    for p in partes:
        os.remove(p)


# ------------------------------------------------------------------ tipografia
# Identidade própria (2026-09-30, pedido do Vitor: "as letras da ref ficaram melhores — faça melhor"):
# serifada Fraunces (não a Instrument Serif da ref); frase em regular suave; palavra-chave em
# ITÁLICO DOURADO (a ref usa caixa-alta vermelha). Exceção consciente à regra "nunca serif" das
# diretrizes do carrossel — vale para este formato de voz de fundo.

def serif(tam, italico=False):
    f = ImageFont.truetype(SERIF_IT if italico else SERIF, tam)
    # opsz, wght, SOFT, WONK
    f.set_variation_by_axes([144, 470, 100, 1] if italico else [72, 380, 50, 0])
    return f


def quadro(txt, dest, alpha=1.0, subida=0):
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    if dest:
        tam, cor = 168, OURO
        while ImageDraw.Draw(img).textlength(txt, font=serif(tam, True)) > 960:
            tam -= 4
        f = serif(tam, True)
    else:
        tam, cor = 88, OFFWHITE
        f = serif(tam)
    linhas = []
    for ln in txt.split("\n"):             # não cabe em 960 px → quebra em duas linhas equilibradas
        if not dest and ImageDraw.Draw(img).textlength(ln, font=f) > 960:
            ps = ln.split()
            k = min(range(1, len(ps)), key=lambda i: abs(len(" ".join(ps[:i])) - len(" ".join(ps[i:]))))
            linhas += [" ".join(ps[:k]), " ".join(ps[k:])]
        else:
            linhas.append(ln)
    lh = int(tam * 1.1)
    y0 = Y_CENTRO - (len(linhas) * lh) // 2 + subida
    sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ds, d = ImageDraw.Draw(sombra), ImageDraw.Draw(img)
    lmax = max(d.textlength(ln, font=f) for ln in linhas)
    ds.ellipse([540 - lmax * 0.72, y0 - lh * 0.8, 540 + lmax * 0.72, y0 + lh * (len(linhas) + 0.8)],
               fill=(12, 9, 6, int(80 * alpha)))       # penumbra: sem caixa
    for k, ln in enumerate(linhas):
        x, y = (1080 - d.textlength(ln, font=f)) / 2, y0 + k * lh
        ds.text((x, y + 4), ln, font=f, fill=(8, 6, 4, int(215 * alpha)))
        d.text((x, y), ln, font=f, fill=cor + (int(255 * alpha),))
    return Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(22)), img)


def legenda():
    pasta = os.path.join(WORK, "leg")
    os.makedirs(pasta, exist_ok=True)
    vazio = os.path.join(pasta, "vazio.png")
    Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
    seq, t = [], 0.0
    entrada = 5                                   # quadros de fade + subida (≈0,17 s)
    for i, (txt, a, b, dest) in enumerate(LINHAS):
        if a > t:
            seq.append((vazio, a - t))
        for k in range(entrada):                  # entra suave: alfa sobe e o texto sobe 14 px
            p = os.path.join(pasta, f"{i:03d}-{k}.png")
            e = (k + 1) / (entrada + 1)
            quadro(txt, dest, alpha=e, subida=int(14 * (1 - e) ** 2)).save(p)
            seq.append((p, 1 / FPS))
        p = os.path.join(pasta, f"{i:03d}.png")
        quadro(txt, dest).save(p)
        seq.append((p, max(0.05, (b - a) - entrada / FPS)))
        t = b
    seq.append((vazio, 0.5))
    lista = os.path.join(pasta, "lista.txt")
    with open(lista, "w", encoding="utf-8") as fh:
        for p, dur in seq:
            fh.write(f"file '{p}'\nduration {dur:.4f}\n".replace("\\", "/"))
        fh.write(f"file '{vazio}'\n".replace("\\", "/"))
    run(["-f", "concat", "-safe", "0", "-i", lista, "-vf", f"fps={FPS},format=rgba", "-c:v", "png",
         os.path.join(WORK, "legenda.mov")])


def compor():
    run(["-i", os.path.join(WORK, "imagem.mp4"), "-i", os.path.join(WORK, "legenda.mov"),
         "-i", os.path.join(AQUI, "voz.m4a"),
         "-filter_complex", "[0:v][1:v]overlay=format=auto,format=yuv420p[v];[2:a]loudnorm=I=-15:TP=-1.5[a]",
         "-map", "[v]", "-map", "[a]", "-shortest", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", SAIDA])
    print("saída:", SAIDA)


if __name__ == "__main__":
    cenas()
    legenda()
    compor()
