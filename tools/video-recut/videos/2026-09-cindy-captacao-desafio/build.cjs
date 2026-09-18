// Cindy — criativo de captação Desafio Ótica +100K (IMG_3148.mov). Jump cut (cortar.cjs) 48,6 s → 46,2 s.
// uso: node cortar.cjs · render.ps1 -Nome 2026-09-cindy-captacao-desafio [-Previa -Em ...] · node build.cjs --mix (trilha + SFX no output.mp4)
// Tempos abaixo JÁ NO CORTE (ver saída do cortar.cjs).
const path = require("path");
const fs = require("fs");
const { execFileSync } = require("child_process");
const NOME = path.basename(__dirname);
const work = path.join(__dirname, "../../work", NOME);
const DUR = JSON.parse(fs.readFileSync(path.join(work, "meta.json"), "utf8")).duracao;

// SFX: whoosh nas entradas de motion, hit nos impactos, riser antes do título
const WHOOSH = [2.5, 8.02, 15.3, 17.35, 22.87, 24.55, 26.62, 29.4, 36.95, 38.75, 42.4];
const HIT = [7.01, 13.06, 25.95, 28.84, 39.51];
const RISER = [23.1, 24.55];
const MUDO = [12.05, 13.4]; // trilha some no "cansativo"

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
  const T = DUR.toFixed(2);
  // pad Am–F–C–G (2 s por acorde, fade curto na troca) + kick 120 bpm entrando aos poucos
  const pad = "st(0,floor(mod(t,8)/2));st(1,if(eq(ld(0),0),110,if(eq(ld(0),1),87.31,if(eq(ld(0),2),130.81,98))));st(2,if(eq(ld(0),0),1.2,1.26));" +
    "st(3,min(1,mod(t,2)*10)*min(1,(2-mod(t,2))*10));" +
    "ld(3)*(0.22*sin(2*PI*ld(1)*t)+0.16*sin(2*PI*ld(1)*1.5*t)+0.12*sin(2*PI*ld(1)*ld(2)*2*t)+0.07*sin(2*PI*ld(1)*2.004*t)+0.05*sin(2*PI*ld(1)*3*t))";
  const kick = "st(4,mod(t,0.5));0.55*sin(2*PI*(48*ld(4)+2.2*(1-exp(-38*ld(4)))))*exp(-8*ld(4))*clip((t-2.4)/6,0.25,1)";
  const hat = "st(5,mod(t+0.25,0.5));(random(0)*2-1)*exp(-60*ld(5))*0.35*clip((t-7.5)/4,0,1)";
  const mudo = `(1-between(t,${MUDO[0]},${MUDO[1]}))`;
  ff(["-f", "lavfi", "-i", `aevalsrc=exprs='(${pad})+(${kick})':s=48000:d=${T}`, "-f", "lavfi", "-i", `aevalsrc=exprs='${hat}':s=48000:d=${T}`,
    "-filter_complex", `[0:a]lowpass=f=3000,aecho=0.8:0.4:70:0.2[p];[1:a]highpass=f=7000[h];[p][h]amix=inputs=2:normalize=0,volume='${mudo}':eval=frame,afade=t=in:d=0.6,afade=t=out:st=${(DUR - 1.2).toFixed(2)}:d=1.2,pan=stereo|c0=c0|c1=c0[o]`,
    "-map", "[o]", "musica.wav"]);
  // whoosh (ruído com envelope e varredura) · hit (grave + estalo) · riser
  ff(["-f", "lavfi", "-i", "anoisesrc=color=pink:d=0.55:r=48000", "-af", "highpass=f=500,lowpass=f=7000,volume='sin(PI*pow(t/0.55,0.6))*1.6':eval=frame,pan=stereo|c0=c0|c1=c0", "whoosh.wav"]);
  ff(["-f", "lavfi", "-i", "aevalsrc=exprs='sin(2*PI*(46*t+30*(1-exp(-20*t))))*exp(-5*t)+0.4*(random(0)*2-1)*exp(-80*t)':s=48000:d=0.9", "-af", "pan=stereo|c0=c0|c1=c0", "hit.wav"]);
  const rd = RISER[1] - RISER[0];
  ff(["-f", "lavfi", "-i", `anoisesrc=color=white:d=${rd.toFixed(2)}:r=48000`, "-af", `bandpass=f=2500:width_type=o:w=2,volume='pow(t/${rd.toFixed(2)},2.5)*0.9':eval=frame,pan=stereo|c0=c0|c1=c0`, "riser.wav"]);

  const ins = ["-i", "output.mp4", "-i", "musica.wav"];
  let fc = "[0:a]asplit[vk][vsc];[1:a]volume=0.5[mu];[mu][vsc]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=400[md];";
  const fx = [];
  const addFx = (file, t, vol, k) => { ins.push("-i", file); const i = ins.filter((x) => x === "-i").length - 1; fc += `[${i}:a]volume=${vol},adelay=${Math.round(t * 1000)}|${Math.round(t * 1000)}[${k}];`; fx.push(`[${k}]`); };
  WHOOSH.forEach((t, i) => addFx("whoosh.wav", Math.max(0, t - 0.3), 0.35, `w${i}`));
  HIT.forEach((t, i) => addFx("hit.wav", t, 0.55, `h${i}`));
  addFx("riser.wav", RISER[0], 0.3, "r0");
  fc += `[vk][md]${fx.join("")}amix=inputs=${2 + fx.length}:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.93[a]`;
  fs.writeFileSync(path.join(work, "mix-filtro.txt"), fc);
  const saida = path.join(process.env.USERPROFILE, "Downloads", `${NOME}.mp4`);
  ff([...ins, "-filter_complex_script", "mix-filtro.txt", "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida]);
  console.log("final:", saida);
}
