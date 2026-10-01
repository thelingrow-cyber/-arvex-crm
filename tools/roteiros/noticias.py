"""Colheita da manhã — fatos de fronteira (IA aplicada a negócio) das últimas 24-48h.

v2 (2026-10-01): além do Google News, lê as fontes primárias e o que está viralizando:
  - blogs oficiais: OpenAI, Anthropic (página /news), Google, DeepMind, Meta
  - imprensa tech: TechCrunch IA, The Verge IA
  - imprensa de negócio BR: Exame, Valor, NeoFeed, Startups (filtrado por IA)
  - viral: Hacker News (pontos), Reddit (top do dia em 5 subs)
  - X: só se existir APIFY_TOKEN no ambiente (API oficial do X é paga; Nitter morreu)
Agrupa a mesma história e conta quantos veículos cobriram — 9 matérias do mesmo fato viram
1 item com "9 veículos", que é sinal de história grande e não ruído.

O filtro final é humano/modelo: "e daí, para o dono de uma loja de R$ 200 mil/mês?".

uso:  python tools/roteiros/noticias.py [--horas 36] [--salvar]
      --salvar grava docs/conteudo/pautas/AAAA-MM-DD.md
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAUTAS = os.path.join(RAIZ, "docs", "conteudo", "pautas")

# Consultas: o que interessa é IA VIRANDO ROTINA em empresa pequena, não release de laboratório
CONSULTAS = [
    ("agente de IA", '"AI agent" small business OR SMB OR agency'),
    ("IA no comercial", '"AI" sales team OR "sales agent" automation results'),
    ("IA substituindo tarefa", '"AI" replaced OR automated "customer service" OR bookkeeping OR scheduling'),
    ("empresa pequena com IA", '"one-person business" OR "solo founder" AI revenue'),
    ("custo/preço de IA", 'AI API price cut OR open source model release business'),
    # v1 trazia turismo ("PME resultado" sem IA); agora a IA é obrigatória na consulta
    ("Brasil", '"inteligência artificial" (empresa OR PME OR negócio OR varejo)'),
]

# (rótulo, url, tipo, filtrar_por_IA)
FEEDS = [
    ("OpenAI", "https://openai.com/news/rss.xml", "oficial", False),
    ("Google", "https://blog.google/technology/ai/rss/", "oficial", False),
    ("DeepMind", "https://deepmind.google/blog/rss.xml", "oficial", False),
    ("Meta", "https://about.fb.com/news/feed/", "oficial", True),
    ("TechCrunch", "https://techcrunch.com/category/artificial-intelligence/feed/", "tech", False),
    ("The Verge", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "tech", False),
    ("Exame", "https://exame.com/feed/", "brasil", True),
    ("Valor", "https://valor.globo.com/rss/valor", "brasil", True),
    ("NeoFeed", "https://neofeed.com.br/feed/", "brasil", True),
    ("Startups", "https://startups.com.br/feed/", "brasil", True),
]
SUBREDDITS = ["artificial", "OpenAI", "ClaudeAI", "singularity", "smallbusiness"]
X_BUSCAS = ['("AI agent" OR "AI employee") (business OR sales OR customers) min_faves:300 lang:en',
            '("inteligência artificial" OR "IA") (empresa OR negócio) min_faves:100 lang:pt']

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
E_IA = re.compile(r"\b(IA|AI|A\.I\.)\b|intelig[êe]ncia artificial|artificial intelligence|chatgpt|openai|"
                  r"anthropic|claude|gemini|llm|agente|agent|automa", re.I)
# fora: cripto, bolsa, geopolítica e release de laboratório — não respondem "e daí pro dono?"
BLOQUEIO = ("crypto", "bitcoin", "token", "blockchain", "web3", "nasdaq", "stock", "shares", "ipo",
            "beijing", "china's", "pentagon", "military", "lawsuit", "chip export", "nvidia earnings",
            "arc chain", "binary judgments", "memecoin", "bolsa", "ibovespa", "dólar", "copom")
# pontua o que indica IA virando ROTINA com resultado em empresa real
PESO = {"small business": 3, "smb": 3, "agency": 2, "solo": 3, "one-person": 3, "founder": 1,
        "replaced": 3, "automated": 2, "automation": 2, "saved": 2, "cut costs": 3, "revenue": 2,
        "customer service": 2, "sales team": 3, "bookkeeping": 2, "scheduling": 2, "hired": 2,
        "case study": 2, "price cut": 2, "open source": 2, "free tier": 2, "pme": 3, "pequena": 3,
        "resultado": 2, "faturamento": 3, "atendimento": 2, "clínica": 2, "loja": 2, "agente": 2,
        "agent": 1, "layoff": 2, "demiss": 2, "empleo": 1, "jobs": 1, "varejo": 2, "vendas": 2}
BONUS_TIPO = {"oficial": 3, "viral": 2, "brasil": 2, "tech": 1, "google": 0, "x": 2}
STOP = set("that this with from your about into have will their what when they more than after over "
           "como para pelo pela mais sobre entre seus suas está estão também será uma uns umas the and "
           "for are new says said could just".split())


def _get(url, timeout=20):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def _data(txt):
    if not txt:
        return None
    try:
        d = parsedate_to_datetime(txt)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(txt.replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _item(titulo, fonte, link, data, tipo, tema, extra=0, sinal=""):
    titulo = html.unescape(re.sub(r"\s+", " ", titulo or "")).strip()
    return {"titulo": titulo, "fonte": fonte, "link": link, "data": data, "tipo": tipo,
            "tema": tema, "extra": extra, "sinal": sinal}


def _rss(xml_bytes):
    """Lê RSS 2.0 e Atom; devolve (titulo, link, data)."""
    raiz = ElementTree.fromstring(xml_bytes)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for it in raiz.iter("item"):
        yield it.findtext("title"), (it.findtext("link") or "").strip(), _data(it.findtext("pubDate"))
    for it in raiz.iter("{http://www.w3.org/2005/Atom}entry"):
        lk = it.find("a:link", ns)
        yield (it.findtext("a:title", namespaces=ns), lk.get("href") if lk is not None else "",
               _data(it.findtext("a:updated", namespaces=ns) or it.findtext("a:published", namespaces=ns)))


# ---------------------------------------------------------------- fontes

def google_news(rotulo, consulta):
    br = rotulo == "Brasil"
    idioma = "pt-BR&gl=BR&ceid=BR:pt-419" if br else "en-US&gl=US&ceid=US:en"
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(consulta)}+when:2d&hl={idioma}"
    raiz = ElementTree.fromstring(_get(url))
    out = []
    for it in raiz.iter("item"):
        fonte = it.find("source")
        titulo = re.sub(r"\s+-\s+[^-]+$", "", (it.findtext("title") or "").strip())
        out.append(_item(titulo, fonte.text if fonte is not None else "?", (it.findtext("link") or "").strip(),
                         _data(it.findtext("pubDate")), "brasil" if br else "google", rotulo))
    return out


def feed(rotulo, url, tipo, so_ia):
    out = []
    for titulo, link, d in _rss(_get(url)):
        if so_ia and not E_IA.search(titulo or ""):
            continue
        out.append(_item(titulo, rotulo, link, d, tipo, tipo))
    return out


def anthropic():
    """Sem RSS: lê /news e casa cada link com a data <time> que vem logo depois."""
    pagina = _get("https://www.anthropic.com/news").decode("utf-8", "ignore")
    out, vistos = [], set()
    for m in re.finditer(r'href="/news/([a-z0-9-]+)"', pagina):
        slug = m.group(1)
        if slug in vistos:
            continue
        vistos.add(slug)
        t = re.search(r"<time[^>]*>([^<]+)</time>", pagina[m.end():m.end() + 3000])
        d = None
        if t:
            try:
                d = datetime.strptime(t.group(1).strip(), "%b %d, %Y").replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        out.append(_item(slug.replace("-", " ").capitalize(), "Anthropic",
                         f"https://www.anthropic.com/news/{slug}", d, "oficial", "oficial"))
    return out


def hacker_news(horas):
    desde = int(time.time()) - horas * 3600
    url = ("https://hn.algolia.com/api/v1/search?tags=story&hitsPerPage=40"
           f"&query=AI&numericFilters=created_at_i>{desde},points>80")
    out = []
    for h in json.loads(_get(url))["hits"]:
        pts = h.get("points") or 0
        out.append(_item(h.get("title"), "Hacker News", h.get("url") or
                         f"https://news.ycombinator.com/item?id={h['objectID']}",
                         _data(h.get("created_at")), "viral", "viral",
                         extra=min(pts // 100, 6), sinal=f"{pts} pts HN"))
    return out


def reddit(sub):
    out = []
    for pos, (titulo, link, d) in enumerate(_rss(_get(f"https://www.reddit.com/r/{sub}/top/.rss?t=day"))):
        if sub == "smallbusiness" and not E_IA.search(titulo or ""):
            continue
        # o feed de top já vem ordenado por votos: o 1º do dia vale mais
        out.append(_item(titulo, f"r/{sub}", link, d, "viral", "viral",
                         extra=max(4 - pos, 0), sinal=f"top {pos + 1} r/{sub}"))
    return out[:8]


def reddit_todos():
    """Em sequência e com pausa: em paralelo o Reddit devolve 429 a partir do 2º sub."""
    out = []
    for i, sub in enumerate(SUBREDDITS):
        if i:
            time.sleep(2.5)
        try:
            out += reddit(sub)
        except Exception as e:
            print(f"  (r/{sub} falhou: {str(e)[:40]})", file=sys.stderr)
    return out


def x_apify(horas):
    """Busca no X via Apify (tweet scraper). Só roda com APIFY_TOKEN; custo ~US$ 0,40 / 1.000 posts."""
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        return None
    desde = (datetime.now(timezone.utc) - timedelta(hours=horas)).strftime("%Y-%m-%d")
    corpo = json.dumps({"searchTerms": [f"{b} since:{desde}" for b in X_BUSCAS],
                        "sort": "Top", "maxItems": 40}).encode()
    url = f"https://api.apify.com/v2/acts/apidojo~tweet-scraper/run-sync-get-dataset-items?token={token}"
    req = urllib.request.Request(url, data=corpo, headers={"Content-Type": "application/json", **UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        posts = json.loads(r.read())
    out = []
    for p in posts:
        likes = p.get("likeCount") or 0
        autor = (p.get("author") or {}).get("userName", "?")
        texto = (p.get("text") or "").split("\n")[0][:160]
        out.append(_item(texto, f"X @{autor}", p.get("url") or "", _data(p.get("createdAt")),
                         "x", "x", extra=min(likes // 500, 6), sinal=f"{likes} likes X"))
    return out


# ---------------------------------------------------------------- agrupar e pontuar

def _palavras(titulo):
    return {w for w in re.findall(r"[a-zà-ú0-9]{4,}", titulo.lower()) if w not in STOP}


def agrupar(itens):
    """Mesma história em veículos diferentes vira 1 grupo (≥3 palavras em comum ou Jaccard ≥ 0,35)."""
    grupos = []
    for it in itens:
        p = _palavras(it["titulo"])
        for g in grupos:
            comum = len(p & g["palavras"])
            if comum >= 3 or (p and comum / len(p | g["palavras"]) >= 0.35):
                g["itens"].append(it)
                g["palavras"] |= p
                break
        else:
            grupos.append({"itens": [it], "palavras": set(p)})
    return grupos


def colher(horas=36):
    agora = datetime.now(timezone.utc)
    tarefas = [(f"Google: {r}", google_news, (r, c)) for r, c in CONSULTAS]
    tarefas += [(r, feed, (r, u, t, f)) for r, u, t, f in FEEDS]
    tarefas += [("Anthropic", anthropic, ()), ("Hacker News", hacker_news, (horas,))]
    tarefas += [("Reddit", reddit_todos, ())]
    tarefas += [("X", x_apify, (horas,))]

    brutos, status = [], {}
    with ThreadPoolExecutor(max_workers=10) as ex:
        futuros = {nome: ex.submit(fn, *args) for nome, fn, args in tarefas}
        for nome, fut in futuros.items():
            try:
                res = fut.result()
                status[nome] = "sem APIFY_TOKEN" if res is None else len(res)
                brutos += res or []
            except Exception as e:
                status[nome] = f"falhou ({str(e)[:40]})"

    validos = []
    for it in brutos:
        d, baixo = it["data"], it["titulo"].lower()
        # oficial sem data entra (a Anthropic às vezes não expõe); o resto precisa estar na janela
        if not it["titulo"] or (d and agora - d > timedelta(hours=horas)) or (d is None and it["tipo"] != "oficial"):
            continue
        if any(b in baixo for b in BLOQUEIO):
            continue
        it["idade_h"] = round((agora - d).total_seconds() / 3600, 1) if d else None
        it["nota"] = sum(p for k, p in PESO.items() if k in baixo) + BONUS_TIPO[it["tipo"]] + it["extra"]
        validos.append(it)

    grupos = []
    for g in agrupar(validos):
        g["itens"].sort(key=lambda x: (-x["nota"], x["idade_h"] or 999))
        fontes = {x["fonte"] for x in g["itens"]}
        g["veiculos"] = len(fontes)
        g["tipos"] = {x["tipo"] for x in g["itens"]}
        g["nota"] = g["itens"][0]["nota"] + 2 * min(g["veiculos"] - 1, 4) + (2 if len(g["tipos"]) > 1 else 0)
        grupos.append(g)
    grupos.sort(key=lambda g: -g["nota"])
    return [g for g in grupos if g["nota"] > 1], status


# ---------------------------------------------------------------- saída

def _linha(i, g):
    top = g["itens"][0]
    idade = f"{top['idade_h']}h" if top["idade_h"] is not None else "?"
    veic = f" · **{g['veiculos']} veículos**" if g["veiculos"] > 1 else ""
    sinais = ", ".join(sorted({x["sinal"] for x in g["itens"] if x["sinal"]}))
    sinais = f" · 🔥 {sinais}" if sinais else ""
    return [f"{i:>2}. **{top['titulo']}** · {top['fonte']} · {idade}{veic}{sinais}", f"    {top['link']}"]


def montar(grupos, status, horas):
    secoes = [
        ("🔥 Histórias grandes — 3+ veículos ou viral + imprensa",
         lambda g: g["veiculos"] >= 3 or ("viral" in g["tipos"] and len(g["tipos"]) > 1)),
        ("🏢 Fonte oficial — o que as empresas anunciaram", lambda g: "oficial" in g["tipos"]),
        ("📈 Viralizando — HN, Reddit, X", lambda g: g["tipos"] & {"viral", "x"}),
        ("🇧🇷 Brasil", lambda g: "brasil" in g["tipos"]),
        ("📰 Resto da imprensa", lambda g: True),
    ]
    limites = [8, 6, 8, 6, 8]
    linhas = [f"# Pautas da manhã — {datetime.now():%d/%m/%Y}", "",
              f"Janela: últimas {horas}h. Filtro antes de virar roteiro:",
              "**e daí, para o dono de uma loja de R$ 200 mil por mês?** Se não responder, é notícia de tech.",
              "Toda notícia escolhida é conferida na **fonte primária** antes do roteiro.", ""]
    usados, n = set(), 0
    for (titulo, cond), lim in zip(secoes, limites):
        sel = [g for g in grupos if id(g) not in usados and cond(g)][:lim]
        if not sel:
            continue
        linhas += [f"## {titulo}", ""]
        for g in sel:
            usados.add(id(g))
            n += 1
            linhas += _linha(n, g)
        linhas.append("")
    linhas += ["---", "", "**Fontes desta colheita:** " +
               " · ".join(f"{k} {v}" for k, v in status.items())]
    return "\n".join(linhas)


if __name__ == "__main__":
    horas = int(sys.argv[sys.argv.index("--horas") + 1]) if "--horas" in sys.argv else 36
    grupos, status = colher(horas)
    texto = montar(grupos, status, horas)
    print(texto)
    if "--salvar" in sys.argv:
        os.makedirs(PAUTAS, exist_ok=True)
        p = os.path.join(PAUTAS, f"{datetime.now():%Y-%m-%d}.md")
        open(p, "w", encoding="utf-8").write(texto + "\n")
        print("\nsalvo em", os.path.relpath(p, RAIZ))
