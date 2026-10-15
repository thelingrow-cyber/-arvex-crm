"""Máquina de conteúdo, etapas 1 e 3: puxa os reels dos concorrentes e atualiza o banco de ganchos.

Rodar a cada 2 dias. Para cada perfil de 05-Concorrentes/concorrentes.json: puxa os reels recentes
(Apify), transcreve os de mais views (Groq) e grava a coleta do dia. Depois reconstrói, a partir de
todas as coletas, o painel (05-Concorrentes/painel.html) e o banco de ganchos (06-Ganchos/ganchos.md),
ordenado por views.

uso:  python tools/maquina/coletar.py            # coleta de hoje (retoma se cair no meio)
      python tools/maquina/coletar.py --so-banco # só reconstrói painel e ganchos
"""
import argparse, datetime, glob, html, json, os, sys
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "tools", "roteiros"))
from estudo_player import listar, transcrever  # noqa: E402  (mesma Apify e mesmo Groq do estudo)

MAQ = os.path.join(RAIZ, "docs", "conteudo", "maquina")
CONC = os.path.join(MAQ, "05-Concorrentes")
CACHE = os.path.join(RAIZ, "tools", "roteiros", "work", "maquina")


def coletar_perfil(p, dia, cfg):
    destino = os.path.join(CONC, "coletas", dia, f"{p['usuario']}.json")
    if os.path.exists(destino):
        return p["usuario"], "já coletado"
    cache = os.path.join(CACHE, dia, p["usuario"])
    os.makedirs(cache, exist_ok=True)
    itens = [i for i in listar(p["usuario"], cfg["limite_por_perfil"], cache)
             if i.get("shortCode") and not i.get("isPinned")]
    itens.sort(key=lambda i: i.get("timestamp") or "", reverse=True)
    itens = itens[:cfg["limite_por_perfil"]]
    views = lambda i: i.get("videoPlayCount") or i.get("videoViewCount") or 0
    top = {i["shortCode"] for i in sorted(itens, key=views, reverse=True)[:cfg["transcrever_top"]]}
    saida = []
    for it in itens:
        tr = None
        if it["shortCode"] in top:
            try:
                tr = transcrever(it, cache, p.get("lang", "pt"))
            except Exception as e:  # carrossel sem áudio, mídia expirada
                print(f"  {p['usuario']} {it['shortCode']}: sem transcrição ({e})", flush=True)
        segs = [s["text"].strip() for s in (tr or {}).get("segments", [])]
        saida.append({
            "perfil": p["usuario"], "nome": p["nome"], "shortCode": it["shortCode"],
            "url": f"https://www.instagram.com/reel/{it['shortCode']}/",
            "data": (it.get("timestamp") or "")[:10], "views": views(it),
            "curtidas": it.get("likesCount"), "comentarios": it.get("commentsCount"),
            "duracao": round(it.get("videoDuration") or 0), "legenda": it.get("caption") or "",
            "abertura": " ".join(segs[:2]), "transcricao": " ".join(segs),
        })
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    json.dump(saida, open(destino, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return p["usuario"], f"{len(saida)} reels, {len(top)} transcritos"


def todos_reels():
    vistos = {}
    for arq in sorted(glob.glob(os.path.join(CONC, "coletas", "*", "*.json"))):
        for r in json.load(open(arq, encoding="utf-8")):
            vistos[r["shortCode"]] = r  # a coleta mais nova sobrescreve (views atualizadas)
    return sorted(vistos.values(), key=lambda r: -(r["views"] or 0))


def fmt(n):
    return f"{n or 0:,}".replace(",", ".")


def banco_ganchos(reels):
    com = [r for r in reels if r["abertura"]]
    L = ["# Banco de ganchos", "",
         f"> Gerado por `tools/maquina/coletar.py` em {datetime.date.today():%d/%m/%Y}. **{len(com)} aberturas** "
         "de concorrentes, ordenadas por views. O roteirista **modela o mecanismo** do gancho; não copia a frase.", "",
         "| # | Views | Perfil | Abertura literal | Data | Link |", "|---|---|---|---|---|---|"]
    for n, r in enumerate(com, 1):
        ab = r["abertura"].replace("|", "/")[:220]
        L.append(f"| {n} | {fmt(r['views'])} | @{r['perfil']} | {ab} | {r['data']} | [reel]({r['url']}) |")
    os.makedirs(os.path.join(MAQ, "06-Ganchos"), exist_ok=True)
    open(os.path.join(MAQ, "06-Ganchos", "ganchos.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    return len(com)


def painel(reels, dia):
    ultima = [r for r in reels if os.path.exists(os.path.join(CONC, "coletas", dia, f"{r['perfil']}.json"))]
    por_perfil = {}
    for r in ultima:
        por_perfil.setdefault(r["perfil"], []).append(r)
    top = max(por_perfil.items(), key=lambda kv: sum(r["views"] or 0 for r in kv[1]), default=("—", []))
    gancho = next((r for r in ultima if r["abertura"]), None)
    linhas = "".join(
        f"<tr><td>{fmt(r['views'])}</td><td>@{html.escape(r['perfil'])}</td><td>{r['data']}</td>"
        f"<td>{html.escape(r['abertura'][:160] or (r['legenda'] or '')[:160])}</td>"
        f"<td><a href='{r['url']}'>abrir</a></td></tr>" for r in ultima[:80])
    card = lambda t, v: f"<div class='c'><small>{t}</small><b>{v}</b></div>"
    doc = f"""<!doctype html><html lang="pt-br"><head><meta charset="utf-8"><title>Painel dos concorrentes</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>
body{{font:14px system-ui;background:#f4f1ea;color:#1d1d1b;margin:0;padding:24px}}h1{{margin:0 0 4px}}
.g{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:16px 0}}
.c{{background:#fff;border-radius:8px;padding:12px}}.c small{{display:block;color:#777;font-size:11px;text-transform:uppercase}}
.c b{{font-size:20px}}table{{width:100%;border-collapse:collapse;background:#fff}}td,th{{padding:8px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}}
</style></head><body><h1>Painel dos concorrentes</h1><div>coleta de {dia} · a cada 2 dias</div><div class="g">
{card("reels puxados", len(ultima))}{card("views somadas", fmt(sum(r["views"] or 0 for r in ultima)))}
{card("conta top", "@" + top[0])}{card("gancho top", html.escape((gancho or {}).get("abertura", "—")[:60]))}
</div><table><tr><th>Views</th><th>Perfil</th><th>Data</th><th>Abertura</th><th></th></tr>{linhas}</table></body></html>"""
    open(os.path.join(CONC, "painel.html"), "w", encoding="utf-8").write(doc)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--so-banco", action="store_true")
    a = ap.parse_args()
    dia = datetime.date.today().isoformat()
    cfg = json.load(open(os.path.join(CONC, "concorrentes.json"), encoding="utf-8"))
    if not a.so_banco:
        with ThreadPoolExecutor(4) as ex:
            def seguro(p):
                try:
                    return coletar_perfil(p, dia, cfg)
                except Exception as e:  # um perfil fora do ar não derruba a coleta
                    return p["usuario"], f"FALHOU ({e})"
            for usuario, msg in ex.map(seguro, cfg["perfis"]):
                print(f"  @{usuario}: {msg}", flush=True)
    reels = todos_reels()
    n = banco_ganchos(reels)
    painel(reels, dia)
    print(f"banco de ganchos: {n} aberturas · painel: 05-Concorrentes/painel.html")


if __name__ == "__main__":
    main()
