-- ── ARVEX CRM — permissão do Financeiro sai do código e vai para o banco ────
-- Story:   CRM-UX-002 (Lote 2 / F4) · docs/stories/crm-lote2-verdade-dos-dados.story.md
-- Autor:   @data-engineer (Dara) · 2026-07-12 · validado por @po (Pax)
-- Rodar:   aditivo e idempotente (safe re-run)
--
-- POR QUE EXISTE:
--   Quem vê o módulo Financeiro estava definido por lista de e-mail HARDCODED em DOIS
--   lugares: no JS (const FINANCEIRO_USERS) e aqui no banco (is_financeiro_user() com
--   auth.email() in (...)). Trocar um responsável exigia editar código e fazer deploy.
--
-- SEGURANÇA (não quebrar):
--   8 policies dependem de is_financeiro_user() — vendas (4 cmd) e parcelas (4 cmd).
--   Mantemos NOME, ASSINATURA e SECURITY DEFINER: as policies seguem válidas sem tocar nelas.
--
-- ARMADILHA REAL (achado na aplicação):
--   arvexdigital@gmail.com (Gabriel) NÃO tinha linha em profiles. Um simples UPDATE não o
--   alcançaria e, com a coluna default false, ele PERDERIA o acesso ao Financeiro no próximo
--   login. Por isso o seed é UPSERT a partir de auth.users, criando a linha que falta.
-- ─────────────────────────────────────────────────────────────────────────────

-- 1. COLUNA (ortogonal a role: Gabriel é 'sdr' e tem financeiro; Sabrina é 'cs' e não tem)
alter table profiles add column if not exists financeiro boolean not null default false;

comment on column profiles.financeiro is
  'Acesso ao módulo Financeiro (Cobranças/Clientes). Independente de role. '
  'Gerenciável direto no banco — mudar aqui NÃO exige deploy.';

-- 2. SEED — upsert a partir de auth.users (fonte de verdade do e-mail)
--    Cria a linha se o usuário nunca logou; se já existe, só liga a flag (preserva role).
insert into profiles (id, name, role, financeiro)
select u.id, u.email, 'sdr', true
from auth.users u
where u.email in (
  'viktorsimoess@gmail.com',        -- Vitor (admin)
  'arvexdigital@gmail.com',         -- Gabriel (closer) — não tinha profile
  'vhpacheco02@gmail.com',          -- Pacheco (closer)
  'compromissiondigital@gmail.com'  -- acesso adicional
)
on conflict (id) do update set financeiro = true;   -- NÃO sobrescreve role

-- 3. FUNÇÃO — mesma assinatura, nova fonte de verdade
create or replace function is_financeiro_user()
returns boolean
language sql
stable security definer     -- precisa ler profiles independente da RLS de quem chama
set search_path = public
as $$
  select coalesce((select p.financeiro from profiles p where p.id = auth.uid()), false)
$$;

comment on function is_financeiro_user() is
  'true se profiles.financeiro do usuário logado é true. Fonte única (antes era lista de '
  'e-mail hardcoded aqui e no JS). Usada por 8 policies de vendas e parcelas.';

grant execute on function is_financeiro_user() to authenticated;

-- ─────────────────────────────────────────────────────────────────────────────
-- VERIFICAÇÃO
--   select u.email, p.role, p.financeiro
--   from auth.users u join profiles p on p.id = u.id order by p.financeiro desc, u.email;
--   -- esperado: os 4 com financeiro=true; Sabrina (cs) com false.
--
-- ROLLBACK (volta a lista hardcoded)
--   create or replace function is_financeiro_user()
--   returns boolean language sql stable security definer as $$
--     select auth.email() in ('viktorsimoess@gmail.com','arvexdigital@gmail.com',
--                             'vhpacheco02@gmail.com','compromissiondigital@gmail.com')
--   $$;
--   alter table profiles drop column if exists financeiro;
-- ─────────────────────────────────────────────────────────────────────────────
