"""Máquina de conteúdo, etapa 9b: monta o vídeo final a partir do edicao.json, sem ajuste à mão.

Generaliza o molde aprovado no "Rei do gelo" (14/10): pintura fixa no topo (opcional), título em Bebas Neue,
legenda de uma palavra por vez em Montserrat ExtraBold minúscula e inserções laterais retas, alternando.
Sem topo (molde Regra): só o título fixo na altura do peito e a legenda.

Entrada (na pasta do rascunho):
  edicao.json   {"titulo": "...", "topo": {"url": "...commons..."} | null,
                 "laterais": [{"de": 3.5, "ate": 6.1, "lado": "ESQ"|"DIR", "url": "..."}]}
  vídeo limpo   Downloads/<pasta>-limpo.mp4      (saída do limpar.cjs, etapa 8)
  transcrição   tools/video-recut/work/<pasta>/limpeza/palavras-editado.json   (tempos por palavra, já no vídeo cortado)
Saída: <pasta>/final.mp4 + <pasta>/previa.jpg

uso:  python tools/maquina/montar.py <pasta>
"""
import json, os, re, shutil, subprocess, sys, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
RASC = os.path.join(RAIZ, "docs", "conteudo", "maquina", "02-Rascunhos")
FONTES = os.path.join(RAIZ, "tools", "video-recut", "assets", "fontes")
BEBAS, MONT = os.path.join(FONTES, "BebasNeue-Regular.ttf"), os.path.join(FONTES, "Montserrat.ttf")
L, A, Y = 540, 400, 110                  # pintura do topo
ESQ, DIR = (170, 985), (910, 985)        # centro das laterais (rosto em x ~330–740)
LARG, ALT = 310, 390
Y_TIT_SEM_TOPO = 1180                    # molde Regra: título na altura do peito
Y_LEG = 1300                             # 16/10: o Vitor pediu a legenda menor e mais perto do meio (era 1440, fonte 54)


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def url_direta(u):
    """Página do Commons (…/wiki/File:X.jpg) → arquivo (Special:FilePath), em tamanho bom para 1080p."""
    m = re.search(r"commons\.wikimedia\.org/wiki/(?:File|Arquivo):(.+)$", u)
    if m:
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{m.group(1)}?width=1600"
    return u


def baixar(u, dest):
    if not os.path.exists(dest):
        req = urllib.request.Request(url_direta(u), headers={"User-Agent": "ARVEX-maquina/1.0 (conteudo)"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
            f.write(r.read())
    return dest


def enquadrar(im, larg, alt):
    im = im.convert("RGB")
    e = max(larg / im.width, alt / im.height)
    im = im.resize((int(im.width * e) + 1, int(im.height * e) + 1), Image.LANCZOS)
    x0, y0 = (im.width - larg) // 2, (im.height - alt) // 2
    return im.crop((x0, y0, x0 + larg, y0 + alt))


def titulo_png(texto, dest):
    tam = 96
    while tam > 40:
        ft = ImageFont.truetype(BEBAS, tam)
        if ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(texto, font=ft) <= 900:
            break
        tam -= 2
    linhas = [texto]
    if ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(texto, font=ft) > 900:   # quebra em 2 linhas
        p = texto.split(); meio = len(p) // 2
        linhas = [" ".join(p[:meio]), " ".join(p[meio:])]
        ft = ImageFont.truetype(BEBAS, 84)
    out = Image.new("RGBA", (1080, 110 * len(linhas) + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    for i, ln in enumerate(linhas):
        x = (1080 - ImageDraw.Draw(out).textlength(ln, font=ft)) / 2
        ImageDraw.Draw(sh).text((x, 24 + i * 100), ln, font=ft, fill=(0, 0, 0, 220), stroke_width=6, stroke_fill=(0, 0, 0, 220))
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(6)))
    for i, ln in enumerate(linhas):
        x = (1080 - ImageDraw.Draw(out).textlength(ln, font=ft)) / 2
        ImageDraw.Draw(out).text((x, 20 + i * 100), ln, font=ft, fill=(255, 255, 255), stroke_width=2, stroke_fill=(20, 20, 20))
    out.save(dest)
    return out.height


def palavras(transcricao, dur):
    j = json.load(open(transcricao, encoding="utf-8"))
    ws = [[x["word"].strip(), x["start"]] for x in (j["words"] if isinstance(j, dict) else j) if x["word"].strip()]
    out = []
    for k, (p, a) in enumerate(ws):
        if out and a <= out[-1][1]:                       # início fora de ordem devolvido pelo Whisper
            prox = ws[k + 1][1] if k + 1 < len(ws) else a + 0.3
            a = max(out[-1][1] + 0.12, min(prox - 0.12, out[-1][1] + 0.3))
        out.append([p, a])
    return out


def legenda_mov(ws, dur, work):
    fonte = ImageFont.truetype(MONT, 46)
    fonte.set_variation_by_name("ExtraBold")
    pasta = os.path.join(work, "leg"); shutil.rmtree(pasta, ignore_errors=True); os.makedirs(pasta)
    vazio = os.path.join(pasta, "vazio.png"); Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
    linhas, t = [], 0.0
    for i, (p, a) in enumerate(ws):
        txt = p.rstrip(".,?!;:")
        txt = txt if (txt[:1].isupper() and i and ws[i - 1][0][-1:] not in ".?!") else txt.lower()   # mantém nome próprio
        b = min(ws[i + 1][1] if i + 1 < len(ws) else dur, a + 0.8)
        if a > t:
            linhas.append((vazio, a - t))
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        x = (1080 - ImageDraw.Draw(img).textlength(txt, font=fonte)) / 2
        ImageDraw.Draw(sh).text((x, Y_LEG + 4), txt, font=fonte, fill=(0, 0, 0, 160), stroke_width=7, stroke_fill=(0, 0, 0, 160))
        img = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)), img)
        ImageDraw.Draw(img).text((x, Y_LEG), txt, font=fonte, fill="white", stroke_width=5, stroke_fill=(15, 15, 15))
        q = os.path.join(pasta, f"{i:03d}.png"); img.save(q)
        linhas.append((q, b - a)); t = b
    linhas.append((vazio, max(dur - t, 0) + 0.5))
    lista = os.path.join(pasta, "lista.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for q, d in linhas:
            f.write(f"file '{q}'\nduration {d:.3f}\n")
        f.write(f"file '{vazio}'\n")
    mov = os.path.join(work, "legenda.mov")
    run(["-f", "concat", "-safe", "0", "-i", lista, "-vf", "fps=30,format=rgba", "-c:v", "qtrle", mov])
    shutil.rmtree(pasta)
    return mov


def montar(pasta):
    pasta = os.path.join(RASC, os.path.basename(pasta.rstrip("/\\")))
    nome = os.path.basename(pasta)
    plano = json.load(open(os.path.join(pasta, "edicao.json"), encoding="utf-8-sig"))
    video = os.path.join(os.path.expandvars("%USERPROFILE%"), "Downloads", f"{nome}-limpo.mp4")
    # tempos do vídeo JÁ CORTADO: transcricao.json é do bruto e atrasa a legenda a cada pausa cortada (16/10)
    transc = os.path.join(RAIZ, "tools", "video-recut", "work", nome, "limpeza", "palavras-editado.json")
    for p in (video, transc):
        if not os.path.exists(p):
            sys.exit(f"falta {p}: rode antes  python tools/maquina/maquina.py corte {nome}")
    work = os.path.join(RAIZ, "tools", "video-recut", "work", nome, "montagem")
    os.makedirs(work, exist_ok=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                               capture_output=True, text=True).stdout.strip())

    topo = None
    if plano.get("topo") and plano["topo"].get("url"):
        im = Image.open(baixar(plano["topo"]["url"], os.path.join(work, "topo-orig")))
        topo = os.path.join(work, "topo.png")
        ImageOps.autocontrast(enquadrar(im, L, A), cutoff=1).save(topo)
    tit = os.path.join(work, "titulo.png")
    titulo_png(plano["titulo"], tit)
    y_tit = Y + A + 14 if topo else Y_TIT_SEM_TOPO
    lados = []
    for i, ins in enumerate(plano.get("laterais") or []):
        try:
            im = Image.open(os.path.join(RAIZ, ins["arquivo"]) if ins.get("arquivo")       # gráfico gerado (ex.: número do estudo)
                            else baixar(ins["url"], os.path.join(work, f"lado{i}-orig")))
        except Exception as e:                       # imagem que não baixa não derruba o vídeo
            print(f"  lateral {i} pulada ({e})"); continue
        q = os.path.join(work, f"lado{i}.png")
        ImageOps.autocontrast(enquadrar(im, LARG, ALT), cutoff=1).save(q)
        lados.append((q, float(ins["de"]), min(float(ins["ate"]), dur), ESQ if ins.get("lado", "ESQ").upper().startswith("E") else DIR))
    mov = legenda_mov(palavras(transc, dur), dur, work)

    FOLGA = 0.6                                       # 16/10: respiro depois da última palavra (o "torto" terminava cortado)
    dur += FOLGA
    ins, fc, ult, n = ["-i", video], [f"[0:v]fps=30,scale=1080:1920,format=yuv420p,tpad=stop_mode=clone:stop_duration={FOLGA}[b0]"], "b0", 1
    if topo:
        ins += ["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", topo]
        fc.append(f"[{ult}][{n}:v]overlay=x={(1080 - L) // 2}:y={Y}[ot0]"); ult, n = "ot0", n + 1
    ins += ["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", tit]
    fc.append(f"[{ult}][{n}:v]overlay=x=0:y={y_tit}[ot]"); ult, n = "ot", n + 1
    for i, (q, e, s, (cx, cy)) in enumerate(lados):
        ins += ["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", q]
        fc.append(f"[{n}:v]format=rgba,fade=t=in:st={e}:d=0.15:alpha=1,fade=t=out:st={s - 0.15}:d=0.15:alpha=1[l{i}]")
        fc.append(f"[{ult}][l{i}]overlay=x={cx - LARG // 2}:y='{cy - ALT // 2}+28*max(0,1-(t-{e})/0.22)':enable='between(t,{e},{s})'[ol{i}]")
        ult, n = f"ol{i}", n + 1
    ins += ["-i", mov]
    fc.append(f"[{ult}][{n}:v]overlay=format=auto[v]"); n += 1
    mus = plano.get("musica")   # {"arquivo": "tools/video-recut/assets/musica/x.mp3", "inicio": 8, "volume": 0.08}
    if mus:
        ins += ["-ss", str(mus.get("inicio", 0)), "-stream_loop", "-1", "-i", os.path.join(RAIZ, mus["arquivo"])]
        vol = float(mus.get("volume", 0.08))   # 16/10: "mais baixa", por baixo da voz
        fc += [f"[0:a]apad=pad_dur={FOLGA},loudnorm=I=-15:TP=-1.5[voz]",
               f"[{n}:a]volume={vol},afade=t=in:d=1,afade=t=out:st={max(dur - 1.5, 0):.2f}:d=1.5[mus]",
               "[voz][mus]amix=inputs=2:duration=first:normalize=0[aud]"]
    else:
        fc.append(f"[0:a]apad=pad_dur={FOLGA},loudnorm=I=-15:TP=-1.5[aud]")
    final = os.path.join(pasta, "final.mp4")
    run(["-threads", "2"] + ins + ["-filter_complex", ";".join(fc), "-filter_threads", "2", "-map", "[v]", "-map", "[aud]",
         "-t", str(dur), "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final])
    # prévia: 8 quadros do vídeo final, para a aprovação
    tiles = []
    for k in range(8):
        f = os.path.join(work, "_q.png")
        run(["-ss", f"{dur * (k + 0.5) / 8:.2f}", "-i", final, "-frames:v", "1", "-vf", "scale=270:480", f])
        tiles.append(Image.open(f).convert("RGB"))
    prev = Image.new("RGB", (270 * 4, 480 * 2))
    for k, tl in enumerate(tiles):
        prev.paste(tl, (270 * (k % 4), 480 * (k // 4)))
    prev.save(os.path.join(pasta, "previa.jpg"), quality=82)
    return final


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("final:", montar(sys.argv[1]))
