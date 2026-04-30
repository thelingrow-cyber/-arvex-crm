-- ── ARVEX CRM — Módulo CS Cindy Batista ─────────────────────────────────────
-- Rodar no Supabase SQL Editor APÓS o setup.sql principal
-- Versão: 1.0 | 2026-04-30

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. TABELA PRINCIPAL — clientes_cs
-- ─────────────────────────────────────────────────────────────────────────────

create table if not exists clientes_cs (
  id                  uuid default gen_random_uuid() primary key,

  -- Vínculo com o lead original
  lead_id             uuid references leads(id) on delete set null,

  -- Dados básicos
  nome                text not null,
  tel                 text,
  expert              text default 'cindy',
  resp_cs             text,                        -- Sabrina (CS responsável)

  -- Etapa atual no kanban CS
  cs_stage            text default 'onboarding',
  -- valores: onboarding | triagem | campanha | gate_cindy | ativo | risco_churn

  -- Datas de controle
  data_fechamento     date,
  data_boas_vindas    date,
  data_triagem        date,
  data_campanha_inicio date,
  data_campanha_fim   date,
  data_reuniao_cindy  date,
  ultimo_contato      date,

  -- Gate: reunião com Cindy
  aula_assistida      boolean default false,
  campanha_rodou      boolean default false,
  resultado_coletado  boolean default false,

  -- Meta oficial (preenchida pela Cindy na reunião)
  meta_oficial        text,

  -- Resultado da campanha
  resultado_campanha  text,
  faturamento_campanha numeric,

  -- Diagnóstico de triagem (11 campos)
  diag_regiao         text,
  diag_num_lojas      integer,
  diag_tem_socio      boolean,
  diag_motivo_entrada text,
  diag_expectativa    text,
  diag_faturamento_atual numeric,
  diag_captacao       text,     -- tráfego | indicação | panfletagem | misto
  diag_instagram      text,     -- link do Instagram
  diag_seguidores     integer,
  diag_equipe_qtd     integer,
  diag_exame_vista    text,
  diag_armacoes       text,     -- marca própria | grife | misto
  diag_ticket_medio   numeric,
  diag_lentes         text,     -- marca própria | laboratório parceiro
  diag_faz_crediario  boolean,
  diag_faz_trafego    boolean,
  diag_gasto_trafego  numeric,
  diag_tem_sistema    boolean,

  -- Churn
  churn_flag          text default 'ok',
  -- valores: ok | amarelo | vermelho
  churn_dias_sem_resp integer default 0,

  -- Histórico de atividades (mesmo padrão do pipeline)
  activities          jsonb default '[]',

  -- Observações gerais
  obs                 text,

  created_at          timestamptz default now(),
  updated_at          timestamptz default now()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. TABELA DE CHECKS — cs_checks
-- Registra cada check da cadência (D+2, D+4, D+6...)
-- ─────────────────────────────────────────────────────────────────────────────

create table if not exists cs_checks (
  id              uuid default gen_random_uuid() primary key,
  cliente_cs_id   uuid references clientes_cs(id) on delete cascade,
  dia_relativo    integer not null,              -- D+2, D+4, D+6...
  semana          integer,                       -- 1 ou 2
  entregavel      text,                          -- o que foi solicitado
  resposta        text,                          -- o que o aluno enviou
  status          text default 'pendente',       -- pendente | respondido | sem_resposta
  data_check      date,
  data_resposta   date,
  created_at      timestamptz default now()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. RLS — Row Level Security
-- ─────────────────────────────────────────────────────────────────────────────

alter table clientes_cs  enable row level security;
alter table cs_checks    enable row level security;

-- clientes_cs: todos autenticados podem ler e escrever
create policy "cs_select" on clientes_cs for select to authenticated using (true);
create policy "cs_insert" on clientes_cs for insert to authenticated with check (true);
create policy "cs_update" on clientes_cs for update to authenticated using (true);
create policy "cs_delete" on clientes_cs for delete to authenticated using (true);

-- cs_checks: todos autenticados podem ler e escrever
create policy "checks_select" on cs_checks for select to authenticated using (true);
create policy "checks_insert" on cs_checks for insert to authenticated with check (true);
create policy "checks_update" on cs_checks for update to authenticated using (true);
create policy "checks_delete" on cs_checks for delete to authenticated using (true);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. TRIGGER — updated_at automático
-- ─────────────────────────────────────────────────────────────────────────────

create or replace function update_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists cs_updated_at on clientes_cs;
create trigger cs_updated_at
  before update on clientes_cs
  for each row execute procedure update_updated_at();

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. TRIGGER — churn flag automático
-- Atualiza churn_flag baseado em dias sem contato
-- ─────────────────────────────────────────────────────────────────────────────

create or replace function calcular_churn_flag()
returns trigger language plpgsql as $$
begin
  if new.ultimo_contato is not null then
    new.churn_dias_sem_resp = (current_date - new.ultimo_contato);

    if new.churn_dias_sem_resp >= 5 then
      new.churn_flag = 'vermelho';
    elsif new.churn_dias_sem_resp >= 3 then
      new.churn_flag = 'amarelo';
    else
      new.churn_flag = 'ok';
    end if;
  end if;
  return new;
end;
$$;

drop trigger if exists cs_churn_flag on clientes_cs;
create trigger cs_churn_flag
  before insert or update on clientes_cs
  for each row execute procedure calcular_churn_flag();

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. FUNÇÃO — mover lead fechado para CS
-- Chama ao clicar em "→ CS" no card do pipeline
-- ─────────────────────────────────────────────────────────────────────────────

create or replace function mover_lead_para_cs(p_lead_id uuid)
returns uuid language plpgsql security definer as $$
declare
  v_lead    leads%rowtype;
  v_novo_id uuid;
begin
  select * into v_lead from leads where id = p_lead_id;

  if not found then
    raise exception 'Lead não encontrado: %', p_lead_id;
  end if;

  insert into clientes_cs (
    lead_id, nome, tel, expert,
    data_fechamento, cs_stage, ultimo_contato
  ) values (
    v_lead.id, v_lead.nome, v_lead.tel, v_lead.expert,
    current_date, 'onboarding', current_date
  ) returning id into v_novo_id;

  -- Marca o lead como movido para CS
  update leads set status = 'cs' where id = p_lead_id;

  return v_novo_id;
end;
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- 7. CHECKS PADRÃO — inserir cadência ao criar cliente CS
-- ─────────────────────────────────────────────────────────────────────────────

create or replace function criar_checks_padrao()
returns trigger language plpgsql as $$
begin
  insert into cs_checks (cliente_cs_id, dia_relativo, semana, entregavel) values
    (new.id, 2,  1, 'Confirmação de acesso à plataforma'),
    (new.id, 4,  1, 'Grupo VIP criado — enviar link'),
    (new.id, 6,  1, 'Primeiras mensagens disparadas — enviar print'),
    (new.id, 8,  1, 'Campanha no ar — enviar print da oferta'),
    (new.id, 10, 1, 'Resultado parcial de vendas — enviar número'),
    (new.id, 13, 2, 'Resultado parcial da campanha — enviar números'),
    (new.id, 16, 2, 'Campanha encerrada — enviar resultado final');
  return new;
end;
$$;

drop trigger if exists cs_criar_checks on clientes_cs;
create trigger cs_criar_checks
  after insert on clientes_cs
  for each row execute procedure criar_checks_padrao();

-- ─────────────────────────────────────────────────────────────────────────────
-- FIM — ARVEX CRM CS v1.0
-- ─────────────────────────────────────────────────────────────────────────────
