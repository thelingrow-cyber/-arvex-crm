-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║             CRM ARVEX — setup-sdr-webhook-v1.sql                          ║
-- ╠═══════════════════════════════════════════════════════════════════════════╣
-- ║ Config da edge function `sdr-webhook` — a entrada única das mensagens do  ║
-- ║ WhatsApp no CRM (revisão de 2026-09-15).                                  ║
-- ║                                                                           ║
-- ║ Aditivo e idempotente. Nada destrutivo, nada renomeado.                   ║
-- ║ Pode rodar por conexão direta ou no SQL Editor — não pede segredo nenhum. ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝
--
-- POR QUE ASSIM:
--
-- 1. A janela de silêncio e o debounce vivem no BANCO, não no código. Ajustar o
--    comportamento da Carol de madrugada não pode exigir redeploy.
--
-- 2. O anti-duplicação já existe e não é recriado aqui: o índice único parcial
--    `agente_sdr_historico_wa_id_uidx` (wa_id) já está em produção. É ele que
--    faz o eco das nossas próprias mensagens ser reconhecido em vez de virar
--    "humano assumiu a conversa".
--
-- 3. O agente continua nascendo DESLIGADO. Este arquivo não liga nada.

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. JANELA DE HORÁRIO E DEBOUNCE
--    · não responder antes/depois: o lead escreve 03h da manhã e a Carol
--      responder na hora entrega que é robô, além de ser inconveniente.
--    · debounce: o lead manda três mensagens picadas em dez segundos. Sem
--      espera, saem três respostas. A function espera este tanto e só responde
--      se nenhuma mensagem nova chegou — mesma regra do f2-debounce do n8n.
-- ─────────────────────────────────────────────────────────────────────────────
alter table agente_sdr
  add column if not exists nao_responder_antes  int not null default 8,
  add column if not exists nao_responder_depois int not null default 21,
  add column if not exists debounce_seg         int not null default 12;

comment on column agente_sdr.nao_responder_antes is
  'Hora local (Brasília) antes da qual o agente não responde. Fora da janela a mensagem é registrada, mas fica para o humano.';
comment on column agente_sdr.nao_responder_depois is
  'Hora local a partir da qual o agente não responde.';
comment on column agente_sdr.debounce_seg is
  'Segundos que o agente espera antes de responder, para agrupar o burst do lead. 0 desliga a espera.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. VERIFICAÇÃO E OPERAÇÃO
-- ─────────────────────────────────────────────────────────────────────────────
-- Config atual:
--   select nome, ativo, modelo, nao_responder_antes, nao_responder_depois, debounce_seg
--     from agente_sdr;
--
-- LIGAR a Carol (só depois do teste no próprio número):
--   update agente_sdr set ativo = true, updated_at = now();
--
-- DESLIGAR na hora (a function volta a só registrar e fazer handoff):
--   update agente_sdr set ativo = false, updated_at = now();
--
-- Leads em que o agente está fora (humano assumiu):
--   select nome, tel, atendente, agente_pausado from leads where agente_pausado;
--
-- Devolver um lead ao agente (desfaz o handoff — ato consciente):
--   update leads set agente_pausado = false where tel = '55...';
--
-- O que a Carol respondeu de fato:
--   select session_id, message->>'content' texto,
--          message->'additional_kwargs'->>'operator' quem
--     from agente_sdr_historico
--    where message->'additional_kwargs'->>'operator' = 'Carol'
--    order by id desc limit 30;
-- FIM
