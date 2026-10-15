"""Máquina de conteúdo, etapa 5a: checagem de voz determinística (sem IA), antes do revisor.

Pega o que dá para pegar sem julgamento: palavra proibida, travessão, frase sem fôlego,
"não é X, é Y" repetido, abertura e fecho proibidos, expressão de player, IA como assunto, duração.
As regras saem de squads/conteudo/voz.md e de docs/conteudo/maquina/_regras/proibido.md.

uso:  python tools/maquina/checar_voz.py <roteiro.md>      # sai com código 1 se houver erro
"""
import re, sys

PROIBIDAS = ["otimizar", "escalar", "alavancar", "solução", "ecossistema", "jornada", "mindset", "destravar",
             "potencializar", "exponencial", "game changer", "imagine só", "vamos lá", "é importante lembrar",
             "em resumo", "nesse sentido", "vale destacar", "portanto"]
ABERTURAS = ["você já parou", "nesse vídeo", "neste vídeo", "hoje eu vou", "deixa eu te mostrar"]
FECHOS = ["comece hoje", "o segredo é", "reflita", "pense nisso", "me segue", "comenta aí"]
PLAYER = ["ponto final", "presta atenção no discurso", "tá, luana", "meu anjo", "filhotão"]
IA = [r"\bIA\b", r"intelig[êe]ncia artificial", r"\bChatGPT\b", r"\bagentes?\b", r"\bClaude\b", r"\bprompt"]


def texto_do_roteiro(md):
    m = re.search(r"## Roteiro\s*```[^\n]*\n(.*?)```", md, re.S)
    return (m.group(1) if m else md).strip()


def checar(md):
    t = texto_do_roteiro(md)
    baixo = t.lower()
    erros, avisos = [], []
    for p in PROIBIDAS:
        if re.search(rf"\b{re.escape(p)}", baixo):
            erros.append(f"palavra proibida: '{p}' (proibido 26)")
    if "—" in t or re.search(r"\s–\s", t):
        erros.append("travessão no texto: ele fala em ponto final (proibido 24)")
    primeira = baixo.splitlines()[0] if baixo else ""
    for a in ABERTURAS:
        if a in primeira:
            erros.append(f"abertura proibida: '{a}' (proibido 27)")
    fim = " ".join(baixo.splitlines()[-3:])
    for f in FECHOS:
        if f in fim:
            erros.append(f"fecho de conselho ou isca: '{f}' (proibido 28)")
    for x in PLAYER:
        if x in baixo:
            erros.append(f"expressão de player: '{x}' (proibido 6)")
    n_nao_e = len(re.findall(r"\bnão é\b[^.!?\n]{0,60}[.,]\s*(?:é|e sim)\b", baixo))
    if n_nao_e > 1:
        erros.append(f"'não é X, é Y' aparece {n_nao_e} vezes (proibido 23)")
    for frase in re.split(r"(?<=[.!?])\s+|\n", t):
        if len(frase.split()) > 22:
            erros.append(f"frase sem fôlego ({len(frase.split())} palavras): '{frase[:70]}…' (proibido 25)")
    if re.search(r"\b\w+(?:ção|dade|ência|ância|ismo), \w+(?:ção|dade|ência|ância|ismo) e \w+(?:ção|dade|ência|ância|ismo)\b", baixo):
        erros.append("tríade de abstrações (proibido 22)")
    # "IA" em maiúscula de propósito: com re.I casaria o verbo "ia" ("eu ia ter casa")
    hits = [p for p in IA if re.search(p, t, 0 if p == r"\bIA\b" else re.I)]
    if hits:
        avisos.append("fala de IA: confirmar que IA não é o assunto, no máximo a virada (proibido 8)")
    palavras = len(t.split())
    seg = round(palavras / 2.6)
    if not 45 <= palavras <= 130:
        avisos.append(f"duração fora da faixa: {palavras} palavras, ~{seg}s (faixa de 20 a 45s)")
    return erros, avisos, palavras, seg


def relatorio(md):
    erros, avisos, palavras, seg = checar(md)
    L = [f"voz: {'ok' if not erros else 'ERRO'} · {palavras} palavras · ~{seg}s"]
    L += [f"- ❌ {e}" for e in erros] + [f"- ⚠️ {a}" for a in avisos]
    return "\n".join(L), not erros


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    texto, ok = relatorio(open(sys.argv[1], encoding="utf-8").read())
    print(texto)
    sys.exit(0 if ok else 1)
