# Meet Transcriber — Diagnóstico Profundo & Plano "Redondo"

> Autor: @architect (Aria) · análise com Fable 5 · 2026-07-06
> Executor previsto: @dev (Dex) com Opus/Sonnet — este documento é autossuficiente; NÃO requer reanálise
> Escopo: `docs/plugin-meet-transcriber/` (extensão MV3) + Edge Function `ingest-meeting` (Supabase do CRM) · consumidor downstream: Sales Coach Fase 3 (`docs/crm/sales-coach-fase3-ARCHITECTURE.md`)
> Base lida: código completo (manifest, content.js, caption-parser.js, popup.*, styles.css, tests/) + todos os reports (PLAN, BUILD, OPTIMIZE, PLAN-PERFECT-AND-CONNECT, CONNECT, README) + diff local não commitado

---

## 1. Contexto e constraints (não violar)

- **O plugin é FUNCIONAL** (validado ao vivo pelo Vitor). Nada aqui é reescrita — é fechar as lacunas que separam "funciona" de "redondo".
- **Vanilla JS, MV3, sem build step.** Manter. 6 arquivos de extensão + 2 de teste; o valor do produto é ser leve e manutenível por 1 pessoa + agentes.
- **Diff local não commitado** em `caption-parser.js`/`content.js`/`styles.css` (heurística de falante por subida de árvore, strip de nome vazado, agrupamento visual por falante). É código BOM, mas **não testado ao vivo** — o plano abaixo o valida antes de commitar (S1), não o descarta.
- **Push é exclusivo de @devops.** Todo o código do plugin existe só nesta máquina — isso é um risco em si (perda de disco = perda do produto).

## 2. Diagnóstico — por que "não tá redondo"

### 🔴 CRITICAL-1 — Endpoint de ingestão aberto ao mundo (segurança estrutural, não pontual)

- `content.js` l.15-16 embute `INGEST_URL` + publishable key. Publishable key ser pública é OK por design; o problema é que **`ingest-meeting` roda com `verify_jwt=false` e service_role** (CONNECT-REPORT, "Notas técnicas") e não valida NADA além do formato do body.
- Consequência concreta: **qualquer pessoa com a URL** (que está num content script legível por qualquer usuário da extensão — e vai pro GitHub no push) pode: (a) criar reuniões ilimitadas no CRM (poluição de dados no Sales Coach), (b) **disparar `analyze-meeting` em loop e queimar créditos Anthropic** — é um endpoint que gasta dinheiro sem autenticação, (c) atribuir reuniões a qualquer closer, pois a identidade é um **e-mail digitado no popup, sem verificação** (`arvex_closer_email`, popup.js l.60-62 → content.js l.286-294).
- O próprio CONNECT-REPORT registrou como "TODO futuro: shared-secret". Com o push pro GitHub se aproximando, deixou de ser futuro: **é pré-requisito do push**.

### 🔴 CRITICAL-2 — Tokens vazados: o padrão, não só as chaves

- Já mapeado: Supabase **access token** (Management API — admin da conta inteira, não só deste projeto) e **chave Anthropic** expostos em chat. Ainda não rotacionados (CONNECT-REPORT l.34).
- O ponto ARQUITETURAL: o vazamento aconteceu porque o fluxo de deploy dos loops autônomos usa Management API **com token colado na conversa**. Enquanto esse processo existir, rotacionar chave é enxugar gelo — a próxima sessão vaza a chave nova. A correção é de processo (ADR-3), não só de credencial.

### 🟠 HIGH-1 — Parser: mitigação razoável, mas SEM detecção de quebra (falha silenciosa)

- A dívida estrutural (scraping de DOM de terceiro sem contrato: `.a4cQT`, `.NmXUuc`, `jsname="dsyhDe"`) está bem documentada no código e a estratégia atual é honesta: 3 camadas (semântico `role=region`+aria-label → `jsname=dsyhDe` → heurística avatar/diferença), e o diff local adiciona a 4ª (subida de árvore independente de classe). É o desenho certo para o problema — **não existe abordagem estruturalmente "à prova de Google"** sem trocar de fonte (ver ADR-1 para o plano B real).
- O que FALTA e é grave: quando o Google mudar o DOM, o plugin **falha em silêncio** — `tick()` engole exceções (`catch(e){}`, content.js l.118), o badge fica em "0 linhas" e o closer só descobre no FIM da call que perdeu a reunião inteira. Para uma ferramenta de captura de calls de venda reais, **falha silenciosa é o pior modo de falha possível**. Falta um canário: "capturando há 30s, legenda visível, zero linhas parseadas → alertar AGORA".
- Risco pontual no diff novo: a heurística de subida de árvore aceita ancestral com `len < text.length + 80` (caption-parser.js l.108). Com 2 turnos curtos visíveis simultaneamente (caso real de call com 2+ pessoas), um ancestral que contém DOIS turnos pode caber nos +80 chars → falante errado. É exatamente o cenário "call com 2+ pessoas reais" que nunca foi testado. Não é motivo pra reverter — é motivo pra testar antes de commitar (S1).

### 🟠 HIGH-2 — Envio pro CRM: fire-and-forget num momento de valor máximo

- `sendToCRM()` (content.js l.284-300) é 1 fetch sem retry, sem timeout, sem idempotência, sem estado persistente:
  - **Rede caiu / função fria demorou** → `catch` → flash de 1,6s "Erro de rede" e nada mais. A transcrição não se perde (está no storage), mas o closer que fechou a aba achando que enviou perdeu a análise.
  - **Duplo clique** → 2 reuniões duplicadas no CRM (nenhum guard, nenhuma idempotency key).
  - **Enviou com sucesso** → flash de 1,6s e o painel volta ao normal; não há registro visível de "esta reunião JÁ foi enviada". Reenvio acidental = duplicata de novo.
- O elo mais fraco do fluxo ponta-a-ponta está justamente na transição de maior valor (captura → CRM).

### 🟠 HIGH-3 — Timestamps: a promessa da Fase 3 do Sales Coach NÃO está sendo cumprida

- `sales-coach-fase3-ARCHITECTURE.md` §1 afirma: *"Plugin já captura transcrição AO VIVO com timestamp real… desbloqueia o Replay Timeline sem trabalho extra"*. É meia-verdade: cada turno TEM `at: Date.now()` (content.js l.110), mas **`asText()` (l.148-153) descarta os timestamps** — o que chega ao CRM é texto puro `Nome: fala`. A Fase 3e vai quebrar nessa premissa.
- Fix barato (formatar `[hh:mm:ss]` relativo ao início no export) e desbloqueio grande. É o achado com melhor razão custo/valor do diagnóstico.

### 🟡 MEDIUM-1 — Identidade da reunião: sala recorrente contamina a call seguinte

- `meetingId = location.pathname` (content.js l.13) → `STORE_KEY` idem. Salas recorrentes do Meet **reusam o mesmo código de sala**: a call de hoje carrega a transcrição da call da semana passada (`load()` no boot), e o "⬆ CRM" envia as duas misturadas. Além disso, transcripts antigos ficam no `chrome.storage.local` para sempre (sem TTL/limpeza).

### 🟡 MEDIUM-2 — Testes: simulador ad-hoc, sem comando, sem DOM real

- `tests/simulator.html` + `driver.js` são um bom começo (testam o parser real com legenda rolante), mas: (a) rodam via invocação manual de Chrome headless `--dump-dom` que só existiu na sessão do loop — **não há comando reproduzível** (`npm run test:parser` não existe); (b) o driver reimplementa uma lógica de commit por estabilidade que **não é a do content.js atual** (que usa identidade de nó via `data-arvex-id`) — o teste valida um pipeline que não é o de produção; (c) as fixtures são HTML inventado (`rowImg()`), não o DOM real do Meet — sendo que o botão 🐞 (copyDebug) já existe exatamente pra capturar DOM real e nunca foi usado pra gerar fixture versionada.
- Dado que a fonte de dados é um DOM de terceiro instável, **teste de regressão com fixture real é a única defesa barata** que existe. Sem isso, cada mudança do Google vira depuração ao vivo em call de venda.

### 🟡 MEDIUM-3 — Render O(n) por tick + perda de seleção de texto

- `renderTranscript()` reconstrói `innerHTML` da lista inteira a cada tick de 700ms. Em call de 1h (centenas de turnos): trabalho de DOM crescente e — bug concreto de UX — **qualquer seleção de texto que o usuário fizer na lista é destruída a cada 700ms** (impossível copiar um trecho durante a gravação). Basta reconciliação incremental (atualizar só o último grupo / append).

### 🟡 MEDIUM-4 — CC manual + começo de call às cegas

- O usuário precisa lembrar de ligar o CC **e** clicar "▶ Transcrever". Se esquecer qualquer um dos dois, o resultado é o mesmo silêncio do HIGH-1. O botão de legendas do Meet é clicável programaticamente (aria-label estável e multi-idioma, mesma classe de fragilidade que o parser já aceita) — auto-ligar CC ao iniciar captura remove o passo mais esquecível.

### 🔵 LOW (agrupados)

- Observer do `start()` só se anexa se a região já existe e nunca re-anexa se o Meet recriar o nó — o poll de 700ms cobre, então o observer hoje é quase decorativo. Aceitável; documentar.
- Se o usuário disser o próprio nome no início da fala ("Vitor, tudo bem?" dito POR outro Vitor), o strip de nome vazado (diff novo) pode comer a palavra. Raro; anotar no teste S1.
- `popup.js` duplica copy/download do painel; versão fixa `0.1.0` sem changelog; código só existe local (push pendente).

### Lacuna de percepção (o "não tá redondo" que o Vitor sente) — ARVEX vs Tactiq

O painel ARVEX **funciona**, mas comunica quase nada sobre o estado do sistema; o Tactiq comunica estado o tempo todo. Lado a lado:

| Dimensão | Tactiq | ARVEX hoje |
|---|---|---|
| Status do sistema | Fileira de ícones sempre visível (gravando, nuvem, escudo) | Só o botão "● Gravando" pulsando |
| Legenda/idioma | Badge "Transcrição: Portuguese (Brazil)" + Mudar | Nada — se o CC tá desligado, silêncio |
| Empty state | Caixa desenhada com instrução clara | 2 linhas de texto cinza |
| Estrutura | Mini-app com abas (Transcrição / IA) + seção Notas | Lista única + footer apinhado |
| Ações | Barra inferior limpa (3 ícones) + CTA claro | 5 botões-ícone crípticos (⧉⤓🗑🐞) espremidos com o campo Cliente |
| Pós-ação | Estado persistente | Flash de 1,6s e some |

A diferença de percepção não é feature — é **feedback de estado contínuo + hierarquia**. É isso que o redesign (ADR-7) ataca.

---

## 3. Decisões arquiteturais (ADRs)

### ADR-1 — Resiliência ao DOM do Meet: manter scraping em camadas + canário de captura + plano B documentado (não construído)

- **Decisão:** o scraping em camadas ATUAL (semântico → `jsname` → heurística estrutural do diff) é a arquitetura correta e fica. Não existe seletor imune ao Google; a resposta estrutural certa não é "seletor melhor", é **detectar a quebra em segundos e degradar com alerta**:
  1. **Canário runtime:** se `capturing && findRegion()!==null && 0 linhas novas há 30s` OU `capturing && findRegion()===null há 15s` → badge de erro no painel ("⚠ Legenda não detectada — ligue o CC" / "⚠ Parser desatualizado — toque para copiar diagnóstico") que aciona o `copyDebug()` já existente. A falha silenciosa (HIGH-1) morre aqui.
  2. **Loop de calibração formalizado:** fixture real capturada pelo 🐞 vira arquivo versionado em `tests/fixtures/` (ADR-2). Cada quebra futura do Google = 1 fixture nova + ajuste em `caption-parser.js` + regressão verde. O botão 🐞 sai do footer e vai pro estado de erro (só aparece quando é útil).
- **Plano B estratégico (documentar, NÃO construir agora):** se o Google matar estruturalmente as legendas scrapeáveis, a rota é **captura de áudio da aba (`chrome.tabCapture`) + STT local** — que é exatamente o motor do WhisperFlow próprio (`docs/ferramentas-proprias/whisperflow-proprio/`). A empresa já está construindo o componente que elimina essa dependência; não duplicar esforço antecipando.
- **Descartado:** interceptar o data channel interno do Meet (protobuf via WebRTC) — mais frágil que o DOM, pior em ToS, e ninguém no time mantém isso.

### ADR-2 — Testes: harness reproduzível com fixtures reais, testando o pipeline de PRODUÇÃO

- **Decisão:** transformar `tests/` em regressão executável por comando único:
  - `tests/run.js` (Node + Chrome headless via `--dump-dom`, mesmo truque já validado no OPTIMIZE, agora scriptado) OU jsdom se `:has()` suportar — decisão de implementação do @dev, critério: rodar com `node tests/run.js` em <15s, exit code ≠0 em falha.
  - **O driver passa a exercitar `upsertRow`/`bestText` reais do content.js** (extrair essas 3 funções puras pra um `transcript-core.js` compartilhado entre content.js e teste — refactor mínimo, sem build step: `content.js` continua funcionando, só passa a ler de `window.ArvexTranscriptCore` como já faz com o parser).
  - **Fixtures:** manter os cenários sintéticos A/B/C + adicionar `fixtures/real-*.html` capturadas com o 🐞 em call real (mínimo: 1 falante PT, 2 falantes PT, turno sem avatar). Fixture real é o contrato de fato com o DOM do Meet.
- **Racional:** com fonte de dados sem contrato, o teste de fixture é o único "contrato" possível. Sem CI pesado — é 1 comando local que o @dev roda antes de cada commit no parser.

### ADR-3 — Credenciais: shared-secret no ingest + rotação + regra de processo

- **Decisão em 3 níveis:**
  1. **Rotacionar/revogar JÁ (Vitor, ~10 min, guiado):** access token Supabase (Account → Access Tokens → revoke) e chave Anthropic (console → rotate). Pré-requisito de qualquer push.
  2. **`ingest-meeting` passa a exigir `x-arvex-key`** (secret ≥32 chars em env var da função via `supabase secrets set`; comparação constant-time). A extensão NÃO embute o secret no código: campo "Chave de envio (CRM)" no popup → `chrome.storage.local` (mesmo padrão do e-mail). Requisição sem/da chave errada → 401. Adicional na função: cap de tamanho do transcript (ex. 200KB) e rejeição de body malformado — fecha o vetor "queimar créditos Anthropic".
  3. **Regra de processo (a correção do PADRÃO):** deploy de Edge Function em sessão de agente usa token lido de env/secret local (`SUPABASE_ACCESS_TOKEN` no ambiente), **nunca colado no chat**. Registrar em memória de projeto. Sem isso, CRITICAL-2 se repete a cada loop autônomo.
- **Descartado:** auth por JWT de usuário logado no CRM (exigiria fluxo de login na extensão — peso desproporcional pro tamanho do time); OAuth/identity do Chrome (idem).

### ADR-4 — Envio confiável: idempotência + retry + estado persistente "enviado"

- **Decisão:** o POST pro CRM ganha:
  - **Idempotency key** = `meetingId + data(YYYY-MM-DD)` enviada no body (`client_key`); `ingest-meeting` faz upsert por essa chave (coluna `client_key` unique em `meetings`, nullable — aditivo, não quebra ingestão manual). Duplo clique e retry deixam de gerar duplicata **no servidor**, que é onde importa.
  - **Retry com backoff** (3 tentativas: 0s/2s/6s, timeout 15s por tentativa) + botão desabilitado com spinner durante o envio.
  - **Estado persistente por reunião:** `arvex_sent_{meetingId+data}` no storage → painel mostra badge "✓ Enviada ao CRM às hh:mm"; reenviar vira ação explícita ("Reenviar"), não acidente.
- **Racional:** transforma o momento de maior valor do produto de fire-and-forget em transação com confirmação visível.

### ADR-5 — Identidade da reunião + timestamps no export

- **Decisão:**
  - `meetingId = pathname + "_" + YYYY-MM-DD` (data local do boot do content script). Sala recorrente deixa de contaminar a call seguinte.
  - **Limpeza:** no boot, remover do storage chaves `arvex_transcript_*` com `at` mais recente >7 dias.
  - **Export com timestamps:** `asText()` passa a emitir `[hh:mm:ss] Nome: fala` (relativo ao primeiro turno). O painel mostra hora absoluta discreta no cabeçalho de cada grupo de falante. **Isto cumpre a premissa da Fase 3e do Sales Coach** (Replay Timeline) — alinhar com `analyze-meeting` que o formato com `[..]` não quebra o prompt (teste E2E no S3).
- **Racional:** HIGH-3 + MEDIUM-1 se resolvem juntos porque compartilham a mesma raiz (identidade temporal da reunião).

### ADR-6 — Auto-CC ao iniciar captura

- **Decisão:** ao clicar "Transcrever", se `findRegion()===null`, tentar ligar o CC programaticamente: botão por `aria-label` (regex multi-idioma `ligar legendas|turn on captions|ativar legendas...`, mesma técnica do `detectSelfName`) → `click()` → aguardar até 3s pela região. Sucesso → segue; falha → badge "⚠ Ligue a legenda (CC)" (canário do ADR-1 cobre o caso contínuo).
- **Racional:** é a pendência nº1 do Vitor; mesma classe de fragilidade que o produto já aceita (aria-label é ordens de magnitude mais estável que classe ofuscada). **Descartado:** auto-iniciar a captura sozinho ao entrar na call — decisão de gravar tem peso de consentimento/etiqueta; fica manual (1 clique) por escolha de produto, não por limitação.

### ADR-7 — Redesign do painel: nível Tactiq, sem os elementos de venda de plano

**Princípio: adotar do Tactiq a comunicação contínua de estado e a hierarquia de mini-app; descartar tudo que só existe porque o Tactiq vende assinatura.**

| Elemento do Tactiq | Veredito | Justificativa |
|---|---|---|
| Fileira de ícones de status no topo | **ADOTAR (adaptado)** | É o que dá sensação de "sistema vivo": ● rec, estado CC, estado CRM, ⚙ |
| Linha de cota "6 reuniões restantes" | **DESCARTAR** | ARVEX não tem plano/cota; cota fake é ruído |
| CTA "⚡ Melhoria" (upgrade) | **DESCARTAR** | Idem — não há o que vender pro próprio time |
| Abas "Transcrição / Pergunte à IA" | **ADOTAR (adaptado)** | 2 abas: **Transcrição / Notas**. Aba de IA NÃO: o "Chat com a call" já está decidido pra viver no CRM (Fase 3b do Sales Coach) — duplicar no plugin criaria 2ª superfície de IA pra manter |
| Badge de idioma "Transcrição: Portuguese (Brazil)" | **ADAPTAR** | Vira o **badge de estado do CC/captura** — mais útil que idioma: "Legendas ativas · PT-BR" / "⚠ Ligue o CC" (com botão Ligar = ADR-6) / "⚠ Parser desatualizado" (canário ADR-1) |
| Empty state desenhado (caixa amarela) | **ADOTAR** | Caixa com borda âmbar, logo ARVEX, 3 passos numerados (CC → Transcrever → falar). Substitui as 2 linhas cinza atuais |
| Seção NOTAS com textarea | **ADOTAR** | Alto valor real: closer anota durante a call; conteúdo persiste por reunião (storage) e **vai no payload do ⬆ CRM** (`notas` — campo novo aditivo no ingest) |
| Barra inferior de 3 ícones | **ADOTAR (adaptado)** | Footer em 2 níveis, ver estrutura abaixo |
| Botão de pausar circular | **ADOTAR** | O toggle atual vira o elemento primário e central do footer |

**Estrutura alvo do painel (hierarquia decidida; @dev não redecide):**

```
#arvex-panel (mantém: fixed right, 340px, dark #0E1420, radius 14, z-max)
├─ #arvex-head          ARVEX(logo pill) · "Meet Transcriber" · [●rec] [☁crm] [⚙] [–]
│                        ●rec: cinza=parado, vermelho pulsando=gravando
│                        ☁crm: cinza=nunca enviou, verde=✓ enviada, amarelo=enviando, vermelho=falhou
│                        ⚙: abre o popup-config inline (nome, e-mail, chave de envio — migra do popup)
├─ #arvex-status        badge full-width, 1 dos estados: (oculto se tudo ok e gravando)
│                        [ℹ Legendas ativas]  [⚠ Ligue o CC — (Ligar)]  [⚠ Sem captura há 30s — (Diagnóstico)]
├─ #arvex-tabs          [ Transcrição ]  [ Notas ]   (aba ativa: fundo claro, como no Tactiq)
├─ #arvex-list          (aba 1) grupos por falante — MANTÉM o layout do diff local:
│                        .arvex-group > .arvex-sp (verde, + hora hh:mm à direita, discreta) > .arvex-tx*
│                        empty state: caixa âmbar com 3 passos (ver acima)
│   #arvex-notes        (aba 2) textarea flex:1, placeholder "Anote aqui — vai junto pro CRM",
│                        autosave no storage por reunião
└─ #arvex-foot          nível 1: [⏺/⏸ botão primário largo]  [⧉] [⋯ menu: Baixar .txt · Limpar]
                         nível 2: [input Cliente] [⬆ Enviar ao CRM]  → após sucesso vira "✓ Enviada · Reenviar"
```

- 🐞 sai do footer (vive no badge de diagnóstico); 🗑 Limpar vai pro menu ⋯ (ação destrutiva não merece botão de 1º nível); popup do Chrome fica só como atalho de config/estado (a config migra pro ⚙ do painel — 1 lugar só).
- Tokens visuais: manter paleta atual (#0E1420 / #5B6CFF / #86E5A0 / #3FB950), radius 14/8, system-ui. O que muda é hierarquia e estado, não identidade.

---

## 4. Plano de execução (stories em série; commits `feat(meet-transcriber): S{n} — {resumo}`)

> Regra: nenhuma story declara pronto sem executar a verificação. S0 bloqueia o push; S1 bloqueia commit do diff local que já está no working tree.

### S0 — Segurança: rotação + shared-secret no ingest (½ sessão + 10 min do Vitor)

**Fazer:** guiar o Vitor na revogação do access token Supabase e rotação da chave Anthropic (1 passo por vez) · `supabase secrets set ARVEX_INGEST_KEY=...` · `ingest-meeting` valida `x-arvex-key` (401 sem/errada) + cap 200KB no transcript · extensão: campo "Chave de envio" no popup/⚙, header no fetch · registrar a regra de processo do ADR-3.3 na memória do projeto.
**Pronto quando:**
- [ ] `curl` sem header → 401; com header certo → `{ok, meeting_id}` e reunião analisada no CRM (E2E igual ao do CONNECT).
- [ ] Token antigo Supabase testado → inválido; chave Anthropic antiga testada → inválida.
- [ ] Nenhum secret novo aparece em arquivo do repo (`grep` por prefixos de chave no diff).

### S1 — Validar o diff local + harness de regressão (1 sessão)

**Fazer:** extrair `bestText`/`mergeRolling`/`upsertRow` pra `transcript-core.js` (carregado antes do content.js no manifest) · `tests/run.js` executável (`node tests/run.js`) rodando parser REAL + core REAL contra cenários A/B/C · capturar com o 🐞 pelo menos 1 fixture real (call de teste rápida do Vitor ou call 2p do S6 se antes não houver) e versionar em `tests/fixtures/` · caso sintético novo cobrindo o risco do +80 chars (2 turnos curtos simultâneos) · rodar tudo verde → **commitar o diff local junto com o harness**.
**Pronto quando:**
- [ ] `node tests/run.js` → exit 0, imprime transcrição esperada por cenário; sabotar 1 seletor → exit ≠0.
- [ ] Cenário "2 turnos curtos simultâneos" atribui os falantes certos.
- [ ] Diff local commitado (parser+core+styles) com testes verdes no mesmo commit.

### S2 — Envio confiável (½–1 sessão)

**Fazer:** ADR-4 completo: `client_key` no body + coluna unique nullable em `meetings` + upsert na função · retry 3× com backoff e timeout · estado `arvex_sent_*` + badge ✓/Reenviar · botão com spinner/disabled durante envio.
**Pronto quando:**
- [ ] Clicar ⬆ CRM 2× rápido → **1** reunião no banco.
- [ ] Simular offline (DevTools → Offline) no clique → UI mostra falha após retries; voltar online e reenviar → sucesso, mesma `client_key`, ainda 1 reunião.
- [ ] Recarregar a página após envio → painel ainda mostra "✓ Enviada".

### S3 — Identidade temporal + timestamps (½ sessão)

**Fazer:** ADR-5: `meetingId` com data · limpeza >7 dias no boot · `asText()` com `[hh:mm:ss]` relativo · hora nos cabeçalhos de grupo · E2E: enviar transcript com timestamps e conferir que `analyze-meeting` analisa normalmente.
**Pronto quando:**
- [ ] Simular sala recorrente (mesmo pathname, mudar data do relógio ou mockar) → transcrições separadas.
- [ ] `.txt` baixado tem `[hh:mm:ss]` em toda linha; reunião enviada com timestamps é analisada (status done) no CRM.
- [ ] Chave antiga fake com `at` de 8 dias some do storage após reload.

### S4 — Auto-CC + canário de captura (½ sessão)

**Fazer:** ADR-6 (clicar CC via aria-label ao iniciar, espera 3s) · canário ADR-1.1 (badge ⚠ nos 2 modos: sem região 15s / região sem linhas 30s) · badge aciona `copyDebug`.
**Pronto quando:**
- [ ] Num Meet real com CC desligado: clicar Transcrever → CC liga sozinho e captura começa (observar de fato).
- [ ] Desligar o CC no meio da gravação → badge ⚠ aparece em ≤15s; religar → badge some.
- [ ] Botão Diagnóstico copia HTML da região pro clipboard.

### S5 — Redesign do painel (1 sessão)

**Fazer:** estrutura do ADR-7 exatamente como especificada (head com ícones de estado, badge de status, abas Transcrição/Notas, empty state âmbar, footer 2 níveis, config no ⚙, notas no payload `notas` do ingest — campo aditivo na função) · render incremental da lista (MEDIUM-3: append/patch do último grupo em vez de rebuild total).
**Pronto quando:**
- [ ] Screenshot do painel nos 4 estados: vazio (caixa âmbar) · gravando (● vermelho + badge oculto) · alerta CC · pós-envio (✓).
- [ ] Nota digitada persiste a F5 e chega em `meetings` (conferir no banco).
- [ ] Selecionar texto na transcrição DURANTE a gravação → seleção sobrevive aos ticks; call simulada com 300+ turnos rola sem travar.

### S6 — Teste ao vivo 2+ pessoas + push (call real do Vitor + @devops)

**Fazer:** call real com 2+ participantes seguindo checklist: auto-CC → captura → falantes corretos (validar a heurística nova ao vivo) → troca rápida de falante → nota → envio → ✓ → conferir reunião analisada com timestamps no CRM. Se falante errar: capturar fixture com o botão Diagnóstico → ajustar parser → regressão S1 verde → repetir. Depois: **@devops faz o push** (S0 já garantiu que não há secret no código).
**Pronto quando:**
- [ ] Transcrição da call 2p legível, falantes 100% corretos, reunião no CRM com análise done e notas.
- [ ] Repo remoto atualizado (push feito por @devops), `manifest.json` bump pra `0.2.0`.

---

## 5. O que NÃO fazer (anti-overengineering)

- ❌ Reescrever a captura sobre `tabCapture`+Whisper agora — é o plano B documentado (ADR-1), acionado só se o Google quebrar estruturalmente as legendas.
- ❌ Aba de IA/chat no painel — o Chat-com-a-call vive no CRM (Fase 3b); o plugin é braço de CAPTURA.
- ❌ Login/JWT na extensão, Chrome Web Store, service worker de background, framework de UI, build step — peso desproporcional pro time de 1 + agentes.
- ❌ Interceptar data channel interno do Meet — mais frágil e pior em ToS que o DOM.
- ❌ Auto-iniciar gravação sem clique — decisão de etiqueta/consentimento, fica manual por design.

## Mapa de dependências e estimativa

`S0 → S1 → S2 → S3 → S4 → S5 → S6` (serial; S0 e S1 destravam o resto; S6 é o gate final humano).
Total: ~4-5 sessões de @dev (Sonnet/Opus) + ~10 min do Vitor (S0) + 1 call real (S6). Nenhuma story exige Fable — todas as decisões estão tomadas neste dossiê.
