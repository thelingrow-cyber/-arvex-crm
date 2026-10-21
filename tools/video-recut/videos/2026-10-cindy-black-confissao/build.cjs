// Cindy — Black Recorde, confissão (narração do clone + B-roll da ótica). Receita do 2026-09-cindy-falta-1-dia.
// Fluxo: node tts.cjs → node preparar.cjs → render.ps1 -Nome 2026-10-cindy-black-confissao [-Previa] → node build.cjs --mix
const path = require("path");
const fs = require("fs");
const { execFileSync } = require("child_process");
const NOME = path.basename(__dirname);
const work = path.join(__dirname, "../../work", NOME);
const DUR = JSON.parse(fs.readFileSync(path.join(work, "meta.json"), "utf8")).duracao;

const CORTES = [3.15, 7.85, 11.45, 14.35, 18.4, 22.35, 24.9, 30.95, 34.75];
const SFX_DIR = path.join(__dirname, "../../assets/sfx");
const SFX = [
  ...[0.2, 3.3, 7.95, 11.55, 18.45, 22.45, 25.0, 31.0, 34.8].map((t) => ["whoosh-short.mp3", t - 0.2, 0.26]),
  ["whoosh.mp3", 14.25, 0.38],
  ["impact-bass-1.mp3", 14.4, 0.55], ["impact-bass-2.mp3", 10.97, 0.35],
  ["sparkle.mp3", 24.27, 0.25], ["sparkle.mp3", 33.18, 0.2],
  ...[18.56, 19.62].map((t) => ["click-soft.mp3", t - 0.02, 0.26]),
];
const RISER = { arq: "riser.mp3", fimEm: 14.4, dur: 2.4, vol: 0.3 };
const MUSICA = { arq: path.join(__dirname, "../../assets/musica/mixkit-32.mp3"), inicio: 20.5, vol: 0.11 };
const RESPIRO = [13.5, 14.35];

if (process.argv.includes("--mix")) { mix(); return; }

const V = require("../../lib.cjs").criar({ dur: DUR });
V.corteSuave(CORTES);
V.flash([14.35, 24.9, 34.75]);
V.shake([14.4], { forca: 12 });

// ── bloco 1: a confissão (frio) ──
V.cardTitulo("c0", 0.2, 3.0, { kicker: "EU JÁ FUI ESSA ÓTICA", titulo: "QUE BAIXA", gold: "TUDO", tituloAt: 1.5, goldAt: 1.92 });
V.cardTitulo("c1", 3.3, 7.7, { kicker: "NA BLACK, O DESCONTO", titulo: "IGUAL AO", gold: "VIZINHO", tituloAt: 3.6, goldAt: 4.23 });
V.cardTitulo("c2", 7.95, 11.3, { kicker: "A LOJA ATÉ ENCHIA", titulo: "MAS SOBRAVA", gold: "POUCO", tituloAt: 9.54, goldAt: 10.97 });
V.cardTitulo("c3", 11.55, 14.2, { kicker: "NO PREÇO, A ÓTICA", titulo: "NÃO GANHA DO", gold: "SITE", tituloAt: 13.45, goldAt: 14.02 });

// ── bloco 2: a virada ──
V.insertTitulo({ start: 14.4, end: 17.4, kicker: "O QUE MUDOU", linhas: [["PLANEJAR", 15.86], ["A BLACK", 16.57], ["ANTES", 16.99]] });
V.cardLista("c4", 18.45, 22.2, { kicker: "ANTES DE NOVEMBRO", itens: [["OFERTA PRONTA", 18.56], ["EQUIPE PREPARADA", 19.62]] });
V.cardTitulo("c5", 22.45, 24.8, { kicker: "E AÍ VIERAM", titulo: "AS MELHORES", gold: "BLACKS", tituloAt: 23.55, goldAt: 24.27 });

// ── bloco 3: o convite ──
V.cardTitulo("c6", 25.0, 30.8, { kicker: "WORKSHOP OPERAÇÃO BLACK RECORDE", titulo: "27/10 · AO VIVO ·", gold: "20H", tituloAt: 25.29, goldAt: 26.28 });
V.cardTitulo("c7", 31.0, 34.6, { kicker: "PRA VOCÊ BUSCAR O SEU RECORDE", titulo: "NOS ÚLTIMOS", gold: "60 DIAS", tituloAt: 32.83, goldAt: 33.18 });
V.cardCTA("c8", 34.8, { kicker: "GRATUITO · VAGAS NO GRUPO", texto: "ENTRE NO GRUPO VIP", popAt: 35.99 });

const leg = JSON.parse(fs.readFileSync(path.join(work, "legenda.json"), "utf8"))
  .map((g) => g.filter(([, t]) => t < 14.4 || t >= 17.4))
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
