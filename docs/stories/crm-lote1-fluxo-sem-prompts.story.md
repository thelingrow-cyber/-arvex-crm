# Story CRM-UX-001 — Lote 1: fluxo sem prompts nativos (F1, F2, F8, F9)

**Tipo:** Brownfield enhancement (CRM ARVEX — sem epic formal)
**Status:** Done
**Owner:** @dev (Dex) — frontend puro, sem SQL
**Criado:** 2026-07-12 por @sm (River)
**Validado:** 2026-07-12 por @po (Pax) — score 8/10 **GO** (AC3 reescrito: RLS admin-only + FK ON DELETE SET NULL invalidavam o undo original)
**Solicitante:** Vitor (founder ARVEX)
**Fonte:** `docs/crm/UX-IMPROVEMENT-PLAN.md` §3 (findings) e §4 (Lote 1) — auditoria Fable 5, marcada autossuficiente
**Repositório:** `thelingrow-cyber/-arvex-crm` · Deploy: `arvex-crm.vercel.app`
**Arquivo alvo:** `docs/crm/index.html` (master) → publicação por cópia para `index.html` (main)
**Complexidade:** M — frontend ~2-3h + QA visual ~30min
**Prioridade:** Alta (F2 inutiliza o Relatório por Expert hoje)
**Predecessor:** Lote 0 (`b4b0a6f`) já em produção — `showToast()`, `closeTopModal()`, `MODAL_CLOSERS` e Esc/overlay já existem e DEVEM ser reutilizados.

---

## Business Value

As transições mais usadas do CRM rodam em caixinha nativa do browser (`prompt`/`confirm`): mover card para Perdido, Call, Follow Up e Fechado. Isso (a) quebra o visual premium, (b) é péssimo no mobile — onde SDR e CS mais operam, e (c) no caso do **motivo de perda em texto livre**, destrói o dado: `renderExperts()` agrupa por string exata, então "Sem budget" ≠ "sem budget" ≠ "orçamento" viram buckets diferentes e o Relatório por Expert vira lixo.

**Ganho:** fluxo inteiro dentro do design system, motivo de perda agregável (relatório de perdas volta a valer), erro de clique reversível (undo) e feedback consistente em todo CRUD.

---

## Acceptance Criteria

### AC1 — Modal genérico de transição substitui os 4 `prompt()` (F1)
- [x] Novo modal único (`modal-transition`) reutilizado pelas 4 transições de `changeStatus()` (l.2175-2192), seguindo o markup dos 8 modais existentes (`.modal-overlay` > `.modal` > header/body/footer)
- [x] **Perdido:** chips de motivo (ver AC2) — obrigatório escolher
- [x] **Call:** `<input type="datetime-local">` pré-preenchido com agora (mantém o comportamento atual de `data_call`)
- [x] **Follow Up:** `<input type="text">` para `proximo_passo` (placeholder: "Ex: Ligar segunda 14h, Enviar proposta")
- [x] **Fechado:** `<input type="number">` para valor pago → grava em `ticket` (mantém o encadeamento existente: se `isFinanceiroUser()`, abre o modal de negociação depois)
- [x] Cancelar o modal **não move o card** (comportamento atual do `prompt` cancelado: `renderPipeline()` e retorna)
- [x] Reordenar dentro da mesma coluna continua NÃO abrindo modal (guarda `mudouColuna` já existe — preservar)
- [x] Modal fecha com Esc e clique no overlay (registrar em `MODAL_CLOSERS` se tiver estado pendente)

### AC2 — Motivo de perda vira chips pré-definidos (F2)
- [x] Constante única `MOTIVOS_PERDA = ['Sem budget','Não era o perfil','Não atendeu','Concorrente','Sumiu/Ghost','Outro']`
- [x] UI de chips (reutilizar padrão visual `.move-chip`, já existe no CSS l.321-323 e nunca foi usado)
- [x] "Outro" revela input de texto livre; o valor salvo é o texto digitado (não a palavra "Outro")
- [x] Sem chip selecionado → botão salvar desabilitado (não grava "Não informado" silenciosamente)
- [x] `renderExperts()` continua agrupando por `motivo_perda` sem alteração — os buckets passam a ser consistentes por construção
- [x] Leads antigos com motivo em texto livre continuam renderizando (não quebrar histórico)

### AC3 — Confirmações destrutivas viram modal + undo (F8)

> ⚠️ **Correções do @po (validação 2026-07-12) — obrigatórias.** A versão original deste AC assumia que qualquer usuário deleta lead e que re-inserir "desfaz". Ambas são falsas contra o banco real:
> - RLS `leads_delete` = `is_admin()` (setup-rls-v2-security.sql l.67). Para SDR/CS o `.delete()` do PostgREST **afeta 0 linhas e NÃO retorna erro** → hoje o ✕ falha em silêncio e o lead reaparece.
> - `vendas.lead_id` e `clientes_cs.lead_id` são FK `ON DELETE SET NULL`. Excluir órfã a venda; re-inserir gera **novo UUID** e o vínculo **não volta**.

- [x] **Guarda de permissão:** o botão ✕ só aparece para `currentRole === 'admin'` (alinha a UI com a RLS; acaba a falha silenciosa)
- [x] **Guarda de vínculo:** se o lead tem venda (`cachedVendas.some(v => v.lead_id === id)`) ou está em CS (`csLeadIds.has(id)`), NÃO excluir — toast de erro: "Lead tem venda/CS vinculado. Remova o vínculo antes de excluir."
- [x] **Delete verificado:** usar `.delete().eq('id', id).select()` e conferir que retornou 1 linha; 0 linhas → toast de erro "Sem permissão para excluir" (nunca alegar sucesso sem evidência)
- [x] Só então: toast **"Lead excluído · Desfazer"** com janela de 6s (sem `confirm()` — o undo É a rede de proteção)
- [x] "Desfazer" re-insere **preservando o `id` original** (`insert({ ...snapshot })` com o id explícito) — mantém qualquer referência futura consistente
- [x] Passados os 6s sem clique, o toast some e a exclusão é definitiva
- [x] `excluirVenda()` (l.3139-3140) troca o **duplo `confirm()`** por UM modal de confirmação (venda tem parcelas → destrutivo demais para undo silencioso; manter confirmação explícita, mas no design system)
- [x] `moverParaCS()` (l.2622), `deleteAgente()` (l.2730) e `desmarcarPago()` (l.3120) usam o mesmo modal de confirmação padrão

### AC4 — Toasts globais substituem `alert()` (F9)
- [x] Os 20 `alert()` de erro viram `showToast(msg, 'error')` (a função e o CSS `.fin-toast.error` já existem, l.3181)
- [x] Toast de sucesso em todo CRUD que hoje é silencioso: salvar lead, mover card (status alterado), registrar check CS, salvar agente
- [x] Toast não bloqueia a UI e não empilha infinito (container já limita por remoção após 3s)

### AC5 — Nenhuma regressão nos fluxos vivos
- [x] Kanban CS (Sabrina) e Pipeline continuam funcionando: drag desktop, long-press mobile, drop indicator, auto-scroll
- [x] Encadeamento Fechado → modal de negociação (financeiro) preservado
- [x] Realtime (`subscribeRealtime`) continua re-renderizando após as mudanças

---

## Tasks

- [x] **T1** — Criar `modal-transition` no HTML (1 modal, corpo dinâmico por tipo) + `MOTIVOS_PERDA`
- [x] **T2** — Refatorar `changeStatus()` para abrir o modal e continuar via callback (o `await` some; o move acontece no submit do modal)
- [x] **T3** — Chips de perda com "Outro" + validação de obrigatoriedade
- [x] **T4** — `deleteLead()` com undo por toast (guardar snapshot, re-insert)
- [x] **T5** — Modal de confirmação padrão (`confirmarAcao(msg, onOk)`) para venda/CS/agente/parcela
- [x] **T6** — Varrer os 20 `alert()` → `showToast(..., 'error')` + toasts de sucesso nos CRUDs silenciosos
- [x] **T7** — Verificação mobile (viewport 390px) das 4 transições + undo

---

## Dev Notes

**Reutilizar (NÃO recriar):**
- `showToast(msg, type)` — l.3181, já com `.success`/`.error`
- `closeTopModal()` / `MODAL_CLOSERS` / Esc+overlay — Lote 0
- `.move-chip` (CSS l.321) — desenhado e nunca usado; é a base dos chips de perda
- Estrutura de modal: copiar de `modal-pago` (o mais simples, l.1104+)

**Armadilha conhecida (do Lote 0):** `const` no topo do script **não** vai para `window`, mas handlers inline (`onclick=`) resolvem no escopo léxico global — funciona. Não "consertar" isso convertendo para `var`.

**Cuidado com o fluxo assíncrono:** hoje `changeStatus()` é síncrono-bloqueante graças ao `prompt()`. Com modal, vira orientado a evento — garantir que `updateLeadField()` só rode no submit, e que o card não "pisque" de volta na coluna antiga enquanto o modal está aberto.

**Constraints (herdadas do REFACTOR-PLAN):** single-file, vanilla JS, sem framework, sem build step. Não mexer em paleta/layout.

---

## CodeRabbit Integration

- **Story type:** Feature (UX/frontend)
- **Focus:** XSS em novos `innerHTML` (usar `esc()` em todo dado do banco), regressão de fluxo, escaping de handlers inline
- **Gate:** CRITICAL → auto-fix (máx 2 iterações) · HIGH → auto-fix · MEDIUM → débito

---

## Verificação (obrigatória antes de Done)

1. Mover card para **cada** uma das 4 colunas especiais — desktop **e** mobile (390px)
2. Perda: só salva com chip; "Outro" grava o texto digitado; Relatório por Expert agrupa sem fragmentar
3. Excluir lead → toast "Desfazer" → lead volta com os mesmos dados
4. Provocar 1 erro de banco → aparece toast vermelho (não `alert`)
5. Kanban CS e pipeline intactos (drag + long-press)

---

## File List

- `docs/crm/index.html` (modificado) — modais `modal-transition` e `modal-confirm`; CSS `.move-chip.sel` + `.toast-action`; `changeStatus`/`aplicarStatus`/`abrirTransition`/`submitTransition`/`cancelTransition`/`selecionarMotivo`; `confirmarAcao`/`fecharConfirm`/`confirmarOk`; `deleteLead` + `desfazerExclusaoLead`; `showToast` com ação; `moverParaCS`, `deleteAgente`, `desmarcarPago`, `excluirVenda` migrados; 20 `alert()` → toast

## Dev Agent Record

**Agent Model Used:** Opus 4.8 (@dev / Dex)

**Completion Notes:**
- **0 `prompt()`, 0 `confirm()`, 0 `alert()`** restantes no CRM (as 3 ocorrências no grep são comentários).
- `changeStatus()` deixou de ser bloqueante: agora abre modal e o lead só se move no submit (`aplicarStatus`). Cancelar re-renderiza o pipeline e o card volta — verificado: status permaneceu `call` após cancelar.
- Chips de perda: 6 valores fechados; "Outro" revela input e exige texto. Salvar sem motivo é recusado com toast.
- AC3 (guardas do @po) verificado no browser: venda vinculada bloqueia, CS vinculado bloqueia, não-admin bloqueia, e o ✕ nem aparece para não-admin (`x_visivel_para_sdr: false`).
- `showToast` ganhou `opts.actionLabel/onAction/duration` — usa `textContent` (sem XSS com nome de lead).
- Undo re-insere preservando o `id` original.
- CodeRabbit não executado nesta sessão (CLI em WSL, review leva 7-30min) — débito registrado para o gate do @qa.

**Debug Log:** verificação no browser em `localhost:8778` — console sem erros; JS parseia (vm.Script); screenshot do modal de perda no design system.

---

## Change Log

| Data | Autor | Mudança |
|------|-------|---------|
| 2026-07-12 | @sm (River) | Story criada a partir do UX-IMPROVEMENT-PLAN §4 Lote 1 |
| 2026-07-12 | @po (Pax) | Validação 8/10 GO. AC3 reescrito (3 guardas novas: permissão, vínculo, delete verificado). T4 ajustada. Achado extra p/ backlog: o ✕ hoje falha em silêncio para não-admin — corrigido dentro do AC3. |

---

## QA Results

**Gate:** `docs/qa/gates/crm-ux-001-lote1.yml` · **Verdict: PASS** (após 1 iteração do QA Loop) · @qa (Quinn), 2026-07-12

**ISSUE-1 (HIGH) — encontrado e corrigido:** `aplicarStatus()` exibia "Lead movido para X" mesmo quando o UPDATE falhava, porque `updateLeadField()` tratava o erro internamente e não retornava status. Evidência (browser, erro simulado): dois toasts — "Erro ao atualizar: permission denied" seguido de "Lead movido para Fechado". Agravante: em `fechado`, abria o modal de negociação para uma venda inexistente. **Fix:** `updateLeadField()` retorna boolean; `aplicarStatus()` aborta antes do toast de sucesso e de `onLeadFechado()` quando falha. **Re-verificado:** com erro → só o toast vermelho, modal de venda não abre; com sucesso → toast verde normal.

**Débitos registrados (não bloqueiam):**
- ISSUE-2 (low): `moveTo()` virou código morto — remover no Lote 3.
- ISSUE-3 (low): `updateCSField()` tem o mesmo padrão de sucesso presumido (pré-existente) — aplicar o mesmo contrato de retorno no Lote 2.

**Segurança:** innerHTML dos modais novos só interpola constantes (via `esc()`) e `ticket` numérico; `showToast` usa `textContent`. Sem nova superfície XSS.
