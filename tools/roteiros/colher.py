"""Colheita de referência para o banco de roteiros.

Dado um link (Instagram, TikTok, YouTube), baixa, transcreve (Groq), detecta os cortes e a folha de
contato, e escreve a FICHA RASCUNHO em docs/conteudo/banco-roteiros/referencias/ no molde do banco.
A análise (arquitetura, mecânicas, esqueleto) é preenchida depois — a máquina só entrega a matéria-prima.

uso:  python tools/roteiros/colher.py <url> [<url> ...] [--autor nome] [--lang en]
      python tools/roteiros/colher.py --lista links.txt
"""
import json, os, re, subprocess, sys, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BANCO = os.path.join(RAIZ, "docs", "conteudo", "banco-roteiros", "referencias")
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")


def slug(t, n=5):
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    palavras = [p for p in re.findall(r"[a-z0-9]+", t) if len(p) > 2][:n]
    return "-".join(palavras) or "sem-titulo"


def chave_groq():
    k = os.environ.get("GROQ_API_KEY")
    if not k:
        k = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "[Environment]::GetEnvironmentVariable('GROQ_API_KEY','User')"],
                           capture_output=True, text=True).stdout.strip()
    if not k:
        raise RuntimeError("GROQ_API_KEY não encontrada")
    return k


def baixar(url, dest):
    cmd = ["yt-dlp", url, "-o", f"{dest}.%(ext)s", "--write-info-json", "--no-warnings", "-q", "--no-playlist"]
    if subprocess.run(cmd).returncode:
        # Instagram às vezes dá HTTP 500 no áudio DASH (o padrão bv+ba); os progressivos "1/2/3" (vídeo+áudio juntos) baixam
        subprocess.run(cmd + ["-f", "1/2/3/b", "--retries", "3"], check=True)
    video = next(f"{dest}.{e}" for e in ("mp4", "mkv", "webm", "mov") if os.path.exists(f"{dest}.{e}"))
    info = json.load(open(f"{dest}.info.json", encoding="utf-8"))
    return video, info


def transcrever(video, dest, lang):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000",
                    "-b:a", "48k", f"{dest}.mp3"], check=True)
    subprocess.run(["curl.exe", "-s", "https://api.groq.com/openai/v1/audio/transcriptions",
                    "-H", f"Authorization: Bearer {chave_groq()}", "-F", f"file=@{dest}.mp3",
                    "-F", "model=whisper-large-v3", "-F", f"language={lang}",
                    "-F", "response_format=verbose_json", "-F", "timestamp_granularities[]=segment",
                    "-o", f"{dest}.json"], check=True)
    os.remove(f"{dest}.mp3")
    return json.load(open(f"{dest}.json", encoding="utf-8"))


def cortes(video):
    """Segundos em que a imagem muda de cena (B-roll, troca de plano)."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-filter:v",
                          "select='gt(scene,0.25)',showinfo", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return [round(float(m), 1) for m in re.findall(r"pts_time:([\d.]+)", out)]


def folha(video, dest, dur):
    passo = max(1, round(dur / 24))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf",
                    f"fps=1/{passo},scale=216:384,tile=8x3", "-frames:v", "1", f"{dest}-folha.png"], check=True)
    return f"{dest}-folha.png"


def ficha(url, info, texto, autor, sheet, cuts, dur):
    # id pela @ do perfil (bitterbuilds), como as fichas antigas; autor por extenso fica no corpo
    perfil = info.get("channel") or info.get("uploader_id") or autor
    codigo = (info.get("id") or "").split("_")[0][-11:] or "x"
    nome = f"ref-{slug(perfil, 2)}-{slug(info.get('description') or info.get('title') or 'sem-titulo', 4)}-{codigo}"
    linhas = [
        "---", f"id:            {nome}", "tipo:          referencia", f"autor:         {autor}",
        f"link:          {url}",
        f"publicado:     {info.get('upload_date', '')[:4]}-{info.get('upload_date', '')[4:6]}-{info.get('upload_date', '')[6:]}",
        f"duracao:       {dur:.0f}", "formato:       # talking head | tela + voz | demonstração",
        "faixa:         # Jornal | Intervalo | Nobre | Documentário", "funil:         # topo | meio | fundo",
        "gancho:        # G1–G10 ou candidato novo",
        "abertura:      # evidência | rótulo | pergunta | segredo | número",
        "mecanicas:     []", "cta:", "metricas_pub:",
        f"  curtidas:    {info.get('like_count', '')}", f"  comentarios: {info.get('comment_count', '')}",
        "  compartilh:  # preencher na mão (não vem na API)",
        "veredito:      # testar | descartar", "---", "",
        f"# {autor} — (título)", "", "> RASCUNHO da colheita automática. Falta: arquitetura, mecânicas, o que não copiar, esqueleto e adaptação.", "",
        "## Legenda do post", "", (info.get("description") or "—").strip(), "",
        "## Transcrição", "",
    ]
    for s in texto["segments"]:
        linhas.append(f"**{s['start']:.1f}s** {s['text'].strip()}")
    linhas += ["", "## Cortes detectados (s)", "", ", ".join(str(c) for c in cuts) or "nenhum (take único)", "",
               f"*Folha de contato:* `{os.path.relpath(sheet, RAIZ)}`", "",
               "## Arquitetura", "", "| Tempo | Fase | O que acontece | Função |", "|---|---|---|---|", "",
               "## Mecânicas", "", "## O que não copiar", "", "## Esqueleto", "", "```", "[0s]  ", "```", "",
               "## Adaptação", ""]
    destino = os.path.join(BANCO, f"{nome}.md")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    return destino


def colher(url, autor=None, lang="en"):
    os.makedirs(WORK, exist_ok=True)
    dest = os.path.join(WORK, re.sub(r"\W+", "_", url)[-40:])
    video, info = baixar(url, dest)
    autor = autor or info.get("uploader") or info.get("channel") or "desconhecido"
    dur = float(info.get("duration") or subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
        capture_output=True, text=True).stdout.strip())
    texto = transcrever(video, dest, lang)
    p = ficha(url, info, texto, autor, folha(video, dest, dur), cortes(video), dur)
    print(f"  ok: {autor} · {dur:.0f}s · {len(texto['segments'])} falas -> {os.path.relpath(p, RAIZ)}")
    return p


if __name__ == "__main__":
    args = sys.argv[1:]
    autor = lang = None
    if "--autor" in args:
        i = args.index("--autor"); autor = args[i + 1]; del args[i:i + 2]
    if "--lang" in args:
        i = args.index("--lang"); lang = args[i + 1]; del args[i:i + 2]
    if args and args[0] == "--lista":
        args = [l.strip() for l in open(args[1], encoding="utf-8") if l.strip().startswith("http")]
    for u in args:
        try:
            colher(u, autor, lang or "en")
        except Exception as e:
            print(f"  FALHOU {u}: {e}")
