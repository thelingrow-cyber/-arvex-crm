# Amigo do carro (29/10) — Nova Hilux 2027 "já nasceu velha?". Referência: post DdXN8QFCS1C (Ronan).
# Molde da casa (igual Tank 400 / Denza): clipes do carro em cima, ele embaixo, headline em caixa vermelha no início.
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont
W = "C:/Users/Vitor Simões/Desktop/ARVEX/tools/video-recut/work/2026-10-29-amigo-carro"
C = f"{W}/clipes"
FONTE = "C:/Users/Vitor Simões/Desktop/ARVEX/tools/video-recut/assets/fontes/Montserrat.ttf"
B = "C:/Users/Vitor Simões/Downloads/2026-10-29-amigo-carro-limpo.mp4"
SAIDA = sys.argv[1] if len(sys.argv) > 1 else f"{W}/final.mp4"
# NZ = Toyota NZ (prata, limpo) · IN = Toyota India (laranja, cinema) · TH = trailer YOUCAR (tem texto tailandês: só trechos sem texto)
# OFF = off-road branco sem fala · RANGER / AMAROK / S10 = comerciais oficiais
NZ, IN, TH, OFF = (f"{C}/{x}.mp4" for x in ["RF3pBf48XmI", "xmPx0KzlO2o", "0BlPS65WN5Q", "4zGQARlfb_E"])
RANGER, AMAROK, S10 = (f"{C}/{x}.mp4" for x in ["DWWxYWO0S9A", "xCIOivkJxgA", "58b4bTxJatU"])
TOP, BOT = 1000, 920
# zoom leve (1060 de altura) tira o texto legal "Filmed under controlled conditions" do rodapé dos oficiais
# (arquivo, início no clipe, até quando no vídeo final) — segue a fala dele
seq = [(NZ, 0.0, 2.9),                       # nova Hilux já nasceu velha?
       (IN, 18.8, 5.0), (NZ, 12.0, 6.8),     # vindo totalmente diferente
       (NZ, 54.0, 8.3),                      # muita tecnologia
       (NZ, 9.0, 10.8), (NZ, 56.0, 12.8),    # interior totalmente reformado
       (NZ, 20.0, 16.4),                     # diferente do modelo anterior
       (OFF, 32.0, 20.1),                    # eu falo velha é porque... mantendo
       (OFF, 160.0, 23.0), (OFF, 104.0, 26.3),  # chassi IMV, usa há muitos anos
       (OFF, 80.0, 29.0),                    # durabilidade
       (NZ, 3.0, 30.6), (IN, 24.0, 31.9),    # confiança de ser Toyota
       (TH, 63.0, 34.5), (IN, 33.0, 37.5),   # eletrificação, chega em 2027
       (TH, 66.0, 39.9), (NZ, 45.0, 42.0),   # elétrico / híbrido
       (NZ, 69.0, 44.4),                     # e aí, o que você acha? o pesadelo da
       (RANGER, 9.0, 45.5), (AMAROK, 72.5, 46.4), (S10, 42.0, 48.2),
       (OFF, 16.0, 52.3),                    # mudar totalmente a estrutura
       (NZ, 87.0, 54.0),                     # a identidade da Hilux?
       (NZ, 66.0, 60.0)]                     # deixa nos comentários (corta no fim da fala)

def fonte(px):
    f = ImageFont.truetype(FONTE, px); f.set_variation_by_name("Black"); return f
im = Image.new("RGBA", (1080, TOP), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = fonte(58)
linhas = ["A NOVA HILUX 2027", "JÁ NASCEU VELHA?"]
lw = max(d.textlength(l, font=f) for l in linhas); h = 30 + 72 * len(linhas)
x0, y0 = (1080 - lw) / 2 - 30, TOP - h - 40
d.rectangle((x0, y0, x0 + lw + 60, y0 + h), fill=(200, 16, 30))
for i, l in enumerate(linhas):
    d.text(((1080 - d.textlength(l, font=f)) / 2, y0 + 14 + i * 72), l, font=f, fill=(255, 255, 255))
im.save(f"{W}/titulo.png")

ins, fc, t = [], [], 0.0
for i, (arq, ss, fim) in enumerate(seq):
    du = round(fim - t, 3); t = fim
    ins += ["-ss", str(ss), "-t", str(du + 0.1), "-i", arq]
    fc.append(f"[{i}:v]scale=-2:1060,crop=1080:{TOP}:(iw-1080)/2:20,setsar=1,fps=30,trim=duration={du},setpts=PTS-STARTPTS[s{i}]")
n = len(seq)
fc.append("".join(f"[s{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[top0]")
ins += ["-loop", "1", "-framerate", "30", "-t", "4.2", "-i", f"{W}/titulo.png", "-i", B]
fc.append(f"[{n}:v]format=rgba,fade=t=out:st=3.9:d=0.3:alpha=1[tit];[top0][tit]overlay=0:0:eof_action=pass[top]")
# bruto é HDR do iPhone (HLG/bt2020): converter para SDR, senão o rosto fica estourado/branco
TM = ("zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
      "tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
fc.append(f"[{n+1}:v]{TM},scale=1080:1920,crop=1080:{BOT}:0:740,setsar=1,fps=30[bot]")
fc.append("[top][bot]vstack=2[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{n+1}:a",
    "-c:v", "libx264", "-threads", "4", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
    "-movflags", "+faststart", "-shortest", SAIDA], check=True)
