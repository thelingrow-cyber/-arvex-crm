// Black Recorde (2026-10-cindy-black-numero): narração da voz PRO da Cindy + B-roll da ótica. Cortes ancorados na fala (ancora.cjs).
// uso: node tts.cjs → node preparar.cjs
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const NOME = path.basename(__dirname);
const raiz = path.join(__dirname, "../..");
const work = path.join(raiz, "work", NOME);
const pub = path.join(work, "public");
const DL = path.join(process.env.USERPROFILE, "Downloads");
const ff = (args) => execFileSync("ffmpeg", ["-v", "error", "-y", ...args], { cwd: work, stdio: "inherit" });
fs.mkdirSync(path.join(pub, "fonts"), { recursive: true });
fs.mkdirSync(path.join(pub, "vendor"), { recursive: true });

// ── 1. narração: voz.wav já vem do tts.cjs (clone da Cindy no ElevenLabs) ──
const DUR = +parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path.join(work, "voz.wav")]).toString()).toFixed(2);

// ── 2. B-roll: [arquivo, início, duração, tom] — tom frio no bloco do problema, quente depois ──
const FRIO = "hqdn3d=1.5:1.5:5:5,eq=contrast=1.05:saturation=0.55:gamma=0.95,colorbalance=rs=-0.04:bs=0.06,curves=all='0/0.03 0.5/0.47 1/0.95'";
const QUENTE = "hqdn3d=1.2:1.2:4:4,eq=contrast=1.1:saturation=1.16:gamma=0.98,colorbalance=rs=0.04:gs=0.01:bs=-0.03,curves=all='0/0.02 0.5/0.5 1/0.98'";
// cortes colados na fala (tempos do voz.wav — ver transcricao.json)
// cenas ancoradas na fala: [arquivo, início no take, frase onde o corte entra, tom]
const A = require("../../ancora.cjs")(work);
const LEN = (a) => +execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path.join(DL, a)]).toString();
const BASE = [
  ["IMG_4935.MOV", 20, null, "frio"], // balcão/caixa
  ["IMG_4929.MOV", 1, "esse é o número", "frio"], // vitrine
  ["IMG_4928.MOV", 1, "esquece a ótica", "frio"], // loja ampla
  ["IMG_4928.MOV", 12, "porque fechar", "frio"], // loja com gente
  ["IMG_4935.MOV", 35, "e repetir", "frio"], // balcão
  ["IMG_4934.MOV", 0.3, "eu já passei", "quente"], // a Cindy (virada)
  ["IMG_4937.MOV", 2, "a gente tá no fim", "quente"], // atendimento
  ["IMG_4935.MOV", 45, "na operação", "quente"], // sob o insert
  ["IMG_4928.MOV", 16, "o recorde que", "quente"], // loja cheia
  ["IMG_4931.MOV", 8, "clica em saiba", "quente"], // CTA
];
const T = BASE.map(([, , fr]) => (fr ? +(A.at(fr) - 0.12).toFixed(2) : 0));
const CENAS = BASE.map(([a, ini, , tom], i) => {
  const dur = +((i < BASE.length - 1 ? T[i + 1] : DUR) - T[i]).toFixed(2);
  return [a, Math.max(0, Math.min(ini, LEN(a) - dur - 0.1)), dur, tom];
});
fs.mkdirSync(work, { recursive: true }); fs.writeFileSync(path.join(work, "cortes.json"), JSON.stringify(T.slice(1)));
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
