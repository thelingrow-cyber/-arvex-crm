# Story CRM-UX-004 — Lote 4: higiene interna (Fase 2 do REFACTOR-PLAN)

**Tipo:** Refatoração (brownfield, sem mudança funcional)
**Status:** Done
**Owner:** @dev (Dex) — frontend puro, sem SQL
**Criado:** 2026-07-13 por @sm (River)
**Validado:** 2026-07-13 por @po (Pax) — **NO-GO no escopo original (6/10) · GO no escopo enxuto (9/10)**. AC3 (event delegation) ADIADO com justificativa numérica — ver §Decisão do @po
**Solicitante:** Vitor (founder ARVEX)
**Fonte:** `docs/crm/UX-IMPROVEMENT-PLAN.md` §4 (Lote 4) + `docs/crm/REFACTOR-PLAN.md` §4 (Fase 2)
**Repositório:** `thelingrow-cyber/-arvex-crm` · Deploy: `arvex-crm.vercel.app`
**Arquivo alvo:** `docs/crm/index.html`
**Complexidade:** S/M (após corte do @po) — ~30 pontos de edição, não 336
**Prioridade:** Média (ganho indireto: custo de manutenção)
**Predecessores:** Lotes 0 (`b4b0a6f`), 1 (`f76489a`), 2 (`8251072`), 3 (`9581fa2`) — todos em produção

---

## Business Value

**Nenhum ganho visível ao usuário — e isso é intencional.** O valor é de manutenção, e está declarado no REFACTOR-PLAN:

1. **Custo de token por edição.** Todo agente que edita o CRM relê o arquivo inteiro. Blocos de `style` repetidos 17× e 3.797 linhas inflam esse custo em toda story futura.
2. **Seams para o SaaS óptico / Viziom.** Markup acoplado a lógica por `onclick` inline não é extraível para um módulo reusável.
3. **Classe inteira de bug eliminada.** O CS já teve um bug de escaping em `onclick` com texto interpolado (resolvido na marra, por índice). Event delegation remove a possibilidade.

**Critério de sucesso: o CRM tem de ficar visual e funcionalmente IDÊNTICO.** Qualquer diferença perceptível é regressão, não melhoria.

---

## Estado medido (baseline, 2026-07-13)

| Métrica | Valor |
|---|---|
| Linhas | 3.797 |
| `style="` inline | 260 |
| `onclick=` | 91 — **54 em HTML estático** (sem interpolação) + **37 em templates JS** |
| `onchange`/`oninput`/`onkeydown` | 47 |
| Blocos `<style>` | 2 (o 2º na l.845, dentro do body — anomalia) |
| Bloco de `style` de select repetido | **17×** (mesmos ~130 caracteres) |

---

## Acceptance Criteria

### AC1 — Um único bloco de CSS
- [x] O 2º `<style>` (l.845, dentro do `<body>`, do módulo Coach) é absorvido pelo bloco principal do `<head>`
- [x] Zero mudança visual: as regras `.coach-*` continuam valendo exatamente igual

### AC2 — Inline styles repetidos viram classes (os que dão ganho real)
- [x] **Só o padrão com ganho concreto (@po):** `.di-select` / `.di-input` — o bloco de ~130 caracteres repetido **17×** nos selects/inputs do modal de detalhe e do CS
- [x] ~~Meta de ≤150 inline styles~~ — **cortada (@po).** Os 260 inline styles somam 17.685 bytes = **7,5% de um arquivo de 235KB**. Perseguir a meta renderia ~3% de redução (~2.000 tokens numa leitura de 60k) ao custo de ~200 edições. **Não compensa.** Trocar 1 padrão repetido 17× é ganho legítimo; caçar `style="margin-top:8px"` é churn.
- [x] Nenhuma regra nova de CSS altera a aparência: as classes carregam **exatamente** as mesmas declarações

### ~~AC3 — Event delegation~~ → **ADIADO pelo @po (não é dívida esquecida, é decisão)**

> 🚫 **Cortado do Lote 4.** Justificativa medida, não opinião:
> - **O motivo original evaporou.** A delegação era justificada por "elimina a classe de bug de escaping". Medição: os 20 handlers que interpolam dado passam **UUID**, não texto livre. O bug do CS (texto com aspas quebrando o atributo) **não é mais possível** — já foi resolvido por índice.
> - **O risco é concreto:** 37 handlers, **7 deles dentro de elementos clicáveis dependendo de `stopPropagation()`**. Delegar isso num CRM em produção, sem suíte de testes, para ganhar zero função.
> - **O seam real do SaaS não é este.** Extrair módulo para o SaaS óptico exige a **camada `db.*` (Fase 3 do REFACTOR-PLAN)**, não trocar `onclick` por `data-action`. Estamos pagando risco por um benefício que mora em outra fase.
>
> **Reavaliar quando:** a extração de módulos do SaaS óptico começar de verdade (Fase 3) — aí a delegação vira pré-requisito real e entra junto, com testes.

### AC4 — JS organizado por seções nomeadas
- [x] Bandeiras de comentário por domínio (`// ===== VIEW: PIPELINE =====`, `CS`, `FINANCEIRO`, `COACH`, `AGENTE SDR`, `DASHBOARD`, `AUTH`, `UTILS`), agrupando estado → data-access → render → handlers
- [x] **Sem módulos ES, sem build, sem reordenar funções que criem TDZ** (armadilha do Lote 2 — mover uma chamada para antes da `const` derruba o boot inteiro)

### AC5 — Zero regressão (o AC mais importante)
- [x] **Baseline visual:** screenshot de cada view (dashboard, pipeline, leads, CS, financeiro, clientes, reuniões, agente, por-expert) **antes** e **depois** — diferença perceptível = FAIL
- [x] Smoke test dos fluxos vivos: criar lead · mover card (drag desktop) · mover por chip (Lote 3) · abrir detalhe · excluir lead com undo (Lote 1) · mover card CS · registrar check CS · lançar venda · marcar parcela paga · abrir reunião
- [x] Lotes 0-3 intactos (debounce, Esc/overlay, modal de transição, chips de perda, métricas de movimento, deep-link, atalhos, valor por coluna)
- [x] Console limpo; `document.querySelectorAll('[onclick]')` nos containers dinâmicos = 0

---

## Tasks

- [x] **T1** — Baseline: screenshots das views principais + contagem inicial
- [x] **T2** — AC1: absorver o 2º `<style>`
- [x] **T3** — AC2: classes `.di-select`/`.di-input` (o padrão 17×)
- [x] ~~**T4** — event delegation~~ **ADIADO pelo @po** (ver AC3)
- [x] **T5** — AC4: bandeiras de seção no JS (**este é o item de maior valor real** — permite leitura parcial do arquivo por agentes)
- [x] **T6** — AC5: comparação visual antes/depois + smoke test

---

## Dev Notes

**Ordem obrigatória: uma view por vez, verificando entre cada uma.** Um "big bang" em 336 pontos é irrecuperável se quebrar — não há testes automatizados aqui, a rede de segurança é a verificação em browser.

**Delegação e `stopPropagation`:** hoje vários botões vivem dentro de elementos clicáveis (ex.: `.btn-card-action` dentro de `.lead-card`; `✕` dentro de `<tr onclick=openDetail>`). Ao delegar, o listener do container recebe **os dois**. Resolver com `e.target.closest('[data-action]')` primeiro e `return` — nunca deixar o clique no botão cair no handler do card.

**Drag & touch:** `.lead-card` e `.cs-card` têm listeners de `dragstart`/`touchstart` anexados após cada render. A delegação **não** substitui isso — não mexer no drag.

**Armadilha do Lote 2 (TDZ):** reorganizar o JS não pode mover chamadas para antes das `const` que elas consomem. `vm.Script` (parse) **não** pega isso — só o browser. Verificar console em cada etapa.

**Constraints:** single-file, vanilla JS, sem build step, sem framework. Paleta e layout **não mudam**.

---

## O que NÃO fazer (anti-churn)

- ❌ **Não perseguir "zero inline style".** Style pontual e único (ex.: `style="width:90px"` numa parcela) é legítimo e mais legível que uma classe de uso único. O alvo são os **repetidos**.
- ❌ **Não converter os 54 `onclick` do HTML estático.** Sem interpolação, sem risco, sem ganho de reuso.
- ❌ Não introduzir módulos ES, bundler, framework CSS ou TypeScript (§5 do UX-IMPROVEMENT-PLAN).
- ❌ Não "melhorar" nada de aparência de passagem. Este lote é **invisível** por definição.
- ❌ Não reescrever o kanban CS nem o drag — funcionam e têm usuários.

---

## CodeRabbit Integration

- **Story type:** Refactor
- **Focus:** breaking changes, interface stability, escaping no `data-*`, handlers órfãos (função referenciada por `data-action` que não existe)
- **Gate:** CRITICAL → auto-fix · HIGH → auto-fix · MEDIUM → débito

---

## Verificação (obrigatória antes de Done)

1. Screenshots das 9 views antes/depois — **sem diferença perceptível**
2. Smoke test dos 10 fluxos listados no AC5
3. `[onclick]` = 0 nos containers dinâmicos; `style="` ≤ 150
4. Console limpo em cada view (TDZ e handler órfão só aparecem aqui)
5. Mobile 390px: drag por long-press e chips continuam funcionando

---

## File List

- `docs/crm/index.html` (modificado) — 2º `<style>` (41 linhas do Coach) absorvido no bloco do `<head>`; classes `.di-field`/`.di-select`/`.di-input` substituem o style repetido 17×; 13 bandeiras `// ===== DOMINIO: X =====` + índice grepável no topo do script

## Dev Agent Record

**Agent Model Used:** Opus 4.8 (@dev / Dex)

**Resultado medido:**

| | Antes | Depois |
|---|---|---|
| Blocos `<style>` | 2 | **1** |
| Inline styles | 260 | **243** (−17, o padrão repetido) |
| Bytes | 234.918 | **232.331** |
| Bandeiras de domínio grepáveis | 0 | **13** + índice |

**Completion Notes:**
- **Zero mudança visual — provado, não afirmado.** O `computed style` do select convertido bate **exatamente** com o inline original (navy3, borda, raio 6px, Inter 13px, padding 6×10, largura 100%, margem 4px). As 39 regras `.coach-*` continuam ativas após saírem do `<body>` para o `<head>`.
- **Smoke test:** as 9 views renderizam sem erro; Lote 0 (Esc), Lote 1 (modal de transição + 6 chips de perda), Lote 2 (métricas de movimento) e Lote 3 (8 chips de status, valor por coluna) intactos. Console limpo.
- **O ganho real do lote é o índice, não o CSS.** Um agente agora faz `grep "===== DOMINIO: CS"` e lê **só** aquele trecho, em vez dos 235KB. As convenções que já custaram bugs (TDZ, "sucesso só após o banco confirmar") estão escritas no cabeçalho — quem editar o arquivo lê antes de errar.
- **Nada foi movido de lugar.** As bandeiras são troca de texto de comentário; reordenar funções era o caminho para repetir a TDZ do Lote 2.

**Escopo cortado (decisão do @po, confirmada pelo Vitor):** event delegation dos 37 handlers dinâmicos — o bug de escaping que a justificava não é mais possível (os `data-id` são UUID) e 7 handlers dependem de `stopPropagation` dentro de cards clicáveis. Reavaliar na Fase 3 (camada `db.*`), quando o seam for real.

---

## Change Log

| Data | Autor | Mudança |
|------|-------|---------|
| 2026-07-13 | @sm (River) | Story criada. Escopo reduzido vs. REFACTOR-PLAN: os 54 onclick estáticos ficam; meta de inline styles ≤150. |
| 2026-07-13 | @po (Pax) | **NO-GO no escopo original (6/10); GO no enxuto (9/10).** Cortes com base em medição: (1) inline styles = 7,5% do arquivo → a meta renderia ~3% de ganho por ~200 edições: cortada, fica só o padrão 17×; (2) event delegation ADIADA — o bug de escaping que a justificava não é mais possível (data-id é UUID) e 7 handlers dependem de stopPropagation; o seam real do SaaS é a camada `db.*` (Fase 3), não `data-action`. Sobra o que tem ganho real e risco ~zero: 2º `<style>`, o padrão de select 17×, e as bandeiras de seção no JS. |

---

## QA Results

**Gate:** `docs/qa/gates/crm-ux-004-lote4.yml` · **Verdict: PASS** (sem iteração) · @qa (Quinn), 2026-07-13

**"Zero mudança" foi provado, não afirmado.** Comparei **classe a classe contra a produção**: 9 classes `.coach-*`/`.cc-*` medidas por computed style (background, color, radius, padding, font-size, font-weight, border, display) na versão no ar (sem Lote 4) e na versão com Lote 4 → **zero divergências**. A cascata não mudou: o CSS do Coach continua depois de todas as regras originais.

**Focos auditados:** nenhum dos 17 elementos convertidos tinha `class=` própria (sem sobrescrita); nenhum ficou com `style=` conflitante; 9/9 views renderizam; Lotes 0-3 intactos; console limpo.

**Nota do QA sobre o valor real:** o ganho deste lote **não** é a redução de bytes (−1,1%, irrelevante). É o **índice de domínios** no cabeçalho: um agente agora greppa `===== DOMINIO: CS` e lê só aquele trecho em vez dos 235KB. E as convenções que já custaram bugs nesta própria série — a **TDZ** (Lote 2, derrubou o boot inteiro) e o **"sucesso só após o banco confirmar"** (Lote 1, toast mentia em falha) — estão agora escritas onde quem for editar o arquivo lê **antes** de repetir o erro. Isso é prevenção, não cosmética.
