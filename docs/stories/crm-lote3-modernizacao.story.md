# Story CRM-UX-003 — Lote 3: modernização Linear-like (F5, F7, F12, F14, F15)

**Tipo:** Brownfield enhancement (CRM ARVEX — sem epic formal)
**Status:** Done
**Owner:** @dev (Dex) — frontend puro, sem SQL
**Criado:** 2026-07-12 por @sm (River)
**Validado:** 2026-07-12 por @po (Pax) — score 8/10 **GO** (2 correções: empilhamento de modais no Esc, deep-link vs role)
**Solicitante:** Vitor (founder ARVEX)
**Fonte:** `docs/crm/UX-IMPROVEMENT-PLAN.md` §3 (F5, F7, F12, F14, F15) e §4 (Lote 3)
**Repositório:** `thelingrow-cyber/-arvex-crm` · Deploy: `arvex-crm.vercel.app`
**Arquivo alvo:** `docs/crm/index.html`
**Complexidade:** M — frontend ~2-3h + QA ~40min
**Prioridade:** Média-Alta (F5 é bloqueio operacional real no celular)
**Predecessores:** Lote 0 (`b4b0a6f`), Lote 1 (`f76489a`), Lote 2 (`8251072`) — todos em produção

---

## Business Value

1. **No celular só dá para mover lead arrastando (F5).** O drag depende de long-press de 400ms + auto-scroll — frágil no toque, e é assim que SDR e CS operam. O modal de detalhe mostra tudo mas **não move o lead**. A classe `.move-chips` foi desenhada no CSS (l.321) e **nunca usada**.
2. **Nada é linkável (F12).** Refresh sempre cai no dashboard; não dá para mandar "olha esse lead" no WhatsApp do time.
3. **46 emojis misturados com o sistema Lucide (F14)** — a migração de ícones ficou pela metade e a UI parece remendada.
4. **Pipeline não mostra dinheiro (F15).** A coluna diz "3 leads", não "R$ 34k" — visão de valor é padrão em Pipedrive/Attio.
5. **Zero atalhos (F7-resto)** para quem vive no CRM o dia inteiro.

**Ganho:** operar o CRM pelo celular sem arrastar card; compartilhar lead por link; UI visualmente coesa; pipeline com valor à vista.

---

## Acceptance Criteria

### AC1 — Mover lead pelo modal de detalhe, com chips (F5)
- [x] Linha de chips de status no `openDetail()` (l.2298), reutilizando `.move-chips`/`.move-chip`/`.move-chip.sel` (já existem — não criar CSS novo)
- [x] Um chip por coluna do pipeline (`COLS`), com o status atual destacado (`.sel`) e **não clicável**
- [x] Clicar em outro chip dispara o **mesmo fluxo do Lote 1**: `changeStatus()` → abre `modal-transition` quando a coluna exige dado (perdido/call/followup/fechado). **NÃO** duplicar a lógica de transição
- [x] **Chip NÃO é marcado otimisticamente (@po):** a fonte de verdade é `lead.status`. Após `aplicarStatus()` confirmar no banco, o modal de detalhe é re-renderizado (`openDetail(id)`) e o chip novo aparece selecionado. Cancelar não muda nada — não há estado visual para "voltar"
- [x] **BUG PRÉ-EXISTENTE que este AC expõe (@po):** com `modal-detail` e `modal-transition` abertos ao mesmo tempo, `closeTopModal()` (Lote 0) escolhe o último `.modal-overlay.open` **na ordem do DOM** — e o `modal-transition` vem ANTES do `modal-detail` no HTML. Esc fecharia o **detalhe** e deixaria a transição órfã. **Corrigir:** o "topo" deve ser o **último aberto**, não o último no DOM (ex.: `dataset.openedAt = Date.now()` ao abrir; `closeTopModal` ordena por isso). Vale para o clique no overlay também
- [x] Mobile (390px): mover um lead = **2 toques** (abrir lead → tocar no chip), sem drag
- [x] `moveTo()` (l.2341) — código morto desde o Lote 1 (QA ISSUE-2) — é **removido** ou passa a ser a função usada pelos chips

### AC2 — Deep-link e rota por hash (F12)
- [x] `goTo(view)` atualiza `location.hash` (`#pipeline`, `#leads`, `#cs`…) sem recarregar a página
- [x] Abrir a URL com hash cai direto na view (refresh não volta mais pro dashboard)
- [x] `#lead/{id}` abre a view de leads **e** o modal de detalhe daquele lead
- [x] Fechar o modal de detalhe limpa o `#lead/{id}` do hash (volta para `#leads`)
- [x] Hash inválido ou lead inexistente → cai no dashboard sem erro no console
- [x] **Deep-link respeita o role (@po):** `applyRole()` esconde views por role (e força a Sabrina/CS direto para `#cs`). Um link `#pipeline` NÃO pode jogar o usuário numa view que a UI dele esconde — se a view alvo estiver oculta para o role, cair na view default dele (CS → `#cs`; demais → dashboard). Não é segurança (a RLS protege os dados), é coerência de navegação
- [x] `hashchange` (botão voltar do navegador) navega corretamente — sem loop de render

### AC3 — Ícones 100% Lucide (F14)
- [x] Os **46 emojis** da UI são substituídos por ícones Lucide (`icon(nome)`), incluindo os que faltam no `LUCIDE`: `trash`, `pencil`, `send`, `undo`, `phone`, `link`, `user`, `handshake`/`users2`, `video`
- [x] Zero emoji renderizado na interface. **Exceção permitida:** emoji dentro de dado do usuário (ex.: nome de lead que contém emoji) — não filtrar dado
- [x] Ícones herdam `currentColor` (nada de cor fixa que quebre no hover) e mantêm os tamanhos atuais
- [x] Botões que hoje são só emoji (✏️, 🗑️, ➤) ganham `title=` e `aria-label` (acessibilidade mínima)

### AC4 — Valor por coluna no pipeline (F15)
- [x] `col-header` do pipeline mostra, além da contagem, a **soma de ticket** dos leads da coluna, formatada compacta (`R$ 34k`, `R$ 1,2k`)
- [x] **Só para admin** — confirmado no código: `card-ticket` (l.2078) já usa `currentRole === 'admin'`. A soma por coluna usa o mesmo guard; para não-admin o header fica como está hoje (só contagem)
- [x] Coluna sem valor não exibe `R$ 0` — omite
- [x] Kanban CS **não** recebe valor (não é pipeline de venda)

### AC5 — Atalhos de teclado (F7-resto)
- [x] `N` abre "Novo Lead" (só nas views comerciais, onde o botão existe)
- [x] `/` foca a busca da view atual
- [x] Atalhos **não disparam** quando o foco está em `input`, `textarea`, `select` ou com modal aberto
- [x] `Esc` continua fechando modal/sidebar (Lote 0) — sem conflito

### AC6 — Débitos herdados dos gates anteriores
- [x] **ISSUE-3 (Lote 1):** `updateCSField()` (l.2922) presume sucesso — mostra erro e segue como se tivesse salvo. Aplicar o mesmo contrato do `updateLeadField()`: **retornar boolean** e só renderizar/toastar sucesso se o banco confirmou
- [x] **Débito (Lote 2):** título "Evolução Diária — Leads" → "Leads captados por dia" (o gráfico plota criação, não movimento — o nome atual induz a erro)

### AC7 — Sem regressão
- [x] Lote 1 intacto: modal de transição, chips de perda, undo do delete, toasts
- [x] Lote 2 intacto: métricas de movimento, filtros, `profiles.financeiro`, experts centralizados
- [x] Drag desktop e long-press mobile continuam funcionando (chips **somam**, não substituem)
- [x] Kanban CS e Financeiro sem alteração de comportamento

---

## Tasks

- [x] **T1** — Chips de status no `openDetail()` reutilizando `changeStatus()`; resolver `moveTo()`
- [x] **T2** — Hash routing: `goTo()` escreve o hash, boot lê o hash, `hashchange`, `#lead/{id}`
- [x] **T3** — Ampliar `LUCIDE` com os ícones faltantes e varrer os 46 emojis
- [x] **T4** — Valor por coluna no pipeline (admin), formato compacto
- [x] **T5** — Atalhos `N` e `/` com guarda de foco/modal
- [x] **T6** — Débitos: `updateCSField()` com retorno; título do gráfico
- [x] **T7** — Verificação: mobile 390px (2 toques), deep-link colado em aba nova, zero emoji, console limpo

---

## Dev Notes

**Reutilizar (NÃO recriar):**
- `changeStatus()` / `modal-transition` (Lote 1) — os chips são só um **novo gatilho** para o fluxo que já existe
- `.move-chips`, `.move-chip`, `.move-chip.sel` (CSS já pronto)
- `icon(nome, opts)` / `initIcons()` (l.1172+) — o sistema Lucide já existe, faltam só paths
- `COLS` / `BLABEL` para montar os chips

**Armadilha do Lote 2 (não repetir):** `initSelectsEquipe()` foi chamada antes das `const` que usa → TDZ derrubou o boot inteiro e o `vm.Script` (parse) passou limpo. **Qualquer chamada de função no topo do script deve vir depois das declarações que ela consome** — e a verificação tem que ser no browser, não só no parser.

**Hash routing sem framework:** `goTo()` é chamado com `(id, el)` a partir de `onclick` inline. Ao adicionar o hash, cuidar para o `hashchange` **não** re-disparar `goTo()` em loop (guardar flag ou comparar o hash atual antes de navegar).

**Constraints:** single-file, vanilla JS, sem build. Não mexer em paleta/layout (o redesign está aprovado).

---

## CodeRabbit Integration

- **Story type:** Feature (UX/frontend)
- **Focus:** XSS nos novos `innerHTML` (chips e ícones — usar `esc()` em dado do banco), loop de render no `hashchange`, vazamento de ticket para não-admin
- **Gate:** CRITICAL → auto-fix · HIGH → auto-fix · MEDIUM → débito

---

## Verificação (obrigatória antes de Done)

1. **Mobile 390px:** abrir lead → tocar chip "Perdido" → modal de motivo → salvar. Lead move sem nenhum drag
2. Colar `#lead/{id}` em aba nova → abre o modal do lead certo; fechar → hash volta para `#leads`
3. Botão voltar do navegador navega entre views sem loop
4. `grep` visual: zero emoji na UI (exceto dado do usuário)
5. Admin vê `R$` no topo das colunas do pipeline; SDR **não** vê
6. `N` abre novo lead; `/` foca a busca; nenhum dos dois dispara digitando num campo
7. Console limpo; Lotes 1 e 2 intactos

---

## File List

- `docs/crm/index.html` (modificado) — `abrirModal()`/`topModal()` (ordem de abertura); chips de status em `openDetail()` + `moveTo()` revivido; `VIEWS`/`viewPermitida()`/`aplicarHash()`/`hashchange`; 11 ícones Lucide novos (trash, pencil, send, undo, phone, link, user, handshake, video, hourglass, gift2) e 46 emojis substituídos; `valorDaColuna()` + `.col-valor`; atalhos N e `/` com `digitandoEmCampo()`; `updateCSField()` com retorno booleano; título do gráfico corrigido

## Dev Agent Record

**Agent Model Used:** Opus 4.8 (@dev / Dex)

**Completion Notes:**
- **Fix do @po verificado no browser:** com `modal-detail` + `modal-transition` empilhados, `topModal()` devolve o **transition** (mesmo ele vindo antes no DOM) e o Esc fecha o de cima, mantendo o detalhe. Todas as 13 aberturas de modal migraram para `abrirModal()`, que carimba `dataset.openedAt`.
- **Chips (F5):** 8 chips no detalhe; o atual fica `.sel` e `disabled`. Clicar dispara `changeStatus()` — o **mesmo** fluxo do Lote 1 (o modal de motivo/valor abre por cima). Sem marcação otimista: o modal só é reaberto depois que o banco confirma.
- **Deep-link (F12):** abrir lead escreve `#lead/{id}`; fechar volta para a view. `aplicarHash()` roda **depois** dos dados carregarem (senão `#lead/{id}` não acharia o lead) e respeita o role.
- **Ícones (F14):** 46 emojis → 0. Botões só-ícone ganharam `title` + `aria-label`.
- **Valor por coluna (F15):** admin vê `R$ 34,5k`; SDR não vê nada (verificado — não vaza ticket).
- **Atalhos (F7):** `N` abre novo lead, `/` foca a busca; ambos ignorados com modal aberto ou foco em campo.
- **Débitos quitados:** `updateCSField()` agora retorna boolean e **desfaz o cache otimista** em erro (antes a CS via o card certo na tela com o dado não salvo); gráfico renomeado para "Leads captados por dia".

**Debug Log:** `document.hasFocus() === false` na aba automatizada — `focus()` não pega, o que tornou 2 asserts inconclusivos à primeira passada. Contornado espionando `focus()` e testando a guarda pura (`digitandoEmCampo`). Não era bug: um modal deixado aberto pelo teste anterior é que bloqueava o `/` — exatamente como a guarda deve se comportar.

---

## Change Log

| Data | Autor | Mudança |
|------|-------|---------|
| 2026-07-12 | @sm (River) | Story criada a partir do UX-IMPROVEMENT-PLAN §4 Lote 3, incluindo os 2 débitos herdados dos gates dos Lotes 1 e 2 |
| 2026-07-12 | @po (Pax) | Validação 8/10 GO. AC1: chip sem marcação otimista + **bug pré-existente exposto** (closeTopModal usa ordem do DOM, não ordem de abertura → Esc fecharia o modal errado com 2 modais empilhados). AC2: deep-link precisa respeitar role (CS não pode cair no pipeline por link). |

---

## QA Results

**Gate:** `docs/qa/gates/crm-ux-003-lote3.yml` · **Verdict: PASS** (sem iteração) · @qa (Quinn), 2026-07-12

Primeiro lote a passar de primeira. Os 5 focos de risco foram auditados no browser:
- **Sem loop de navegação:** 1 navegação por mudança de URL, 0 re-disparos por clique — a flag `_navegando` corta o ciclo.
- **Chip sem modal (ex.: Qualificado):** move direto e o chip reflete o novo status. *Minha primeira medição deu falso negativo* (esperei 500ms; o `await loadHistory()` real demorou mais) — o log instrumentado provou que `openDetail` é chamado com o cache já atualizado.
- **Deep-link respeita role:** como CS, `#pipeline` cai em `view-cs`.
- **Zero regressão** nos Lotes 0/1/2.
- **Zero emoji** renderizado (`innerText` limpo) e o valor por coluna **não vaza** para SDR.

**DEBT-1 (low):** `aplicarStatus()` aguarda `loadHistory()` (rede) antes de reabrir o detalhe — pelo chip, o usuário espera ~300ms para o chip mudar. Reabrir o modal antes do `loadHistory()` resolve. Não bloqueia.
