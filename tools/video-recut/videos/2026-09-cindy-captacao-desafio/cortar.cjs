// Jump cut: tira as pausas entre frases a partir dos timestamps de palavra (Groq) e remapeia a legenda.
// uso: node cortar.cjs   (roda depois do prep; guarda o vídeo inteiro em input-full.mp4 e grava cortes.json)
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const NOME = path.basename(__dirname);
const work = path.join(__dirname, "../../work", NOME);
const pub = path.join(work, "public");
const full = path.join(work, "input-full.mp4");
if (!fs.existsSync(full)) fs.renameSync(path.join(pub, "input-video.mp4"), full);

const GAP = 0.28, PRE = 0.06, POS = 0.08; // pausa maior que GAP sai; folga antes/depois da fala
// correções da transcrição (ASR errou nomes)
const FIX = { "taca": "estaca", "Oscars": "óticas", "Oscar": "ótica", "100K.": "+100K." };
const j = JSON.parse(fs.readFileSync(path.join(work, "transcricao.json"), "utf8").replace(/^﻿/, ""));
let prev = 0;
const words = j.words.map((w) => { const s = Math.max(w.start, prev); prev = s; return { t: FIX[w.word.trim()] ?? w.word.trim(), s, e: Math.max(w.end, s + 0.05) }; });

// o Groq estica o fim da palavra até a próxima → pausas vêm do áudio (silencedetect), não da transcrição
const log = require("child_process").spawnSync("ffmpeg", ["-hide_banner", "-i", full, "-af", `silencedetect=noise=-33dB:d=${GAP}`, "-f", "null", "-"], { encoding: "utf8" }).stderr;
const durFull = parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", full]).toString());
const sil = [...log.matchAll(/silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)/g)].map((m) => [+m[1], +m[2]]);
const seg = [];
let a = 0;
for (const [s, e] of sil) {
  if (s < 0.05) { a = Math.max(0, e - PRE); continue; }
  if (e > durFull - 0.2) break;
  seg.push([a, s + POS]); a = e - PRE;
}
seg.push([a, Math.min(durFull, words[words.length - 1].e + 0.9)]);
const off = []; let acc = 0; for (const [x, y] of seg) { off.push(acc); acc += y - x; }
const map = (t) => { for (let i = 0; i < seg.length; i++) { const [x, y] = seg[i]; if (t < x) return off[i]; if (t <= y) return off[i] + t - x; } return acc; };

let fc = "";
seg.forEach(([x, y], i) => {
  fc += `[0:v]trim=${x.toFixed(3)}:${y.toFixed(3)},setpts=PTS-STARTPTS[v${i}];[0:a]atrim=${x.toFixed(3)}:${y.toFixed(3)},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st=${(y - x - 0.03).toFixed(3)}:d=0.03[a${i}];`;
});
fc += seg.map((_, i) => `[v${i}][a${i}]`).join("") + `concat=n=${seg.length}:v=1:a=1[v][a]`;
fs.writeFileSync(path.join(work, "cortes-filtro.txt"), fc);
execFileSync("ffmpeg", ["-v", "error", "-y", "-i", full, "-filter_complex_script", path.join(work, "cortes-filtro.txt"), "-map", "[v]", "-map", "[a]",
  "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
  path.join(pub, "input-video.mp4")], { stdio: "inherit" });

// legenda remapeada (mesmas regras do agrupar.cjs)
const groups = []; let cur = [];
words.forEach((w, i) => {
  cur.push(w);
  const nx = words[i + 1];
  const chars = cur.map((x) => x.t).join(" ").length;
  if (!nx || nx.s - w.e > 0.45 || cur.length >= 4 || chars >= 22 || (/[.,!?;:]$/.test(w.t) && cur.length >= 2)) {
    groups.push(cur.map((x) => [x.t, +map(x.s).toFixed(2)])); cur = [];
  }
});
fs.writeFileSync(path.join(work, "legenda.json"), "[\n" + groups.map((g) => "  " + JSON.stringify(g)).join(",\n") + "\n]\n");
fs.writeFileSync(path.join(work, "meta.json"), JSON.stringify({ duracao: +acc.toFixed(2) }));
fs.writeFileSync(path.join(work, "cortes.json"), JSON.stringify({ seg, off }));
console.log(`${seg.length} trechos · ${durFull.toFixed(2)}s → ${acc.toFixed(2)}s`);
console.log("cortes (tempo editado):", off.slice(1).map((o) => o.toFixed(2)).join(" "));
console.log(words.map((w) => `${w.t}@${map(w.s).toFixed(2)}`).join(" "));
