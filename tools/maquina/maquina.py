"""Máquina de conteúdo: orquestra as etapas que usam IA. Um Claude por etapa, uma página por trabalho.

Cada etapa é uma chamada nova de `claude -p`, que só enxerga a página dela (docs/conteudo/maquina/_paginas/)
e os arquivos que a mensagem aponta. As etapas não conversam: cada uma deixa um arquivo para a próxima.

uso:
  python tools/maquina/maquina.py temas                       # 2 · lista temas novos em 01-Ideias
  python tools/maquina/maquina.py roteiro 12 [13 14 …]        # 4+5 · roteiro + checagem de voz + revisor (até 2 voltas)
  python tools/maquina/maquina.py reescrever <pasta> "nota"   # 6 · o Vitor não curtiu: reescreve com a nota dele
  python tools/maquina/maquina.py corte <pasta>               # 8 · bruto/ → vídeo limpo (limpar.cjs: última tentativa, sem pausas)
  python tools/maquina/maquina.py edicao <pasta>              # 9 · plano de legenda e animações + CREDITOS.txt
  python tools/maquina/maquina.py legenda <pasta>             # 10 · capas + código + guia.md (material do direct) + legenda.txt
  python tools/maquina/maquina.py arquivar <pasta> [--limpar] # 11 · move para 03-Publicados (--limpar apaga o bruto)
  python tools/maquina/maquina.py status                      # rascunhos e veredito de cada um
"""
import datetime, glob, json, os, re, shutil, subprocess, sys, unicodedata
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
from checar_voz import relatorio  # noqa: E402

MAQ = os.path.join(RAIZ, "docs", "conteudo", "maquina")
PAG = os.path.join(MAQ, "_paginas")
TEMAS = os.path.join(MAQ, "01-Ideias", "TEMAS-NAO-COBERTOS.md")
RASC = os.path.join(MAQ, "02-Rascunhos")
PUBL = os.path.join(MAQ, "03-Publicados")
VOLTAS = 2
rel = lambda p: os.path.relpath(p, RAIZ).replace("\\", "/")


def claude(pagina, mensagem, web=False, modelo="opus"):
    """Uma sessão nova: a página + a mensagem. Devolve só o texto da resposta."""
    corpo = open(os.path.join(PAG, f"{pagina}.md"), encoding="utf-8").read()
    prompt = (f"{corpo}\n\n---\n\n# Mensagem desta execução\n\n{mensagem}\n\n"
              "Abra com a ferramenta Read todos os arquivos que a página e a mensagem apontam antes de responder. "
              "Responda só com o conteúdo pedido, sem comentário antes ou depois.")
    ferramentas = ["Read", "Glob", "Grep"] + (["WebSearch", "WebFetch"] if web else [])
    r = subprocess.run(["claude.cmd", "-p", "--model", modelo, "--allowedTools", *ferramentas],
                       input=prompt, capture_output=True, text=True, encoding="utf-8", cwd=RAIZ, timeout=1800)
    saida = r.stdout.strip()
    if r.returncode or not saida:
        raise RuntimeError(f"claude falhou na página {pagina}: {r.stderr[-400:]}")
    m = re.fullmatch(r"```(?:markdown|md)?\n(.*)\n```", saida, re.S)  # tira a cerca externa, se vier
    return m.group(1).strip() if m else saida


def slug(t, n=5):
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return "-".join([p for p in re.findall(r"[a-z0-9]+", t) if len(p) > 2][:n]) or "sem-titulo"


# ---------- 2 · temas ----------
def temas():
    coletas = sorted(glob.glob(os.path.join(MAQ, "05-Concorrentes", "coletas", "*")))
    if not coletas:
        sys.exit("sem coleta: rode antes  python tools/maquina/coletar.py")
    if not os.path.exists(TEMAS):
        open(TEMAS, "w", encoding="utf-8").write(
            "# Temas que eu não cobri\n\n> Gerado pela etapa 2 (`maquina.py temas`). Para escrever: "
            "`python tools/maquina/maquina.py roteiro <N>`.\n\n"
            "| N | Tema (a tese, em uma frase dele) | Molde | Estilo de gancho | Veio de | Views |\n"
            "|---|---|---|---|---|---|\n")
    atual = open(TEMAS, encoding="utf-8").read()
    ultimo = max([int(n) for n in re.findall(r"^\| (\d+) \|", atual, re.M)] or [0])
    msg = (f"Coleta mais recente: `{rel(coletas[-1])}/` (um JSON por perfil). "
           f"Lista atual: `{rel(TEMAS)}` (o último número é {ultimo}, comece em {ultimo + 1}).")
    linhas = [l for l in claude("temas", msg).splitlines() if re.match(r"^\| \d+ \|", l.strip())]
    with open(TEMAS, "a", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print(f"{len(linhas)} temas novos em {rel(TEMAS)}")
    for l in linhas:
        print("  " + l[:150])


def linha_tema(n):
    for l in open(TEMAS, encoding="utf-8"):
        if re.match(rf"^\| {n} \|", l):
            return l.strip()
    sys.exit(f"tema {n} não está em {rel(TEMAS)}")


# ---------- 4 + 5 · roteiro e revisão ----------
def revisar(pasta):
    """Checagem de voz (script) + revisor novo. Até VOLTAS reescritas automáticas."""
    rot = os.path.join(pasta, "roteiro.md")
    hist = []
    for volta in range(VOLTAS + 1):
        texto = open(rot, encoding="utf-8").read()
        voz, _ = relatorio(texto)
        parecer = claude("revisor", f"Resultado do `checar_voz.py`:\n\n{voz}\n\nO roteiro (`{rel(rot)}`):\n\n{texto}")
        hist.append(f"## Volta {volta + 1}\n\n{voz}\n\n{parecer}\n")
        aprovado = "VEREDITO: APROVADO" in parecer.upper()
        escalado = "VEREDITO: ESCALAR" in parecer.upper()
        if aprovado or escalado or volta == VOLTAS:
            break
        shutil.copy(rot, os.path.join(pasta, f"roteiro-v{volta + 1}.md"))
        novo = claude("roteiro", f"Reescreva o roteiro abaixo aplicando TODAS as correções do revisor.\n\n"
                      f"## Correções do revisor\n\n{voz}\n\n{parecer}\n\n## Roteiro atual\n\n{texto}", web=True)
        open(rot, "w", encoding="utf-8").write(novo + "\n")
    veredito = ("APROVADO" if aprovado else "ESCALADO PARA O VITOR (ver revisao.md)" if escalado
                else "REFAZER (esgotou as voltas: o Vitor decide)")
    open(os.path.join(pasta, "revisao.md"), "w", encoding="utf-8").write(
        f"# Revisão: {veredito}\n\n" + "\n".join(hist))
    return veredito


def roteiro(n):
    tema = linha_tema(n)
    cel = [c.strip() for c in tema.strip("|").split("|")]
    pasta = os.path.join(RASC, f"{datetime.date.today():%Y-%m-%d}-{int(n):03d}-{slug(cel[1])}")
    os.makedirs(pasta, exist_ok=True)
    texto = claude("roteiro", f"Tema nº {n}, linha da lista `{rel(TEMAS)}`:\n\n{tema}\n\n"
                   f"(colunas: N | tema | molde | estilo de gancho | veio de | views)", web=True)
    open(os.path.join(pasta, "roteiro.md"), "w", encoding="utf-8").write(texto + "\n")
    v = revisar(pasta)
    return f"tema {n}: {v} → {rel(pasta)}/roteiro.md"


def reescrever(pasta, nota):
    pasta = os.path.join(RASC, os.path.basename(pasta.rstrip("/\\")))
    rot = os.path.join(pasta, "roteiro.md")
    k = len(glob.glob(os.path.join(pasta, "roteiro-v*.md"))) + 1
    shutil.copy(rot, os.path.join(pasta, f"roteiro-v{k}.md"))
    with open(os.path.join(pasta, "notas-do-vitor.md"), "a", encoding="utf-8") as f:
        f.write(f"- {datetime.datetime.now():%d/%m %H:%M} · {nota}\n")
    # método do Fabiano: a nota vira incidente, e só sai de PENDENTE quando a página da etapa que errou for editada
    inc = os.path.join(MAQ, "_regras", "INCIDENTES.md")
    txt = open(inc, encoding="utf-8").read()
    linha = f"| {datetime.date.today():%d/%m} | 4 · roteiro (conferir se não nasceu antes) | {os.path.basename(pasta)}: {nota.replace('|', '/')} | PENDENTE |\n"
    txt = txt.replace("\n## Medição semanal", linha + "\n## Medição semanal", 1) if "\n\n## Medição semanal" not in txt else \
        txt.replace("\n\n## Medição semanal", "\n" + linha + "\n## Medição semanal", 1)
    open(inc, "w", encoding="utf-8").write(txt)
    novo = claude("roteiro", f"O Vitor leu e não curtiu. **Nota dele:** {nota}\n\n"
                  f"Reescreva aplicando a nota. Ela vale mais que qualquer regra.\n\n"
                  f"## Roteiro atual\n\n{open(rot, encoding='utf-8').read()}", web=True)
    open(rot, "w", encoding="utf-8").write(novo + "\n")
    print(f"{revisar(pasta)} → {rel(rot)}")


# ---------- 10 · capa e legenda ----------
def legenda(pasta):
    pasta = os.path.join(RASC, os.path.basename(pasta.rstrip("/\\")))
    out = claude("capa", f"Roteiro aprovado: `{rel(os.path.join(pasta, 'roteiro.md'))}`")
    open(os.path.join(pasta, "materiais.md"), "w", encoding="utf-8").write(out + "\n")
    secao = lambda nome: (re.search(rf"## {re.escape(nome)}\s*(.*?)(?=\n## |\Z)", out, re.S | re.I) or [None, ""])[1].strip()
    open(os.path.join(pasta, "legenda.txt"), "w", encoding="utf-8").write(secao("legenda.txt") + "\n")
    open(os.path.join(pasta, "guia.md"), "w", encoding="utf-8").write(secao("guia.md") + "\n")
    print(f"materiais.md (capas + código) · guia.md (material do direct) · legenda.txt em {rel(pasta)}")


# ---------- 8 · corte ----------
def corte(pasta):
    pasta = os.path.join(RASC, os.path.basename(pasta.rstrip("/\\")))
    brutos = sorted(glob.glob(os.path.join(pasta, "bruto", "*")))
    if not brutos:
        sys.exit(f"ponha a gravação em {rel(pasta)}/bruto/ e rode de novo")
    nome = os.path.basename(pasta)
    subprocess.run(["node", os.path.join(RAIZ, "tools", "video-recut", "limpar.cjs"), brutos[-1], nome], check=True)
    print(f"vídeo limpo: Downloads\\{nome}-limpo.mp4 · relatório: tools/video-recut/work/{nome}/limpeza/RELATORIO.md")


# ---------- 9 · legendas + animações (plano) ----------
def edicao(pasta):
    pasta = os.path.join(RASC, os.path.basename(pasta.rstrip("/\\")))
    tr = os.path.join(RAIZ, "tools", "video-recut", "work", os.path.basename(pasta), "limpeza", "transcricao.json")
    msg = f"Roteiro: `{rel(os.path.join(pasta, 'roteiro.md'))}`" + (f"\nTranscrição com tempos: `{rel(tr)}`" if os.path.exists(tr) else
                                                                  "\n(Ainda sem gravação: dê os tempos como estimativa pela ordem das frases.)")
    out = claude("animacoes", msg, web=True)
    open(os.path.join(pasta, "edicao.md"), "w", encoding="utf-8").write(out + "\n")
    m = re.search(r"## CREDITOS\.txt\s*(.*)", out, re.S | re.I)
    open(os.path.join(pasta, "CREDITOS.txt"), "w", encoding="utf-8").write((m.group(1) if m else "").strip() + "\n")
    print(f"edicao.md + CREDITOS.txt em {rel(pasta)}")


# ---------- 11 · arquivar ----------
def arquivar(pasta, limpar=False):
    origem = os.path.join(RASC, os.path.basename(pasta.rstrip("/\\")))
    destino = os.path.join(PUBL, os.path.basename(origem))
    os.makedirs(PUBL, exist_ok=True)
    shutil.move(origem, destino)
    if limpar and os.path.isdir(os.path.join(destino, "bruto")):  # "limpa as gravações", só depois de postado
        shutil.rmtree(os.path.join(destino, "bruto"))
    print(f"arquivado em {rel(destino)}" + (" · gravação bruta apagada" if limpar else ""))


def status():
    for p in sorted(glob.glob(os.path.join(RASC, "*"))):
        rv = os.path.join(p, "revisao.md")
        v = open(rv, encoding="utf-8").readline().strip("# \n") if os.path.exists(rv) else "sem revisão"
        print(f"{os.path.basename(p):60} {v}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd = a[0]
    if cmd == "temas":
        temas()
    elif cmd == "roteiro":
        with ThreadPoolExecutor(3) as ex:
            for r in ex.map(lambda n: _seguro(roteiro, n), a[1:]):
                print(r, flush=True)
    elif cmd == "reescrever":
        reescrever(a[1], " ".join(a[2:]))
    elif cmd == "legenda":
        legenda(a[1])
    elif cmd == "corte":
        corte(a[1])
    elif cmd == "edicao":
        edicao(a[1])
    elif cmd == "arquivar":
        arquivar(a[1], "--limpar" in a)
    elif cmd == "status":
        status()
    else:
        sys.exit(__doc__)


def _seguro(f, *x):
    try:
        return f(*x)
    except Exception as e:
        return f"FALHOU {x}: {e}"


if __name__ == "__main__":
    main()
