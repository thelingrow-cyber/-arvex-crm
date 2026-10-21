// Black Recorde — confissão (Cindy): narração do clone + B-roll da ótica. Receita do 2026-09-cindy-falta-1-dia.
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
const CENAS = [
  ["IMG_4929.MOV", 0.5, 3.15, "frio"],   // 0.00 loja parada — "eu já fui essa ótica que baixa tudo"
  ["IMG_4928.MOV", 1.0, 4.70, "frio"],   // 3.15 loja ampla — "desconto igual ao do vizinho, cartaz na porta"
  ["IMG_4928.MOV", 12.0, 3.60, "frio"],  // 7.85 loja com gente — "a loja até enchia… sobrava pouco"
  ["IMG_4930.MOV", 1.5, 2.90, "frio"],   // 11.45 armações — "no preço a ótica não ganha do site"
  ["IMG_4934.MOV", 0.5, 4.05, "quente"], // 14.35 VIRADA, ela trabalhando — "comecei a planejar a Black antes"
  ["IMG_4937.MOV", 2.0, 3.95, "quente"], // 18.40 atendimento — "oferta pronta, equipe sabendo o que falar"
  ["IMG_4928.MOV", 16.0, 2.55, "quente"],// 22.35 loja cheia — "minhas melhores Blacks"
  ["IMG_4935.MOV", 6.0, 6.05, "quente"], // 24.90 balcão — "dia 27, às 8 da noite… passo a passo"
  ["IMG_4930.MOV", 6.0, 3.80, "quente"], // 30.95 armações — "buscar o seu recorde… 60 dias"
  ["IMG_4931.MOV", 8.0, +(DUR - 34.75).toFixed(2), "quente"], // 34.75 CTA
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
