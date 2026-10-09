"""Gera os anexos do ESTUDO.md de um player a partir dos dados e da classificação.

Entrada (em docs/conteudo/banco-roteiros/players/<pasta>/):
  reels.json          — saída do estudo_player.py (métricas + transcrição)
  classificacao.json  — feita pelo analista: {"usuario", "videos": {shortCode: [formato, gancho, fecho]},
                        "repostagens": [...], "picos": [...]}
Saída: reescreve, no fim do ESTUDO.md, a região a partir do marcador ANEXOS:
  Anexo A — mediana por formato · Anexo B — os vídeos com a abertura literal ·
  Anexo C — roteiros completos dos maiores (+ picos de fora da janela, do cache do estudo_player)

uso: python tools/roteiros/estudo_anexos.py <pasta> [--roteiros 10]
"""
import json, os, re, statistics as st, sys, collections

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYERS = os.path.join(RAIZ, "docs", "conteudo", "banco-roteiros", "players")
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work", "estudo")
MARCADOR = "<!-- ANEXOS · gerado por tools/roteiros/estudo_anexos.py · não editar à mão daqui para baixo -->"
TESTE = 500  # abaixo disso, em perfil grande, é trial reel reprovado (não post normal)


def br(n):
    return f"{n:,}".replace(",", ".")


def frases(texto):
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+", texto) if f.strip()]


def bloco_roteiro(titulo, texto):
    return [titulo + "\n", "```", *frases(texto), "```\n"]


def main():
    args = sys.argv[1:]
    pasta = args[0]
    n_rot = int(args[args.index("--roteiros") + 1]) if "--roteiros" in args else 10
    base = os.path.join(PLAYERS, pasta)
    d = json.load(open(os.path.join(base, "reels.json"), encoding="utf-8"))
    c = json.load(open(os.path.join(base, "classificacao.json"), encoding="utf-8"))
    F, rep, picos = c["videos"], set(c.get("repostagens", [])), c.get("picos", [])
    falt = [x["shortCode"] for x in d if x["shortCode"] not in F]
    if falt:
        sys.exit(f"classificacao.json sem estes vídeos: {falt}")

    texto = {x["shortCode"]: " ".join(s["texto"] for s in x["transcricao"]).strip() for x in d}
    out = [MARCADOR, "", "---", "", "## Anexo A — mediana por formato", "",
           f"Cada roteiro contado uma vez (repostagens fora). *Testes* = abaixo de {br(TESTE)} views.", "",
           "| Formato | Vídeos | Mediana de views | Teto | Duração mediana | Testes reprovados |",
           "|---|---|---|---|---|---|"]
    g = collections.defaultdict(list)
    for x in d:
        if x["shortCode"] not in rep:
            g[F[x["shortCode"]][0]].append(x)
    for k, v in sorted(g.items(), key=lambda kv: -st.median([y["views"] or 0 for y in kv[1]])):
        vs = [y["views"] or 0 for y in v]
        out.append(f"| {k} | {len(v)} | {br(int(st.median(vs)))} | {br(max(vs))} | "
                   f"{int(st.median([y['duracao'] for y in v]))}s | {sum(i < TESTE for i in vs)} |")

    out += ["", "## Anexo B — os vídeos, com a abertura literal", "",
            "Ordenados por views. 🔁 = repostagem · 🧪 = teste reprovado · ❤ -1 = curtidas ocultas.", "",
            "| Views | ❤ | 💬 | Data | Dur. | Formato | Gancho (tipo) | Fecho | Abertura literal |",
            "|---|---|---|---|---|---|---|---|---|"]
    for x in sorted(d, key=lambda x: -(x["views"] or 0)):
        sc = x["shortCode"]
        f = F[sc]
        ab = texto[sc][:150].rsplit(" ", 1)[0].replace("|", "/") + "…"
        tag = ("🔁 " if sc in rep else "") + ("🧪 " if (x["views"] or 0) < TESTE else "")
        out.append(f"| [{br(x['views'] or 0)}]({x['url']}) | {br(x['curtidas'] or 0)} | {br(x['comentarios'] or 0)} | "
                   f"{x['data']} | {x['duracao']}s | {tag}{f[0]} | {f[1]} | {f[2]} | {ab} |")

    out += ["", "---", "", "## Anexo C — roteiros completos dos maiores", "",
            "Transcrição automática (Whisper), uma frase por linha para ler o ritmo da fala. "
            "Pode ter palavra trocada ou acento faltando; o conteúdo é fiel.", ""]
    vistos, n = set(), 0
    for x in sorted(d, key=lambda x: -(x["views"] or 0)):
        sc, t = x["shortCode"], texto[x["shortCode"]]
        if sc in rep or len(t.split()) < 40 or t[:60].lower() in vistos:
            continue
        vistos.add(t[:60].lower())
        out += bloco_roteiro(f"### {br(x['views'] or 0)} views · {x['duracao']}s · {x['data']} · [link]({x['url']})", t)
        n += 1
        if n == n_rot:
            break

    cache = os.path.join(WORK, c.get("usuario", ""))
    if picos and os.path.isdir(cache):
        apify = {i["shortCode"]: i for i in json.load(open(os.path.join(cache, "apify.json"), encoding="utf-8"))
                 if i.get("shortCode")}
        out += ["### Picos de fora da janela", ""]
        for sc in picos:
            arq = os.path.join(cache, f"{sc}.json")
            if not os.path.exists(arq) or sc not in apify:
                out.append(f"*{sc}: sem transcrição no cache (rodar estudo_player.py com --picos).*\n")
                continue
            i = apify[sc]
            t = " ".join(s["text"].strip() for s in json.load(open(arq, encoding="utf-8"))["segments"])
            out += bloco_roteiro(f"#### {br(i.get('videoPlayCount') or 0)} views · {round(i.get('videoDuration') or 0)}s · "
                                 f"{(i.get('timestamp') or '')[:10]} · [link](https://www.instagram.com/reel/{sc}/)", t)

    caminho = os.path.join(base, "ESTUDO.md")
    atual = open(caminho, encoding="utf-8").read() if os.path.exists(caminho) else f"# {pasta} — estudo completo\n"
    if MARCADOR in atual:
        topo = atual[:atual.index(MARCADOR)]
    else:  # estudos antigos: anexos colados sem marcador, a partir do primeiro "## Anexo A"
        m = re.search(r"(\n---\s*\n+)?## Anexo A", atual)
        topo = atual[:m.start()] if m else atual
    open(caminho, "w", encoding="utf-8").write(topo.rstrip() + "\n\n" + "\n".join(out) + "\n")
    print(f"{pasta}: anexos A ({len(g)} formatos) · B ({len(d)} vídeos) · C ({n} roteiros + {len(picos)} picos)")


if __name__ == "__main__":
    main()
