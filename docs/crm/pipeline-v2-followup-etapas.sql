-- =====================================================================
-- Pipeline v2 — o follow-up vira contagem, e quem sumiu deixa de ser "perdido"
-- Autor: Orion (aiox-master) · 2026-08-24 · tarefa CD-11
--
-- POR QUE: `followup` era um balde único com 53 leads, 50 deles parados há
-- mais de 7 dias, sem ninguém saber se era o 1º toque ou o 5º. E `perdido`
-- tinha 202 leads dos quais só 27 (13%) tinham decisão real — os outros 146
-- simplesmente pararam de responder. Silêncio não é recusa.
--
-- `leads.status` é texto livre (não há CHECK constraint), então os valores
-- novos entram sem alteração de schema. A reversão é um UPDATE.
-- =====================================================================

begin;

-- ---------------------------------------------------------------------
-- 1. `qualificado` morre. A etapa nunca foi usada: 7 leads, 6 nunca
--    tocados, o mais velho parado há 53 dias. O lead ia de contato
--    direto para call — a coluna só acumulava.
-- ---------------------------------------------------------------------
update leads set status = 'contato' where status = 'qualificado';

-- ---------------------------------------------------------------------
-- 2. O follow-up vira três etapas. Todos os 53 entram em fup1: hoje
--    ninguém sabe em que toque cada um está, então a contagem começa
--    limpa em vez de começar errada.
-- ---------------------------------------------------------------------
update leads set status = 'fup1' where status = 'followup';

-- ---------------------------------------------------------------------
-- 3. Quem fez call e sumiu não é perdido — é "volta depois".
--    Critério (definição do Vitor): passou pela call, passou pelo
--    follow-up e não deu retorno. Some-se a quem foi marcado como
--    perdido com motivo de silêncio explícito.
--    Fica FORA: quem disse não de verdade (sem budget, concorrente,
--    não era o perfil) e o lixo de importação (duplicado, número errado).
-- ---------------------------------------------------------------------
update leads
   set status = 'volta_depois'
 where status = 'perdido'
   and (
     (data_call is not null
      and coalesce(nullif(trim(motivo_perda), ''), 'Não informado')
          in ('Não informado', 'Não atendeu', 'NÃO RESPONDE', '.'))
     or trim(motivo_perda) in ('Não atendeu', 'NÃO RESPONDE')
   );

commit;

-- =====================================================================
-- O MAPA NOVO
-- =====================================================================
--   SDR      novo → contato (Conversando) → call (Agendado)
--   CLOSER   quente (Call feita) → fup1 → fup2 → fup3
--   SAÍDAS   fechado · volta_depois · perdido
--
-- `quente` e `call` mantêm o id no banco e mudam só de rótulo na tela:
-- renomear o id quebraria histórico, RLS e o agente. O rótulo é o que
-- o time lê — e é ele que precisava dizer um fato ("Call feita",
-- "Agendado") em vez de uma expectativa ("Quente").
--
-- REGRAS que a tela passa a cobrar (TRANSICOES no index.html):
--   fup1/fup2/fup3 → exigem próximo passo escrito
--   volta_depois   → exige data de reativação
--   perdido        → exige motivo (só decisão real chega aqui agora)
-- =====================================================================

-- =====================================================================
-- ROLLBACK
-- =====================================================================
-- begin;
--   update leads set status='followup' where status in ('fup1','fup2','fup3');
--   update leads set status='perdido'  where status = 'volta_depois';
--   -- `qualificado` NÃO volta: os 7 leads não têm como ser distinguidos
--   -- dos demais em `contato` depois da migração. A etapa estava morta.
-- commit;

-- =====================================================================
-- PARTE 2 — a data de retomada (2026-08-25)
--
-- `volta_depois` sem data é o mesmo balde de antes com outro nome: alguém
-- promete voltar e ninguém volta. A tela passou a exigir a data na entrada
-- da coluna, então o banco precisa ter onde guardá-la.
-- Aditivo e reversível: nenhuma linha existente é tocada.
-- =====================================================================

alter table leads add column if not exists reabordar_em date;

comment on column leads.reabordar_em is
  'Data marcada para reabordar um lead em volta_depois (Abordar no futuro). Preenchida pela transição no CRM.';

-- Os 34 leads que já estavam em volta_depois entraram pela migração da Parte 1,
-- antes da coluna existir — ficam sem data até alguém decidir a deles.
-- Não invento data: um lead com data errada some da fila do mesmo jeito.

-- ROLLBACK: alter table leads drop column if exists reabordar_em;
