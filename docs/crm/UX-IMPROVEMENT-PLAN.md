# CRM ARVEX — Auditoria de UX/Usabilidade & Plano de Modernização

> Autor: Fable 5 (janela 2026-07-12) · auditoria linha a linha de `docs/crm/index.html` (3.212 linhas, 9 views)
> Executor previsto: @dev (Dex) com Sonnet/Opus — documento autossuficiente, NÃO requer reanálise
> Irmão do `REFACTOR-PLAN.md` (higiene de código): este cobre o eixo **experiência/fluxo de trabalho**. Lote 4 funde os dois.

---

## 1. Constraints (idênticas ao REFACTOR-PLAN — não violar)

- Single-file `index.html`, vanilla JS + Supabase UMD. Sem framework, sem build step.
- Usuários reais em produção: Vitor (admin), Sabrina (CS), SDRs, financeiro (Vitor/Gabriel/Pacheco).
- **Paleta, layout e identidade visual (Linear/Attio dark) FICAM** — o redesign visual já foi aprovado. Este plano melhora fluxo, não estética.
- Heurísticas do Vitor aplicáveis: A2 (mobile é o juiz — validar TODO lote no viewport mobile), A4 (cirurgia, não reforma), C3 (simplicidade corta camada), C4 (ship primeiro).

## 2. Método da auditoria

Fluxo real por persona: SDR (novo lead → mover card → WhatsApp → registrar atividade), Sabrina (checks de hoje → mover card CS → registrar resposta), Financeiro (cobranças do dia → marcar pago), Vitor (dashboard → drill). Cada finding tem linha e evidência.

## 3. Findings ranqueados

### 🔴 F1 — `prompt()`/`confirm()`/`alert()` nativos no fluxo principal
`changeStatus()` (l.2157-2190) usa **4 prompts nativos** nas transições mais frequentes do CRM: motivo da perda, data da call, próximo passo, valor fechado. Mais: `confirm()` em deleteLead (l.2206), moverParaCS (l.2613), excluirVenda (double-confirm, l.3130-3131); `alert()` como único feedback de erro em ~15 pontos. Problemas: quebra total do visual premium; péssimo no mobile; sem validação; sem opções pré-definidas. O sistema de modais JÁ existe (7 modais no arquivo) — é replicação, não invenção.

### 🔴 F2 — Motivo de perda em texto livre → relatório vira lixo
O prompt de perda aceita qualquer string; `renderExperts()` (l.2050) agrupa por string exata. "Sem budget" ≠ "sem budget" ≠ "orçamento" → buckets fragmentados, análise de perda inútil. Fix: modal com **chips pré-definidos** (Sem budget · Não era o perfil · Não atendeu · Concorrente · Sumiu/Ghost · Outro+texto). Heurística A7: o dado só vale se agregável.

### 🔴 F3 — Dashboard mede snapshot, não movimento (métrica mente)
`m-contatos`/`m-qualif`/`m-calls` contam leads **atualmente naquele status** (l.1678-1681). Um lead que fez call e avançou pra followup some de "Calls". "Calls realizadas: 3" pode significar 15 calls no período. Não existe histórico de transição. Fix estrutural: tabela `status_history` (lead_id, from, to, at, by) + insert em `changeStatus()` → métricas de fluxo honestas (calls no período, tempo médio por etapa, conversão real). **Bônus estratégico: é a semente do event-bus da Fase 3 do REFACTOR-PLAN (seam Viziom) e alimenta o Sales Coach Fase 3.**

### 🔴 F4 — Resto da Fase 1 no client: e-mails hardcoded continuam
RLS v2 aplicado no banco ✅, mas o JS ainda: define role por listas de e-mail hardcoded (l.1284-1286), mantém `FINANCEIRO_USERS` (l.1262) e faz `profiles.upsert({role})` client-side (l.1305, 1338). O RLS bloqueia auto-promoção, mas o passo 2 da Fase 1 ("JS lê role de profiles; apagar listas") nunca foi concluído. Fix: 1 query em `profiles` no login → `currentRole`/`isFinanceiro` do banco; remover upserts de role e listas.

### 🟠 F5 — Modal de detalhe do lead NÃO permite mudar status (mobile sofre)
`openDetail()` (l.2106-2151) mostra tudo mas não move o lead. Única forma de mover = drag no kanban (touch com long-press 400ms + auto-scroll — frágil no celular). A classe `.move-chips` (l.321-323) foi desenhada e **nunca usada**. Fix: linha de chips de status no modal detail (1 chip por coluna, atual destacado) → mover vira 2 toques no mobile. Heurística A2.

### 🟠 F6 — Expert morto e equipe hardcoded em 6+ lugares
"Dr. Alex" saiu da operação (2026-07-06), mas segue em: form novo lead (l.927), filtros dashboard/leads (l.573, 684), `renderExperts()` (l.2039), agente SDR (l.2661). SDRs/closers (Victor P/Gabriel/Vitor) hardcoded em 4 selects (form, detail×2). Fix: constantes únicas `EQUIPE = {experts:[], sdrs:[], closers:[]}` no topo do JS (1 lugar pra editar) e montar todos os selects a partir delas; arquivar Dr. Alex (mantém histórico nos dados, some dos forms novos).

### 🟠 F7 — Zero teclado: Esc não fecha modal, sem atalhos
Nenhum modal fecha com Esc ou clique no overlay. Sem atalhos para uso diário (N=novo lead, /=busca). Para operador que vive no CRM, é fricção diária. Fix: listener global (Esc fecha `.modal-overlay.open`; clique no overlay idem — cuidado para não fechar com clique dentro do modal); N e / com guard de input focado.

### 🟠 F8 — Sem undo em ações destrutivas
deleteLead apaga de verdade com 1 confirm. Fix barato: toast "Lead excluído · **Desfazer**" (guarda o objeto 6s; desfazer = re-insert). Padrão moderno que elimina o medo do ✕.

### 🟡 F9 — Feedback inconsistente: toast só no financeiro
`showToast()` (l.3172) é global mas só o financeiro usa. Salvar lead, mover card, registrar check → silêncio. Fix: toast em todo CRUD de sucesso; erros trocam `alert()` por toast `.error`.

### 🟡 F10 — Busca re-renderiza tudo a cada tecla, sem debounce
`oninput="renderAllLeads()"` (l.673) e similares reconstroem o innerHTML da tabela inteira por caractere. Com o volume atual passa; com o agente SDR captando, trava. Fix: `debounce(150ms)` compartilhado.

### 🟡 F11 — Sem loading states: primeira carga "pisca" dados zerados
Login → dashboard renderiza 0s → dados chegam → números pulam. Fix: skeleton simples (classe `.skeleton` com shimmer nos metric-cards e 3 linhas de tabela) enquanto `loadLeads()` não resolve. Percepção de velocidade estilo Linear.

### 🟡 F12 — Sem deep-link/rota: refresh sempre volta pro dashboard
`goTo()` não toca na URL. Não dá pra mandar "olha esse lead" no WhatsApp do time. Fix: hash routing mínimo (`#pipeline`, `#lead/{id}` abre o detail) — ~20 linhas, muda o uso em equipe.

### 🟡 F13 — Bugs de CSS: variáveis inexistentes
`.fin-metodo-sel` usa `var(--text)` (l.435) e `.fin-search-wrap input:focus` usa `var(--accent)` (l.439) — **nenhuma das duas existe** em `:root` → cor herdada errada e foco sem highlight. Fix: trocar por `--white`/`--blue`.

### 🟡 F14 — Emojis vs Lucide: migração de ícones ficou pela metade
Sistema Lucide inline existe (l.1149+), mas sobram emojis: 👥 no h1 (l.820), 💬📱🎯❌🤝📹 nos cards/detail, ✏️🗑️↩️➤ em botões, ✅🔴⏳ em badges fin. Padronizar tudo em Lucide (adicionar os paths que faltam: trash, pencil, send, undo) = salto de maturidade visual imediato.

### 🟡 F15 — Pipeline sem valor por coluna
`col-header` mostra só count (l.1822). Para admin, somar ticket da coluna (`R$ 34k`) ao lado do count = visão de pipeline value (padrão Attio/Pipedrive), 5 linhas de código.

### 🔵 F16 — Menores
- Sidebar "Em breve — Agenda" morta (l.525-528): remover.
- Telefone sem normalização no save → wa.me quebra se digitarem +55 (normalizar em `insertLead`).
- Botão login sem loading/disable (duplo submit).
- Tabela Leads sem paginação (adiar até doer — anti-overengineering).
- `CS_SUBS` hardcoded no JS (l.2226): mudar processo CS exige deploy. Mover pra tabela config na **Fase 3** (white-label precisa de qualquer forma). NÃO fazer agora.

## 4. Plano de execução — lotes

### Lote 0 — Correções secas (30 min, zero risco)
F13 (vars CSS) · F16 sidebar morta · Esc/overlay fecha modais (parte do F7) · debounce (F10) · loading do botão login.
**Verificação:** foco visível na busca fin; Esc fecha todos os 8 modais; digitação fluida na busca.

### Lote 1 — Fluxo sem prompts nativos (1 sessão @dev)
F1+F2: um modal genérico `modal-transition` reutilizado pelas 4 transições (perda com chips+outro, call com datetime, followup com texto, fechado com valor) · confirm de delete/excluir vira modal padrão · F8 undo no delete · F9 toasts globais.
**Verificação:** mover card para cada coluna especial nos viewports desktop E mobile; motivo de perda só aceita chip ou "Outro" preenchido; excluir lead → desfazer → lead volta.

### Lote 2 — Verdade dos dados (1 sessão @dev + @data-engineer para o SQL)
F3: `setup-status-history-v1.sql` (tabela + índice; insert no `changeStatus`) → dashboard passa a contar transições do período (calls realizadas, fechamentos) · F4 role do banco · F6 equipe centralizada + arquivar Dr. Alex.
**Verificação:** mover lead novo→call→followup e conferir que "Calls" do período = 1 (não 0); login Sabrina continua caindo direto no CS; nenhum select mostra Dr. Alex.

### Lote 3 — Modernização Linear-like (1-2 sessões @dev)
F5 chips de status no detail · F12 hash routing + deep-link de lead · F14 Lucide 100% · F15 valor por coluna · F7 atalhos N e /.
**Verificação:** mobile: abrir lead → mudar status por chip em 2 toques; colar `#lead/{id}` em aba nova abre o modal certo; zero emojis na UI (grep visual).

### Lote 4 — Fusão com REFACTOR-PLAN Fase 2 (background, YOLO por view)
Ao passar a higiene (239 inline styles → classes, 81 onclick → delegation), executar **por view e por cima dos lotes 1-3 já aplicados**, nunca antes — evita retrabalho. Ordem por view: dashboard → pipeline → leads → cs → financeiro → coach → agente.

## 5. O que NÃO fazer

- ❌ Redesign visual (paleta/tipografia/layout aprovados ficam).
- ❌ Framework, build, virtual scrolling, paginação preventiva.
- ❌ Notificações push, multi-idioma, dark/light toggle.
- ❌ Command palette ⌘K completa — desejável, mas só depois do Lote 3 (e só se o uso pedir; N + / cobrem 80%).
- ❌ Mexer no kanban CS além do que os lotes especificam (usuários ativos).

## 6. Publicação

Cada lote sobe para produção pelo fluxo atual (cópia manual `docs/crm/index.html` → raiz na main), **reconciliando antes** com o alerta de divergência master/main (memória `project_crm_divergencia_master_main`). Smoke test pós-deploy: login das 3 personas + 1 ação núcleo de cada.
