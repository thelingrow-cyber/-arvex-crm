// Limpeza do bruto: corta silêncios e repetições (fica com a ÚLTIMA tentativa da frase).
// uso: node tools/video-recut/limpar.cjs "C:\...\bruto.MOV" 2026-10-meu-video [--gap 0.30] [--sim 0.62] [--sem-render]
// saída: Downloads\<nome>-limpo.mp4 + work\<nome>\limpeza\ (transcricao.json, cortes.json, RELATORIO.md)
// depois: usar o -limpo.mp4 como -Video no prep.ps1 (legenda e cards seguem o fluxo normal).
const fs = require("fs");
const path = require("path");
const os = require("os");
const { spawnSync, execFileSync } = require("child_process");

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const [VIDEO, NOME] = args.filter((a, i) => !a.startsWith("--") && !["--gap", "--sim"].includes(args[i - 1]));
if (!VIDEO || !NOME) { console.error('uso: node limpar.cjs "<video bruto>" <nome> [--gap 0.30] [--sim 0.62] [--sem-render]'); process.exit(1); }
const GAP = +opt("--gap", 0.30);   // silêncio maior que isto sai
const SIM = +opt("--sim", 0.62);   // semelhança mínima para considerar "repetiu a frase"
const PRE = 0.07, POS = 0.12;      // respiro antes/depois da fala (evita cortar consoante)
const RENDER = !args.includes("--sem-render");

const work = path.join(__dirname, "work", NOME, "limpeza");
fs.mkdirSync(work, { recursive: true });
const sh = (cmd, a) => spawnSync(cmd, a, { encoding: "utf8", maxBuffer: 1 << 28 });
const dur = parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VIDEO]).toString());

async function transcrever() {
  const cache = path.join(work, "transcricao.json");
  if (fs.existsSync(cache)) return JSON.parse(fs.readFileSync(cache, "utf8"));
  const k = process.env.GROQ_API_KEY || sh("powershell", ["-NoProfile", "-c", "[Environment]::GetEnvironmentVariable('GROQ_API_KEY','User')"]).stdout.trim();
  if (!k) throw new Error("GROQ_API_KEY não encontrada (env ou variável de usuário).");
  const audio = path.join(os.tmpdir(), `limpar-${process.pid}.flac`);
  execFileSync("ffmpeg", ["-v", "error", "-y", "-i", VIDEO, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "flac", audio]);
  const fd = new FormData();
  fd.append("file", new Blob([fs.readFileSync(audio)]), "audio.flac");
  fd.append("model", "whisper-large-v3-turbo");
  fd.append("language", "pt");
  fd.append("response_format", "verbose_json");
  fd.append("timestamp_granularities[]", "word");
  fd.append("timestamp_granularities[]", "segment");
  const r = await fetch("https://api.groq.com/openai/v1/audio/transcriptions", { method: "POST", headers: { Authorization: `Bearer ${k}` }, body: fd });
  fs.unlinkSync(audio);
  const j = await r.json();
  if (!r.ok || j.error) throw new Error("Groq: " + JSON.stringify(j.error || j));
  fs.writeFileSync(cache, JSON.stringify(j));
  return j;
}

// --- texto ---
const norm = (t) => t.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9%]/g, "");
function lev(a, b) {
  const d = Array.from({ length: a.length + 1 }, (_, i) => [i]);
  for (let j = 1; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++)
    d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return d[a.length][b.length];
}
const ratio = (a, b) => (a.length || b.length) ? 1 - lev(a, b) / Math.max(a.length, b.length) : 1;
// quanto o trecho `cauda` é refeito no começo de `prox` (o refazer pode ter umas palavras a mais ou a menos)
function refeito(cauda, prox) {
  let best = 0;
  for (let m = Math.max(1, cauda.length - 3); m <= Math.min(prox.length, cauda.length + 4); m++) best = Math.max(best, ratio(cauda, prox.slice(0, m)));
  return best;
}

(async () => {
  const j = await transcrever();
  let prev = 0;
  const words = (j.words || []).map((w) => { const s = Math.max(w.start, prev); prev = s; return { t: w.word.trim(), n: norm(w.word), s, e: Math.max(w.end, s + 0.05) }; }).filter((w) => w.n);
  if (!words.length) throw new Error("transcrição sem palavras");

  // 1. fala × silêncio vem do ÁUDIO (o Groq estica o fim das palavras)
  const log = sh("ffmpeg", ["-hide_banner", "-i", VIDEO, "-af", `silencedetect=noise=-33dB:d=${GAP}`, "-f", "null", "-"]).stderr;
  const sil = [...log.matchAll(/silence_start: (-?[\d.]+)[\s\S]*?silence_end: ([\d.]+)/g)].map((m) => [Math.max(0, +m[1]), +m[2]]);
  let fala = []; let a = 0;
  for (const [s, e] of sil) { if (s > a) fala.push([a, s]); a = e; }
  if (a < dur) fala.push([a, dur]);
  fala = fala.filter(([x, y]) => words.some((w) => w.s < y && w.s + 0.04 >= x - 0.15)); // bloco sem palavra = ruído

  // 2. blocos de fala com as palavras dentro
  const blocos = fala.map(([x, y]) => ({ x, y, w: words.filter((w) => w.s >= x - 0.15 && w.s < y) })).filter((b) => b.w.length);

  // 3. repetição imediata dentro do bloco ("o motivo pode o motivo pode mudar") → sai a 1ª cópia
  const cortes = []; // [ini, fim, texto, motivo]
  for (const b of blocos) {
    for (let k = 6; k >= 2; k--) for (let i = 0; i + 2 * k <= b.w.length; i++) {
      const A = b.w.slice(i, i + k).map((w) => w.n), B = b.w.slice(i + k, i + 2 * k).map((w) => w.n);
      if (A.join(" ") === B.join(" ")) {
        cortes.push([b.w[i].s - 0.03, b.w[i + k].s - 0.03, b.w.slice(i, i + k).map((w) => w.t).join(" "), "repetiu na mesma tomada"]);
        b.w.splice(i, k); i--;
      }
    }
  }

  // 4. retomada entre blocos: o fim do bloco anterior é refeito no começo do seguinte → sai a 1ª tentativa
  const vivos = [];
  for (const b of blocos) {
    let mudou = true;
    while (mudou && vivos.length) {
      mudou = false;
      const A = vivos[vivos.length - 1];
      const prox = b.w.map((w) => w.n);
      let cut = -1;
      for (let p = 0; p < A.w.length; p++) {
        const cauda = A.w.slice(p).map((w) => w.n);
        const curta = A.w.length - p <= 2;
        if (curta && p > 0) continue;                           // cauda de 1–2 palavras só conta se for o bloco inteiro (falso começo)
        const r = refeito(cauda, prox);
        if (r >= (curta ? 0.99 : SIM)) { cut = p; break; }      // a 1ª (maior) cauda que passa
      }
      if (cut < 0) {                                            // tentativa abandonada: começa igual ao próximo e para no meio
        const ini = A.w.slice(0, 3).map((w) => w.n);
        if (A.w.length >= 2 && A.w.length < prox.length && ratio(ini, prox.slice(0, ini.length)) >= 0.99) cut = 0;
        // falso começo curto ("porque a…" → "porque agora…"): até 3 palavras, mesma 1ª palavra (não artigo/conectivo de 1–2 letras)
        else if (A.w.length <= 3 && prox.length > A.w.length && A.w[0].n === prox[0] && A.w[0].n.length >= 3) cut = 0;
      }
      if (cut >= 0) {
        const t0 = cut === 0 ? A.x : A.w[cut].s - 0.03;
        cortes.push([t0, A.y, A.w.slice(cut).map((w) => w.t).join(" "), "refez a frase (ficou a última)"]);
        if (cut === 0) { vivos.pop(); mudou = true; } else { A.y = t0; A.w = A.w.slice(0, cut); }
      }
    }
    vivos.push(b);
  }

  // 5. trechos que ficam = blocos vivos com respiro, menos os cortes internos
  let keep = vivos.map((b) => [Math.max(0, b.x - PRE), Math.min(dur, b.y + POS)]);
  for (const [c0, c1] of cortes.filter((c) => c[3].startsWith("repetiu"))) {
    keep = keep.flatMap(([x, y]) => (c1 <= x || c0 >= y) ? [[x, y]] : [[x, c0], [c1, y]].filter(([p, q]) => q - p > 0.05));
  }
  keep = keep.sort((p, q) => p[0] - q[0]).reduce((acc, s) => { const l = acc[acc.length - 1]; if (l && s[0] <= l[1] + 0.02) l[1] = Math.max(l[1], s[1]); else acc.push([...s]); return acc; }, []);
  // a última palavra costuma morrer abaixo do limiar de silêncio e era cortada no meio ("torto", 16/10):
  // o último trecho vai até o fim da última palavra + 0.5s, ou até o fim do bruto
  if (keep.length) { const ult = vivos.flatMap((b) => b.w).pop(); if (ult) keep[keep.length - 1][1] = Math.min(dur, Math.max(keep[keep.length - 1][1], ult.e + 0.5)); }
  const total = keep.reduce((s, [x, y]) => s + y - x, 0);
  const off = []; let acc = 0; for (const [x, y] of keep) { off.push(acc); acc += y - x; }
  const map = (t) => { for (let i = 0; i < keep.length; i++) { const [x, y] = keep[i]; if (t < x) return off[i]; if (t <= y) return off[i] + t - x; } return acc; };

  // 6. relatório + transcrição no tempo editado
  const ficou = vivos.flatMap((b) => b.w).filter((w) => keep.some(([x, y]) => w.s >= x && w.s < y));
  fs.writeFileSync(path.join(work, "cortes.json"), JSON.stringify({ keep, cortes, gap: GAP, sim: SIM }, null, 1));
  fs.writeFileSync(path.join(work, "palavras-editado.json"), JSON.stringify(ficou.map((w) => ({ word: w.t, start: +map(w.s).toFixed(3) }))));
  const fmt = (t) => `${Math.floor(t / 60)}:${(t % 60).toFixed(1).padStart(4, "0")}`;
  const rel = [
    `# Limpeza — ${NOME}`, "",
    `**Bruto:** ${fmt(dur)} → **limpo:** ${fmt(total)} (−${(dur - total).toFixed(1)}s) · silêncio > ${GAP}s · semelhança ≥ ${SIM}`, "",
    `## Repetições cortadas (${cortes.length}) — confira se alguma era intencional`, "",
    ...(cortes.length ? cortes.sort((p, q) => p[0] - q[0]).map(([x, y, t, m]) => `- **${fmt(x)}–${fmt(y)}** · ${m}: ~~${t}~~`) : ["- nenhuma"]), "",
    "## Texto que ficou", "", ficou.map((w) => w.t).join(" "), "",
  ].join("\n");
  fs.writeFileSync(path.join(work, "RELATORIO.md"), rel);
  console.log(rel);

  if (!RENDER) return;
  // 7. render (mesmo padrão do cortar.cjs: micro-fade em cada emenda, GOP 30 para o HyperFrames)
  let fc = "";
  keep.forEach(([x, y], i) => {
    fc += `[0:v]trim=${x.toFixed(3)}:${y.toFixed(3)},setpts=PTS-STARTPTS[v${i}];[0:a]atrim=${x.toFixed(3)}:${y.toFixed(3)},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st=${Math.max(0, y - x - 0.025).toFixed(3)}:d=0.025[a${i}];`;
  });
  fc += keep.map((_, i) => `[v${i}][a${i}]`).join("") + `concat=n=${keep.length}:v=1:a=1[v][a]`;
  const script = path.join(work, "filtro.txt");
  fs.writeFileSync(script, fc);
  const saida = path.join(os.homedir(), "Downloads", `${NOME}-limpo.mp4`);
  const r = sh("ffmpeg", ["-v", "error", "-y", "-i", VIDEO, "-filter_complex_script", script, "-map", "[v]", "-map", "[a]",
    "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida]);
  if (r.status !== 0) throw new Error(r.stderr);
  console.log(`\nvídeo limpo: ${saida}`);
})().catch((e) => { console.error("ERRO:", e.message); process.exit(1); });
