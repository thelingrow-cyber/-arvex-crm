// Cindy — "falta 1 dia" para os grupos (narração à parte + B-roll da ótica). Conceito: frio/parado → virada → urgência.
// Fluxo: node preparar.cjs → render.ps1 -Nome 2026-09-cindy-falta-1-dia [-Previa] → node build.cjs --mix
// Tempos = tempos da narração limpa (work/…/transcricao.json).
const path = require("path");
const fs = require("fs");
const { execFileSync } = require("child_process");
const NOME = path.basename(__dirname);
const work = path.join(__dirname, "../../work", NOME);
const DUR = JSON.parse(fs.readFileSync(path.join(work, "meta.json"), "utf8")).duracao;

const CORTES = [5.76, 10.2, 13.44, 16.3, 20.0, 23.0, 26.3, 30.28, 34.16, 37.6, 41.5, 45.2, 50.2];
const SFX_DIR = path.join(__dirname, "../../assets/sfx");
const SFX = [
  ...[0.2, 5.9, 10.4, 16.4, 20.2, 30.4, 37.7, 41.6, 45.4, 50.3].map((t) => ["whoosh-short.mp3", t - 0.2, 0.26]), // cards
  ...[13.5, 34.05].map((t) => ["whoosh.mp3", t - 0.15, 0.38]),                                                  // inserts
  ["impact-bass-1.mp3", 14.5, 0.62], ["impact-bass-2.mp3", 44.78, 0.45], ["impact-bass-1.mp3", 13.44, 0.35],
  ["sparkle.mp3", 14.8, 0.28], ["sparkle.mp3", 34.7, 0.2], ["sparkle.mp3", 48.2, 0.2],
  ...[6.78, 7.96, 9.16, 23.02, 24.76, 26.38, 27.98].map((t) => ["click-soft.mp3", t - 0.02, 0.26]),             // itens de lista
  ...[35.85, 37.0].map((t) => ["pop.mp3", t - 0.03, 0.2]),                                                      // provas passando
];
const RISER = { arq: "riser.mp3", fimEm: 13.5, dur: 2.4, vol: 0.32 };
const MUSICA = { arq: path.join(__dirname, "../../assets/musica/mixkit-32.mp3"), inicio: 19.5, vol: 0.11 }; // pico da faixa cai na virada
const RESPIRO = [12.6, 13.44]; // trilha recua sob o riser e volta cheia na virada

if (process.argv.includes("--mix")) { mix(); return; }

const V = require("../../lib.cjs").criar({ dur: DUR });

// o ken burns já vem embutido em cada cena (preparar.cjs) — aqui só a transição de corte
V.corteSuave(CORTES);
V.flash([13.44, 34.16, 37.6, 41.5, 50.2]);
V.shake([14.5, 44.78], { forca: 12 });

// ── bloco 1: o problema (frio) ──
V.cardTitulo("c0", 0.2, 5.5, { kicker: "MENOS DE 10 DIAS ATÉ OUTUBRO", titulo: "O MÊS QUE", gold: "DECIDE", tituloAt: 3.6, goldAt: 4.3 });
V.cardLista("c1", 5.9, 10.0, {
  kicker: "VOCÊ ENTRA EM OUTUBRO COM",
  itens: [["POSICIONAMENTO", 6.78], ["OFERTA MONTADA", 7.96], ["PLANO NA MÃO", 9.16]],
});
V.cardTitulo("c2", 10.4, 13.2, { kicker: "OU ENTRA DE NOVO", titulo: "IMPROVISANDO", tituloAt: 10.66 });

// ── bloco 2: a virada ──
V.insertTitulo({ start: 13.5, end: 16.2, kicker: "COMEÇA AMANHÃ", linhas: [["DESAFIO", 13.58], ["ÓTICA", 14.02], ["+100K", 14.5]] });
V.cardTitulo("c3", 16.4, 19.9, { kicker: "3 DIAS AO VIVO COMIGO", titulo: "22 · 23 · 24", gold: "19H", tituloAt: 18.26, goldAt: 19.4 });
V.cardLista("c4", 20.2, 30.0, {
  kicker: "NESSES 3 DIAS A GENTE VAI",
  itens: [["DEFINIR POSICIONAMENTO", 23.02], ["MONTAR SUA OFERTA", 24.76], ["ESTRATÉGIA DE VENDAS", 26.38], ["PLANO DE OUTUBRO", 27.98]],
});
V.cardTitulo("c5", 30.4, 33.9, { kicker: "VOCÊ SAI COM O PLANO", titulo: "PRONTO PRA", gold: "SEGUNDA", tituloAt: 31.1, goldAt: 33.08 });

// ── bloco 3: a prova (prints reais passando em trilho) ──
V.insertProvas({
  start: 34.05, end: 37.5, kicker: "EDIÇÕES ANTERIORES",
  provas: [
    ["proof-galeria.jpg", "Galeria de Óculos", "De 16k → 63k em outubro", 34.7],
    ["proof-michaella.png", "Michaella", "+R$30k no faturamento", 35.85],
    ["proof-prycia.jpg", "Prycia", "15k só na inauguração", 37.0],
  ],
});

// ── bloco 4: urgência ──
V.cardTitulo("c6", 37.7, 41.3, { kicker: "AGORA O AVISO FINAL", titulo: "ÚLTIMAS", gold: "VAGAS", tituloAt: 39.38, goldAt: 40.24 });
V.cardTitulo("c7", 41.6, 45.1, { kicker: "O LOTE ZERO FECHA", titulo: "EM POUCAS", gold: "HORAS", tituloAt: 42.4, goldAt: 43.08 });
V.cardTitulo("c8", 45.4, 50.0, { kicker: "ENQUANTO ESTIVER ABERTO", titulo: "CONDIÇÃO", gold: "ESPECIAL", tituloAt: 47.88, goldAt: 48.2 });
V.cardCTA("c9", 50.3, { kicker: "GARANTE SUA VAGA NO LOTE ZERO", texto: "CLIQUE NO LINK", popAt: 50.9 });

// ── legenda (some durante o título em tela cheia) ──
const leg = JSON.parse(fs.readFileSync(path.join(work, "legenda.json"), "utf8"))
  .map((g) => g.filter(([, t]) => t < 13.5 || t >= 16.2))
  .filter((g) => g.length);
V.legendaDinamica(leg, { destaques: ["outubro", "trimestre", "improvisando", "amanhã", "vagas", "horas", "zero", "link", "posicionamento", "oferta", "plano"] });
V.salvar(process.argv[2] || path.join(work, "public/index.html"));

// ── trilha + SFX sobre o render ──
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
