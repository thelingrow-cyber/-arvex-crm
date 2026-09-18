// Cindy — criativo de captação Desafio Ótica +100K (IMG_3148.mov). Jump cut (cortar.cjs) 48,6 s → 46,2 s.
// uso: node cortar.cjs · render.ps1 -Nome 2026-09-cindy-captacao-desafio [-Previa -Em ...] · node build.cjs --mix (trilha + SFX no output.mp4)
// Tempos abaixo JÁ NO CORTE (ver saída do cortar.cjs).
const path = require("path");
const fs = require("fs");
const { execFileSync } = require("child_process");
const NOME = path.basename(__dirname);
const work = path.join(__dirname, "../../work", NOME);
const DUR = JSON.parse(fs.readFileSync(path.join(work, "meta.json"), "utf8")).duracao;

// SFX (biblioteca do HyperFrames, assets/sfx) — [arquivo, tempo, volume]
const SFX_DIR = path.join(__dirname, "../../assets/sfx");
const SFX = [
  ...[0.05, 8.02, 13.42, 29.4, 36.95, 38.6, 42.4].map((t) => ["whoosh-short.mp3", t - 0.2, 0.28]),   // cards
  ...[2.5, 17.35, 26.62].map((t) => ["whoosh.mp3", t - 0.15, 0.4]),                                // inserts
  ["impact-bass-1.mp3", 7.01, 0.55], ["impact-bass-1.mp3", 25.95, 0.7], ["impact-bass-2.mp3", 39.51, 0.5],
  ["sparkle.mp3", 26.2, 0.3], ["sparkle.mp3", 22.25, 0.22], ["sparkle.mp3", 39.7, 0.22],
  ...[19.24, 20.52, 22.2, 26.72, 27.1, 27.5].map((t) => ["pop.mp3", t - 0.03, 0.22]),
  ...[8.17, 9.99, 30.92, 31.78, 35.32].map((t) => ["click-soft.mp3", t - 0.02, 0.3]),
  ["whoosh-short.mp3", 37.9, 0.25],                                                                // risco
];
const RISER = { arq: "riser.mp3", fimEm: 24.55, dur: 2.2, vol: 0.35 }; // últimos 2,2 s do riser terminam no título
// trilha: Mixkit "Driving Ambition" (Ahjay Stelino, Mixkit Free License) — pico da faixa (33 s) cai no título
const MUSICA = { arq: path.join(__dirname, "../../assets/musica/mixkit-32.mp3"), inicio: 8.45, vol: 0.11 };
const MUDO = [12.05, 13.4]; // trilha some no "cansativo"
const RESPIRO = [23.7, 24.55]; // trilha recua sob o riser e volta cheia no título

if (process.argv.includes("--mix")) { mix(); return; }

const V = require("../../lib.cjs").criar({ dur: DUR });
const FACE = { faceX: 540, faceY: 560 };

// ── câmera: escala muda a cada frase (corte com zoom); ênfases entram mais fechadas ──
V.camera([
  [0, 1.36, 1.2, 1.08], [1.36, 2.5, 1.0, 1.04],
  [2.5, 8.1, 1.0, 1.0],                               // insert ciclo
  [8.1, 9.27, 1.12, 1.16], [9.27, 12.09, 1.0, 1.06],
  [12.09, 13.42, 1.22, 1.3],                          // "cansativo"
  [13.42, 15.34, 1.0, 1.04], [15.34, 17.35, 1.12, 1.17],
  [17.35, 22.87, 1.0, 1.0],                           // insert etapas
  [22.87, 24.55, 1.14, 1.2],
  [24.55, 29.4, 1.0, 1.0],                            // título + 3 dias
  [29.4, 31.78, 1.0, 1.05], [31.78, 35.32, 1.1, 1.15], [35.32, 36.95, 1.2, 1.25],
  [36.95, 38.63, 1.0, 1.03], [38.63, 39.51, 1.1, 1.12], [39.51, 42.41, 1.22, 1.28],
  [42.41, DUR, 1.0, 1.08],
]);
V.shake([13.06, 36.55, 39.51]);
V.filtro(12.09, 13.42);
V.corteSuave([1.36, 8.1, 9.27, 13.42, 15.34, 22.87, 29.4, 31.78, 35.32, 36.95, 38.63, 39.51, 42.41]);

// ── gancho → ciclo do mês que volta a zero ──
V.cardTitulo("c0", 0.05, 2.45, { kicker: "TODO MÊS É ASSIM", titulo: "NA SUA", gold: "ÓTICA?", tituloAt: 1.7, goldAt: 2.14 });
V.insertCiclo({ start: 2.5, end: 8.1, kicker: "TODO MÊS...", ate: 30, zeroAt: 7.01, rodape: "ESTACA ZERO", ...FACE });

V.cardLista("c1", 8.02, 11.95, {
  kicker: "DE NOVO...",
  itens: [["CORRER ATRÁS", 8.17], ["ESPERAR O MOVIMENTO", 9.99]],
});
V.cardTitulo("c2", 13.42, 17.3, { kicker: "QUEM QUER CRESCER DE VERDADE", titulo: "NÃO", gold: "ESPERA", tituloAt: 15.42, goldAt: 15.78 });

V.insertEtapas({ start: 17.35, end: 22.87, kicker: "UMA FORMA CONSTANTE DE", etapas: [["ATRAIR", 19.24], ["DESEJO", 20.52], ["VENDAS", 22.2]], ...FACE });

V.insertTitulo({ start: 24.55, end: 26.62, kicker: "3 DIAS · 22 A 24 DE SETEMBRO", linhas: [["DESAFIO", 24.79], ["ÓTICA", 25.31], ["+100K", 25.95]] });
V.insertCirculo({
  start: 26.62, end: 29.4, kicker: "EM 3 DIAS",
  blocos: [["22", 26.72], ["23", 27.1], ["24", 27.5]],
  rodape: "UM NOVO JOGO", rodapeAt: 28.84, ...FACE,
});

V.cardLista("c3", 29.4, 36.9, {
  kicker: "O JOGO DAS ÓTICAS QUE",
  itens: [["GERAM DESEJO", 30.92], ["SE DIFERENCIAM", 31.78], ["VENDEM ANTES DO PREÇO", 35.32]],
});
V.cardContraste("c4", 36.95, 42.3, { k1: "NÃO É SOBRE", t1: "TRABALHAR MAIS", t1At: 37.4, riscoAt: 37.95, virarAt: 38.6, k2: "É SOBRE", t2: "CONSTRUIR", t2At: 39.51 });
V.cardCTA("c5", 42.4, { kicker: "GARANTA SEU PASSAPORTE", texto: "CLIQUE NO LINK", popAt: 42.9 });

V.flash([2.5, 7.01, 17.35, 24.55, 25.95, 29.4, 39.51, 42.4]);

// ── legenda: some durante o título em tela cheia; corrige "esse estaca" ──
const leg = JSON.parse(fs.readFileSync(path.join(work, "legenda.json"), "utf8"))
  .map((g) => g.map(([w, t]) => [w === "esse" ? "essa" : w, t]).filter(([, t]) => t < 24.55 || t >= 26.62))
  .filter((g) => g.length);
V.legendaDinamica(leg, { destaques: ["zero", "cansativo", "desejo", "vendas", "jogo", "preço", "construir", "link", "passaporte"] });
V.salvar(process.argv[2] || path.join(work, "public/index.html"));

// ── trilha gerada (sem direitos) + SFX, mixados sobre o render ──
function mix() {
  const ff = (args) => execFileSync("ffmpeg", ["-v", "error", "-y", ...args], { cwd: work, stdio: "inherit" });
  const riserDur = parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path.join(SFX_DIR, RISER.arq)]).toString());
  const env = `(1-0.97*between(t,${MUDO[0]},${MUDO[1]}))*(1-0.55*between(t,${RESPIRO[0]},${RESPIRO[1]}))`;
  const ins = ["-i", "output.mp4", "-ss", String(MUSICA.inicio), "-i", MUSICA.arq];
  let fc = "[0:a]asplit[vk][vsc];" +
    `[1:a]atrim=0:${DUR},asetpts=PTS-STARTPTS,aresample=48000,volume=${MUSICA.vol},volume='${env}':eval=frame,afade=t=in:d=0.8,afade=t=out:st=${(DUR - 1.6).toFixed(2)}:d=1.6[mu];` +
    "[mu][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=500[md];";
  const fx = [];
  const addFx = (file, t, vol, extra = "") => {
    ins.push("-i", path.join(SFX_DIR, file));
    const i = ins.filter((x) => x === "-i").length - 1, ms = Math.max(0, Math.round(t * 1000)), k = `f${i}`;
    fc += `[${i}:a]aresample=48000,${extra}volume=${vol},adelay=${ms}|${ms}[${k}];`; fx.push(`[${k}]`);
  };
  SFX.forEach(([f, t, v]) => addFx(f, t, v));
  addFx(RISER.arq, RISER.fimEm - RISER.dur, RISER.vol, `atrim=${(riserDur - RISER.dur).toFixed(2)},asetpts=PTS-STARTPTS,afade=t=in:d=0.6,`);
  fc += `[vk][md]${fx.join("")}amix=inputs=${2 + fx.length}:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.9[a]`;
  fs.writeFileSync(path.join(work, "mix-filtro.txt"), fc);
  const saida = path.join(process.env.USERPROFILE, "Downloads", `${NOME}.mp4`);
  ff([...ins, "-filter_complex_script", "mix-filtro.txt", "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida]);
  console.log("final:", saida);
}
