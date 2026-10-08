"""Estudo de player: puxa os reels de um perfil (Apify) e transcreve todos (Groq).

Matéria-prima para o estudo de padrões: métricas + transcrição de cada reel, num JSON só.
A análise é feita depois, em players/<pasta>/ESTUDO.md.

uso:  python tools/roteiros/estudo_player.py <usuario_instagram> <pasta> [--limite 50] [--lang pt]
saída: docs/conteudo/banco-roteiros/players/<pasta>/reels.json
cache: tools/roteiros/work/estudo/<usuario>/  (retoma de onde parou se o Groq limitar)
"""
import json, os, subprocess, sys, time, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYERS = os.path.join(RAIZ, "docs", "conteudo", "banco-roteiros", "players")
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work", "estudo")


def env(nome):
    v = os.environ.get(nome)
    if not v:
        v = subprocess.run(["powershell", "-NoProfile", "-Command",
                            f"[Environment]::GetEnvironmentVariable('{nome}','User')"],
                           capture_output=True, text=True).stdout.strip()
    if not v:
        raise RuntimeError(f"{nome} não encontrada")
    return v


def listar(usuario, limite, cache):
    arq = os.path.join(cache, "apify.json")
    if os.path.exists(arq):
        return json.load(open(arq, encoding="utf-8"))
    url = ("https://api.apify.com/v2/acts/apify~instagram-reel-scraper/run-sync-get-dataset-items"
           f"?token={env('APIFY_TOKEN')}&timeout=600")
    corpo = json.dumps({"username": [usuario], "resultsLimit": limite}).encode()
    req = urllib.request.Request(url, corpo, {"Content-Type": "application/json"})
    itens = json.load(urllib.request.urlopen(req, timeout=660))
    json.dump(itens, open(arq, "w", encoding="utf-8"), ensure_ascii=False)
    return itens


def transcrever(item, cache, lang):
    sc = item["shortCode"]
    arq = os.path.join(cache, f"{sc}.json")
    if os.path.exists(arq):
        return json.load(open(arq, encoding="utf-8"))
    midia = item.get("audioUrl") or item.get("videoUrl")
    if not midia:
        return None
    bruto, mp3 = os.path.join(cache, f"{sc}.src"), os.path.join(cache, f"{sc}.mp3")
    urllib.request.urlretrieve(midia, bruto)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", bruto, "-vn", "-ac", "1", "-ar", "16000",
                    "-b:a", "32k", mp3], check=True)
    os.remove(bruto)
    # A cota do Groq é por modelo: no 429, alterna para o outro antes de esperar.
    modelos = ["whisper-large-v3", "whisper-large-v3-turbo"]
    for tentativa in range(16):
        modelo = modelos[tentativa % 2]
        out = subprocess.run(["curl.exe", "-s", "-w", "\n%{http_code}",
                              "https://api.groq.com/openai/v1/audio/transcriptions",
                              "-H", f"Authorization: Bearer {env('GROQ_API_KEY')}",
                              "-F", f"file=@{mp3}", "-F", f"model={modelo}",
                              "-F", f"language={lang}", "-F", "response_format=verbose_json",
                              "-F", "timestamp_granularities[]=segment"],
                             capture_output=True, text=True, encoding="utf-8").stdout
        corpo, _, codigo = out.rpartition("\n")
        if codigo == "200":
            dado = json.loads(corpo)
            json.dump(dado, open(arq, "w", encoding="utf-8"), ensure_ascii=False)
            os.remove(mp3)
            return dado
        if codigo == "429" and tentativa % 2 == 0:
            continue  # tenta já o outro modelo
        espera = 60 * (tentativa // 2 + 1) if codigo == "429" else 10
        print(f"  {sc}: HTTP {codigo} nos dois modelos, nova tentativa em {espera}s", flush=True)
        time.sleep(espera)
    raise RuntimeError(f"{sc}: Groq falhou 16 vezes")


def main():
    args = sys.argv[1:]
    limite = int(args[args.index("--limite") + 1]) if "--limite" in args else 50
    lang = args[args.index("--lang") + 1] if "--lang" in args else "pt"
    usuario, pasta = [a for a in args if not a.startswith("--") and a not in (str(limite), lang)][:2]
    cache = os.path.join(WORK, usuario)
    os.makedirs(cache, exist_ok=True)

    # Fixados ficam fora (costumam ser antigos); o estudo prioriza os mais recentes.
    itens = [i for i in listar(usuario, limite + 10, cache) if i.get("shortCode") and not i.get("isPinned")]
    itens = sorted(itens, key=lambda i: i.get("timestamp") or "", reverse=True)[:limite]
    print(f"{usuario}: {len(itens)} reels", flush=True)
    saida = []
    for n, it in enumerate(itens, 1):
        t = transcrever(it, cache, lang)
        print(f"  [{n}/{len(itens)}] {it['shortCode']} ok", flush=True)
        saida.append({
            "shortCode": it["shortCode"],
            "url": f"https://www.instagram.com/reel/{it['shortCode']}/",
            "data": (it.get("timestamp") or "")[:10],
            "fixado": bool(it.get("isPinned")),
            "views": it.get("videoPlayCount") or it.get("videoViewCount"),
            "curtidas": it.get("likesCount"),
            "comentarios": it.get("commentsCount"),
            "duracao": round(it.get("videoDuration") or 0),
            "legenda": it.get("caption") or "",
            "transcricao": [{"t": round(s["start"], 1), "texto": s["text"].strip()}
                            for s in (t or {}).get("segments", [])],
        })
    destino = os.path.join(PLAYERS, pasta)
    os.makedirs(destino, exist_ok=True)
    json.dump(saida, open(os.path.join(destino, "reels.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"salvo: {os.path.join(destino, 'reels.json')}")


if __name__ == "__main__":
    main()
