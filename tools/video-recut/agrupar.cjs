// Transforma a transcrição da Groq (verbose_json com words) em grupos de legenda.
// uso: node agrupar.cjs <transcricao.json> <inicioCorte> <fimCorte> <saida legenda.json>
// Regras: quebra em pontuação, pausa > 0.45s, 4 palavras ou 22 caracteres. Revisar à mão depois (ASR erra nomes).
const fs = require("fs");
const [, , src, ini = "0", fim = "99999", out = "legenda.json"] = process.argv;
const t0 = parseFloat(ini), t1 = parseFloat(fim);
const j = JSON.parse(fs.readFileSync(src, "utf8").replace(/^﻿/, ""));
const words = (j.words || []).filter((w) => w.start >= t0 - 0.05 && w.start < t1)
  .map((w) => ({ t: w.word.trim(), s: +(w.start - t0).toFixed(2), e: +(Math.min(w.end, t1) - t0).toFixed(2) }));

const groups = [];
let cur = [];
words.forEach((w, i) => {
  cur.push(w);
  const next = words[i + 1];
  const chars = cur.map((x) => x.t).join(" ").length;
  const pontua = /[.,!?;:]$/.test(w.t);
  const pausa = next && next.s - w.e > 0.45;
  if (!next || pausa || cur.length >= 4 || chars >= 22 || (pontua && cur.length >= 2)) {
    groups.push(cur.map((x) => [x.t, x.s]));
    cur = [];
  }
});
fs.writeFileSync(out, "[\n" + groups.map((g) => "  " + JSON.stringify(g)).join(",\n") + "\n]\n", "utf8");
console.log(`${words.length} palavras → ${groups.length} grupos → ${out}`);
console.log(words.map((w) => `${w.t}@${w.s}`).join(" "));
