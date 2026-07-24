-- ── ARVEX CRM — RLS de leitura em agente_sdr_historico ──────────────────────
-- Story:   crm-atendimento-unificacao (Fase 1) · ADR: atendimento-unificacao-ARCHITECTURE.md
-- Versao:  1.0 | 2026-07-24 | @data-engineer (Dara)
-- Rodar:   aditivo, idempotente
--
-- CONTEXTO: agente_sdr_historico guarda as conversas vivas da Carol (memoria n8n:
-- session_id=telefone, message jsonb LangChain). A tabela esta com RLS habilitado
-- e ZERO policies => deny-all para a chave anon do navegador. Por isso o CRM nao
-- consegue exibir as conversas no Atendimento.
--
-- DECISAO: liberar SOMENTE SELECT para usuarios autenticados (staff), espelhando
-- o padrao ja usado em `leads` (SELECT TO authenticated USING true). E PII de
-- cliente, mas da mesma camada de sensibilidade que `leads`, que o staff ja le.
--
-- WRITES: nao ha policy de INSERT/UPDATE/DELETE de proposito. A Carol (n8n) e o
-- envio do operador (edge function evolution-proxy) escrevem via service_role,
-- que BYPASSA RLS. O navegador nunca altera o historico — defense in depth.
-- ─────────────────────────────────────────────────────────────────────────────

-- garante RLS ligado (ja esta, mas idempotente e explicito)
alter table public.agente_sdr_historico enable row level security;

-- leitura para staff autenticado (mesmo criterio de leads)
drop policy if exists agente_sdr_historico_select on public.agente_sdr_historico;
create policy agente_sdr_historico_select
  on public.agente_sdr_historico
  for select
  to authenticated
  using (true);

comment on policy agente_sdr_historico_select on public.agente_sdr_historico is
  'Fase 1 atendimento: staff autenticado le as conversas da Carol no CRM. '
  'Writes ficam so no service_role (n8n Carol + edge evolution-proxy). ADR atendimento-unificacao.';

-- ─────────────────────────────────────────────────────────────────────────────
-- VALIDACAO (esperado):
--   -- policy existe:
--   select policyname, cmd from pg_policies where tablename='agente_sdr_historico';
--   -- como anon => 0 linhas (deny); como authenticated => le. Testar no app.
-- ROLLBACK:
--   drop policy if exists agente_sdr_historico_select on public.agente_sdr_historico;
-- FIM
-- ─────────────────────────────────────────────────────────────────────────────
