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
Y_TIT_SEM_TOPO = 470                     # molde Regra: título acima da cabeça (em 1180 batia no rosto e na legenda, 16/10)
Y_LEG = 1300                             # 16/10: o Vitor pediu a legenda menor e mais perto do meio (era 1440, fonte 54)


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def url_direta(u):
    """Página do Commons (…/wiki/File:X.jpg) → arquivo (Special:FilePath), em tamanho bom para 1080p."""
    m = re.search(r"commons\.wikimedia\.org/wiki/(?:File|Arquivo):(.+)$", u)
    if m:
        nome = urllib.parse.quote(urllib.parse.unquote(m.group(1)))   # nome com acento ("único") quebrava o download
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{nome}?width=1600"
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
    while tam > 78:   # 17/10: abaixo disso o título longo ficava miúdo numa linha; quebra em 2 linhas grandes
        ft = ImageFont.truetype(BEBAS, tam)
        if ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(texto, font=ft) <= 900:
            break
        tam -= 2
    linhas = [texto]
    if ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(texto, font=ft) > 900:   # quebra em 2 linhas
        ft = ImageFont.truetype(BEBAS, 84)
        p, med = texto.split(), ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength
        meio = min(range(1, len(p)), key=lambda m: max(med(" ".join(p[:m]), font=ft), med(" ".join(p[m:]), font=ft)))
        linhas = [" ".join(p[:meio]), " ".join(p[meio:])]   # quebra que equilibra as duas linhas
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


def y_legenda(video, dur, work):
    """Legenda logo abaixo do queixo: acha o rosto em 6 quadros (OpenCV) e usa a mediana.
    Posição fixa não serve: no "Efeito IKEA" o rosto estava baixo, no "Remar" alto e a legenda caiu na boca (16/10)."""
    try:
        import cv2, numpy as np
        # YuNet (o OpenCV 5 não traz mais o haar). Modelo lido da memória: o OpenCV não abre caminho com acento ("Simões")
        buf = np.fromfile(os.path.join(RAIZ, "tools", "video-recut", "assets", "modelos", "face_yunet.onnx"), np.uint8)
        det, fundos = cv2.FaceDetectorYN.create("onnx", buf, np.array([], np.uint8), (1080, 1920), 0.7), []
        for k in range(6):
            f = os.path.join(work, f"_rosto{k}.png")
            run(["-ss", f"{dur * (k + 0.5) / 6:.2f}", "-i", video, "-frames:v", "1", "-vf", "scale=1080:1920", f])
            img = cv2.imdecode(np.fromfile(f, np.uint8), cv2.IMREAD_COLOR)
            _, rostos = det.detect(img)
            if rostos is not None:
                x, y, w, h = max(rostos[:, :4].tolist(), key=lambda r: r[2] * r[3])
                fundos.append(y + h)
        if fundos:
            return int(min(1620, max(1150, sorted(fundos)[len(fundos) // 2] + 30)))   # a caixa do YuNet termina no queixo
    except Exception as e:
        print(f"  rosto não detectado ({e}); legenda na altura padrão")
    return Y_LEG


def legenda_mov(ws, dur, work, y_leg=Y_LEG):
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
        ImageDraw.Draw(sh).text((x, y_leg + 4), txt, font=fonte, fill=(0, 0, 0, 160), stroke_width=7, stroke_fill=(0, 0, 0, 160))
        img = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)), img)
        ImageDraw.Draw(img).text((x, y_leg), txt, font=fonte, fill="white", stroke_width=5, stroke_fill=(15, 15, 15))
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
    if plano.get("topo") and (plano["topo"].get("url") or plano["topo"].get("arquivo")):
        im = Image.open(os.path.join(RAIZ, plano["topo"]["arquivo"]) if plano["topo"].get("arquivo")   # quadro de vídeo (17/10)
                        else baixar(plano["topo"]["url"], os.path.join(work, "topo-orig")))
        topo = os.path.join(work, "topo.png")
        ImageOps.autocontrast(enquadrar(im, L, A), cutoff=1).save(topo)
    tit = os.path.join(work, "titulo.png")
    titulo_png(plano["titulo"], tit)
    y_tit = Y + A + 14 if topo else Y_TIT_SEM_TOPO
    lados = []
    for i, ins in enumerate(plano.get("laterais") or []):
        lado = ESQ if ins.get("lado", "ESQ").upper().startswith("E") else DIR
        if ins.get("video"):   # 17/10: inserção em vídeo no mesmo quadro lateral ({"video", "inicio", "crop": "w:h:x:y"})
            q = os.path.join(work, f"lado{i}.mp4")
            e, s = float(ins["de"]), min(float(ins["ate"]), dur)
            vf = (f"crop={ins['crop']}," if ins.get("crop") else "") + \
                 f"scale={LARG}:{ALT}:force_original_aspect_ratio=increase,crop={LARG}:{ALT},fps=30,setsar=1"
            run(["-ss", str(ins.get("inicio", 0)), "-t", f"{s - e:.2f}", "-i", os.path.join(RAIZ, ins["video"]),
                 "-vf", vf, "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", q])
            lados.append((q, e, s, lado))
            continue
        try:
            im = Image.open(os.path.join(RAIZ, ins["arquivo"]) if ins.get("arquivo")       # gráfico gerado (ex.: número do estudo)
                            else baixar(ins["url"], os.path.join(work, f"lado{i}-orig")))
        except Exception as e:                       # imagem que não baixa não derruba o vídeo
            print(f"  lateral {i} pulada ({e})"); continue
        q = os.path.join(work, f"lado{i}.png")
        ImageOps.autocontrast(enquadrar(im, LARG, ALT), cutoff=1).save(q)
        lados.append((q, float(ins["de"]), min(float(ins["ate"]), dur), lado))
    y_leg = y_legenda(video, dur, work)
    print(f"  legenda em y={y_leg}")
    mov = legenda_mov(palavras(transc, dur), dur, work, y_leg)

    FOLGA = 0.6                                       # 16/10: respiro depois da última palavra (o "torto" terminava cortado)
    dur += FOLGA
    ins, fc, ult, n = ["-i", video], [f"[0:v]fps=30,scale=1080:1920,format=yuv420p,tpad=stop_mode=clone:stop_duration={FOLGA}[b0]"], "b0", 1
    if topo:
        ins += ["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", topo]
        fc.append(f"[{ult}][{n}:v]overlay=x={(1080 - L) // 2}:y={Y}[ot0]"); ult, n = "ot0", n + 1
    ins += ["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", tit]
    fc.append(f"[{ult}][{n}:v]overlay=x=0:y={y_tit}[ot]"); ult, n = "ot", n + 1
    for i, (q, e, s, (cx, cy)) in enumerate(lados):
        if q.endswith(".mp4"):   # vídeo: começa a tocar quando a inserção entra
            ins += ["-i", q]
            fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{e}/TB,format=rgba,fade=t=in:st={e}:d=0.15:alpha=1,"
                      f"fade=t=out:st={s - 0.15}:d=0.15:alpha=1[l{i}]")
            fc.append(f"[{ult}][l{i}]overlay=x={cx - LARG // 2}:y='{cy - ALT // 2}+28*max(0,1-(t-{e})/0.22)':eof_action=pass:"
                      f"enable='between(t,{e},{s})'[ol{i}]")
            ult, n = f"ol{i}", n + 1
            continue
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
