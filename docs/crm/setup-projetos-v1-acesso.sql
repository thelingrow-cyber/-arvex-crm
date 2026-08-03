-- Acesso ao módulo Projetos: flag própria em profiles (mesmo padrão de profiles.financeiro,
-- que substituiu a lista de e-mail hardcoded). "admin" não basta: há 3 admins no CRM e as
-- frentes pessoais/estratégicas do Vitor não devem aparecer para os outros.
alter table profiles add column if not exists projetos boolean not null default false;

update profiles set projetos = true
 where id in (select id from auth.users where email = 'viktorsimoess@gmail.com');

create or replace function tem_projetos() returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((select p.projetos from profiles p where p.id = auth.uid()), false)
$$;

drop policy if exists projetos_frentes_admin on projetos_frentes;
create policy projetos_frentes_acesso on projetos_frentes for all to authenticated
  using (tem_projetos()) with check (tem_projetos());

drop policy if exists projetos_tarefas_admin on projetos_tarefas;
create policy projetos_tarefas_acesso on projetos_tarefas for all to authenticated
  using (tem_projetos()) with check (tem_projetos());
