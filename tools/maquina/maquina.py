"""Máquina de conteúdo: orquestra as etapas que usam IA. Um Claude por etapa, uma página por trabalho.

Cada etapa é uma chamada nova de `claude -p`, que só enxerga a página dela (docs/conteudo/maquina/_paginas/)
e os arquivos que a mensagem aponta. As etapas não conversam: cada uma deixa um arquivo para a próxima.

uso:
  python tools/maquina/maquina.py temas                       # 2 · lista temas novos em 01-Ideias
  python tools/maquina/maquina.py roteiro 12 [13 14 …]        # 4+5 · roteiro + checagem de voz + revisor (até 2 voltas)
  python tools/maquina/maquina.py reescrever <pasta> "nota"   # 6 · o Vitor não curtiu: reescreve com a nota dele
  python tools/maquina/maquina.py corrigir <pasta>            # ciclo · diagnostica qual página errou e propõe a edição (antes → depois)
  python tools/maquina/maquina.py corte <pasta>              # 8 · bruto/ → vídeo limpo (limpar.cjs: última tentativa, sem pausas)
  python tools/maquina/maquina.py edicao <pasta>              # 9 · plano de legenda e animações + CREDITOS.txt
  python tools/maquina/maquina.py legenda <pasta>             # 10 · capas + código + guia.md (material do direct) + legenda.txt
  python tools/maquina/maquina.py arquivar <pasta> [--limpar] # 11 · move para 03-Publicados (--limpar apaga o bruto)
  python tools/maquina/maquina.py status                      # rascunhos e veredito de cada um
  python tools/maquina/maquina.py manha [N]                   # gatilho da manhã · N roteiros APROVADOS no WhatsApp (padrão 1) [--as 10:00]
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


# Quem executa cada etapa (19/10, pedido do Vitor: "adicione cada agente melhor em cada etapa").
# A página diz O QUE fazer e o formato; o agente traz o método e as bases dele. Persona + bases entram em toda chamada.
SQ = "squads/conteudo/agents/"
PARALELO = int(os.environ.get("MAQUINA_PARALELO", "1"))   # 19/10: 2 em paralelo morreu por RAM (PC com ~1 GB livre); 1 cabe em 4h–7h
BASE_ROTEIRO = ["squads/conteudo/roteiros-ouro.md",   # 19/10: princípios com o porquê + os textos que ele aprovou/falou
                "squads/conteudo/voz.md", "squads/conteudo/voz-pares.md", "docs/conteudo/ESTUDO-GANCHOS.md",
                "docs/conteudo/banco-pautas/GANCHOS-PRONTOS.md", "docs/conteudo/maquina/06-Ganchos/ganchos.md",
                "docs/conteudo/banco-roteiros/players/CATALOGO-MOLDES.md", "docs/conteudo/banco-roteiros/players/SINTESE-FORMATOS.md",
                "docs/conteudo/maquina/_regras/proibido.md", "docs/conteudo/maquina/_regras/nao-fale-assim.md"]
AGENTES = {
    "curadoria": ([SQ + "pauteiro.md"],
                  ["docs/conteudo/banco-roteiros/players/bernardo-precht/ESTUDO.md", "squads/conteudo/voz.md"]),
    "temas":     ([SQ + "analista-referencias.md", SQ + "pauteiro.md"],
                  ["docs/conteudo/ESTUDO-GANCHOS.md", "docs/conteudo/banco-roteiros/players/CATALOGO-MOLDES.md",
                   "docs/conteudo/banco-pautas/BANCO.md"]),
    "roteiro":   ([SQ + "roteirista.md", "squads/marketing/agents/copy-chief.md"], BASE_ROTEIRO),
    "revisor":   (["squads/marketing/agents/copy-chief.md"],
                  ["squads/conteudo/roteiros-ouro.md", "squads/conteudo/voz.md", "squads/conteudo/voz-pares.md", "docs/conteudo/ESTUDO-GANCHOS.md",
                   "docs/conteudo/maquina/_regras/proibido.md", "docs/conteudo/maquina/_regras/nao-fale-assim.md"]),
    "corrigir":  ([SQ + "roteirista.md"], ["squads/conteudo/voz.md", "docs/conteudo/maquina/_regras/proibido.md"]),
    "capa":      (["squads/marketing/agents/copy-chief.md", SQ + "roteirista.md"],
                  ["docs/conteudo/ESTUDO-GANCHOS.md", "squads/conteudo/voz.md"]),
    "animacoes": ([SQ + "editor-video.md"], ["tools/video-recut/README.md", "tools/maquina/montar.py",
                                             "docs/conteudo/LINHA-EDITORIAL-FORMATOS.md"]),
}


def quem(pagina):
    """O cabeçalho do agente da etapa: persona(s) na íntegra + bases para abrir antes de trabalhar."""
    if pagina not in AGENTES:
        return ""
    personas, bases = AGENTES[pagina]
    txt = "\n\n".join(open(os.path.join(RAIZ, f), encoding="utf-8").read() for f in personas)
    return ("# Quem executa esta etapa\n\nVocê é o agente abaixo (se forem dois, trabalham juntos: o primeiro escreve, "
            "o segundo cobra). Use o método e o critério deles.\n\n" + txt +
            "\n\n## Bases obrigatórias: abra cada uma com Read ANTES de começar\n" + "\n".join(f"- `{b}`" for b in bases) +
            "\n\n**Precedência:** onde a persona conflitar com `squads/conteudo/voz.md`, com `_regras/` ou com a página "
            "abaixo, valem esses (são mais novos e vieram das reprovações do Vitor). O formato de saída é SEMPRE o da "
            "página, não o \"Entregue sempre\" da persona.\n\n---\n\n")


def claude(pagina, mensagem, web=False, modelo="opus"):
    """Uma sessão nova: o agente da etapa + a página + a mensagem. Devolve só o texto da resposta."""
    corpo = quem(pagina) + open(os.path.join(PAG, f"{pagina}.md"), encoding="utf-8").read()
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


# ---------- manhã · o roteiro do dia chega no WhatsApp (gatilho: tarefa agendada no Windows) ----------
def usados():
    pastas = glob.glob(os.path.join(RASC, "*")) + glob.glob(os.path.join(PUBL, "*"))
    return {int(m.group(1)) for p in pastas if (m := re.match(r"\d{4}-\d{2}-\d{2}-(\d{3})-", os.path.basename(p)))}


def _aguardar(hora):
    """Segura o envio até HH:MM (o roteiro fica pronto antes; chega no horário combinado)."""
    if hora:
        alvo = datetime.datetime.combine(datetime.date.today(), datetime.time(*map(int, hora.split(":"))))
        import time
        while datetime.datetime.now() < alvo:
            time.sleep(20)


# semana de 19/10 (decisão do Vitor): 5 por dia, puxado para Regra e Identidade, que saem sem edição pesada
COTA = {"Regra": 2, "Identidade": 2, "Tendência": 1}
ICONE = {"Mercado": "📰", "Regra": "⚖️", "Identidade": "🗿", "Tendência": "📈", "Negócio": "🏢", "Bastidor": "🛠️"}


def _temas():
    return [[c.strip() for c in l.strip().strip("|").split("|")] for l in open(TEMAS, encoding="utf-8")
            if re.match(r"^\| \d+ \|", l.strip())]


def abastecer(reserva=1):
    """Se faltar tema de algum molde da cota (cota + reserva, contra reprovação do revisor), coleta os concorrentes
    (se a última coleta tem 2 dias ou mais) e roda a etapa 2 para listar temas novos."""
    livres = [c for c in _temas() if int(c[0]) not in usados()]
    falta = [m for m, q in COTA.items() if sum(c[2] == m for c in livres) < q + reserva]
    if not falta:
        return
    coletas = sorted(glob.glob(os.path.join(MAQ, "05-Concorrentes", "coletas", "*")))
    ultima = datetime.date.fromisoformat(os.path.basename(coletas[-1])) if coletas else datetime.date.min
    if (datetime.date.today() - ultima).days >= 2:
        subprocess.run([sys.executable, os.path.join(AQUI, "coletar.py")], cwd=RAIZ, check=False)
    temas()


def resumo_zap(pasta):
    """O que vai no celular: título, o texto para ler na câmera e o título da tela. As notas de gravação ficam no arquivo."""
    t = open(os.path.join(pasta, "roteiro.md"), encoding="utf-8").read()
    titulo = re.search(r"^# (.+)", t, re.M)
    fala = re.search(r"## Roteiro\s*```\w*\n(.*?)\n```", t, re.S) or re.search(r"## Roteiro\s*\n(.*?)(?=\n## |\Z)", t, re.S)
    tela = re.search(r"\*\*T[íi]tulo fixo:\*\*\s*(.+)", t)
    return ((f"*{titulo.group(1).strip()}*\n\n" if titulo else "") + (fala.group(1).strip() if fala else t.strip())
            + (f"\n\n📺 Título na tela: {tela.group(1).strip()}" if tela else ""))


def _gerar_grade(qtd=5):
    """Escreve e revisa os roteiros da grade pela COTA de moldes. Devolve ([(pasta, molde, tema, veredito)], falhas).
    Ordem de preferência: aprovado pelo revisor > escalado > esgotou as voltas (esse vai marcado)."""
    abastecer()
    livres = sorted([c for c in _temas() if int(c[0]) not in usados()],
                    key=lambda c: int(re.sub(r"\D", "", c[5]) or 0), reverse=True)
    cota = dict(COTA) if qtd == sum(COTA.values()) else {"": qtd}
    candidatos = []                                                     # cota + 1 de reserva por molde
    for m, q in cota.items():
        candidatos += [int(c[0]) for c in livres if not m or c[2] == m][:q + 1]
    with ThreadPoolExecutor(PARALELO) as ex:                                   # 4 em paralelo estourou a memória (19/10)
        res = dict(zip(candidatos, ex.map(lambda n: _seguro(roteiro, n), candidatos)))
    molde = {int(c[0]): c[2] for c in _temas()}
    escolhidos = []
    for m, q in cota.items():
        bons = sorted([n for n in candidatos if (not m or molde[n] == m) and _nota(res[n]) < 9], key=lambda n: _nota(res[n]))
        escolhidos += bons[:q]
    _log(f"grade: escolhidos {escolhidos} · " + " | ".join(res.values()))
    falhas = [r for n, r in res.items() if n not in escolhidos]
    return [(os.path.join(RAIZ, res[n].split("→ ")[1].rsplit("/", 1)[0]), molde[n], n, res[n]) for n in escolhidos], falhas


def _nota(r):
    return 0 if ": APROVADO" in r else 1 if "ESCALADO" in r else 2 if "REFAZER" in r else 9


def _log(txt):
    with open(os.path.join(MAQ, "_regras", "manha.log"), "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M} · {txt}\n")


def _enviar(lista, prefixo, inicio=1):
    """Um roteiro por mensagem, com código (N1… / R1…). O id fica em zap.registrar: quando o Vitor responde em cima,
    o maestro sabe de qual roteiro é."""
    import zap
    dia_ = f"{datetime.date.today():%d/%m}"
    for i, (pasta, molde, tema, ver) in enumerate(lista, inicio):
        cod = f"{prefixo}{i}"
        aviso = "" if _nota(ver) == 0 else "\n\n⚠️ _O revisor não aprovou de primeira: lê com atenção._"
        r = zap.texto(f"🎬 *{cod} · {ICONE.get(molde, '')} {molde}* · {dia_}\n\n{resumo_zap(pasta)}{aviso}")
        zap.registrar(r["key"]["id"], {"tipo": "roteiro", "codigo": cod, "dia": str(datetime.date.today()),
                                       "pasta": rel(pasta), "molde": molde, "tema": tema, "status": "enviado"})


def _cabecalho(n_noticias, n_grade):
    import zap
    partes = ([f"📰 {n_noticias} de mercado (N)"] if n_noticias else []) + ([f"🎬 {n_grade} da grade (R)"] if n_grade else [])
    zap.texto(f"☀️ *Roteiros de hoje ({datetime.date.today():%d/%m})*: " + " + ".join(partes) + ".\n\n"
              "↩️ Responde *em cima* de cada um (segura a mensagem → Responder):\n"
              "• *ok* = aprovado, pode gravar\n• escreve ou manda *áudio* com o que mudar = eu reescrevo\n"
              "• *troca* = outro tema\n\n🎥 Gravou? Sobe na pasta *Vídeos claude* com qualquer nome.")


def manha(qtd=5, hora=None):
    import zap
    lista, falhas = _gerar_grade(qtd)
    _aguardar(hora)
    if lista:
        _cabecalho(0, len(lista))
    _enviar(lista, "R")
    if len(lista) < qtd:
        zap.texto(f"⚠️ Hoje saíram {len(lista)} de {qtd} da grade. O que falhou:\n" + "\n".join(falhas))


# ---------- manhã · notícias de mercado (Caio cura e confere → Téo + copy-chief escrevem → revisor) ----------
def _concorrentes_recentes(dias=3):
    """20/10, pedido do Vitor (como o Fabiano faz): antes da curadoria, puxa os reels dos concorrentes e resume o que
    eles postaram nos últimos dias, para o Caio ver se alguém já deu a notícia (batida) ou se um player de fora deu
    algo que ninguém no Brasil pegou (sinal a favor). Falha da coleta não trava as notícias."""
    try:
        subprocess.run([sys.executable, os.path.join(AQUI, "coletar.py")], cwd=RAIZ, check=False,
                       capture_output=True, timeout=1800)
    except Exception as e:
        _log(f"coleta dos concorrentes falhou: {e}")
    corte = f"{datetime.date.today() - datetime.timedelta(days=dias):%Y-%m-%d}"
    vistos = {}
    for arq in sorted(glob.glob(os.path.join(RAIZ, "docs", "conteudo", "maquina", "05-Concorrentes", "coletas", "*", "*.json"))):
        for r in json.load(open(arq, encoding="utf-8")):
            if (r.get("data") or "") >= corte:
                vistos[r["shortCode"]] = r          # a coleta mais nova sobrescreve (views atualizadas)
    linhas = []
    for r in sorted(vistos.values(), key=lambda r: (r["data"], int(r.get("views") or 0)), reverse=True):
        txt = re.sub(r"\s+", " ", (r.get("abertura") or "") + " | " + (r.get("legenda") or ""))[:280]
        linhas.append(f"- @{r['perfil']} · {r['data']} · {int(r.get('views') or 0)} views · {txt}")
    return "\n".join(linhas)


def _gerar_noticias(qtd=4, inicio=1, escolha=None):
    hoje = f"{datetime.date.today():%Y-%m-%d}"
    subprocess.run([sys.executable, os.path.join(RAIZ, "tools", "roteiros", "noticias.py"), "--horas", "72", "--salvar"],
                   cwd=RAIZ, check=False, capture_output=True)
    pautas = os.path.join(RAIZ, "docs", "conteudo", "pautas", f"{hoje}.md")
    conc = _concorrentes_recentes()
    ja = sorted({re.sub(r"^\d{4}-\d{2}-\d{2}-n\d+-", "", os.path.basename(p))
                 for p in glob.glob(os.path.join(RASC, "*-n[0-9]*")) + glob.glob(os.path.join(PUBL, "*-n[0-9]*"))})
    cur = claude("curadoria", f"Escolha {qtd} notícias.\nPautas do dia: `{rel(pautas)}`" +
                 ("" if os.path.exists(pautas) else " (não foi gerado: busque na web)") +
                 "\nJá usados (não repetir): " + (", ".join(ja) or "nenhum") +
                 "\n\n## O que os concorrentes postaram nos últimos 3 dias (coleta de hoje)\n\n" +
                 (conc or "(coleta indisponível hoje)") +
                 (f"\n\n## O Vitor já escolheu as notícias (20/10)\n\nUse EXATAMENTE estas, nesta ordem; seu trabalho é conferir "
                  f"cada fato na fonte primária e montar os blocos (número que não confere vai para 'Não confere'):\n\n{escolha}"
                  if escolha else ""), web=True)
    blocos = re.findall(r"### N\d+ · ([\w-]+)\s*\n(.*?)(?=\n### N\d+ ·|\Z)", cur, re.S)[:qtd]
    if not blocos:
        raise RuntimeError("a curadoria não devolveu blocos ### N1 · slug")

    def um(k_bloco):
        k, (sl, fatos) = k_bloco
        pasta = os.path.join(RASC, f"{hoje}-n{k}-{slug(sl.replace('-', ' '), 6)}")
        os.makedirs(pasta, exist_ok=True)
        open(os.path.join(pasta, "pauta.md"), "w", encoding="utf-8").write(f"# Pauta do Caio\n\n{fatos.strip()}\n")
        txt = claude("roteiro", "**Molde: 📰 Mercado da manhã** (notícia + leitura de negócio, modelo @beprecht, 60 a 80 s; "
                     "ver `docs/conteudo/banco-roteiros/players/bernardo-precht/ESTUDO.md`). Use SÓ os fatos conferidos abaixo "
                     "(nada de número fora deles). Padrão-ouro desta voz: os textos de `squads/conteudo/roteiros-ouro.md` "
                     "(N3 final e o N4 que o Vitor reescreveu à mão). Use os princípios, não copie as frases. No cabeçalho, em vez de Tema nº, escreva em uma linha a "
                     "família de gancho usada (ESTUDO-GANCHOS).\n\n"
                     f"## Pauta conferida pelo Caio\n\n{fatos.strip()}", web=True)
        open(os.path.join(pasta, "roteiro.md"), "w", encoding="utf-8").write(txt + f"\n\n## Fontes (Caio)\n\n{fatos.strip()}\n")
        return pasta, "Mercado", None, revisar(pasta)

    with ThreadPoolExecutor(PARALELO) as ex:
        res = list(ex.map(lambda kb: _seguro(um, kb), enumerate(blocos, inicio)))
    ok = [r for r in res if isinstance(r, tuple)]
    _log(f"notícias: {len(ok)}/{qtd} · " + " | ".join(f"{rel(r[0])}: {r[3]}" if isinstance(r, tuple) else r for r in res))
    ok.sort(key=lambda r: _nota(r[3]))
    return ok, [r for r in res if not isinstance(r, tuple)]


def _noticias_de_hoje():
    """Quantas notícias de hoje já têm roteiro (ex.: o Vitor escolheu 3 de madrugada). O `dia` continua a numeração
    e só escreve o que falta, sem repetir assunto nem colidir pasta/código."""
    hoje = f"{datetime.date.today():%Y-%m-%d}"
    return len([p for p in glob.glob(os.path.join(RASC, f"{hoje}-n[0-9]*")) if os.path.exists(os.path.join(p, "roteiro.md"))])


def noticias(qtd=4, hora=None, escolha=None):
    ja = _noticias_de_hoje()
    lista, _ = _gerar_noticias(qtd, ja + 1, escolha)
    _aguardar(hora)
    if lista:
        _cabecalho(len(lista), 0)
    _enviar(lista, "N", ja + 1)


def dia(n_noticias=4, n_grade=5, hora=None):
    """A manhã inteira: gera as notícias e a grade (em sequência, para não estourar a memória), espera a hora e manda
    primeiro as N (o primeiro vídeo do dia é o de mercado), depois as R."""
    import zap
    ln, fn = [], []
    ja = _noticias_de_hoje()                       # 20/10: notícias escolhidas antes (madrugada) já contam
    pedidas, n_noticias = n_noticias, max(0, n_noticias - ja)
    if n_noticias:
        r = _seguro(_gerar_noticias, n_noticias, ja + 1)
        ln, fn = r if isinstance(r, tuple) else ([], [r])
    lr, fr = _gerar_grade(n_grade) if n_grade else ([], [])
    _aguardar(hora)
    if ln or lr:
        _cabecalho(len(ln), len(lr))
    _enviar(ln, "N", ja + 1)
    _enviar(lr, "R")
    if len(ln) < n_noticias or len(lr) < n_grade:
        zap.texto(f"⚠️ Hoje saíram {len(ln)}/{n_noticias} de mercado e {len(lr)}/{n_grade} da grade.\n"
                  + "\n".join(map(str, fn + fr)))


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
    def secao(nome):  # a seção inteira até o próximo "## " de topo; tira a cerca ``` que o modelo às vezes põe em volta
        m = re.search(rf"^## {re.escape(nome)}\s*\n(?:```\w*\n(.*?)\n```|(.*?)(?=^## |\Z))", out, re.S | re.I | re.M)
        return ((m.group(1) or m.group(2)) if m else "").strip()
    open(os.path.join(pasta, "legenda.txt"), "w", encoding="utf-8").write(secao("legenda.txt") + "\n")
    open(os.path.join(pasta, "guia.md"), "w", encoding="utf-8").write(secao("guia.md") + "\n")
    from guia_pdf import gerar
    pdf = gerar(pasta)
    print(f"materiais.md (capas + código) · guia.md + guia.pdf (material do direct) · legenda.txt em {rel(pasta)}")


# ---------- ciclo · corrigir a página, não o caso ----------
def corrigir(pasta):
    pasta = os.path.join(RASC, os.path.basename(pasta.rstrip("/\\")))
    arqs = [rel(p) for p in sorted(glob.glob(os.path.join(pasta, "roteiro*.md")) +
                                  glob.glob(os.path.join(pasta, "notas-do-vitor.md")) +
                                  glob.glob(os.path.join(pasta, "revisao.md")))]
    out = claude("corrigir", "Arquivos desta pasta:\n" + "\n".join(f"- `{a}`" for a in arqs))
    open(os.path.join(pasta, "correcao-de-pagina.md"), "w", encoding="utf-8").write(out + "\n")
    print(f"diagnóstico em {rel(pasta)}/correcao-de-pagina.md: ler, aplicar a edição na página e tirar o PENDENTE do INCIDENTES.md")


# ---------- 8 · corte ----------
def corte(pasta):
    pasta = os.path.join(RASC, os.path.basename(pasta.rstrip("/\\")))
    brutos = sorted(glob.glob(os.path.join(pasta, "bruto", "*")))
    if not brutos:
        sys.exit(f"ponha a gravação em {rel(pasta)}/bruto/ e rode de novo")
    nome = os.path.basename(pasta)
    subprocess.run(["node", os.path.join(RAIZ, "tools", "video-recut", "limpar.cjs"), brutos[-1], nome], check=True)
    print(f"vídeo limpo: Downloads\\{nome}-limpo.mp4 · relatório: tools/video-recut/work/{nome}/limpeza/RELATORIO.md")


def par_voz(pasta):
    """Depois do corte: guarda o roteiro enviado ao lado do que ele disse (squads/conteudo/voz-pares.md).
    É assim que a página do roteiro aprende o jeito dele de falar, gravação por gravação."""
    pasta = os.path.join(RASC, os.path.basename(pasta.rstrip("/\\")))
    tr = os.path.join(RAIZ, "tools", "video-recut", "work", os.path.basename(pasta), "limpeza", "palavras-editado.json")
    if not os.path.exists(tr):
        return
    j = json.load(open(tr, encoding="utf-8"))
    falado = " ".join(w.get("word", "").strip() for w in (j.get("words", j) if isinstance(j, dict) else j)).strip()
    resumo = resumo_zap(pasta)
    titulo = resumo.split("\n", 1)[0].strip("* ")
    escrito = re.sub(r"\s+", " ", resumo.split("\n", 1)[-1].split("📺")[0]).strip()
    with open(os.path.join(RAIZ, "squads", "conteudo", "voz-pares.md"), "a", encoding="utf-8") as f:
        f.write(f"\n## {datetime.date.today()} · {titulo}\n\n**Escrito:**\n\n{escrito}\n\n**Falado:**\n\n{falado}\n")


# ---------- 9 · legendas + animações (plano) ----------
def edicao(pasta):
    pasta = os.path.join(RASC, os.path.basename(pasta.rstrip("/\\")))
    tr = os.path.join(RAIZ, "tools", "video-recut", "work", os.path.basename(pasta), "limpeza", "palavras-editado.json")  # tempos do vídeo cortado
    msg = f"Roteiro: `{rel(os.path.join(pasta, 'roteiro.md'))}`" + (f"\nTranscrição com tempos: `{rel(tr)}`" if os.path.exists(tr) else
                                                                  "\n(Ainda sem gravação: dê os tempos como estimativa pela ordem das frases.)")
    out = claude("animacoes", msg, web=True)
    open(os.path.join(pasta, "edicao.md"), "w", encoding="utf-8").write(out + "\n")
    m = re.search(r"## CREDITOS\.txt\s*(.*?)(?=\n## |\Z)", out, re.S | re.I)
    open(os.path.join(pasta, "CREDITOS.txt"), "w", encoding="utf-8").write((m.group(1) if m else "").strip() + "\n")
    j = re.search(r"## edicao\.json\s*```(?:json)?\s*(\{.*?\})\s*```", out, re.S | re.I)
    if not j:
        sys.exit(f"o plano não trouxe o bloco edicao.json: veja {rel(os.path.join(pasta, 'edicao.md'))}")
    plano = json.loads(j.group(1))  # inválido = erro aqui, antes de chegar ao montador
    json.dump(plano, open(os.path.join(pasta, "edicao.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"edicao.md + edicao.json + CREDITOS.txt em {rel(pasta)}")


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
    elif cmd == "revisar":  # roteiro escrito fora da máquina: passa só pela etapa 5
        print(revisar(os.path.join(RASC, os.path.basename(a[1].rstrip("/\\")))))
    elif cmd == "corrigir":
        corrigir(a[1])
    elif cmd == "corte":
        corte(a[1])
    elif cmd == "edicao":
        edicao(a[1])
    elif cmd == "arquivar":
        arquivar(a[1], "--limpar" in a)
    elif cmd == "status":
        status()
    elif cmd in ("noticias", "dia"):
        hora = a[a.index("--as") + 1] if "--as" in a else None
        nums = [int(x) for x in a[1:] if x.isdigit()]
        if cmd == "noticias":   # --escolha arquivo.md: as notícias que o Vitor escolheu (o Caio só confere)
            esc = open(a[a.index("--escolha") + 1], encoding="utf-8").read() if "--escolha" in a else None
            noticias(nums[0] if nums else 4, hora=hora, escolha=esc)
        else:
            dia(*(nums + [4, 5][len(nums):])[:2], hora=hora)
    elif cmd == "manha":
        hora = a[a.index("--as") + 1] if "--as" in a else None
        manha(int(a[1]) if len(a) > 1 and a[1].isdigit() else 5, hora=hora)
    else:
        sys.exit(__doc__)


def _seguro(f, *x):
    try:
        return f(*x)
    except Exception as e:
        return f"FALHOU {x}: {e}"


if __name__ == "__main__":
    main()
