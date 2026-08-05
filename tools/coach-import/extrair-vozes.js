#!/usr/bin/env node
/**
 * extrair-vozes — separa um acervo de .vtt por falante e destaca as vozes dos CONVIDADOS.
 *
 * Numa live/aula, a fala do host é conteúdo; a fala dos participantes é matéria-prima de ICP:
 * é o dono de ótica descrevendo a própria dor, com as palavras dele. Este script inverte a
 * proporção — descarta o host e devolve só o que os outros disseram, com o arquivo de origem.
 *
 * Uso:
 *   node tools/coach-import/extrair-vozes.js <pasta> --host "Cindy Batista" [--min 40] [--out arquivo.md]
 *
 *   --host   nome (ou parte) do falante a descartar; repetível com vírgula
 *   --min    ignora falas menores que N chars (default 40) — corta "sim", "uhum", "isso"
 *   --out    grava o resultado num arquivo em vez do stdout
 */

const fs = require('fs');
const path = require('path');

function args() {
  const a = process.argv.slice(2);
  const o = { alvo: a[0] };
  for (let i = 1; i < a.length; i++) {
    if (!a[i].startsWith('--')) continue;
    const k = a[i].slice(2);
    o[k] = a[i + 1] && !a[i + 1].startsWith('--') ? a[++i] : true;
  }
  return o;
}

/** Lê um .vtt e devolve [{falante, texto}] agregando falas consecutivas do mesmo falante. */
function lerVtt(file) {
  const linhas = fs.readFileSync(file, 'utf8').replace(/^﻿/, '').split(/\r?\n/);
  const turnos = [];
  for (const l of linhas) {
    const t = l.trim();
    if (!t || t === 'WEBVTT' || /^\d+$/.test(t) || t.includes('-->')) continue;
    const m = t.match(/^([^:]{2,40}):\s*(.+)$/);
    if (!m) continue;
    const [, falante, texto] = m;
    const ult = turnos[turnos.length - 1];
    if (ult && ult.falante === falante) ult.texto += ' ' + texto;
    else turnos.push({ falante, texto });
  }
  return turnos;
}

const o = args();
if (!o.alvo) {
  console.error('uso: node extrair-vozes.js <pasta> --host "Nome" [--min 40] [--out arq.md]');
  process.exit(1);
}
const hosts = String(o.host || '').split(',').map((s) => s.trim().toLowerCase()).filter(Boolean);
const MIN = Number(o.min || 40);

// filtro opcional: só falas que contenham marcador de dor/número (regex, case-insensitive)
const FILTRO = o.filtro && o.filtro !== true ? new RegExp(String(o.filtro), 'i') : null;

const arquivos = fs.statSync(o.alvo).isFile()
  ? [o.alvo]
  // ignora cópias do navegador ("arquivo (1).vtt") — o acervo do Downloads tem várias
  : fs.readdirSync(o.alvo)
      .filter((f) => /\.vtt$/i.test(f) && !/\(\d+\)\.vtt$/i.test(f) && !/\.cc\.vtt$/i.test(f))
      .map((f) => path.join(o.alvo, f));

const out = [];
const stats = [];

for (const file of arquivos.sort()) {
  let turnos;
  try { turnos = lerVtt(file); } catch (e) { continue; }
  if (!turnos.length) continue;

  const porFalante = {};
  for (const t of turnos) porFalante[t.falante] = (porFalante[t.falante] || 0) + t.texto.length;

  const convidados = turnos.filter(
    (t) => !hosts.some((h) => t.falante.toLowerCase().includes(h)) &&
           t.texto.length >= MIN &&
           (!FILTRO || FILTRO.test(t.texto)),
  );
  const chars = convidados.reduce((s, t) => s + t.texto.length, 0);
  stats.push({
    arquivo: path.basename(file),
    falantes: Object.keys(porFalante).length,
    total_kb: Math.round(turnos.reduce((s, t) => s + t.texto.length, 0) / 1024),
    convidados_kb: Math.round(chars / 1024),
    vozes: Object.keys(porFalante).filter((f) => !hosts.some((h) => f.toLowerCase().includes(h))).join(', ').slice(0, 60),
  });
  if (!convidados.length) continue;

  out.push(`\n## ${path.basename(file)}\n`);
  for (const t of convidados) out.push(`**${t.falante}:** ${t.texto}`);
}

console.table(stats);
const texto = out.join('\n');
console.log(`\nTotal extraído: ${(texto.length / 1024).toFixed(0)} KB de fala de convidados (de ${arquivos.length} arquivos)`);
if (o.out) {
  fs.writeFileSync(o.out, `# Vozes dos convidados — acervo de lives\n\n> Gerado por tools/coach-import/extrair-vozes.js (host descartado: ${o.host})\n${texto}`, 'utf8');
  console.log(`Gravado em ${o.out}`);
}
