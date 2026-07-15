-- ── Mídias do agente SDR (provas sociais pro lembrete de call) ───────────────
-- Story: crm-sdr-lembrete-call (Fase 3)
-- Versao: 1.0 | 2026-07-15 | Opus 4.8 | aditivo/idempotente
--
-- Guarda as imagens em base64 no banco pra o envio via Evolution sendMedia não
-- depender de hospedagem externa. Populada por script (lê os .jpeg de
-- docs/agente-sdr/provas-sociais/ e grava base64). O workflow de lembrete lê
-- daqui e alterna as provas por índice na fila do dia.
-- ─────────────────────────────────────────────────────────────────────────────

create table if not exists sdr_midias (
  id         uuid primary key default gen_random_uuid(),
  chave      text unique not null,        -- 'prova-16k-63k', 'prova-naty'
  descricao  text,
  mime       text not null default 'image/jpeg',
  base64     text not null,               -- imagem em base64 (sem prefixo data:)
  ordem      int  not null default 0,     -- ordem de alternância (0, 1, ...)
  ativo      boolean not null default true,
  created_at timestamptz not null default now()
);

comment on table sdr_midias is
  'Provas sociais (imagens base64) usadas pelo lembrete de call. Alternadas por ordem.';

-- Popular: node script que lê os .jpeg e grava base64 (ver commit VIZIOM-F3).
-- Conferir:  select chave, ordem, length(base64) from sdr_midias where ativo order by ordem;
