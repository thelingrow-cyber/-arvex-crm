# Planejar legendas e animações

## Quando esta página é usada
Na etapa 9, depois do corte, com o comando `maquina.py edicao <pasta>`. Pode rodar antes da gravação, e aí os tempos saem estimados.

## O que chega
O caminho do `roteiro.md` e, se já houver, a transcrição do vídeo limpo com os tempos (`tools/video-recut/work/<pasta>/limpeza/palavras-editado.json`, já nos tempos do vídeo cortado).

## O que sai
~~~
## Topo
The Course of Empire: Destruction · Thomas Cole · 1836 · https://commons.wikimedia.org/… · domínio público

## Título fixo
ATÉ OS MELHORES AFUNDAM.

## Inserções
| De (s) | Até (s) | Lado | Imagem | Link | Licença |
| 12.0 | 18.5 | ESQ | Frederic Tudor, retrato | https://commons… | domínio público |

## CREDITOS.txt
Imagens: Thomas Cole (domínio público) · …

## edicao.json
```json
{"titulo": "ATÉ OS MELHORES AFUNDAM.",
 "topo": {"url": "https://commons.wikimedia.org/wiki/File:Cole_Thomas_The_Course_of_Empire_Destruction_1836.jpg"},
 "laterais": [{"de": 12.0, "ate": 18.5, "lado": "ESQ", "url": "https://commons.wikimedia.org/wiki/File:…"}]}
```
~~~
O exemplo real é o "Rei do gelo", aprovado em 14/10. O bloco `edicao.json` é o que o `tools/maquina/montar.py` lê para montar o vídeo sozinho: os links são as páginas `File:` do Commons, os tempos vêm da transcrição e `"topo": null` quando o molde não leva topo.

## Como fazer
1. Leia o roteiro e a seção "Edição por molde" de `docs/conteudo/LINHA-EDITORIAL-FORMATOS.md`.
2. Pelo molde, decida se o vídeo leva **topo fixo** (Identidade, Negócio, Tendência) ou só o **título fixo** (Regra).
3. Ache no Wikimedia Commons uma pintura clássica de domínio público que **traduza a tese e represente o arquétipo** do vídeo (o homem que decide, constrói, resiste) e anote autor, ano, link e licença. Confira que o link `File:` existe de verdade.
4. Escreva o título fixo: a ordem ou a lei, sem repetir a primeira fala.
5. Só se o roteiro citar algo com imagem real, planeje as inserções laterais (310×390, alternando esquerda e direita), com os tempos.
6. Monte o `CREDITOS.txt`.
7. Feche com o bloco `edicao.json`, com os mesmos topo, título e inserções da tabela.

## Regras que não se quebram
- Imagem só com licença conferida. *Motivo: o vídeo é publicado com o nome do Vitor.*
- Sem borda redonda, logo em fundo branco, imagem genérica de banco, motion de desenho ou texto descritivo sobre a foto. *Motivo: tudo isso foi reprovado entre 07/10 e 14/10.*
- A legenda sai uma palavra por vez, em Montserrat ExtraBold minúscula. *Motivo: é o molde aprovado em 14/10.*

## Critério de pronto
- [ ] Topo com link e licença, ou "sem topo" justificado pelo molde.
- [ ] Toda inserção tem tempos, link e licença.
- [ ] O `CREDITOS.txt` cobre todas as imagens.
- [ ] O bloco `edicao.json` é JSON válido e bate com a tabela.

## Erros conhecidos
| Sintoma | Causa | Correção |
|---|---|---|
| Legenda e inserções fora de hora (16/10, Efeito IKEA) | tempos lidos da transcrição do bruto, antes do corte das pausas | usar `palavras-editado.json`, que já está nos tempos do vídeo cortado |
