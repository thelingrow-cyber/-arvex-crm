-- ── ARVEX CRM — Tabela de Perfis e Roles ─────────────────────────────────
-- Rodar no Supabase SQL Editor
-- Versão: 1.0 | 2026-04-30

-- 1. Tabela profiles (vinculada ao auth.users)
create table if not exists profiles (
  id    uuid primary key references auth.users(id) on delete cascade,
  name  text,
  role  text default 'sdr'
  -- roles: admin | cs | sdr
);

-- 2. RLS
alter table profiles enable row level security;

-- Usuário lê/atualiza só o próprio perfil
create policy "profiles_self" on profiles
  for all to authenticated
  using (id = auth.uid())
  with check (id = auth.uid());

-- 3. Trigger — cria perfil automático ao cadastrar usuário no Auth
create or replace function handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into profiles (id, name, role)
  values (new.id, new.email, 'sdr')
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure handle_new_user();

-- FIM
