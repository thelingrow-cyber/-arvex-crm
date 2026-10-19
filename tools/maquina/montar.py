"""Máquina de conteúdo, etapa 9b: monta o vídeo final a partir do edicao.json, sem ajuste à mão.

Generaliza o molde aprovado no "Rei do gelo" (14/10): pintura fixa no topo (opcional), título em Bebas Neue,
legenda de uma palavra por vez em Montserrat ExtraBold minúscula e inserções laterais retas, alternando.
Sem topo (molde Regra): só o título fixo na altura do peito e a legenda.

Entrada (na pasta do rascunho):
  edicao.json   {"titulo": "...", "topo": {"url": "...commons..."} | null,
                 "laterais": [{"de": 3.5, "ate": 6.1, "lado": "ESQ"|"DIR", "url": "..."}]}
  vídeo limpo   Downloads/<pasta>-limpo.mp4      (saída do limpar.cjs, etapa 8)
  transcrição   tools/video-recut/work/<pasta>/limpeza/palavras-editado.json   (tempos por palavra, já no vídeo cortado)
Chaves opcionais (todas retrocompatíveis: sem elas o vídeo sai como antes):
  "topo": {"seq": [{"de": 0, "video": "tools/…/x.mp4", "inicio": 46, "crop": "w:h:x:y"} | {"de": 4.3, "arquivo"|"url": …}]}
          topo que troca ao longo do vídeo (corte seco), foto com zoom lento ou trecho de vídeo
  "topo": {"trio": [{"url"|"arquivo": …} | {"video": "tools/…/x.mp4", "inicio": 12, "crop": "w:h:x:y"}, …×3]}
          19/10 (referência do Vitor): 3 quadros quadrados lado a lado no topo, fixos o vídeo todo, título logo
          abaixo; vídeo no quadro toca em loop. As laterais continuam entrando e saindo embaixo.
  "laterais": [{"de", "ate", "lado", "video", "inicio", "crop"}]   inserção lateral em vídeo
  "cheia": [{"de": 13.5, "ate": 15.4, "video": "tools/…/x.mp4" | "arquivo"|"url": "…", "inicio": 82.5,
             "crop": "w:h:x:y", "modo": "encaixe" | "cobrir"}]
          19/10: momento em TELA INTEIRA, por cima de topo, título e laterais (a legenda continua por cima).
          "encaixe" (padrão): o quadro 16:9 inteiro na largura, sobre ele mesmo desfocado e escurecido, para não
          cortar a manchete do telejornal. "cobrir": recorta para preencher 1080x1920 (use "crop" para mirar).
          Entra e sai com dissolução de 0,2 s, para a volta à tela dividida não ser um corte seco.
Saída: <pasta>/final.mp4 + <pasta>/previa.jpg

uso:  python tools/maquina/montar.py <pasta>
"""
import hashlib, json, os, re, shutil, subprocess, sys, urllib.parse, urllib.request
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
TRIO, TGAP = 280, 24                     # 19/10: topo com 3 quadros lado a lado (referência do Vitor)
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
    dest += "-" + hashlib.md5(u.encode()).hexdigest()[:8]   # 19/10: cache pela URL (por posição, trocar a foto não pegava)
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


def titulo_fino(texto, dest):
    """18/10: tipografia do post da Amazon que o Vitor mandou de referência: caixa alta, fina (Arial regular),
    da largura da imagem do topo, em até 2 linhas equilibradas, sombra suave."""
    ft, med = ImageFont.truetype(os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "arial.ttf"), 56), \
        ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength
    texto, linhas = texto.upper(), [texto.upper()]
    if med(texto, font=ft) > 900:   # 18/10: o Vitor quer o título em uma linha só
        p = texto.split()
        meio = min(range(1, len(p)), key=lambda m: max(med(" ".join(p[:m]), font=ft), med(" ".join(p[m:]), font=ft)))
        linhas = [" ".join(p[:meio]), " ".join(p[meio:])]
    out = Image.new("RGBA", (1080, 64 * len(linhas) + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    for i, ln in enumerate(linhas):
        ImageDraw.Draw(sh).text(((1080 - med(ln, font=ft)) / 2, 22 + i * 64), ln, font=ft, fill=(0, 0, 0, 235),
                                stroke_width=5, stroke_fill=(0, 0, 0, 235))   # 18/10: lâmpada atrás apagava a letra fina
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(5)))
    for i, ln in enumerate(linhas):
        ImageDraw.Draw(out).text(((1080 - med(ln, font=ft)) / 2, 20 + i * 64), ln, font=ft, fill=(255, 255, 255))
    out.save(dest)
    return out.height


def titulo_png(texto, dest):
    tam = 96
    while tam > 64:   # 17/10: abaixo de 64 o título ficava miúdo numa linha; aí quebra em 2 linhas grandes
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
    if plano.get("topo") and plano["topo"].get("seq"):   # 18/10: topo que troca (vídeo e imagem em sequência, corte seco)
        partes = []
        for k, it in enumerate(plano["topo"]["seq"]):
            e = float(it["de"]); s = dur + 0.6 if k == len(plano["topo"]["seq"]) - 1 else float(plano["topo"]["seq"][k + 1]["de"])
            q = os.path.join(work, f"topo{k}.mp4")
            if it.get("video"):
                vf = (f"crop={it['crop']}," if it.get("crop") else "") + \
                     f"scale={L}:{A}:force_original_aspect_ratio=increase,crop={L}:{A},fps=30,setsar=1,eq=contrast=1.05"
                run(["-ss", str(it.get("inicio", 0)), "-t", f"{s - e:.3f}", "-i", os.path.join(RAIZ, it["video"]),
                     "-vf", vf, "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", q])
            else:
                im = Image.open(os.path.join(RAIZ, it["arquivo"]) if it.get("arquivo") else baixar(it["url"], os.path.join(work, f"topo{k}-orig")))
                p = os.path.join(work, f"topo{k}.png"); ImageOps.autocontrast(enquadrar(im, L, A), cutoff=1).save(p)
                run(["-loop", "1", "-framerate", "30", "-t", f"{s - e:.3f}", "-i", p, "-vf",   # zoom lento: a foto não fica morta
                     f"scale={L * 2}:{A * 2},zoompan=z='1+0.04*on/({(s - e) * 30:.0f})':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={L}x{A}:fps=30",
                     "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", q])
            partes.append(q)
        topo = os.path.join(work, "topo.mp4")   # filtro concat: o demuxer concat engolia a parte em vídeo logo após a foto (18/10)
        run(sum([["-i", q] for q in partes], []) + ["-filter_complex", "".join(f"[{k}:v]" for k in range(len(partes))) +
            f"concat=n={len(partes)}:v=1:a=0[v]", "-map", "[v]", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", topo])
    elif plano.get("topo") and (plano["topo"].get("url") or plano["topo"].get("arquivo")):
        im = Image.open(os.path.join(RAIZ, plano["topo"]["arquivo"]) if plano["topo"].get("arquivo")   # quadro de vídeo (17/10)
                        else baixar(plano["topo"]["url"], os.path.join(work, "topo-orig")))
        topo = os.path.join(work, "topo.png")
        ImageOps.autocontrast(enquadrar(im, L, A), cutoff=1).save(topo)
    trio = []
    if plano.get("topo") and plano["topo"].get("trio"):   # 19/10: 3 quadros lado a lado, fixos o vídeo todo
        x0 = (1080 - 3 * TRIO - 2 * TGAP) // 2
        for k, it in enumerate(plano["topo"]["trio"][:3]):
            if it.get("video"):
                q = os.path.join(work, f"trio{k}.mp4")
                vf = (f"crop={it['crop']}," if it.get("crop") else "") +                      f"scale={TRIO}:{TRIO}:force_original_aspect_ratio=increase,crop={TRIO}:{TRIO},fps=30,setsar=1"
                run(["-stream_loop", "-1", "-ss", str(it.get("inicio", 0)), "-i", os.path.join(RAIZ, it["video"]),
                     "-t", f"{dur + 0.6:.2f}", "-vf", vf, "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", q])
            else:
                im = Image.open(os.path.join(RAIZ, it["arquivo"]) if it.get("arquivo") else baixar(it["url"], os.path.join(work, f"trio{k}-orig")))
                q = os.path.join(work, f"trio{k}.png")
                ImageOps.autocontrast(enquadrar(im, TRIO, TRIO), cutoff=1).save(q)
            trio.append((q, x0 + k * (TRIO + TGAP)))
    tit = os.path.join(work, "titulo.png")
    estilo = titulo_png if plano.get("titulo_estilo") == "bebas" else titulo_fino   # 19/10: fino é o padrão (o Vitor mandou a referência 2x)
    estilo(plano["titulo"], tit)
    y_tit = Y + A + 14 if topo else Y + TRIO + 14 if trio else Y_TIT_SEM_TOPO
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
    cheias = []
    for i, ch in enumerate(plano.get("cheia") or []):   # 19/10: tela inteira (ver docstring)
        e, s = float(ch["de"]), min(float(ch["ate"]), dur)
        q = os.path.join(work, f"cheia{i}.mp4")
        if ch.get("video"):
            src = ["-ss", str(ch.get("inicio", 0)), "-t", f"{s - e:.3f}", "-i", os.path.join(RAIZ, ch["video"])]
        else:
            p = os.path.join(RAIZ, ch["arquivo"]) if ch.get("arquivo") else baixar(ch["url"], os.path.join(work, f"cheia{i}-orig"))
            src = ["-loop", "1", "-framerate", "30", "-t", f"{s - e:.3f}", "-i", p]
        cr = f"crop={ch['crop']}," if ch.get("crop") else ""
        if ch.get("modo", "encaixe") == "cobrir":
            fcc = f"[0:v]{cr}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1[v]"
        else:
            fcc = (f"[0:v]{cr}fps=30,setsar=1,split[a][b];"
                   f"[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2,eq=brightness=-0.28[bg];"
                   f"[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]")
        run(src + ["-filter_complex", fcc, "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", q])
        cheias.append((q, e, s))
    y_leg = y_legenda(video, dur, work)
    print(f"  legenda em y={y_leg}")
    mov = legenda_mov(palavras(transc, dur), dur, work, y_leg)

    FOLGA = 0.6                                       # 16/10: respiro depois da última palavra (o "torto" terminava cortado)
    dur += FOLGA
    ins, fc, ult, n = ["-i", video], [f"[0:v]fps=30,scale=1080:1920,format=yuv420p,tpad=stop_mode=clone:stop_duration={FOLGA}[b0]"], "b0", 1
    if topo:
        ins += ["-i", topo] if topo.endswith(".mp4") else ["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", topo]
        fc.append(f"[{n}:v]setpts=PTS-STARTPTS[tp];[{ult}][tp]overlay=x={(1080 - L) // 2}:y={Y}:eof_action=repeat[ot0]"); ult, n = "ot0", n + 1
    for k, (q, x) in enumerate(trio):
        ins += ["-i", q] if q.endswith(".mp4") else ["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", q]
        fc.append(f"[{ult}][{n}:v]overlay=x={x}:y={Y}:eof_action=repeat[tr{k}]"); ult, n = f"tr{k}", n + 1
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
    for i, (q, e, s) in enumerate(cheias):   # tela inteira: por cima de tudo, menos da legenda
        ins += ["-i", q]
        fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{e}/TB,format=rgba,fade=t=in:st={e}:d=0.2:alpha=1,"
                  f"fade=t=out:st={s - 0.2}:d=0.2:alpha=1[c{i}]")
        fc.append(f"[{ult}][c{i}]overlay=x=0:y=0:eof_action=pass:enable='between(t,{e},{s})'[oc{i}]")
        ult, n = f"oc{i}", n + 1
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
