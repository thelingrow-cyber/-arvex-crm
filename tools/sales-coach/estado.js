#!/usr/bin/env node
/**
 * estado.js — imprime a VERDADE do Sales Coach lendo o banco de produção.
 *
 * Existe porque documentação envelhece e banco não. Antes de confiar em qualquer
 * doc do sistema, rode isto.
 *
 * Uso:  SUPABASE_DB_URL=... node tools/sales-coach/estado.js
 * No Windows (PowerShell):
 *   $env:SUPABASE_DB_URL = (Get-ItemProperty -Path 'HKCU:\Environment' -Name 'SUPABASE_DB_URL').SUPABASE_DB_URL
 *   $env:NODE_PATH = 'c:\Users\Vitor Simões\Desktop\ARVEX\node_modules'
 *   node tools\sales-coach\estado.js
 */
const { Client } = require('pg');

const TETO_CEREBRO = 28000; // espelha KB_MAX_CHARS nas edge functions

const QUERIES = [
  ['CÉREBRO — blocos ativos', `
    select tipo, titulo, length(conteudo) chars, peso
      from sales_knowledge where ativo order by peso desc, chars desc`],
  ['CÉREBRO — total', `
    select count(*) blocos, sum(length(conteudo)) chars,
           ${TETO_CEREBRO} - sum(length(conteudo)) folga_ate_o_teto
      from sales_knowledge where ativo`],
  ['CÉREBRO — desativados (histórico, fora do prompt)', `
    select titulo, length(conteudo) chars from sales_knowledge where not ativo order by updated_at desc`],
  ['REUNIÕES — por status', `
    select status, count(*) qtd, sum(length(transcript))/1024 kb_transcricao
      from meetings group by status order by 1`],
  ['REUNIÕES — por closer', `
    select coalesce(m.closer_nome,'(sem closer)') closer,
           count(*) total,
           count(*) filter (where m.status='done') analisadas,
           count(*) filter (where m.resultado='ganhou') ganhou,
           count(*) filter (where m.resultado='perdeu') perdeu,
           count(*) filter (where m.resultado='aberto' or m.resultado is null) aberto,
           round(avg(m.nota_geral),1) nota_media
      from meetings m group by 1 order by 2 desc`],
  ['REUNIÕES — vínculo com lead (pré-requisito do desfecho automático)', `
    select count(*) total, count(lead_id) com_lead, count(*)-count(lead_id) sem_lead from meetings`],
  ['SCHEMA — o que já existe do roadmap', `
    select 'coluna meetings.metrics (ADR-20)' item,
           (select count(*) from information_schema.columns
             where table_name='meetings' and column_name='metrics')::text existe
    union all select 'função stats_closer (ADR-21)',
           (select count(*) from pg_proc p join pg_namespace n on n.oid=p.pronamespace
             where n.nspname='public' and p.proname='stats_closer')::text
    union all select 'tabela closer_profiles (fase 3c)',
           (select count(*) from information_schema.tables
             where table_schema='public' and table_name='closer_profiles')::text
    union all select 'índice único de título no cérebro (guard 011)',
           (select count(*) from pg_indexes
             where tablename='sales_knowledge' and indexname='sales_knowledge_titulo_uk')::text`],
];

(async () => {
  if (!process.env.SUPABASE_DB_URL) {
    console.error('SUPABASE_DB_URL não definida.');
    process.exit(1);
  }
  const c = new Client({ connectionString: process.env.SUPABASE_DB_URL, ssl: { rejectUnauthorized: false } });
  await c.connect();
  console.log(`\n=== SALES COACH — estado em ${new Date().toLocaleString('pt-BR')} ===`);
  for (const [titulo, sql] of QUERIES) {
    try {
      const r = await c.query(sql);
      console.log(`\n### ${titulo}`);
      if (!r.rows.length) console.log('(vazio)');
      else console.table(r.rows);
    } catch (e) {
      console.log(`\n### ${titulo}\nERRO: ${e.message}`);
    }
  }
  // alertas
  const { rows: [kb] } = await c.query('select sum(length(conteudo)) t from sales_knowledge where ativo');
  const { rows: [mt] } = await c.query(`select count(*) p from meetings where status='pending'`);
  console.log('\n### ALERTAS');
  const alertas = [];
  if (Number(kb.t) > TETO_CEREBRO) alertas.push(`⚠ cérebro acima do teto (${kb.t}/${TETO_CEREBRO}) — o excedente NÃO é enviado`);
  if (Number(mt.p) > 0) alertas.push(`⚠ ${mt.p} reunião(ões) pendente(s) de análise — abrir Reuniões no CRM e rodar`);
  console.log(alertas.length ? alertas.join('\n') : '✓ nada a reportar');
  console.log('');
  await c.end();
})();
