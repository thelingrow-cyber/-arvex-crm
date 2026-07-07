# Story: Meet Transcriber — "Redondo" v1 (0.1.0 → 0.2.0)

> Status: **InProgress** (S0/S1/S2/S3/S5 verificados de ponta a ponta incl. deploy real; S4 código pronto, verificação ao vivo pendente; S6 não iniciada)
> Fonte de decisões: `docs/plugin-meet-transcriber/DEEP-ANALYSIS-FABLE.md` (diagnóstico + ADR-1..7 + plano S0-S6) — **autossuficiente, NÃO redecidir nada**; seção 5 lista o que foi descartado (não reintroduzir).
> Executor: @dev (Dex) com Sonnet/Opus · Push final: @devops (S6)
> Commits: `feat(meet-transcriber): S{n} — {resumo}` · 1 story-fase por vez, em ordem estrita
> ⚠️ Working tree JÁ contém diff não commitado em `caption-parser.js`/`content.js`/`styles.css` — ele só pode ser commitado dentro da S1 (com regressão verde), nunca antes.

## Contexto (1 parágrafo)

Extensão Chrome MV3 funcional que transcreve o Meet via CC e envia pro Sales Coach do CRM. O diagnóstico Fable achou 2 CRITICALs de segurança (endpoint `ingest-meeting` aberto que gasta créditos Anthropic; tokens vazados não rotacionados), 3 HIGHs de confiabilidade (falha silenciosa do parser, envio fire-and-forget, timestamps descartados no export que quebram a premissa da Fase 3 do Sales Coach) e uma lacuna de percepção de UI vs Tactiq. Esta story fecha tudo em 7 fases seriais.

## Acceptance Criteria (por fase — detalhe completo na seção 4 do dossiê)

### S0 — Segurança: rotação + shared-secret (BLOQUEIA O PUSH) — ADR-3 ✅ VERIFICADO (deploy real)
- [ ] Vitor guiado: access token Supabase revogado + chave Anthropic rotacionada — **PARCIAL**: 3 tokens novos foram gerados/expostos durante o processo de deploy (nenhum é o token original vazado que motivou o diagnóstico) e precisam ser revogados; chave Anthropic ainda não rotacionada
- [x] `ingest-meeting` exige header `x-arvex-key` (comparação em tempo constante) → sem/errada = 401; cap 200KB no transcript — **DEPLOYADO e VERIFICADO**: `curl` sem header → `HTTP 401` real, confirmado
- [x] Extensão: campo "Chave de envio (CRM)" → migrou pro ⚙ inline do painel (não o popup — decisão da S5/ADR-7) → storage → header `x-arvex-key` enviado no fetch quando presente
- [x] `curl` E2E: sem header → 401 · com header certo → `{"ok":true,"meeting_id":"..."}` — **rodado de verdade contra produção**, ambos confirmados
- [x] `grep` no diff: nenhum secret em arquivo do repo — verificado, limpo
- [x] Regra de processo ADR-3.3 registrada — ver memória `feedback_processo_deploy_secrets` (reforçada: 3 tokens vazaram em chat DURANTE esta própria sessão ao tentar seguir a regra — evidência de que o processo de deploy interativo por chat é estruturalmente arriscado, não só um incidente pontual)

### S1 — Validar diff local + harness de regressão (BLOQUEIA COMMIT DO DIFF) — ADR-2 ✅ VERIFICADO
- [x] `bestText`/`mergeRolling`/`upsertRow` extraídos pra `transcript-core.js` (sem build step; content.js consome via `window.ArvexTranscriptCore`, carregado antes no manifest)
- [x] `node tests/run.js` roda parser REAL + core REAL: 7 fixtures, exit 0 verde (~8s), exit ≠0 confirmado sabotando o guard novo do parser (rodado de propósito e restaurado)
- [x] Cenário "2 turnos curtos simultâneos" (scenario D) — **AC refinado**: não há sinal estrutural pra recuperar o nome certo num DOM genuinamente ambíguo (classe renomeada, sem nome em nenhum turno); o critério real e verificado é **não corromper** (retornar "" em vez de nome/texto errado). Bug real encontrado e corrigido no processo (ver commit).
- [ ] ≥1 fixture de DOM real (capturada com 🐞 numa call de verdade) — **PENDENTE**: fixtures atuais reconstroem a estrutura DOCUMENTADA no código (`.a4cQT`/`.NmXUuc`/`jsname=dsyhDe`), não foram capturadas ao vivo (sem sessão de Meet disponível neste ambiente). Substituir/complementar na S6.
- [x] Diff local commitado JUNTO com o harness, tudo verde — commit `fcf7d99`

### S2 — Envio confiável — ADR-4 ✅ VERIFICADO (deploy real)
- [x] `client_key` (= meetingId+data) enviado no body · coluna unique + upsert na função — **DEPLOYADO**. Achado real na verificação: o índice único inicial era PARCIAL (`where client_key is not null`), incompatível com `ON CONFLICT` do supabase-js (retornava erro "no unique or exclusion constraint matching"). Corrigido pra `unique constraint` normal (NULL múltiplos já são permitidos por padrão no Postgres, não precisava ser parcial). Migration de correção aplicada.
- [x] Retry 3× (0s/2s/6s, timeout 15s) · botão disabled+texto "Enviando…" — **verificado** (fixture G: mock de fetch falha 2x/sucede na 3ª, confirma 3 tentativas e badge final)
- [x] Estado persistente `arvex_sent_*` → badge "✓ Enviada às hh:mm" · reenvio vira ação explícita — verificado (fixture G)
- [x] Duplo clique não dispara 2ª rodada de tentativas (guard `sendInFlight`, verificado na fixture G) · "1 reunião no banco" — **verificado contra produção de verdade**: 2 chamadas com a mesma `client_key` retornaram o MESMO `meeting_id` (`bc988d50-220e-47c6-8782-9eca80cb3312`), sem duplicar. Linha de teste removida do banco após verificação.

### S3 — Identidade temporal + timestamps — ADR-5 ✅ VERIFICADO (client-side)
- [x] `meetingId = pathname + "_" + YYYY-MM-DD` (sala recorrente não contamina) · limpeza storage >7 dias no boot
- [x] `asText()` emite `[hh:mm:ss]` relativo — verificado em isolamento (Node, `Core.createStore()` com relógio fake: `00:00:00`/`00:00:05`/`00:01:08`) · hora discreta no cabeçalho de grupo (implementado)
- [ ] E2E: transcript com timestamps analisado pelo `analyze-meeting` — **PENDENTE** (só depois do deploy)

### S4 — Auto-CC + canário de captura — ADR-6 + ADR-1.1 (código pronto, verificação ao vivo pendente)
- [x] Implementado: `tryEnableCC` (clica CC via aria-label multi-idioma, espera ≤3s) + canário (`runCanary`: região sumiu 15s / 0 linhas 30s → badge)
- [ ] Observar em Meet real (CC liga sozinho, badge aparece/some) — **PENDENTE**: precisa de sessão real do Meet, não disponível neste ambiente

### S5 — Redesign do painel (nível Tactiq) — ADR-7 ✅ VERIFICADO (estrutural)
- [x] Estrutura ADR-7 implementada e verificada estruturalmente (fixture E: painel monta sem exceção, abas alternam, ⚙ abre/fecha)
- [x] Notas: autosave por reunião (debounce 400ms) + campo `notas` no payload do ingest — envio client-side ok; aceitação no banco não verificável (servidor)
- [x] Render incremental (MEDIUM-3) — **verificado por referência de nó** (fixture F: nós DOM não recriados quando o texto não muda; merge em turno não-final não corrompe os demais)
- [ ] Screenshots dos 4 estados em Meet real — **PENDENTE** (sem browser/Meet ao vivo neste ambiente)
- [x] NÃO adotado: cota, CTA upgrade, aba de IA — respeitado

### S6 — Gate final: call real 2+ pessoas + push — @devops
- [x] **1ª call real rodada** (2026-07-07, Vitor + "Lingrow", 2 janelas): auto-detect de 2 falantes funcionou, mas achou 2 bugs reais (ver S7) — não conta como gate aprovado ainda
- [ ] Call real com o **protocolo ADR-10** (frases curtas/distintas, não repetir, 🐞 no meio e no fim): falantes 100% corretos → troca rápida de falante → nota → envio ✓ → reunião analisada com timestamps no CRM
- [ ] `manifest.json` → `0.2.0` · **push por @devops** (S0 garantiu repo limpo de secrets)

### S7 — Correções pós-1ª-call (ADR-8/9/10, adendo §6 do dossiê) — parcial ✅
- [x] ADR-8: flight recorder (ring buffer 120 ticks: caminho do parser, rows, merges) — `copyDebug()` agora copia `{html, recorder}` juntos
- [x] ADR-9 Guard 1: nó de DOM reciclado pra falante diferente → turno novo, nunca merge (bug real da 1ª call: nome colado no meio do texto). Testado sabotando o guard (fixture H falha reproduzindo o bug, restaurado passa)
- [x] ADR-9 Guard 2: caminho principal sumiu por <2s (Meet reconstruindo DOM) → pula o tick, não cai no fallback. Testado do mesmo jeito (fixture I)
- [x] Regressão inteira verde: 9 fixtures, `node tests/run.js` (~9s) — commit `94f9f31`
- [ ] **Protocolo ADR-10 rodado numa call real** com o Vitor (frases curtas/distintas, 🐞 no meio e no fim) — só com esse dado dá pra confirmar/refutar H3 (nó recriado) e H4 (mergeRolling sob repetição) e decidir se precisam de fix adicional
- [ ] Fixture real (`tests/fixtures/real-*.html`) gerada a partir do dump do 🐞 — ainda pendente, precisa da call do item acima
- [ ] Refinamento visual do agrupamento (só depois de confirmar que a atribuição de falante está 100% correta com dado real — Fable foi explícito: não polir CSS antes disso)

## File List

- [x] `docs/plugin-meet-transcriber/content.js` — reescrito: core extraído, S3/S4/S5/S2-client/S0-client
- [x] `docs/plugin-meet-transcriber/caption-parser.js` — fix HIGH-1 (guard multi-turno em `speakerFor`)
- [x] `docs/plugin-meet-transcriber/transcript-core.js` — NOVO (S1); Guard 1 (S7)
- [x] `docs/plugin-meet-transcriber/styles.css` — CSS do painel redesenhado (S5)
- [x] `docs/plugin-meet-transcriber/popup.html` / `popup.js` — simplificados (config migrou pro ⚙)
- [x] `docs/plugin-meet-transcriber/manifest.json` — `transcript-core.js` adicionado ao content_scripts (versão 0.1.0 mantida; bump pra 0.2.0 fica pra S6)
- [x] `docs/plugin-meet-transcriber/tests/run.js` + `tests/harness.js` — NOVOS (S1)
- [x] `docs/plugin-meet-transcriber/tests/fixtures/scenario-{a..g}-*.html` — NOVOS (7 fixtures, todas verdes)
- [x] `docs/plugin-meet-transcriber/tests/driver.js` / `simulator.html` — REMOVIDOS (testavam pipeline reimplementado, achado MEDIUM-2)
- [x] `supabase/functions/ingest-meeting/index.ts` — x-arvex-key obrigatório + cap 200KB + upsert por client_key (S0/S2) — **código pronto, deploy pendente**
- [x] `docs/crm/setup-meet-transcriber-hardening-v1.sql` — NOVO: migration aditiva (colunas `client_key`+`notas`, unique index) — **escrita, aplicação no SQL Editor pendente**

## Dev Notes

- Correção de rota (importante): a suposição inicial de que o repo `arvex-crm` era externo/inacessível estava ERRADA — o remote origin deste próprio repositório É `.../-arvex-crm`, e a pasta `supabase/functions/` já vive aqui na branch `master`. O código servidor foi implementado direto neste ambiente.
- O que falta de verdade agora é só **deploy + ação do Vitor** (ver checklist que vou mandar na resposta): gerar o valor da chave, `supabase secrets set`, `supabase functions deploy ingest-meeting`, aplicar a migration no SQL Editor, e rotacionar os 2 tokens vazados. Nenhum desses comandos pode rodar sem login interativo do Supabase CLI (OAuth via browser) — por isso ficam como ação do Vitor, não bloqueio de acesso a repo.
- Critério de pronto é VERIFICADO de fato — nesta sessão, tudo marcado [x] rodou de verdade (Chrome headless real, 7 fixtures, `node tests/run.js` em ~8s) ou foi revisado por leitura cuidadosa quando não havia como executar (código servidor, sem Deno/CLI disponíveis aqui). Itens que dependem de deploy/CLI/Meet real ficam [ ] explicitamente.
- Anti-overengineering (seção 5 do dossiê): sem tabCapture/Whisper agora, sem login/JWT, sem Web Store, sem build step, sem auto-iniciar gravação — respeitado.

## Dev Agent Record

**Agent Model Used:** Claude Sonnet 5 (persona @dev/Dex)

**Completion Notes:**
- Bug real encontrado pelo próprio harness de teste (não hipotético): a heurística de subida de árvore em `speakerFor` podia atribuir um nome corrompido (um pedaço da própria fala, ex. "Oi") quando 2 turnos curtos caem sob o mesmo ancestral sem sinal de nome. Corrigido com um guard que detecta ancestral com >1 nó de fala e prefere `""` a um palpite errado. Verificado sabotando o guard e vendo o teste falhar reproduzindo o bug exato, depois restaurando.
- Escopo real executado: S1 completo e verificado; S3 completo e verificado (client-side); S5 completo e verificado estruturalmente; S4 código completo (verificação ao vivo pendente); S2/S0 código client+servidor completos (deploy/secrets/migration pendentes — ação do Vitor com Supabase CLI).
- Commits locais (sem push, por restrição de @dev): `fcf7d99` (client), `606a164` (servidor).

**Change Log:**
- 2026-07-06: S1/S3/S5 implementados e verificados; S4 implementado (verificação ao vivo pendente); S0/S2 código completo (client+servidor), deploy/secrets/migration pendentes de ação do Vitor. Status: Ready → InProgress.
