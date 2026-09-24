"""Gera imagem ou vídeo via Kie.ai e salva o arquivo no projeto.

Cria a task, acompanha até terminar, baixa o resultado para output/midia/AAAA-MM-DD/ e registra
o custo real (créditos antes × depois) em output/midia/ledger.jsonl.

uso:  python .claude/skills/kieai/scripts/gerar.py --modelo imagem --prompt "..." [--params '{"aspect_ratio":"9:16"}'] [--nome slug]
      python .claude/skills/kieai/scripts/gerar.py --saldo
"""
import argparse, datetime, json, os, re, subprocess, sys, time, urllib.error, urllib.request

API = "https://api.kie.ai/api/v1"
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
SAIDA = os.path.join(RAIZ, "output", "midia")

# Apelido → (model id no Kie, parâmetros padrão). Para outro modelo do catálogo, passe o id direto em --modelo.
MODELOS = {
    "imagem": ("google/nano-banana", {"aspect_ratio": "1:1", "output_format": "png"}),
    "video": ("bytedance/seedance-2", {"resolution": "480p", "aspect_ratio": "9:16", "duration": 5,
                                       "generate_audio": False}),
}


def chave():
    k = os.environ.get("KIEAI_API_KEY")
    if not k and os.name == "nt":  # setx só vale para processos novos; lê direto do registro do usuário
        k = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "[Environment]::GetEnvironmentVariable('KIEAI_API_KEY','User')"],
                           capture_output=True, text=True).stdout.strip()
    if not k:
        sys.exit("KIEAI_API_KEY não encontrada. No PowerShell: setx KIEAI_API_KEY \"sua-chave\" (nunca colar no chat).")
    return k


def http(metodo, caminho, corpo=None):
    req = urllib.request.Request(API + caminho, method=metodo,
                                 data=json.dumps(corpo).encode() if corpo is not None else None,
                                 headers={"Authorization": f"Bearer {chave()}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            res = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit({401: "HTTP 401 — chave inválida.", 402: "HTTP 402 — sem créditos (kie.ai → Cobrança)."}
                 .get(e.code, f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')}"))
    except urllib.error.URLError as e:
        sys.exit(f"Erro de rede: {e}")
    if res.get("code") != 200:
        sys.exit(f"Kie.ai recusou: {res.get('msg')}")
    return res.get("data")


def saldo():
    return http("GET", "/chat/credit")


def acompanhar(task_id, limite_s):
    inicio, ultimo = time.time(), None
    while time.time() - inicio < limite_s:
        time.sleep(5)
        d = http("GET", f"/jobs/recordInfo?taskId={task_id}")
        estado = d.get("state")
        if estado != ultimo:
            print(f"  estado: {estado}", file=sys.stderr, flush=True)
            ultimo = estado
        if estado == "success":
            return json.loads(d.get("resultJson") or "{}").get("resultUrls") or []
        if estado == "fail":
            sys.exit(f"Geração falhou: {d.get('failCode')} {d.get('failMsg')}")
    sys.exit(f"Tempo esgotado ({limite_s}s). taskId {task_id} — dá para consultar depois em kie.ai → Logs.")


def slug(t):
    return "-".join(re.findall(r"[a-z0-9]+", t.lower())[:6]) or "midia"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--modelo", help="apelido (imagem, video) ou id do Kie (ex.: google/nano-banana)")
    p.add_argument("--prompt")
    p.add_argument("--params", default="{}", help="JSON com parâmetros extras do modelo")
    p.add_argument("--nome", help="slug do arquivo de saída")
    p.add_argument("--saldo", action="store_true", help="só mostra os créditos")
    a = p.parse_args()

    if a.saldo:
        print(json.dumps({"creditos": saldo()}))
        return
    if not (a.modelo and a.prompt):
        p.error("--modelo e --prompt são obrigatórios")

    modelo, padrao = MODELOS.get(a.modelo, (a.modelo, {}))
    entrada = {**padrao, **json.loads(a.params), "prompt": a.prompt}

    antes = saldo()
    print(f"→ {modelo} (saldo {antes})", file=sys.stderr, flush=True)
    task_id = http("POST", "/jobs/createTask", {"model": modelo, "input": entrada})["taskId"]
    urls = acompanhar(task_id, 600 if "video" in a.modelo or "seedance" in modelo else 300)

    pasta = os.path.join(SAIDA, datetime.date.today().isoformat())
    os.makedirs(pasta, exist_ok=True)
    base, arquivos = f"{datetime.datetime.now():%H%M%S}-{a.nome or slug(a.prompt)}", []
    for i, url in enumerate(urls):
        ext = os.path.splitext(url.split("?")[0])[1] or ".bin"
        destino = os.path.join(pasta, f"{base}{'-' + str(i + 1) if len(urls) > 1 else ''}{ext}")
        urllib.request.urlretrieve(url, destino)
        arquivos.append(os.path.relpath(destino, RAIZ).replace("\\", "/"))

    depois = saldo()
    registro = {"quando": datetime.datetime.now().isoformat(timespec="seconds"), "modelo": modelo,
                "entrada": entrada, "taskId": task_id, "creditos": round(antes - depois, 2),
                "saldo": depois, "arquivos": arquivos}
    with open(os.path.join(SAIDA, "ledger.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    print(json.dumps(registro, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
