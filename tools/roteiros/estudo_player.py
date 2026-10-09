"""Estudo de player: puxa os reels de um perfil (Apify) e transcreve todos (Groq).

Matéria-prima para o estudo de padrões: métricas + transcrição de cada reel, num JSON só.
A análise é feita depois, em players/<pasta>/ESTUDO.md.

uso:  python tools/roteiros/estudo_player.py <usuario_instagram> <pasta> [--limite 50] [--picos 3] [--lang pt]
saída: docs/conteudo/banco-roteiros/players/<pasta>/reels.json + resumo.json
       (resumo: medianas, por mês, testes reprovados <500, repostagens, picos de fora da janela já transcritos)
cache: tools/roteiros/work/estudo/<usuario>/  (retoma de onde parou se o Groq limitar)
"""
import argparse, collections, json, os, statistics as st, subprocess, sys, time, urllib.request

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


def resumir(saida, itens_todos, janela, cache, lang, n_picos):
    """Números do perfil, testes reprovados, repostagens e picos de fora da janela (transcritos)."""
    hoje = max(x["data"] for x in saida)
    from datetime import date
    idade = lambda x: (date.fromisoformat(hoje) - date.fromisoformat(x["data"])).days
    testes = [x["shortCode"] for x in saida if (x["views"] or 0) < 500]
    recentes = [x["shortCode"] for x in saida if idade(x) < 3]
    validos = [x["views"] or 0 for x in saida if x["shortCode"] not in testes and x["shortCode"] not in recentes]
    por_mes = collections.defaultdict(list)
    for x in saida:
        por_mes[x["data"][:7]].append(x["views"] or 0)
    grupos = collections.defaultdict(list)
    for x in sorted(saida, key=lambda x: x["data"]):
        chave = " ".join(s["texto"] for s in x["transcricao"])[:60].lower()
        if len(chave) > 30:
            grupos[chave].append(x["shortCode"])
    repostagens = [g for g in grupos.values() if len(g) > 1]

    fora = sorted([i for i in itens_todos if i["shortCode"] not in janela],
                  key=lambda i: -(i.get("videoPlayCount") or i.get("videoViewCount") or 0))[:n_picos]
    picos = []
    for i in fora:
        try:
            transcrever(i, cache, lang)
            ok = True
        except Exception as e:  # carrossel sem áudio etc.
            print(f"  pico {i['shortCode']}: sem transcrição ({e})", flush=True)
            ok = False
        picos.append({"shortCode": i["shortCode"], "views": i.get("videoPlayCount") or i.get("videoViewCount"),
                      "data": (i.get("timestamp") or "")[:10], "fixado": bool(i.get("isPinned")), "transcrito": ok})
    return {
        "n": len(saida), "janela": [min(x["data"] for x in saida), hoje],
        "mediana_views": int(st.median([x["views"] or 0 for x in saida])),
        "mediana_sem_testes_e_recentes": int(st.median(validos)) if validos else None,
        "duracao_mediana": int(st.median([x["duracao"] for x in saida])),
        "por_mes": {k: {"reels": len(v), "mediana": int(st.median(v))} for k, v in sorted(por_mes.items())},
        "testes_reprovados": testes, "recentes_menos_de_3_dias": recentes,
        "repostagens": repostagens, "picos_fora_da_janela": picos,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("usuario")
    ap.add_argument("pasta")
    ap.add_argument("--limite", type=int, default=50)
    ap.add_argument("--picos", type=int, default=3)
    ap.add_argument("--lang", default="pt")
    a = ap.parse_args()
    cache = os.path.join(WORK, a.usuario)
    os.makedirs(cache, exist_ok=True)

    # Lista o dobro para achar os picos de fora da janela; a janela são os mais recentes, sem fixados.
    todos = [i for i in listar(a.usuario, a.limite * 2, cache) if i.get("shortCode")]
    itens = sorted([i for i in todos if not i.get("isPinned")], key=lambda i: i.get("timestamp") or "",
                   reverse=True)[:a.limite]
    print(f"{a.usuario}: {len(itens)} reels", flush=True)
    saida = []
    for n, it in enumerate(itens, 1):
        t = transcrever(it, cache, a.lang)
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
    destino = os.path.join(PLAYERS, a.pasta)
    os.makedirs(destino, exist_ok=True)
    json.dump(saida, open(os.path.join(destino, "reels.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    resumo = {"usuario": a.usuario, **resumir(saida, todos, {x["shortCode"] for x in saida}, cache, a.lang, a.picos)}
    json.dump(resumo, open(os.path.join(destino, "resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"salvo: reels.json + resumo.json em {destino}")
    print(f"  mediana {resumo['mediana_views']} · sem testes/recentes {resumo['mediana_sem_testes_e_recentes']} · "
          f"testes {len(resumo['testes_reprovados'])} · repostagens {len(resumo['repostagens'])} · "
          f"picos {[p['views'] for p in resumo['picos_fora_da_janela']]}")


if __name__ == "__main__":
    main()
