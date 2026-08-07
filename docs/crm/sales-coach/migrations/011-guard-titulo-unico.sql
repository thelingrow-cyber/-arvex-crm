-- ============================================================================
-- Guard das migrations do cérebro.
--
-- PROBLEMA que isto resolve: as migrations 002-010 são `insert ... on conflict
-- do nothing`, mas NÃO havia constraint alguma para dar conflito. Reaplicar
-- qualquer uma delas duplicava blocos no cérebro silenciosamente — e bloco
-- duplicado consome o teto de 28k duas vezes.
--
-- A partir daqui: título é único. Reaplicar migration vira no-op de verdade,
-- e migrations novas devem usar `on conflict (titulo) do nothing`.
-- ============================================================================

-- Se existirem duplicatas de título (de alguma reaplicação anterior), mantém a
-- mais recente e desativa as demais antes de criar o índice.
update sales_knowledge s set ativo = false, updated_at = now()
 where exists (
   select 1 from sales_knowledge o
    where o.titulo = s.titulo and o.id <> s.id
      and (o.created_at, o.id) > (s.created_at, s.id)
 );

delete from sales_knowledge s
 where not ativo
   and exists (
     select 1 from sales_knowledge o
      where o.titulo = s.titulo and o.id <> s.id
        and (o.created_at, o.id) > (s.created_at, s.id)
   );

create unique index if not exists sales_knowledge_titulo_uk on sales_knowledge (titulo);
