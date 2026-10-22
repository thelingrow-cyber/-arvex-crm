// B17 "Sexta à noite" (Cindy, Black Recorde): voz PRO + B-roll da ótica. Poucos cards; o pico é o insert do evento em tela cheia.
// Fluxo: node tts.cjs → node ../../compactar-pausas.cjs ../../work/<nome> 0.38 1.07 → node preparar.cjs
//        → (na pasta work) node <este> public/index.html → npx hyperframes render public ... → node <este> --mix
const path = require("path");
const fs = require("fs");
const { execFileSync } = require("child_process");
const NOME = path.basename(__dirname);
const work = path.join(__dirname, "../../work", NOME);
const DUR = JSON.parse(fs.readFileSync(path.join(work, "meta.json"), "utf8")).duracao;
const { at, fim } = require("../../ancora.cjs")(work);
const CORTES = JSON.parse(fs.readFileSync(path.join(work, "cortes.json"), "utf8"));
const EV = { ini: at("na operação") - 0.25, fim: fim("sessenta dias do ano") + 0.45 };
const SFX_DIR = path.join(__dirname, "../../assets/sfx");
const SFX = [
  ...CORTES.filter((t) => t < EV.ini - 0.3 || t > EV.fim).map((t) => ["whoosh-short.mp3", t - 0.1, 0.24]),
  ["impact-bass-2.mp3", at("sobrou"), 0.4],
  ["whoosh.mp3", EV.ini - 0.1, 0.4],
  ["impact-bass-1.mp3", at("black recorde"), 0.5], ["impact-bass-1.mp3", at("recorde"), 0.65],
  ["click-soft.mp3", at("dia vinte"), 0.3],
  ["sparkle.mp3", at("você sai") + 0.2, 0.25],
  ["whoosh.mp3", EV.fim - 0.4, 0.3],
];
const RISER = { arq: "riser.mp3", fimEm: at("black recorde"), dur: 2.6, vol: 0.32 };
const MUSICA = { arq: path.join(__dirname, "../../assets/musica/mixkit-32.mp3"), inicio: 20.5, vol: 0.11 };
const RESPIRO = [at("vendeu muito") - 0.2, at("eu já vivi")];

if (process.argv.includes("--mix")) { mix(); return; }

const V = require("../../lib.cjs").criar({ dur: DUR });
V.corteSuave(CORTES.filter((t) => t < EV.ini || t > EV.fim));
V.flash([at("o que mudou") - 0.12]);

// gancho
V.cardTitulo("c0", 0.15, at("gente pedindo") - 0.2, { kicker: "A LOJA CHEIA O DIA INTEIRO", titulo: "SEXTA DE", gold: "BLACK FRIDAY", tituloAt: 0.2, goldAt: at("black") });
// a dor em uma linha
V.cardTitulo("c1", at("vendeu muito") - 0.05, at("eu já vivi") - 0.15, { kicker: "VENDEU MUITO.", titulo: "SOBROU", gold: "POUCO", tituloAt: at("sobrou"), goldAt: at("pouco") });
V.shake([at("pouco")], { forca: 10 });
// a virada
V.cardTitulo("c2", at("o que mudou") - 0.05, at("sabendo o que") - 0.1, { kicker: "O QUE MUDOU", titulo: "A OFERTA MONTADA", gold: "ANTES", tituloAt: at("oferta"), goldAt: at("antes") });
// pico: o evento em tela cheia
V.insertEvento({ start: EV.ini, end: EV.fim, kicker: "WORKSHOP AO VIVO",
  selos: ["27/10", "20H", "AO VIVO E GRATUITO"], promessa: "SEU RECORDE NOS ÚLTIMOS", contaAte: 60, sufixo: "DIAS",
  faixa: "OPERAÇÃO BLACK RECORDE • 27/10 • 20H • AO VIVO E GRATUITO",
  t: { nome1: at("black recorde"), nome2: at("recorde"), selos: at("dia vinte"), promessa: at("você sai") } });
V.cardCTA("c8", at("clica") - 0.1, { kicker: "O LINK SAI SÓ NO GRUPO", texto: "ENTRE NO GRUPO VIP", popAt: at("grupo vip") });

const leg = JSON.parse(fs.readFileSync(path.join(work, "legenda.json"), "utf8"))
  .map((g) => g.filter(([, t]) => t < EV.ini || t >= EV.fim))
  .filter((g) => g.length);
V.legendaDinamica(leg, { destaques: ["cheia", "barata", "nove", "pouco", "margem", "antes", "fora", "sexta", "vip"] });
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
