# Registro de incidentes e medição

> Regra do método: **toda correção vira edição de página.** Discutir no chat conserta uma vez; arrumar a página conserta sempre.
> O `maquina.py reescrever` registra aqui sozinho cada nota do Vitor, com a edição marcada como PENDENTE. Ela só sai de PENDENTE quando a página da etapa que errou for editada.

## Incidentes (4 campos)

| Data | Etapa que errou | Sintoma (o que saiu errado) | Edição na página (antes → depois) |
|---|---|---|---|
| 15/10 | 5 · revisor | reprovou 3 de 3 roteiros até esgotar as voltas | `revisor.md`: entraram o critério de aprovação e a regra da 2ª volta |
| 15/10 | 5 · revisor | tratou "Tá, Vitor, mas…" como transposição | `proibido.md` item 6: entrou a exceção escrita |
| 15/10 | 5 · checar_voz | acusava "IA" no verbo "ia" | `checar_voz.py`: "IA" passou a ser buscado só em maiúscula |
| 15/10 | 4 · roteiro | traduziu o gancho do Jett ("Quando eu era criança, achava…") | `roteiro.md`: regra contra tradução literal |

## Medição semanal (4 números)

| Semana | Roteiros gerados | Aprovados pelo revisor na 1ª volta | Aprovados pelo Vitor sem reescrita | Erro que voltou (mesmo tipo, outro nome) |
|---|---|---|---|---|
| 13–19/10 | 3 | 0 | — | — |

**Se o ciclo funciona:** em 6 semanas, o 3º número sobe e o 4º vai a zero. Se o mesmo erro voltar com outro nome, a correção foi feita no caso e não na página.
