# Brief para o Fable — Meet Transcriber, refatoração

## Situação

Extensão Chrome MV3 própria que transcreve reuniões do Google Meet lendo as legendas ao vivo (mesma técnica do Tactiq — não grava áudio, lê o CC). Vive em `docs/plugin-meet-transcriber/`. É o braço de captura da Sales Intelligence Platform: o dataset proprietário de reuniões que alimenta o Sales Coach do CRM.

Estado do código, medido agora:

- `content.js` — 564 linhas. Parsing do DOM da legenda, estado, render do painel e envio pro CRM convivem no mesmo arquivo. O painel é montado com uma string `innerHTML` grande no início e depois manipulado via `createElement`/`classList`.
- `transcript-core.js` — 122 linhas. Núcleo puro (`bestText`/`mergeRolling`/`upsertRow`) extraído pra ser compartilhado com os testes. É a parte mais sã do código.
- `caption-parser.js` — 147 linhas.
- `styles.css` — 141 linhas, injetado direto na página do Meet. **Sem Shadow DOM.**
- `popup.html` — 30 linhas, quase vestigial: a config real migrou pro ⚙ inline do painel (decisão ADR-7).
- Sem build step, sem framework, sem dependências. 1081 linhas no total.
- 9 fixtures rodando em Chrome headless real via `tests/run.js` (~8s).

Dossiê de decisões anteriores (autossuficiente, com ADR-1 a ADR-10): `DEEP-ANALYSIS-FABLE.md`. Story: `docs/stories/meet-transcriber-redondo-v1.story.md`, status InProgress.

## Tensões reais

**1. O sequenciamento contradiz o pedido.** Na última análise você foi explícito: não polir CSS/visual antes de confirmar que a atribuição de falante está 100% correta com dado real. O protocolo ADR-10 (call real com frases curtas e distintas por pessoa, 🐞 no meio e no fim, dumps do flight recorder colados) **nunca foi rodado**. As hipóteses H3 (nó de DOM recriado pelo Meet) e H4 (`mergeRolling` sob repetição) continuam sem confirmação nem refutação. Agora o pedido é justamente uma refatoração de front. Isso é reabrir uma decisão sua com informação nova, ou é furar a fila?

**2. Restrição de tempo assimétrica.** Este é o último dia de acesso ao Fable. O que sobra depois é execução via Sonnet/Opus. Isso muda o cálculo do que vale gastar aqui: um plano bem abstraído pode ser executado depois sem você, mas um diagnóstico que depende de dado que ainda não existe (a call ADR-10) não pode ser feito hoje de jeito nenhum. Como isso deveria reordenar o que você produz agora?

**3. O front não é só CSS.** O painel injeta estilos globais na página do Meet, que o Google reescreve com frequência e sem aviso. Não há isolamento. A camada de view está entrelaçada com a de parsing no mesmo arquivo. Ao mesmo tempo, o plugin inteiro tem 1081 linhas e zero dependências — introduzir build step, framework ou design system tem um custo que pode não se pagar num artefato deste tamanho, e que quebraria o fluxo atual de "carregar sem compactação" no `chrome://extensions`.

**4. A referência é ambígua.** O alvo declarado é "parecer os grandes plugins do mercado". Mas o Tactiq — o benchmark original — foi deliberadamente desviado em decisões anteriores: cota, CTA de upgrade e aba de IA foram descartados de propósito (o Chat-com-a-call vive no CRM, não no plugin). Então copiar a percepção de qualidade do Tactiq sem copiar o modelo de produto dele é coerente ou é cargo cult?

**5. Dívida ainda aberta.** Nada disso foi pusheado — os commits são locais. E há duas pendências de segurança não resolvidas: 3 access tokens do Supabase expostos durante o deploy, e a chave Anthropic não rotacionada. O endpoint `ingest-meeting` gasta créditos Anthropic por chamada.

## Perguntas

- Dado que a atribuição de falante nunca foi validada com dado real, uma refatoração de front agora constrói em cima de fundação incerta — ou é independente o suficiente pra não importar?
- Sendo este o último dia de acesso a você: o que só você consegue produzir, que sobreviva à execução por modelos menores depois?
- O que "moderno e funcional" deveria significar concretamente num artefato de 1081 linhas que roda dentro da página de outra empresa? Onde a ambição de UI vira passivo de manutenção?
- Onde eu estou sendo inconsistente comigo mesmo neste projeto?

Formato livre. Não precisa entregar checklist.
