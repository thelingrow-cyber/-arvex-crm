#!/usr/bin/env node
/**
 * analisar-pendentes.js — dispara a análise das reuniões que estão paradas.
 *
 * Existe porque a importação em lote (tools/coach-import) grava a call mas NÃO
 * analisa: até 2026-08-13 a única forma de rodar era abrir a aba Reuniões no CRM
 * e clicar em "Reanalisar" uma a uma. Resultado: 6 calls com transcrição completa
 * ficaram 8 dias em `pending` e o cérebro (11 blocos) nunca tinha rodado uma
 * análise sequer. Ingestão sem disparo é dado morto.
 *
 * Autentica como service: a edge function aceita o Bearer que for igual à
 * SERVICE_ROLE_KEY do runtime (caminho 1 do authenticate()). Como o projeto tem
 * chaves legacy e novas (sb_secret_), testamos as candidatas na primeira reunião
 * e seguimos com a que o runtime aceitar.
 *
 * Uso (PowerShell):
 *   $reg = Get-ItemProperty -Path 'HKCU:\Environment'
 *   $env:SUPABASE_DB_URL = $reg.SUPABASE_DB_URL
 *   $env:SUPABASE_ACCESS_TOKEN = $reg.SUPABASE_ACCESS_TOKEN
 *   $env:NODE_PATH = 'c:\Users\Vitor Simões\Desktop\ARVEX\node_modules'
 *   node tools\sales-coach\analisar-pendentes.js
 *
 * Cada call leva ~50s (Sonnet 4.6 com cérebro + histórico injetados).
 */
const { Client } = require('pg');

const REF = 'sgeoikzyahhdrncesbpn';
const FN = `https://${REF}.supabase.co/functions/v1/analyze-meeting`;

async function chavesDeServico() {
  const r = await fetch(`https://api.supabase.com/v1/projects/${REF}/api-keys?reveal=true`, {
    headers: { Authorization: `Bearer ${process.env.SUPABASE_ACCESS_TOKEN}` }
  });
  if (!r.ok) throw new Error(`api-keys ${r.status}: ${await r.text()}`);
  const keys = await r.json();
  const cand = [keys.find(k => k.type === 'secret'), keys.find(k => k.name === 'service_role')]
    .filter(Boolean).map(k => k.api_key);
  if (!cand.length) throw new Error('nenhuma chave de serviço no projeto');
  return cand;
}

const invoke = async (meeting_id, key) => {
  const r = await fetch(FN, {
    method: 'POST',
    headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ meeting_id })
  });
  return { status: r.status, body: await r.json().catch(() => ({})) };
};

const naoAutorizado = b => b.error === 'token inválido' || b.error === 'não autorizado';

(async () => {
  for (const v of ['SUPABASE_DB_URL', 'SUPABASE_ACCESS_TOKEN']) {
    if (!process.env[v]) { console.error(`${v} não definida.`); process.exit(1); }
  }
  const candidatas = await chavesDeServico();

  const c = new Client({ connectionString: process.env.SUPABASE_DB_URL, ssl: { rejectUnauthorized: false } });
  await c.connect();
  const { rows } = await c.query(`
    select id, cliente_nome, closer_nome, resultado, length(transcript) chars
      from meetings
     where status in ('pending', 'error') and coalesce(transcript, '') <> ''
     order by data_reuniao asc nulls last`);

  if (!rows.length) { console.log('✓ nenhuma reunião pendente.'); await c.end(); return; }
  console.log(`${rows.length} reunião(ões) a analisar (~50s cada)\n`);

  let key = null;
  const feito = [];

  for (const m of rows) {
    const rotulo = `${m.cliente_nome ?? '(sem nome)'} — ${m.closer_nome ?? '(sem closer)'}/${m.resultado}, ${m.chars} chars`;
    const t0 = Date.now();
    process.stdout.write(`→ ${rotulo} ... `);
    try {
      let res;
      if (key) {
        res = await invoke(m.id, key);
      } else {
        // primeira reunião: descobre qual chave o runtime aceita
        for (const k of candidatas) {
          res = await invoke(m.id, k);
          if (!naoAutorizado(res.body)) { key = k; break; }
        }
        if (!key) throw new Error('nenhuma chave de serviço foi aceita pela edge function');
      }
      const s = ((Date.now() - t0) / 1000).toFixed(0);
      if (res.body.ok) {
        feito.push(m.id);
        console.log(`OK nota ${res.body.nota_geral} (${s}s)`);
      } else {
        console.log(`FALHOU ${res.status}: ${res.body.error ?? JSON.stringify(res.body)} (${s}s)`);
      }
    } catch (e) {
      console.log(`ERRO: ${e.message}`);
      if (/nenhuma chave/.test(e.message)) break; // não adianta insistir nas outras
    }
  }

  const { rows: fim } = await c.query(`select status, count(*) qtd from meetings group by status order by 1`);
  console.log(`\n${feito.length}/${rows.length} analisadas · status: ${fim.map(r => `${r.status}=${r.qtd}`).join(' · ')}`);
  await c.end();
})().catch(e => { console.error('ERR:', e.message); process.exit(1); });
