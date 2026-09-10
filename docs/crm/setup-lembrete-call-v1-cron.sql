-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║          CRM ARVEX — setup-lembrete-call-v1-cron.sql (PARTE 2)            ║
-- ╠═══════════════════════════════════════════════════════════════════════════╣
-- ║ Agendamento do lembrete de call (pg_cron + pg_net).                       ║
-- ║                                                                           ║
-- ║ ⚠️  RODAR NO SQL EDITOR DO SUPABASE, NÃO POR AQUI.                        ║
-- ║ Este arquivo pede a SERVICE_ROLE KEY. Ela nunca é colada em chat, nunca   ║
-- ║ é commitada e nunca entra em arquivo versionado (ADR-3.3 — causa raiz de  ║
-- ║ dois vazamentos anteriores). Você cola o valor direto no SQL Editor; ele  ║
-- ║ vai para o Vault criptografado e some da tela.                            ║
-- ║                                                                           ║
-- ║ Pré-requisitos: setup-lembrete-call-v1.sql aplicado (feito) e a edge      ║
-- ║ function `lembrete-call` deployada.                                       ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. EXTENSÕES — já habilitadas em 2026-09-10. Idempotente, pode rodar de novo.
-- ─────────────────────────────────────────────────────────────────────────────
create extension if not exists pg_net;
create extension if not exists pg_cron;

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. GUARDAR A CHAVE NO VAULT
--    Supabase → Project Settings → API → service_role (secret). Copie e cole
--    NO LUGAR do placeholder abaixo. Rode só esta parte primeiro.
--    O cron lê daqui; a chave não fica no texto do job.
-- ─────────────────────────────────────────────────────────────────────────────
select vault.create_secret(
  'COLE_AQUI_A_SERVICE_ROLE_KEY',   -- ← substituir, rodar, e não salvar o arquivo com a chave
  'lembrete_call_service_key',
  'service_role key usada pelo cron do lembrete de call'
);
-- Se já existir e você precisar trocar a chave depois:
--   select vault.update_secret(
--     (select id from vault.secrets where name = 'lembrete_call_service_key'),
--     'NOVA_KEY'
--   );

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. FUNÇÃO DISPARADORA
--    Encapsula a chamada HTTP para não repetir a leitura do Vault em cada job
--    e para o texto do cron ficar legível em `select * from cron.job`.
-- ─────────────────────────────────────────────────────────────────────────────
create or replace function public.disparar_lembrete_call(p_tipo text)
returns bigint
language plpgsql
security definer
set search_path = public, vault
as $$
declare
  v_key text;
  v_req bigint;
begin
  select decrypted_secret into v_key
    from vault.decrypted_secrets
   where name = 'lembrete_call_service_key';

  if v_key is null then
    raise exception 'segredo lembrete_call_service_key ausente no Vault';
  end if;

  select net.http_post(
    url     := 'https://sgeoikzyahhdrncesbpn.supabase.co/functions/v1/lembrete-call',
    headers := jsonb_build_object(
                 'Content-Type',  'application/json',
                 'Authorization', 'Bearer ' || v_key
               ),
    body    := jsonb_build_object('tipo', p_tipo, 'dry_run', false),
    timeout_milliseconds := 60000
  ) into v_req;

  return v_req;
end;
$$;

revoke all on function public.disparar_lembrete_call(text) from public, anon, authenticated;

comment on function public.disparar_lembrete_call(text) is
  'Chama a edge function lembrete-call. security definer + Vault: a service_role key não aparece no texto do job nem é acessível a usuário logado.';

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. OS DOIS JOBS
--
--    ⚠️ pg_cron roda em UTC. O Brasil está em UTC-3 (sem horário de verão
--    desde 2019). Some 3 horas ao horário desejado:
--      09:00 de Brasília  →  12:00 UTC
--
--    · manhã : uma vez por dia, varre todas as calls do dia
--    · 1h    : a cada 10 min, das 07h às 21h de Brasília (10-23 UTC). Fora
--              dessa faixa não há call, e a própria function tem janela de
--              silêncio como segunda trava.
-- ─────────────────────────────────────────────────────────────────────────────
select cron.unschedule('lembrete-call-manha') where exists (
  select 1 from cron.job where jobname = 'lembrete-call-manha'
);
select cron.unschedule('lembrete-call-1h') where exists (
  select 1 from cron.job where jobname = 'lembrete-call-1h'
);

select cron.schedule(
  'lembrete-call-manha',
  '0 12 * * *',                       -- 09:00 de Brasília
  $$select public.disparar_lembrete_call('manha')$$
);

select cron.schedule(
  'lembrete-call-1h',
  '*/10 10-23 * * *',                 -- a cada 10 min, 07h–20h50 de Brasília
  $$select public.disparar_lembrete_call('1h')$$
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. LIGAR DE VERDADE (só depois do teste em dry-run e da aprovação do texto)
-- ─────────────────────────────────────────────────────────────────────────────
-- update lembretes_config set ativo = true, updated_at = now() where id = 1;

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. VERIFICAÇÃO E OPERAÇÃO DO DIA A DIA
-- ─────────────────────────────────────────────────────────────────────────────
-- Jobs agendados:
--   select jobid, jobname, schedule, active from cron.job;
--
-- Últimas execuções do cron (falhou? demorou?):
--   select jobid, status, return_message, start_time
--     from cron.job_run_details order by start_time desc limit 20;
--
-- Respostas HTTP da edge function (o que ela devolveu de fato):
--   select id, created, status_code, content
--     from net._http_response order by created desc limit 20;
--
-- Lembretes enviados:
--   select l.enviado_em, le.nome, l.tipo, l.status, l.detalhe
--     from lembretes_call l join leads le on le.id = l.lead_id
--    order by l.enviado_em desc limit 30;
--
-- PARAR TUDO na hora (não precisa desagendar):
--   update lembretes_config set ativo = false where id = 1;
--
-- Desagendar de vez:
--   select cron.unschedule('lembrete-call-manha');
--   select cron.unschedule('lembrete-call-1h');
-- FIM
