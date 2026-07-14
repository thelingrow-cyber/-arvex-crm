-- ── ARVEX CRM — F4: fila de follow-up automático do agente SDR ──────────────
-- Story:   crm-viziom-integracao-f4
-- Versão:  1.0 | 2026-07-14 | @dev (execução autônoma noturna)
-- Rodar:   Supabase SQL Editor ou psql direto — aditivo, idempotente
--
-- Contexto (VIZIOM-INTEGRATION-PLAN.md, fluxo F3):
--   lead sem resposta → +4h toque 1 → +24h toque 2 → +48h toque 3 →
--   +72h marca 'sem resposta' e encerra a fila (lead fica pra ação humana).
--   Qualquer resposta do lead zera/reprograma a fila (isso é lógica do n8n,
--   que faz DELETE/UPDATE nesta tabela via service_role — não é trigger de banco,
--   fica simples e visível no workflow em vez de escondido em PL/pgSQL).
--
-- Quem escreve aqui: o n8n via service_role key (bypassa RLS por natureza).
-- RLS existe para o caso de alguém tentar mexer via anon key logado.
-- ─────────────────────────────────────────────────────────────────────────────

-- 1. TABELA — fila de follow-up (1 linha ativa por lead; workflow reusa a
--    mesma linha entre toques, só avança agendado_para/tentativa)
create table if not exists sdr_followups (
  id            uuid primary key default gen_random_uuid(),
  lead_id       uuid not null references leads(id) on delete cascade,
  tel           text not null,
  tentativa     int not null default 0,        -- 0 = ainda não tocou; 1/2/3 = qual toque já foi
  agendado_para timestamptz not null,           -- quando o próximo toque deve disparar
  status        text not null default 'pendente' check (status in ('pendente','concluido','cancelado')),
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- só 1 fila ativa por lead — evita duplicar follow-up se o n8n rodar 2x por engano
create unique index if not exists sdr_followups_lead_pendente_uidx
  on sdr_followups (lead_id) where status = 'pendente';

create index if not exists sdr_followups_poll_idx
  on sdr_followups (status, agendado_para);

-- 2. CADÊNCIA CONFIGURÁVEL — o Vitor ajusta pela UI do CRM (aba Agente SDR)
alter table agente_sdr add column if not exists cadencia jsonb
  default '{"toques_horas":[4,24,48],"encerra_horas":72}'::jsonb;

comment on table sdr_followups is 'Fila de follow-up automático do agente SDR (F4). Escrita pelo n8n via service_role; nunca por trigger de banco.';
comment on column agente_sdr.cadencia is 'Horas de espera de cada toque + prazo de encerramento. Default: 4h/24h/48h, encerra em 72h.';

-- 3. RLS — segue o mesmo padrão do resto (setup-rls-v2-security.sql):
--    select amplo (dashboards podem querer mostrar fila pendente), mutação só admin.
--    service_role do n8n ignora RLS por natureza — isto é só contra abuso via anon key.
alter table sdr_followups enable row level security;

drop policy if exists "followups_select" on sdr_followups;
create policy "followups_select" on sdr_followups for select to authenticated using (true);

drop policy if exists "followups_insert" on sdr_followups;
create policy "followups_insert" on sdr_followups for insert to authenticated with check (is_admin());

drop policy if exists "followups_update" on sdr_followups;
create policy "followups_update" on sdr_followups for update to authenticated using (is_admin());

drop policy if exists "followups_delete" on sdr_followups;
create policy "followups_delete" on sdr_followups for delete to authenticated using (is_admin());

-- ── COMO VERIFICAR DEPOIS DE RODAR ──────────────────────────────────────────
--   select tablename, policyname, cmd from pg_policies where tablename='sdr_followups';
--   select column_name from information_schema.columns where table_name='agente_sdr' and column_name='cadencia';
