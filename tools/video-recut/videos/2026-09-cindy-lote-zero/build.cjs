// Cindy — convite Lote Zero (IMG_3101.mov). Edição só com ffmpeg + ASS (sem HyperFrames), render ~2 min.
// uso: node build.cjs [--previa 5,20,44,48]
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const ORIGEM = 'C:/Users/Vitor Simões/Downloads/IMG_3101.mov';
const WORK = path.resolve(__dirname, '../../work/2026-09-cindy-lote-zero');
const SAIDA = 'C:/Users/Vitor Simões/Downloads/2026-09-cindy-lote-zero.mp4';
const FRZ = 2.4; // congelamento final com o card

// trechos mantidos (s do original) — pausas e o respiro de 2,5 s depois de "trimestre" saem
const SEG = [[0.78, 3.56], [3.98, 8.51], [8.78, 10.26], [10.48, 15.14], [15.50, 26.76], [27.03, 30.16], [30.38, 33.62], [36.13, 42.31], [42.53, 52.30]];
const OFF = []; let acc = 0; for (const [a, b] of SEG) { OFF.push(acc); acc += b - a; }
const F = acc; // fim da fala no vídeo editado
const T = F + FRZ;
const map = (t) => { for (let i = 0; i < SEG.length; i++) { const [a, b] = SEG[i]; if (t < a) return OFF[i]; if (t <= b) return OFF[i] + t - a; } return F; };

const ff = (args) => execFileSync('ffmpeg', ['-v', 'error', '-y', ...args], { cwd: WORK, stdio: 'inherit', env: { ...process.env, FONTCONFIG_FILE: path.join(WORK, 'fonts.conf') } });
fs.mkdirSync(WORK, { recursive: true });
fs.writeFileSync(path.join(WORK, 'fonts.conf'), '<?xml version="1.0"?><fontconfig><dir>C:/Windows/Fonts</dir><cachedir>' + WORK.replace(/\\/g, '/') + '/fc-cache</cachedir></fontconfig>');

// ---------- legenda palavra a palavra ----------
const ts = (s) => { s = Math.max(0, s); const m = Math.floor(s / 60); return `0:${String(m).padStart(2, '0')}:${(s - m * 60).toFixed(2).padStart(5, '0')}`; };
const GOLD = '&H0070B8DD&', NAVY = '&H002E1714&';
const CHAVE = /^(AMANHÃ|8|LOTE|ZERO|VAGAS|\+100K|400|BÔNUS|20|PRIMEIROS|ACABOU|COMPROMETIDO)$/;
const words = JSON.parse(fs.readFileSync(path.join(WORK, 'transcricao.json'), 'utf8')).words
  .map((w) => ({ w: w.word.trim().toUpperCase().replace('100K', '+100K'), s: map(w.start), e: map(w.end), os: w.start, oe: w.end }))
  .filter((w) => w.e - w.s > 0.02 || w.w.length);
const grupos = []; let g = [];
for (const w of words) {
  const len = g.map((x) => x.w).join(' ').length + w.w.length + 1;
  if (g.length && (g.length >= 3 || len > 17 || w.os - g[g.length - 1].oe > 0.3)) { grupos.push(g); g = []; }
  g.push(w);
  if (/[,.?!]$/.test(w.w)) { grupos.push(g); g = []; }
}
if (g.length) grupos.push(g);

let ev = '';
grupos.forEach((gr, gi) => {
  const fimGrupo = Math.min(gr[gr.length - 1].e + 0.3, gi + 1 < grupos.length ? grupos[gi + 1][0].s : F);
  gr.forEach((w, wi) => {
    const ini = w.s;
    const fim = wi + 1 < gr.length ? gr[wi + 1].s : fimGrupo;
    if (fim - ini < 0.01) return;
    const pop = wi === 0 ? '\\fscx82\\fscy82\\t(0,90,\\fscx104\\fscy104)\\t(90,170,\\fscx100\\fscy100)' : '';
    const txt = gr.map((x, xi) => {
      const limpo = x.w.replace(/[,.]$/, '');
      const chave = CHAVE.test(limpo);
      if (xi === wi) return `{\\c${GOLD}\\fscx112\\fscy112}${limpo}{\\r}`;
      return chave ? `{\\c${GOLD}}${limpo}{\\r}` : limpo;
    }).join(' ');
    ev += `Dialogue: 1,${ts(ini)},${ts(fim)},L,,0,0,0,,{\\an5\\pos(540,1395)${pop}}${txt}\n`;
  });
});

// ---------- motions do final ----------
const rect = (w, h) => `m 0 0 l ${w} 0 ${w} ${h} 0 ${h}`;
function card(ini, fim, kicker, titulo) {
  const d = Math.round((fim - ini) * 1000);
  const y = 250;
  ev += `Dialogue: 5,${ts(ini)},${ts(fim)},P,,0,0,0,,{\\an5\\pos(540,${y})\\1c${NAVY}\\1a&H18&\\fscx0\\t(0,240,0.5,\\fscx100)\\fad(0,200)\\p1}${rect(800, 190)}{\\p0}\n`;
  ev += `Dialogue: 6,${ts(ini)},${ts(fim)},P,,0,0,0,,{\\an5\\pos(540,${y + 92})\\1c${GOLD}\\fscx0\\t(200,520,0.5,\\fscx100)\\fad(0,200)\\p1}${rect(800, 8)}{\\p0}\n`;
  ev += `Dialogue: 7,${ts(ini + 0.14)},${ts(fim)},K,,0,0,0,,{\\an5\\move(540,${y - 28},540,${y - 48},0,260)\\alpha&HFF&\\t(0,260,\\alpha&H00&)\\fad(0,200)}${kicker}\n`;
  ev += `Dialogue: 7,${ts(ini + 0.24)},${ts(fim)},C,,0,0,0,,{\\an5\\move(540,${y + 50},540,${y + 22},0,300)\\alpha&HFF&\\t(0,300,\\alpha&H00&)\\fscx92\\fscy92\\t(0,300,\\fscx100\\fscy100)\\t(${d - 240},${d},\\alpha&HFF&)}${titulo}\n`;
}
const flash = (t, forte) => { ev += `Dialogue: 9,${ts(t)},${ts(t + 0.35)},P,,0,0,0,,{\\an7\\pos(0,0)\\1c&HFFFFFF&\\1a&H${forte ? '40' : '90'}&\\t(0,350,\\1a&HFF&)\\p1}${rect(1080, 1920)}{\\p0}\n`; };

card(map(38.20), map(40.45), 'LOTE ZERO', 'AMANHÃ ÀS 8H');
flash(map(42.62), false); // "acabou"
card(map(44.32), map(47.70), 'SÓ PARA OS 20 PRIMEIROS', 'BÔNUS ESPECIAL');
// congelamento: escurece, flash, "LOTE ZERO" abre o espaçamento, "AMANHÃ · 8H" entra
ev += `Dialogue: 4,${ts(F)},${ts(T)},P,,0,0,0,,{\\an7\\pos(0,0)\\1c&H000000&\\1a&HFF&\\t(0,500,\\1a&H70&)\\p1}${rect(1080, 1920)}{\\p0}\n`;
flash(F, true);
ev += `Dialogue: 8,${ts(F + 0.12)},${ts(T)},G,,0,0,0,,{\\an5\\pos(540,1240)\\fsp40\\alpha&HFF&\\t(0,260,\\alpha&H00&)\\t(0,${Math.round(FRZ * 1000)},0.4,\\fsp8)}LOTE ZERO\n`;
ev += `Dialogue: 8,${ts(F + 0.5)},${ts(T)},C,,0,0,0,,{\\an5\\move(540,1390,540,1365,0,300)\\alpha&HFF&\\t(0,300,\\alpha&H00&)}AMANHÃ · 8H\n`;
ev += `Dialogue: 8,${ts(F + 0.95)},${ts(T)},K,,0,0,0,,{\\an5\\pos(540,1460)\\alpha&HFF&\\t(0,300,\\alpha&H00&)}VAGAS LIMITADAS\n`;

const head = ['[Script Info]', 'ScriptType: v4.00+', 'PlayResX: 1080', 'PlayResY: 1920', 'WrapStyle: 2', 'ScaledBorderAndShadow: yes', '',
  '[V4+ Styles]',
  'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
  'Style: L,Segoe UI Black,76,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,5,3,5,40,40,0,1',
  'Style: P,Segoe UI,20,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1',
  `Style: K,Segoe UI Black,34,${GOLD.slice(0, -1)},&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,6,0,1,0,0,5,0,0,0,1`,
  'Style: C,Segoe UI Black,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,0,3,5,0,0,0,1',
  `Style: G,Segoe UI Black,128,${GOLD.slice(0, -1)},&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,8,0,1,0,4,5,0,0,0,1`, '',
  '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text', ''].join('\n');
fs.writeFileSync(path.join(WORK, 'cap.ass'), '\ufeff' + head + ev);

// ---------- trilha de antecipação (gerada, sem direitos) ----------
const R = 7; // riser nos últimos 7 s de fala
const expr = [
  // drone grave desafinado com respiração lenta
  `(0.30*sin(2*PI*55*t)+0.22*sin(2*PI*55.35*t)+0.15*sin(2*PI*82.41*t)+0.09*sin(2*PI*110.2*t))*(0.8+0.2*sin(2*PI*0.2*t))*(1-0.85*clip((t-${F})/${FRZ},0,1))`,
  // batimento (dupla batida, 70 bpm) que cresce nos últimos 16 s
  `st(0,mod(t,0.857));(sin(2*PI*52*ld(0))*exp(-14*ld(0))+0.6*gte(ld(0),0.2)*sin(2*PI*52*(ld(0)-0.2))*exp(-14*(ld(0)-0.2)))*(0.30+0.70*clip((t-${F - 16})/14,0,1))*lt(t,${F})`,
  // tique de relógio (colcheias) entrando aos poucos
  `st(1,mod(t,0.4285));0.10*sin(2*PI*1900*ld(1))*exp(-90*ld(1))*clip((t-${F - 14})/6,0,1)*lt(t,${F})`,
  // riser senoidal 200→800 Hz
  `st(2,t-${F - R});0.10*sin(2*PI*(200*ld(2)+${(600 / (2 * R)).toFixed(3)}*ld(2)*ld(2)))*pow(clip(ld(2)/${R},0,1),2)*lt(t,${F})`,
  // impacto grave no congelamento
  `st(3,t-${F});0.9*gte(ld(3),0)*sin(2*PI*44*ld(3))*exp(-2.8*ld(3))`,
].map((e) => `(${e})`).join('+');
ff(['-f', 'lavfi', '-i', `aevalsrc=exprs='0.5*(${expr})':s=48000:d=${T.toFixed(2)}`,
  '-f', 'lavfi', '-i', `anoisesrc=color=pink:amplitude=0.25:d=${T.toFixed(2)}:r=48000`,
  '-filter_complex',
  `[0:a]lowpass=f=2600,aecho=0.8:0.5:60:0.25[m];` +
  `[1:a]bandpass=f=1800:width_type=o:w=2,volume='0.02+0.55*pow(clip((t-${F - R})/${R},0,1),3)*lt(t,${F})+0.5*between(t,${F},${F + 0.25})*(1-(t-${F})/0.25)':eval=frame[n];` +
  `[m][n]amix=inputs=2:normalize=0,afade=t=in:d=1.5,afade=t=out:st=${(T - 0.8).toFixed(2)}:d=0.8,pan=stereo|c0=c0|c1=c0[out]`,
  '-map', '[out]', '-c:a', 'pcm_s16le', 'musica.wav']);

// ---------- vídeo ----------
const MUS = 0.55; // volume da trilha sob a voz
const zoom = SEG.map(([a, b], i) => (i % 2 ? `0.075*between(t,${OFF[i].toFixed(3)},${(OFF[i] + b - a).toFixed(3)})` : null)).filter(Boolean).join('+');
const push = `0.13*clip((t-${OFF[8].toFixed(3)})/${(T - OFF[8]).toFixed(3)},0,1)`;
let fc = '';
SEG.forEach(([a, b], i) => {
  const d = (b - a).toFixed(3);
  fc += `[0:v]trim=${a}:${b},setpts=PTS-STARTPTS[v${i}];[0:a]atrim=${a}:${b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st=${(b - a - 0.04).toFixed(3)}:d=0.04[a${i}];`;
});
fc += SEG.map((_, i) => `[v${i}][a${i}]`).join('') + `concat=n=${SEG.length}:v=1:a=1[vc][voz];`;
fc += `[vc]fps=30,tpad=stop_mode=clone:stop_duration=${FRZ},scale=w='2*trunc(540*(1+${zoom}+${push}))':h=-2:eval=frame:flags=bicubic,` +
  `crop=1080:1920:(in_w-1080)/2:(in_h-1920)*0.33,setsar=1,` +
  `eq=contrast=1.06:saturation=1.10:gamma=0.98,vignette=angle=0.38,subtitles=cap.ass,format=yuv420p[vout];`;
fc += `[voz]loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur=${FRZ},asplit[vk][vsc];`;
fc += `[1:a]volume=${MUS}[mus];[mus][vsc]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=450[musd];`;
fc += `[vk][musd]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.92,atrim=0:${T.toFixed(2)}[aout]`;
fs.writeFileSync(path.join(WORK, 'filtro.txt'), fc);

const previa = process.argv.indexOf('--previa');
if (previa > 0) {
  // renderiza só o necessário e tira quadros nos tempos pedidos (tempo do vídeo editado)
  ff(['-i', ORIGEM, '-i', 'musica.wav', '-filter_complex_script', 'filtro.txt', '-map', '[vout]', '-map', '[aout]', '-c:a', 'aac', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28', 'previa.mp4']);
  const at = process.argv[previa + 1].split(',');
  at.forEach((s, i) => ff(['-ss', s, '-i', 'previa.mp4', '-frames:v', '1', '-vf', 'scale=270:-1', `p${i}.png`]));
  ff(['-i', 'p%d.png', '-vf', `tile=${at.length}x1`, '-frames:v', '1', 'previa.jpg']);
  console.log('prévia:', path.join(WORK, 'previa.jpg'));
} else {
  ff(['-i', ORIGEM, '-i', 'musica.wav', '-filter_complex_script', 'filtro.txt', '-map', '[vout]', '-map', '[aout]', '-r', '30',
    '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', SAIDA]);
  console.log('final:', SAIDA);
}
console.log(`fala ${F.toFixed(2)}s + congelamento ${FRZ}s = ${T.toFixed(2)}s · ${grupos.length} grupos de legenda`);
