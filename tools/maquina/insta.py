"""Instagram do Vitor via Zernio (API oficial da Meta). SÓ LEITURA.

Uso:
  python tools/maquina/insta.py contas
  python tools/maquina/insta.py posts [N] [--ordem date|views|reach|saves|shares|ig_reels_avg_watch_time] [--dias 90] [--json]
  python tools/maquina/insta.py seguidores [dias]

Chave: variável de usuário ZERNIO_API_KEY (nunca no chat nem em arquivo).
Regras (guia Fabiano + Meta): ritmo humano, sem varrer perfil de terceiro, nada de escrita aqui.
Publicar/responder ficará em outro comando, sempre com APROVADO do Vitor.
"""
import datetime as dt
import json
import os
import subprocess
import sys
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


def get(caminho, **params):
    q = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(f"{API}{caminho}?{q}", headers={"Authorization": f"Bearer {_env('ZERNIO_API_KEY')}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


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
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
