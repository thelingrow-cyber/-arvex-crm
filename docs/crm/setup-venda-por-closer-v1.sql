-- ── ARVEX CRM — separar "registrar a venda que fechei" de "ver o caixa da empresa" ──
-- Autor:  @data-engineer (Dara) · 2026-07-13
-- Rodar:  aditivo e idempotente (safe re-run)
--
-- O PROBLEMA:
--   Todas as 8 policies de vendas/parcelas exigiam is_financeiro_user() — inclusive SELECT.
--   Consequência: um closer sem acesso ao Financeiro NÃO conseguia registrar a venda que ele
--   mesmo fechou (o insert do front usa .select() e o PostgREST precisa reler a linha).
--   Por isso TODO closer acabou com financeiro=true (Gabriel, Pacheco) — não foi decisão de
--   confiança, foi consequência técnica. E "financeiro" mostra as cobranças, valores e
--   parcelas de TODOS os clientes.
--
-- O QUE MUDA:
--   Vendas e parcelas passam a saber QUEM as criou (criado_por, default auth.uid()).
--   A partir daí, duas permissões distintas:
--     · closer  → registra a venda que fechou e vê SÓ as suas
--     · financeiro → vê e administra TUDO (cobranças, valores, parcelas de todos)
--
-- DECISÕES (não reverter sem ler):
--   1. UPDATE e DELETE continuam EXCLUSIVOS do financeiro. O closer registra; correção de
--      valor/parcela/baixa é do financeiro. Menos superfície, menos erro.
--   2. Vendas antigas ficam com criado_por = NULL (não temos como saber quem criou). Como
--      NULL nunca casa com auth.uid(), closers não enxergam o histórico — só o financeiro.
--   3. Não usar responsavel_cobranca (texto livre) para autorizar: nome não é identidade.
-- ─────────────────────────────────────────────────────────────────────────────

-- 1. AUTORIA (a base de tudo)
alter table vendas   add column if not exists criado_por uuid references auth.users(id) default auth.uid();
alter table parcelas add column if not exists criado_por uuid references auth.users(id) default auth.uid();

comment on column vendas.criado_por is
  'Quem registrou a venda (auth.uid() no momento do insert). Base da RLS: o closer vê e '
  'registra as PRÓPRIAS vendas sem ver o caixa da empresa. NULL nas vendas anteriores a 2026-07-13.';
comment on column parcelas.criado_por is
  'Quem criou a parcela. Mesma lógica de vendas.criado_por.';

-- índices: as policies filtram por criado_por
create index if not exists idx_vendas_criado_por   on vendas   (criado_por);
create index if not exists idx_parcelas_criado_por on parcelas (criado_por);

-- 2. VENDAS — policies
drop policy if exists "vendas_select" on vendas;
create policy "vendas_select" on vendas
  for select to authenticated
  using ( is_financeiro_user() or criado_por = auth.uid() );
  -- financeiro vê tudo; closer vê só as vendas que ele registrou
  -- (isto é o que faz o insert().select() do front funcionar para o closer)

drop policy if exists "vendas_insert" on vendas;
create policy "vendas_insert" on vendas
  for insert to authenticated
  with check ( is_financeiro_user() or criado_por = auth.uid() );
  -- o closer só pode inserir venda EM SEU PRÓPRIO NOME (não falsifica autoria)

drop policy if exists "vendas_update" on vendas;
create policy "vendas_update" on vendas
  for update to authenticated
  using ( is_financeiro_user() ) with check ( is_financeiro_user() );

drop policy if exists "vendas_delete" on vendas;
create policy "vendas_delete" on vendas
  for delete to authenticated
  using ( is_financeiro_user() );

-- 3. PARCELAS — mesma lógica (o closer cria as parcelas junto com a venda)
drop policy if exists "parcelas_select" on parcelas;
create policy "parcelas_select" on parcelas
  for select to authenticated
  using ( is_financeiro_user() or criado_por = auth.uid() );

drop policy if exists "parcelas_insert" on parcelas;
create policy "parcelas_insert" on parcelas
  for insert to authenticated
  with check ( is_financeiro_user() or criado_por = auth.uid() );

drop policy if exists "parcelas_update" on parcelas;
create policy "parcelas_update" on parcelas
  for update to authenticated
  using ( is_financeiro_user() ) with check ( is_financeiro_user() );
  -- marcar como paga / mudar vencimento é do financeiro

drop policy if exists "parcelas_delete" on parcelas;
create policy "parcelas_delete" on parcelas
  for delete to authenticated
  using ( is_financeiro_user() );

-- ─────────────────────────────────────────────────────────────────────────────
-- VERIFICAÇÃO
--   select tablename, policyname, cmd, coalesce(qual::text, with_check::text)
--   from pg_policies where tablename in ('vendas','parcelas') order by tablename, cmd;
--
--   -- como um closer SEM financeiro (impersonação):
--   set local role authenticated;
--   set local request.jwt.claims to '{"sub":"<uuid-do-closer>","role":"authenticated"}';
--   select count(*) from vendas;          -- deve ver só as próprias (0 no começo)
--   insert into vendas (cliente, valor_total) values ('Teste', 100) returning id;  -- deve PASSAR
--   update vendas set valor_total = 1 where id = '<qualquer>';                     -- deve FALHAR
--
-- ROLLBACK (volta ao estado anterior: tudo restrito ao financeiro)
--   create policy "vendas_select"   on vendas   for select to authenticated using (is_financeiro_user());
--   create policy "vendas_insert"   on vendas   for insert to authenticated with check (is_financeiro_user());
--   create policy "parcelas_select" on parcelas for select to authenticated using (is_financeiro_user());
--   create policy "parcelas_insert" on parcelas for insert to authenticated with check (is_financeiro_user());
--   (as colunas criado_por podem permanecer — são aditivas e inofensivas)
-- ─────────────────────────────────────────────────────────────────────────────
