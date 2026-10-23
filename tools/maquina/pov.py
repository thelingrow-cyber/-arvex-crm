"""Vídeo de 8 s sem fala: um take + uma frase na tela (formato "POV", modelo do Fabiano às 9h e 15h).

  python tools/maquina/pov.py <take.mp4> "<frase>" <saida.mp4> [--inicio 0] [--dur 8] [--topo 230]

- O take vira 1080x1920. Se for mais curto que --dur, é desacelerado até caber (nunca abaixo de 0,6x).
- A frase fica no terço de cima, fora da área dos botões do Instagram, em branco com contorno preto
  (a cara de texto nativo do app). Parada o vídeo inteiro: nada de animação (cartões animados reprovados).
- Sem áudio de terceiros: sai com faixa muda. O som do momento, se quiser, entra no app.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

FONTE = os.path.join(os.path.dirname(__file__), "..", "video-recut", "assets", "fontes", "Inter-800.ttf")
W, H = 1080, 1920
TOPO = 230            # logo abaixo da barra de cima do Reels; --topo muda por take (não cobrir o rosto)
LARG = 900
TAM = 62


def _quebrar(draw, texto, fonte):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if draw.textlength(teste, font=fonte) <= LARG:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    linhas.append(atual)
    return linhas


def placa(texto, caminho, topo=None):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONTE, TAM)
    y = topo or TOPO
    for bloco in texto.split("\n"):           # \n na frase = quebra forçada
        for linha in _quebrar(d, bloco, f):
            x = (W - d.textlength(linha, font=f)) / 2
            d.text((x, y), linha, font=f, fill="white", stroke_width=6, stroke_fill="black")
            y += int(TAM * 1.22)
        y += int(TAM * 0.35)
    img.save(caminho)


def duracao(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def montar(take, frase, saida, inicio=0.0, dur=8.0, topo=None):
    resto = duracao(take) - inicio
    lento = max(min(resto / dur, 1.0), 0.6)    # <1 = desacelera o take curto
    trecho = min(resto, dur * lento)
    png = os.path.join(tempfile.mkdtemp(), "frase.png")
    placa(frase, png, topo)
    os.makedirs(os.path.dirname(os.path.abspath(saida)), exist_ok=True)
    filtro = (f"[0:v]setpts=PTS/{lento:.4f},scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H},fps=30,format=yuv420p[v];[v][1:v]overlay=0:0[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(inicio), "-t", f"{trecho:.3f}", "-i", take,
                    "-i", png, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-filter_complex", filtro, "-map", "[out]", "-map", "2:a", "-t", f"{trecho / lento:.3f}",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", saida], check=True)
    return saida


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 3:
        sys.exit(__doc__)
    ini = float(a[a.index("--inicio") + 1]) if "--inicio" in a else 0.0
    du = float(a[a.index("--dur") + 1]) if "--dur" in a else 8.0
    tp = int(a[a.index("--topo") + 1]) if "--topo" in a else None
    print(montar(a[0], a[1].replace("\\n", "\n"), a[2], ini, du, tp))
