-- ============================================================================
-- Meet Transcriber — hardening v2 (fix do v1)
-- Corrige o índice único parcial do v1, que não funcionava com o upsert
-- (ON CONFLICT) usado pelo supabase-js — erro real visto em produção:
-- "there is no unique or exclusion constraint matching the ON CONFLICT specification"
-- Postgres já permite múltiplos NULL numa unique constraint normal — não
-- precisava do índice parcial (where client_key is not null).
-- Aplicado e verificado em produção em 2026-07-06 (curl E2E: 2 envios com a
-- mesma client_key retornaram o MESMO meeting_id, sem duplicar).
-- ============================================================================

drop index if exists meetings_client_key_uidx;
alter table meetings add constraint meetings_client_key_key unique (client_key);
