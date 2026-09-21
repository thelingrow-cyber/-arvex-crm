// Falta 1 dia (Cindy) — narração à parte + B-roll da ótica. Este script: limpa o áudio (tirando as
// repetições da gravação), monta o B-roll 9:16 (moldura 4:5 sobre o próprio take desfocado, com ken burns),
// junta com a narração e transcreve o áudio limpo para a legenda.
// uso: node preparar.cjs  [--so-audio]
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const NOME = path.basename(__dirname);
const raiz = path.join(__dirname, "../..");
const work = path.join(raiz, "work", NOME);
const pub = path.join(work, "public");
const DL = path.join(process.env.USERPROFILE, "Downloads");
const ORIG = path.join(DL, "WhatsApp Audio 2026-09-21 at 14.27.22.mp4");
const ff = (args) => execFileSync("ffmpeg", ["-v", "error", "-y", ...args], { cwd: work, stdio: "inherit" });
fs.mkdirSync(path.join(pub, "fonts"), { recursive: true });
fs.mkdirSync(path.join(pub, "vendor"), { recursive: true });

// ── 1. narração limpa: fora as repetições e as falsas partidas ──
const VOZ = [
  [2.38, 40.02],   // abertura → "…as óticas das edições anteriores aplicaram"
  [47.62, 55.21],  // "o aviso final: estamos nas últimas vagas… porque amanhã já começa"
  [55.58, 60.60],  // "enquanto ele estiver aberto… depois disso, acabou"
  [60.97, 65.25],  // "o link está aqui embaixo… entra para esse desafio"
  [71.45, 72.85],  // "te vejo amanhã"
];
let fc = VOZ.map(([a, b], i) => `[0:a]atrim=${a}:${b},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st=${(b - a - 0.05).toFixed(2)}:d=0.05[a${i}];`).join("");
fc += VOZ.map((_, i) => `[a${i}]`).join("") + `concat=n=${VOZ.length}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11,highpass=f=90[out]`;
ff(["-i", ORIG, "-filter_complex", fc, "-map", "[out]", "-c:a", "pcm_s16le", "voz.wav"]);
const DUR = +parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path.join(work, "voz.wav")]).toString()).toFixed(2);
console.log(`narração limpa: ${DUR}s (original 74s)`);

// ── 2. B-roll: [arquivo, início, duração, tom] — tom frio no bloco do problema, quente depois ──
const FRIO = "hqdn3d=1.5:1.5:5:5,eq=contrast=1.05:saturation=0.55:gamma=0.95,colorbalance=rs=-0.04:bs=0.06,curves=all='0/0.03 0.5/0.47 1/0.95'";
const QUENTE = "hqdn3d=1.2:1.2:4:4,eq=contrast=1.1:saturation=1.16:gamma=0.98,colorbalance=rs=0.04:gs=0.01:bs=-0.03,curves=all='0/0.02 0.5/0.5 1/0.98'";
// cortes colados na fala (tempos do voz.wav — ver transcricao.json)
const CENAS = [
  ["IMG_4928.MOV", 1.0, 5.76, "frio"],   // 0.00 loja ampla — "menos de 10 dias até outubro"
  ["IMG_4930.MOV", 1.5, 4.44, "frio"],   // 5.76 armações — "posicionamento, oferta, plano na mão"
  ["IMG_4929.MOV", 0.8, 3.24, "frio"],   // 10.20 loja parada — "improvisando de novo"
  ["IMG_4931.MOV", 2.0, 2.86, "quente"], // 13.44 VIRADA — "o Desafio começa amanhã"
  ["IMG_4934.MOV", 0.8, 3.70, "quente"], // 16.30 ela trabalhando — "3 dias ao vivo comigo"
  ["IMG_4937.MOV", 2.0, 3.00, "quente"], // 20.00 atendimento — "não é aula solta"
  ["IMG_4930.MOV", 7.0, 3.30, "quente"], // 23.00 armações — "definir o seu posicionamento"
  ["IMG_4935.MOV", 6.0, 3.98, "quente"], // 26.30 balcão — "oferta e estratégia de vendas"
  ["IMG_4934.MOV", 3.0, 3.88, "quente"], // 30.28 ela trabalhando — "pronto pra executar na segunda"
  ["IMG_4928.MOV", 12.0, 3.44, "quente"],// 34.16 loja com gente — PROVAS por cima
  ["IMG_4937.MOV", 8.5, 3.90, "quente"], // 37.60 urgência — "o aviso final"
  ["IMG_4935.MOV", 22.0, 3.70, "quente"],// 41.50 urgência — "o lote fecha em poucas horas"
  ["IMG_4928.MOV", 16.0, 5.00, "quente"],// 45.20 "enquanto ele estiver aberto"
  ["IMG_4931.MOV", 8.0, 5.80, "quente"], // 50.20 CTA — "o link está aqui embaixo"
];
if (process.argv.includes("--so-audio")) return;

// moldura 4:5 sobre o próprio take desfocado (os takes são horizontais) + ken burns lento
const seg = path.join(work, "seg");
fs.mkdirSync(seg, { recursive: true });
CENAS.forEach(([arq, ini, dur, tom], i) => {
  const cor = tom === "frio" ? FRIO : QUENTE;
  // ken burns: a moldura 4:5 aproxima (pares) ou afasta (ímpares) 7% ao longo da cena
  // os takes já são verticais (rotação -90 nos metadados) → tela cheia, sem moldura
  // ken burns: aproxima (pares) ou afasta (ímpares) 8%. ⚠️ usar n (quadro), não t — t vem NaN aqui
  const q = Math.round(dur * 30);
  const larg = i % 2 ? `1080*(1.09-0.08*n/${q})` : `1080*(1.01+0.08*n/${q})`;
  const vf =
    `[0:v]fps=30,${cor},scale=w='2*trunc(${larg}/2)':h=-2:eval=frame:flags=bicubic,` +
    `crop=1080:1920:(iw-1080)/2:(ih-1920)/2,setsar=1`;
  ff(["-ss", String(ini), "-t", String(dur), "-i", path.join(DL, arq), "-an", "-filter_complex", vf,
    "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p", path.join(seg, `s${i}.mp4`)]);
  console.log(`cena ${i + 1}/${CENAS.length}: ${arq}`);
});

// ── 3. concat + narração → input-video.mp4 ──
const lista = path.join(work, "lista.txt");
fs.writeFileSync(lista, CENAS.map((_, i) => `file '${path.join(seg, `s${i}.mp4`).replace(/\\/g, "/")}'`).join("\n"), "utf8");
ff(["-f", "concat", "-safe", "0", "-i", lista, "-i", path.join(work, "voz.wav"),
  "-map", "0:v", "-map", "1:a", "-shortest", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
  "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", path.join(pub, "input-video.mp4")]);

// assets do renderer + folha de contato
for (const f of fs.readdirSync(path.join(raiz, "assets/fonts"))) fs.copyFileSync(path.join(raiz, "assets/fonts", f), path.join(pub, "fonts", f));
fs.copyFileSync(path.join(raiz, "assets/vendor/gsap.min.js"), path.join(pub, "vendor/gsap.min.js"));
const durFinal = parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path.join(pub, "input-video.mp4")]).toString());
fs.writeFileSync(path.join(work, "meta.json"), JSON.stringify({ duracao: +durFinal.toFixed(2), cenas: CENAS.map(([a, , d]) => [a, d]) }));
ff(["-i", path.join(pub, "input-video.mp4"), "-vf", "fps=1/4,scale=180:-1,tile=6x3", "-frames:v", "1", "contato.jpg"]);
console.log(`input-video.mp4: ${durFinal.toFixed(2)}s · folha: ${path.join(work, "contato.jpg")}`);
