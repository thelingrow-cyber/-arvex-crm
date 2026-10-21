// Cindy — Black Recorde, confissão (narração do clone + B-roll da ótica). Receita do 2026-09-cindy-falta-1-dia.
// Fluxo: node tts.cjs → node preparar.cjs → render.ps1 -Nome 2026-10-cindy-black-confissao [-Previa] → node build.cjs --mix
const path = require("path");
const fs = require("fs");
const { execFileSync } = require("child_process");
const NOME = path.basename(__dirname);
const work = path.join(__dirname, "../../work", NOME);
const DUR = JSON.parse(fs.readFileSync(path.join(work, "meta.json"), "utf8")).duracao;

const CORTES = [3.31, 8.78, 12.15, 15.44, 20.29, 25.25, 28.72, 35.68, 39.96];
const SFX_DIR = path.join(__dirname, "../../assets/sfx");
const SFX = [
  ...[0.2, 3.51, 8.88, 12.24, 20.38, 25.38, 28.9, 35.69, 40.03].map((t) => ["whoosh-short.mp3", t - 0.2, 0.26]),
  ["whoosh.mp3", 15.35, 0.38],
  ["impact-bass-1.mp3", 15.48, 0.55], ["impact-bass-2.mp3", 11.46, 0.35],
  ["sparkle.mp3", 27.93, 0.25], ["sparkle.mp3", 38.32, 0.2],
  ...[20.51, 22.09].map((t) => ["click-soft.mp3", t - 0.02, 0.26]),
];
const RISER = { arq: "riser.mp3", fimEm: 15.48, dur: 2.4, vol: 0.3 };
const MUSICA = { arq: path.join(__dirname, "../../assets/musica/mixkit-32.mp3"), inicio: 23.09, vol: 0.11 };
const RESPIRO = [14.62, 15.44];

if (process.argv.includes("--mix")) { mix(); return; }

const V = require("../../lib.cjs").criar({ dur: DUR });
V.corteSuave(CORTES);
V.flash([15.44, 28.72, 39.96]);
V.shake([15.48], { forca: 12 });

// ── bloco 1: a confissão (frio) ──
V.cardTitulo("c0", 0.12, 3.12, { kicker: "EU JÁ FUI ESSA ÓTICA", titulo: "QUE BAIXA", gold: "TUDO", tituloAt: 1.7, goldAt: 2.29 });
V.cardTitulo("c1", 3.51, 8.63, { kicker: "NA BLACK, O DESCONTO", titulo: "IGUAL AO", gold: "VIZINHO", tituloAt: 3.84, goldAt: 4.65 });
V.cardTitulo("c2", 8.88, 11.98, { kicker: "A LOJA ATÉ ENCHIA", titulo: "MAS SOBRAVA", gold: "POUCO", tituloAt: 10.02, goldAt: 11.46 });
V.cardTitulo("c3", 12.24, 15.3, { kicker: "NO PREÇO, A ÓTICA", titulo: "NÃO GANHA DO", gold: "SITE", tituloAt: 14.59, goldAt: 15.13 });

// ── bloco 2: a virada ──
V.insertTitulo({ start: 15.48, end: 19.11, kicker: "O QUE MUDOU", linhas: [["PLANEJAR", 17.62], ["A BLACK", 18.22], ["ANTES", 18.59]] });
V.cardLista("c4", 20.38, 25.05, { kicker: "ANTES DE NOVEMBRO", itens: [["OFERTA PRONTA", 20.51], ["EQUIPE PREPARADA", 22.09]] });
V.cardTitulo("c5", 25.38, 28.54, { kicker: "E AÍ VIERAM", titulo: "AS MELHORES", gold: "BLACKS", tituloAt: 27.1, goldAt: 27.93 });

// ── bloco 3: o convite ──
V.cardTitulo("c6", 28.9, 35.57, { kicker: "WORKSHOP OPERAÇÃO BLACK RECORDE", titulo: "27/10 · AO VIVO ·", gold: "20H", tituloAt: 29.34, goldAt: 30.49 });
V.cardTitulo("c7", 35.69, 39.77, { kicker: "PRA VOCÊ BUSCAR O SEU RECORDE", titulo: "NOS ÚLTIMOS", gold: "60 DIAS", tituloAt: 37.94, goldAt: 38.32 });
V.cardCTA("c8", 40.03, { kicker: "GRATUITO · VAGAS NO GRUPO", texto: "ENTRE NO GRUPO VIP", popAt: 41.45 });

const leg = JSON.parse(fs.readFileSync(path.join(work, "legenda.json"), "utf8"))
  .map((g) => g.filter(([, t]) => t < 15.48 || t >= 19.11))
  .filter((g) => g.length);
V.legendaDinamica(leg, { destaques: ["tudo", "vizinho", "pouco", "site", "outubro", "pronta", "melhores", "oito", "recorde", "sessenta", "vip"] });
V.salvar(process.argv[2] || path.join(work, "public/index.html"));

function mix() {
  const ff = (args) => execFileSync("ffmpeg", ["-v", "error", "-y", ...args], { cwd: work, stdio: "inherit" });
  const riserDur = parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path.join(SFX_DIR, RISER.arq)]).toString());
  const env = `(1-0.6*between(t,${RESPIRO[0]},${RESPIRO[1]}))`;
  const ins = ["-i", "output.mp4", "-ss", String(MUSICA.inicio), "-i", MUSICA.arq];
  let fc = "[0:a]asplit[vk][vsc];" +
    `[1:a]atrim=0:${DUR},asetpts=PTS-STARTPTS,aresample=48000,volume=${MUSICA.vol},volume='${env}':eval=frame,afade=t=in:d=1.2,afade=t=out:st=${(DUR - 1.8).toFixed(2)}:d=1.8[mu];` +
    "[mu][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=500[md];";
  const fx = [];
  const addFx = (file, t, vol, extra = "") => {
    ins.push("-i", path.join(SFX_DIR, file));
    const i = ins.filter((x) => x === "-i").length - 1, ms = Math.max(0, Math.round(t * 1000)), k = `f${i}`;
    fc += `[${i}:a]aresample=48000,${extra}volume=${vol},adelay=${ms}|${ms}[${k}];`; fx.push(`[${k}]`);
  };
  SFX.forEach(([f, t, v]) => addFx(f, t, v));
  addFx(RISER.arq, RISER.fimEm - RISER.dur, RISER.vol, `atrim=${(riserDur - RISER.dur).toFixed(2)},asetpts=PTS-STARTPTS,afade=t=in:d=0.8,`);
  fc += `[vk][md]${fx.join("")}amix=inputs=${2 + fx.length}:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.9[a]`;
  fs.writeFileSync(path.join(work, "mix-filtro.txt"), fc);
  const saida = path.join(process.env.USERPROFILE, "Downloads", `${NOME}.mp4`);
  ff([...ins, "-filter_complex_script", "mix-filtro.txt", "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida]);
  console.log("final:", saida);
}
