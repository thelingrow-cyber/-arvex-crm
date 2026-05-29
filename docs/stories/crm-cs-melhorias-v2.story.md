# Story CRM-CS-002 — Melhorias operacionais do módulo CS (v2)

**Tipo:** Brownfield enhancement (CRM ARVEX — sem epic formal)
**Status:** Done
**Owner:** @dev (frontend) + @data-engineer (SQL mínimo)
**Criado:** 2026-05-29 por @sm (River)
**Validado:** 2026-05-29 por @po (Pax) — score 9/10 GO
**Solicitante:** Vitor (founder ARVEX) — dores reportadas pela operação CS (Sabrina/Cindy)
**Repositório:** `thelingrow-cyber/-arvex-crm` · Deploy: `arvex-crm.vercel.app`
**Complexidade:** M (médio) — SQL ~15min (2 colunas) + Frontend ~2-3h + QA visual ~30min
**Prioridade:** Alta (acompanhamento operacional do CS quebrado/incompleto)

---

## Business Value

A CS (Sabrina) usa o Kanban CS pra conduzir cada cliente da Cindy. Hoje o acompanhamento tem buracos:
- As sub-etapas de Onboarding **aparecem mas não dão pra marcar** → vira informação morta, não checklist real.
- Não há registro de **qual produto** o cliente comprou (Estrategista Óptico / Express / Curadoria) → CS não sabe o que entregar.
- Não há onde listar **entregáveis bônus** prometidos na venda → bônus se perdem.
- A jornada não tem a etapa de **tráfego pago** (que acontece depois do Gate Cindy) → fase invisível no board.
- O registro de resposta dos checks usa um `prompt()` nativo tosco → CS evita anotar o que o cliente respondeu.

**Ganho:** CS com acompanhamento real (não só leitura), entrega correta por produto, bônus rastreados, jornada de tráfego visível e histórico de respostas legível.

---

## Acceptance Criteria

### AC1 — Sub-etapas de Onboarding (e todas as fases) clicáveis (BUG)
- [ ] Clicar numa sub-etapa de Onboarding marca/desmarca o check (✅/○) e persiste em `clientes_cs.activities`
- [ ] Vale pra todas as fases que usam `CS_SUBS` (triagem, gate_cindy, ativo, risco_churn), não só onboarding
- [ ] Causa raiz corrigida: escaping do `onclick` em `renderCSCard` (texto com aspas/parênteses quebrava o atributo HTML)

### AC2 — Seletor de produto no card
- [ ] Campo `produto` em `clientes_cs` com 3 valores: Formação Estrategista Óptico / Formação Express / Curadoria
- [ ] Seletor de produto disponível no detalhe do cliente (`openCSDetail`)
- [ ] Produto escolhido aparece como badge no card do Kanban CS
- [ ] Cliente sem produto definido não quebra render (estado neutro)

### AC3 — Entregáveis bônus
- [ ] Campo `entregaveis_bonus` (jsonb lista) em `clientes_cs`
- [ ] No detalhe do cliente: bloco pra adicionar e remover itens de bônus (texto livre)
- [ ] Card mostra indicador de bônus (ex: 🎁 N) quando houver ao menos um
- [ ] Persiste corretamente; lista vazia é o default

### AC4 — Nova fase Tráfego no Kanban (depois do Gate Cindy)
- [ ] Nova coluna **Tráfego** posicionada **entre** Gate Cindy e Ativo em `CS_COLS`
- [ ] Drag-and-drop entra e sai da coluna Tráfego normalmente
- [ ] Coluna tem cor própria (CSS `.col-cs-trafego`), distinta das demais
- [ ] Fase tem suas próprias sub-etapas em `CS_SUBS` (checklist de tráfego pago) — clicáveis (depende de AC1)
- [ ] Banco aceita o novo valor sem migration de constraint (`cs_stage` é `text` sem CHECK — confirmado no schema)

### AC5 — Melhorar registro de resposta dos checks (substituir prompt)
- [ ] Botão "✅ Respondeu" abre **input inline** pra digitar o que o cliente respondeu (em vez do `prompt()` nativo)
- [ ] "❌ Sem resposta" continua direto, sem pedir texto
- [ ] Texto digitado é salvo em `cs_checks.resposta_obs` (coluna já existe; RPC `registrar_tentativa` já grava)
- [ ] O que foi respondido fica **visível** no card (lista de checks da Campanha) quando houver `resposta_obs`

### Não-regressão
- [ ] Banner "Hoje", churn flag, badge "Pronto para avançar", drag-drop e roles (admin/cs/sdr) continuam funcionando
- [ ] Triggers e RPCs de CS existentes não são alterados
- [ ] Realtime do CRM continua atualizando o Kanban CS

---

## Escopo

**IN:**
- Frontend `docs/crm/index.html`: `CS_COLS`, `CS_SUBS`, `renderCSCard`, `openCSDetail`, `registrarCheck`, novas funções (bônus + resposta inline), CSS `.col-cs-trafego`
- SQL: novo arquivo `docs/crm/setup-cs-v5.sql` — apenas 2 `add column if not exists` (`produto`, `entregaveis_bonus`)

**OUT:**
- Constraint CHECK em `cs_stage` (não existe e não será criada — manteria flexibilidade)
- Métricas novas no dashboard por produto (story futura)
- Refactor do single-file pra framework
- Migração de dados históricos (campos nascem nulos/vazios — aditivo puro)

---

## Tasks

### @data-engineer — SQL v5 (mínimo)
- [x] Criar `docs/crm/setup-cs-v5.sql`: `alter table clientes_cs add column if not exists produto text;` e `add column if not exists entregaveis_bonus jsonb default '[]';`
- [x] Cabeçalho documentando: aditivo, idempotente, sem destrutivos, sem impacto em dados/RLS existentes
- [x] Registrar que `cs_stage` não precisa de mudança (text sem CHECK) e `resposta_obs` já existe (v2)

### @dev — Frontend
- [x] **AC1:** corrigir escaping em `renderCSCard` — passar índice da sub-etapa em vez de string crua no `onclick`; ajustar `toggleSubCS` pra resolver via índice
- [x] **AC2:** const `CS_PRODUTOS`; select no `openCSDetail`; badge no card
- [x] **AC3:** campo `entregaveis_bonus`; bloco add/remove no detalhe; indicador 🎁 no card; funções `addBonusCS`/`removeBonusCS`
- [x] **AC4:** entrada `trafego` em `CS_COLS` entre `gate_cindy` e `ativo`; `CS_SUBS.trafego`; CSS `.col-cs-trafego`
- [x] **AC5:** trocar `prompt()` por input inline (`abrirRespostaCheck`/`confirmarResposta`); `registrarCheck` aceita `obs`; exibir `resposta_obs` no card
- [x] Atualizar File List e checkboxes

### @qa — Review
- [x] Validar AC1-AC5 (code review; UI testável com `?demo=1` ou em prod após push)
- [x] Não-regressão + console limpo
- [x] Decisão: PASS / CONCERNS / FAIL → **PASS com CONCERNS** (ver QA Results)

### @devops — Push (após OK do Vitor)
- [ ] Aplicar `setup-cs-v5.sql` no Supabase ANTES do deploy do frontend
- [ ] Commit + push `main` → Vercel auto-deploy

---

## File List

**Modificar:** `docs/crm/index.html`
**Criar:** `docs/crm/setup-cs-v5.sql`
**Não tocar:** `setup-cs.sql`, `setup-cs-v2.sql`, `setup-cs-v3.sql`, `setup-cs-v4.sql` (histórico imutável)

---

## Dev Notes

- `cs_stage` é `text` sem CHECK (`setup-cs.sql:22`) → fase Tráfego é só frontend.
- `cs_checks.resposta_obs` já existe (`setup-cs-v2.sql:17`) e a RPC `registrar_tentativa` já grava `p_obs` lá (`setup-cs-v2.sql:152`) → AC5 é frontend.
- Bug do AC1: `renderCSCard` injeta `${JSON.stringify(s)}` dentro de `onclick="..."` (aspas duplas) — strings como `'Boas-vindas enviada (WhatsApp)'` quebram o atributo. Fix: passar índice.
- Sub-etapas de Tráfego são conteúdo de negócio (array `CS_SUBS.trafego`) — fácil ajustar depois; valores iniciais são uma proposta.

---

## Riscos

| Risco | Prob. | Mitigação |
|-------|-------|-----------|
| Frontend deployar antes do SQL (produto/bônus quebram) | Média | Aplicar `setup-cs-v5.sql` ANTES do push (@devops) |
| Sub-etapas de tráfego não baterem com o processo real | Baixa | Array editável; Vitor ajusta os textos |
| Input inline de resposta conflitar com re-render | Média | Usar id único por check; salvar dispara reload de estado |

---

## Definition of Done

- [ ] AC1-AC5 atendidos no código
- [ ] @qa gate PASS ou CONCERNS aceitos
- [ ] `setup-cs-v5.sql` aplicado no Supabase
- [ ] Push em `main` com deploy verde
- [ ] Vitor valida o fluxo no CRM

---

## QA Results

**Reviewer:** @qa (Quinn) · **Data:** 2026-05-29 · **Método:** code review (single-file sem build; UI validável em prod/`?demo=1`)
**Verdict:** ✅ **PASS com CONCERNS**

| AC | Status | Nota |
|----|--------|------|
| AC1 — sub-etapas clicáveis | ✅ PASS | `onclick` agora passa índice (`${i}`); `toggleSubCS` resolve via `CS_SUBS[fase][idx]`. Causa raiz (aspas duplas do `JSON.stringify`) eliminada. Vale pra todas as fases. |
| AC2 — produto | ✅ PASS | `CS_PRODUTOS` + select no detalhe + badge ciano no card. Estado neutro quando NULL. |
| AC3 — bônus | ✅ PASS | `entregaveis_bonus` jsonb; add/remove no detalhe; indicador 🎁 N no card; `Array.isArray` defensivo. |
| AC4 — fase Tráfego | ✅ PASS | Coluna entre Gate Cindy e Ativo; CSS `.col-cs-trafego`; 6 sub-etapas; drag-drop e badge "Pronto" herdados genericamente. |
| AC5 — resposta inline | ✅ PASS | Prompt substituído por input inline (Enter ou Salvar); `resposta_obs` exibido no card. |
| Não-regressão | ✅ PASS | `registrarCheck(obs=null)` retrocompatível; banner Hoje intacto; roles/realtime/triggers não tocados. |

**Issues (não bloqueadoras):**
| ID | Sev | Descrição | Recomendação |
|----|-----|-----------|--------------|
| LOW-01 | LOW | Banner "Hoje" mantém registro rápido ✅/❌ sem input de texto (decisão de design: agenda do dia é rápida; texto detalhado fica no card da Campanha) | Se a CS quiser anotar pelo banner também, estender com o mesmo `abrirRespostaCheck` |
| LOW-02 | LOW | Sub-etapas de Tráfego (`CS_SUBS.trafego`) são proposta inicial baseada em tráfego pago genérico | Vitor/Sabrina validam e ajustam os textos do array conforme o processo real |

**Pré-requisito de deploy:** aplicar `setup-cs-v5.sql` no Supabase **antes** do push do frontend (senão produto/bônus quebram).

---

## Change Log

| Data | Agente | Ação |
|------|--------|------|
| 2026-05-29 | @sm (River) | Story criada (Draft) — 5 itens triados pelo Vitor: onboarding clicável, produto, bônus, fase tráfego, resposta inline. Definições travadas via Q&A: tudo numa story; tráfego = nova coluna; resposta = texto livre. |
| 2026-05-29 | @po (Pax) | Validação 10-point: GO 9/10. Descobertas que enxugaram escopo (cs_stage sem CHECK; resposta_obs já existe) reduzem SQL a 2 colunas. Status Draft → **Ready**. Liberado pra @data-engineer. |
| 2026-05-29 | @data-engineer (Dara) | `setup-cs-v5.sql` entregue: 2 colunas aditivas (`produto` text, `entregaveis_bonus` jsonb `[]`) + `comment on column`. Idempotente, sem destrutivos. Documentado que `cs_stage` e `resposta_obs` já cobrem os outros itens. |
| 2026-05-29 | @dev (Dex) | Frontend em `docs/crm/index.html` (9 edits): CSS `.col-cs-trafego`; fase `trafego` em CS_COLS + CS_SUBS; `CS_PRODUTOS`; fix escaping do `onclick` (índice) + `toggleSubCS` por índice; badge produto + indicador 🎁 no card; select produto + bloco bônus (`addBonusCS`/`removeBonusCS`) no detalhe; `registrarCheck` aceita `obs`; input inline (`abrirRespostaCheck`/`confirmarResposta`); exibe `resposta_obs` no card. Status → InReview. |
| 2026-05-29 | @qa (Quinn) | QA Gate: **PASS com CONCERNS**. AC1-AC5 atendidos no código. 2 LOW (banner Hoje sem texto inline — by design; sub-etapas de tráfego a validar). Pré-requisito: aplicar SQL v5 antes do deploy. Aguardando OK do Vitor pra @devops push. |
| 2026-05-29 | @devops (Gage) | `setup-cs-v5.sql` aplicado pelo Vitor no Supabase. Commit atômico `3e62389` em `master`. **Descoberto que `master` (Preview) ≠ branch de produção:** Vercel publica de `main`, que serve o CRM como `index.html` na RAIZ (`master` mantém em `docs/crm/index.html` + monorepo). Sync correto = copiar `docs/crm/index.html` → `index.html` raiz de `main` (NÃO é merge git). Sync feito: commit `cd4aa7d` em `main` (só index.html, +87/-8). Produção verificada no ar (`col-cs-trafego`, `CS_PRODUTOS`, `abrirRespostaCheck` presentes). Status → **Done**. |
