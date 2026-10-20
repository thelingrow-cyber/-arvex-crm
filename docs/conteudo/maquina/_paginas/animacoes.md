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
2. **Escolha o topo pelo molde** (os dois foram aprovados em 19/10):
   - **📰 Mercado / notícia → topo que TROCA:** `"topo": {"seq": [{"de": 0, "url": "…"}, {"de": 4.3, "url": "…"}, …]}`, **uma imagem nova a cada 3 a 6 s**, casada com a fala (a pessoa citada, a empresa, o produto, o lugar). Aprovado no N3 "Buffett na contramão de novo".
   - **Regra, Identidade, ideia, filosofia → TRIO fixo:** `"topo": {"trio": [{"url": …}, {"url": …}, {"url": …}]}`, 3 quadros quadrados lado a lado o vídeo todo. **Os 3 ativam o arquétipo do vídeo, não ilustram palavra:** a pessoa citada + uma figura do arquétipo filosófico (Marco Aurélio, Sêneca, Rodin, pintura clássica) + um empreendedor de tecnologia/construtor (Jobs, Bezos, Musk, Ford…). Aprovado no vídeo do Bezos (Bezos + Marco Aurélio + Jobs). *Motivo: o Vitor reprovou o estádio no trio ("não fez sentido, coloque fotos que ativem mais o arquétipo filosófico, empreendedor tech"), 19/10.*
3. Imagens: **o primeiro quadro do topo mostra o rosto/assunto principal** (ex.: a cara do Buffett). Pessoa, empresa, produto e lugar = foto atual e real (Wikimedia Commons, press kit, site oficial com licença). Ideia ou metáfora = pintura histórica de domínio público (Rembrandt, Caravaggio, Turner, Leutze…). Nada de nudez. Confira que cada link `File:` existe. **Só imagem (url), sem vídeo**: aqui não há como baixar vídeo, e foto mantém a edição em minutos.
4. Título fixo: **curto (até ~30 caracteres), caixa alta, provocação ou síntese que gera curiosidade**, sem repetir a primeira fala. Sai em tipografia FINA (padrão do `montar.py`; não use `titulo_estilo`). Referências aprovadas: "OCUPADO DEMAIS PRA CONSTRUIR?", "BUFFETT NA CONTRAMÃO DE NOVO". Se o roteiro trouxer "Título fixo", parta dele.
5. Planeje **de 8 a 12 inserções laterais contínuas** (310×390, alternando esquerda e direita, 2,5 a 4 s cada, uma logo depois da outra, do primeiro nome citado até o fecho), nos momentos concretos da fala (nome, objeto, cena, lugar). **Foto boa = específica e forte**: a garagem onde a Amazon começou, uma ampulheta no "lento demais", o Pensador no "ficar parado"; nada infantil (caracol, desenho) nem genérico de banco.
   **Todo número que ele fala vira cartão animado**: `{"de", "ate", "lado", "numero": 70, "sufixo": "%", "linhas": ["DO QUE VOCÊ", "GOSTARIA DE SABER"]}` (conta de 0 até o número, barra enche, frase sobe; `"prefixo": "R$ "`, `"sufixo": " bi"`; `"cor": "vermelho"` para o número ruim). Só número conferido no roteiro/Fontes. *Motivo: o Vitor pediu "motion melhor no gráfico de número", 19/10.* Opcional: **1 ou 2 momentos em tela cheia** (`"cheia": [{"de","ate","url","modo":"encaixe"}]`, 1,5 a 3 s) no número ou na frase mais forte.
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
| Topo e metáforas contemporâneas demais (16/10, "Remar" v2) e depois cena comum histórica demais (v3: loja de 1890, carroça) | a página não separava cena comum de metáfora | topo e metáfora = históricos; cena do dia a dia = foto atual |
| Regra saiu sem topo e sem inserção (16/10, "Remar"), e o Vitor pediu os dois | a página mandava Regra sem topo e inserção só com caso real | todo molde leva topo e inserções (hoje: 8 a 12 contínuas) |
| Trio com estádio, caracol na lateral, número em cartão parado (19/10, Bezos v1) | foto que ilustra a palavra em vez do arquétipo; card estático | trio = arquétipo; foto específica e forte; número = cartão animado (`numero`) |
| Legenda e inserções fora de hora (16/10, Efeito IKEA) | tempos lidos da transcrição do bruto, antes do corte das pausas | usar `palavras-editado.json`, que já está nos tempos do vídeo cortado |


> **20/10, reprovado pelo Vitor:** o cartão animado de número (`"numero"`) ficou "horrível". Não use até ser redesenhado. Número dito na fala vira imagem real do objeto (capa do livro, vídeo da pessoa dizendo a frase, foto do lugar). Autor citado = mostre o livro dele.
