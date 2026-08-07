-- ============================================================================
-- DESFECHO REAL — fecha o loop de aprendizado do coach.
--
-- Hoje o coach analisa a call, dá nota e missão... e NUNCA descobre se acertou.
-- Sem saber o que aconteceu depois, ele acumula opinião, não aprendizado.
--
-- O que já existia: trigger `vendas_marca_meeting_ganhou` (marca resultado e
-- copia o ticket quando uma venda é registrada para o lead). Bom, mas não grava
-- QUANDO — e sem data não há ciclo de fechamento — nem cobre o caso da perda.
--
-- Esta migration acrescenta:
--   · desfecho_em      → quando fechou/perdeu (permite medir dias até a decisão)
--   · motivo_perda     → por que não fechou (alimenta o cérebro com padrão real)
--   · desfecho_origem  → 'auto' (trigger) ou 'manual' (closer marcou)
--   · trigger atualizada para carimbar data e origem
-- ============================================================================

alter table meetings add column if not exists desfecho_em     date;
alter table meetings add column if not exists motivo_perda    text;
alter table meetings add column if not exists desfecho_origem text;

comment on column meetings.desfecho_em is
  'Data em que a venda foi ganha ou perdida. Diferença para data_reuniao = ciclo de fechamento.';
comment on column meetings.motivo_perda is
  'Por que não fechou: preco | decisor | timing | concorrente | sumiu | outro. Alimenta o cérebro.';
comment on column meetings.desfecho_origem is
  'auto = trigger de venda · manual = closer marcou na UI';

create index if not exists meetings_desfecho_idx on meetings (resultado, desfecho_em);

-- Trigger: além de marcar ganhou e copiar o ticket, carimba quando e de onde veio.
create or replace function public.meetings_marcar_ganhou_ao_vender()
 returns trigger
 language plpgsql
 security definer
 set search_path to 'public'
as $function$
begin
  update meetings
     set resultado       = 'ganhou',
         ticket          = new.valor_total,
         desfecho_em     = coalesce(new.created_at::date, current_date),
         desfecho_origem = 'auto',
         motivo_perda    = null,
         updated_at      = now()
   where lead_id = new.lead_id
     and resultado = 'aberto';
  return new;
end;
$function$;

-- Backfill conservador: reuniões que JÁ estavam marcadas como ganhou/perdeu antes
-- deste campo existir ficam com a data da própria reunião como referência, e a
-- origem marcada como 'retroativo' para não contaminar a métrica de ciclo.
update meetings
   set desfecho_em = data_reuniao, desfecho_origem = 'retroativo'
 where resultado in ('ganhou','perdeu') and desfecho_em is null;
