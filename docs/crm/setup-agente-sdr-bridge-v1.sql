-- ── ARVEX CRM — F1: Ponte n8n↔CRM (registrar evento do agente SDR) ─────────
-- Story:   crm-viziom-integracao-f1
-- Versão:  1.0 | 2026-07-06 | @dev
-- Rodar:   Supabase SQL Editor — aditivo, idempotente
--
-- Chamada via RPC pelo n8n (service_role, bypassa RLS) a cada mensagem
-- recebida/enviada pelo agente. Idempotente: se o lead já existe (por tel),
-- atualiza; senão, cria com status='contato' (AD-5: entra direto no funil).
-- ─────────────────────────────────────────────────────────────────────────────

create or replace function registrar_evento_lead(
  p_tel   text,
  p_nome  text,
  p_texto text,
  p_autor text default 'lead'  -- 'lead' | 'agente' | 'humano'
)
returns uuid language plpgsql security definer as $$
declare
  v_lead_id uuid;
  v_status  text;
  v_evento  jsonb;
begin
  v_evento := jsonb_build_object(
    'autor', p_autor,
    'texto', p_texto,
    'data',  now()
  );

  select id, status into v_lead_id, v_status from leads where tel = p_tel limit 1;

  if v_lead_id is null then
    insert into leads (nome, tel, status, origem, activities)
    values (coalesce(p_nome, p_tel), p_tel, 'contato', 'whatsapp-agente-sdr', jsonb_build_array(v_evento))
    returning id into v_lead_id;
  else
    update leads
    set activities = activities || v_evento,
        status = case when v_status = 'novo' then 'contato' else v_status end
    where id = v_lead_id;
  end if;

  return v_lead_id;
end;
$$;

comment on function registrar_evento_lead(text, text, text, text) is
  'Chamada pelo n8n (agente SDR) a cada mensagem: cria o lead se nao existir '
  '(status=contato) ou loga o evento em activities. Bypassa a UI - so a ponte n8n via service_role usa.';

grant execute on function registrar_evento_lead(text, text, text, text) to service_role;
grant execute on function registrar_evento_lead(text, text, text, text) to authenticated;

-- ─────────────────────────────────────────────────────────────────────────────
-- VALIDACAO (rodar depois, no SQL Editor):
--   select registrar_evento_lead('5511999999999', 'Teste F1', 'oi, quero saber mais', 'lead');
--   select nome, tel, status, activities from leads where tel = '5511999999999';
--   -- limpar teste depois: delete from leads where tel = '5511999999999';
-- FIM — F1 Ponte
-- ─────────────────────────────────────────────────────────────────────────────
