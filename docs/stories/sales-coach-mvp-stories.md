# Stories — Sales Coach MVP (arvex-crm)

**Autor:** @sm (River) · Data: 2026-06-27 · Status: Draft (aguarda validação @po)
**Refs:** `docs/crm/sales-coach-mvp-brief.md` · `sales-coach-architecture.md` · `setup-sales-coach-v1.sql` · `sales-coach-ux-spec.md`
**Stack:** `docs/crm/index.html` (vanilla) + Supabase (DB/RLS/Realtime) + Supabase Edge Function (Deno/TS) + API Claude. **Sem n8n.**

## Pré-condições externas (infra do Vitor — bloqueiam o "ao vivo")
- **P1** `ANTHROPIC_API_KEY` disponível p/ secret da Edge Function.
- **P2** Acesso ao Supabase SQL Editor do CRM (rodar S1).
- **P3** Capacidade de deploy de Edge Function (Supabase CLI **ou** editor do Dashboard).
> O código (S2–S6) é escrito independente da infra; P1–P3 só são necessárias pra rodar de verdade.

## Mapa de execução
- 🟢 **FATIA VERTICAL DE HOJE:** S1 → S2 → S3 → S4 (prova o loop com 1 transcrição de teste).
- 🔵 **Enhancements:** S5 (detalhe rico) — *na prática S4 precisa de um detalhe mínimo; S5 enriquece* — e S6 (evolução).
- Ordem de dependência: **S1 bloqueia tudo**; S2 e S3 podem ir em paralelo; S4 depende de S1+S2+S3; S5 depende de S3/S4; S6 depende de dados (S4).

---

## S1 — Banco: tabela `meetings` + RLS  🟢
**Contexto:** base de dados do módulo. DDL já pronto em `setup-sales-coach-v1.sql` (parte MVP).
**AC:**
1. Rodar a PARTE MVP do `setup-sales-coach-v1.sql` no Supabase → "Success".
2. Tabela `meetings` existe com todos os campos do DDL; `resultado` NOT NULL; `status` default 'pending'.
3. RLS ativa: closer só vê/edita o próprio; admin vê/edita tudo; delete só admin (4 políticas).
4. Seção Fase 2 (pgvector) **não** executada.
**Tasks:** [ ] aplicar SQL · [ ] validar `select count(*) from meetings`=0 · [ ] conferir `pg_policies` (4).
**Deps:** P2. **DoD:** tabela + RLS no Supabase, validadas.

## S2 — Edge Function `analyze-meeting`  🟢
**Contexto:** backend da análise (architecture §2/§3).
**AC:**
1. Função recebe `{ meeting_id }`, valida JWT do chamador (usuário autenticado).
2. Seta `status='processing'`, lê `transcript` (service_role).
3. Chama Claude (temp 0) com **rubrica fixa** + **playbook curto hardcoded** + transcript; força **JSON estrito**: `nota_geral`, `scores{8 dims}`, `insights{acertos[],erros[],faltou[],sugestoes[]}`.
4. Valida/parseia JSON; grava `scores/insights/nota_geral`, `status='done'`, `analyzed_at=now()`.
5. Em falha (LLM/parse): `status='error'`, `erro_msg` preenchido; não derruba a função.
6. `ANTHROPIC_API_KEY` lida de secret (nunca hardcoded). Custo-alvo NFR1 (centavos).
**Tasks:** [ ] scaffold função Deno · [ ] prompt+rubrica das 8 dimensões · [ ] tool/JSON schema do Claude · [ ] parse+persist · [ ] tratamento de erro · [ ] secret.
**Deps:** S1, P1, P3. **DoD:** invocando com um `meeting_id` de teste, grava notas/insights reais.

## S3 — Aba "Coach" + Lista  🟢
**Contexto:** UX spec §1/§2.
**AC:**
1. Item `nav-coach` (ícone `graduation-cap`, seção Comercial) → `view-coach` via `goTo`.
2. Gating `applyRole`: closer/sdr veem (só as suas, por RLS); admin vê todas + filtro por closer; cs não vê.
3. Lista renderiza cards: cliente, produto, data, closer, **resultado** (dot+label), **nota geral** (tabular-nums), **status** (dot: pendente/analisando/analisado/erro).
4. Filtros (busca cliente, resultado, período) e **empty state**.
5. **Demo mode `?demo=1`** injeta 3–4 reuniões fictícias.
6. Visual herda 100% o design system (sem componente novo além do medidor).
**Tasks:** [ ] nav+view+goTo · [ ] applyRole · [ ] query `meetings` + render cards · [ ] filtros · [ ] empty state · [ ] demo data.
**Deps:** S1. **DoD:** aba navegável, lista real + demo, gating correto.

## S4 — Modal "Nova Reunião" + disparo da análise  🟢
**Contexto:** UX spec §3; fluxo architecture §2.
**AC:**
1. Botão `+ Nova reunião` abre modal com: transcrição (textarea, obrigatório), cliente, produto, data, lead (select opcional), **resultado obrigatório** (ganhou/perdeu/aberto), **ticket** condicional (só se ganhou).
2. Validação bloqueia envio sem transcrição e sem resultado.
3. Submit: `insert` em `meetings` (status=pending) → `sb.functions.invoke('analyze-meeting',{meeting_id})` → fecha modal.
4. Card aparece com **"Analisando…"** (dot âmbar) e troca p/ "Analisado" **via Realtime** sem refresh.
5. Erro de envio tratado com mensagem.
**Tasks:** [ ] modal+form · [ ] validação · [ ] insert+invoke · [ ] subscribe realtime na lista · [ ] estados.
**Deps:** S1, S2, S3. **DoD:** subir 1 transcrição de teste → análise aparece no card (loop provado = meta de hoje).

## S5 — Detalhe da call  🔵 (mínimo entra hoje; rico depois)
**Contexto:** UX spec §4.
**AC:**
1. "Ver call" (status=done) abre detalhe: topo (cliente/produto/data/closer/resultado/ticket) + **nota geral** em destaque.
2. **8 medidores** horizontais (rapport, diagnóstico, escuta, valor, controle, fechamento, transição, objeções) com valor.
3. **4 blocos de insights** (acertos/erros/faltou/sugestões) com ícones.
4. Editar **resultado/ticket** (dono ou admin — FR9).
5. Botão **Reanalisar** (re-invoca a função; status volta a processing).
**Tasks:** [ ] view/modal detalhe · [ ] medidores · [ ] insights · [ ] editar resultado · [ ] reanalisar.
**Deps:** S2, S3. **DoD:** detalhe completo renderizado a partir do `scores/insights`.
> Nota: um detalhe **mínimo** (mostrar JSON/medidores básicos) já é útil hoje; o restante (editar/reanalisar) pode fechar logo após.

## S6 — Evolução do closer  🔵 (enhancement)
**Contexto:** UX spec §5.
**AC:**
1. Painel "Minha evolução": média por dimensão (todas as reuniões do closer), calculada no front.
2. Tendência ↑/↓ vs período anterior + frase-resumo (ponto forte / foco).
3. Comparação entre closers fica para Fase 3 (fora).
**Tasks:** [ ] agregação no front · [ ] medidores de média · [ ] tendência.
**Deps:** S4 (dados). **DoD:** painel de evolução com médias e tendência.

---

## CodeRabbit / Qualidade (por story)
- S2 (Edge Function): revisar segurança (secret, validação JWT, sanitização), tratamento de erro.
- S1: revisar RLS (cobertura, sem bypass).
- S3–S6: revisar XSS na renderização da transcrição/insights (escapar HTML), consistência de UI.

## Handoff
→ **@po (Pax):** validar as stories (checklist 10 pontos). Depois → @dev implementa S1–S4 (fatia de hoje) → @qa → @devops (deploy front + função).

---

## ✅ Validação @po (Pax) — 2026-06-27 · Veredito: **GO** (9/10)

**Cobertura de FRs:**
| FR | Story | OK |
|----|-------|----|
| FR1 criar reunião (transcript/lead/data/produto) | S4 AC1 | ✅ |
| FR2 resultado + ticket no upload | S4 AC1/AC2 | ✅ |
| FR3 dispara análise | S2 + S4 AC3 | ✅ |
| FR4 notas por dimensão | S2 AC3 + S5 AC2 | ✅ |
| FR5 acertos/erros/faltou/sugestões | S2 AC3 + S5 AC3 | ✅ |
| FR6 persistência | S1 + S2 AC4 | ✅ |
| FR7 lista/detalhe/evolução | S3 + S5 + S6 | ✅ |
| FR8 alimentar Sales Brain | — | ⚠️ **deferido p/ Fase 2** (decisão de arquitetura; MVP usa playbook hardcoded) |
| FR9 confirmar/ajustar resultado | S5 AC4 | ✅ |

**Riscos endereçados:** R1 (rótulo) ✅ forte — S4 AC2 bloqueia envio sem resultado. R2 (consistência) ✅ — S2 rubrica fixa+temp0+JSON. R4 (privacidade/RLS) ✅ — S1 AC3 + nota XSS no CodeRabbit. Sequência/deps e pré-condições P1–P3 ✅.

**Ajustes recomendados (não bloqueiam o GO — incorporar na implementação):**
1. **FR8:** registrar explicitamente como **Story Fase 2** (S7 — ingestão do Sales Brain + pgvector) pra não "sumir" do backlog. (Não entra hoje.)
2. **S2:** adicionar AC do **NFR4** (resultado em ≤~2 min, fluxo assíncrono) e **validar/clampar** as notas em 0–10 ao parsear o JSON do Claude.
3. **S2/S5:** "Reanalisar" deve resetar `status→processing` e ser idempotente (sobrescreve scores anteriores).
4. **S5:** ao editar resultado p/ "ganhou", exigir/permitir ticket (consistência com FR2).

**Decisão:** **GO** para o @dev iniciar a fatia S1→S4. Enhancements (S5 detalhe rico, S6 evolução) e S7 (Fase 2) seguem no backlog.

→ Próximo elo: **@qa (Quinn)** — plano de testes / quality gate.
