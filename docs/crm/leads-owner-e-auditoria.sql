-- =====================================================================
-- leads: dono (owner_id) + trilha de auditoria
-- Origem: achado A-3 da auditoria de RLS (docs/crm/security-audit-rls-2026-07-23.md)
-- Autor: Dara (squad AIOX, data-engineer) · 2026-07-29
--
-- CONTEXTO: hoje `leads_update` é USING (true) — qualquer conta autenticada
-- edita qualquer um dos 248 leads, e o único trigger existente registra
-- apenas mudança de `status`. Alteração de ticket, telefone, obs ou closer
-- não deixa rastro nenhum.
--
-- ESTE ARQUIVO É IDEMPOTENTE. Pode rodar mais de uma vez sem efeito colateral.
-- A FASE 2 (a policy) está comentada de propósito — ver o porquê no fim.
-- =====================================================================

begin;

-- ---------------------------------------------------------------------
-- FASE 1.1 — a coluna de dono
-- ---------------------------------------------------------------------
alter table public.leads
  add column if not exists owner_id uuid references public.profiles(id) on delete set null;

comment on column public.leads.owner_id is
  'Dono do lead (FK profiles). NULL = sem dono definido — editável por todos ate ser atribuido. Criado em 2026-07-29 pelo achado A-3.';

create index if not exists idx_leads_owner_id on public.leads(owner_id);

-- ---------------------------------------------------------------------
-- FASE 1.2 — todo lead novo nasce com dono
-- Sem isto, a tabela volta a acumular orfaos e o problema se repete.
-- ---------------------------------------------------------------------
create or replace function public.leads_set_owner()
returns trigger
language plpgsql
security invoker           -- roda como quem inseriu; auth.uid() e o dono real
set search_path = public
as $$
begin
  if new.owner_id is null then
    new.owner_id := auth.uid();   -- NULL quando vem do n8n/service_role: aceitavel
  end if;
  return new;
end;
$$;

drop trigger if exists trg_leads_set_owner on public.leads;
create trigger trg_leads_set_owner
  before insert on public.leads
  for each row execute function public.leads_set_owner();

-- ---------------------------------------------------------------------
-- FASE 1.3 — trilha de auditoria de QUALQUER update
-- Esta e a metade do risco que da para fechar hoje, sem depender de decisao.
-- Guarda apenas o diff (campos que mudaram), nao a linha inteira.
-- ---------------------------------------------------------------------
create table if not exists public.leads_audit (
  id          bigserial primary key,
  lead_id     uuid        not null,
  changed_at  timestamptz not null default now(),
  changed_by  uuid,                       -- auth.uid() de quem editou
  campo       text        not null,
  valor_antigo text,
  valor_novo   text
);

comment on table public.leads_audit is
  'Trilha de alteracoes em leads (diff campo a campo). Alimentada por trigger; ninguem escreve direto.';

create index if not exists idx_leads_audit_lead   on public.leads_audit(lead_id, changed_at desc);
create index if not exists idx_leads_audit_by     on public.leads_audit(changed_by, changed_at desc);

alter table public.leads_audit enable row level security;

-- leitura: so admin ve a trilha. Ninguem escreve/edita/apaga via API.
drop policy if exists leads_audit_select on public.leads_audit;
create policy leads_audit_select on public.leads_audit
  for select to authenticated
  using (is_admin());

revoke all on public.leads_audit from anon;   -- lição do A-1: nao depender so do RLS

create or replace function public.leads_log_changes()
returns trigger
language plpgsql
security definer            -- precisa gravar mesmo que o editor nao tenha grant
set search_path = public
as $$
declare
  col  text;
  ant  text;
  novo text;
begin
  foreach col in array array[
    'nome','tel','expert','origem','resp','ticket','status','socio','obs',
    'data_call','proximo_passo','motivo_perda','closer','atendente','owner_id'
  ]
  loop
    execute format('select ($1).%I::text, ($2).%I::text', col, col)
      into ant, novo using old, new;
    if ant is distinct from novo then
      insert into public.leads_audit(lead_id, changed_by, campo, valor_antigo, valor_novo)
      values (new.id, auth.uid(), col, ant, novo);
    end if;
  end loop;
  return new;
end;
$$;

drop trigger if exists trg_leads_audit on public.leads;
create trigger trg_leads_audit
  after update on public.leads
  for each row execute function public.leads_log_changes();

-- ---------------------------------------------------------------------
-- FASE 1.4 — backfill do que o Vitor confirmou (decisoes de 2026-07-29)
--   'Vitor'   -> db35377e (viktorsimoess@gmail.com)
--   'Gabriel' -> ddc790a7 (arvexdigital@gmail.com)   [D2 resolvida]
--   'Victor P' e 'Closer' -> NAO atribuidos: lixo de importacao [D1/D3]
-- Regra: `resp` manda; se `resp` for nulo, cai para `closer`.
-- ---------------------------------------------------------------------
-- Vitor  (profiles.name guarda o e-mail da conta)
update public.leads l
   set owner_id = p.id
  from public.profiles p
 where l.owner_id is null
   and p.name = 'viktorsimoess@gmail.com'
   and (l.resp = 'Vitor' or (l.resp is null and l.closer = 'Vitor'));

-- Gabriel (conta confirmada pelo Vitor em 2026-07-29)
update public.leads l
   set owner_id = p.id
  from public.profiles p
 where l.owner_id is null
   and p.name = 'arvexdigital@gmail.com'
   and (l.resp = 'Gabriel' or (l.resp is null and l.closer = 'Gabriel'));

commit;

-- =====================================================================
-- FASE 2 — a policy. NAO APLICAR AINDA.
-- =====================================================================
-- Aplicar isto hoje QUEBRA a operacao: 205 dos 248 leads (83%) nao tem
-- resp nem closer, e a Thalita (role sdr) nao e dona de nenhum lead nem e
-- admin — ela perderia a edicao de 100% da base.
--
-- A versao abaixo ja preve isso: `owner_id is null` preserva o
-- comportamento atual nos leads sem dono, e a protecao vai valendo
-- conforme os leads ganham dono. Migracao gradual, sem porta fechada
-- na cara de ninguem.
--
--   drop policy if exists leads_update on public.leads;
--   create policy leads_update on public.leads
--     for update to authenticated
--     using (owner_id = auth.uid() or owner_id is null or is_admin())
--     with check (owner_id = auth.uid() or owner_id is null or is_admin());
--
-- =====================================================================
-- DECISOES — respondidas pelo Vitor em 2026-07-29
-- =====================================================================
-- D1. 'Victor P' (17 leads, sem conta em profiles) -> LIXO DE IMPORTACAO.
--     Nao atribuido. owner_id fica NULL; seguem editaveis por todos.
-- D2. Dois profiles admin com display_name 'Gabriel' -> o humano e
--     arvexdigital@gmail.com. Backfill aplicado nessa conta (12 leads).
-- D3. 'Closer' (1 lead) -> mesmo tratamento do D1: nao atribuido.
-- D4. Thalita (sdr, sem lead proprio) -> a policy da Fase 2 preve
--     `owner_id is null`, entao ela mantem a edicao dos 226 sem dono.
--
-- ESTADO APOS A FASE 1 (aplicada em 2026-07-29):
--   248 leads · 22 com dono (Gabriel 12, Vitor 10) · 226 sem dono
--   3 triggers ativos: trg_leads_status_history, trg_leads_set_owner,
--   trg_leads_audit
--   Smoke test executado e revertido: insert atribui dono, update grava
--   diff campo a campo na trilha, anon bloqueado em leads_audit.
--
-- QUANDO APLICAR A FASE 2: quando a maioria dos leads ativos tiver dono.
-- Hoje 91% esta sem dono — a policy funcionaria, mas protegeria pouco.
-- O trigger de INSERT resolve isso sozinho com o tempo.
-- =====================================================================

-- =====================================================================
-- ROLLBACK COMPLETO
-- =====================================================================
-- begin;
--   drop trigger if exists trg_leads_audit     on public.leads;
--   drop trigger if exists trg_leads_set_owner on public.leads;
--   drop function if exists public.leads_log_changes();
--   drop function if exists public.leads_set_owner();
--   drop table if exists public.leads_audit;
--   alter table public.leads drop column if exists owner_id;
-- commit;
