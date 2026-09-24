"""Colheita da manhã — fatos de fronteira (IA aplicada a negócio) das últimas 24-48h.

Puxa o Google News RSS (sem chave, sem cadastro) em várias consultas, remove repetidos e
imprime/ grava a lista para a peça de segunda (`À FRENTE`) e para o Registro do Amanhã.
O filtro final é humano/modelo: "e daí, para o dono de uma loja de R$ 200 mil/mês?".

uso:  python tools/roteiros/noticias.py [--horas 36] [--salvar]
      --salvar grava docs/conteudo/pautas/AAAA-MM-DD.md
"""
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAUTAS = os.path.join(RAIZ, "docs", "conteudo", "pautas")

# Consultas: o que interessa é IA VIRANDO ROTINA em empresa pequena, não release de laboratório
CONSULTAS = [
    ("agente de IA", '"AI agent" small business OR SMB OR agency'),
    ("IA no comercial", '"AI" sales team OR "sales agent" automation results'),
    ("IA substituindo tarefa", '"AI" replaced OR automated "customer service" OR bookkeeping OR scheduling'),
    ("empresa pequena com IA", '"one-person business" OR "solo founder" AI revenue'),
    ("custo/preço de IA", 'AI API price cut OR open source model release business'),
    ("Brasil", 'inteligência artificial empresa pequena OR PME resultado'),
]
UA = {"User-Agent": "Mozilla/5.0 (ARVEX colheita/1.0)"}
# fora: cripto, bolsa, geopolítica e release de laboratório — não respondem "e daí pro dono?"
BLOQUEIO = ("crypto", "bitcoin", "token", "blockchain", "web3", "nasdaq", "stock", "shares", "ipo",
            "beijing", "china's", "pentagon", "military", "lawsuit", "chip export", "nvidia earnings",
            "arc chain", "binary judgments", "memecoin")
# pontua o que indica IA virando ROTINA com resultado em empresa real
PESO = {"small business": 3, "smb": 3, "agency": 2, "solo": 3, "one-person": 3, "founder": 1,
        "replaced": 3, "automated": 2, "automation": 2, "saved": 2, "cut costs": 3, "revenue": 2,
        "customer service": 2, "sales team": 3, "bookkeeping": 2, "scheduling": 2, "hired": 2,
        "case study": 2, "price cut": 2, "open source": 2, "free tier": 2, "pme": 3, "pequena": 3,
        "resultado": 2, "faturamento": 3, "atendimento": 2, "clínica": 2, "loja": 2, "agente": 2}


def buscar(consulta, br=False):
    idioma = "pt-BR&gl=BR&ceid=BR:pt-419" if br else "en-US&gl=US&ceid=US:en"
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(consulta)}+when:2d&hl={idioma}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
            raiz = ElementTree.fromstring(r.read())
    except Exception as e:
        print(f"  (falhou: {consulta[:40]} — {e})")
        return []
    itens = []
    for it in raiz.iter("item"):
        titulo = (it.findtext("title") or "").strip()
        fonte = it.find("source")
        itens.append({
            "titulo": re.sub(r"\s+-\s+[^-]+$", "", titulo),
            "fonte": (fonte.text if fonte is not None else "?"),
            "link": (it.findtext("link") or "").strip(),
            "data": (it.findtext("pubDate") or "").strip(),
        })
    return itens


def quando(txt):
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            d = datetime.strptime(txt, fmt)
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def colher(horas=36):
    agora = datetime.now(timezone.utc)
    vistos, saida = set(), []
    for rotulo, consulta in CONSULTAS:
        for it in buscar(consulta, br=(rotulo == "Brasil")):
            chave = re.sub(r"\W+", "", it["titulo"].lower())[:60]
            d = quando(it["data"])
            if chave in vistos or not it["titulo"] or (d and agora - d > timedelta(hours=horas)):
                continue
            baixo = it["titulo"].lower()
            if any(b in baixo for b in BLOQUEIO):
                continue
            vistos.add(chave)
            it["tema"] = rotulo
            it["idade_h"] = round((agora - d).total_seconds() / 3600, 1) if d else None
            it["nota"] = sum(p for k, p in PESO.items() if k in baixo)
            saida.append(it)
    # melhor nota primeiro; empate desempata pelo mais recente
    saida.sort(key=lambda x: (-x["nota"], x["idade_h"] is None, x["idade_h"] or 999))
    return [x for x in saida if x["nota"] > 0][:20]


if __name__ == "__main__":
    horas = int(sys.argv[sys.argv.index("--horas") + 1]) if "--horas" in sys.argv else 36
    itens = colher(horas)
    linhas = [f"# Pautas da manhã — {datetime.now():%d/%m/%Y}", "",
              f"{len(itens)} fatos das últimas {horas}h. Filtro antes de virar roteiro:",
              "**e daí, para o dono de uma loja de R$ 200 mil por mês?** Se não responder, é notícia de tech.", ""]
    for i, it in enumerate(itens, 1):
        idade = f"{it['idade_h']}h" if it["idade_h"] is not None else "?"
        linhas.append(f"{i:>2}. **{it['titulo']}** · {it['fonte']} · {idade} · _{it['tema']}_")
        linhas.append(f"    {it['link']}")
    texto = "\n".join(linhas)
    print(texto)
    if "--salvar" in sys.argv:
        os.makedirs(PAUTAS, exist_ok=True)
        p = os.path.join(PAUTAS, f"{datetime.now():%Y-%m-%d}.md")
        open(p, "w", encoding="utf-8").write(texto + "\n")
        print("\nsalvo em", os.path.relpath(p, RAIZ))
