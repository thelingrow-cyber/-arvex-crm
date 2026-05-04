-- ── ARVEX CRM — CS v3 — Checks criados só ao entrar em Campanha ─────────────
-- Rodar no Supabase SQL Editor
-- Versão: 3.0 | 2026-04-30

-- 1. Remove checks existentes criados prematuramente
delete from cs_checks ch
using clientes_cs cc
where ch.cliente_cs_id = cc.id
  and cc.cs_stage <> 'campanha';

-- 2. Drop trigger antigo (criava checks no INSERT)
drop trigger if exists cs_criar_checks on clientes_cs;

-- 3. Nova função — cria checks só quando entra em Campanha
create or replace function criar_checks_ao_entrar_campanha()
returns trigger language plpgsql as $$
declare
  v_base date;
  v_existing integer;
begin
  -- só dispara quando cs_stage muda PARA 'campanha'
  if new.cs_stage = 'campanha' and (old.cs_stage is distinct from 'campanha') then

    -- verifica se já tem checks (evita duplicar)
    select count(*) into v_existing from cs_checks where cliente_cs_id = new.id;
    if v_existing > 0 then return new; end if;

    -- base: data_triagem se preenchida, senão hoje
    v_base := coalesce(new.data_triagem, current_date);

    insert into cs_checks (cliente_cs_id, dia_relativo, semana, entregavel, data_prevista) values
      (new.id, 2,  1, 'Confirmar acesso à plataforma',         v_base + 2),
      (new.id, 4,  1, 'Grupo VIP criado — solicitar link',      v_base + 4),
      (new.id, 6,  1, 'Primeiras mensagens disparadas — print', v_base + 6),
      (new.id, 8,  1, 'Campanha no ar — print da oferta',       v_base + 8),
      (new.id, 10, 1, 'Resultado parcial de vendas — número',   v_base + 10),
      (new.id, 13, 2, 'Resultado parcial da campanha',          v_base + 13),
      (new.id, 16, 2, 'Campanha encerrada — resultado final',   v_base + 16);
  end if;
  return new;
end;
$$;

create trigger cs_criar_checks_campanha
  after update on clientes_cs
  for each row execute procedure criar_checks_ao_entrar_campanha();

-- FIM
