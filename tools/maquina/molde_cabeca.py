"""Molde "cabeça" (18/10, referência do Vitor: GaryVee, instagram.com/p/DeZgaGaAP0F).

Fundo preto, cabeça de perfil em linhas brancas (arte própria, Nano Banana via Kie), o vídeo dele recortado
dentro do crânio e a legenda branca em Inter 800, de 1 a 2 palavras, no meio do vídeo. As linhas ficam por cima
do vídeo (blend lighten: o preto da arte não apaga nada, só as linhas aparecem).

uso:  python tools/maquina/molde_cabeca.py <video-limpo.mp4> <palavras.json> <saida.mp4> [rosto_y]
      rosto_y = altura do centro do rosto no vídeo 1080×1920 (padrão 1050)
"""
import json, os, shutil, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(RAIZ, "tools", "video-recut", "assets")
ARTE = os.path.join(ASSETS, "cabeca", "cabeca-v3.png")
INTER = os.path.join(ASSETS, "fontes", "Inter-800.ttf")
CX, CY, RX, RY = 490, 650, 370, 280      # janela dentro do crânio (coordenadas do quadro 1080×1920)
Y_LEG = 760                              # legenda na metade de baixo da janela, como na referência


def run(a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)


def preparar(work):
    arte = Image.open(ARTE).convert("RGB").resize((1080, 1890), Image.LANCZOS)
    fundo = Image.new("RGB", (1080, 1920)); fundo.paste(arte, (0, 15)); fundo.save(os.path.join(work, "arte.png"))
    m = Image.new("L", (1080, 1920))
    ImageDraw.Draw(m).ellipse((CX - RX, CY - RY, CX + RX, CY + RY), fill=255)
    m.filter(ImageFilter.GaussianBlur(28)).save(os.path.join(work, "mascara.png"))


def grupos(ws):
    """1 a 2 palavras por vez; quebra no ponto final e quando passa de 14 letras."""
    out = []
    for p in ws:
        w, a = p["word"].strip(), p["start"]
        if not w:
            continue
        if out and len(out[-1][0]) + len(w) < 14 and out[-1][0][-1:] not in ".?!," and " " not in out[-1][0]:
            out[-1][0] += " " + w
        else:
            out.append([w, a])
    return out


def legenda(ws, dur, work):
    fonte = ImageFont.truetype(INTER, 76)
    pasta = os.path.join(work, "leg"); os.makedirs(pasta)
    vazio = os.path.join(pasta, "vazio.png"); Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
    gs, linhas, t = grupos(ws), [], 0.0
    for i, (txt, a) in enumerate(gs):
        a = max(a, t)
        b = gs[i + 1][1] if i + 1 < len(gs) else min(dur, a + 1.0)
        if a > t:
            linhas.append((vazio, a - t))
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        x = (1080 - ImageDraw.Draw(img).textlength(txt, font=fonte)) / 2
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((x, Y_LEG + 3), txt, font=fonte, fill=(0, 0, 0, 200))
        img = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), img)
        ImageDraw.Draw(img).text((x, Y_LEG), txt, font=fonte, fill="white")
        q = os.path.join(pasta, f"{i:03d}.png"); img.save(q)
        linhas.append((q, max(b - a, 0.05))); t = b
    linhas.append((vazio, max(dur - t, 0) + 0.5))
    lista = os.path.join(pasta, "lista.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for q, d in linhas:
            f.write(f"file '{q}'\nduration {d:.3f}\n")
        f.write(f"file '{vazio}'\n")
    mov = os.path.join(work, "legenda.mov")
    run(["-f", "concat", "-safe", "0", "-i", lista, "-vf", "fps=30,format=rgba", "-c:v", "qtrle", mov])
    return mov


def montar(video, palavras, saida, rosto_y=1050):
    work = tempfile.mkdtemp(prefix="cabeca-")
    try:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                                   capture_output=True, text=True).stdout)
        preparar(work)
        mov = legenda(json.load(open(palavras, encoding="utf-8")), dur, work)
        jw, jh = 2 * RX + 40, 2 * RY + 40                     # o vídeo cobre a janela com folga para a borda suave
        ch = int(1080 * jh / jw) // 2 * 2
        y0 = max(0, min(1920 - ch, rosto_y - ch // 2))
        fc = (f"[0:v]scale=1080:1920,crop=1080:{ch}:0:{y0},scale={jw}:{jh},setsar=1,format=rgba[v];"
              f"[2:v]format=gray[m];[v]pad=1080:1920:{CX - jw // 2}:{CY - jh // 2}:black@0,format=rgba[vp];"
              f"[vp][m]alphamerge[vm];[1:v]format=rgba[arte];[arte][vm]overlay=0:0:format=auto[base];"
              f"[1:v]format=gbrp[lin];[base]format=gbrp[b2];[b2][lin]blend=all_mode=lighten,format=rgba[cab];"
              f"[cab][3:v]overlay=0:0:eof_action=pass,format=yuv420p[out]")
        run(["-i", video, "-loop", "1", "-i", os.path.join(work, "arte.png"), "-loop", "1", "-i", os.path.join(work, "mascara.png"),
             "-i", mov, "-filter_complex", fc, "-map", "[out]", "-map", "0:a", "-t", f"{dur:.3f}", "-r", "30",
             "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", saida])
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 3:
        sys.exit(__doc__)
    montar(a[0], a[1], a[2], int(a[3]) if len(a) > 3 else 1050)
    print("ok", a[2])
