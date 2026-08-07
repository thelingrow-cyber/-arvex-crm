-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║                    CRM ARVEX — setup-sales-coach-v1.sql                    ║
-- ╠═══════════════════════════════════════════════════════════════════════════╣
-- ║ Módulo: Sales Coach (Sales Intelligence) — análise de reuniões de closers ║
-- ║ Autor:  @data-engineer (Dara)                                             ║
-- ║ Data:   2026-06-27                                                        ║
-- ║ Refs:   docs/crm/sales-coach-architecture.md · sales-coach-mvp-brief.md   ║
-- ║                                                                           ║
-- ║ DECISÕES:                                                                 ║
-- ║   • scores/insights = jsonb (8 dimensões fixas) → MVP enxuto; normaliza   ║
-- ║     só na Fase 3 (comparação entre closers).                              ║
-- ║   • resultado (ganhou/perdeu/aberto) NOT NULL = o ATIVO do sistema.       ║
-- ║   • RLS no padrão do CRM: closer vê só o seu; admin vê tudo.              ║
-- ║   • Backend = Supabase Edge Function (NÃO n8n) escreve via service_role.  ║
-- ║                                                                           ║
-- ║ NATUREZA: aditiva, idempotente, sem DROP. Seguro rodar múltiplas vezes.   ║
-- ║                                                                           ║
-- ║ COMO APLICAR:                                                             ║
-- ║   ► MVP (rodar HOJE):    Seções 1 a 5.                                    ║
-- ║   ► FASE 2 (rodar depois): Seção 6 (pgvector + Sales Brain).              ║
-- ║   Supabase Dashboard → SQL Editor → colar → Run.                          ║
-- ║   Esperado: "Success. No rows returned."                                  ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝


-- ═════════════════════════════════════════════════════════════════════════════
--  PARTE MVP  (rodar hoje — Seções 1 a 5)
-- ═════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- 0. Helper: trigger genérico de updated_at (idempotente, reusável)
-- ─────────────────────────────────────────────────────────────────────────────
create or replace function set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Tabela meetings — uma reunião analisada
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists meetings (
  id            uuid primary key default gen_random_uuid(),
  lead_id       uuid references leads(id) on delete set null,        -- reaproveita lead existente (opcional)
  closer_id     uuid not null references auth.users(id) on delete cascade,
  closer_nome   text,                                                -- denormalizado p/ exibir sem join
  cliente_nome  text,
  produto       text,                                                -- o que foi apresentado
  data_reuniao  date,
  transcript    text,                                                -- ⚠️ dado sensível de cliente (RLS protege)
  resultado     text not null default 'aberto'
                  check (resultado in ('ganhou','perdeu','aberto')), -- O ATIVO
  ticket        numeric,                                             -- preenchido se resultado='ganhou'
  status        text not null default 'pending'
                  check (status in ('pending','processing','done','error')),
  nota_geral    numeric,                                             -- 0–10, média ponderada das dimensões
  scores        jsonb,                                               -- {rapport, diagnostico, escuta, valor, controle, fechamento, transicao, objecoes}
  insights      jsonb,                                               -- {acertos[], erros[], faltou[], sugestoes[]}
  erro_msg      text,                                                -- preenchido se status='error'
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  analyzed_at   timestamptz                                          -- quando a IA concluiu
);

comment on table  meetings is 'Reuniões de closers analisadas pela IA (Sales Coach). Dataset rotulado por resultado = ativo central.';
comment on column meetings.resultado is 'ganhou | perdeu | aberto — rótulo obrigatório; base do aprendizado do sistema.';
comment on column meetings.scores    is 'jsonb {dimensao: nota 0-10} para as 8 dimensões avaliadas.';
comment on column meetings.insights  is 'jsonb {acertos[], erros[], faltou[], sugestoes[]} gerado pela IA.';
comment on column meetings.status    is 'pending → processing → done | error (controlado pela Edge Function).';

-- trigger de updated_at
drop trigger if exists meetings_set_updated_at on meetings;
create trigger meetings_set_updated_at
  before update on meetings
  for each row execute procedure set_updated_at();

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Índices (servem os padrões de acesso: "minhas reuniões", fila de análise, agenda)
-- ─────────────────────────────────────────────────────────────────────────────
create index if not exists meetings_closer_idx       on meetings (closer_id, created_at desc);
create index if not exists meetings_status_idx        on meetings (status);
create index if not exists meetings_data_reuniao_idx  on meetings (data_reuniao desc);
create index if not exists meetings_resultado_idx     on meetings (resultado);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. RLS — habilitar
-- ─────────────────────────────────────────────────────────────────────────────
alter table meetings enable row level security;

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. Políticas RLS — closer vê só o seu; admin vê/edita tudo
--    (mesmo modelo do CRM: subquery em profiles para checar role='admin')
-- ─────────────────────────────────────────────────────────────────────────────

-- SELECT: dono OU admin
drop policy if exists meetings_select on meetings;
create policy meetings_select on meetings
  for select to authenticated
  using (
    closer_id = auth.uid()
    or exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin')
  );

-- INSERT: o closer só cria reunião como dono (closer_id = ele); admin pode criar p/ qualquer um
drop policy if exists meetings_insert on meetings;
create policy meetings_insert on meetings
  for insert to authenticated
  with check (
    closer_id = auth.uid()
    or exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin')
  );

-- UPDATE: dono OU admin (cobre FR9 — confirmar/ajustar resultado)
drop policy if exists meetings_update on meetings;
create policy meetings_update on meetings
  for update to authenticated
  using (
    closer_id = auth.uid()
    or exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin')
  )
  with check (
    closer_id = auth.uid()
    or exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin')
  );

-- DELETE: só admin (higiene; closer não apaga histórico = preserva o ativo)
drop policy if exists meetings_delete on meetings;
create policy meetings_delete on meetings
  for delete to authenticated
  using (exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin'));

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. NOTA sobre a Edge Function (analyze-meeting)
--    A função roda com SERVICE_ROLE (bypassa RLS) para ler transcript e gravar
--    scores/insights/status. NUNCA usar service_role no front. Sem ação de SQL aqui.
-- ─────────────────────────────────────────────────────────────────────────────


-- ═════════════════════════════════════════════════════════════════════════════
--  PARTE FASE 2  (Sales Brain — pgvector) — NÃO precisa rodar hoje
--  Rodar quando for indexar playbook/frameworks p/ RAG. Até lá, a Edge Function
--  usa um playbook curto hardcoded no prompt (ver architecture §6).
-- ═════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.1 Extensão pgvector
-- ─────────────────────────────────────────────────────────────────────────────
-- create extension if not exists vector;

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.2 Tabela sales_brain_docs — base de conhecimento indexada
-- ─────────────────────────────────────────────────────────────────────────────
-- create table if not exists sales_brain_docs (
--   id         uuid primary key default gen_random_uuid(),
--   titulo     text,
--   tipo       text check (tipo in ('playbook','framework','script','objecao','case')),
--   conteudo   text not null,
--   embedding  vector(1536),               -- OpenAI text-embedding-3-small
--   created_at timestamptz not null default now()
-- );
-- comment on table sales_brain_docs is 'Sales Brain: chunks de conhecimento comercial p/ RAG (Fase 2).';

-- índice ANN (hnsw cosine — funciona em tabela vazia, sem tuning de lists)
-- create index if not exists sales_brain_docs_embedding_idx
--   on sales_brain_docs using hnsw (embedding vector_cosine_ops);

-- RLS: leitura p/ autenticados; escrita só admin
-- alter table sales_brain_docs enable row level security;
-- drop policy if exists brain_select on sales_brain_docs;
-- create policy brain_select on sales_brain_docs
--   for select to authenticated using (true);
-- drop policy if exists brain_write on sales_brain_docs;
-- create policy brain_write on sales_brain_docs
--   for all to authenticated
--   using      (exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin'))
--   with check (exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin'));

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.3 RPC match_brain — similarity search (chamada pela Edge Function)
-- ─────────────────────────────────────────────────────────────────────────────
-- create or replace function match_brain(query_embedding vector(1536), match_count int default 5)
-- returns table (id uuid, titulo text, tipo text, conteudo text, similarity float)
-- language sql stable as $$
--   select d.id, d.titulo, d.tipo, d.conteudo,
--          1 - (d.embedding <=> query_embedding) as similarity
--   from sales_brain_docs d
--   where d.embedding is not null
--   order by d.embedding <=> query_embedding
--   limit match_count;
-- $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- VALIDAÇÃO (MVP):
--   select count(*) from meetings;                          -- deve retornar 0
--   select policyname from pg_policies where tablename='meetings';  -- 4 políticas
-- ─────────────────────────────────────────────────────────────────────────────
-- FIM — ARVEX CRM Sales Coach v1.0
