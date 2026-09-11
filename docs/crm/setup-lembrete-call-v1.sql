-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║              CRM ARVEX — setup-lembrete-call-v1.sql                        ║
-- ╠═══════════════════════════════════════════════════════════════════════════╣
-- ║ Lembrete automático de call para o LEAD (WhatsApp via Evolution).         ║
-- ║ Pedido da Thalita (closer) · 2026-09-10 · @data-engineer (Dara)           ║
-- ║                                                                           ║
-- ║ DOIS DISPAROS por call (decisão do Vitor):                               ║
-- ║   · manhã  — 9h do dia da call, para todas as calls do dia                ║
-- ║   · 1h antes — de cada call, individualmente                              ║
-- ║                                                                           ║
-- ║ Texto FIXO com variáveis (não passa pela Carol). Carol está ativo=false   ║
-- ║ e sem número; este fluxo não depende dela.                                ║
-- ║                                                                           ║
-- ║ Natureza: aditivo e idempotente. Nada destrutivo, nada renomeado.         ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝
--
-- POR QUE ASSIM (não reverter sem ler):
--
-- 1. `leads.data_call` é TEXT e está sujo. Dos 135 registros com data, só 104
--    estão no padrão ISO do <input type="datetime-local"> ("2026-09-10T14:00").
--    O resto é legado digitado à mão ("29/06/2026", "26/05/2026 - 19:30h").
--    NÃO alteramos o tipo da coluna: o front escreve texto e mudar o tipo
--    quebraria o CRM em produção. Em vez disso, `call_em_ts()` converte só o
--    que é ISO e devolve NULL para o resto — lixo antigo nunca vira disparo.
--
-- 2. A idempotência é do BANCO, não do código. O índice único
--    (lead_id, tipo, call_em) é o que garante "nunca mando o mesmo lembrete
--    duas vezes", mesmo se o cron rodar em duplicidade. Mesma lição do
--    incidente das 76k linhas do sync: quem garante unicidade é o índice.
--
-- 3. Remarcar a call REARMA o lembrete de propósito: mudou `data_call`, muda
--    `call_em`, muda a chave única, o lead recebe o lembrete do novo horário.
--
-- 4. Nasce DESLIGADO (`ativo = false`). É mensagem automática saindo para
--    cliente no WhatsApp da operação — só liga depois que o Vitor aprovar o
--    texto e rodar um envio de teste.
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. PARSE SEGURO DE `data_call` (text → timestamptz)
--    O CRM grava horário local de Brasília sem fuso ("2026-09-10T14:00").
--    Interpretar como UTC atrasaria todo lembrete em 3 horas.
-- ─────────────────────────────────────────────────────────────────────────────
create or replace function public.call_em_ts(p_data_call text)
returns timestamptz
language sql
immutable
set search_path = public
as $$
  select case
    when p_data_call ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}'
      then (substring(p_data_call from 1 for 16))::timestamp
           at time zone 'America/Sao_Paulo'
    else null
  end
$$;

comment on function public.call_em_ts(text) is
  'Converte leads.data_call (text, horário de Brasília) em timestamptz. NULL se o texto não estiver no padrão ISO do datetime-local — protege contra o legado digitado à mão.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. CONFIGURAÇÃO (linha única) — o texto e os horários vivem no banco,
--    não no código da function. Ajustar aqui não exige redeploy.
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists lembretes_config (
  id                 int primary key default 1 check (id = 1),
  ativo              boolean     not null default false,  -- nasce desligado (ver nota 4)
  hora_manha         int         not null default 9,      -- hora local do disparo da manhã
  antecedencia_min   int         not null default 60,     -- "1h antes" = 60 min
  janela_min         int         not null default 10,     -- tolerância do cron (roda a cada 10 min)
  gap_minimo_min     int         not null default 90,     -- manhã só avisa call que ainda falta ≥ isto
  nao_enviar_antes   int         not null default 8,      -- silêncio antes das 8h
  nao_enviar_depois  int         not null default 21,     -- silêncio depois das 21h
  texto_manha        text        not null,
  texto_1h           text        not null,
  updated_at         timestamptz not null default now()
);

comment on table lembretes_config is
  'Config do lembrete de call. Linha única (id=1). Variáveis nos textos: {nome} {hora} {data} {resp}.';
comment on column lembretes_config.gap_minimo_min is
  'Se a call for daqui a menos que isto, o lembrete da manhã é pulado — o de 1h antes já cobre e dois avisos colados incomodam.';

-- Textos padrão — PROPOSTA, sujeita a aprovação do Vitor antes de ligar.
insert into lembretes_config (id, texto_manha, texto_1h)
values (
  1,
  E'Oi {nome}, bom dia! 😊\n\nPassando só pra confirmar nossa conversa de hoje às {hora}.\n\nTá de pé pra você?',
  E'Oi {nome}, nossa conversa é daqui a pouco, às {hora}!\n\nTe chamo por aqui mesmo. Até já 👋'
)
on conflict (id) do nothing;

-- ─────────────────────────────────────────────────────────────────────────────
-- 2b. IMAGEM DE PROVA (2026-09-11) — o disparo da manhã leva um print de
--     resultado de mentorado junto. URL vazia = texto puro, como antes.
--     A edge function troca sendText por sendMedia quando isto está preenchido,
--     com o texto virando legenda: uma mensagem só, não duas.
-- ─────────────────────────────────────────────────────────────────────────────
alter table lembretes_config
  add column if not exists imagem_manha_url text;

comment on column lembretes_config.imagem_manha_url is
  'URL pública da imagem de prova enviada junto do lembrete da manhã (legenda = texto_manha). NULL/vazio = envio de texto puro.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2c. TEXTOS VIGENTES — aprovados pelo Vitor em 2026-09-11, substituem a
--     proposta acima (o insert não sobrescreve linha existente, por isso o
--     update explícito). O segundo disparo passou de 60 para 30 min de
--     antecedência; o tipo continua gravado como '1h' por compatibilidade.
-- ─────────────────────────────────────────────────────────────────────────────
update lembretes_config set
  texto_manha = E'Bom dia, {nome}!\n\nPassando aqui para te lembrar da nossa reunião hoje às {hora}. Por aqui já estamos preparando tudo para o nosso bate-papo!\n\nNos vemos às {hora}!',
  texto_1h    = E'Olá, {nome}!\n\nEm 30 min já envio o link da nossa reunião, ok?',
  antecedencia_min = 30,
  janela_min       = 5,    -- cron a cada 5 min: a mensagem cai entre 25 e 35 min antes
  updated_at  = now()
where id = 1;

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. LOG DE ENVIOS — é também o mecanismo anti-duplicação
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists lembretes_call (
  id          uuid primary key default gen_random_uuid(),
  lead_id     uuid not null references leads(id) on delete cascade,
  tipo        text not null check (tipo in ('manha', '1h')),
  call_em     timestamptz not null,          -- horário da call que originou o aviso
  tel         text not null,
  texto       text,
  status      text not null default 'enviado' check (status in ('enviado', 'falha', 'simulado')),
  detalhe     text,                          -- erro do Evolution, quando falha
  enviado_em  timestamptz not null default now()
);

-- A GARANTIA. Um lembrete por lead, por tipo, por horário de call.
create unique index if not exists lembretes_call_uidx
  on lembretes_call (lead_id, tipo, call_em);

create index if not exists lembretes_call_recentes_idx
  on lembretes_call (enviado_em desc);

comment on table lembretes_call is
  'Log de lembretes de call enviados. O índice único (lead_id, tipo, call_em) é o que impede envio duplicado — não confie em lógica de aplicação para isso.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. VIEW — as calls elegíveis, com o horário já convertido
--    security_invoker: quem consulta pela anon key vê o que a RLS de `leads`
--    deixar ver; a edge function usa service_role e enxerga tudo.
-- ─────────────────────────────────────────────────────────────────────────────
create or replace view public.calls_agendadas
with (security_invoker = true)
as
select
  l.id                        as lead_id,
  l.nome,
  l.tel,
  l.resp,
  l.closer,
  l.expert,
  public.call_em_ts(l.data_call) as call_em
from leads l
where l.status = 'call'
  and l.tel is not null
  and length(regexp_replace(l.tel, '\D', '', 'g')) >= 10
  and public.call_em_ts(l.data_call) is not null;

comment on view public.calls_agendadas is
  'Calls agendadas elegíveis a lembrete: status=call, telefone plausível e data_call em formato ISO parseável.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. RLS — padrão do projeto: leitura ampla para authenticated, mutação só
--    admin. A edge function usa service_role e ignora RLS por natureza; isto
--    aqui protege contra uso indevido via anon key logada.
-- ─────────────────────────────────────────────────────────────────────────────
alter table lembretes_config enable row level security;
alter table lembretes_call   enable row level security;

drop policy if exists "lembretes_config_select" on lembretes_config;
create policy "lembretes_config_select" on lembretes_config
  for select to authenticated using (true);

drop policy if exists "lembretes_config_update" on lembretes_config;
create policy "lembretes_config_update" on lembretes_config
  for update to authenticated using (is_admin());

drop policy if exists "lembretes_call_select" on lembretes_call;
create policy "lembretes_call_select" on lembretes_call
  for select to authenticated using (true);

drop policy if exists "lembretes_call_insert" on lembretes_call;
create policy "lembretes_call_insert" on lembretes_call
  for insert to authenticated with check (is_admin());

drop policy if exists "lembretes_call_delete" on lembretes_call;
create policy "lembretes_call_delete" on lembretes_call
  for delete to authenticated using (is_admin());

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. VERIFICAÇÃO — rodar depois de aplicar
-- ─────────────────────────────────────────────────────────────────────────────
--   select * from calls_agendadas order by call_em;
--   select ativo, hora_manha, antecedencia_min from lembretes_config;
--   select tipo, status, count(*) from lembretes_call group by 1,2;
--
-- O AGENDAMENTO (pg_cron + pg_net) fica em setup-lembrete-call-v1-cron.sql,
-- separado porque exige a service_role key — que nunca passa por chat nem
-- por arquivo versionado.
-- FIM
