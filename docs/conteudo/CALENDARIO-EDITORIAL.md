# Calendário Editorial — 5 bons por dia

**Vigente desde:** 2026-09-28 (primeira semana) · **Substitui:** a grade de 7/semana de `docs/ecossistema/linha-editorial-e-calendario.md` §03 (o resto daquele doc — registros VISÃO/OBRA, métrica, revisão de 11/11 — continua valendo)

**Princípio:** 5 vídeos por dia, **todos os 5 quadros todos os dias, inclusive sábado e domingo.** Nenhum deles é para cumprir tabela. A diferença é usar a IA no máximo em tudo que não é a câmera — pesquisa, pauta, checagem, roteiro, edição — para que o Vitor só grave, e grave coisa boa.

---

## Os 5 quadros

| Quadro | O que é | Duração | Exemplo já feito | De onde vem a pauta |
|---|---|---|---|---|
| ☕ **CAFEIA** | A notícia do dia: o fato, o que ela muda para quem tem negócio e o ângulo que ninguém falou | 45–65s | Episódio 2 — o anúncio entrou na conversa | `noticias.py` toda manhã |
| 🛠️ **Na Tela** (seg · qua · sex) | Algo que o Vitor construiu com IA, rodando na tela. Editado para o **dono de negócio**: mostra o resultado e o tempo que levou; código só de relance, como prova. Nunca "qualquer um faz em 5 min" — o honesto é "montei um sistema que faz X" | 45–90s | "Montei um sistema que edita meus vídeos — o das 18h saiu assim" | Obra real da semana (CRM, agentes, QG, editor, WhisperFlow) |
| 🔍 **Curiosidade** | Sua visão sobre uma novidade ou um fato curioso do mundo | 40–60s | iPhone novo da Apple · o café que só tem milionário | O que apareceu na semana + `noticias.py` |
| ⚡ **Curto** | O mais seco da grade. Pode ser: **uma frase** com a história por trás (Alexandre, o Grande), **um mecanismo** com nome, ou **uma lista**. Molde dos curtos do Kaio | 15–45s | Alexandre, o Grande · 11 leis da psicologia · "tudo que você força foge" | Referências traduzidas (`colher.py`) + frases/leis com fonte |
| 🔭 **Visão** | Leitura estratégica: o que está por baixo do que todo mundo vê. Molde da Luana | 60–90s | Kahneman — "quanto custa × quanto tá custando" | Banco de pautas + fichas de referência |

---

## A grade — igual nos 7 dias

| Horário | Quadro |
|---|---|
| **07h30** | ☕ CAFEIA (notícia + ângulo no mesmo vídeo) |
| **12h00** | 🛠️ Na Tela (seg · qua · sex) · ⚡ Curto extra (ter · qui · sáb · dom) |
| **15h00** | 🔍 Curiosidade |
| **18h00** | ⚡ Curto |
| **20h30** | 🔭 Visão |

**Por que uma CAFEIA só (mudança de 28/09):** duas notícias por dia era o quadro mais fácil de virar "cumprir tabela". O ângulo que ia para a CAFEIA 2 entra dentro da CAFEIA. O horário foi para o **Na Tela**, que é onde o banco de referências aponta o melhor desempenho (Matheus: obra na tela no topo, opinião sem obra no fundo). Na Tela é **3×/semana** porque não existe obra nova todo dia — forçar diário viraria demonstração encenada.

**No fim de semana a notícia rende menos:** a CAFEIA de sábado e domingo é **"a notícia da semana que você perdeu"**.

**Tema da Visão por dia** (para nunca começar do zero):

| Seg | Ter | Qua | Qui | Sex | Sáb | Dom |
|---|---|---|---|---|---|---|
| Dinheiro e decisão | Negócio e estratégia | Comportamento e psicologia | Mercado e empresas grandes | Futuro e trabalho | IA na prática | Leitura da semana |

**Total:** 35 por semana · ~450 em 90 dias.

---

## O portão — nada sai sem passar

É isso que separa "5 por dia" de "5 bons por dia". Cada vídeo passa pelas 5 perguntas antes de ir para edição. **Um não = não posta.** Entra um do estoque no lugar; nunca um vídeo mais fraco para preencher o horário.

1. **Gancho:** a primeira frase segura sozinha, lida em voz alta?
2. **Uma ideia só:** dá para resumir o vídeo em uma frase? (Se precisa de duas, são dois vídeos.)
3. **Fonte:** todo número, pesquisa e fato foi conferido na fonte primária e anotado no roteiro?
4. **Ângulo próprio:** diz algo que o post da notícia/da referência não disse?
5. **Voz:** soa falado, sem tríade, sem "não é X, é Y", sem cara de IA?

---

## Estoque — o que segura a qualidade no dia ruim

Manter sempre **6 vídeos prontos e editados** na gaveta: 2 Curtos, 2 Visões, 2 Curiosidades. São os que não envelhecem.

- Vídeo reprovado no portão → entra um do estoque.
- Dia de viagem, doença, travado → os quadros sem notícia saem do estoque; a CAFEIA é gravada pelo celular em 15 min ou pula (notícia requentada não entra).
- Estoque abaixo de 4 → o bloco de quinta repõe antes de gravar a semana.

---

## A divisão: o que a IA faz, o que o Vitor faz

| Etapa | Quem | Como |
|---|---|---|
| Colher notícias | IA | `python tools/roteiros/noticias.py --salvar` às 06h30 |
| Escolher as 2 da CAFEIA + ângulo | IA propõe, **Vitor escolhe** | 3 opções com ângulo, em `pautas/AAAA-MM-DD.md` |
| Colher e traduzir referências | IA | `colher.py <link>` — ficha + tradução no banco |
| Pesquisar e conferir fontes | IA | busca na fonte primária, anotada no roteiro |
| Escrever roteiro | IA escreve, **Vitor lê em voz alta e ajusta** | `banco-pautas/roteiro-*.md` |
| Portão | IA checa 1–3 e 5, **Vitor decide o 4** | checklist acima |
| **Gravar** | **Vitor** | o único passo que ninguém faz por ele |
| Editar | IA | `tools/video-recut/` — 1 prévia + 1 render |
| Legenda do post | IA | junto com o roteiro |

## A rotina

| Quando | O quê | Tempo do Vitor |
|---|---|---|
| **Todo dia, 06h45** | Escolher a notícia da CAFEIA → ler o roteiro → gravar | ~25 min |
| **Segunda, bloco** | Gravar 7 Visões + 7 Curiosidades da semana; gravar a tela das 3 obras (Na Tela) | ~3h30 |
| **Quinta, bloco** | Gravar 11 Curtos (7 das 18h + 4 extras do meio-dia) + repor o estoque | ~1h30 |
| **Domingo à noite** | Aprovar as pautas da semana seguinte (roteiros já prontos) | ~1h |

**Onde cada coisa mora:**
- Pautas do dia → `docs/conteudo/pautas/AAAA-MM-DD.md`
- Roteiros → `docs/conteudo/banco-pautas/roteiro-*.md`
- Referências colhidas → `docs/conteudo/banco-roteiros/referencias/`
- Vídeos editados → `tools/video-recut/videos/<nome>/` → saída em `Downloads\`

---

## Regras que valem para os 5 quadros

1. **Falado de verdade.** Ler em voz alta antes de gravar.
2. **Número ou pesquisa só com fonte conferida.** Seção "Checagem de fonte" em todo roteiro.
3. **Sem CTA de venda** no conteúdo. CTA, quando houver, é DM.
4. **Saída da Cindy é confidencial.** Nunca em roteiro.

---

## Conta

- 35/semana ≈ **450 vídeos em 90 dias**, todos passando no portão.
- A meta do plano de 90 dias é **1.000**. O caminho sem baixar a régua é **cortes**: cada Visão (60–90s) rende 2 cortes bons, cada CAFEIA e cada Na Tela rende 1 → +24/semana → ~760. Os cortes também passam no portão.
