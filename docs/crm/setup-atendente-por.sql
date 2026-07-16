-- ── "quem atendeu" (por) no evento de mensagem humana ───────────────────────
-- Story: crm-atendimento-quem-atende
-- Versao: 3.0 | 2026-07-15 | aditivo
--
-- registrar_evento_lead ganha p_por opcional: quando um humano responde pelo
-- CRM (autor='humano'), grava QUEM atendeu no evento ({...,"por":"nome"}). O
-- valor vem do login validado na edge function evolution-proxy (não do front,
-- pra não ser forjável). A versao de 4 args foi DROPADA — a de 5 args cobre as
-- chamadas antigas (n8n) via default p_por=null (sem ambiguidade de overload).
-- ─────────────────────────────────────────────────────────────────────────────

drop function if exists registrar_evento_lead(text, text, text, text);

create or replace function registrar_evento_lead(
  p_tel text, p_nome text, p_texto text, p_autor text default 'lead', p_por text default null
)
returns uuid language plpgsql security definer as $$
declare v_lead_id uuid; v_status text; v_evento jsonb;
begin
  v_evento := jsonb_build_object('text', p_texto, 'date', (extract(epoch from now())*1000)::bigint, 'autor', p_autor);
  if p_por is not null and p_por <> '' then v_evento := v_evento || jsonb_build_object('por', p_por); end if;
  select id, status into v_lead_id, v_status from leads where tel = p_tel limit 1;
  if v_lead_id is null then
    insert into leads (nome, tel, status, origem, activities)
    values (coalesce(p_nome, p_tel), p_tel, 'contato', 'whatsapp-agente-sdr', jsonb_build_array(v_evento))
    returning id into v_lead_id;
  else
    update leads set activities = coalesce(activities, '[]'::jsonb) || v_evento,
      status = case when v_status = 'novo' then 'contato' else v_status end
    where id = v_lead_id;
  end if;
  return v_lead_id;
end; $$;

grant execute on function registrar_evento_lead(text, text, text, text, text) to service_role, authenticated;
