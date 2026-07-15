-- ── FASE 4 — fundação do takeover humano ─────────────────────────────────────
-- Story: crm-sdr-fase4
-- Versao: 1.0 | 2026-07-14 | Opus 4.8 | aditivo/idempotente
--
-- agente_pausado: quando true, o F2 pula a IA (humano assumiu a conversa) e a
-- edge function evolution-proxy seta isso ao enviar uma mensagem manual (send).
-- ─────────────────────────────────────────────────────────────────────────────

alter table leads add column if not exists agente_pausado boolean not null default false;

comment on column leads.agente_pausado is
  'Takeover: true = humano assumiu a conversa, o agente SDR (Carol) para de responder este lead.';
