-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║                       CRM ARVEX — setup-cs-v5.sql                          ║
-- ╠═══════════════════════════════════════════════════════════════════════════╣
-- ║ v5 — Melhorias operacionais do módulo CS                                  ║
-- ║                                                                           ║
-- ║ Story: crm-cs-melhorias-v2                                                ║
-- ║ Autor: @data-engineer (Dara)                                              ║
-- ║ Data:  2026-05-29                                                         ║
-- ║                                                                           ║
-- ║ MUDANÇAS:                                                                 ║
-- ║   1. clientes_cs.produto           — qual produto o cliente comprou       ║
-- ║   2. clientes_cs.entregaveis_bonus — lista de bônus prometidos na venda   ║
-- ║                                                                           ║
-- ║ NÃO PRECISA mudar:                                                        ║
-- ║   • cs_stage (nova fase 'trafego') — coluna é `text` SEM constraint CHECK ║
-- ║     (ver setup-cs.sql:22), então o banco já aceita o novo valor.          ║
-- ║   • cs_checks.resposta_obs (item "o que respondeu") — JÁ existe desde v2  ║
-- ║     (ver setup-cs-v2.sql:17) e a RPC registrar_tentativa já o grava.      ║
-- ║                                                                           ║
-- ║ NATUREZA: aditiva, idempotente, sem DROP, sem destrutivos.                ║
-- ║           Campos nascem NULL / '[]' — zero impacto em dados existentes.   ║
-- ║           RLS de clientes_cs (policies "cs_*") já cobre as novas colunas. ║
-- ║                                                                           ║
-- ║ COMO APLICAR:                                                             ║
-- ║   1. Supabase Dashboard → SQL Editor                                      ║
-- ║   2. Colar este arquivo inteiro e executar                                ║
-- ║   3. Esperado: "Success. No rows returned."                               ║
-- ║   4. Aplicar ANTES do deploy do frontend v5 (senão produto/bônus quebram) ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Produto contratado pelo cliente
-- ─────────────────────────────────────────────────────────────────────────────
-- valores usados pelo frontend (CS_PRODUTOS):
--   'estrategista_optico' | 'express' | 'curadoria' | NULL (não definido)
alter table clientes_cs add column if not exists produto text;

comment on column clientes_cs.produto is
  'Produto contratado: estrategista_optico | express | curadoria. NULL = não definido.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Entregáveis bônus prometidos na venda
-- ─────────────────────────────────────────────────────────────────────────────
-- formato: ["Mentoria extra", "Pack de criativos", ...]  (array de strings)
alter table clientes_cs add column if not exists entregaveis_bonus jsonb default '[]';

comment on column clientes_cs.entregaveis_bonus is
  'Lista (jsonb) de bônus prometidos na venda. Default []. Editado pela CS no detalhe do cliente.';

-- ─────────────────────────────────────────────────────────────────────────────
-- VALIDAÇÃO
-- ─────────────────────────────────────────────────────────────────────────────
-- Conferir que as colunas existem após rodar:
--   select column_name, data_type, column_default
--   from information_schema.columns
--   where table_name = 'clientes_cs' and column_name in ('produto','entregaveis_bonus');
--
-- FIM — ARVEX CRM CS v5.0
