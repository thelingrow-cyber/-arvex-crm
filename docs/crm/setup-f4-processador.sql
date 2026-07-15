-- ── F4 Processador — parte de banco (coluna + view) ─────────────────────────
-- Story:   crm-sdr-f4-processador
-- Autor:   Dara (@data-engineer) | 2026-07-15 | aditivo/idempotente
-- Handoff: @architect (Aria) — docs/crm/AGENTE-SDR-F4-PROCESSADOR-ARCHITECTURE.md
--
-- (1) prompt_followup: system prompt do toque de follow-up (a IA gera o texto —
--     ADR-F4-1). Nullable; se vazio, o workflow usa um default embutido.
-- (2) v_followups_devidos: 1 GET resolve o poll do n8n (fila + dados do lead
--     pros gates ADR-F4-2). security_invoker herda a RLS das tabelas base.
-- ─────────────────────────────────────────────────────────────────────────────

-- (1) prompt de follow-up, editável pela UI depois
alter table agente_sdr add column if not exists prompt_followup text;
comment on column agente_sdr.prompt_followup is
  'System prompt do toque de follow-up (F4). A IA gera o texto retomando o contexto. Se null, workflow usa default.';

-- (2) view do poll: fila pendente e vencida + dados do lead pros gates
create or replace view v_followups_devidos
with (security_invoker = true) as
select
  f.id,
  f.lead_id,
  f.tel,
  f.tentativa,
  f.agendado_para,
  f.status,
  l.status         as lead_status,
  l.agente_pausado,
  l.nome,
  l.activities
from sdr_followups f
join leads l on l.id = f.lead_id
where f.status = 'pendente'
  and f.agendado_para <= now();

comment on view v_followups_devidos is
  'F4 poll: follow-ups pendentes já vencidos, com dados do lead pros gates (lead_status, agente_pausado, activities). security_invoker.';

-- (3) o poll index (status, agendado_para) já existe: sdr_followups_poll_idx.
--     Nada a criar — validado no handoff.
