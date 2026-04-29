-- ── ARVEX CRM — Setup Supabase ──────────────────────────────────────────

-- 1. Tabela de perfis (roles)
create table if not exists profiles (
  id   uuid references auth.users on delete cascade primary key,
  name text,
  role text not null default 'sdr' -- 'admin' | 'sdr' | 'closer'
);

-- 2. Tabela de leads
create table if not exists leads (
  id             uuid default gen_random_uuid() primary key,
  nome           text not null,
  tel            text,
  expert         text,
  origem         text,
  resp           text,
  closer         text,
  ticket         numeric,
  status         text default 'novo',
  socio          text,
  obs            text,
  data_call      text,
  proximo_passo  text,
  motivo_perda   text,
  activities     jsonb default '[]',
  created_at     timestamptz default now()
);

-- 3. Habilitar RLS
alter table profiles enable row level security;
alter table leads    enable row level security;

-- 4. Políticas de profiles
create policy "profiles_select" on profiles for select to authenticated using (true);
create policy "profiles_insert" on profiles for insert to authenticated with check (auth.uid() = id);
create policy "profiles_update" on profiles for update to authenticated using (auth.uid() = id);

-- 5. Políticas de leads (todos autenticados podem ler e escrever)
create policy "leads_select" on leads for select to authenticated using (true);
create policy "leads_insert" on leads for insert to authenticated with check (true);
create policy "leads_update" on leads for update to authenticated using (true);
create policy "leads_delete" on leads for delete to authenticated using (true);

-- 6. Criar perfil automaticamente quando usuário é criado
create or replace function handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into profiles (id, name, role)
  values (new.id, new.raw_user_meta_data->>'name', coalesce(new.raw_user_meta_data->>'role', 'sdr'));
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure handle_new_user();
