// B20 "O celular no balcão" (Cindy, Black Recorde): voz PRO + B-roll com cor viva + mosaico e pilha de vídeos.
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
const FRIO = "hqdn3d=1.2:1.2:4:4,eq=contrast=1.05:saturation=0.82:gamma=0.97,colorbalance=rs=-0.02:bs=0.04,unsharp=5:5:0.4";
const QUENTE = "hqdn3d=1.2:1.2:4:4,eq=contrast=1.07:saturation=1.2:gamma=0.98,colorbalance=rs=0.03:gs=0.01:bs=-0.02:rm=0.02,curves=all='0/0.02 0.5/0.51 1/0.98',unsharp=5:5:0.45";
// cortes colados na fala (tempos do voz.wav — ver transcricao.json)
// cenas ancoradas na fala: [arquivo, início no take, frase onde o corte entra, tom]
const A = require("../../ancora.cjs")(work);
const LEN = (a) => +execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path.join(DL, a)]).toString();
const BASE = [
  ["IMG_4935.MOV", 2, null, "quente"],             // balcão: o celular gira por cima
  ["IMG_4928.MOV", 12, "se a resposta", "quente"], // loja com gente: o preço cai no celular
  ["IMG_4928.MOV", 16, "e no fim do dia", "frio"], // loja cheia, sem cor: a margem ficou na porta
  ["IMG_4934.MOV", 0.3, "eu já caí", "frio"],      // a Cindy
  ["IMG_4937.MOV", 2, "o que mudou", "quente"],    // virada (pilha de vídeos por cima)
  ["IMG_4935.MOV", 14, "isso se monta", "quente"],
  ["IMG_4935.MOV", 4, "nesse exato", "quente"],    // volta ao balcão do gancho
  ["IMG_4928.MOV", 1, "é isso que", "quente"],     // sob o insert do evento
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

// ── 4. extras: mosaico 3x3 (fundo do evento) e pilha de 3 vídeos (virada) ──
const EVD = +(A.fim("sessenta dias do ano") - A.at("na operação") + 1.2).toFixed(2);
const MOS = [["IMG_4928.MOV", 3], ["IMG_3043.MOV", 12], ["IMG_4930.MOV", 4], ["IMG_4937.MOV", 6], ["IMG_4935.MOV", 30], ["IMG_3101.mov", 10], ["IMG_4929.MOV", 1], ["IMG_3148.mov", 8], ["IMG_4934.MOV", 1]];
ff([...MOS.flatMap(([a, ini]) => ["-ss", String(ini), "-t", String(EVD), "-i", path.join(DL, a)]), "-an", "-filter_complex",
  MOS.map((_, i) => `[${i}:v]fps=30,scale=360:640:force_original_aspect_ratio=increase,crop=360:640,eq=saturation=1.1,setsar=1[m${i}]`).join(";") + ";" +
  MOS.map((_, i) => `[m${i}]`).join("") + "xstack=inputs=9:layout=0_0|360_0|720_0|0_640|360_640|720_640|0_1280|360_1280|720_1280[v]",
  "-map", "[v]", "-t", String(EVD), "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p", path.join(pub, "mosaico.mp4")]);
const PD = +(A.at("isso se monta") - A.at("o que mudou") + 0.4).toFixed(2);
[["IMG_3148.mov", 5], ["IMG_4937.MOV", 8], ["IMG_4935.MOV", 40]].forEach(([a, ini], i) =>
  ff(["-ss", String(ini), "-t", String(PD), "-i", path.join(DL, a), "-an", "-vf", `fps=30,${QUENTE},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1`,
    "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", path.join(pub, `pilha${i}.mp4`)]));
fs.rmSync(path.join(pub, "input-blur.mp4"), { force: true }); // o desfoque é do vídeo novo

// assets do renderer + folha de contato
for (const f of fs.readdirSync(path.join(raiz, "assets/fonts"))) fs.copyFileSync(path.join(raiz, "assets/fonts", f), path.join(pub, "fonts", f));
fs.copyFileSync(path.join(raiz, "assets/vendor/gsap.min.js"), path.join(pub, "vendor/gsap.min.js"));
const durFinal = parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path.join(pub, "input-video.mp4")]).toString());
fs.writeFileSync(path.join(work, "meta.json"), JSON.stringify({ duracao: +durFinal.toFixed(2), cenas: CENAS.map(([a, , d]) => [a, d]) }));
ff(["-i", path.join(pub, "input-video.mp4"), "-vf", "fps=1/4,scale=180:-1,tile=6x3", "-frames:v", "1", "contato.jpg"]);
console.log(`input-video.mp4: ${durFinal.toFixed(2)}s · folha: ${path.join(work, "contato.jpg")}`);
