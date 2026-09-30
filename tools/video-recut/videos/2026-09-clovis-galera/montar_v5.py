"""v5 — "a galera gosta" na régua nova (ref. Deybson Mallony, Dd2ev3tx41O, 16,8k ❤, MESMO áudio).

O que veio da ref (dentro do que os nossos takes de celular permitem):
  - UMA PALAVRA POR VEZ, no tempo exato da fala (words.json, Groq por palavra)
  - 3 estilos com função: palavra comum (Inter, a fonte da marca) · NOMES gigantes (serifada dourada
    que o Vitor aprovou na v4) com a imagem escurecendo · fecho que ACUMULA ("Quem tem que achar bom")
    e fecha num "SOU EU" grande
  - glitch curto na abertura, flash branco no "foram"
  - 10 planos em vez de 3 (sacada/estúdio/mesa alternando), push-in lento em cada um
  - corta o áudio no "sou eu" e fecha com imagem (≈20 s, como a ref)
Não tentamos: cursiva amarela, cortes de câmera de cinema, 16:9 — dependem de filmagem que não temos.

uso:  python montar_v5.py   →  Downloads/2026-09-clovis-galera-v5.mp4
"""
import json
import os
import random
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(AQUI, "..", "..", "work", "2026-09-clovis-galera-v5")
TAKES = os.path.join(AQUI, "takes")
SAIDA = os.path.join(os.environ["USERPROFILE"], "Downloads", "2026-09-clovis-galera-v5.mp4")
os.makedirs(WORK, exist_ok=True)

SERIF = os.path.join(AQUI, "InstrumentSerif-Regular.ttf")
SERIF_IT = os.path.join(AQUI, "InstrumentSerif-Italic.ttf")
INTER = os.path.join(AQUI, "Inter.ttf")

FPS, DUR, FIM_VOZ = 30, 20.0, 17.45
BRANCO, CREME, OURO = (255, 255, 255), (243, 238, 222), (226, 184, 88)

MESA = os.path.join(TAKES, "74C15A77-8FDB-4B26-AC84-FE7CB203E865.mp4")
SACADA = os.path.join(TAKES, "E3202855-2C0F-41A4-B3BA-DC5D1B9B1DDD.mp4")
ESTUDIO = os.path.join(TAKES, "C8D81249-B745-41EB-A3E8-86673BB24A85.mp4")

# (take, início no take, entra na linha do tempo, sai)
# Cortes AGRUPADOS POR LUGAR (como a ref: muitos cortes, mesmo espaço). A v5.0 alternava lugar a cada
# frase (sacada→mesa→sacada→estúdio…) e ficou "vai e volta sem motivo" — avaliação de 2026-09-30.
PLANOS = [
    # sacada — abertura
    (SACADA, 0.0, 0.00, 1.82),      # a galera gosta, foda-se
    (SACADA, 1.9, 1.82, 4.54),      # se o que a galera gosta fosse bom
    (SACADA, 3.9, 4.54, 5.64),      # não teríamos matado
    # estúdio — os nomes
    (ESTUDIO, 0.0, 5.64, 7.24),     # Sócrates · Jesus
    (ESTUDIO, 1.6, 7.24, 8.76),     # Gandhi
    (ESTUDIO, 3.1, 8.76, 10.40),    # Martin Luther King
    (ESTUDIO, 4.2, 10.40, 12.96),   # todos os grandes foram mortos pela galera
    # mesa — o fecho, digitando
    (MESA, 0.0, 12.96, 15.70),      # então, foda-se o que a galera acha bom
    (MESA, 6.0, 15.70, 17.45),      # quem tem que achar bom sou eu
    (MESA, 12.0, 17.45, 20.00),     # fecho sem texto
]

NOMES = {"sócrates", "jesus", "gandhi", "martin", "luther", "king"}


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


# ------------------------------------------------------------------ imagem

def imagem():
    partes = []
    for i, (arq, ini, a, b) in enumerate(PLANOS):
        d = b - a
        out = os.path.join(WORK, f"p{i}.mp4")
        # push-in lento de 4% ao longo do plano (a imagem nunca fica parada)
        vf = ("scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,"
              f"scale=w='trunc(1080*(1+0.04*t/{d:.3f})/2)*2':h=-2:eval=frame:flags=bicubic,"
              f"crop=1080:1920,setsar=1,fps={FPS},format=yuv420p")
        run(["-ss", str(ini), "-t", f"{d + 0.2:.3f}", "-i", arq, "-an", "-vf", vf, "-t", f"{d:.3f}",
             "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-g", "30", out])
        partes.append(out)
    lista = os.path.join(WORK, "planos.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for p in partes:
            f.write(f"file '{p}'\n".replace("\\", "/"))
    run(["-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", os.path.join(WORK, "imagem.mp4")])
    for p in partes:
        os.remove(p)


# ------------------------------------------------------------------ eventos de texto

def eventos():
    """Lista de (início, fim, estilo, texto) a partir das palavras cronometradas."""
    todas = json.load(open(os.path.join(AQUI, "words.json"), encoding="utf-8"))["words"]
    for w in todas:        # o Whisper pôs "Todos" (9,94) antes de "o caralho"; na fala vem depois
        if w["word"].strip().lower() == "todos":
            w["start"] = 10.36
    todas.sort(key=lambda w: w["start"])
    ws = []
    for w in todas:                                  # para no "eu" (o áudio segue, o vídeo não)
        ws.append(w)
        if w["word"].strip().strip(".,!?").lower() == "eu":
            break
    ev, acum_ini = [], None
    for i, w in enumerate(ws):
        txt = w["word"].strip().strip(".,!?")
        ini = w["start"]
        fim = ws[i + 1]["start"] if i + 1 < len(ws) else FIM_VOZ
        fim = max(fim, ini + 0.12)
        chave = txt.lower()
        if ini >= 15.65 and chave not in ("sou", "eu"):          # fecho acumulando
            acum_ini = acum_ini or ini
            ev.append((ini, fim, "acum", txt))
        elif chave in ("sou", "eu"):
            if chave == "sou":
                ev.append((ini, 18.9, "final", "SOU EU"))
        elif chave == "foda-se" and ini < 2:
            ev.append((ini, fim, "grito", "FODA-SE"))
        elif chave in NOMES:
            ev.append((ini, fim, "nome", txt.upper()))
        else:
            ev.append((ini, fim, "palavra", txt.lower() if txt not in ("Jesus",) else txt))
    return ev


# ------------------------------------------------------------------ tipografia

def fonte(caminho, tam, peso=None):
    f = ImageFont.truetype(caminho, tam)
    if peso:
        f.set_variation_by_axes([min(32, tam), peso])
    return f


def escalar(b, s):
    """Escala a IMAGEM já desenhada (sub-pixel, liso). Escalar a fonte dava degraus de tamanho
    inteiro e, na Inter variável, fazia o peso cair para Regular no meio da animação (tremida)."""
    if abs(s - 1.0) < 1e-3:
        return b
    return b.resize((max(1, round(b.width * s)), max(1, round(b.height * s))), Image.LANCZOS)


def bloco(txt_partes, f, cor_partes, alpha=1.0):
    """Renderiza uma linha (lista de pedaços com cores) num canvas pequeno com sombra suave."""
    esp = f.getlength(" ")
    larg = sum(f.getlength(p) for p in txt_partes) + esp * (len(txt_partes) - 1)
    H = int(f.size * 1.6)
    W = int(larg + 80)
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(txt), ImageDraw.Draw(sh)
    x = 40
    for p, c in zip(txt_partes, cor_partes):
        ds.text((x, int(f.size * 0.18) + 4), p, font=f, fill=(0, 0, 0, int(190 * alpha)))
        d.text((x, int(f.size * 0.18)), p, font=f, fill=c + (int(255 * alpha),))
        x += f.getlength(p) + esp
    return Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(max(4, f.size // 12))), txt)


def colar(frame, b, cy):
    frame.alpha_composite(b, (int(540 - b.width / 2), int(cy - b.height / 2)))


def penumbra(frame, larg, alt, cy, alpha):
    """Escurece de leve só a região atrás da legenda branca (sem borda visível): dá 'chão' para a
    letra em fundo claro — camiseta branca, céu, parede do estúdio. Desfoque num canvas pequeno."""
    m = 140
    W, H = int(larg * 1.3) + 2 * m, int(alt * 1.5) + 2 * m
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(c).ellipse([m, m, W - m, H - m], fill=(0, 0, 0, int(95 * alpha)))
    c = c.filter(ImageFilter.GaussianBlur(48))
    frame.alpha_composite(c, (int(540 - W / 2), int(cy - H / 2)))


F_PALAVRA = fonte(INTER, 88, 620)
F_NOME = fonte(SERIF, 230)
F_GRITO = fonte(SERIF, 300)
F_ACUM = fonte(SERIF_IT, 92)
F_FINAL = fonte(SERIF, 250)
Y = 980          # centro: nomes, grito e "SOU EU" (a imagem escurece junto)
Y_BRANCO = 1560  # terço de baixo: legenda branca, onde os 3 takes são mais escuros (fora do rosto/camiseta)


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def quadro(t, ev, flash_em, glitch):
    frame = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    ativos = [e for e in ev if e[0] <= t < e[1]]
    # escurecer a imagem nos nomes / grito / final
    escuro = 0.0
    for a, b, est, _ in ev:
        if est in ("nome", "grito", "final") and a - 0.05 <= t < b:
            escuro = max(escuro, 0.5 * ease((t - a + 0.05) / 0.12) * (1 if est != "final" else ease((18.9 - t) / 0.4)))
    if escuro:
        frame.alpha_composite(Image.new("RGBA", frame.size, (0, 0, 0, int(255 * escuro))))
    # fecho acumulando
    acum = [e for e in ev if e[2] == "acum" and e[0] <= t < 16.66]
    if acum:
        partes = [e[3] for e in acum]
        cores = [OURO if p.lower() == "bom" else CREME for p in partes]
        b = bloco(partes, F_ACUM, cores)
        penumbra(frame, b.width, F_ACUM.size, Y_BRANCO, 1.0)
        colar(frame, b, Y_BRANCO)
    for a, b_, est, txt in ativos:
        p = (t - a)
        if est == "palavra":
            # parada no lugar, só um fade de 2 quadros — sem crescer (era o que tremia)
            e = ease(p / 0.066)
            b = bloco([txt], F_PALAVRA, [BRANCO], alpha=e)
            penumbra(frame, b.width, F_PALAVRA.size, Y_BRANCO, e)
            colar(frame, b, Y_BRANCO)
        elif est in ("nome", "grito"):
            e = ease(p / 0.16)
            f = F_GRITO if est == "grito" else F_NOME
            f_fit = f
            while f_fit.getlength(txt) > 980:
                f_fit = f_fit.font_variant(size=f_fit.size - 6)
            colar(frame, escalar(bloco([txt], f_fit, [OURO], alpha=e), 1.08 - 0.08 * e), Y)
        elif est == "final":
            e = ease(p / 0.18)
            sai = ease((18.9 - t) / 0.4)
            colar(frame, escalar(bloco([txt], F_FINAL, [OURO], alpha=min(e, sai)), 1.1 - 0.1 * e), Y)
    # flash branco no "foram"
    if flash_em is not None and 0 <= t - flash_em < 0.2:
        a = int(215 * (1 - (t - flash_em) / 0.2))
        frame.alpha_composite(Image.new("RGBA", frame.size, (255, 250, 240, a)))
    # glitch de abertura (6 quadros): faixas horizontais deslocadas em tons da marca
    if t < 0.2:
        rnd = random.Random(int(t * FPS))
        d = ImageDraw.Draw(frame)
        for _ in range(14):
            y = rnd.randint(0, 1900)
            h = rnd.choice([6, 10, 18, 30])
            x0 = rnd.randint(-200, 700)
            cor = rnd.choice([(226, 184, 88, 190), (243, 238, 222, 170), (40, 40, 48, 200)])
            d.rectangle([x0, y, x0 + rnd.randint(200, 900), y + h], fill=cor)
    return frame


def legenda():
    ev = eventos()
    flash = next((e[0] for e in ev if e[3].lower() == "foram"), None)
    pasta = os.path.join(WORK, "leg")
    os.makedirs(pasta, exist_ok=True)
    n = int(DUR * FPS)
    for i in range(n):
        quadro(i / FPS, ev, flash, True).save(os.path.join(pasta, f"{i:04d}.png"))
    run(["-framerate", str(FPS), "-i", os.path.join(pasta, "%04d.png"), "-c:v", "png",
         os.path.join(WORK, "legenda.mov")])
    for f in os.listdir(pasta):
        os.remove(os.path.join(pasta, f))


def compor():
    run(["-i", os.path.join(WORK, "imagem.mp4"), "-i", os.path.join(WORK, "legenda.mov"),
         "-i", os.path.join(AQUI, "voz.m4a"),
         "-filter_complex",
         "[0:v][1:v]overlay=format=auto,format=yuv420p[v];"
         f"[2:a]atrim=0:{FIM_VOZ},afade=t=out:st={FIM_VOZ - 0.15}:d=0.15,apad=whole_dur={DUR},"
         "loudnorm=I=-15:TP=-1.5[a]",
         "-map", "[v]", "-map", "[a]", "-t", str(DUR), "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", SAIDA])
    print("saída:", SAIDA)


if __name__ == "__main__":
    imagem()
    legenda()
    compor()
