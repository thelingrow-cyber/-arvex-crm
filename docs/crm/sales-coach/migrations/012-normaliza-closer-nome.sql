-- ============================================================================
-- Normaliza `meetings.closer_nome`.
--
-- PROBLEMA: reuniões criadas por caminhos diferentes gravaram coisas diferentes
-- no mesmo campo — umas com o nome ("Vitor"), outras com o e-mail
-- ("viktorsimoess@gmail.com"). O mesmo closer aparecia como duas pessoas em
-- qualquer relatório agrupado por nome.
--
-- Não quebra nada hoje (o histórico do closer usa closer_id), mas polui leitura
-- e quebraria a aba Direção quando ela existir.
--
-- Fonte da verdade: profiles.display_name → profiles.name → e-mail.
-- ============================================================================

update meetings m
   set closer_nome = coalesce(nullif(p.display_name, ''), nullif(p.name, ''), u.email),
       updated_at  = now()
  from profiles p
  join auth.users u on u.id = p.id
 where p.id = m.closer_id
   and m.closer_nome is distinct from coalesce(nullif(p.display_name, ''), nullif(p.name, ''), u.email);
