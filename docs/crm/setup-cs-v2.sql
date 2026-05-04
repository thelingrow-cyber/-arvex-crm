-- ── ARVEX CRM — Módulo CS v2 — Correções estruturais ────────────────────────
-- Rodar no Supabase SQL Editor
-- Versão: 2.0 | 2026-04-30

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. ADICIONAR CAMPOS FALTANTES em cs_checks
-- ─────────────────────────────────────────────────────────────────────────────

-- Data prevista calculada (data_triagem + dia_relativo)
alter table cs_checks add column if not exists data_prevista date;

-- Log de tentativas de contato (array de timestamps)
alter table cs_checks add column if not exists tentativas jsonb default '[]';
-- formato: [{"data": "2026-04-30", "hora": "09:15", "resultado": "sem_resposta"}, ...]

-- Observação da resposta do aluno
alter table cs_checks add column if not exists resposta_obs text;

-- Quem executou o check
alter table cs_checks add column if not exists executado_por text;

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. ADICIONAR CAMPOS FALTANTES em clientes_cs
-- ─────────────────────────────────────────────────────────────────────────────

-- Última tentativa de contato (diferente de ultimo_contato que é quando respondeu)
alter table clientes_cs add column if not exists ultima_tentativa date;

-- Total de tentativas sem resposta consecutivas
alter table clientes_cs add column if not exists tentativas_sem_resp integer default 0;

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. RECRIAR FUNÇÃO criar_checks_padrao — com data_prevista calculada
-- ─────────────────────────────────────────────────────────────────────────────

create or replace function criar_checks_padrao()
returns trigger language plpgsql as $$
declare
  v_base date;
begin
  -- usa data_triagem se disponível, senão data_fechamento, senão hoje
  v_base := coalesce(new.data_triagem, new.data_fechamento, current_date);

  insert into cs_checks (cliente_cs_id, dia_relativo, semana, entregavel, data_prevista) values
    (new.id, 2,  1, 'Confirmar acesso à plataforma',          v_base + 2),
    (new.id, 4,  1, 'Grupo VIP criado — solicitar link',       v_base + 4),
    (new.id, 6,  1, 'Primeiras mensagens disparadas — print',  v_base + 6),
    (new.id, 8,  1, 'Campanha no ar — print da oferta',        v_base + 8),
    (new.id, 10, 1, 'Resultado parcial de vendas — número',    v_base + 10),
    (new.id, 13, 2, 'Resultado parcial da campanha',           v_base + 13),
    (new.id, 16, 2, 'Campanha encerrada — resultado final',    v_base + 16);
  return new;
end;
$$;

drop trigger if exists cs_criar_checks on clientes_cs;
create trigger cs_criar_checks
  after insert on clientes_cs
  for each row execute procedure criar_checks_padrao();

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. FUNÇÃO — recalcular datas dos checks quando data_triagem for preenchida
-- ─────────────────────────────────────────────────────────────────────────────

create or replace function recalcular_datas_checks()
returns trigger language plpgsql as $$
begin
  -- só recalcula se data_triagem mudou e não era nula antes
  if new.data_triagem is not null and (old.data_triagem is null or new.data_triagem <> old.data_triagem) then
    update cs_checks
    set data_prevista = new.data_triagem + dia_relativo
    where cliente_cs_id = new.id;
  end if;
  return new;
end;
$$;

drop trigger if exists cs_recalcular_datas on clientes_cs;
create trigger cs_recalcular_datas
  after update on clientes_cs
  for each row execute procedure recalcular_datas_checks();

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. RECRIAR FUNÇÃO calcular_churn_flag — baseado em ultima_tentativa
-- ─────────────────────────────────────────────────────────────────────────────

create or replace function calcular_churn_flag()
returns trigger language plpgsql as $$
declare
  v_ref date;
  v_dias integer;
begin
  -- usa ultima_tentativa se existe, senão ultimo_contato
  v_ref := coalesce(new.ultima_tentativa, new.ultimo_contato);

  if v_ref is not null then
    v_dias := (current_date - v_ref);
    new.churn_dias_sem_resp := v_dias;

    if v_dias >= 5 then
      new.churn_flag := 'vermelho';
    elsif v_dias >= 3 then
      new.churn_flag := 'amarelo';
    else
      new.churn_flag := 'ok';
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
-- 6. FUNÇÃO — registrar tentativa de contato num check
-- Chamada pelo frontend ao clicar "Respondeu" ou "Sem resposta"
-- ─────────────────────────────────────────────────────────────────────────────

create or replace function registrar_tentativa(
  p_check_id      uuid,
  p_resultado     text,   -- 'respondido' | 'sem_resposta'
  p_obs           text default null,
  p_executado_por text default null
)
returns void language plpgsql security definer as $$
declare
  v_check   cs_checks%rowtype;
  v_cliente clientes_cs%rowtype;
  v_nova_tentativa jsonb;
begin
  select * into v_check from cs_checks where id = p_check_id;
  if not found then raise exception 'Check não encontrado'; end if;

  select * into v_cliente from clientes_cs where id = v_check.cliente_cs_id;

  -- monta nova tentativa
  v_nova_tentativa := jsonb_build_object(
    'data',      current_date,
    'hora',      to_char(now(), 'HH24:MI'),
    'resultado', p_resultado,
    'obs',       coalesce(p_obs, '')
  );

  -- atualiza o check
  update cs_checks set
    tentativas      = tentativas || v_nova_tentativa,
    status          = p_resultado,
    data_resposta   = case when p_resultado = 'respondido' then current_date else data_resposta end,
    resposta_obs    = case when p_resultado = 'respondido' and p_obs is not null then p_obs else resposta_obs end,
    executado_por   = coalesce(p_executado_por, executado_por)
  where id = p_check_id;

  -- atualiza o cliente
  if p_resultado = 'respondido' then
    update clientes_cs set
      ultimo_contato       = current_date,
      ultima_tentativa     = current_date,
      tentativas_sem_resp  = 0,
      churn_flag           = 'ok',
      churn_dias_sem_resp  = 0
    where id = v_check.cliente_cs_id;
  else
    update clientes_cs set
      ultima_tentativa    = current_date,
      tentativas_sem_resp = tentativas_sem_resp + 1
    where id = v_check.cliente_cs_id;
  end if;

end;
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- 7. VIEW — checks de hoje (facilita o frontend mostrar "agenda do dia")
-- ─────────────────────────────────────────────────────────────────────────────

create or replace view checks_hoje as
select
  ch.id,
  ch.cliente_cs_id,
  cc.nome,
  cc.tel,
  cc.cs_stage,
  cc.churn_flag,
  ch.dia_relativo,
  ch.entregavel,
  ch.data_prevista,
  ch.status,
  ch.tentativas,
  ch.resposta_obs
from cs_checks ch
join clientes_cs cc on cc.id = ch.cliente_cs_id
where ch.data_prevista = current_date
  and ch.status = 'pendente'
order by cc.nome;

-- ─────────────────────────────────────────────────────────────────────────────
-- FIM — ARVEX CRM CS v2.0
-- ─────────────────────────────────────────────────────────────────────────────
