-- ── ARVEX CRM — RLS v2: fecha o buraco de segurança (Fase 1 / F0) ───────────
-- Story:   crm-rls-hardening-v1
-- Versão:  1.0 | 2026-07-05 | @architect (Aria) + @dev
-- Rodar:   Supabase SQL Editor — aditivo, idempotente (drop policy if exists antes de recriar)
--
-- O QUE ISSO CORRIGE:
--   1. profiles: update permitia auto-promoção de role (auth.uid()=id sem checar
--      o valor de `role`) — qualquer usuário virava admin sozinho.
--   2. clientes_cs / cs_checks: insert/update/delete abertos a QUALQUER autenticado
--      (using(true)) — SDR conseguia apagar dados de CS da Cindy.
--   3. leads: delete aberto a qualquer autenticado — risco de perda de dados.
--   4. agente_sdr: insert/update/delete abertos — qualquer autenticado ligava/desligava
--      o agente de IA ou reescrevia o prompt dele.
--
-- O QUE NÃO MUDA (escopo deliberado, ver REFACTOR-PLAN.md):
--   - SELECT segue amplo (using(true)) nas 4 tabelas — dashboards/rollups cross-role
--     dependem disso hoje; apertar leitura é item separado, não crítico.
--   - JS do index.html (listas de e-mail hardcoded) NÃO é tocado aqui — é mudança
--     de UI com risco de quebrar o login; fica para uma sessão dedicada e testada.
--   - n8n vai falar com o banco via service_role key, que ignora RLS por natureza;
--     este fix protege contra abuso via anon key por qualquer usuário logado.
-- ─────────────────────────────────────────────────────────────────────────────

-- 1. HELPERS — mesmo padrão de is_financeiro_user() já usado no Financeiro
create or replace function is_admin()
returns boolean language sql security definer stable as $$
  select exists (select 1 from profiles where id = auth.uid() and role = 'admin')
$$;

create or replace function is_cs_or_admin()
returns boolean language sql security definer stable as $$
  select exists (select 1 from profiles where id = auth.uid() and role in ('cs', 'admin'))
$$;

grant execute on function is_admin() to authenticated;
grant execute on function is_cs_or_admin() to authenticated;

comment on function is_admin() is 'Usuário autenticado tem role=admin em profiles.';
comment on function is_cs_or_admin() is 'Usuário autenticado tem role=cs ou role=admin em profiles.';

-- 2. FIX CRÍTICO — profiles: impedir auto-promoção de role
drop policy if exists "profiles_update" on profiles;
create policy "profiles_update" on profiles for update to authenticated
  using (auth.uid() = id)
  with check (
    auth.uid() = id
    and (role = (select p.role from profiles p where p.id = auth.uid()) or is_admin())
  );

-- 3. clientes_cs / cs_checks — mutação só CS ou admin (select segue amplo)
drop policy if exists "cs_insert" on clientes_cs;
drop policy if exists "cs_update" on clientes_cs;
drop policy if exists "cs_delete" on clientes_cs;
create policy "cs_insert" on clientes_cs for insert to authenticated with check (is_cs_or_admin());
create policy "cs_update" on clientes_cs for update to authenticated using (is_cs_or_admin());
create policy "cs_delete" on clientes_cs for delete to authenticated using (is_admin());

drop policy if exists "checks_insert" on cs_checks;
drop policy if exists "checks_update" on cs_checks;
drop policy if exists "checks_delete" on cs_checks;
create policy "checks_insert" on cs_checks for insert to authenticated with check (is_cs_or_admin());
create policy "checks_update" on cs_checks for update to authenticated using (is_cs_or_admin());
create policy "checks_delete" on cs_checks for delete to authenticated using (is_admin());

-- 4. leads — delete só admin (insert/update seguem amplos: sdr/cs registram e movem leads)
drop policy if exists "leads_delete" on leads;
create policy "leads_delete" on leads for delete to authenticated using (is_admin());

-- 5. agente_sdr — painel de controle do agente de IA: mutação só admin
--    (n8n usa service_role e ignora isto; protege contra qualquer usuário logado
--    ligar/desligar o agente ou reescrever prompt via anon key)
drop policy if exists "agente_sdr_insert" on agente_sdr;
drop policy if exists "agente_sdr_update" on agente_sdr;
drop policy if exists "agente_sdr_delete" on agente_sdr;
create policy "agente_sdr_insert" on agente_sdr for insert to authenticated with check (is_admin());
create policy "agente_sdr_update" on agente_sdr for update to authenticated using (is_admin());
create policy "agente_sdr_delete" on agente_sdr for delete to authenticated using (is_admin());

-- ─────────────────────────────────────────────────────────────────────────────
-- VALIDAÇÃO (rodar depois, no SQL Editor):
--
--   -- 1. Confirmar policies ativas:
--   select tablename, policyname, cmd from pg_policies
--   where tablename in ('profiles','clientes_cs','cs_checks','leads','agente_sdr')
--   order by tablename, cmd;
--
--   -- 2. Teste funcional (logado como Sabrina/cs no app):
--   --    - Kanban CS: mover card, registrar check → deve funcionar normal.
--   --    - Tentar (via console do navegador) deletar um lead → deve falhar.
--   --    - Tentar mudar o próprio role → deve falhar.
--
-- FIM — ARVEX CRM RLS v2 (F0)
-- ─────────────────────────────────────────────────────────────────────────────
