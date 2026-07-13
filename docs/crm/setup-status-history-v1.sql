-- ── ARVEX CRM — status_history: histórico de transições de status ───────────
-- Story:   CRM-UX-002 (Lote 2 / F3) · docs/stories/crm-lote2-verdade-dos-dados.story.md
-- Autor:   @data-engineer (Dara) · 2026-07-12 · validado por @po (Pax) 8/10 GO
-- Rodar:   aditivo e idempotente (safe re-run)
--
-- POR QUE EXISTE:
--   O dashboard contava leads PARADOS num status ("Calls: 3" = 3 leads na coluna Call),
--   não calls REALIZADAS. Lead que fez call e avançou sumia da métrica. Sem histórico de
--   transição, nenhuma métrica de movimento é possível.
--
-- DECISÕES (não reverter sem ler):
--   1. Populado por TRIGGER, não pelo client: o CRM não é a única porta de entrada
--      (ponte n8n/agente SDR e imports SQL escrevem direto no banco). Histórico gravado
--      pelo front perderia tudo que não passa pela UI.
--   2. Trigger é SECURITY DEFINER: a RLS abaixo NEGA insert ao client. Sem definer, o
--      próprio trigger seria barrado e a gravação falharia em silêncio.
--   3. `origem` separa 'trigger' (transição real) de 'backfill' (estado inicial importado).
--      O backfill usa created_at, que NÃO é a data real das transições passadas — por isso
--      ele NUNCA conta como movimento nas métricas (exigência do @po; Art. IV — No Invention).
--   4. SEM check constraint em `para`: o trigger roda dentro do UPDATE de leads. Um status
--      novo no front faria o insert falhar e derrubaria o update do lead. Integridade aqui
--      não vale o risco de travar a operação.
-- ─────────────────────────────────────────────────────────────────────────────

-- 1. TABELA
create table if not exists status_history (
  id       uuid        primary key default gen_random_uuid(),
  lead_id  uuid        not null references leads(id) on delete cascade,
  de       text,                                   -- null no backfill (não havia estado anterior)
  para     text        not null,
  at       timestamptz not null default now(),
  por      text,                                   -- e-mail de quem moveu; 'system' quando via service key (n8n)
  origem   text        not null default 'trigger'
             check (origem in ('trigger','backfill'))
);

comment on table status_history is
  'Histórico imutável de transições de status de leads. Populado APENAS pelo trigger '
  'trg_leads_status_history (security definer). origem=backfill é o estado inicial importado '
  'na migration e NÃO representa movimento real — não usar em métricas de período.';

-- 2. ÍNDICES (servem as duas leituras previstas)
create index if not exists idx_sh_lead on status_history (lead_id);                      -- timeline de um lead
create index if not exists idx_sh_at   on status_history (at desc);                      -- corte por período
create index if not exists idx_sh_mov  on status_history (para, at desc)                 -- métricas de movimento
  where origem = 'trigger';                                                              -- índice parcial: só o que conta

-- 3. TRIGGER (a única coisa que escreve aqui)
create or replace function log_status_change()
returns trigger
language plpgsql
security definer            -- indispensável: a RLS abaixo nega insert ao client
set search_path = public
as $$
begin
  insert into status_history (lead_id, de, para, por, origem)
  values (new.id, old.status, new.status, coalesce(auth.email(), 'system'), 'trigger');
  return new;
end;
$$;

comment on function log_status_change() is
  'Grava em status_history toda mudança de leads.status. SECURITY DEFINER porque a RLS de '
  'status_history nega insert ao client — o histórico só pode nascer daqui.';

drop trigger if exists trg_leads_status_history on leads;
create trigger trg_leads_status_history
  after update of status on leads
  for each row
  when (old.status is distinct from new.status)   -- reordenar card na mesma coluna não gera linha
  execute function log_status_change();

-- 4. RLS — histórico é imutável para o client
alter table status_history enable row level security;

drop policy if exists "sh_select" on status_history;
create policy "sh_select" on status_history
  for select to authenticated
  using (true);   -- dashboards cross-role (mesmo padrão de leads/vendas)

-- Sem policy de insert/update/delete = negado a qualquer client autenticado.
-- O trigger (security definer, owner postgres) não passa pela RLS.

grant select on status_history to authenticated;

-- 5. BACKFILL (idempotente) — estado inicial, marcado como tal
insert into status_history (lead_id, de, para, at, por, origem)
select l.id, null, l.status, l.created_at, 'backfill', 'backfill'
from leads l
where not exists (
  select 1 from status_history sh
  where sh.lead_id = l.id and sh.origem = 'backfill'
);

-- ─────────────────────────────────────────────────────────────────────────────
-- VERIFICAÇÃO
--   select origem, count(*) from status_history group by origem;
--   -- mover um lead no CRM e conferir:
--   select de, para, por, origem, at from status_history where origem='trigger' order by at desc limit 5;
--
-- ROLLBACK
--   drop trigger if exists trg_leads_status_history on leads;
--   drop function if exists log_status_change();
--   drop table if exists status_history;
-- ─────────────────────────────────────────────────────────────────────────────
