-- ── BUG-A FIX — registrar_evento_lead grava no formato que o front lê ─────────
-- Story: crm-sdr-buga-fix
-- Versao: 2.0 | 2026-07-14 | Opus 4.8
-- Rodar: aditivo/idempotente. Testado em transacao+ROLLBACK antes de aplicar.
--
-- ANTES: gravava {autor, texto, data(ISO)} -> o front le {text, date(epoch)} e
--        renderizava undefined. As mensagens do agente sumiam do modal do lead.
-- AGORA: grava {text, date(epoch ms), autor} -> compativel com o front + o campo
--        'autor' habilita as bolhas do chat de atendimento (lead vs agente vs humano).
-- Linhas antigas no formato {texto,data} sao tratadas pela normalizacao no front.
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
    'text',  p_texto,
    'date',  (extract(epoch from now()) * 1000)::bigint,
    'autor', p_autor
  );

  select id, status into v_lead_id, v_status from leads where tel = p_tel limit 1;

  if v_lead_id is null then
    insert into leads (nome, tel, status, origem, activities)
    values (coalesce(p_nome, p_tel), p_tel, 'contato', 'whatsapp-agente-sdr', jsonb_build_array(v_evento))
    returning id into v_lead_id;
  else
    update leads
    set activities = coalesce(activities, '[]'::jsonb) || v_evento,
        status = case when v_status = 'novo' then 'contato' else v_status end
    where id = v_lead_id;
  end if;

  return v_lead_id;
end;
$$;

grant execute on function registrar_evento_lead(text, text, text, text) to service_role;
grant execute on function registrar_evento_lead(text, text, text, text) to authenticated;
