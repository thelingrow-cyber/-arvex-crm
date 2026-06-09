-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║              CRM ARVEX — Import em massa de clientes CS (Cindy)            ║
-- ╠═══════════════════════════════════════════════════════════════════════════╣
-- ║ Data:  2026-06-08                                                         ║
-- ║ Fonte: planilha enviada pelo Vitor (35 clientes da mentoria da Cindy)     ║
-- ║                                                                           ║
-- ║ O QUE FAZ:                                                                ║
-- ║   1. Carrega os 35 clientes numa staging temporária.                      ║
-- ║   2. Para cada um, TENTA achar um lead existente pelo telefone            ║
-- ║      (match pelos últimos 8 dígitos). Se achar → vincula (lead_id).       ║
-- ║      Se não achar → cria card novo sem vínculo (lead_id NULL).            ║
-- ║   3. Insere em clientes_cs com stage, datas, faturamento, bônus e obs.    ║
-- ║                                                                           ║
-- ║ SEGURANÇA:                                                                ║
-- ║   • Idempotente: não duplica quem já existir com o mesmo nome.            ║
-- ║   • Roda dentro de transação (BEGIN/COMMIT).                              ║
-- ║   • NÃO cria checks (após v3 os checks só nascem ao entrar em Campanha).  ║
-- ║                                                                           ║
-- ║ COMO APLICAR:                                                             ║
-- ║   1. Supabase Dashboard → SQL Editor → colar tudo → Run                   ║
-- ║   2. Esperado: a query final mostra a contagem por coluna do kanban.      ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

begin;

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Staging temporária com os dados crus já normalizados
-- ─────────────────────────────────────────────────────────────────────────────
create temp table _imp_cs (
  nome            text,
  tel             text,
  stage           text,
  dt_inicio       date,
  reuniao_cindy   date,
  fat             numeric,
  resultado       text,
  bonus           jsonb,
  churn           text,
  num_lojas       integer,
  campanha_rodou  boolean,
  obs             text
) on commit drop;

insert into _imp_cs
  (nome, tel, stage, dt_inicio, reuniao_cindy, fat, resultado, bonus, churn, num_lojas, campanha_rodou, obs)
values
  ('KAREN KARDENE',                  '98 8432-0988', 'risco_churn', '2026-01-05', null,         null,     null,                                '[]',                                   'vermelho', null, false, '⚠️ Loja foi assaltada (sem fase). Venc.: 05/06/2026.'),
  ('ANGELICA SILVA',                 '19 99187-4661','gate_cindy',  '2026-01-08', '2026-02-23', null,     'Orgânica — sem resultados',         '[]',                                   'ok',       null, true,  'Venc.: 08/06/2026.'),
  ('GLEICE CASTELO',                 '51 99828-4488','campanha',    '2026-01-10', null,         null,     'Em orgânica (mais 2 meses)',        '[]',                                   'ok',       null, true,  'Ainda na orgânica (mais 2 meses). Venc.: 10/06/2026.'),
  ('ELLEN CRISTINA BARBOSA',         '83 99913-5650','gate_cindy',  '2026-01-14', '2026-02-23', 2279.90,  'Orgânica — R$ 2.279,90',            '[]',                                   'ok',       null, true,  'Venc.: 14/06/2026.'),
  ('INES ISABEL CADORE',             '66 98416-5219','risco_churn', '2026-01-14', null,         null,     null,                                '["30 dias de Gestor"]',                'vermelho', null, false, 'Mentoria pausada.'),
  ('JOAO LUCAS DA SILVA MANGUEIRA',  '71 8148-3766', 'gate_cindy',  '2026-01-14', '2026-03-04', 3420.00,  'Orgânica — R$ 3.420,00',            '[]',                                   'ok',       null, true,  null),
  ('ROSINEIA COELHO BARROSO',        '96 99106-0523','trafego',     '2026-01-14', '2026-03-30', null,     'Orgânica — sem resultados',         '["30 dias de Gestor"]',                'ok',       null, true,  'Preparando os anúncios para subir (tráfego). Venc.: mentoria prolongada (PROLO).'),
  ('ROSEANE DOS PASSOS MANDADORE',   '48 99112-4048','gate_cindy',  '2026-01-14', '2026-02-17', 10882.25, 'Orgânica — R$ 10.882,25',           '[]',                                   'ok',       null, true,  'Segunda reunião com a Cindy em 12/03/2026. Venc.: 14/06/2026.'),
  ('ANDERSON ROBERTO PEREIRA',       '19 98876-2012','gate_cindy',  '2026-01-15', '2026-02-23', 14655.00, 'Orgânica — R$ 14.655,00 (3 lojas)', '[]',                                   'ok',       3,    true,  '3 lojas. Venc.: 15/06/2026.'),
  ('ROSIMEIRE RIBEIRO DE VILLAS BOAS','19 99758-8585','trafego',    '2026-01-19', '2026-02-24', null,     'Orgânica — sem resultados',         '[]',                                   'ok',       null, true,  'Tráfego com o Kadu, mas sem muitos leads. Venc.: 19/06/2026.'),
  ('JACILDA CARVALHO',               '89 99429-1009','gate_cindy',  '2026-01-21', '2026-03-05', 8065.00,  'Orgânica — R$ 8.065,00',            '["Gestor (somente em fevereiro)"]',    'ok',       null, true,  'Venc.: 21/06/2026.'),
  ('THAIS FLORENCIO',                '35 9887-2779', 'gate_cindy',  '2026-01-21', '2026-03-31', 6205.00,  'Orgânica — R$ 6.205,00',            '[]',                                   'ok',       null, true,  'Venc.: mentoria prolongada (PROLO).'),
  ('CRISTIANE ABDIAS',               '84 99998-6353','gate_cindy',  '2026-01-26', '2026-03-25', null,     'Orgânica — somente 1 venda',        '[]',                                   'ok',       null, true,  'Segunda reunião com a Cindy em 05/05/2026. Venc.: mentoria prolongada (PROLO).'),
  ('MARIA DANTAS',                   '83 98780-9747','gate_cindy',  '2026-01-29', '2026-02-16', 1500.00,  'Orgânica — R$ 1.500,00',            '[]',                                   'ok',       null, true,  'Venc.: 29/06/2026.'),
  ('JULIA CASSIANO',                 '83 99319-0229','gate_cindy',  '2026-01-29', '2026-03-27', 8240.00,  'Orgânica — R$ 8.240,00',            '[]',                                   'ok',       null, true,  'Venc.: 29/06/2026.'),
  ('KELLY NEUBAUER',                 '41 99703-7884','gate_cindy',  '2026-01-30', '2026-03-17', 6000.00,  'Orgânica — R$ 6.000,00',            '[]',                                   'ok',       null, true,  'Venc.: 30/06/2026.'),
  ('LARISSA LEAO',                   '8098882-6655', 'gate_cindy',  '2026-01-30', '2026-03-03', 12000.00, 'Orgânica — R$ 12.000,00',           '[]',                                   'ok',       null, true,  'Venc.: 30/06/2026.'),
  ('ANDREA TAVARES',                 '98 98626-8712','gate_cindy',  '2026-01-30', '2026-03-12', null,     'Orgânica — sem resultados',         '[]',                                   'ok',       null, true,  'Venc.: 30/06/2026.'),
  ('LARISSA CAMPIOTTO',              '19 99526-0503','gate_cindy',  '2026-01-31', '2026-02-24', null,     'Passou direto para o digital com a Cindy', '[]',                            'ok',       null, false, 'Ótica nova — não fez orgânica, passou direto pro digital com a Cindy. Venc.: 30/06/2026 (planilha: 31/06).'),
  ('EGIANE PRIMIANO',                '16 99708-3815','risco_churn', '2026-02-02', null,         null,     null,                                '[]',                                   'vermelho', null, false, 'Pediu pra pausar — mentoria pausada.'),
  ('ANA FLORA NUNES',                '331 98787-8001','gate_cindy', '2026-02-03', '2026-04-28', null,     'Não fez orgânica — passou direto pra Cindy', '[]',                          'ok',       null, false, 'Não fez orgânica — passou direto pra Cindy. Venc.: 03/07/2026.'),
  ('NEURIANE',                       '86 99567-0373','gate_cindy',  '2026-02-03', '2026-02-20', 3769.00,  'Orgânica — R$ 3.769,00',            '[]',                                   'ok',       null, true,  'Venc.: 03/06/2026.'),
  ('ADRIANA ANDREA',                 '34 99981-9961','trafego',     '2026-02-04', '2026-03-03', null,     'Orgânica — sem resultados',         '[]',                                   'ok',       null, true,  'No patrocinado com o Bil. Venc.: 04/06/2026.'),
  ('DESIREE',                        '85 8706-6497', 'gate_cindy',  '2026-02-13', '2026-03-24', null,     'Orgânica — sem resultados',         '[]',                                   'ok',       null, true,  'Venc.: 13/06/2026.'),
  ('SANDRO DE JESUS',                '47 9636-8209', 'trafego',     '2026-02-19', '2026-03-25', 1099.90,  'Orgânica — R$ 1.099,90',            '[]',                                   'ok',       null, true,  'No tráfego com o Bil. Venc.: 19/06/2026.'),
  ('CAMILA MOURA (ÓTICA DO ZERO)',   '92 98401-1082','gate_cindy',  '2026-02-27', '2026-03-06', null,     'Ótica do zero — direto com a Cindy','[]',                                   'ok',       null, false, 'Ótica do zero — direto com a Cindy. Só deu start em 02/03. Venc.: 02/07/2026.'),
  ('EVERTON E ADRIANO',              '11 97159-9715','gate_cindy',  '2026-02-27', '2026-03-25', 3261.97,  'Orgânica — R$ 3.261,97',            '[]',                                   'ok',       null, true,  'Venc.: 27/06/2026.'),
  ('ROSEANE E NORMA',                '85 98926-2082','trafego',     '2026-03-05', '2026-03-24', 3600.00,  'Orgânica — R$ 3.600,00',            '[]',                                   'ok',       null, true,  'Com o Bil no tráfego. Venc.: 05/07/2026.'),
  ('GIOVANA COSTA',                  '19 99751-8728','gate_cindy',  '2026-03-24', '2026-05-08', 2843.00,  'Orgânica — R$ 2.843,00',            '["30 dias de Gestor"]',                'ok',       null, true,  'Venc.: 24/07/2026.'),
  ('RODOF E CLAYTON',                '92 98403-0998','gate_cindy',  '2026-03-27', null,         null,     'Orgânica — sem resultados',         '["30 dias de Gestor"]',                'ok',       null, true,  'Reunião com a Cindy feita (data não informada). Venc.: 27/07/2026.'),
  ('LUIZ GUSTAVO',                   null,           'onboarding',  null,         null,         null,     null,                                '[]',                                   'ok',       null, false, null),
  ('RAISSA E LEONARDO',              null,           'onboarding',  null,         null,         null,     null,                                '["30 dias de Gestor"]',                'ok',       null, false, null),
  ('GIOVANE',                        null,           'onboarding',  null,         null,         null,     null,                                '["30 dias de Gestor"]',                'ok',       null, false, null),
  ('DANIELA HERNING',                '42 98431-5106','onboarding',  '2026-04-07', null,         null,     null,                                '[]',                                   'ok',       null, false, null),
  ('NICOLE',                         '19 98893-0821','onboarding',  '2026-04-07', null,         null,     null,                                '[]',                                   'ok',       null, false, null);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Insere em clientes_cs com match automático de lead pelo telefone
--    (últimos 8 dígitos). Idempotente: pula quem já existe pelo nome.
-- ─────────────────────────────────────────────────────────────────────────────
insert into clientes_cs (
  lead_id, nome, tel, expert, resp_cs, cs_stage,
  data_fechamento, data_reuniao_cindy,
  faturamento_campanha, resultado_campanha, campanha_rodou,
  entregaveis_bonus, churn_flag, diag_num_lojas, obs, posicao
)
select
  (
    select l.id
    from leads l
    where l.tel is not null
      and length(regexp_replace(s.tel, '\D', '', 'g')) >= 8
      and right(regexp_replace(l.tel, '\D', '', 'g'), 8)
        = right(regexp_replace(s.tel, '\D', '', 'g'), 8)
    limit 1
  )                                                            as lead_id,
  s.nome,
  s.tel,
  'cindy',
  'Sabrina',
  s.stage,
  s.dt_inicio,
  s.reuniao_cindy,
  s.fat,
  s.resultado,
  s.campanha_rodou,
  coalesce(s.bonus, '[]'::jsonb),
  coalesce(s.churn, 'ok'),
  s.num_lojas,
  s.obs,
  row_number() over (partition by s.stage order by s.dt_inicio nulls last, s.nome) * 1000.0
from _imp_cs s
where not exists (
  select 1 from clientes_cs c where c.nome = s.nome
);

commit;

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. VALIDAÇÃO — contagem por coluna do kanban (rode pra conferir)
-- ─────────────────────────────────────────────────────────────────────────────
select cs_stage, count(*) as qtd
from clientes_cs
where resp_cs = 'Sabrina'
group by cs_stage
order by cs_stage;

-- Quantos foram vinculados a um lead existente vs criados do zero:
--   select count(*) filter (where lead_id is not null) as vinculados,
--          count(*) filter (where lead_id is null)     as novos
--   from clientes_cs where expert = 'cindy';

-- FIM — import-cs-clientes-2026-06-08.sql
