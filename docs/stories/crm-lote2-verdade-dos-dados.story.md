# Story CRM-UX-002 — Lote 2: verdade dos dados (F3, F4, F6)

**Tipo:** Brownfield enhancement (CRM ARVEX — sem epic formal)
**Status:** Done
**Owner:** @data-engineer (Dara) — SQL · @dev (Dex) — frontend
**Criado:** 2026-07-12 por @sm (River)
**Validado:** 2026-07-12 por @po (Pax) — score 8/10 **GO** (3 correções aplicadas: backfill honesto, trigger SECURITY DEFINER, seed via auth.users)
**Solicitante:** Vitor (founder ARVEX)
**Fonte:** `docs/crm/UX-IMPROVEMENT-PLAN.md` §3 (F3, F4, F6) e §4 (Lote 2) — auditoria Fable 5
**Repositório:** `thelingrow-cyber/-arvex-crm` · Deploy: `arvex-crm.vercel.app`
**Arquivo alvo:** `docs/crm/index.html` + nova migration SQL
**Complexidade:** M/L — SQL ~40min + frontend ~2h + QA ~40min
**Prioridade:** Alta (F3: você toma decisão comercial com número errado)
**Predecessor:** Lote 1 (CRM-UX-001) Done, em produção (`f76489a`)

---

## Business Value

1. **O dashboard mente (F3).** "Calls: 3" não significa 3 calls no período — significa 3 leads *parados agora* na coluna Call. Um lead que fez call e avançou para Follow Up **some da métrica**. O mesmo vale para Contatos e Qualificados. Não existe histórico de transição, então nenhuma métrica de *movimento* (calls realizadas, tempo por etapa, conversão real) é possível hoje. **Decisão comercial em cima de número errado.**
2. **Permissão do financeiro em lista de e-mail, duplicada (F4).** A lista existe no JS (`FINANCEIRO_USERS`, l.1295) **e** dentro da função `is_financeiro_user()` do banco (`auth.email() in (...)`). Trocar quem vê o financeiro exige editar código em dois lugares e fazer deploy.
3. **Expert morto na UI (F6).** "Dr. Alex" (fora da operação desde 2026-07-06) aparece em 9 lugares, inclusive nos selects de cadastro — SDR ainda pode cadastrar lead para um expert que não existe. Equipe (Victor P/Gabriel/Vitor) hardcoded em 4 selects.

**Ganho:** métricas que refletem o que a operação realmente fez; permissão gerenciável pelo banco (sem deploy); e a UI parando de oferecer opções mortas.

---

## Acceptance Criteria

### AC1 — Histórico de transições de status (F3) — @data-engineer
- [x] Migration `setup-status-history-v1.sql` (aditiva, idempotente): tabela `status_history` com `id`, `lead_id` (FK → leads, ON DELETE CASCADE), `de` (text, nullable), `para` (text not null), `at` (timestamptz default now()), `por` (text — e-mail de quem moveu)
- [x] Índice por `(lead_id)` e por `(at)` — as duas leituras previstas (timeline do lead, métricas por período)
- [x] **Populada por trigger no Postgres** (`after update on leads when old.status is distinct from new.status`), NÃO pelo client — assim capta também mudanças vindas da ponte n8n/agente SDR (Viziom) e de qualquer import futuro
- [x] RLS: `select` liberado a `authenticated` (dashboards cross-role); `insert/update/delete` **negados** ao client. A função do trigger **deve ser `security definer`** (@po) — sem isso o próprio trigger é barrado pela RLS que acabamos de criar e a gravação falha em silêncio
- [x] Coluna `origem text not null default 'trigger'` com check `in ('trigger','backfill')` — **exigência do @po (ver abaixo)**
- [x] **Backfill honesto:** uma linha por lead existente (`de = null`, `para = status`, `at = created_at`, **`origem = 'backfill'`**). Serve para a timeline do lead, **não** para métrica de período.
- [x] Verificação: mover um lead no CRM → nova linha em `status_history` com `de`/`para`/`por` corretos e `origem = 'trigger'`

> ⚠️ **Correção do @po (validação contra o banco real, 2026-07-12).** O backfill original (`at = created_at`) **falsificaria as métricas**: um lead criado em 01/06 e fechado ontem viraria "transição para fechado em 01/06" — o filtro de 7 dias esconderia a venda real e o de 90 dias a contaria na data errada. Trocaríamos uma mentira (snapshot) por outra (data fabricada). O `at` real das transições passadas **não existe e não pode ser inventado** (Art. IV — No Invention).
> **Regra:** métricas de movimento (AC2) contam **apenas `origem = 'trigger'`**. Linhas de backfill existem só para dar um ponto de partida à timeline de cada lead.

### AC2 — Dashboard passa a medir movimento (F3) — @dev
- [x] `Contatos`, `Qualificados`, `Calls` deixam de contar leads parados no status e passam a contar **transições PARA aquele status dentro do período**, filtrando `status_history` por `at` **e por `origem = 'trigger'`** (backfill não conta — ver correção do @po no AC1)
- [x] `Leads Captados` continua contando criação no período (não muda) e `Fechamentos` conta transições para `fechado` no período
- [x] **Honestidade do período (exigência do @po):** o histórico começa na data da migration. Se o período selecionado for anterior a ela, os cards de movimento exibem sub-rótulo `"movimento desde {data}"` — nunca um número que finge cobrir o período inteiro
- [x] Filtro de período (7/30/90/Tudo) e filtros de vendedor/expert continuam funcionando sobre a nova fonte (join `lead_id` → cache de leads, sem duplicar colunas)
- [x] Funil comercial (`renderFunnel`) **mantém** a lógica de estágio acumulado atual (é um funil de posição, não de fluxo) — não confundir as duas leituras
- [x] Sem `status_history` disponível (erro de rede), o dashboard não quebra: degrada para a contagem antiga **e diz que está degradado** (não exibir número de fluxo com dado de snapshot em silêncio)

### AC3 — Permissão do financeiro vem do banco (F4) — @data-engineer + @dev
- [x] Coluna `profiles.financeiro boolean not null default false` (migration aditiva)
- [x] `is_financeiro_user()` reescrita para ler `profiles.financeiro` do usuário logado (mantém o nome e a assinatura — as policies existentes do módulo financeiro continuam válidas sem alteração)
- [x] Os 4 e-mails atuais recebem `financeiro = true` no mesmo script — **seed via `auth.users` (@po):** `update profiles p set financeiro = true from auth.users u where u.id = p.id and u.email in (...)`. NÃO casar por `profiles.name` (hoje name guarda o e-mail por coincidência do código de login — é frágil)
- [x] `is_financeiro_user()` continua **`security definer stable`** (precisa ler `profiles` independente da RLS de quem chama). Verificado no banco: 8 policies (`vendas` e `parcelas`, 4 cmd cada) dependem dela — manter nome e assinatura preserva todas
- [x] No JS: `FINANCEIRO_USERS` e a função local `isFinanceiroUser()` baseada em e-mail são **removidas**; a flag vem junto com o `profiles.select('role')` do login (`select('role, financeiro')`)
- [x] Verificação: dar/remover a flag no banco muda o acesso ao módulo financeiro **sem deploy**

### AC4 — Expert e equipe centralizados (F6) — @dev
- [x] Constantes únicas no topo do JS: `EXPERTS` (ativos), `EXPERTS_ARQUIVADOS`, `SDRS`, `CLOSERS`
- [x] Todos os selects (novo lead, filtros do dashboard, filtros de leads, detalhe do lead, agente SDR) são montados a partir dessas constantes — nenhum `<option>` de pessoa/expert escrito à mão no HTML
- [x] **Dr. Alex arquivado:** sai dos selects de cadastro/edição; **continua** aparecendo em filtros e relatórios **se houver dados históricos dele** (não apagar o passado)
- [x] `renderExperts()` monta a lista a partir dos experts presentes nos dados + ativos (não da constante hardcoded `['Dr. Alex','Cindy Batista']`)
- [x] Trocar um SDR/closer/expert passa a ser edição de **1 linha**

### AC5 — Sem regressão
- [x] Pipeline, Kanban CS, Financeiro, Reuniões e Agente SDR seguem funcionando
- [x] Leads históricos com expert "Dr. Alex" continuam renderizando normalmente
- [x] Lote 1 intacto (modais de transição, chips, undo, toasts)

---

## Tasks

- [x] **T1** (@data-engineer) — `setup-status-history-v1.sql`: tabela + índices + trigger + RLS + backfill
- [x] **T2** (@data-engineer) — `setup-financeiro-flag-v1.sql`: coluna `profiles.financeiro` + `is_financeiro_user()` lendo do banco + seed dos 4 usuários atuais
- [x] **T3** (@data-engineer) — aplicar as duas migrations em produção e **verificar no banco** (linha em `status_history` após um update; `is_financeiro_user()` retornando true para os 4)
- [x] **T4** (@dev) — dashboard lê `status_history` (métricas de movimento) com degradação segura
- [x] **T5** (@dev) — remover `FINANCEIRO_USERS`; flag vem do `profiles`
- [x] **T6** (@dev) — constantes `EXPERTS`/`SDRS`/`CLOSERS`; selects montados; Dr. Alex arquivado
- [x] **T7** (@dev/@qa) — verificação em browser: mover lead → métrica sobe; filtro de período; sem Dr. Alex em cadastro; mobile

---

## Dev Notes

**Por que trigger e não insert no client:** o CRM não é a única porta de entrada dos leads (a ponte n8n do agente SDR / Viziom escreve direto no banco, e há imports por SQL). Histórico populado pelo client perde tudo que não passa pela UI. Além disso, a RLS de `leads` permite update por vários roles — o trigger é o único ponto que vê todas as mudanças.

**Semente do event-bus (Fase 3 do REFACTOR-PLAN):** `status_history` é literalmente a primeira tabela de eventos de domínio do CRM. A integração Viziom (follow-up automático) vai consumir daqui, e o Sales Coach (Fase 3) pode cruzar transição × reunião. Modelar com isso em mente — mas **sem** generalizar para uma tabela `events` genérica agora (anti-overengineering; ver §5 do UX-IMPROVEMENT-PLAN).

**`por` (quem moveu):** dentro do trigger, usar `auth.email()` quando houver (client autenticado) e cair para `null`/`'system'` quando a mudança vier de um contexto sem sessão (n8n com service key).

**Cuidado com o filtro de vendedor/expert no dashboard:** `status_history` não tem `resp`/`expert` — o cruzamento é via `lead_id` → `leads`. Fazer o join no client (cache de leads já existe) em vez de duplicar colunas.

**Constraints:** single-file, vanilla JS, sem build. Migrations aditivas e idempotentes (padrão dos SQLs existentes).

---

## CodeRabbit Integration

- **Story type:** Database + Feature
- **Focus:** SQL injection nas queries novas, RLS coverage da tabela nova, migration safety (idempotência), correção das métricas
- **Gate:** CRITICAL → auto-fix · HIGH → auto-fix · MEDIUM → débito

---

## Verificação (obrigatória antes de Done)

1. Mover um lead novo → call → followup e conferir: "Calls" do período = 1 (hoje seria 0, porque o lead saiu da coluna)
2. `select * from status_history order by at desc limit 5` mostra as transições com `de`, `para`, `por`
3. Tirar a flag `financeiro` de um usuário no banco → ele perde a aba Cobranças **sem deploy**
4. Cadastro de novo lead **não** oferece Dr. Alex; lead histórico do Dr. Alex continua aparecendo no relatório
5. Mobile (390px): dashboard e selects OK

---

## File List

- `docs/crm/setup-status-history-v1.sql` (novo, @data-engineer) — tabela + índices (1 parcial) + trigger `security definer` + RLS select-only + backfill marcado
- `docs/crm/setup-financeiro-flag-v1.sql` (novo, @data-engineer) — `profiles.financeiro` + `is_financeiro_user()` lendo do banco + seed upsert via `auth.users`
- `docs/crm/index.html` (modificado, @dev) — `loadHistory`/`contarMovimento`/`subRotuloMovimento`; `renderDashboard` mede movimento; `EXPERTS`/`SDRS`/`CLOSERS`/`opts`/`initSelectsEquipe`/`refreshFiltrosExpert`; `currentFinanceiro` do banco; `FINANCEIRO_USERS` removido

## Dev Agent Record

**Agent Model Used:** Opus 4.8 — @data-engineer (Dara) SQL · @dev (Dex) frontend

**Completion Notes:**
- **A mentira do dashboard está provada e corrigida.** Cenário verificado no browser: lead que fez call e avançou para Follow Up contava **0 calls** na regra antiga; agora conta **1**.
- **Honestidade de período:** se o intervalo pedido é anterior ao início do histórico, o card diz `"desde 08/07"` em vez de fingir cobrir 90 dias. Sem histórico, diz `"sem histórico — mostrando posição atual"` e degrada para a contagem de posição — nunca exibe número de fluxo com dado de snapshot em silêncio.
- **Backfill não polui métrica:** as 190 linhas de backfill têm `origem='backfill'` e a query filtra `origem='trigger'`.
- **F4:** `FINANCEIRO_USERS` eliminado do JS; `currentFinanceiro` vem de `profiles.financeiro` (mesma fonte que a RLS). Trocar quem vê o Financeiro = UPDATE no banco, sem deploy.
- **F6:** Dr. Alex fora do cadastro (verificado: `f-expert` = Cindy + Outro), mas preservado em filtros/relatórios enquanto houver dados históricos (`expertsComDados()`). Zero `<option>` de pessoa no HTML.

**Debug Log — bug real encontrado na verificação:**
`initSelectsEquipe()` estava sendo chamada **antes** da declaração de `EXPERTS`/`SDRS` (const). A TDZ lançava `ReferenceError: Cannot access 'expertsAtivos' before initialization` e **derrubava o boot inteiro do script** — o `vm.Script` (parse) passava limpo, só o browser revelou. Chamada movida para o fim do script. Console limpo após o fix.

**Incidente de produção (@data-engineer):** durante a verificação do trigger, um `UPDATE` de teste foi feito em lead real enquanto o Vitor usava o CRM ao vivo; 2 leads (Kamila, Adriana) tiveram status alterado indevidamente e foram **reparados** (estado final conferido contra o pré-migration: 145 perdidos / 22 fechados / 22 contato+qualificado / 1 quente = 190). Gotcha registrado: **nunca testar trigger com UPDATE em linha real — usar transação com ROLLBACK**.

---

## Change Log

| Data | Autor | Mudança |
|------|-------|---------|
| 2026-07-12 | @sm (River) | Story criada a partir do UX-IMPROVEMENT-PLAN §4 Lote 2 |
| 2026-07-12 | @po (Pax) | Validação 8/10 GO contra o banco real (190 leads, 29 vendas, 4 profiles). 3 correções: (1) backfill com `origem` e fora das métricas — o `at=created_at` falsificaria fechamentos; (2) trigger `security definer` senão a própria RLS o bloqueia; (3) seed do financeiro via `auth.users`, não por `profiles.name`. |

---

## QA Results

**Gate:** `docs/qa/gates/crm-ux-002-lote2.yml` · **Verdict: PASS** (após 1 iteração do QA Loop) · @qa (Quinn), 2026-07-12

**ISSUE-1 (HIGH) — encontrado e corrigido:** `contarMovimento()` usava como universo os leads de `filterLeads()`, que corta por **data de criação**. Um lead criado há 60 dias e **fechado hoje** ficava fora do universo do filtro de 7 dias — a venda de hoje não era contada. Era a **mesma classe de erro que o Lote 2 veio corrigir**, apenas amarrada ao `created_at` em vez do status. Evidência: "Fechamentos" exibia 0 onde deveria exibir 1.
**Fix:** dois universos explícitos — `filterLeadsSemPeriodo()` (só vendedor/expert) para movimento, com o recorte de período aplicado ao `at` da transição; `filterLeads()` (com `created`) segue servindo Leads Captados, tabela e funil. Taxa/Ticket/Valor Total passaram a derivar de quem **fechou no período**.
**Re-verificado:** lead de 60 dias fechado hoje conta (7d) · venda de 45 dias atrás não polui · filtro de expert respeitado · 90d = 3 fechamentos · valor = R$ 12.000.

**Focos auditados e aprovados:** Financeiro sem regressão (`currentFinanceiro` setado antes de `applyRole`); RLS de `status_history` só tem `sh_select` — insert/update/delete negados ao client, histórico imutável; Dr. Alex fora do cadastro mas presente em filtros e relatório com dados históricos, e seus leads renderizam normalmente.

**Débito (low):** o gráfico "Evolução Diária — Leads" plota criação (correto), mas o título pode ser lido como movimento — renomear no Lote 3.
