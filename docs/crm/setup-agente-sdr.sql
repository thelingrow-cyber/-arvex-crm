-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║                    CRM ARVEX — setup-agente-sdr.sql                        ║
-- ╠═══════════════════════════════════════════════════════════════════════════╣
-- ║ Tabela de configuração/treino dos Agentes SDR (IA).                       ║
-- ║ A tela "Agente SDR" do CRM grava aqui; o N8N LÊ esta config pra rodar     ║
-- ║ o agente no WhatsApp (prompt, modelo, conhecimento, escalonamento).       ║
-- ║                                                                           ║
-- ║ Autor: @data-engineer (Dara) · Data: 2026-05-29                          ║
-- ║ Natureza: aditiva, idempotente, sem destrutivos. RLS ampla (controle de   ║
-- ║           acesso é por role no frontend, padrão das tabelas do CRM).      ║
-- ║                                                                           ║
-- ║ COMO APLICAR: Supabase → SQL Editor → colar tudo → Run.                   ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. TABELA — agente_sdr
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists agente_sdr (
  id                  uuid default gen_random_uuid() primary key,

  -- Identidade
  nome                text not null,                 -- ex: "Carol"
  ativo               boolean default false,         -- liga/pausa o agente
  cor                 text,                          -- hex pro card (opcional)
  expert              text,                          -- nicho: cindy | dr_alex | geral (text livre)
  whatsapp_numero     text,                          -- número Evolution que o agente usa (opcional)

  -- Inteligência
  modelo              text default 'claude-sonnet-4-6',

  -- Comportamento / Treino
  instrucoes          text,                          -- personalidade/prompt base
  conhecimento        text,                          -- base de conhecimento (treino, vai no prompt)
  qualificacao        text,                          -- critério de qualificação/desqualificação
  mensagem_abertura   text,                          -- saudação proativa ao lead novo

  -- Ferramentas / Escalonamento
  escalar_ativo       boolean default true,
  escalar_instrucoes  text,                          -- quando passar pro humano
  notificar_ativo     boolean default false,
  notificar_contato   text,                          -- quem/quando notificar

  created_at          timestamptz default now(),
  updated_at          timestamptz default now()
);

comment on table agente_sdr is
  'Config/treino dos agentes SDR (IA). Frontend grava; N8N lê pra rodar o agente no WhatsApp.';
comment on column agente_sdr.ativo        is 'Liga/pausa o agente (N8N só responde se true).';
comment on column agente_sdr.expert       is 'Nicho vinculado: cindy | dr_alex | geral (text livre, sem CHECK).';
comment on column agente_sdr.instrucoes   is 'Personalidade/prompt base do agente.';
comment on column agente_sdr.conhecimento is 'Base de conhecimento (treino) injetada no prompt.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. RLS — padrão amplo to authenticated (controle por role no frontend)
-- ─────────────────────────────────────────────────────────────────────────────
alter table agente_sdr enable row level security;

drop policy if exists "agente_sdr_select" on agente_sdr;
drop policy if exists "agente_sdr_insert" on agente_sdr;
drop policy if exists "agente_sdr_update" on agente_sdr;
drop policy if exists "agente_sdr_delete" on agente_sdr;

create policy "agente_sdr_select" on agente_sdr for select to authenticated using (true);
create policy "agente_sdr_insert" on agente_sdr for insert to authenticated with check (true);
create policy "agente_sdr_update" on agente_sdr for update to authenticated using (true);
create policy "agente_sdr_delete" on agente_sdr for delete to authenticated using (true);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. TRIGGER — updated_at automático (reusa função existente update_updated_at)
-- ─────────────────────────────────────────────────────────────────────────────
drop trigger if exists agente_sdr_updated_at on agente_sdr;
create trigger agente_sdr_updated_at
  before update on agente_sdr
  for each row execute procedure update_updated_at();

-- ─────────────────────────────────────────────────────────────────────────────
-- VALIDAÇÃO:
--   select column_name, data_type from information_schema.columns
--   where table_name = 'agente_sdr' order by ordinal_position;
--
-- FIM — ARVEX CRM Agente SDR
-- ─────────────────────────────────────────────────────────────────────────────
