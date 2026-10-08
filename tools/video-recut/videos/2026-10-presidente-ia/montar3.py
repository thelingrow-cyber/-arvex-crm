"""Se eu fosse presidente — v3 (sóbria). Feedback do Vitor na v2: "animado demais, infantil".

- Sai: pódio, carimbos, bonecos/avião, calendários, cofre, roleta 3º×35º, fecho "SÓ CLIENTE", balão de comentário.
- Entra: fotografia editorial (Kie.ai, Nano Banana) + selo discreto com o dado e a fonte.
- Fica (aprovado): Vale do Silício (tela cheia), chip, usina solar (tela cheia), data center — reusa os m2-*.
- Inserções de baixo 28% menores e mais baixas (não cobrem boca/queixo); entram só com fade.
- Título do topo: titulo.png (igual à v2).

uso: python montar3.py [fotos compor]
"""
import os, shutil, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar2 as M2
from montar2 import F, BLACK, SEMI, BRANCO, AMARELO, CINZA, FUNDO, LW, LH, w, run, cobrir, abrir, ease, emoldurar, DUR, ORIG

SAIDA = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "2026-10-presidente-ia-v3.mp4")
ESC = 0.72          # tamanho das inserções de baixo
LOW_Y = 1470        # centro vertical (abaixo do queixo)


def foto(arquivo, dur, selo=None, fonte=None, fx=0.5, fy=0.5):
    def fn(t):
        c = cobrir(abrir(arquivo), LW, LH, 1.03 + 0.05 * t / max(dur, 0.1), fx, fy)
        if selo:
            d = ImageDraw.Draw(c)
            fz = F(BLACK, 38)
            larg = d.textlength(selo, font=fz)
            alt = 62 + (34 if fonte else 0)
            d.rounded_rectangle([28, LH - 28 - alt, 28 + max(larg, d.textlength(fonte or "", font=F(SEMI, 24))) + 44, LH - 28], 14, fill=FUNDO + (215,))
            d.text((50, LH - 28 - alt + 8), selo, font=fz, fill=BRANCO)
            if fonte:
                d.text((50, LH - 28 - 38), fonte, font=F(SEMI, 24), fill=(185, 190, 200))
        return c
    return fn


# (nome, inicio, fim, fonte_do_video) — fonte: ("novo", fn) | ("m2", arquivo) | ("full", arquivo)
TL = [
    ("abertura", 0.00, 6.25, ("novo", foto("010450-p3-abertura.png", 6.25, None, None, 0.35, 0.5))),
    ("chatgpt", 6.30, 12.45, ("novo", foto("010527-p3-chatgpt.jpg", 6.15, "3º país que mais usa o ChatGPT", "Fonte: OpenAI, ago/2025"))),
    ("lab", 12.55, 19.35, ("novo", foto("010435-p3-lab.png", 6.8, "35º no ranking de quem cria IA", "Fonte: Global AI Index (Tortoise), 2023"))),
    ("aeroporto", 23.30, 30.90, ("novo", foto("010501-p3-aeroporto.png", 7.6, "70% não pensam em voltar", "Fonte: Revista Pesquisa FAPESP, mai/2026", 0.62))),
    ("engenheiros", 31.00, 37.60, ("novo", foto("010606-p3-engenheiros.jpg", 6.6, "Dia 1 · imposto de renda zero por 10 anos"))),
    ("investidores", 41.70, 48.40, ("novo", foto("010606-p3-investidores.jpg", 6.7, "Mês 1 · dinheiro pra quem fabrica"))),
    ("e1979", 48.95, 58.25, ("novo", foto("010606-p3-1979.jpg", 9.3, "EUA · 1979", "Fundos de aposentadoria liberados para empresas novas"))),
    ("vale", 58.30, 63.95, ("full", "m2-vale.mp4")),
    ("dcint", 68.10, 70.85, ("novo", foto("010555-p3-datacenter-int.png", 2.75, "Ano 1 · a máquina"))),
    ("chip", 70.90, 75.55, ("m2", "m2-chip.mov")),
    ("solar", 78.90, 82.95, ("full", "m2-solar.mp4")),
    ("dc", 86.70, 92.95, ("m2", "m2-dc.mov")),
]


def fotos():
    for nome, e, s, (tipo, src) in TL:
        if tipo != "novo":
            continue
        tmp = w("_frames"); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
        for i in range(int(round((s - e) * 30)) + 1):
            emoldurar(src(i / 30)).save(os.path.join(tmp, f"{i:04d}.png"), compress_level=1)
        run(["-framerate", "30", "-i", os.path.join(tmp, "%04d.png"), "-c:v", "qtrle", w(f"m3-{nome}.mov")])
        shutil.rmtree(tmp)
        print("  foto", nome, flush=True)


def compor():
    ins = ["-i", w("base.mp4"), "-i", ORIG]
    fc, ult, n = [], "0:v", 2
    LWp, LHp = int((LW + 2 * M2.PAD) * ESC), int((LH + 2 * M2.PAD) * ESC)
    for j, (nome, e, s, (tipo, src)) in enumerate(TL):
        arq = w(f"m3-{nome}.mov") if tipo == "novo" else w(src)
        ins += ["-i", arq]
        if tipo == "full":
            fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{e}/TB,format=rgba,fade=t=in:st={e}:d=0.2:alpha=1,"
                      f"fade=t=out:st={s - 0.2}:d=0.2:alpha=1[i{j}]")
            pos = "x=0:y=0"
        else:
            fi = "" if e == 0 else f"fade=t=in:st={e}:d=0.3:alpha=1,"
            fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{e}/TB,scale={LWp}:{LHp},format=rgba,{fi}"
                      f"fade=t=out:st={s - 0.3}:d=0.3:alpha=1[i{j}]")
            pos = f"x=(W-w)/2:y={LOW_Y}-h/2"
        fc.append(f"[{ult}][i{j}]overlay={pos}:enable='between(t,{e},{s})':eof_action=pass[o{j}]")
        ult, n = f"o{j}", n + 1
    ins += ["-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", w("titulo.png")]
    fc.append(f"[{ult}][{n}:v]overlay=x=0:y=0:shortest=1[v]")
    fc.append("[1:a]loudnorm=I=-15:TP=-1.5[aud]")
    run(["-threads", "2"] + ins + ["-filter_complex", ";".join(fc), "-filter_threads", "2", "-map", "[v]",
         "-map", "[aud]", "-t", str(DUR), "-c:v", "libx264", "-crf", "19", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", SAIDA])
    print("saída:", SAIDA)


if __name__ == "__main__":
    for etapa in sys.argv[1:] or ["fotos", "compor"]:
        print(f"[{etapa}]", flush=True)
        globals()[etapa]()
