-- ============================================================================
-- Sync do Atendimento — escopo das conversas + trava anti-duplicação
-- Aplicado em produção: 2026-07-29 (depois do incidente das 76.145 linhas)
--
-- POR QUE ESTE ARQUIVO EXISTE
-- Ligar o sync sem regra de escopo despejou a caixa INTEIRA do WhatsApp no CRM
-- (conversas pessoais incluídas), e o dedupe feito em memória falhou porque o
-- .select() do PostgREST corta em 1000 linhas — passando disso o polling de 25s
-- reinseria tudo. Duas correções estruturais:
--
--   1. wa_id vira COLUNA com índice único → duplicar deixa de ser possível,
--      independente da lógica da edge function estar certa. O banco garante.
--   2. evo_sync_state guarda o marco temporal ("de quando pra frente conta") e
--      a lista de números a ignorar.
--
-- REGRA DE ESCOPO (definida pelo Vitor): entra no CRM a conversa que
--   (a) for com um telefone que JÁ é lead no banco — inclusive histórico antigo; OU
--   (b) começar depois do marco em evo_sync_state.desde — conversa nova, tanto
--       iniciada pela equipe no celular quanto pela Carol.
-- Conversa antiga com quem não é lead (pessoal) fica de fora.
-- ============================================================================

-- ── 1. Trava anti-duplicação ────────────────────────────────────────────────
-- wa_id = id da mensagem no WhatsApp. Nullable: o n8n (memória LangChain) e as
-- mensagens enviadas pelo próprio CRM não têm esse id, e continuam funcionando.
alter table public.agente_sdr_historico add column if not exists wa_id text;

-- índice PARCIAL: só vale para linhas que têm wa_id, então não atrapalha o n8n
create unique index if not exists agente_sdr_historico_wa_id_uidx
  on public.agente_sdr_historico (wa_id) where wa_id is not null;

-- busca por conversa (o CRM lê por session_id; hoje só existia a PK)
create index if not exists agente_sdr_historico_session_idx
  on public.agente_sdr_historico (session_id, id);

-- ── 2. Estado do sync ───────────────────────────────────────────────────────
create table if not exists public.evo_sync_state (
  id         int primary key default 1,
  desde      timestamptz not null default now(),  -- marco: conversa nova conta a partir daqui
  ignorados  text[] not null default '{}',        -- telefones que nunca entram (pessoal)
  updated_at timestamptz not null default now(),
  constraint evo_sync_state_singleton check (id = 1)
);

insert into public.evo_sync_state (id, desde) values (1, now())
  on conflict (id) do nothing;

-- Só o service_role (edge function) enxerga. Não é dado de app.
alter table public.evo_sync_state enable row level security;
revoke all on public.evo_sync_state from anon, authenticated;
