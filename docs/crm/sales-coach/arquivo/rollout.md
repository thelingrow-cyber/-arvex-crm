> ⚠️ **DOCUMENTO ARQUIVADO — não use como referência.**
> Superado pelo estado atual do sistema. Ponto de entrada: [../README.md](../README.md)
> Mantido só como registro histórico.

# Plano de Rollout / Deploy — Sales Coach MVP (arvex-crm)

**Autor:** @devops (Gage) · Data: 2026-06-27 · Refs: architecture · setup-sales-coach-v1.sql · stories (P1–P3) · qa-plan (gate)
**Alçada:** publicação é exclusiva do @devops. **Gate obrigatório:** só sobe com QA = PASS (SEC-1..5 ok + smoke E2E).

---

## 0. Componentes a publicar
1. **Banco** — `setup-sales-coach-v1.sql` (parte MVP) no Supabase.
2. **Edge Function** — `analyze-meeting` + secret `ANTHROPIC_API_KEY`.
3. **Front** — aba Coach dentro de `docs/crm/index.html` → publicar via fluxo master→main do CRM.

## 1. Ordem de deploy (segura) + rollback por etapa
> Sempre nesta ordem: **dados → função → front**. Front é o último (se subir antes, chamaria função inexistente).

| # | Etapa | Ação | Rollback |
|---|-------|------|----------|
| 1 | **Banco** | Rodar parte MVP do SQL no Supabase SQL Editor | `drop table meetings cascade;` (tabela nova, isolada — não afeta o CRM atual) |
| 2 | **Secret** | Criar `ANTHROPIC_API_KEY` nos secrets do Supabase | remover o secret |
| 3 | **Edge Function** | Deploy `analyze-meeting` | deletar a função (nada no CRM depende ainda) |
| 4 | **Teste isolado** | Invocar a função com 1 `meeting_id` de teste (sem front) | — |
| 5 | **Front** | Publicar `index.html` com a aba Coach (master→main) | restaurar `index.html` anterior (cópia de backup) |

**Princípio de segurança:** as etapas 1–4 são **aditivas e isoladas** — não tocam em nada do CRM em produção. O risco real só aparece na etapa 5 (front), que tem rollback simples (arquivo).

## 2. Edge Function — passo a passo (2 opções)

### Secret (obrigatório, em ambas)
- Supabase Dashboard → **Project Settings → Edge Functions → Secrets** → add `ANTHROPIC_API_KEY = sk-ant-...`
- (CLI alternativo: `supabase secrets set ANTHROPIC_API_KEY=sk-ant-...`)

### Opção A — Dashboard (sem CLI, recomendado p/ o Vitor)
1. Dashboard → **Edge Functions → Create a function** → nome `analyze-meeting`.
2. Colar o código (entregue pelo @dev) no editor.
3. **Deploy** pelo botão.

### Opção B — Supabase CLI
1. `supabase login` · `supabase link --project-ref <ref>`
2. código em `supabase/functions/analyze-meeting/index.ts`
3. `supabase functions deploy analyze-meeting`

### Teste isolado (antes do front)
- Inserir manualmente uma linha em `meetings` (SQL) com uma transcrição de teste.
- Invocar: Dashboard (Function → Invoke) ou `curl` com o anon/JWT + `{ "meeting_id": "<id>" }`.
- **Esperado:** linha vira `status=done` com `scores`/`insights`. (Cobre QA S2-1.)

## 3. Front (aba Coach) — fluxo master→main do CRM
> Memória `project_crm_deploy_flow`: **master = trabalho** (`docs/crm/index.html`), **main = produção** (`index.html` na raiz). Publicar = **sync manual master→main (copiar o arquivo), NÃO merge git.**
1. Confirmar aba Coach funcionando no `docs/crm/index.html` (master) com `?demo=1` e contra o Supabase.
2. **Backup** do `index.html` de produção atual (rollback da etapa 5).
3. Copiar `docs/crm/index.html` → `index.html` (raiz/produção), conforme o fluxo já estabelecido.
4. Publicar produção como já é feito hoje no CRM.

## 4. Checklist PRÉ-deploy
- [ ] QA gate = **PASS** (qa-plan): smoke E2E fecha + **SEC-1..5 ok** (RLS, service_role, XSS escapado, key não vaza).
- [ ] CodeRabbit sem CRITICAL na Edge Function e no front.
- [ ] Secret `ANTHROPIC_API_KEY` setado (não no front).
- [ ] Backup do `index.html` de produção feito.
- [ ] Custo por reunião confirmado em centavos (NFR1).

## 5. Checklist PÓS-deploy
- [ ] Login real (closer + admin) → gating correto (closer só o seu).
- [ ] Smoke E2E em produção: subir 1 transcrição → análise volta → detalhe ok.
- [ ] Console do navegador sem erro.
- [ ] Confirmar no banco que a transcrição (dado sensível) só é acessível por RLS.

## 6. Rollback total (se algo quebrar pós-deploy)
1. Restaurar `index.html` de produção (backup) → CRM volta ao estado anterior **na hora** (a feature some, nada mais é afetado).
2. (Opcional) desativar a Edge Function.
3. Tabela `meetings` pode ficar (isolada) ou `drop` se quiser limpeza total.
> Como a feature é aditiva e isolada, o rollback do front já neutraliza o risco para o resto do CRM.

## 7. Responsabilidades
| Item | Quem |
|------|------|
| Fornecer `ANTHROPIC_API_KEY` | **Vitor** |
| Rodar o SQL no Supabase | **Vitor** (ou @devops orienta) |
| Deploy da Edge Function | **Vitor** (Dashboard) ou @devops (se tiver acesso/CLI) |
| Publicar o front (master→main) | **@devops** (alçada exclusiva) |
| Escrever código (função + aba) | @dev |
| Gate de qualidade | @qa |

---
**Status:** planejamento COMPLETO. Próximo passo: **@dev implementa a fatia S1→S4**. Deploy só após QA PASS e com a infra do Vitor pronta (P1–P3).

— Gage, deployando com confiança 🚀
