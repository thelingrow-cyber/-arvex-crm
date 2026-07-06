-- ============================================================================
-- Meet Transcriber — hardening v1 (S2/S5 do plano "redondo")
-- Fonte: docs/plugin-meet-transcriber/DEEP-ANALYSIS-FABLE.md (ADR-4, ADR-7)
-- Aditivo, não quebra ingestão manual existente (colunas nullable).
-- Aplicar manualmente no SQL Editor do Supabase (mesmo padrão dos outros setup-*.sql).
-- ============================================================================

-- client_key: idempotency key do lado cliente (Meet Transcriber). meetingId+data.
-- Permite upsert por ON CONFLICT em vez de sempre INSERT — duplo-clique e retry
-- deixam de criar reunião duplicada no banco (ADR-4).
alter table meetings add column if not exists client_key text;

-- notas: anotações do closer feitas durante a call (aba "Notas" do plugin),
-- enviadas junto com a transcrição no mesmo payload (ADR-7).
alter table meetings add column if not exists notas text;

comment on column meetings.client_key is 'Idempotency key do lado cliente (Meet Transcriber): meetingId+data. Upsert evita duplicata em duplo-clique/retry.';
comment on column meetings.notas is 'Notas do closer feitas durante a call (aba Notas do plugin) — enviadas junto com a transcrição.';

-- unique parcial (permite múltiplos NULL — reuniões criadas por outros fluxos que não mandam client_key)
create unique index if not exists meetings_client_key_uidx on meetings (client_key) where client_key is not null;
