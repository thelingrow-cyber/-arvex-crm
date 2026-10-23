"""Vídeo de 8 s sem fala: um take + uma frase na tela (formato "POV", modelo do Fabiano às 9h e 15h).

  python tools/maquina/pov.py <take.mp4> "<frase>" <saida.mp4> [--inicio 0] [--dur 8] [--topo 300]

- O take vira 1080x1920. Se for mais curto que --dur, é desacelerado até caber (nunca abaixo de 0,6x).
- A frase fica no terço de cima, fora da área dos botões do Instagram, em branco
  com sombra suave (como o texto do Fabiano). Parada o vídeo inteiro: nada de animação (cartões animados reprovados).
- A imagem é escurecida de leve (menos brilho e saturação, bordas mais escuras), como na referência:
  é isso que faz o texto branco pequeno ler sem contorno.
- Sem áudio de terceiros: sai com faixa muda. O som do momento, se quiser, entra no app.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTE = os.path.join(os.path.dirname(__file__), "..", "video-recut", "assets", "fontes", "Poppins-SemiBold.ttf")
# referência Fabiano (DeZ1KZCiPDR, ampliado quadro a quadro): Poppins SemiBold bate letra por letra
W, H = 1080, 1920
TOPO = 300            # logo abaixo da barra de cima do Reels; --topo muda por take (não cobrir o rosto)
LARG = 980
TAM = 42            # medido no DeZ1KZCiPDR: 46 = mesma largura do dele; 40 compensa take fechado


ESPACO = 0.035        # espaço extra entre letras (em fração do tamanho), medido no dele


def _largura(draw, texto, fonte):
    return draw.textlength(texto, font=fonte) + ESPACO * TAM * (len(texto) - 1)


def _escrever(draw, x, y, texto, fonte):
    for c in texto:
        draw.text((x, y), c, font=fonte, fill=255)
        x += draw.textlength(c, font=fonte) + ESPACO * TAM


def _quebrar(draw, texto, fonte):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if _largura(draw, teste, fonte) <= LARG:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    linhas.append(atual)
    return linhas


def placa(texto, caminho, topo=None):
    f = ImageFont.truetype(FONTE, TAM)
    letras = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(letras)
    y = topo or TOPO
    for bloco in texto.split("\n"):           # \n na frase = quebra forçada
        for linha in _quebrar(d, bloco, f):
            _escrever(d, (W - _largura(d, linha, f)) / 2, y, linha, f)
            y += int(TAM * 1.15)   # entrelinha medido no dele
    sombra = letras.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(5))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    borda = letras.filter(ImageFilter.MaxFilter(5))   # contorno fino escuro colado na letra, como no dele
    img.paste((0, 0, 0, 255), (2, 3), sombra.point(lambda v: int(v * 0.85)))
    img.paste((20, 20, 20, 255), (0, 0), borda.point(lambda v: int(v * 0.8)))
    img.paste((255, 255, 255, 255), (0, 0), letras)
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
              f"crop={W}:{H},fps=30,eq=brightness=-0.04:contrast=1.06:saturation=0.85:gamma=0.96,"
              f"vignette=PI/6,format=yuv420p[v];[v][1:v]overlay=0:0[out]")
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
