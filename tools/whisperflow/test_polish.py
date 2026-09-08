"""test_polish.py — o guarda-corpo do polimento, sem rede.

Casos tirados do historico real (2026-09-08), quando o polimento colou no
cursor coisas que o Vitor nunca disse.

    .venv/Scripts/python.exe test_polish.py     (tambem roda sob pytest)
"""

from __future__ import annotations

import sys

sys.path.insert(0, ".")

from polish import looks_wrong


def test_rejects_the_model_answering_instead_of_cleaning():
    """Caso real 18:11:59 — 39 palavras de instrucoes viraram uma pergunta
    do proprio modelo, e ERA ISSO que ia para o cursor."""
    raw = (
        "Tire todos os travessões que fiquem remetentes a IA. Tire também a "
        "parte que fala que é só no grupo, que recebe material. Não, para "
        "entrar no grupo para receber a oferta especial. Tire todos esses "
        "excessos de informação."
    )
    assert looks_wrong(raw, "Por favor, envie o texto que deseja que eu limpe.")
    print("OK  rejeita o modelo respondendo em vez de limpar")


def test_rejects_restructuring_into_a_spec():
    """Caso real 18:12:39 — 13 palavras viraram 27 em formato de spec."""
    raw = "Quero que tire esses travessões, quero que tire algumas informações, Elissa e Nex."
    polished = (
        "Objetivo: remover os travessões e excluir as informações referentes a "
        "Elissa e Nex.\nRequisitos: eliminar todos os travessões do texto; "
        "excluir quaisquer menções a Elissa e Nex."
    )
    assert looks_wrong(raw, polished)
    print("OK  rejeita reestruturacao em 'Objetivo:/Requisitos:'")


def test_accepts_an_honest_cleanup():
    raw = "é, tipo, eu queria confirmar a reuniao de amanha, ne, umas quinze horas"
    assert not looks_wrong(raw, "Eu queria confirmar a reunião de amanhã, umas quinze horas.")
    print("OK  aceita limpeza honesta (vicios de fala fora, conteudo intacto)")


def test_accepts_heavy_but_faithful_cleanup():
    """Limpeza pesada nao pode ser confundida com invencao: mesmo cortando
    muita muleta, as palavras de conteudo continuam la."""
    raw = (
        "Então, tipo assim, sabe, eu acho que a gente deveria, né, revisar a "
        "proposta da Cindy antes de mandar, entendeu?"
    )
    assert not looks_wrong(raw, "Acho que deveríamos revisar a proposta da Cindy antes de mandar.")
    print("OK  aceita limpeza pesada mas fiel")


def test_user_may_dictate_the_word_objetivo_himself():
    """Se a fala JA tem 'objetivo:', o cabecalho na saida nao e invencao."""
    raw = "objetivo: fechar a pagina de captura hoje. requisitos: usar a nossa paleta."
    polished = "Objetivo: fechar a página de captura hoje. Requisitos: usar a nossa paleta."
    assert not looks_wrong(raw, polished)
    print("OK  nao pune cabecalho que o proprio usuario ditou")


def test_empty_or_tiny_input_is_never_flagged():
    assert not looks_wrong("", "")
    assert not looks_wrong("oi", "Oi.")
    print("OK  entrada vazia/curta nao dispara o guarda-corpo")


if __name__ == "__main__":
    test_rejects_the_model_answering_instead_of_cleaning()
    test_rejects_restructuring_into_a_spec()
    test_accepts_an_honest_cleanup()
    test_accepts_heavy_but_faithful_cleanup()
    test_user_may_dictate_the_word_objetivo_himself()
    test_empty_or_tiny_input_is_never_flagged()
    print("")
    print("6/6 passaram")
