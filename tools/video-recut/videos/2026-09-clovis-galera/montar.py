"""Voz de fundo (Clóvis de Barros Filho, "a galera gosta") + takes do Vitor sem fala + legenda no meio.

Formato: ref. Carlos Lehmann (DcWj_iKyyIX, 92k ❤). v4 (2026-09-30) — pedido do Vitor: "faça algo
mais parecido com o dele, mas com o nosso toque, e tire o filtro escuro".
  - estrutura da ref: 1 take curto na abertura (sacada) + 1 take longo (mesa); imagem SEM filtro
  - tipografia da ref medida: serifada condensada (Instrument Serif), tracking apertado, entrelinha
    colada, frase em creme ~60% da largura, centro um pouco acima do meio; nomes em CAIXA-ALTA no
    mesmo corpo; "Foda-se" gigante
  - o nosso toque: dourado da marca no lugar do vermelho; entrada suave de cada frase
  - histórico: v1 Inter (recusada: "as letras dele ficaram melhores"), v3 Fraunces itálico (recusada:
    "ainda não tá legal como o dele")
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
FONTE = os.path.join(AQUI, "InstrumentSerif-Regular.ttf")   # Google Fonts, OFL
os.makedirs(WORK, exist_ok=True)

CREME = (243, 238, 222)
OURO = (226, 184, 88)       # dourado da marca, mais saturado para saltar sobre imagem sem filtro
FPS = 30

MESA = os.path.join(TAKES, "74C15A77-8FDB-4B26-AC84-FE7CB203E865.mp4")
SACADA = os.path.join(TAKES, "E3202855-2C0F-41A4-B3BA-DC5D1B9B1DDD.mp4")
ESTUDIO = os.path.join(TAKES, "C8D81249-B745-41EB-A3E8-86673BB24A85.mp4")

# (arquivo, início no arquivo, duração no arquivo, velocidade) — sem recorte, sem filtro
CENAS = [
    (SACADA, 0.0, 5.0, 0.887),     # abertura curta, como a ref
    (MESA, 0.0, 15.1, 1.0),        # mesa: de "Sócrates" até "Algoritmo"
    (ESTUDIO, 0.0, 6.8, 0.806),    # estúdio com o notebook (volta a pedido, 2026-09-30)
]
CORTES = [0.0, 5.64, 20.66, 29.1]  # trocas em "Sócrates" e "de uma vontade genérica"

# (texto, início, fim, estilo)   estilo: "frase" | "nome" (caixa-alta dourada) | "grito" (gigante dourado)
LINHAS = [
    ("A galera gosta,", 0.00, 0.88, "frase"),
    ("Foda-se", 0.88, 1.82, "grito"),
    ("Se o que a galera\ngosta fosse bom,", 1.82, 4.54, "frase"),
    ("não teríamos matado", 4.54, 5.64, "frase"),
    ("Sócrates", 5.64, 6.36, "nome"),
    ("não teríamos matado", 6.36, 7.24, "frase"),
    ("Jesus", 7.24, 7.98, "nome"),
    ("Gandhi", 7.98, 8.76, "nome"),
    ("Martin Luther King", 8.76, 10.40, "nome"),
    ("Todos os grandes foram\nmortos pela galera.", 10.40, 12.96, "frase"),
    ("Então, foda-se o que\na galera acha bom.", 12.96, 15.70, "frase"),
    ("Quem tem que achar\nbom sou eu.", 15.70, 17.36, "frase"),
    ("Quando você é escravo\nde um número,", 17.36, 19.66, "frase"),
    ("Algoritmo", 19.66, 20.66, "nome"),
    ("de uma vontade\ngenérica,", 20.66, 22.40, "frase"),
    ("nossa…", 22.40, 23.08, "frase"),
    ("ela sempre\nte surpreende", 23.08, 24.88, "frase"),
    ("e você fica\ndelirantemente", 24.88, 26.70, "frase"),
    ("à mercê do que dá certo\ne do que dá errado.", 26.70, 29.10, "frase"),
]

Y_CENTRO = 900       # um pouco acima do meio, como na ref (medido: ~46% da altura)


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


# ------------------------------------------------------------------ imagem (sem filtro)

def cenas():
    partes = []
    for i, (arq, ini, dur, vel) in enumerate(CENAS):
        alvo = CORTES[i + 1] - CORTES[i]
        out = os.path.join(WORK, f"cena{i}.mp4")
        vf = (f"scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,"
              f"setpts=PTS/{vel},fps={FPS},trim=0:{alvo:.3f},setpts=PTS-STARTPTS,format=yuv420p")
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

def largura(txt, f, trk):
    return f.getlength(txt) + trk * (len(txt) - 1)


def desenhar(d, x, y, txt, f, trk, cor, grosso=0):
    """Tracking apertado mantendo o kerning (cada letra na posição do prefixo já kernado).
    `grosso` engrossa o traço (a Instrument Serif só tem peso regular; a ref é mais encorpada)."""
    for i, ch in enumerate(txt):
        d.text((x + f.getlength(txt[:i]) + trk * i, y), ch, font=f, fill=cor,
               stroke_width=grosso, stroke_fill=cor)


def quadro(txt, estilo, alpha=1.0, subida=0):
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    if estilo == "grito":
        tam, trk, cor, lh_f, grosso = 360, -8, OURO, 1.0, 2
    elif estilo == "nome":
        txt, tam, trk, cor, lh_f, grosso = txt.upper(), 124, -3, OURO, 1.0, 1
    else:
        tam, trk, cor, lh_f, grosso = 122, -4, CREME, 0.92, 1
    f = ImageFont.truetype(FONTE, tam)
    while max(largura(ln, f, trk) for ln in txt.split("\n")) > 980:
        tam -= 4
        f = ImageFont.truetype(FONTE, tam)
    linhas = txt.split("\n")
    lh = int(tam * lh_f)
    y0 = Y_CENTRO - (len(linhas) * lh) // 2 - int(tam * 0.12) + subida
    # sem filtro na imagem: penumbra muito esfumada só atrás das letras segura o contraste.
    # Camada própria com desfoque grande (sem borda visível); centrada no desenho das letras,
    # que na Instrument Serif começa ~0,25·tam abaixo do y do texto.
    lmax = max(largura(ln, f, trk) for ln in linhas)
    cy = y0 + len(linhas) * lh / 2 + tam * 0.18
    meia_alt, meia_larg = len(linhas) * lh / 2 + tam * 0.3, lmax * 0.6
    pen = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(pen).ellipse([540 - meia_larg, cy - meia_alt, 540 + meia_larg, cy + meia_alt],
                                fill=(0, 0, 0, int(78 * alpha)))
    pen = pen.filter(ImageFilter.GaussianBlur(55))
    sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ds, d = ImageDraw.Draw(sombra), ImageDraw.Draw(img)
    for k, ln in enumerate(linhas):
        x, y = (1080 - largura(ln, f, trk)) / 2, y0 + k * lh
        desenhar(ds, x, y + 4, ln, f, trk, (0, 0, 0, int(200 * alpha)), grosso)
        desenhar(d, x, y, ln, f, trk, cor + (int(255 * alpha),), grosso)
    base = Image.alpha_composite(pen, sombra.filter(ImageFilter.GaussianBlur(10)))
    return Image.alpha_composite(base, img)


def legenda():
    pasta = os.path.join(WORK, "leg")
    os.makedirs(pasta, exist_ok=True)
    vazio = os.path.join(pasta, "vazio.png")
    Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
    seq, t = [], 0.0
    entrada = 4                                   # fade curto (≈0,13 s) + subida leve
    for i, (txt, a, b, estilo) in enumerate(LINHAS):
        if a > t:
            seq.append((vazio, a - t))
        for k in range(entrada):
            p = os.path.join(pasta, f"{i:03d}-{k}.png")
            e = (k + 1) / (entrada + 1)
            quadro(txt, estilo, alpha=e, subida=int(10 * (1 - e) ** 2)).save(p)
            seq.append((p, 1 / FPS))
        p = os.path.join(pasta, f"{i:03d}.png")
        quadro(txt, estilo).save(p)
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
