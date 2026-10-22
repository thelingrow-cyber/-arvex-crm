// Encurta as pausas longas da narração (voz.wav), acelera opcionalmente (atempo, sem mudar o tom)
// e corrige os tempos da transcricao.json. Sempre parte do original (voz-longa.wav / transcricao-longa.json),
// então pode rodar várias vezes.
// uso: node compactar-pausas.cjs <pasta work> [pausaMax=0.38] [tempo=1]   (env RUIDO=-30 = limiar do silêncio em dB)
const fs = require("fs"), path = require("path"), { execFileSync, spawnSync } = require("child_process");
const work = process.argv[2], MAX = parseFloat(process.argv[3] || "0.38"), TEMPO = parseFloat(process.argv[4] || "1");
const P = (f) => path.join(work, f);
if (!fs.existsSync(P("voz-longa.wav"))) { fs.copyFileSync(P("voz.wav"), P("voz-longa.wav")); fs.copyFileSync(P("transcricao.json"), P("transcricao-longa.json")); }
const t = JSON.parse(fs.readFileSync(P("transcricao-longa.json"), "utf8")), W = t.words;
const dur = +execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", P("voz-longa.wav")]).toString();
// silêncios reais do áudio (o alinhamento da ElevenLabs estica o fim das palavras por cima da pausa)
const log = spawnSync("ffmpeg", ["-i", P("voz-longa.wav"), "-af", `silencedetect=noise=${process.env.RUIDO || "-30"}dB:d=${MAX}`, "-f", "null", "-"], { encoding: "utf8" }).stderr;
const S = [...log.matchAll(/silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)/g)].map((m) => [+m[1], +m[2]]);
const keep = [], shift = []; let ini = 0, corte = 0;
for (const [s0, s1] of S) {
  if (s0 < 0.2 || s1 > dur - 0.05) continue;
  const a = s0 + MAX / 2, b = s1 - MAX / 2;
  keep.push([ini, a]); ini = b; corte += b - a; shift.push([s1, corte]);
}
keep.push([ini, dur]);
const off = (x) => { let s = 0; for (const [t0, c] of shift) if (x >= t0 - 0.15) s = c; return s; };
W.forEach((w) => { const s = off(w.start); w.start = +((w.start - s) / TEMPO).toFixed(3); w.end = +((w.end - s) / TEMPO).toFixed(3); });
const sel = keep.map(([a, b]) => `between(t,${a.toFixed(3)},${b.toFixed(3)})`).join("+");
execFileSync("ffmpeg", ["-v", "error", "-y", "-i", P("voz-longa.wav"), "-af", `aselect='${sel}',asetpts=N/SR/TB${TEMPO !== 1 ? `,atempo=${TEMPO}` : ""}`, P("voz.wav")]);
fs.writeFileSync(P("transcricao.json"), JSON.stringify(t));
const novo = +execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", P("voz.wav")]).toString();
console.log(`pausas cortadas: ${shift.length} · ${dur.toFixed(2)}s → ${novo.toFixed(2)}s (tempo ${TEMPO})`);
