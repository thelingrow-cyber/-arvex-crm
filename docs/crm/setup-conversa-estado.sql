-- ============================================================================
-- conversa_estado — "resolver" conversa no Atendimento (Fase 2 do inbox)
-- Aplicado em produção: 2026-07-29
--
-- DECISÃO DE DESIGN (por que assim e não como o Chatwoot)
-- O benchmark tem 4 abas manuais (Aberto/Aguardando/Fechado/IA). Na instância
-- real do Vitor isso estava assim: Aberto 2 · Aguardando 50 · Fechado 0 — ou
-- seja, "Aguardando" virou cemitério e ninguém nunca fechou nada. Estado que
-- depende de disciplina humana não se mantém.
--
-- Aqui existe UM único estado manual: resolvida ou não. Todo o resto é
-- DERIVADO do próprio histórico, então está sempre correto sem ninguém marcar:
--   • "esperando você"    = última mensagem da conversa é do cliente (type human)
--   • "aguardando cliente" = última mensagem é nossa (type ai)
--   • quem atende          = badge de responsável (dimensão diferente de estado)
--
-- REABERTURA AUTOMÁTICA SEM TRIGGER: a conversa conta como resolvida somente
-- enquanto `resolvida_em` for MAIS NOVO que a última mensagem do cliente. Se o
-- cliente responder depois, ela volta sozinha para a lista — é comparação de
-- timestamp na leitura, não estado a ser mantido em sincronia.
--
-- A conversa não tem tabela própria no CRM (é agrupamento por session_id em
-- agente_sdr_historico), por isso a chave aqui é o telefone/session_id.
-- ============================================================================

create table if not exists public.conversa_estado (
  session_id   text primary key,
  resolvida_em timestamptz,
  resolvida_por text,
  updated_at   timestamptz not null default now()
);

create index if not exists conversa_estado_resolvida_idx
  on public.conversa_estado (resolvida_em) where resolvida_em is not null;

alter table public.conversa_estado enable row level security;

-- Atendimento é trabalho de equipe: quem está logado no CRM opera o inbox.
-- Espelha o padrão de leitura de agente_sdr_historico (SELECT liberado a
-- authenticated); escrita idem, porque resolver/reabrir é a ação do dia a dia.
-- Não é dado sensível: guarda telefone + quando/quem resolveu.
drop policy if exists conversa_estado_select on public.conversa_estado;
create policy conversa_estado_select on public.conversa_estado
  for select to authenticated using (true);

drop policy if exists conversa_estado_insert on public.conversa_estado;
create policy conversa_estado_insert on public.conversa_estado
  for insert to authenticated with check (true);

drop policy if exists conversa_estado_update on public.conversa_estado;
create policy conversa_estado_update on public.conversa_estado
  for update to authenticated using (true) with check (true);

revoke all on public.conversa_estado from anon;
