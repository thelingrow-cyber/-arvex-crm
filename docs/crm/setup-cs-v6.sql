-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║                       CRM ARVEX — setup-cs-v6.sql                          ║
-- ╠═══════════════════════════════════════════════════════════════════════════╣
-- ║ v6 — Reordenação manual persistente de cards no kanban                    ║
-- ║                                                                           ║
-- ║ Feature: arrastar card pra cima/baixo dentro da coluna e a ordem PERSISTE ║
-- ║ Autor:  @data-engineer (Dara)                                             ║
-- ║ Data:   2026-05-29                                                        ║
-- ║                                                                           ║
-- ║ DECISÃO DE DESIGN — ranking fracionário (double precision):              ║
-- ║   • Inserir um card entre A e B = posicao (A+B)/2 → apenas 1 UPDATE.      ║
-- ║   • Evita renumerar a coluna inteira a cada arraste (padrão Trello/Jira). ║
-- ║   • Aplicado em clientes_cs (ordena por cs_stage) e leads (por status).   ║
-- ║                                                                           ║
-- ║ NATUREZA: aditiva, idempotente, sem DROP. Backfill só toca linhas NULL,   ║
-- ║           então é seguro rodar múltiplas vezes. RLS existente já cobre.   ║
-- ║                                                                           ║
-- ║ COMO APLICAR:                                                             ║
-- ║   1. Supabase Dashboard → SQL Editor → colar tudo → Run                   ║
-- ║   2. Esperado: "Success. No rows returned."                               ║
-- ║   3. Aplicar ANTES do deploy do front v6.                                 ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Coluna de posição (ranking fracionário)
-- ─────────────────────────────────────────────────────────────────────────────
alter table clientes_cs add column if not exists posicao double precision;
alter table leads       add column if not exists posicao double precision;

comment on column clientes_cs.posicao is
  'Ranking fracionário p/ ordenação manual dentro da coluna (cs_stage). Menor = topo. Reorder = (A+B)/2.';
comment on column leads.posicao is
  'Ranking fracionário p/ ordenação manual dentro da coluna (status). Menor = topo. Reorder = (A+B)/2.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Backfill dos registros existentes (só onde posicao IS NULL → idempotente)
--    Inicializa por coluna, na ordem atual (created_at), com gap de 1000
--    pra deixar espaço amplo entre cards (permite muitas inserções por bisseção).
-- ─────────────────────────────────────────────────────────────────────────────
with ranked_cs as (
  select id,
         row_number() over (partition by cs_stage order by created_at) * 1000.0 as nova_pos
  from clientes_cs
)
update clientes_cs c
   set posicao = r.nova_pos
  from ranked_cs r
 where r.id = c.id
   and c.posicao is null;

with ranked_leads as (
  select id,
         row_number() over (partition by status order by created_at) * 1000.0 as nova_pos
  from leads
)
update leads l
   set posicao = r.nova_pos
  from ranked_leads r
 where r.id = l.id
   and l.posicao is null;

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Índices p/ ordenação por coluna (barato e correto; tabelas pequenas hoje,
--    mas evita full sort conforme crescem)
-- ─────────────────────────────────────────────────────────────────────────────
create index if not exists clientes_cs_stage_pos_idx on clientes_cs (cs_stage, posicao);
create index if not exists leads_status_pos_idx       on leads (status, posicao);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. (OPCIONAL — fallback raro) Rebalanceamento de uma coluna
--    Em teoria, após MUITAS reinserções no mesmo ponto, o gap entre dois
--    cards pode encolher além da precisão do double. Isso é raríssimo neste
--    volume, mas se acontecer, rode pra renumerar UMA coluna com gaps limpos.
--
--    -- CS, ex. coluna 'campanha':
--    -- with r as (select id, row_number() over (order by posicao, created_at)*1000.0 p
--    --            from clientes_cs where cs_stage='campanha')
--    -- update clientes_cs c set posicao=r.p from r where r.id=c.id;
-- ─────────────────────────────────────────────────────────────────────────────

-- VALIDAÇÃO:
--   select cs_stage, count(*), min(posicao), max(posicao)
--   from clientes_cs group by cs_stage order by cs_stage;
--
-- FIM — ARVEX CRM CS v6.0
