"""video-recut / camadas — Reels em camadas, sem HyperFrames (ffmpeg + PIL + recorte torchvision).

  1. vídeo principal (talking-head) com cor ajustada
  2. faixa de cenas rolando de lado ATRÁS da pessoa, semitransparente (recorte)
  3. cenas de apoio em tela cheia (B-roll literal da frase, estilo @bitterbuilds)
  4. card pequeno com foto (ex.: autor da citação)
  5. legenda branca simples, 2-3 palavras

Primeiro vídeo (aprovado e postado 2026-09-19): videos/2026-09-plano-vs-prova/camadas.json
uso: python tools/video-recut/camadas/camadas.py <nome> [transcrever recorte fundo card legenda compor previa]
     sem etapas = todas; transcrever e recorte são pulados se o arquivo já existir em work/<nome>/.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V916 = "fps=30,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
FONTE = r"C:\Windows\Fonts\seguisb.ttf"


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def duracao(arq):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


class Projeto:
    def __init__(self, nome):
        self.nome = nome
        self.pasta_cfg = os.path.join(RAIZ, "videos", nome)
        self.work = os.path.join(RAIZ, "work", nome)
        os.makedirs(self.work, exist_ok=True)
        with open(os.path.join(self.pasta_cfg, "camadas.json"), encoding="utf-8") as f:
            self.c = json.load(f)
        self.base = os.path.expandvars(self.c.get("pasta", r"%USERPROFILE%\Downloads"))
        self.principal = self.arq(self.c["principal"])
        self.dur = self.c.get("duracao") or duracao(self.principal)
        self.cor = self.c.get("cor", "")
        fundo = self.c.get("fundo")
        # a máscara cobre o fundo com folga para o fade de entrada/saída
        self.mask_ini = max(0.0, fundo["inicio"] - 0.6) if fundo else 0
        self.trecho = (fundo["fim"] - self.mask_ini + 0.1) if fundo else 0

    def arq(self, nome):
        """Procura em videos/<nome>/, depois work/<nome>/, depois na pasta base (Downloads)."""
        if os.path.isabs(nome):
            return nome
        for pasta in (self.pasta_cfg, self.work, self.base):
            p = os.path.join(pasta, nome)
            if os.path.exists(p):
                return p
        raise FileNotFoundError(f"não achei {nome} em videos/, work/ nem {self.base}")

    def w(self, nome):
        return os.path.join(self.work, nome)

    # ------------------------------------------------------------ etapas
    def transcrever(self, forcar=False):
        if os.path.exists(self.w("words.json")) and not forcar:
            return print("  transcrição: já existe")
        chave = os.environ.get("GROQ_API_KEY") or subprocess.run(
            ["powershell", "-NoProfile", "-Command", "[Environment]::GetEnvironmentVariable('GROQ_API_KEY','User')"],
            capture_output=True, text=True).stdout.strip()
        if not chave:
            raise RuntimeError("GROQ_API_KEY não encontrada")
        run(["-i", self.principal, "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k", self.w("audio.mp3")])
        cfg = self.c.get("transcricao", {})
        subprocess.run(["curl.exe", "-s", "https://api.groq.com/openai/v1/audio/transcriptions",
                        "-H", f"Authorization: Bearer {chave}", "-F", f"file=@{self.w('audio.mp3')}",
                        "-F", "model=whisper-large-v3", "-F", "language=pt", "-F", f"prompt={cfg.get('prompt', '')}",
                        "-F", "response_format=verbose_json", "-F", "timestamp_granularities[]=word",
                        "-o", self.w("words.json")], check=True)
        os.remove(self.w("audio.mp3"))
        print("  transcrição:", json.load(open(self.w("words.json"), encoding="utf-8"))["text"][:160], "…")

    def recorte(self, forcar=False):
        if not self.c.get("fundo") or (os.path.exists(self.w("mask.mp4")) and not forcar):
            return print("  recorte: já existe / sem fundo")
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from recorte import recortar
        recortar(self.principal, self.w("mask.mp4"), self.mask_ini, self.trecho)

    def fundo(self):
        f = self.c.get("fundo")
        if not f:
            return
        tw, th = f.get("tile", [560, 996])
        gap, vel = f.get("gap", 24), f.get("velocidade", 180)
        dur = f["fim"] - f["inicio"] + 0.2
        ins, fc = [], []
        for i, (arq, ini, d) in enumerate(f["cenas"]):
            p = self.w(f"fundo{i}.mp4")   # trecho curto, repetido em loop no tile
            run(["-ss", str(ini), "-i", self.arq(arq), "-t", str(d), "-an", "-vf", V916,
                 "-c:v", "libx264", "-crf", "16", "-g", "30", "-pix_fmt", "yuv420p", p])
            ins += ["-stream_loop", "-1", "-i", p]
            fc.append(f"[{i}:v]trim=0:{dur},setpts=PTS-STARTPTS,scale={tw}:{th},pad={tw + gap}:{th}:{gap // 2}:0:black[t{i}]")
        n = len(f["cenas"])
        larg = n * (tw + gap)
        if larg - 1080 < vel * dur:
            print(f"  aviso: faixa curta ({n} cenas) para {dur:.1f}s a {vel}px/s — vai parar no fim")
        fc.append("".join(f"[t{i}]" for i in range(n)) + f"hstack={n},pad={larg}:1920:0:{(1920 - th) // 2}:black,"
                  f"crop=1080:1920:x='min(t*{vel},{larg - 1080})':y=0,format=yuv420p[v]")
        run(ins + ["-filter_complex", ";".join(fc), "-map", "[v]", "-t", str(dur), "-r", "30",
                   "-c:v", "libx264", "-crf", "16", "-g", "30", self.w("fundo.mp4")])

    def card(self):
        k = self.c.get("card")
        if not k:
            return
        W, H, B, R = 360, 450, 8, 22
        im = Image.open(self.arq(k["foto"])).convert("RGB")
        w, h = im.size
        if w * H / W <= h:   # foto mais alta que o card: corta embaixo, mantém o rosto
            ch = int(w * H / W); y0 = int(h * k.get("topo", 0.02))
            im = im.crop((0, y0, w, min(h, y0 + ch)))
        else:
            cw = int(h * W / H); x0 = (w - cw) // 2
            im = im.crop((x0, 0, x0 + cw, h))
        im = im.resize((W, H), Image.LANCZOS)
        card = Image.new("RGBA", (W + 2 * B, H + 2 * B + 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([0, 0, card.width - 1, card.height - 1], R, fill=(255, 255, 255, 255))
        m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, W - 1, H - 1], R - 6, fill=255)
        card.paste(im, (B, B), m)
        fonte = ImageFont.truetype(FONTE, 26)
        t = k.get("legenda", "")
        d.text(((card.width - d.textlength(t, font=fonte)) / 2, H + B + 14), t, font=fonte, fill=(20, 20, 24, 255))
        pad = 30
        out = Image.new("RGBA", (card.width + 2 * pad, card.height + 2 * pad), (0, 0, 0, 0))
        sombra = Image.new("RGBA", out.size, (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle([pad, pad + 8, pad + card.width, pad + card.height + 8], R, fill=(0, 0, 0, 120))
        out = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(14)), out)
        out.alpha_composite(card, (pad, pad))
        out = out.rotate(k.get("giro", -4), resample=Image.BICUBIC, expand=True)
        e = k.get("escala", 0.7)
        out.resize((int(out.width * e), int(out.height * e)), Image.LANCZOS).save(self.w("card.png"))

    def grupos(self):
        cfg = self.c.get("transcricao", {})
        remover = set(cfg.get("remover", []))
        trocar = cfg.get("trocar", {})
        ws = []
        for x in json.load(open(self.w("words.json"), encoding="utf-8"))["words"]:
            t = x["word"].strip()
            if t.strip(",.") in remover:
                continue
            ws.append([trocar.get(t, t), x["start"], x["end"]])
        grupos, atual = [], []
        for i, x in enumerate(ws):
            atual.append(x)
            pausa = i + 1 < len(ws) and ws[i + 1][1] - x[2] > 0.35
            if len(atual) >= 3 or x[0][-1] in ".,?!" or pausa or i == len(ws) - 1:
                grupos.append([" ".join(y[0] for y in atual).rstrip(".,"), atual[0][1], x[2]])
                atual = []
        for i, g in enumerate(grupos):   # fica até o próximo grupo (máx. +0,5 s)
            nxt = grupos[i + 1][1] if i + 1 < len(grupos) else self.dur
            g[2] = min(max(g[2], g[1] + 0.3) + 0.5, nxt)
        return grupos

    def legenda(self):
        cfg = self.c.get("legenda", {})
        fonte = ImageFont.truetype(cfg.get("fonte", FONTE), cfg.get("tamanho", 46))
        y = cfg.get("y", 1235)
        pasta = self.w("leg"); os.makedirs(pasta, exist_ok=True)
        vazio = os.path.join(pasta, "vazio.png")
        Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
        linhas, t = [], 0.0
        for i, (txt, a, b) in enumerate(self.grupos()):
            if a > t:
                linhas.append((vazio, a - t))
            img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
            sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
            x = (1080 - ImageDraw.Draw(img).textlength(txt, font=fonte)) / 2
            ImageDraw.Draw(sombra).text((x, y + 3), txt, font=fonte, fill=(0, 0, 0, 170))
            img = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(5)), img)
            ImageDraw.Draw(img).text((x, y), txt, font=fonte, fill=(255, 255, 255, 255))
            p = os.path.join(pasta, f"{i:03d}.png"); img.save(p)
            linhas.append((p, b - a)); t = b
        linhas.append((vazio, self.dur - t + 0.5))
        lista = os.path.join(pasta, "lista.txt")
        with open(lista, "w", encoding="utf-8") as f:   # UTF-8 sem BOM: caminho com acento
            for p, d in linhas:
                f.write(f"file '{p}'\nduration {d:.3f}\n")
            f.write(f"file '{vazio}'\n")
        run(["-f", "concat", "-safe", "0", "-i", lista, "-vf", "fps=30,format=rgba", "-c:v", "qtrle", self.w("legenda.mov")])

    def trecho_fundo(self):
        """Só o trecho com fundo passa pelo blend/recorte em gbrp (pesado em RAM); o resto fica em yuv."""
        f = self.c["fundo"]
        ini, fim, a0 = f["inicio"] - self.mask_ini, f["fim"] - self.mask_ini, f.get("opacidade", 0.5)
        # ATENÇÃO: no blend, T vem NaN nesta build do ffmpeg — usar N/30 (contador de quadros)
        a = f"{a0}*clip((N/30-{ini})/0.35,0,1)*clip(({fim}-N/30)/0.35,0,1)"
        fc = [
            f"[0:v]setpts=PTS-STARTPTS,{V916}{self.cor},format=gbrp,split=2[m1][m2]",
            f"[1:v]setpts=PTS-STARTPTS,format=gbrp,tpad=start_duration={ini}:stop_mode=clone:stop_duration=5,"
            f"trim=0:{self.trecho},setpts=PTS-STARTPTS[f]",
            "[2:v]fps=30,scale=1080:1920:flags=bicubic,gblur=sigma=2.5,format=gbrp[k]",
            f"[m1][f]blend=all_expr='A*(1-({a}))+B*({a})'[bg]",
            "[bg][m2][k]maskedmerge,format=yuv420p[v]",
        ]
        run(["-threads", "2", "-ss", str(self.mask_ini), "-t", str(self.trecho), "-i", self.principal,
             "-i", self.w("fundo.mp4"), "-i", self.w("mask.mp4"), "-filter_complex", ";".join(fc),
             "-filter_threads", "2", "-map", "[v]", "-t", str(self.trecho), "-c:v", "libx264", "-crf", "16",
             "-preset", "fast", "-threads", "2", self.w("trecho.mp4")])

    def compor(self):
        tem_fundo = bool(self.c.get("fundo"))
        if tem_fundo:
            self.trecho_fundo()
        ins, fc = ["-i", self.principal, "-i", self.w("legenda.mov")], [f"[0:v]{V916}{self.cor},format=yuv420p[c0]"]
        n, ultimo = 2, "c0"
        if tem_fundo:
            ins += ["-i", self.w("trecho.mp4")]
            fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{self.mask_ini}/TB[tr]")
            fc.append(f"[c0][tr]overlay=enable='between(t,{self.mask_ini},{self.mask_ini + self.trecho - 0.02})':eof_action=pass[c1]")
            n, ultimo = n + 1, "c1"
        for i, (arq, ini, em, dur, extra) in enumerate(self.c.get("apoio", [])):
            ins += ["-ss", str(ini), "-t", str(dur), "-i", self.arq(arq)]
            fc.append(f"[{n}:v]{V916}{extra},format=yuv420p,setpts=PTS-STARTPTS+{em}/TB[a{i}]")
            fc.append(f"[{ultimo}][a{i}]overlay=enable='between(t,{em},{em + dur - 0.02})':eof_action=pass[o{i}]")
            n, ultimo = n + 1, f"o{i}"
        k = self.c.get("card")
        if k:
            ins += ["-loop", "1", "-framerate", "30", "-t", str(self.dur), "-i", self.w("card.png")]
            e, s = k["entra"], k["sai"]
            fc.append(f"[{n}:v]format=rgba,fade=t=in:st={e}:d=0.25:alpha=1,fade=t=out:st={s - 0.3}:d=0.3:alpha=1[pc]")
            fc.append(f"[{ultimo}][pc]overlay=x=(W-w)/2:y='{k.get('y', 1300)}+60*max(0,1-(t-{e})/0.3)':"
                      f"enable='between(t,{e},{s})'[oc]")
            n, ultimo = n + 1, "oc"
        fc.append(f"[{ultimo}][1:v]overlay=format=auto[v]")
        m = self.c.get("musica")
        if m:   # {"arquivo": ..., "volume": 0.09} — o padrão é SEM música (Vitor põe no app)
            ins += ["-stream_loop", "-1", "-i", self.arq(m["arquivo"])]
            fc.append(f"[{n}:a]volume={m.get('volume', 0.09)},afade=t=out:st={self.dur - 2}:d=2[mus];"
                      "[0:a]loudnorm=I=-15:TP=-1.5[voz];[voz][mus]amix=inputs=2:duration=first:normalize=0[aud]")
        else:
            fc.append("[0:a]loudnorm=I=-15:TP=-1.5[aud]")
        saida = os.path.join(self.base, self.c.get("saida", f"{self.nome}.mp4"))
        run(["-threads", "2"] + ins + ["-filter_complex", ";".join(fc), "-filter_threads", "2",
             "-map", "[v]", "-map", "[aud]", "-t", str(self.dur), "-c:v", "libx264", "-crf", "18",
             "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida])
        print("  saída:", saida)

    def previa(self):
        """Folha de contato: 1 quadro a cada 3 s do vídeo final -> work/<nome>/previa.png"""
        saida = os.path.join(self.base, self.c.get("saida", f"{self.nome}.mp4"))
        run(["-i", saida, "-vf", "fps=1/3,scale=216:384,tile=8x2", "-frames:v", "1", self.w("previa.png")])
        print("  prévia:", self.w("previa.png"))


if __name__ == "__main__":
    p = Projeto(sys.argv[1])
    etapas = sys.argv[2:] or ["transcrever", "recorte", "fundo", "card", "legenda", "compor", "previa"]
    for e in etapas:
        print(f"[{e}]", flush=True)
        getattr(p, e)()
