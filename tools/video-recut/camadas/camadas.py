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
import json, os, re, subprocess, sys
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

    # ---------------------------------------------------------- corte seco
    def cortar(self):
        """Tira as respirações/silêncios e reescreve o vídeo. Os tempos do JSON continuam
        sendo os do ORIGINAL — `self.t()` traduz para a linha do tempo já cortada."""
        cfg = self.c.get("cortar")
        if not cfg:
            return
        if isinstance(cfg, bool):
            cfg = {}
        saida = self.w("cortado.mp4")
        if not os.path.exists(saida):
            ruido, minimo, folga = cfg.get("ruido", -30), cfg.get("min", 0.30), cfg.get("folga", 0.10)
            out = subprocess.run(["ffmpeg", "-hide_banner", "-i", self.principal, "-af",
                                  f"silencedetect=noise={ruido}dB:d={minimo}", "-f", "null", "-"],
                                 capture_output=True, text=True).stderr
            silencios = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)],
                                 [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]))
            manter, t = [], 0.0
            for ini, fim in silencios:
                if ini - t > 0.25:
                    manter.append((max(0, t - folga), min(self.dur, ini + folga)))
                t = fim
            if self.dur - t > 0.25:
                manter.append((max(0, t - folga), self.dur))
            # "tirar": trechos do ORIGINAL a remover à mão (tentativa repetida, tropeço, gaguejo).
            # Subtrai cada faixa do que o detector de silêncio decidiu manter.
            for ta, tb in cfg.get("tirar", []):
                novos = []
                for a, b in manter:
                    if tb <= a or ta >= b:
                        novos.append((a, b))
                        continue
                    if a < ta:
                        novos.append((a, ta))
                    if b > tb:
                        novos.append((tb, b))
                manter = [(a, b) for a, b in novos if b - a > 0.12]
            fc = []
            for i, (a, b) in enumerate(manter):
                fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}]")
            fc.append("".join(f"[v{i}][a{i}]" for i in range(len(manter))) + f"concat=n={len(manter)}:v=1:a=1[v][a]")
            run(["-i", self.principal, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
                 "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-g", "30", "-c:a", "aac", "-b:a", "192k", saida])
            json.dump(manter, open(self.w("corte.json"), "w"))
            print(f"  corte: {len(manter)} trechos, {self.dur:.1f}s -> {sum(b - a for a, b in manter):.1f}s")
        self.mapa = json.load(open(self.w("corte.json")))
        self.principal = saida
        self.dur = round(sum(b - a for a, b in self.mapa), 2)

    def t(self, torig):
        """Tempo do original -> tempo no vídeo cortado."""
        if not getattr(self, "mapa", None):
            return torig
        acc = 0.0
        for a, b in self.mapa:
            if torig <= a:
                return round(acc, 3)
            if torig <= b:
                return round(acc + (torig - a), 3)
            acc += b - a
        return round(acc, 3)

    def arq(self, nome):
        """Procura em videos/<nome>/, depois work/<nome>/, depois na pasta base (Downloads)."""
        if os.path.isabs(nome):
            return nome
        for pasta in (self.pasta_cfg, self.work, os.path.join(RAIZ, "assets", "musica"),
                      os.path.join(RAIZ, "assets"), self.base):
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

    def cards(self):
        """Um ou vários cards com foto. `card` (dict) ou `cards` (lista) no JSON."""
        lista = self.c.get("cards") or ([self.c["card"]] if self.c.get("card") else [])
        for i, k in enumerate(lista):
            if k["foto"].lower().endswith((".mov", ".mp4")):
                continue           # card animado: o arquivo já vem pronto
            self._card(k, i)

    def card(self):
        self.cards()

    def _card(self, k, i=0):
        W, H, B, R = k.get("largura", 360), k.get("altura", 450), 8, 22
        im = Image.open(self.arq(k["foto"])).convert("RGB")
        w, h = im.size
        alvo, atual = W / H, w / h
        if atual > alvo:     # foto mais larga que o card: corta as laterais
            cw = int(h * alvo); x0 = (w - cw) // 2
            im = im.crop((x0, 0, x0 + cw, h))
        else:                # foto mais alta: corta embaixo e mantém o topo (rosto)
            ch = int(w / alvo); y0 = min(int(h * k.get("topo", 0.02)), h - ch)
            im = im.crop((0, y0, w, y0 + ch))
        im = im.resize((W, H), Image.LANCZOS)
        B = k.get("borda", B)                    # borda: 0 = imagem sem moldura branca
        rodape = 64 if k.get("legenda") else 0   # sem nome embaixo = moldura só na foto
        card = Image.new("RGBA", (W + 2 * B, H + 2 * B + rodape), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        if B:
            d.rounded_rectangle([0, 0, card.width - 1, card.height - 1], R, fill=(255, 255, 255, 255))
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, W - 1, H - 1], max(2, R - 6), fill=255)
        card.paste(im, (B, B), m)
        t = k.get("legenda", "")
        if t:
            fonte = ImageFont.truetype(FONTE, 26)
            d.text(((card.width - d.textlength(t, font=fonte)) / 2, H + B + 14), t, font=fonte, fill=(20, 20, 24, 255))
        pad = 30
        out = Image.new("RGBA", (card.width + 2 * pad, card.height + 2 * pad), (0, 0, 0, 0))
        sombra = Image.new("RGBA", out.size, (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle([pad, pad + 8, pad + card.width, pad + card.height + 8], R, fill=(0, 0, 0, 120))
        out = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(14)), out)
        out.alpha_composite(card, (pad, pad))
        out = out.rotate(k.get("giro", -4), resample=Image.BICUBIC, expand=True)
        e = k.get("escala", 0.7)
        out.resize((int(out.width * e), int(out.height * e)), Image.LANCZOS).save(self.w(f"card{i}.png"))

    def titulo(self):
        """Título fixo no topo, em caixa colorida (cobre a legenda queimada do original)."""
        k = self.c.get("titulo")
        if not k:
            return
        fonte = ImageFont.truetype(k.get("fonte", FONTE), k.get("tamanho", 58))
        larg_max = k.get("largura", 860)
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        linhas, atual = [], ""
        for p in k["texto"].split():
            teste = (atual + " " + p).strip()
            if d.textlength(teste, font=fonte) > larg_max and atual:
                linhas.append(atual); atual = p
            else:
                atual = teste
        linhas.append(atual)
        lh = int(fonte.size * 1.24)
        px, py = k.get("padding", [30, 18])
        # a caixa pode ser forçada mais larga que o texto para cobrir a legenda queimada do original
        w = max(max(d.textlength(l, font=fonte) for l in linhas), k.get("caixa_largura", 0) - 2 * px)
        x0, y0 = (1080 - w) / 2 - px, k.get("y", 300) - py
        x1, y1 = x0 + w + 2 * px, y0 + len(linhas) * lh + 2 * py
        sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle([x0, y0 + 8, x1, y1 + 8], k.get("raio", 18), fill=(0, 0, 0, 120))
        img = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(16)), img)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([x0, y0, x1, y1], k.get("raio", 18), fill=k.get("caixa", "#0E8F7A"))
        for i, l in enumerate(linhas):
            d.text((1080 / 2, y0 + py + i * lh + lh / 2), l, font=fonte, fill=k.get("cor", "#FFFFFF"), anchor="mm")
        img.save(self.w("titulo.png"))

    def _pasta(self, d, x, y, lado, simbolo):
        """Ícone de pasta desenhado (não é emoji do sistema), com um símbolo dentro."""
        c1, c2 = (74, 148, 226), (108, 176, 240)
        aba_h = lado * 0.17
        d.rounded_rectangle([x, y + aba_h * 0.5, x + lado * 0.52, y + aba_h * 1.6], lado * 0.06, fill=c1)
        d.rounded_rectangle([x, y + aba_h, x + lado, y + lado * 0.86], lado * 0.10, fill=c2)
        cx, cy, s = x + lado * 0.5, y + lado * 0.53, lado * 0.30
        if simbolo == "laptop":
            d.rounded_rectangle([cx - s, cy - s * 0.66, cx + s, cy + s * 0.4], s * 0.12, fill=(28, 32, 40))
            d.rounded_rectangle([cx - s * 1.22, cy + s * 0.4, cx + s * 1.22, cy + s * 0.66], s * 0.1,
                                fill=(210, 214, 220))
        elif simbolo == "pessoa":
            d.ellipse([cx - s * 0.46, cy - s * 0.86, cx + s * 0.46, cy + s * 0.06], fill=(246, 214, 176))
            d.rounded_rectangle([cx - s * 0.74, cy + s * 0.16, cx + s * 0.74, cy + s * 0.96], s * 0.34,
                                fill=(70, 96, 128))
        elif simbolo == "dinheiro":
            d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=(232, 196, 92))
            d.ellipse([cx - s * 0.78, cy - s * 0.78, cx + s * 0.78, cy + s * 0.78], outline=(150, 118, 40),
                      width=max(2, int(s * 0.1)))
            f = ImageFont.truetype(FONTE, int(s * 1.25))
            d.text((cx, cy), "$", font=f, fill=(120, 92, 26), anchor="mm")
        elif simbolo == "microfone":
            d.rounded_rectangle([cx - s * 0.34, cy - s * 0.92, cx + s * 0.34, cy + s * 0.18], s * 0.34,
                                fill=(44, 48, 56))
            d.arc([cx - s * 0.66, cy - s * 0.42, cx + s * 0.66, cy + s * 0.56], 0, 180,
                  fill=(44, 48, 56), width=max(3, int(s * 0.14)))
            d.line([(cx, cy + s * 0.56), (cx, cy + s * 0.94)], fill=(44, 48, 56), width=max(3, int(s * 0.14)))

    def blocos(self):
        """Padrão da referência do AI with Remy: NÃO existe título fixo na tela.

        Cada arquivo vira um bloco — cabeçalho com ícone de pasta + nome, e uma sub-lista
        numerada que se preenche conforme a fala. Ao acabar o bloco, ele é substituído pelo
        próximo. A densidade mora na sub-lista, não numa lista única que cresce.

        camadas.json:
          "blocos": {
            "x": 56, "y_nome": 150, "y_lista": 330, "tempos": "corte",
            "itens": [{"nome": "company.md", "simbolo": "laptop", "de": 4.1, "ate": 9.4,
                       "campos": [{"texto": "o que você faz", "em": 4.8}, ...]}]
          }
        """
        k = self.c.get("blocos")
        if not k:
            return
        cru = k.get("tempos") == "corte"          # tempos já na linha do tempo cortada
        T = (lambda v: v) if cru else self.t
        f_nome = ImageFont.truetype(k.get("fonte", FONTE), k.get("tamanho_nome", 62))
        f_item = ImageFont.truetype(k.get("fonte_item", r"C:\Windows\Fonts\segoeui.ttf"),
                                    k.get("tamanho_item", 38))
        x = k.get("x", 56)
        y_nome, y_lista, lh = k.get("y_nome", 150), k.get("y_lista", 330), k.get("linha", 58)
        lado = k.get("icone", 96)

        estados, n = [], 0
        ab = k.get("abertura")
        if ab:
            # Abertura igual à referência: cada linha do gancho tem a SUA pílula branca
            # (não é uma caixa só), legenda branca embaixo trocando com a fala, e as pastas
            # se empilhando uma de cada vez no meio do quadro.
            f_cx = ImageFont.truetype(k.get("fonte_caixa", r"C:\Windows\Fonts\seguisb.ttf"),
                                      ab.get("tamanho_caixa", 58))
            f_lg = ImageFont.truetype(k.get("fonte_abertura", r"C:\Windows\Fonts\seguisb.ttf"),
                                      ab.get("tamanho", 52))
            legs, pilhas = ab["legendas"], ab.get("pastas", [])
            for j, leg in enumerate(legs):
                img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ds, d = ImageDraw.Draw(sombra), ImageDraw.Draw(img)
                y = ab.get("y_caixa", 286)
                lh = int(f_cx.size * 1.30)
                for l in ab["caixa"].split("\n"):          # uma pílula por linha
                    lw = d.textlength(l, font=f_cx)
                    px, py = 26, 13
                    x0, x1 = (1080 - lw) / 2 - px, (1080 + lw) / 2 + px
                    ds.rounded_rectangle([x0, y + 7, x1, y + lh + 2 * py + 7], 14, fill=(0, 0, 0, 100))
                    y += lh + 6
                img = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(13)), img)
                d = ImageDraw.Draw(img)
                y = ab.get("y_caixa", 286)
                for l in ab["caixa"].split("\n"):
                    lw = d.textlength(l, font=f_cx)
                    px, py = 26, 13
                    x0, x1 = (1080 - lw) / 2 - px, (1080 + lw) / 2 + px
                    d.rounded_rectangle([x0, y, x1, y + lh + 2 * py], 14, fill="#FFFFFF")
                    d.text((540, y + py + lh / 2), l, font=f_cx, fill="#15161A", anchor="mm")
                    y += lh + 6
                sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ds = ImageDraw.Draw(sombra)
                g = ab.get("icone", 250)
                for p in pilhas:                            # pastas empilhando
                    if leg["em"] >= p["em"]:
                        self._pasta(ImageDraw.Draw(img), p["x"], p["y"], g, p["simbolo"])
                y_leg = ab.get("y_legenda", 1270)
                ds.text((543, y_leg + 4), leg["texto"], font=f_lg, fill=(0, 0, 0, 220), anchor="mm")
                img = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(9)), img)
                ImageDraw.Draw(img).text((540, y_leg), leg["texto"], font=f_lg,
                                         fill="#FFFFFF", anchor="mm")
                img.save(self.w(f"bl-ab{j}.png"))
                ini = T(leg["em"])
                fim = T(legs[j + 1]["em"]) if j + 1 < len(legs) else T(ab["ate"])
                estados.append((self.w(f"bl-ab{j}.png"), ini, fim))

        for b in k["itens"]:
            campos = b["campos"]
            for passo in range(len(campos) + 1):
                img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ds, d = ImageDraw.Draw(sombra), ImageDraw.Draw(img)
                self._pasta(d, x, y_nome, lado, b.get("simbolo", "laptop"))
                ds.text((x + lado + 26 + 3, y_nome + lado * 0.5 + 4), b["nome"], font=f_nome,
                        fill=(0, 0, 0, 205), anchor="lm")
                d.text((x + lado + 26, y_nome + lado * 0.5), b["nome"], font=f_nome,
                       fill=k.get("cor_nome", "#FFFFFF"), anchor="lm")
                for i, c in enumerate(campos):     # números visíveis desde o início do bloco
                    yy = y_lista + i * lh
                    ds.text((x + 3, yy + 3), f"{i + 1}.", font=f_item, fill=(0, 0, 0, 200))
                    d.text((x, yy), f"{i + 1}.", font=f_item, fill="#FFFFFF")
                    if i < passo:
                        ds.text((x + 58 + 3, yy + 3), c["texto"], font=f_item, fill=(0, 0, 0, 200))
                        d.text((x + 58, yy), c["texto"], font=f_item, fill="#FFFFFF")
                img = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(7)), img)
                img.save(self.w(f"bl{n}.png"))
                ini = T(b["de"]) if passo == 0 else T(campos[passo - 1]["em"])
                fim = T(campos[passo]["em"]) if passo < len(campos) else T(b["ate"])
                estados.append((self.w(f"bl{n}.png"), ini, fim))
                n += 1

        vazio = self.w("bl-vazio.png")
        Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(vazio)
        linhas, t = [], 0.0
        for cam, ini, fim in estados:
            if ini > t + 0.04:                      # intervalo entre blocos: tela limpa
                linhas += [f"file '{vazio}'".replace("\\", "/"), f"duration {round(ini - t, 3)}"]
            if fim > ini:
                linhas += [f"file '{cam}'".replace("\\", "/"), f"duration {round(fim - ini, 3)}"]
                t = fim
        linhas.append(f"file '{vazio}'".replace("\\", "/"))
        cam_txt = self.w("blocos.txt")
        open(cam_txt, "w", encoding="utf-8").write("\n".join(linhas) + "\n")
        run(["-f", "concat", "-safe", "0", "-i", cam_txt, "-vf", "fps=30,format=rgba",
             "-c:v", "qtrle", self.w("blocos.mov")])
        print(f"  blocos: {len(k['itens'])} arquivos, {n} estados -> blocos.mov")

    def lista(self):
        """Lista numerada que se preenche, com título fixo no topo (padrão medido em 74 mil ❤).

        A sacada da referência: os números de 1 a N aparecem VAZIOS desde o primeiro segundo.
        Quem assiste vê que faltam itens e fica para ver — retenção embutida na arte.

        Não anima: a lista só troca de estado. Por isso sai como N+1 PNGs em vez de vídeo,
        o que evita o pipe de gigabytes que um .mov de tela cheia custaria nesta máquina.

        camadas.json:
          "lista": {
            "titulo": "As 7 leis do ...",
            "itens": [{"texto": "Lei da ...", "em": 3.2}, ...],
            "x": 48, "y": 560, "linha": 74, "tamanho": 38, "titulo_tamanho": 46
          }
        """
        k = self.c.get("lista")
        if not k:
            return
        itens = k["itens"]
        f_it = ImageFont.truetype(k.get("fonte", FONTE), k.get("tamanho", 38))
        f_tt = ImageFont.truetype(k.get("fonte", FONTE), k.get("titulo_tamanho", 46))
        x = k.get("x", 48)
        y0 = k.get("y", 560)
        lh = k.get("linha", 74)
        cor = k.get("cor", "#FFFFFF")
        apagado = k.get("cor_numero", "#FFFFFF")
        larg_num = max(ImageDraw.Draw(Image.new("RGBA", (9, 9))).textlength(f"{i + 1}.", font=f_it)
                       for i in range(len(itens))) + 16

        for passo in range(len(itens) + 1):
            img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
            sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ds = ImageDraw.Draw(sombra)
            d = ImageDraw.Draw(img)
            if k.get("titulo"):                       # faixa branca no topo, texto escuro
                ty = k.get("titulo_y", 84)
                tw = d.textlength(k["titulo"], font=f_tt)
                px, py = 34, 16
                cx0, cx1 = (1080 - tw) / 2 - px, (1080 + tw) / 2 + px
                ds.rounded_rectangle([cx0, ty - py + 6, cx1, ty + f_tt.size + py + 6],
                                     k.get("raio", 10), fill=(0, 0, 0, 110))
                d.rounded_rectangle([cx0, ty - py, cx1, ty + f_tt.size + py],
                                    k.get("raio", 10), fill=k.get("titulo_caixa", "#FFFFFF"))
                d.text((540, ty + f_tt.size / 2), k["titulo"], font=f_tt,
                       fill=k.get("titulo_cor", "#15161A"), anchor="mm")
            for i, it in enumerate(itens):            # número sempre; texto só depois do `em`
                yy = y0 + i * lh
                ds.text((x + 2, yy + 3), f"{i + 1}.", font=f_it, fill=(0, 0, 0, 190))
                d.text((x, yy), f"{i + 1}.", font=f_it, fill=apagado)
                if i < passo:
                    ds.text((x + larg_num + 2, yy + 3), it["texto"], font=f_it, fill=(0, 0, 0, 190))
                    d.text((x + larg_num, yy), it["texto"], font=f_it, fill=cor)
            img = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(7)), img)
            img.save(self.w(f"lista{passo}.png"))

        # Um .mov unico em vez de N PNGs em loop: 13 entradas de tela cheia estouram a RAM
        # desta maquina. O concat por duracao da o mesmo resultado com uma entrada so.
        marcos = [self.t(k.get("entra", 0.15))] + [self.t(it["em"]) for it in itens]
        fim = (self.t(k["sai"]) if "sai" in k else self.dur)
        linhas = []
        for passo in range(len(itens) + 1):
            ini = marcos[passo]
            prox = marcos[passo + 1] if passo + 1 < len(marcos) else fim
            if prox <= ini:
                continue
            linhas.append(f"file '{self.w(f'lista{passo}.png')}'".replace("\\", "/"))
            linhas.append(f"duration {round(prox - ini, 3)}")
        linhas.append(f"file '{self.w(f'lista{len(itens)}.png')}'".replace("\\", "/"))
        cam = self.w("lista.txt")
        open(cam, "w", encoding="utf-8").write("\n".join(linhas) + "\n")
        run(["-f", "concat", "-safe", "0", "-i", cam, "-vf", "fps=30,format=rgba",
             "-c:v", "qtrle", self.w("lista.mov")])
        print(f"  lista: {len(itens)} itens, {len(itens) + 1} estados -> lista.mov")

    def motions(self):
        """Texto animado POR CIMA do vídeo (não é card).
        tipo 'cinetico' (padrão): palavra por palavra subindo sob máscara, régua de destaque
        que se abre e assinatura com entreletras fechando. tipo 'riscado': entra e é riscado."""
        for i, m in enumerate(self.c.get("motions", [])):
            if m.get("tipo", "cinetico") == "cinetico":
                self._motion_cinetico(m, i)
            else:
                self._motion_riscado(m, i)

    def _motion_cinetico(self, m, i):
        cor, destaque = m.get("cor", "#FFFFFF"), m.get("destaque", "#25D366")
        fonte = ImageFont.truetype(m.get("fonte", FONTE), m.get("tamanho", 104))
        f_sub = ImageFont.truetype(m.get("fonte", FONTE), m.get("tamanho_sub", 30))
        larg_max, W = m.get("largura", 920), 1080
        medida = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
        espaco = medida.textlength(" ", font=fonte)
        linhas, atual = [], []
        for p in m["texto"].split():
            teste = atual + [p]
            if medida.textlength(" ".join(teste), font=fonte) > larg_max and atual:
                linhas.append(atual); atual = [p]
            else:
                atual = teste
        linhas.append(atual)
        lh = int(fonte.size * 1.16)
        sub = m.get("sub", "")
        H = len(linhas) * lh + (130 if sub else 50) + 40
        dur = m["sai"] - m["entra"]
        passo = m.get("passo", 0.11)          # atraso entre palavras
        total_palavras = sum(len(l) for l in linhas)
        t_regua = passo * total_palavras + 0.22
        t_sub = t_regua + 0.22
        proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
                                 "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "qtrle",
                                 self.w(f"motion{i}.mov")], stdin=subprocess.PIPE)
        suave = lambda p: 1 - (1 - p) ** 3     # ease-out
        for f in range(int(dur * 30)):
            t = f / 30
            quadro = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            k = 0
            bloco_larg = 0
            for j, palavras in enumerate(linhas):
                larg_linha = sum(medida.textlength(p, font=fonte) for p in palavras) + espaco * (len(palavras) - 1)
                bloco_larg = max(bloco_larg, larg_linha)
                faixa = Image.new("RGBA", (int(larg_linha) + 24, lh + 18), (0, 0, 0, 0))
                x = 12
                for p in palavras:
                    pw = medida.textlength(p, font=fonte)
                    prog = suave(min(1.0, max(0.0, (t - k * passo) / 0.34)))
                    if prog > 0:
                        palavra = Image.new("RGBA", (int(pw) + 24, lh + 18), (0, 0, 0, 0))
                        dp = ImageDraw.Draw(palavra)
                        dp.text((12, 8 + 3), p, font=fonte, fill=(0, 0, 0, 190))   # sombra
                        dp.text((12, 8), p, font=fonte, fill=cor)
                        palavra = palavra.filter(ImageFilter.GaussianBlur(0)) if prog > 0.99 else palavra
                        faixa.alpha_composite(palavra, (int(x) - 12, int((1 - prog) * (lh + 10))))
                    x += pw + espaco
                    k += 1
                quadro.alpha_composite(faixa, (int((W - larg_linha) / 2) - 12, 20 + j * lh))
            d = ImageDraw.Draw(quadro)
            pr = suave(min(1.0, max(0.0, (t - t_regua) / 0.40)))       # régua de destaque
            if pr > 0:
                yy = 20 + len(linhas) * lh + 10
                lw = bloco_larg * 0.92 * pr
                d.rounded_rectangle([(W - lw) / 2, yy, (W + lw) / 2, yy + 7], 4, fill=destaque)
            if sub:
                ps = min(1.0, max(0.0, (t - t_sub) / 0.45))
                if ps > 0:
                    tracking = 16 - 10 * suave(ps)
                    larg_sub = sum(medida.textlength(c, font=f_sub) + tracking for c in sub) - tracking
                    xs, ys = (W - larg_sub) / 2, 20 + len(linhas) * lh + 52   # folga da régua
                    tinta = (255, 255, 255, int(190 * ps))
                    for c in sub:
                        d.text((xs, ys), c, font=f_sub, fill=tinta)
                        xs += medida.textlength(c, font=f_sub) + tracking
            a = min(1.0, t / 0.18) * min(1.0, (dur - t) / 0.38)
            quadro.putalpha(quadro.getchannel("A").point(lambda v: int(v * a)))
            proc.stdin.write(quadro.tobytes())
        proc.stdin.close(); proc.wait()
        print(f"  motion{i} (cinético): {len(linhas)} linha(s), {dur:.1f}s")

    def _motion_riscado(self, m, i):
        fonte = ImageFont.truetype(m.get("fonte", FONTE), m.get("tamanho", 88))
        larg_max = m.get("largura", 900)
        medida = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
        linhas, atual = [], ""
        for p in m["texto"].split():
            teste = (atual + " " + p).strip()
            if medida.textlength(teste, font=fonte) > larg_max and atual:
                linhas.append(atual); atual = p
            else:
                atual = teste
        linhas.append(atual)
        lh = int(fonte.size * 1.22)
        W, H = 1080, len(linhas) * lh + 70
        dur = m["sai"] - m["entra"]
        risca = m.get("risca", dur * 0.45)
        proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
                                 "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "qtrle",
                                 self.w(f"motion{i}.mov")], stdin=subprocess.PIPE)
        for f in range(int(dur * 30)):
            t = f / 30
            img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ds, d = ImageDraw.Draw(sombra), ImageDraw.Draw(img)
            entrada = min(1.0, t / 0.28)
            dy = int(18 * (1 - entrada) ** 2)
            prog = 0.0 if t < risca else min(1.0, (t - risca) / 0.38)
            for j, l in enumerate(linhas):
                lw = d.textlength(l, font=fonte)
                x, y = (W - lw) / 2, 35 + j * lh + dy
                ds.text((x, y + 4), l, font=fonte, fill=(0, 0, 0, 200))
                d.text((x, y), l, font=fonte, fill=m.get("cor", "#FFFFFF"))
                pj = min(1.0, max(0.0, prog * len(linhas) - j))   # risca uma linha por vez
                if pj > 0:
                    yy = y + fonte.size * 0.58
                    d.line([(x - 10, yy), (x - 10 + (lw + 20) * pj, yy)],
                           fill=m.get("risco", "#25D366"), width=max(6, fonte.size // 11))
            img = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(9)), img)
            a = min(1.0, t / 0.22) * min(1.0, (dur - t) / 0.3)
            img.putalpha(img.getchannel("A").point(lambda v: int(v * a)))
            proc.stdin.write(img.tobytes())
        proc.stdin.close(); proc.wait()
        print(f"  motion{i}: {len(linhas)} linha(s), {dur:.1f}s")

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
        if cfg is None:      # "legenda": null desliga a legenda (peça de lista não usa)
            print("  legenda: desligada")
            return
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
            larg = ImageDraw.Draw(img).textlength(txt, font=fonte)
            x = (1080 - larg) / 2
            caixa = cfg.get("caixa")
            if caixa:   # palavras brancas dentro de uma caixa colorida (ex.: verde)
                px, py = cfg.get("padding", [26, 14])
                alt = fonte.size + 2 * py
                sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ImageDraw.Draw(sombra).rounded_rectangle(
                    [x - px, y - py + 6, x + larg + px, y + alt - py + 6], cfg.get("raio", 14), fill=(0, 0, 0, 110))
                img = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(12)), img)
                ImageDraw.Draw(img).rounded_rectangle(
                    [x - px, y - py, x + larg + px, y + alt - py], cfg.get("raio", 14), fill=caixa)
            else:
                sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ImageDraw.Draw(sombra).text((x, y + 3), txt, font=fonte, fill=(0, 0, 0, 170))
                img = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(5)), img)
            ImageDraw.Draw(img).text((x, y), txt, font=fonte, fill=cfg.get("cor", "#FFFFFF"))
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

    def _faixa(self, alt, opac):
        """Faixa que divide vídeo (em cima) e pessoa (embaixo): sem linha — os dois vídeos
        escurecem suavemente até se fundirem no meio (curva cosseno)."""
        import math
        col = Image.new("RGBA", (1, alt), (0, 0, 0, 0))
        for y in range(alt):
            a = int(255 * opac * (0.5 + 0.5 * math.cos(math.pi * (y - alt / 2) / (alt / 2))))
            col.putpixel((0, y), (6, 6, 9, a))
        col.resize((1080, alt)).save(self.w("faixa.png"))

    def compor(self):
        tem_fundo = bool(self.c.get("fundo"))
        if tem_fundo:
            self.trecho_fundo()
        tem_leg = self.c.get("legenda", {}) is not None
        ins = ["-i", self.principal] + (["-i", self.w("legenda.mov")] if tem_leg else [])
        fc = [f"[0:v]{V916}{self.cor},format=yuv420p[c0]"]
        n, ultimo = (2 if tem_leg else 1), "c0"
        if tem_fundo:
            ins += ["-i", self.w("trecho.mp4")]
            fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{self.mask_ini}/TB[tr]")
            fc.append(f"[c0][tr]overlay=enable='between(t,{self.mask_ini},{self.mask_ini + self.trecho - 0.02})':eof_action=pass[c1]")
            n, ultimo = n + 1, "c1"
        # tapar: borra um retângulo do próprio vídeo (ex.: legenda queimada no original)
        for i, t in enumerate(self.c.get("tapar", [])):
            x, y, larg, alt = t["x"], t["y"], t["largura"], t["altura"]
            ini, fim = self.t(t["inicio"]), self.t(t["fim"])
            fc.append(f"[{ultimo}]split[tb{i}][tc{i}]")
            fc.append(f"[tc{i}]crop={larg}:{alt}:{x}:{y},boxblur={t.get('forca', 18)}:2,eq=brightness=-0.05[tr{i}]")
            fc.append(f"[tb{i}][tr{i}]overlay={x}:{y}:enable='between(t,{ini},{fim})'[tp{i}]")
            ultimo = f"tp{i}"
        for i, (arq, ini, em, dur, extra) in enumerate(self.c.get("apoio", [])):
            em = self.t(em)
            ins += ["-ss", str(ini), "-t", str(dur), "-i", self.arq(arq)]
            fc.append(f"[{n}:v]{V916}{extra},format=yuv420p,setpts=PTS-STARTPTS+{em}/TB[a{i}]")
            fc.append(f"[{ultimo}][a{i}]overlay=enable='between(t,{em},{em + dur - 0.02})':eof_action=pass[o{i}]")
            n, ultimo = n + 1, f"o{i}"
        # dividido: vídeo em cima, a pessoa embaixo (deslocada para baixo), faixa semitransparente entre os dois
        dv = self.c.get("divisao", {})
        A, Y0, FX = dv.get("altura", 860), dv.get("origem_y", 680), dv.get("faixa", 90)
        if self.c.get("dividido"):
            self._faixa(FX, dv.get("opacidade", 0.55))
        for i, (arq, ini, em, dur, extra) in enumerate(self.c.get("dividido", [])):
            em = self.t(em)
            fim = em + dur - 0.02
            ins += ["-ss", str(ini), "-t", str(dur), "-i", self.arq(arq)]
            ins += ["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", self.w("faixa.png")]
            fc.append(f"[{ultimo}]split[db{i}][ds{i}]")
            fc.append(f"[ds{i}]crop=1080:{1920 - A}:0:{Y0}[dc{i}]")
            fc.append(f"[db{i}][dc{i}]overlay=0:{A}:enable='between(t,{em},{fim})'[dm{i}]")
            fc.append(f"[{n}:v]fps=30{extra},scale=1080:{A}:force_original_aspect_ratio=increase:flags=lanczos,"
                      f"crop=1080:{A},setsar=1,format=yuv420p,setpts=PTS-STARTPTS+{em}/TB[dv{i}]")
            fc.append(f"[dm{i}][dv{i}]overlay=0:0:enable='between(t,{em},{fim})':eof_action=pass[do{i}]")
            fc.append(f"[{n + 1}:v]format=rgba,setpts=PTS-STARTPTS+{em}/TB[df{i}]")
            fc.append(f"[do{i}][df{i}]overlay=0:{A - FX // 2}:enable='between(t,{em},{fim})':eof_action=pass[dx{i}]")
            n, ultimo = n + 2, f"dx{i}"
        for i, k in enumerate(self.c.get("cards") or ([self.c["card"]] if self.c.get("card") else [])):
            animado = k["foto"].lower().endswith((".mov", ".mp4"))
            if animado:            # card já animado (rolagem, lupa): entra como vídeo
                ins += ["-i", self.arq(k["foto"])]
            else:
                ins += ["-loop", "1", "-framerate", "30", "-t", str(self.dur), "-i", self.w(f"card{i}.png")]
            e, s, y = self.t(k["entra"]), self.t(k["sai"]), k.get("y", 1300)
            desliza = k.get("desliza", 60)   # de onde ele entra: +60 = sobe de baixo, -60 = desce de cima
            deslocar = f"setpts=PTS-STARTPTS+{e}/TB," if animado else ""
            # "surge": false = já está na tela no primeiro quadro em que entra (sem fade nem deslize)
            entrada = f"fade=t=in:st={e}:d=0.25:alpha=1," if k.get("surge", True) else ""
            if not k.get("surge", True):
                desliza = 0
            fc.append(f"[{n}:v]{deslocar}format=rgba,{entrada}fade=t=out:st={s - 0.3}:d=0.3:alpha=1[pc{i}]")
            fc.append(f"[{ultimo}][pc{i}]overlay=x={k.get('x', '(W-w)/2')}:y='{y}+{desliza}*max(0,1-(t-{e})/0.3)':"
                      f"enable='between(t,{e},{s})':eof_action=pass[oc{i}]")
            n, ultimo = n + 1, f"oc{i}"
        for i, m in enumerate(self.c.get("motions", [])):
            e, s = self.t(m["entra"]), self.t(m["sai"])
            ins += ["-i", self.w(f"motion{i}.mov")]
            fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{e}/TB[mt{i}]")
            fc.append(f"[{ultimo}][mt{i}]overlay=0:{m.get('y', 760)}:enable='between(t,{e},{s})':"
                      f"eof_action=pass:format=auto[om{i}]")
            n, ultimo = n + 1, f"om{i}"
        k = self.c.get("blocos")
        if k:
            ins += ["-i", self.w("blocos.mov")]
            fc.append(f"[{n}:v]format=rgba[bl]")
            fc.append(f"[{ultimo}][bl]overlay=0:0:eof_action=pass[ob]")
            n, ultimo = n + 1, "ob"

        k = self.c.get("lista")
        if k:
            ini = self.t(k.get("entra", 0.15))
            fim = (self.t(k["sai"]) if "sai" in k else self.dur)
            ins += ["-i", self.w("lista.mov")]
            fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{ini}/TB,format=rgba,"
                      f"fade=t=in:st={ini}:d=0.25:alpha=1[ls]")
            fc.append(f"[{ultimo}][ls]overlay=0:0:enable='between(t,{ini},{fim})':"
                      f"eof_action=pass[ol]")
            n, ultimo = n + 1, "ol"

        k = self.c.get("titulo")
        if k:
            ins += ["-loop", "1", "-framerate", "30", "-t", str(self.dur), "-i", self.w("titulo.png")]
            e, s = self.t(k.get("entra", 0.15)), (self.t(k["sai"]) if "sai" in k else self.dur)
            fc.append(f"[{n}:v]format=rgba,fade=t=in:st={e}:d=0.2:alpha=1,fade=t=out:st={max(e, s - 0.3)}:d=0.3:alpha=1[tt]")
            fc.append(f"[{ultimo}][tt]overlay=0:0:enable='between(t,{e},{s})'[ot]")
            n, ultimo = n + 1, "ot"
        if tem_leg:
            fc.append(f"[{ultimo}][1:v]overlay=format=auto[v]")
        else:
            fc.append(f"[{ultimo}]null[v]")
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
    p.cortar()   # sempre primeiro: troca o vídeo principal e cria o mapa de tempos
    etapas = sys.argv[2:] or ["transcrever", "recorte", "fundo", "cards", "blocos", "lista", "titulo",
                              "legenda", "compor", "previa"]
    for e in etapas:
        print(f"[{e}]", flush=True)
        getattr(p, e)()
