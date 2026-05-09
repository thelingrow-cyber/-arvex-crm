-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║                       CRM ARVEX — setup-cs-v4.sql                         ║
-- ╠═══════════════════════════════════════════════════════════════════════════╣
-- ║ v4 — mantém leads.status='fechado' pra preservar visibilidade comercial   ║
-- ║      dupla (card aparece em Fechado E no CS Kanban simultaneamente)       ║
-- ║                                                                           ║
-- ║ Story: crm-quente-pre-fechado-cs                                          ║
-- ║ Autor: @data-engineer (Dara)                                              ║
-- ║ Data:  2026-05-09                                                         ║
-- ║                                                                           ║
-- ║ MUDANÇAS vs setup-cs.sql:168 (v1):                                        ║
-- ║   1. REMOVIDA  → `update leads set status = 'cs'` (linha 189 v1)          ║
-- ║   2. ADICIONADA → idempotência (retorna id existente se já em CS)         ║
-- ║                                                                           ║
-- ║ COMO APLICAR:                                                             ║
-- ║   1. Abrir Supabase Dashboard → SQL Editor                                ║
-- ║   2. Colar este arquivo inteiro e executar                                ║
-- ║   3. Verificar saída sem erros (`Success. No rows returned.`)             ║
-- ║   4. (Opcional) rodar query de migração de leads legados — ver final      ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. FUNÇÃO mover_lead_para_cs — versão 4 (idempotente, preserva status)
-- ─────────────────────────────────────────────────────────────────────────────

create or replace function mover_lead_para_cs(p_lead_id uuid)
returns uuid language plpgsql security definer as $$
declare
  v_lead     leads%rowtype;
  v_novo_id  uuid;
  v_existing uuid;
begin
  -- Carrega o lead — falha cedo se não existir
  select * into v_lead from leads where id = p_lead_id;
  if not found then
    raise exception 'Lead não encontrado: %', p_lead_id;
  end if;

  -- Idempotência: se já existe cliente_cs apontando pro lead, retorna o id existente
  -- Evita duplicatas em clientes_cs caso o botão "→ CS" seja clicado 2x rapidamente
  -- ou caso haja race condition no frontend
  select id into v_existing
  from clientes_cs
  where lead_id = p_lead_id
  limit 1;

  if v_existing is not null then
    return v_existing;
  end if;

  -- Insere novo cliente_cs (trigger cs_criar_checks dispara automaticamente)
  insert into clientes_cs (
    lead_id, nome, tel, expert,
    data_fechamento, cs_stage, ultimo_contato
  ) values (
    v_lead.id, v_lead.nome, v_lead.tel, v_lead.expert,
    current_date, 'onboarding', current_date
  ) returning id into v_novo_id;

  -- IMPORTANTE: NÃO alterar leads.status aqui.
  -- O lead permanece com status='fechado' pra continuar visível
  -- na coluna Fechado do Pipeline Comercial. O frontend usa a existência
  -- de uma row em clientes_cs.lead_id como sinal de "já enviado pro CS"
  -- pra renderizar o badge "🤝 Em CS" e esconder o botão "→ CS".

  return v_novo_id;
end;
$$;

-- Documentar a mudança diretamente no banco (queryable via \df+)
comment on function mover_lead_para_cs(uuid) is
  'v4 (2026-05-09) — Move lead pra CS preservando status=fechado. '
  'Idempotente: retorna id existente se cliente_cs já existir pro lead.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. (OPCIONAL — recomendado) Reforçar idempotência no schema
-- ─────────────────────────────────────────────────────────────────────────────
-- Constraint UNIQUE em clientes_cs.lead_id garante 1:1 lead→cliente_cs no banco,
-- mesmo se alguém chamar a função fora desse fluxo (defense in depth).
--
-- ATENÇÃO: pode falhar se já houver leads com múltiplas rows em clientes_cs.
-- Verificar antes:
--   select lead_id, count(*) from clientes_cs
--   where lead_id is not null group by lead_id having count(*) > 1;
--
-- Se a query acima retornar zero rows, descomentar:
-- create unique index if not exists clientes_cs_lead_id_uniq
--   on clientes_cs(lead_id) where lead_id is not null;

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. (OPCIONAL — pós-deploy) Migração de leads legados
-- ─────────────────────────────────────────────────────────────────────────────
-- Leads que foram pro CS antes desta v4 estão com status='cs' e ficaram
-- invisíveis no Kanban Comercial. Rodar manualmente quando o frontend v4
-- estiver em produção pra recuperar a visão histórica de Fechados:
--
-- update leads set status = 'fechado'
-- where status = 'cs'
--   and exists (select 1 from clientes_cs where lead_id = leads.id);
--
-- Conferir antes quantos leads serão afetados:
-- select count(*) from leads
-- where status = 'cs'
--   and exists (select 1 from clientes_cs where lead_id = leads.id);

-- ─────────────────────────────────────────────────────────────────────────────
-- VALIDAÇÃO DE SINTAXE
-- ─────────────────────────────────────────────────────────────────────────────
-- Este arquivo é idempotente (create or replace) e seguro pra rodar múltiplas
-- vezes. Não há DROP nem destrutivos. Sem efeito em dados existentes em
-- leads ou clientes_cs (apenas substitui a definição da função).
