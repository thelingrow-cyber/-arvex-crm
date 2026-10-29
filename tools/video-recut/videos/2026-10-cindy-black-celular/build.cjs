// B20 "O celular no balcão" (Cindy, Black Recorde) — Halbert + diretor de criativo, 22/10.
// Voz PRO natural (sem acelerar). Celular desenhado no editor, pergunta em tela cheia, pilha de vídeos na virada,
// evento em tela cheia com mosaico de 9 vídeos ao fundo. Fluxo: tts.cjs → preparar.cjs → (work) build → render → --mix
const path = require("path");
const fs = require("fs");
const { execFileSync } = require("child_process");
const NOME = path.basename(__dirname);
const work = path.join(__dirname, "../../work", NOME);
const DUR = JSON.parse(fs.readFileSync(path.join(work, "meta.json"), "utf8")).duracao;
const { at, fim } = require("../../ancora.cjs")(work);
const CORTES = JSON.parse(fs.readFileSync(path.join(work, "cortes.json"), "utf8"));
const PERG = { ini: at("o que você responde") - 0.12, fim: at("se a resposta") - 0.05 };
const PIL = { ini: at("o que mudou") - 0.1, fim: at("chegar na black") };
const EV = { ini: at("na operação") - 0.25, fim: fim("sessenta dias do ano") + 0.4 };
const SFX_DIR = path.join(__dirname, "../../assets/sfx");
const SFX = [
  ["whoosh.mp3", 0.15, 0.35],
  ["impact-bass-2.mp3", PERG.ini + 0.05, 0.45],
  ...[at("baixar"), at("compara"), at("baixa de novo")].map((t) => ["impact-bass-2.mp3", t, 0.38]),
  ["impact-bass-1.mp3", at("na porta"), 0.4],
  ...CORTES.filter((t) => t > PERG.fim && (t < EV.ini - 0.3 || t > EV.fim)).map((t) => ["whoosh-short.mp3", t - 0.1, 0.22]),
  ...[0, 1, 2].map((i) => ["click-soft.mp3", PIL.ini + 0.15 + i * 0.16, 0.3]),
  ["whoosh.mp3", PIL.fim - 0.6, 0.3],
  ["sparkle.mp3", at("não tem"), 0.25],
  ["whoosh.mp3", at("balcão") + 0.25, 0.35],
  ["whoosh.mp3", EV.ini - 0.1, 0.4],
  ["impact-bass-1.mp3", at("black recorde"), 0.5], ["impact-bass-1.mp3", at("recorde"), 0.65],
  ["click-soft.mp3", at("dia vinte"), 0.3], ["sparkle.mp3", at("pra você buscar") + 0.2, 0.25],
];
const RISER = { arq: "riser.mp3", fimEm: at("black recorde"), dur: 2.6, vol: 0.32 };
const MUSICA = { arq: path.join(__dirname, "../../assets/musica/mixkit-32.mp3"), inicio: 20.5, vol: 0.1 };
const RESPIRO = [PERG.ini, PERG.fim];

if (process.argv.includes("--mix")) { mix(); return; }

const V = require("../../lib.cjs").criar({ dur: DUR });
V.corteSuave(CORTES.filter((t) => t < EV.ini || t > EV.fim));
V.flash([at("o que mudou") - 0.1]);

// gancho: o celular do cliente vira pra câmera no primeiro quadro
V.celular("cel1", { start: 0, end: at("e no fim do dia") - 0.1, giraAt: 0.12, etiqueta: "-20%",
  degraus: [["-40%", at("baixar")], ["-50%", at("compara")], ["-60%", at("baixa de novo")]] });
// a pergunta, em tela cheia
V.insertTitulo({ start: PERG.ini, end: PERG.fim, linhas: [["O QUE VOCÊ", at("o que você")], ["RESPONDE?", at("responde")]] });
// a dor
V.cardTitulo("c1", at("mas a margem") - 0.1, at("eu já caí") - 0.15, { kicker: "A LOJA ENCHEU, MAS A MARGEM", titulo: "FICOU NA", gold: "PORTA", tituloAt: at("ficou"), goldAt: at("porta") });
// virada: vídeos empilhados
V.pilhaVideos({ start: PIL.ini, end: PIL.fim, srcs: ["pilha0.mp4", "pilha2.mp4", "pilha1.mp4"] });
V.cardTitulo("c2", at("uma oferta") - 0.15, at("isso se monta") - 0.15, { kicker: "UMA OFERTA QUE", titulo: "O SITE", gold: "NÃO TEM", tituloAt: at("uma oferta"), goldAt: at("não tem") });
// volta ao balcão do gancho: agora o celular sai de cena
V.celular("cel2", { start: at("nesse exato") - 0.3, end: EV.ini, giraAt: at("nesse exato") - 0.25, etiqueta: "-60%", empurraAt: at("balcão") + 0.3 });
// pico: o evento, com o mosaico de vídeos ao fundo
V.insertEvento({ start: EV.ini, end: EV.fim, kicker: "WORKSHOP AO VIVO", fundoVideo: "mosaico.mp4",
  selos: ["27/10", "20H", "AO VIVO E GRATUITO"], promessa: "SEU RECORDE NOS ÚLTIMOS", contaAte: 60, sufixo: "DIAS",
  faixa: "OPERAÇÃO BLACK RECORDE • 27/10 • 20H • AO VIVO E GRATUITO",
  t: { nome1: at("black recorde"), nome2: at("recorde"), selos: at("dia vinte"), promessa: at("pra você buscar") } });
V.cardCTA("c8", at("clica") - 0.1, { kicker: "O LINK DA AULA SAI SÓ LÁ", texto: "ENTRE NO GRUPO VIP", popAt: at("grupo vip") });

const leg = JSON.parse(fs.readFileSync(path.join(work, "legenda.json"), "utf8"))
  .map((g) => g.filter(([, t]) => (t < PERG.ini || t >= PERG.fim) && (t < EV.ini || t >= EV.fim)))
  .filter((g) => g.length);
V.legendaDinamica(leg, { destaques: ["celular", "site", "novo", "margem", "porta", "oferta", "outubro", "balcão", "vip"] });
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
