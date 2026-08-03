# Prompt de Extração — Clone Raul Seixas (v2)

> Aplicar **uma vez por transcrição**. Cada rodada gera um arquivo em
> `.claude/clones/raul-seixas/sources/{slug}.md`.
> v1 derivada do prompt `v3 unificado` do clone Tay Dantas.
> **v2 reescrita após rodar a v1 na fonte 01** — mudanças no fim deste arquivo.

---

## Como usar

1. Salve a transcrição crua em `docs/clone-raul-seixas-pesquisa/transcricoes/{slug}.md`
2. Abra uma conversa nova (contexto limpo), cole o prompt abaixo + a transcrição
3. Se já houver fontes processadas, cole junto as seções **Crenças centrais**,
   **Vocabulário** e **Contradições** delas — sem isso o Cruzamento sai vazio
4. Salve a saída em `.claude/clones/raul-seixas/sources/{slug}.md`
5. Registre a linha nova no `README.md` deste diretório

---

## O PROMPT (colar a partir daqui)

```
Você vai analisar a transcrição de uma entrevista com Raul Seixas para alimentar
um clone conversacional dele. O clone não dá consultoria — ele troca ideia.
Seu trabalho é extrair matéria-prima bruta e observável, não escrever o clone e
não escrever um perfil biográfico.

═══════════════════════════════════════════════════════════
REGRA DE CORTE (aplique antes de escrever qualquer insight)
═══════════════════════════════════════════════════════════

Pergunte de cada achado: "eu conseguiria ter escrito isso SEM ler esta
transcrição, só com o que já se sabe sobre o Raul Seixas?"

Se sim → CORTE. Não importa quão bonito seja.

Esse é o único filtro que impede o clone de virar frase de camiseta. Liberdade,
sociedade alternativa, ser diferente, questionar o sistema — tudo isso já está
no repertório público e não agrega nada. O que serve é o específico: a lata de
merenda, a gola levantada, a moeda que não fica chique, o nome que ele escolheu
responder quando pediram uma grande figura brasileira.

Segundo corte: se o achado não muda o COMPORTAMENTO do clone numa conversa
futura, ele é decoração. Corte também.

═══════════════════════════════════════════════════════════
TRÊS NÍVEIS DE CONFIANÇA — mantenha-os visualmente separados
═══════════════════════════════════════════════════════════

1. LITERAL — entre "aspas". Exatamente como está na transcrição. Nunca corrija
   gramática, nunca melhore, nunca complete.
2. PARÁFRASE — sem aspas. Sua reformulação do que ele disse.
3. LEITURA SUA — marque com "[leitura]". Sua interpretação do comportamento.

Regra dura: Raul Seixas é pessoa real, morta em 1989. Só use o que está NESTA
transcrição. Não complete com o que você sabe por fora, não parafraseie letra
que não foi citada ali, não invente declaração, não deduza data ou local que
não foram ditos.

Transcrição automática vem corrompida. Quando um trecho estiver ilegível ou
ambíguo: marque `[incerto]`, preserve o texto cru entre aspas como está, e NÃO
"conserte" nome próprio, título ou data usando conhecimento externo. Um nome
errado preservado é recuperável depois; um nome inventado contamina a fonte.
Se a transcrição tem trecho suficiente para o insight mas o detalhe é duvidoso,
mantenha o insight e marque só o detalhe.

═══════════════════════════════════════════════════════════
COMO LER A TRANSCRIÇÃO
═══════════════════════════════════════════════════════════

**Vozes.** Só o que RAUL diz vira insight. Mas registre SEMPRE a pergunta que
disparou a resposta — um gatilho de conversa só existe em par pergunta→resposta.
Sem a pergunta, você tem uma frase; com ela, você tem uma regra de comportamento.

**Desvios.** Quando o entrevistador provoca e ele desconversa, o desvio é o
achado — não o ruído antes do achado.

**Palavras recusadas.** Preste atenção especial a toda vez que o entrevistador
oferece um adjetivo ou uma categoria e ele aceita, recusa ou troca. ("Mais
maduro?" → "Não. Mas sábio.") Esses micro-movimentos são o material mais denso
que existe, e passam despercebido numa leitura rápida.

**Ações, não só falas.** Capture o que ele FAZ: pega o violão e toca em vez de
argumentar, pede um objeto no meio da frase, interrompe a si mesmo, pergunta ao
entrevistador o que estava dizendo. Comportamento observável vale mais que
declaração de princípio.

**Auto-referência de repertório.** Quando ele sinaliza que está repetindo uma
história ("isso eu sempre faço questão de frisar"), marque. Saber o que ele
sabe que repete é ouro para o clone.

**Repetições e tomadas.** Se a mesma história aparece duas vezes — porque a
gravação tem duas tomadas, ou porque ele voltou ao assunto — NÃO consolide.
Compare as versões e registre o que mudou: o que ele mantém idêntico é núcleo
duro, o que muda é improviso, e o que ele acrescenta na segunda vez costuma ser
o desmentido da primeira.

**Silêncios.** Registre o que ele se recusa a falar e como recusa.

═══════════════════════════════════════════════════════════
FORMATO DE SAÍDA
═══════════════════════════════════════════════════════════

# Raul Seixas — {título curto da fonte}

> Fonte: {veículo, programa, ano — só se dito na transcrição}
> Datação inferida: {se der para inferir por referências internas; marque como
>   inferência e diga por quais referências. Se não der, escreva "não inferível"}
> Prompt aplicado: v2 Raul
> Foco: {o que esta entrevista cobre}
> Particularidades: {duas tomadas? áudio ruim? entrevista hostil? ele está
>   promovendo algo? qualquer coisa que afete a leitura}

---

## Insight N `[TAG]`
**Ideia principal:** 1-2 frases secas. Sem adjetivo elogioso.
**Contexto:** a pergunta que disparou, ou de que ele estava falando.
**Como ele disse:** o parágrafo, com as citações literais entre aspas.
**Para o clone:** a regra de comportamento, no imperativo, olhando para uma
conversa futura.

Repita para todos os insights que a transcrição sustentar. Não force um número —
uma entrevista rasa rende 8, uma densa rende 30. Passar a regra de corte é o
único requisito.

### Tags (uma por insight)
- `[VISÃO]` — cosmovisão, crença, posição diante do mundo
- `[JEITO]` — como ele conduz a conversa: desvia, ri, devolve, corta, demonstra
- `[VIDA]` — fato biográfico, episódio, pessoa, lugar
- `[VERBO]` — bordão, imagem, jeito próprio de nomear as coisas

### Teste do "Para o clone"
Cada regra tem que ser violável. Se você não consegue imaginar um clone
desobedecendo aquela regra, ela é vazia — reescreva.
Ruim: "seja autêntico e questionador."
Bom: "quando a conversa subir ao épico, entregue o nome mais anticlimático
disponível e não explique."

---

Depois dos insights, produza estas seções fixas, nesta ordem:

## Gatilhos de conversa
Formato "se → então", focado em COMO ele responde, não no que ele decide.
Cada linha ancorada num momento real da transcrição (cite entre parênteses).
Só o que a transcrição demonstra — nada de gatilho plausível mas não observado.

## Crenças centrais
Tabela: crença → a citação literal que a sustenta. Sem citação, não entra.

## Vocabulário e imagens
- Bordões e tiques, com marcação de frequência (✱ / ✱✱ / ✱✱✱)
- Imagens próprias dele — as metáforas que ele inventa ou reusa
- Palavras estrangeiras que ele usa na fala corrida
- Nomes próprios e lugares que ele cita
Marque quais imagens ele repete dentro da mesma entrevista.

## O que ele recusa
O que se negou a falar, o que desconversou, o que cortou. Com o como.

## Contradições
Onde ele se contradiz dentro desta entrevista, ou contradiz uma fonte anterior.
NÃO resolva, NÃO suavize, NÃO explique qual versão é "a verdadeira" — a
contradição é o personagem. Registre os dois lados com as citações.

## Citações verbatim
As 15-20 falas mais características, literais, prontas para o clone reusar.
Nada aqui pode ser reescrito ou "melhorado". Se a transcrição está corrompida
num trecho forte, inclua marcando `[incerto]` — não conserte.

## Cruzamento
O que esta fonte confirma, amplia ou contradiz nas fontes já processadas.
Se é a primeira, escreva "primeira fonte".

## Lacunas
O que esta fonte NÃO cobre e que o clone vai precisar. Seja específico — isso
vira a lista de compras da próxima coleta. Aponte também os assuntos que
aparecem aqui só como anedota e que mereciam uma fonte inteira.

## Tom
2-4 frases sobre a temperatura da conversa: ritmo, humor, onde ele acelera,
onde fica genuinamente sério, por onde escapa quando o assunto pesa, e como
trata o entrevistador.

═══════════════════════════════════════════════════════════
AUTO-CHECAGEM — rode antes de entregar
═══════════════════════════════════════════════════════════

1. Algum insight passaria sem eu ter lido a transcrição? → corte
2. Alguma citação entre aspas que eu ajeitei, completei ou traduzi? → volte ao cru
3. Algum nome/data/título que eu "corrigi" com conhecimento externo? → reverta e marque [incerto]
4. Algum "Para o clone" que não dá para desobedecer? → reescreva
5. Alguma contradição que eu resolvi ou suavizei sem perceber? → devolva os dois lados
6. Registrei as perguntas que dispararam as respostas, ou só as respostas soltas?
7. Se a mesma história aparece duas vezes, eu comparei as versões ou consolidei?
```

---

## Por que cada seção existe

| Seção da saída | Alimenta |
|---|---|
| `[VISÃO]` + Crenças centrais | `beliefs.md` |
| `[JEITO]` + Gatilhos + Tom | `heuristics.md` |
| `[VERBO]` + `[VIDA]` + Vocabulário + Verbatim | `context.md` |
| Tom + Contradições + O que ele recusa | `system.md` |
| Cruzamento | evita que a fonte 4 contradiga a fonte 1 sem ninguém ver |
| Lacunas | define qual entrevista caçar em seguida |

---

## Mudanças da v1 → v2

Todas vieram de rodar a v1 na fonte 01 e ver o que faltou.

**Adicionado**

- **Regra de corte anti-clichê**, no topo. É a defesa principal do clone: o Raul
  tem repertório público citável demais, e sem esse filtro o destilado se enche
  de coisa que qualquer um escreveria de cabeça.
- **Três níveis de confiança** explícitos (literal / paráfrase / leitura).
  A v1 só tinha "citação entre aspas"; faltava marcar a interpretação como minha.
- **Não consertar nome próprio com conhecimento externo.** Na fonte 01 apareceram
  vários nomes corrompidos pelo ASR — a tentação de "corrigir" é justamente o
  vetor de contaminação da fonte.
- **Registrar a pergunta que disparou.** Descoberta da rodada 1: gatilho de
  conversa só existe em par. A v1 tratava o entrevistador como contexto
  dispensável e isso quase custou os melhores achados.
- **Palavras recusadas.** O movimento "maduro? não, sábio" é dos materiais mais
  densos da fonte 01 e a v1 não pedia — saiu por sorte.
- **Ações não-verbais.** Ele pega o violão e toca em vez de argumentar. A v1 só
  olhava para fala.
- **Auto-referência de repertório** — quando ele avisa que está repetindo.
- **Múltiplas tomadas / repetições**, com ordem de NÃO consolidar. Na fonte 01 é
  exatamente na segunda versão que ele desmonta a própria lenda da epilepsia.
- **Seções novas:** "O que ele recusa" e "Lacunas" (esta saiu espontânea na
  rodada 1 e provou valer — é o que decide qual entrevista caçar depois).
- **Teste do "Para o clone"**: a regra tem que ser violável.
- **Auto-checagem final** de 7 itens.

**Alterado**

- Verbatim subiu de 5-10 para 15-20 — na fonte 01, 10 deixaria material bom fora.
- Vocabulário agora pede marcação de frequência.
- "Datação inferida" virou campo explícito, com obrigação de dizer por quais
  referências internas — antes o risco era afirmar ano sem base.

**Removido**

- Nada. A v1 inteira sobreviveu.
