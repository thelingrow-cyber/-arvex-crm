"""Instagram do Vitor via Zernio (API oficial da Meta).

Leitura:
  python tools/maquina/insta.py contas
  python tools/maquina/insta.py posts [N] [--ordem date|views|reach|saves|shares|ig_reels_avg_watch_time] [--dias 90] [--json]
  python tools/maquina/insta.py seguidores [dias]
  python tools/maquina/insta.py fila                       # o que está agendado
Escrita (só depois do "pode" do Vitor no WhatsApp, que é o APROVADO dele):
  python tools/maquina/insta.py agendar <video.mp4> <legenda.txt> [--quando "2026-10-23 19:00"] [--teste]
  python tools/maquina/insta.py cancelar <id do post>

Chave: variável de usuário ZERNIO_API_KEY (nunca no chat nem em arquivo).
Regras (guia Fabiano + Meta): ritmo humano, sem varrer perfil de terceiro, escrita só com aprovação.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://zernio.com/api/v1"
CONTA_IG = "6ada8cccf527246cdb4441da"  # @vitorsimoesb


def _env(nome):
    # o valor gravado no Windows vem primeiro: terminal aberto antes do gravar carrega o valor velho
    v = subprocess.run(["powershell", "-NoProfile", "-c", f"[Environment]::GetEnvironmentVariable('{nome}','User')"],
                       capture_output=True, text=True).stdout.strip() or os.environ.get(nome)
    if not v:
        sys.exit(f"falta a variável de usuário {nome}")
    return v


FUSO = dt.timezone(dt.timedelta(hours=-3))  # Brasília (sem horário de verão desde 2019)
# Seguidores online (Zernio /online-followers, set–out/26): platô das 12h às 22h, pico perto das 20h.
# O /best-time não serve: puxado por 2 virais (29/09 e 02/10). Rever quando houver mais posts pela Zernio.
HORARIOS = (12, 19, 21)
FOLGA_MIN = 90       # não agenda para menos de 1h30 a partir de agora (dá tempo de cancelar)


def _req(metodo, caminho, corpo=None, **params):
    q = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(f"{API}{caminho}" + (f"?{q}" if q else ""), data=dados, method=metodo,
                                 headers={"Authorization": f"Bearer {_env('ZERNIO_API_KEY')}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            txt = r.read().decode() or "{}"
            return json.loads(txt)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Zernio {metodo} {caminho} → {e.code}: {e.read().decode()[:400]}") from None


def get(caminho, **params):
    return _req("GET", caminho, **params)


# ---------- publicação ----------
def subir(arquivo):
    """Sobe o vídeo para a Zernio (URL pré-assinada) e devolve a URL pública que o post usa."""
    tam = os.path.getsize(arquivo)
    p = _req("POST", "/media/presign", {"filename": os.path.basename(arquivo), "contentType": "video/mp4", "size": tam})
    with open(arquivo, "rb") as f:                       # streaming: a máquina tem pouca RAM livre
        req = urllib.request.Request(p["uploadUrl"], data=f, method="PUT",
                                     headers={"Content-Type": "video/mp4", "Content-Length": str(tam)})
        urllib.request.urlopen(req, timeout=900).read()
    return p["publicUrl"]


def fila():
    d = get("/posts", status="scheduled", platform="instagram", limit=100)
    return sorted(d.get("posts", []), key=lambda p: p.get("scheduledFor") or "")


def proximo_horario(agora=None):
    """Primeiro horário de HORARIOS livre na fila, com pelo menos FOLGA_MIN de antecedência."""
    agora = agora or dt.datetime.now(FUSO)
    ocupados = set()
    for p in fila():
        if p.get("scheduledFor"):
            t = dt.datetime.fromisoformat(p["scheduledFor"].replace("Z", "+00:00")).astimezone(FUSO)
            ocupados.add((t.date(), t.hour))
    for d in range(0, 30):
        dia = (agora + dt.timedelta(days=d)).date()
        for h in HORARIOS:
            t = dt.datetime(dia.year, dia.month, dia.day, h, tzinfo=FUSO)
            if t >= agora + dt.timedelta(minutes=FOLGA_MIN) and (dia, h) not in ocupados:
                return t
    raise RuntimeError("fila cheia pelos próximos 30 dias")


def agendar(video, legenda, quando=None, teste=False):
    """Agenda um reel. `quando` = datetime com fuso (None = próximo horário livre). teste=True: valida sem criar."""
    if len(legenda) > 2200:
        raise ValueError(f"legenda com {len(legenda)} caracteres (o Instagram aceita 2200)")
    quando = quando or proximo_horario()
    url = subir(video)
    corpo = {"content": legenda, "mediaItems": [{"type": "video", "url": url}],
             "platforms": [{"platform": "instagram", "accountId": CONTA_IG,
                            "platformSpecificData": {"shareToFeed": True}}],
             "scheduledFor": quando.isoformat(), "timezone": "America/Sao_Paulo"}
    if teste:                                            # dryRun da Zernio só vale para TikTok: rascunho nunca publica
        corpo["isDraft"] = True
        corpo.pop("scheduledFor")
    r = _req("POST", "/posts", corpo)
    post = r.get("post") or r
    if teste and post.get("_id"):
        _req("DELETE", f"/posts/{post['_id']}")          # apaga o rascunho do teste
    return {"id": post.get("_id"), "quando": quando, "status": post.get("status"), "resposta": r if teste else None}


def cancelar(post_id):
    return _req("DELETE", f"/posts/{post_id}")


def situacao(post_id):
    """status do post (scheduled, published, failed…) e o link no Instagram, quando já saiu."""
    p = get(f"/posts/{post_id}")
    p = p.get("post") or p
    pl = (p.get("platforms") or [{}])[0]
    return {"status": p.get("status"), "url": pl.get("platformPostUrl"), "erro": pl.get("errorMessage")}


def quando_br(t):
    dias = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
    return f"{dias[t.weekday()]} {t:%d/%m} às {t:%H}h"


def posts(n=20, ordem="date", dias=90):
    desde = (dt.date.today() - dt.timedelta(days=dias)).isoformat()
    d = get("/analytics", accountId=CONTA_IG, limit=min(n, 100), sortBy=ordem, order="desc", fromDate=desde)
    out = []
    for p in d.get("posts", []):
        a = p.get("analytics") or {}
        out.append({
            "data": (p.get("publishedAt") or "")[:10],
            "url": p.get("platformPostUrl"),
            "dur_s": a.get("videoDurationSeconds"),
            "views": a.get("views"), "alcance": a.get("reach"),
            "assist_media_s": round((a.get("igReelsAvgWatchTime") or 0) / 1000, 1),
            "pulo_pct": a.get("reelsSkipRate"),
            "salv": a.get("saves"), "compart": a.get("shares"),
            "curt": a.get("likes"), "coment": a.get("comments"),
            "seguiu": a.get("follows"),
        })
    return out


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd = args.pop(0)
    if cmd == "contas":
        for c in get("/accounts").get("accounts", []):
            print(c.get("_id"), c.get("platform"), c.get("username"), "ativa" if c.get("isActive") else "INATIVA")
    elif cmd == "posts":
        ordem = args[args.index("--ordem") + 1] if "--ordem" in args else "date"
        dias = int(args[args.index("--dias") + 1]) if "--dias" in args else 90
        n = int(args[0]) if args and args[0].isdigit() else 20
        linhas = posts(n, ordem, dias)
        if "--json" in args:
            print(json.dumps(linhas, ensure_ascii=False, indent=1))
            return
        print(f"{'data':10} {'dur':>4} {'views':>7} {'alc':>7} {'assist':>6} {'pulo':>4} {'salv':>4} {'comp':>4} {'curt':>5} {'com':>4}  url")
        for l in linhas:
            print(f"{l['data']:10} {l['dur_s'] or 0:>4} {l['views'] or 0:>7} {l['alcance'] or 0:>7} {l['assist_media_s']:>6} "
                  f"{l['pulo_pct'] or 0:>4} {l['salv'] or 0:>4} {l['compart'] or 0:>4} {l['curt'] or 0:>5} {l['coment'] or 0:>4}  {l['url']}")
    elif cmd == "seguidores":
        dias = int(args[0]) if args else 30
        desde = (dt.date.today() - dt.timedelta(days=dias)).isoformat()
        print(json.dumps(get("/analytics/instagram/follower-history", accountId=CONTA_IG, fromDate=desde,
                             metricType="total_value"), ensure_ascii=False, indent=1))
    elif cmd == "fila":
        for p in fila():
            t = dt.datetime.fromisoformat(p["scheduledFor"].replace("Z", "+00:00")).astimezone(FUSO)
            print(p.get("_id"), quando_br(t), (p.get("content") or "").split("\n")[0][:60])
        print(f"próximo horário livre: {quando_br(proximo_horario())}")
    elif cmd == "agendar":
        video, leg = args[0], open(args[1], encoding="utf-8").read().strip()
        quando = None
        if "--quando" in args:
            quando = dt.datetime.strptime(args[args.index("--quando") + 1], "%Y-%m-%d %H:%M").replace(tzinfo=FUSO)
        r = agendar(video, leg, quando, teste="--teste" in args)
        print(("TESTE (rascunho criado e apagado) " if "--teste" in args else "agendado ") + f"{r['id']} · {quando_br(r['quando'])}")
        if r["resposta"]:
            print(json.dumps(r["resposta"], ensure_ascii=False)[:800])
    elif cmd == "cancelar":
        print(cancelar(args[0]))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
