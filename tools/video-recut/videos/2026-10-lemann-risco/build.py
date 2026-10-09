"""Lemann — "o maior risco é não arriscar". Molde do Henrique Bagetti (ref Db9Oh47AI51).

A (tela dividida): Lemann em cima falando, Vitor embaixo escutando; gancho em texto, sem fala de abertura.
B (tela cheia): o fecho do Vitor com legenda fina; "Foi ele." em destaque no final.
Sem música (o Vitor põe no app). Saída: Downloads\\2026-10-lemann-risco.mp4

uso: python -I build.py
"""
import json, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(AQUI, "tmp")
os.makedirs(TMP, exist_ok=True)
SAIDA = os.path.join(os.path.expanduser("~"), "Downloads", "2026-10-lemann-risco.mp4")
FONTE = r"C:\Windows\Fonts\seguisb.ttf"
FONTE_FORTE = r"C:\Windows\Fonts\seguibl.ttf"
COR = "curves=all='0/0 0.5/0.47 1/0.92'"  # padrão aprovado: realces descendo
W, H, MEIO = 1080, 1920, 960

# Lemann (gravação de tela, legenda dele já queimada no vídeo): dois trechos colados
LEMANN = [(0.0, 7.0), (31.5, 39.95)]
DUR_A = sum(b - a for a, b in LEMANN)
SOME = 37.9               # tela.mov: a imagem começa a escurecer em 38,0s (fade da gravação)
INTRO = (1.72, 3.95)      # take do Vitor: "um dos maiores empresários do país, falou" (o nome saiu errado e foi cortado)
ESCUTA_INI = 4.0          # take do Vitor: silêncio de 3,4 a 23,6s = ele escutando
FECHO = (23.45, 42.17)    # take do Vitor: "Um cara que podia…" até "foi ele."
GANCHO = "O maior risco de\nqualquer negócio"


def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def png_texto(caminho, texto, tamanho, fonte=FONTE, cor=(255, 255, 255, 255), largura=W, altura=260):
    img = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    f = ImageFont.truetype(fonte, tamanho)
    d = ImageDraw.Draw(img)
    caixa = d.multiline_textbbox((0, 0), texto, font=f, align="center", spacing=8)
    x = (largura - (caixa[2] - caixa[0])) / 2 - caixa[0]
    y = (altura - (caixa[3] - caixa[1])) / 2 - caixa[1]
    sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).multiline_text((x + 3, y + 4), texto, font=f, fill=(0, 0, 0, 200), align="center", spacing=8)
    img = Image.alpha_composite(img, sombra.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(img).multiline_text((x, y), texto, font=f, fill=cor, align="center", spacing=8)
    img.save(caminho)


def costura(caminho, faixa=280):
    """Faixa escura sem linha no meio: os dois vídeos escurecem e se fundem (curva cosseno)."""
    import math
    img = Image.new("RGBA", (W, faixa))
    px = img.load()
    for y in range(faixa):
        a = int(255 * 0.9 * (0.5 - 0.5 * math.cos(2 * math.pi * y / faixa)))
        for x in range(W):
            px[x, y] = (0, 0, 0, a)
    img.save(caminho)


def blocos_legenda():
    """Até 3 palavras por bloco, quebrando na pontuação. Tempos já relativos ao início do fecho."""
    w = json.load(open(os.path.join(AQUI, "take-vitor-words.json"), encoding="utf-8"))["words"]
    w = [x for x in w if FECHO[0] - 0.2 <= x["start"] < FECHO[1]]
    blocos, atual = [], []
    for x in w:
        atual.append(x)
        if len(atual) == 3 or x["word"].rstrip().endswith((",", ".", "?", "!")):
            blocos.append(atual)
            atual = []
    if atual:
        blocos.append(atual)
    saida = []
    for i, b in enumerate(blocos):
        ini = max(b[0]["start"] - FECHO[0], 0)
        fim = (blocos[i + 1][0]["start"] - FECHO[0]) if i + 1 < len(blocos) else FECHO[1] - FECHO[0]
        texto = " ".join(x["word"].strip() for x in b)
        saida.append((ini, fim, texto))
    return saida


def main():
    # --- A: tela dividida -------------------------------------------------
    partes = []
    for i, (a, b) in enumerate(LEMANN):
        p = os.path.join(TMP, f"lemann{i}.mp4")
        # a gravação escurece sozinha a partir de 38,0s: congela o último quadro bom (37,9s) até o fim da fala
        congela = f",trim=0:{SOME - a:.2f},tpad=stop_mode=clone:stop_duration={b - SOME + 0.1:.2f}" if b > SOME else ""
        ff("-ss", str(a), "-i", os.path.join(AQUI, "tela.mov"), "-t", str(b - a),
           "-vf", f"fps=30,scale=1080:-2,crop=1080:960:0:96,setsar=1{congela}",
           "-af", "aresample=48000", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", p)
        partes.append(p)
    lista = os.path.join(TMP, "lemann.txt")
    open(lista, "w", encoding="utf-8").write("".join(f"file '{p}'\n" for p in partes))
    topo = os.path.join(TMP, "lemann-topo.mp4")
    ff("-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", topo)

    png_texto(os.path.join(TMP, "gancho.png"), GANCHO, 76, fonte=FONTE_FORTE, altura=300)
    costura(os.path.join(TMP, "costura.png"))

    # --- I: abertura — Lemann parado em cima, Vitor falando embaixo --------
    parado = os.path.join(TMP, "lemann-parado.png")
    ff("-ss", "0.05", "-i", os.path.join(AQUI, "tela.mov"), "-frames:v", "1",
       "-vf", "scale=1080:-2,crop=1080:960:0:96,setsar=1", parado)
    dur_i = INTRO[1] - INTRO[0]
    seg_i = os.path.join(TMP, "I.mp4")
    ff("-loop", "1", "-i", parado, "-ss", str(INTRO[0]), "-t", f"{dur_i:.2f}", "-i", os.path.join(AQUI, "take-vitor.mp4"),
       "-loop", "1", "-i", os.path.join(TMP, "costura.png"), "-loop", "1", "-i", os.path.join(TMP, "gancho.png"),
       "-filter_complex",
       f"[0:v]fps=30,setsar=1[topo];[1:v]fps=30,crop=1080:960:0:520,{COR},setsar=1[baixo];"
       f"[topo][baixo]vstack=inputs=2:shortest=1[pilha];"
       f"[pilha][2:v]overlay=0:{MEIO - 140}:shortest=1[c];"
       f"[c][3:v]overlay=0:{MEIO - 150 - 300}:shortest=1[v];"
       f"[1:a]afade=t=in:d=0.05,loudnorm=I=-16:TP=-1.5,aresample=48000[a]",
       "-map", "[v]", "-map", "[a]", "-t", f"{dur_i:.2f}", "-r", "30",
       "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", seg_i)

    seg_a = os.path.join(TMP, "A.mp4")
    ff("-i", topo, "-ss", str(ESCUTA_INI), "-t", f"{DUR_A:.2f}", "-i", os.path.join(AQUI, "take-vitor.mp4"),
       "-loop", "1", "-i", os.path.join(TMP, "costura.png"), "-loop", "1", "-i", os.path.join(TMP, "gancho.png"),
       "-filter_complex",
       f"[1:v]fps=30,crop=1080:960:0:520,{COR},setsar=1[baixo];"
       f"[0:v][baixo]vstack=inputs=2[pilha];"
       f"[pilha][2:v]overlay=0:{MEIO - 140}:shortest=1[c];"
       f"[c][3:v]overlay=0:{MEIO - 150 - 300}:enable='between(t,0,2.5)':shortest=1[v];"
       f"[0:a]loudnorm=I=-16:TP=-1.5,aresample=48000[a]",
       "-map", "[v]", "-map", "[a]", "-t", f"{DUR_A:.2f}", "-r", "30",
       "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", seg_a)

    # --- B: fecho em tela cheia, legenda fina -----------------------------
    blocos = blocos_legenda()
    entradas, filtros, ant = [], [], "[0:v]fps=30," + COR + ",setsar=1[b0]"
    filtros.append(ant)
    rot = "b0"
    for i, (ini, fim, texto) in enumerate(blocos):
        final = texto.lower().startswith("foi ele")
        p = os.path.join(TMP, f"leg{i:02d}.png")
        if final:
            png_texto(p, texto.upper(), 110, fonte=FONTE_FORTE, cor=(255, 214, 10, 255), altura=300)
        else:
            png_texto(p, texto, 68)
        entradas += ["-loop", "1", "-i", p]
        y = 1340 if final else 1340 + 0
        filtros.append(f"[{rot}][{i + 1}:v]overlay=0:{y}:enable='between(t,{ini:.2f},{fim:.2f})':shortest=1[b{i + 1}]")
        rot = f"b{i + 1}"
    seg_b = os.path.join(TMP, "B.mp4")
    ff("-ss", str(FECHO[0]), "-t", f"{FECHO[1] - FECHO[0]:.2f}", "-i", os.path.join(AQUI, "take-vitor.mp4"), *entradas,
       "-filter_complex", ";".join(filtros) + f";[0:a]loudnorm=I=-16:TP=-1.5,aresample=48000[a]",
       "-map", f"[{rot}]", "-map", "[a]", "-t", f"{FECHO[1] - FECHO[0]:.2f}", "-r", "30",
       "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", seg_b)

    # --- junta ------------------------------------------------------------
    ff("-i", seg_i, "-i", seg_a, "-i", seg_b, "-filter_complex",
       "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]",
       "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", SAIDA)
    print("ok:", SAIDA, f"A={DUR_A:.2f}s B={FECHO[1] - FECHO[0]:.2f}s", "blocos de legenda:", len(blocos))


if __name__ == "__main__":
    main()
