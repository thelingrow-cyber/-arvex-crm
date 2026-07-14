# CRM ARVEX — Análise Arquitetural & Plano de Refatoração

> Autor: @architect (Aria) · 2026-07-05 · análise executada com Fable 5 (janela)
> Executor previsto: @dev (Dex) com Opus/Sonnet — este documento é autossuficiente; NÃO requer reanálise
> Repo: `thelingrow-cyber/-arvex-crm` · deploy: Vercel (`arvex-crm.vercel.app`)

---

## 1. Contexto e constraints (não violar)

- **Single-file por design:** `index.html` (3.212 linhas / 207KB) é o app inteiro. O fluxo de publicação é cópia manual master→main de UM arquivo — **manter single-file até a Fase 3**; não introduzir build step sem decisão explícita do Vitor.
- **Stack:** vanilla JS + Supabase (UMD via CDN). Sem framework. Manter.
- **Norte estratégico:** este CRM vira **biblioteca/base do SaaS óptico white-label** e recebe a **integração de IA Viziom** (follow-up de leads). A refatoração deve criar as *costuras* (seams) para isso, não reescrever o produto.
- **Usuários reais em produção** (Vitor/admin, Sabrina/CS, SDRs). Nada pode quebrar o kanban CS nem o pipeline.

## 2. Raio-X (medido em 2026-07-05)

| Métrica | Valor |
|---|---|
| Linhas totais | 3.212 (CSS 10-462 · **2º `<style>` no body l.854-895** · JS 1142-3210) |
| Views | 9 (dashboard, pipeline, leads, cs, financeiro, clientes-fin, experts, coach, agente-sdr) |
| Tabelas Supabase | 8 (parcelas 7×, leads 5×, agente_sdr 5×, vendas 4×, meetings 4×, profiles 2×, clientes_cs 2×, cs_checks 1×) |
| `style="` inline | 239 |
| `onclick=` inline | 81 |
| Funções | ~132 (escopo global único) |
| `innerHTML` | 34 (helper `esc()` existe na l.3188, uso inconsistente) |
| Chamadas `.from()` | 31, espalhadas (sem camada de dados) |

## 3. Findings (ranqueados)

### 🔴 CRITICAL-1 — Autorização é só cosmética no client
- Roles definidas por **lista de e-mails hardcoded no JS** (l.1284-1286) e enforcement por `el.style.display` (l.1315-1320).
- RLS no banco: `clientes_cs`, `cs_checks`, `leads`, `agente_sdr` com `using (true)` para qualquer `authenticated` — **qualquer SDR autenticado pode ler/alterar/deletar TODA a base (CS, leads, agente) via API direta com a anon key**, que é pública por natureza.
- **Ironia útil:** a tabela `profiles.role` JÁ existe e JÁ é populada; e o módulo financeiro JÁ implementou o padrão certo (`is_financeiro_user()` em `setup-financeiro-v1.sql`). O fix é replicação, não invenção.

### 🟠 HIGH-1 — Superfície XSS via innerHTML
34 usos de `innerHTML` com interpolação de dados do banco; `esc()` aplicado de forma inconsistente. Dados vindos de leads/notas (input externo indireto) podem injetar script.

### 🟠 HIGH-2 — Monólito sem seams
132 funções globais, estado global, 31 acessos a dados espalhados. Consequências: (a) toda edição por agente de IA relê 207KB — **custo de token por story alto**; (b) impossível reusar módulos no SaaS óptico; (c) integração Viziom não tem ponto de acoplamento limpo.

### 🟡 MEDIUM-1 — 239 inline styles vs design tokens existentes
O redesign (Linear/Attio) criou tokens no `<style>` principal, mas 239 `style="` os contornam. Segundo `<style>` dentro do body (l.854) é anomalia a absorver no bloco principal.

### 🟡 MEDIUM-2 — 81 onclick inline
Handlers no HTML acoplam markup↔lógica e já causaram bug de escaping (resolvido por índice no CS). Event delegation elimina a classe inteira de bugs.

### 🔵 LOW — CDN sem pin de versão exata do supabase-js; SQLs versionados como arquivos soltos (v1-v5) sem ordem de migração documentada.

## 4. Arquitetura alvo (pragmática, 3 fases)

**Princípio: reutilizar → adaptar → criar.** Nada de framework, nada de build, nada de reescrita.

### Fase 1 — SEGURANÇA (fazer primeiro; ~1 sessão @dev)
1. **Migração `setup-roles-rls-v1.sql`** (novo): funções `is_admin()`, `is_cs_or_admin()` lendo `profiles.role` (padrão copiado de `is_financeiro_user()`); substituir policies `using (true)` de `clientes_cs`, `cs_checks`, `leads`, `agente_sdr` por policies por role. Manter `select` liberado onde o app precisa (SDR vê leads) e restringir `update/delete` por role.
2. **JS lê role de `profiles`** (1 query no login, já existe `.from('profiles')`) e apaga as listas de e-mails hardcoded. `currentRole` vem do banco; o CSS-hiding vira UX, não segurança.
3. **Auditoria XSS mecânica:** listar os 34 `innerHTML`, aplicar `esc()` em toda interpolação de dado do banco (heurística: fix mecânico primeiro, um a um; NÃO criar abstração nova).
- **Verificação:** logar como SDR de teste e tentar, via console, `sb.from('clientes_cs').delete()...` → deve falhar; kanban CS e pipeline seguem funcionando para os roles corretos.

### Fase 2 — HIGIENE INTERNA (single-file mantido; 1-2 sessões @dev)
1. Absorver o 2º `<style>` (l.854) no bloco principal.
2. Converter os 239 inline styles em classes utilitárias sobre os tokens existentes (lote por view: dashboard → pipeline → cs → financeiro…). Mecânico, ideal p/ Sonnet.
3. Substituir 81 `onclick` por event delegation (1 listener por view; `data-action`/`data-id` no markup) — padrão já provado no CS (índice em vez de string).
4. Organizar o JS em **seções nomeadas por view** com bandeiras de comentário (`// ===== VIEW: CS =====`), agrupando: estado, data-access, render, handlers. Sem módulos ES ainda — só ordem.
- **Verificação:** diff visual por view (screenshot antes/depois) + smoke test dos fluxos: criar lead, mover card pipeline, mover card CS, registrar check, lançar venda.

### Fase 3 — SEAMS PARA SAAS + VIZIOM (quando a integração começar)
1. Extrair camada `db.*` (repository-lite): as 31 chamadas `.from()` viram funções nomeadas (`db.leads.list()`, `db.cs.moveCard()`…) numa seção única — pré-requisito para trocar backend/white-label.
2. Ponto de acoplamento Viziom: eventos de domínio (`lead.created`, `cs.checkMissed`) emitidos num barramento simples (função `emit()` + tabela `events` ou webhook) — a IA de follow-up consome daí, sem tocar na UI.
3. SÓ AQUI decidir split de arquivo/build, com o fluxo de deploy repensado junto.

## 5. O que NÃO fazer (anti-overengineering)

- ❌ Migrar para React/Vue/Next — o vanilla single-file atende e o time é 1 pessoa + agentes.
- ❌ Criar build step na Fase 1-2 — quebra o fluxo de publicação por cópia.
- ❌ TypeScript, testes E2E, monorepo — antes das seams da Fase 3, é peso morto.
- ❌ Reescrever o kanban CS — funciona e tem usuários; só higienizar.

## 6. Ordem de execução recomendada

`Fase 1 (CRITICAL, agora) → Fase 2 em lotes por view (background, YOLO) → Fase 3 puxada pela integração Viziom (âncora)`

Cada fase cabe em stories `@sm *draft` ou execução direta `@dev` (padrão ~80% do Vitor). Fase 1 é pré-requisito de QUALQUER exposição maior do CRM (novos usuários, SaaS, demo).
