"""Banco de pautas — o método do "livro × capítulo × insight", com a fonte trocada.

O método original (Hulisses Dias, ficha ref-ativodigitalbrazil-...-DbtwTp-TK1t):
    livros mais vendidos -> capítulos -> 5 insights por capítulo -> 600 reels.

Por que não dá pra rodar como está: a Amazon devolve 503 para leitura automática e nenhuma
fonte livre expõe o sumário dos livros. Sem isso, "os capítulos do livro X" seria invenção —
e a Constituição do projeto proíbe (Art. IV). Além disso o produto final do método é resumo de
livro, que é exatamente o que afunda na grade medida (listicle técnico: 466 curtidas).

O que este script faz no lugar, com a mesma mecânica combinatória:
    FONTE (artefato real + dor com palavra de cliente + inimigo)  ->  papel do livro
    MOLDE DE GANCHO (as 9 famílias medidas em ESTUDO-GANCHOS.md)  ->  papel do capítulo
    PAUTA com gancho escrito, formato e prova exigida             ->  papel do insight

Diferença que importa: aqui toda pauta nasce grudada numa dor com evidência e num gancho com
desempenho medido. Nenhuma nasce de resumo de terceiro.

    python tools/roteiros/pautas.py               # imprime o resumo
    python tools/roteiros/pautas.py --salvar      # grava docs/conteudo/banco-pautas/BANCO.md
    python tools/roteiros/pautas.py --dor d-equipe --n 10
"""
import argparse
import json
import os
import random

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
SAIDA = os.path.join(RAIZ, "docs", "conteudo", "banco-pautas")

# As 9 famílias que aparecem no topo, de docs/conteudo/ESTUDO-GANCHOS.md.
# `pico` é a melhor marca medida da família — serve para ordenar o banco por aposta.
MOLDES = [
    {"id": "imperativo", "familia": "Imperativo contraintuitivo", "pico": 109257,
     "molde": "Pare de {consenso}. Comece a {oposto}.",
     "serve": ["artefato", "dor", "inimigo", "capitulo"], "funcao": "alcance"},
    {"id": "cultural", "familia": "Referência cultural", "pico": 108890,
     "molde": "Lembra de {referencia}? {ponte com a tensão}.",
     "serve": ["artefato", "inimigo"], "funcao": "alcance"},
    {"id": "futuro", "familia": "Futuro ameaçador com data", "pico": 57100,
     "molde": "Até {data}, {consequência verificável para quem tem negócio}.",
     "serve": ["inimigo", "artefato"], "funcao": "alcance"},
    {"id": "acusa", "familia": "Revelação que acusa", "pico": 55700,
     "molde": "O verdadeiro motivo de {fato que ele vive} deveria te incomodar.",
     "serve": ["dor", "inimigo", "capitulo"], "funcao": "alcance"},
    {"id": "descoberta", "familia": "Descoberta / pesquisa", "pico": 55600,
     "molde": "{veículo, data} mostrou que {dado}.",
     "serve": ["inimigo"], "funcao": "alcance", "exige": "fato do dia conferido na fonte primária"},
    {"id": "investigacao", "familia": "Investigação em 1ª pessoa", "pico": 38800,
     "molde": "Eu {fiz a coisa} por {tempo}. O que ninguém conta é {achado}.",
     "serve": ["artefato"], "funcao": "conversão", "exige": "artefato na tela nos primeiros 15s"},
    {"id": "autoridade", "familia": "Autoridade + paradoxo", "pico": 41452,
     "molde": "{autor} escreveu que {contradição}. {a sua leitura em cima}.",
     "serve": ["dor", "inimigo", "capitulo"], "funcao": "alcance",
     "exige": "citar autor + título + ano. Nunca reproduzir trecho, nunca resumir o capítulo"},
    {"id": "alvo", "familia": "Pergunta com alvo concreto", "pico": 33000,
     "molde": "Sabe {quem ou o quê} mais atrapalha {resultado que ele quer}?",
     "serve": ["dor", "inimigo", "artefato", "capitulo"], "funcao": "alcance",
     "nota": "a família mais subutilizada por ele — é a que mais gera compartilhamento"},
    {"id": "arquetipo", "familia": "Arquétipo inesperado", "pico": 21194,
     "molde": "O melhor {papel} que eu conheço é {figura improvável}.",
     "serve": ["dor", "inimigo", "capitulo"], "funcao": "alcance"},
]

FORMATO = {"alcance": "contraste · disrupcao · arquetipo", "conversão": "obra"}


def carregar():
    with open(os.path.join(AQUI, "fontes.json"), encoding="utf-8") as f:
        d = json.load(f)
    with open(os.path.join(AQUI, "livros.json"), encoding="utf-8") as f:
        liv = json.load(f)["livros"]
    fontes = []
    for L in liv:                              # cada capítulo real vira uma fonte
        for i, c in enumerate(L["capitulos"], 1):
            fontes.append({
                "tipo": "capitulo", "id": f"{L['id']}{i:02d}", "nome": c,
                "tensao": f"{L['titulo']} ({L['autor']}, {L['ano']}) — cap. {i}",
                "prova": None, "dor": L.get("dor"),
                "livro": L["titulo"], "autor": L["autor"], "ano": L["ano"],
                "territorio": L["territorio"],
            })
    for a in d["artefatos"]:
        fontes.append({"tipo": "artefato", "id": a["id"], "nome": a["nome"], "tensao": a["tensao"],
                       "prova": a["prova"], "dor": a.get("dor"), "onde": a["onde"], "o_que_e": a["o_que_e"]})
    for x in d["dores"]:
        fontes.append({"tipo": "dor", "id": x["id"], "nome": x["nome"], "tensao": x["palavra"],
                       "prova": None, "dor": x["id"], "evidencia": x["evidencia"]})
    for x in d["inimigos"]:
        fontes.append({"tipo": "inimigo", "id": x["id"], "nome": x["nome"], "tensao": x["frase"],
                       "prova": None, "dor": None})
    return fontes, {x["id"]: x for x in d["dores"]}


def gerar(fontes, dores):
    pautas = []
    for f in fontes:
        for m in MOLDES:
            if f["tipo"] not in m["serve"]:
                continue
            if m["id"] == "investigacao" and not f.get("prova"):
                continue                      # peça de obra sem artefato é o fundo da tabela
            d = dores.get(f.get("dor") or "")
            pautas.append({
                "id": f"{f['id']}-{m['id']}",
                "fonte": f["nome"], "tipo": f["tipo"], "tensao": f["tensao"],
                "familia": m["familia"], "molde": m["molde"], "pico": m["pico"],
                "funcao": m["funcao"], "formato": FORMATO[m["funcao"]],
                "prova": f.get("prova"),
                "dor": d["nome"] if d else None,
                "palavra": d["palavra"] if d else None,
                "exige": m.get("exige"),
                "nota": m.get("nota"),
                "livro": f.get("livro"), "autor": f.get("autor"), "ano": f.get("ano"),
            })
    pautas.sort(key=lambda p: (-p["pico"], p["id"]))
    return pautas


def markdown(pautas, fontes):
    n_art = sum(1 for f in fontes if f["tipo"] == "artefato")
    L = ["# Banco de pautas", "",
         f"> Gerado por `tools/roteiros/pautas.py`. **{len(pautas)} pautas** de "
         f"{len(fontes)} fontes × 9 famílias de gancho medidas.", "",
         "Cada pauta é uma fonte (artefato real, dor com palavra de cliente ou inimigo declarado) "
         "cruzada com uma família de gancho que tem desempenho medido em `ESTUDO-GANCHOS.md`. "
         "Ordenado pelo pico da família — as primeiras são as maiores apostas.", "",
         "**Como usar:** escolhe a linha, entrega fonte + molde ao roteirista (`@Conteudo:agents:roteirista`), "
         "ele escreve passando pelos 12 testes do portão. O gancho abaixo é o molde, não a frase final.", "",
         f"**Fontes hoje:** {n_art} artefatos próprios · "
         f"{sum(1 for f in fontes if f['tipo'] == 'dor')} dores · "
         f"{sum(1 for f in fontes if f['tipo'] == 'inimigo')} inimigos · "
         f"{sum(1 for f in fontes if f['tipo'] == 'capitulo')} capítulos de "
         f"{len({f['livro'] for f in fontes if f['tipo'] == 'capitulo'})} livros.", "",
         "Cada artefato novo em `fontes.json` acrescenta até 9 pautas. Cada livro novo em "
         "`livros.json` acrescenta 5 por capítulo — comprar mais livros é literalmente como o "
         "banco cresce.", "", "---", ""]
    # --- pautas vindas de livro, agrupadas por livro e capítulo nomeado ---
    dos_livros = [p for p in pautas if p["tipo"] == "capitulo"]
    if dos_livros:
        L += [f"## Vindas de livro ({len(dos_livros)})", "",
              "> Método do Hulisses: livro mais vendido → capítulo → ângulo. **O título do capítulo é o "
              "gatilho, não o conteúdo do vídeo.** O roteiro nunca resume o capítulo — usa a tensão do "
              "título como porta e responde com artefato próprio. Citar autor, título e ano é prova de "
              "terceiro; reproduzir trecho, não.", ""]
        for livro in dict.fromkeys(p["livro"] for p in dos_livros):
            desse = [p for p in dos_livros if p["livro"] == livro]
            a, ano = desse[0]["autor"], desse[0]["ano"]
            L += [f"### {livro} — {a}, {ano}", "",
                  f"{len(set(p['fonte'] for p in desse))} capítulos × {len(set(p['familia'] for p in desse))} "
                  f"famílias = {len(desse)} pautas", "",
                  "| Capítulo | Família | Gancho-molde |", "|---|---|---|"]
            for p in sorted(desse, key=lambda x: (x["id"][:-len(x["id"].split("-")[-1]) - 1], -x["pico"])):
                L.append(f"| {p['fonte']} | {p['familia']} | {p['molde']} |")
            L.append("")

    for func in ("alcance", "conversão"):
        sel = [p for p in pautas if p["funcao"] == func and p["tipo"] != "capitulo"]
        L += [f"## Peças de {func} ({len(sel)})", ""]
        if func == "alcance":
            L += ["> Sem CTA. A conversa acontece na DM de quem se reconheceu.", ""]
        else:
            L += ["> Exige artefato na tela nos primeiros 15 segundos. Sem isso, é o fundo da tabela.", ""]
        L += ["| # | Fonte | Família (pico) | Gancho-molde | A tensão | Dor que toca |",
              "|---|---|---|---|---|---|"]
        for i, p in enumerate(sel, 1):
            dor = p["palavra"] or "—"
            pico = f"{p['pico']:,}".replace(",", ".")      # só o número leva ponto de milhar
            L.append(f"| {i} | {p['fonte']} | {p['familia']} ({pico}) | {p['molde']} | "
                     f"{p['tensao']} | {dor} |")
        L.append("")
    L += ["---", "", "## Regras que o banco já embute", "",
          "1. Nenhuma pauta usa família que afunda (listicle técnico, meta-conteúdo, resposta a criador).",
          "2. Peça de obra só existe quando a fonte tem prova — artefato sem tela não entra.",
          "3. Peça de alcance não pede nada. CTA troca alcance por comentário.",
          "4. Molde `descoberta` exige fato do dia conferido na fonte primária (`noticias.py`).",
          "5. Molde `autoridade` exige citação real. Frase de autor não verificada não sobe.", "",
          "## Por que não é o método do livro", "",
          "O método original termina em resumo de livro. A grade medida diz que isso afunda "
          "(listicle técnico: 466 curtidas) e a pesquisa de cliente diz por quê: ele não sofre de falta "
          "de informação, sofre de informação não instalada. Mais um insight alimenta o problema. "
          "Por isso a fonte aqui é **coisa construída**, não capítulo lido.", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salvar", action="store_true")
    ap.add_argument("--dor", help="filtra por id de dor (ex: d-equipe)")
    ap.add_argument("--n", type=int, default=12, help="quantas imprimir")
    a = ap.parse_args()

    fontes, dores = carregar()
    pautas = gerar(fontes, dores)
    if a.dor:
        pautas = [p for p in pautas if (p.get("dor") or "") and a.dor in
                  [k for k, v in dores.items() if v["nome"] == p["dor"]]]

    print(f"{len(pautas)} pautas de {len(fontes)} fontes x 9 familias\n")
    for p in pautas[:a.n]:
        pico = f"{p['pico']:,}".replace(",", ".")
        print(f"[{p['funcao']:9}] {p['familia']:32} {pico:>9}")
        print(f"             fonte: {p['fonte']}")
        print(f"             molde: {p['molde']}")
        print(f"             tensao: {p['tensao']}\n")

    if a.salvar:
        os.makedirs(SAIDA, exist_ok=True)
        cam = os.path.join(SAIDA, "BANCO.md")
        with open(cam, "w", encoding="utf-8") as f:
            f.write(markdown(pautas, fontes))
        with open(os.path.join(SAIDA, "banco.json"), "w", encoding="utf-8") as f:
            json.dump(pautas, f, ensure_ascii=False, indent=2)
        print(f"-> {cam}")


if __name__ == "__main__":
    main()
