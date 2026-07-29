-- ============================================================================
-- _evo_sync_debug — destrava o diagnóstico do sync_out (Atendimento / VIZIOM)
-- Aplicado em produção: 2026-07-29
--
-- CONTEXTO: o evolution-proxy, na ação `sync_out`, JÁ grava um registro de
-- diagnóstico nesta tabela desde o commit 81b79e9 ("sync de mensagens enviadas
-- pelo celular (fromMe) — dry-run"). A tabela nunca foi criada, e o insert usa
-- `.then(()=>{}, ()=>{})` — ou seja, falhava em SILÊNCIO. Resultado: nenhum
-- rastro do que o Evolution devolve, justo na fase em que isso era o objetivo.
--
-- O QUE FICA GRAVADO em info (jsonb), a cada abertura da aba Atendimento:
--   apply              → se o sync está em dry-run (false) ou gravando (true)
--   http / ok          → status da chamada ao Evolution /chat/findMessages
--   total              → mensagens que o Evolution devolveu
--   fromMe             → quantas eram saídas (nossas)
--   candidatos         → quantas sobraram após tirar grupos, já-sincronizadas
--                        e balões da própria Carol
--   amostra_candidatos → até 8 exemplos {sid, waId, texto, ts}
--
-- COMO LER (acesso direto ao banco, ver memória reference_supabase_db_direto):
--   select at, info from _evo_sync_debug order by id desc limit 5;
-- ============================================================================

create table if not exists public._evo_sync_debug (
  id   bigserial primary key,
  at   timestamptz not null default now(),
  info jsonb
);

-- RLS ligada e SEM policies: só o service_role (usado pela edge function)
-- escreve. Nada acessível pela anon key — é tabela de diagnóstico, não de app.
alter table public._evo_sync_debug enable row level security;
revoke all on public._evo_sync_debug from anon, authenticated;
