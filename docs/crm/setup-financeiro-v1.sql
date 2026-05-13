-- ── ARVEX CRM — Módulo Financeiro V1 ─────────────────────────────────────
-- Story:   crm-modulo-financeiro-v1 (CRM-002)
-- Versão:  1.0 | 2026-05-13 | @data-engineer (Dara)
-- Rodar:   Supabase SQL Editor — ANTES do deploy do frontend
-- Tabelas: vendas, parcelas
-- Extras:  RLS por email, trigger updated_at, função atualizar_status_parcelas()
-- ─────────────────────────────────────────────────────────────────────────

-- ── 1. HELPER: acesso ao Financeiro ──────────────────────────────────────
-- Centraliza os e-mails autorizados — alterar aqui reflete em todas as policies
create or replace function is_financeiro_user()
returns boolean language sql security definer stable as $$
  select auth.email() in (
    'viktorsimoess@gmail.com',  -- Vitor (admin)
    'arvexdigital@gmail.com',   -- Gabriel (closer)
    'vhpacheco02@gmail.com'     -- Pacheco (closer)
  )
$$;

comment on function is_financeiro_user() is
  'Retorna true para usuários com acesso total ao módulo Financeiro. '
  'Sabrina (cs) e outros são excluídos automaticamente por não constarem na lista.';

grant execute on function is_financeiro_user() to authenticated;

-- ── 2. TABELA: vendas ─────────────────────────────────────────────────────
create table if not exists vendas (
  id                   uuid        default gen_random_uuid() primary key,
  lead_id              uuid        references leads(id) on delete set null,
  cliente              text        not null,
  valor_total          numeric(10,2) not null check (valor_total > 0),
  expert               text,
  condicao_negociada   text        not null
                         check (condicao_negociada in ('avista', 'parcelado', 'entrada_saldo')),
  responsavel_cobranca text,
  observacao           text,
  created_at           timestamptz default now(),
  updated_at           timestamptz default now()
);

comment on table vendas is
  'Vendas fechadas no Pipeline. Criada automaticamente via modal ao mover lead para Fechado. '
  'Cada venda possui N parcelas na tabela parcelas.';
comment on column vendas.lead_id              is 'FK para leads.id — null se lead for deletado (registro financeiro preservado)';
comment on column vendas.condicao_negociada   is 'avista=1 parcela | parcelado=N parcelas | entrada_saldo=2 parcelas';
comment on column vendas.responsavel_cobranca is 'Nome do closer que fechou — pré-preenchido no modal, editável';

-- ── 3. TABELA: parcelas ───────────────────────────────────────────────────
create table if not exists parcelas (
  id             uuid          default gen_random_uuid() primary key,
  venda_id       uuid          not null references vendas(id) on delete cascade,
  numero         integer       not null check (numero >= 1),
  total_parcelas integer       not null check (total_parcelas >= 1),
  valor          numeric(10,2) not null check (valor > 0),
  vencimento     date          not null,
  status         text          not null default 'pendente'
                   check (status in ('pendente', 'pago', 'atrasado')),
  pago_em        date,
  metodo         text          check (metodo in ('pix', 'boleto', 'cartao')),
  created_at     timestamptz   default now(),
  updated_at     timestamptz   default now(),

  -- Integridade: parcela marcada como paga deve ter data de pagamento
  constraint parcela_paga_requer_data check (status != 'pago' or pago_em is not null)
);

comment on table parcelas is
  'Parcelas individuais de cada venda. Status atualizado por atualizar_status_parcelas() ao carregar o Financeiro.';
comment on column parcelas.numero         is 'Número da parcela (1, 2, 3...) — começa em 1';
comment on column parcelas.status         is 'pendente=aguardando | atrasado=vencido e não pago | pago=recebido';
comment on column parcelas.pago_em        is 'Data real do recebimento — preenchida ao marcar [✓ Pago]';
comment on column parcelas.metodo         is 'Método de recebimento — definido no modal ou ao marcar como pago';

-- ── 4. ÍNDICES ────────────────────────────────────────────────────────────
create index if not exists idx_vendas_lead_id
  on vendas(lead_id);

create index if not exists idx_parcelas_venda_id
  on parcelas(venda_id);

-- Índice parcial: acelera consultas de "Vencem Hoje" e "Próximos 7 dias"
create index if not exists idx_parcelas_vencimento_pendente
  on parcelas(vencimento)
  where status = 'pendente';

create index if not exists idx_parcelas_status
  on parcelas(status);

-- ── 5. TRIGGER: updated_at automático ────────────────────────────────────
create or replace function set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists vendas_set_updated_at on vendas;
create trigger vendas_set_updated_at
  before update on vendas
  for each row execute function set_updated_at();

drop trigger if exists parcelas_set_updated_at on parcelas;
create trigger parcelas_set_updated_at
  before update on parcelas
  for each row execute function set_updated_at();

-- ── 6. FUNÇÃO: atualizar parcelas atrasadas ───────────────────────────────
-- Chamar no início de loadFinanceiro() no frontend antes de buscar dados
-- Retorna quantas parcelas foram atualizadas (útil para debug)
create or replace function atualizar_status_parcelas()
returns integer language plpgsql security definer as $$
declare
  v_count integer;
begin
  update parcelas
  set    status     = 'atrasado',
         updated_at = now()
  where  status    = 'pendente'
    and  vencimento < current_date;

  get diagnostics v_count = row_count;
  return v_count;
end;
$$;

comment on function atualizar_status_parcelas() is
  'Marca como atrasado parcelas pendentes com vencimento anterior a hoje. '
  'Idempotente — seguro rodar múltiplas vezes. Chamar via rpc() no loadFinanceiro().';

grant execute on function atualizar_status_parcelas() to authenticated;

-- ── 7. RLS: vendas ────────────────────────────────────────────────────────
alter table vendas enable row level security;

-- Acesso total para Vitor, Gabriel e Pacheco; Sabrina (cs) não possui policy = sem acesso
create policy "vendas_select" on vendas
  for select to authenticated using (is_financeiro_user());

create policy "vendas_insert" on vendas
  for insert to authenticated with check (is_financeiro_user());

create policy "vendas_update" on vendas
  for update to authenticated
  using (is_financeiro_user()) with check (is_financeiro_user());

create policy "vendas_delete" on vendas
  for delete to authenticated using (is_financeiro_user());

-- ── 8. RLS: parcelas ──────────────────────────────────────────────────────
alter table parcelas enable row level security;

create policy "parcelas_select" on parcelas
  for select to authenticated using (is_financeiro_user());

create policy "parcelas_insert" on parcelas
  for insert to authenticated with check (is_financeiro_user());

create policy "parcelas_update" on parcelas
  for update to authenticated
  using (is_financeiro_user()) with check (is_financeiro_user());

create policy "parcelas_delete" on parcelas
  for delete to authenticated using (is_financeiro_user());

-- ── FIM ───────────────────────────────────────────────────────────────────
-- Para adicionar novo usuário ao Financeiro: editar is_financeiro_user() acima
-- e adicionar o e-mail à lista.
--
-- [OPCIONAL] Verificar criação:
--   select table_name from information_schema.tables
--   where table_schema = 'public' and table_name in ('vendas','parcelas');
--
-- [OPCIONAL] Verificar policies:
--   select tablename, policyname from pg_policies
--   where tablename in ('vendas','parcelas');
