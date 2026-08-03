-- Projetos v2 — acesso POR FRENTE.
-- v1 era tudo-ou-nada (profiles.projetos). O Gabriel precisa ver Cindy e Viziom
-- sem enxergar marca pessoal, oferta e vida pessoal do Vitor.
-- Regra: projetos=true é o portão; projetos_escopo diz QUAIS frentes.
--        NULL = todas (dono). Lista = só aquelas.

alter table profiles add column if not exists projetos_escopo text[];

comment on column profiles.projetos_escopo is
  'Frentes visíveis no módulo Projetos. NULL = todas. Ex: {CD,VZ}';

create or replace function pode_frente(p_frente text) returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((
    select p.projetos and (p.projetos_escopo is null or p_frente = any(p.projetos_escopo))
    from profiles p where p.id = auth.uid()
  ), false)
$$;

drop policy if exists projetos_frentes_acesso on projetos_frentes;
create policy projetos_frentes_acesso on projetos_frentes for all to authenticated
  using (pode_frente(key)) with check (pode_frente(key));

drop policy if exists projetos_tarefas_acesso on projetos_tarefas;
create policy projetos_tarefas_acesso on projetos_tarefas for all to authenticated
  using (pode_frente(frente)) with check (pode_frente(frente));
