"""Voz de fundo (Clóvis de Barros Filho) + takes do Vitor sem fala + legenda serifada no meio.

Molde: ref Carlos Lehmann (DcWj_iKyyIX, 92k ❤) — clima de cinema (escuro, frio, dessaturado),
legenda serifada fina no centro, palavras-chave grandes em vermelho.
Áudio: o mesmo da ref Carlos Lehmann (Clóvis, "a galera gosta, foda-se"). Crédito na legenda do post.
RASCUNHO com os 2 takes existentes — trocar CENAS quando o Vitor mandar os takes novos.

uso:  python montar.py            (gera Downloads/2026-09-clovis-galera.mp4)
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(AQUI, "..", "..", "work", "2026-09-clovis-galera")
TAKES = os.path.join(AQUI, "..", "..", "work", "2026-09-plano-vs-prova")
DOWN = os.path.join(os.environ["USERPROFILE"], "Downloads")
SAIDA = os.path.join(DOWN, "2026-09-clovis-galera.mp4")
FONTE = os.path.join(AQUI, "InstrumentSerif-Regular.ttf")
os.makedirs(WORK, exist_ok=True)

# tratamento de cinema: escuro, frio, dessaturado, vinheta e grão leve
COR = ("curves=all='0/0 0.3/0.2 0.7/0.6 1/0.88',eq=saturation=0.62:contrast=1.08,"
       "colorbalance=bs=0.06:bm=0.03:rs=-0.03,vignette=PI/4.2,noise=alls=5:allf=t")

# (arquivo, início no arquivo, duração no arquivo, velocidade, centro_x 0-1, recorte extra antes do 9:16)
CENAS = [
    (os.path.join(TAKES, "IMG_6248.mov"), 0.0, 5.3, 0.94, 0.42, "eq=brightness=0.07:gamma=1.55,"),
    (os.path.join(TAKES, "CA3DDFFD-C035-4C4C-9C54-402A4C50D1A2.mov"), 0.0, 7.3, 1.0, 0.55, ""),
    (os.path.join(TAKES, "CA3DDFFD-C035-4C4C-9C54-402A4C50D1A2.mov"), 2.0, 5.0, 0.65, 0.5, "crop=1080:1920:236:1890,"),
    (os.path.join(TAKES, "IMG_6248.mov"), 0.0, 5.3, 0.63, 0.42, "eq=brightness=0.07:gamma=1.55,"),
]
CORTES = [0.0, 5.64, 12.96, 20.66, 29.1]

# (texto, início, fim, destaque)  — destaque = palavra grande em vermelho
LINHAS = [
    ("A galera gosta,", 0.00, 0.88, False),
    ("FODA-SE", 0.88, 1.82, True),
    ("Se o que a galera\ngosta fosse bom,", 1.82, 4.54, False),
    ("não teríamos matado", 4.54, 5.64, False),
    ("SÓCRATES", 5.64, 6.36, True),
    ("não teríamos matado", 6.36, 7.24, False),
    ("JESUS", 7.24, 7.98, True),
    ("GANDHI", 7.98, 8.76, True),
    ("MARTIN LUTHER KING", 8.76, 10.40, True),
    ("Todos os grandes foram\nmortos pela galera.", 10.40, 12.96, False),
    ("Então, foda-se o que\na galera acha bom.", 12.96, 15.70, False),
    ("Quem tem que achar\nbom sou eu.", 15.70, 17.36, False),
    ("Quando você é escravo\nde um número,", 17.36, 19.66, False),
    ("ALGORITMO", 19.66, 20.66, True),
    ("de uma vontade genérica,", 20.66, 22.40, False),
    ("nossa...", 22.40, 23.08, False),
    ("ela sempre te surpreende", 23.08, 24.88, False),
    ("e você fica delirantemente", 24.88, 26.70, False),
    ("à mercê do que dá certo\ne do que dá errado.", 26.70, 29.10, False),
]


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def cenas():
    partes = []
    for i, (arq, ini, dur, vel, cx, extra) in enumerate(CENAS):
        alvo = CORTES[i + 1] - CORTES[i]
        out = os.path.join(WORK, f"cena{i}.mp4")
        # 9:16 com o centro escolhido; câmera lenta por setpts
        vf = (f"{extra}scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
              f"crop=1080:1920:'max(0,min(iw-1080,iw*{cx}-540))':0,setsar=1,"
              f"setpts=PTS/{vel},fps=30,{COR},trim=0:{alt(alvo)},setpts=PTS-STARTPTS,format=yuv420p")
        run(["-ss", str(ini), "-t", str(dur), "-i", arq, "-an", "-vf", vf,
             "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-g", "30", out])
        partes.append(out)
    lista = os.path.join(WORK, "cenas.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for p in partes:
            f.write(f"file '{p}'\n".replace("\\", "/"))
    run(["-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", os.path.join(WORK, "imagem.mp4")])
    for p in partes:          # disco apertado: as cenas soltas não servem mais
        os.remove(p)


def alt(x):
    return f"{x:.3f}"


def legenda():
    pasta = os.path.join(WORK, "leg")
    os.makedirs(pasta, exist_ok=True)
    vazio = os.path.join(pasta, "vazio.png")
    Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
    seq, t = [], 0.0
    for i, (txt, a, b, dest) in enumerate(LINHAS):
        if a > t:
            seq.append((vazio, a - t))
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        tam = 180 if dest else 96
        f = ImageFont.truetype(FONTE, tam)
        while dest and ImageDraw.Draw(img).textlength(txt, font=f) > 1000:
            tam -= 6
            f = ImageFont.truetype(FONTE, tam)
        cor = (214, 30, 30, 255) if dest else (246, 242, 236, 255)
        linhas = txt.split("\n")
        lh = int(tam * 1.02)
        y0 = 940 - (len(linhas) * lh) // 2
        sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ds, d = ImageDraw.Draw(sombra), ImageDraw.Draw(img)
        for k, ln in enumerate(linhas):
            w = d.textlength(ln, font=f)
            x, y = (1080 - w) / 2, y0 + k * lh
            ds.text((x, y + 4), ln, font=f, fill=(0, 0, 0, 200))
            d.text((x, y), ln, font=f, fill=cor)
        img = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(8)), img)
        p = os.path.join(pasta, f"{i:03d}.png")
        img.save(p)
        seq.append((p, b - a))
        t = b
    seq.append((vazio, 0.5))
    lista = os.path.join(pasta, "lista.txt")
    with open(lista, "w", encoding="utf-8") as fh:
        for p, dur in seq:
            fh.write(f"file '{p}'\nduration {dur:.3f}\n".replace("\\", "/"))
        fh.write(f"file '{vazio}'\n".replace("\\", "/"))
    run(["-f", "concat", "-safe", "0", "-i", lista, "-vf", "fps=30,format=rgba", "-c:v", "png",
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
