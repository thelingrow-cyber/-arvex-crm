-- ============================================================================
-- Restaura a curadoria do cérebro depois de um ALARME FALSO na interface.
--
-- CAUSA: ao subir o teto de 24.000 → 28.000, as duas edge functions foram
-- atualizadas mas o KB_LIMITE da tela ficou em 24.000. O medidor mostrou
-- vermelho sem motivo, e a curadoria manual reagiu ao alarme:
--   · DESATIVOU  "Quem tira o medo do 'é tudo online' é a autoridade" (bom bloco)
--   · REATIVOU   "Quem é o dono de ótica (perfil real...)" = ICP v1, SUPERADO
--     pelo v2 — deixando os dois ICPs no prompt, dizendo a mesma coisa duas vezes.
--
-- Esta migration devolve o estado curado (27.692 chars). A causa raiz — o número
-- na tela — foi corrigida no index.html no mesmo commit.
-- ============================================================================

-- ICP v1 sai: superado pelo v2 (3 calls + 15 lives), que já está ativo.
update sales_knowledge set ativo = false, updated_at = now()
 where titulo = 'Quem é o dono de ótica (perfil real, extraído de calls)';

-- Autoridade/prova social volta: nenhum outro bloco cobre "o lead vai atrás da
-- autoridade por conta própria antes de fechar".
update sales_knowledge set ativo = true, updated_at = now()
 where titulo = 'Quem tira o medo do "é tudo online" é a autoridade, não o closer';
