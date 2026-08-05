#!/usr/bin/env node
/**
 * coach-import — importador em lote de transcrições para o Sales Coach (arvex-crm)
 *
 * Sobe transcrições de call (arquivo ou pasta) para a tabela `meetings`, prontas para
 * o Sales Coach analisar. Resolve o gargalo real do coach: a call existe, mas nunca chega no CRM.
 *
 * Formatos aceitos:
 *   .vtt  — Zoom / Meet (WEBVTT com "Falante: texto")
 *   .txt  — plugin ARVEX Meet Transcriber ("[hh:mm:ss] texto") ou texto puro
 *   .md   — transcrição já normalizada no repo (frontmatter YAML + "**Falante:** texto")
 *
 * Uso:
 *   node tools/coach-import/import.js <arquivo|pasta> [opções]
 *
 * Opções:
 *   --closer <email|nome>   quem conduziu a call (default: frontmatter, senão obrigatório)
 *   --cliente <nome>        nome do cliente/lead na call
 *   --lead <uuid|nome>      vincula a um lead do CRM (busca por nome se não for uuid)
 *   --data <YYYY-MM-DD>     data da reunião (default: frontmatter, senão mtime do arquivo)
 *   --resultado <r>         ganhou|perdeu|aberto (default: aberto)
 *   --dry                   mostra o que faria, não escreve nada
 *
 * Env: SUPABASE_DB_URL (connection string do Postgres do Supabase)
 *
 * Dedupe: hash do transcript normalizado vai em meetings.client_key (UNIQUE) —
 * reimportar o mesmo arquivo é no-op, o banco recusa.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { Client } = require('pg');

const MIN_CHARS = 500; // ADR-18: transcript curto demais não vale análise (nem o custo de IA)

// ── parsers ────────────────────────────────────────────────────────────────

/** Lixo de UI que o plugin captura junto com a legenda do Meet. */
const RUIDO_PLUGIN = [
  /ARVEX Meet Transcriber/i,
  /Foto do perfil de usu[áa]rio/i,
  /Enviar ao CRM/i,
  /Legenda \(CC\) n[ãa]o detectada/i,
  /Sua c[âa]mera est[áa]/i,
  /Mudar de conta/i,
];

function parseVtt(raw) {
  const linhas = raw.split(/\r?\n/);
  const turnos = [];
  for (const l of linhas) {
    const t = l.trim();
    if (!t || t === 'WEBVTT' || /^\d+$/.test(t) || t.includes('-->')) continue;
    turnos.push(t);
  }
  return turnos.join('\n');
}

function parsePluginTxt(raw) {
  const linhas = raw.split(/\r?\n/);
  const out = [];
  for (const l of linhas) {
    const t = l.trim();
    if (!t) continue;
    if (RUIDO_PLUGIN.some((re) => re.test(t))) continue;
    out.push(t);
  }
  return out.join('\n');
}

function parseMd(raw) {
  // remove frontmatter e converte "**Falante:** texto" → "Falante: texto"
  const semFm = raw.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '');
  return semFm
    .split(/\r?\n/)
    .filter((l) => !/^\s*(#|>)/.test(l)) // tira títulos e blockquotes de anotação
    .map((l) => l.replace(/^\*\*(.+?):\*\*\s*/, '$1: ').trim())
    .filter(Boolean)
    .join('\n');
}

function lerFrontmatter(raw) {
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return {};
  const fm = {};
  for (const linha of m[1].split(/\r?\n/)) {
    const kv = linha.match(/^(\w+):\s*(.+)$/);
    if (kv) fm[kv[1]] = kv[2].trim();
  }
  return fm;
}

function parseArquivo(file) {
  const raw = fs.readFileSync(file, 'utf8').replace(/^﻿/, '');
  const ext = path.extname(file).toLowerCase();
  const fm = ext === '.md' ? lerFrontmatter(raw) : {};
  let texto;
  if (ext === '.vtt') texto = parseVtt(raw);
  else if (ext === '.md') texto = parseMd(raw);
  else texto = parsePluginTxt(raw);
  // normalização final: espaços colapsados, sem linhas vazias repetidas
  texto = texto.replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n').trim();
  return { texto, fm };
}

// ── helpers ────────────────────────────────────────────────────────────────

function hash12(s) {
  return crypto.createHash('sha256').update(s).digest('hex').slice(0, 12);
}

function args() {
  const a = process.argv.slice(2);
  const alvo = a[0];
  const o = {};
  for (let i = 1; i < a.length; i++) {
    if (!a[i].startsWith('--')) continue;
    const k = a[i].slice(2);
    o[k] = a[i + 1] && !a[i + 1].startsWith('--') ? a[++i] : true;
  }
  return { alvo, o };
}

function listar(alvo) {
  const st = fs.statSync(alvo);
  if (st.isFile()) return [alvo];
  return fs
    .readdirSync(alvo)
    .filter((f) => /\.(vtt|txt|md)$/i.test(f))
    .map((f) => path.join(alvo, f));
}

async function resolverCloser(db, ref) {
  if (!ref) return null;
  const r = await db.query(
    `select p.id, p.display_name, u.email from profiles p
     join auth.users u on u.id = p.id
     where u.email ilike $1 or p.display_name ilike $1 or p.name ilike $1 limit 2`,
    [String(ref)],
  );
  if (r.rows.length === 0) throw new Error(`closer não encontrado: ${ref}`);
  if (r.rows.length > 1) throw new Error(`closer ambíguo: ${ref} — use o e-mail completo`);
  return r.rows[0];
}

async function resolverLead(db, ref) {
  if (!ref) return null;
  const ehUuid = /^[0-9a-f-]{36}$/i.test(String(ref));
  const r = ehUuid
    ? await db.query(`select id, nome from leads where id = $1`, [ref])
    : await db.query(`select id, nome from leads where nome ilike $1 order by created_at desc limit 2`, [`%${ref}%`]);
  if (r.rows.length === 0) throw new Error(`lead não encontrado: ${ref}`);
  if (r.rows.length > 1) throw new Error(`lead ambíguo: ${ref} — passe o uuid`);
  return r.rows[0];
}

// ── main ───────────────────────────────────────────────────────────────────

(async function main() {
  const { alvo, o } = args();
  if (!alvo) {
    console.error('uso: node import.js <arquivo|pasta> [--closer x] [--cliente x] [--lead x] [--data YYYY-MM-DD] [--dry]');
    process.exit(1);
  }
  if (!process.env.SUPABASE_DB_URL) {
    console.error('SUPABASE_DB_URL não definida no ambiente.');
    process.exit(1);
  }

  const db = new Client({ connectionString: process.env.SUPABASE_DB_URL, ssl: { rejectUnauthorized: false } });
  await db.connect();

  const arquivos = listar(alvo);
  console.log(`${arquivos.length} arquivo(s) para processar\n`);

  let ok = 0, pulados = 0, erros = 0;

  for (const file of arquivos) {
    const nome = path.basename(file);
    try {
      const { texto, fm } = parseArquivo(file);

      if (texto.length < MIN_CHARS) {
        console.log(`⊘ ${nome} — ${texto.length} chars (< ${MIN_CHARS}), pulado`);
        pulados++;
        continue;
      }

      const closerRef = o.closer || fm.closer;
      const closer = await resolverCloser(db, closerRef);
      if (!closer) throw new Error('informe --closer (e-mail ou nome)');

      const leadRef = o.lead || fm.lead_id;
      const lead = leadRef ? await resolverLead(db, leadRef) : null;

      const data = o.data || fm.data || fs.statSync(file).mtime.toISOString().slice(0, 10);
      const cliente = o.cliente || fm.lead || (lead && lead.nome) || null;
      // frontmatter costuma trazer resultado com explicação ("aberto — pediu prazo..."); só o 1º token importa
      const resultadoBruto = String(o.resultado || fm.resultado || 'aberto').trim().split(/[\s—-]/)[0];
      const resultado = ['ganhou', 'perdeu', 'aberto'].includes(resultadoBruto) ? resultadoBruto : 'aberto';
      const clientKey = `import:${hash12(texto)}`;

      const dup = await db.query(`select id from meetings where client_key = $1`, [clientKey]);
      if (dup.rows.length) {
        console.log(`⊘ ${nome} — já importada (${dup.rows[0].id})`);
        pulados++;
        continue;
      }

      if (o.dry) {
        console.log(`▷ ${nome} — ${texto.length} chars · closer=${closer.display_name || closer.email}` +
          ` · lead=${lead ? lead.nome : '—'} · data=${data} · resultado=${resultado} · key=${clientKey}`);
        ok++;
        continue;
      }

      const ins = await db.query(
        `insert into meetings (lead_id, closer_id, closer_nome, cliente_nome, data_reuniao,
                               transcript, resultado, status, client_key)
         values ($1,$2,$3,$4,$5,$6,$7,'pending',$8) returning id`,
        [lead ? lead.id : null, closer.id, closer.display_name || closer.email, cliente, data,
         texto, resultado, clientKey],
      );
      console.log(`✓ ${nome} — ${texto.length} chars → meeting ${ins.rows[0].id} (status pending)`);
      ok++;
    } catch (e) {
      console.log(`✗ ${nome} — ${e.message}`);
      erros++;
    }
  }

  console.log(`\n${ok} importada(s) · ${pulados} pulada(s) · ${erros} erro(s)`);
  if (ok && !o.dry) console.log('Próximo passo: abrir a aba Reuniões no CRM e rodar a análise das pendentes.');
  await db.end();
})();
