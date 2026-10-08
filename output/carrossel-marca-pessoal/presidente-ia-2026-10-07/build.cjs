'use strict';

const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage, GlobalFonts } = require('@napi-rs/canvas');

const ROOT = __dirname;
const REPO = path.resolve(ROOT, '../../..');
const OUT = path.join(ROOT, 'slides');
const W = 1080;
const H = 1350;
const M = 72;
const C = {
  ink: '#0E0F12',
  inkSoft: '#181A1E',
  cream: '#F4F0E6',
  gray: '#9C978C',
  gold: '#C9A24B',
  goldSoft: '#E7D4A9',
};

GlobalFonts.registerFromPath(
  path.join(REPO, 'tools/video-recut/videos/2026-09-clovis-galera/Inter.ttf'),
  'Inter Carousel',
);

const assetPaths = {
  face: path.join(REPO, 'tools/video-recut/work/2026-10-presidente-ia/ref-rosto.jpg'),
  faceWide: path.join(REPO, 'tools/video-recut/work/2026-10-presidente-ia/frame02.jpg'),
  airport: path.join(REPO, 'output/midia/2026-10-07/010501-p3-aeroporto.png'),
  solar: path.join(REPO, 'output/midia/2026-10-07/001558-pres-solar.jpg'),
};

function faceText(ctx, text, x, y, size, color = C.cream, weight = 900, align = 'left') {
  ctx.font = `${weight} ${size}px "Inter Carousel"`;
  ctx.fillStyle = color;
  ctx.textAlign = align;
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(text, x, y);
  ctx.textAlign = 'left';
}

function fitText(ctx, text, maxWidth, start, min, weight = 900) {
  for (let size = start; size >= min; size -= 2) {
    ctx.font = `${weight} ${size}px "Inter Carousel"`;
    if (ctx.measureText(text).width <= maxWidth) return size;
  }
  return min;
}

function lines(ctx, items, x, y, size, leading, color = C.cream, weight = 900) {
  items.forEach((item, i) => faceText(ctx, item, x, y + i * leading, size, color, weight));
}

function wrapped(ctx, text, x, y, width, size, leading, color = C.cream, weight = 500) {
  ctx.font = `${weight} ${size}px "Inter Carousel"`;
  const words = text.split(/\s+/);
  const rows = [];
  let current = '';
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (current && ctx.measureText(next).width > width) {
      rows.push(current);
      current = word;
    } else current = next;
  }
  if (current) rows.push(current);
  rows.forEach((row, i) => faceText(ctx, row, x, y + i * leading, size, color, weight));
  return rows.length;
}

function rect(ctx, x, y, w, h, fill) {
  ctx.fillStyle = fill;
  ctx.fillRect(x, y, w, h);
}

function rule(ctx, x1, y1, x2, y2, color = C.gold, width = 2) {
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();
}

function photoCover(ctx, img, x, y, w, h, focusX = 0.5, focusY = 0.5) {
  const source = img.width / img.height;
  const target = w / h;
  let sx = 0, sy = 0, sw = img.width, sh = img.height;
  if (source > target) {
    sw = img.height * target;
    sx = Math.max(0, Math.min(img.width - sw, (img.width - sw) * focusX));
  } else {
    sh = img.width / target;
    sy = Math.max(0, Math.min(img.height - sh, (img.height - sh) * focusY));
  }
  ctx.drawImage(img, sx, sy, sw, sh, x, y, w, h);
}

function fade(ctx, x, y, w, h, stops, horizontal = false) {
  const grad = horizontal
    ? ctx.createLinearGradient(x, y, x + w, y)
    : ctx.createLinearGradient(x, y, x, y + h);
  stops.forEach(([at, color]) => grad.addColorStop(at, color));
  rect(ctx, x, y, w, h, grad);
}

function header(ctx, n, light = false, label = 'BRASIL / IA') {
  const fg = light ? C.ink : C.cream;
  faceText(ctx, 'VITOR SIMÕES', M, 76, 23, fg, 900);
  faceText(ctx, label, W - M, 76, 22, fg, 600, 'right');
  rule(ctx, M, 104, W - M, 104, light ? 'rgba(14,15,18,.24)' : 'rgba(244,240,230,.35)', 1);
  const base = light ? 'rgba(14,15,18,.20)' : 'rgba(244,240,230,.25)';
  rule(ctx, M, 1270, W - M, 1270, base, 3);
  rule(ctx, M, 1270, M + (W - 2 * M) * n / 7, 1270, C.gold, 5);
  faceText(ctx, `${String(n).padStart(2, '0')} / 07`, W - M, 1310, 22, fg, 600, 'right');
  faceText(ctx, 'SE EU FOSSE PRESIDENTE', M, 1310, 20, light ? C.gray : C.gray, 600);
}

function grain(ctx, seed = 1, count = 13500, alpha = 0.035) {
  let s = seed >>> 0;
  ctx.fillStyle = `rgba(244,240,230,${alpha})`;
  for (let i = 0; i < count; i++) {
    s = (1664525 * s + 1013904223) >>> 0;
    const x = s % W;
    s = (1664525 * s + 1013904223) >>> 0;
    ctx.fillRect(x, s % H, 1, 1);
  }
}

function slide1(ctx, a) {
  rect(ctx, 0, 0, W, H, C.ink);
  ctx.drawImage(a.face, 0, a.face.height * .24, a.face.width, a.face.height * .54, 0, 0, W, 750);
  rect(ctx, 0, 0, W, 750, 'rgba(14,15,18,.13)');
  fade(ctx, 0, 455, W, 430, [[0, 'rgba(14,15,18,0)'], [.65, 'rgba(14,15,18,.74)'], [1, C.ink]]);
  header(ctx, 1);
  faceText(ctx, 'A DISPUTA REAL', M, 659, 23, C.goldSoft, 700);
  lines(ctx, ['TOP 3 EM USAR', 'CHATGPT.'], M, 772, 84, 94, C.cream, 900);
  lines(ctx, ['E EM CRIAR IA?'], M, 993, 84, 94, C.goldSoft, 900);
  rule(ctx, M, 1050, 455, 1050, C.gold, 4);
  wrapped(ctx, 'O Brasil tem demanda. Meu plano é fazer nascer mais tecnologia aqui.', M, 1125, 880, 34, 44, C.cream, 500);
  faceText(ctx, 'ARRASTE →', M, 1234, 24, C.goldSoft, 700);
  grain(ctx, 3);
}

function slide2(ctx) {
  rect(ctx, 0, 0, W, H, C.cream);
  header(ctx, 2, true, 'O PONTO DE PARTIDA');
  faceText(ctx, '01 / O DADO', M, 210, 27, C.ink, 800);
  faceText(ctx, 'TOP 3', M - 8, 447, 194, C.ink, 900);
  rule(ctx, M, 486, 340, 486, C.gold, 8);
  wrapped(ctx, 'O Brasil está entre os três maiores mercados do ChatGPT por usuários semanais.', M, 583, 900, 45, 61, C.ink, 600);
  rect(ctx, M, 850, W - M * 2, 314, C.ink);
  faceText(ctx, 'MAS ESSE RANKING MEDE USO.', M + 38, 927, 31, C.goldSoft, 800);
  wrapped(ctx, 'Ele não mede quantas empresas daqui criam e vendem tecnologia.', M + 38, 1001, W - M * 2 - 76, 42, 53, C.cream, 600);
  faceText(ctx, 'FONTE: OPENAI, 27 AGO 2026', M, 1222, 21, C.gray, 600);
}

function slide3(ctx) {
  rect(ctx, 0, 0, W, H, C.ink);
  header(ctx, 3, false, 'O MECANISMO');
  faceText(ctx, '02 / O PLANO', M, 211, 27, C.gold, 800);
  lines(ctx, ['TRÊS PEÇAS.', 'NESTA ORDEM.'], M, 335, 89, 103, C.cream, 900);
  wrapped(ctx, 'Eu começaria por quem constrói. Depois, financiaria empresas. Por fim, ampliaria a capacidade de computar.', M, 542, 875, 35, 46, C.cream, 500);
  const steps = [
    ['01', 'GENTE', 'quem sabe construir'],
    ['02', 'CAPITAL', 'quem banca o risco'],
    ['03', 'MÁQUINA', 'onde a IA roda'],
  ];
  steps.forEach(([n, title, sub], i) => {
    const x = M + i * 326;
    rect(ctx, x, 684, 286, 385, C.inkSoft);
    rule(ctx, x, 684, x + 286, 684, C.gold, 4);
    faceText(ctx, n, x + 25, 776, 69, C.gold, 900);
    const size = fitText(ctx, title, 248, 39, 31);
    faceText(ctx, title, x + 25, 895, size, C.cream, 900);
    wrapped(ctx, sub, x + 25, 954, 236, 29, 37, C.cream, 500);
  });
  faceText(ctx, 'Nenhuma das três resolve sozinha.', M, 1188, 37, C.cream, 700);
  grain(ctx, 14);
}

function slide4(ctx, a) {
  rect(ctx, 0, 0, W, H, C.ink);
  // Central crop keeps the departure metaphor, without the synthetic aircraft lettering.
  ctx.drawImage(a.airport, a.airport.width * .115, a.airport.height * .15,
    a.airport.width * .60, a.airport.height * .52, 0, 130, W, 535);
  rect(ctx, 0, 130, W, 535, 'rgba(14,15,18,.13)');
  rect(ctx, M, 568, 411, 54, 'rgba(14,15,18,.88)');
  faceText(ctx, 'IMAGEM GERADA · ILUSTRAÇÃO', M + 16, 605, 23, C.cream, 800);
  fade(ctx, 0, 500, W, 290, [[0, 'rgba(14,15,18,0)'], [1, C.ink]]);
  header(ctx, 4, false, 'DIA 1 / GENTE');
  faceText(ctx, '01 / TALENTO', M, 744, 28, C.goldSoft, 800);
  lines(ctx, ['TRAZER QUEM', 'CONSTRÓI.'], M, 858, 85, 98, C.cream, 900);
  wrapped(ctx, 'Eu proporia IR zero por dez anos para especialistas que viessem construir IA no Brasil.', M, 1074, 905, 38, 51, C.cream, 500);
  faceText(ctx, 'PROPOSTA, NÃO MEDIDA EM VIGOR  ·  IMAGEM ILUSTRATIVA', M, 1225, 19, C.gray, 600);
  grain(ctx, 27);
}

function slide5(ctx) {
  rect(ctx, 0, 0, W, H, C.cream);
  header(ctx, 5, true, 'MÊS 1 / CAPITAL');
  faceText(ctx, '02 / CAPITAL', M, 213, 27, C.ink, 800);
  lines(ctx, ['QUEM CRIA', 'PRECISA DE', 'QUEM APOSTE.'], M, 345, 83, 95, C.ink, 900);
  rule(ctx, M, 660, W - M, 660, C.gold, 3);
  faceText(ctx, 'DINHEIRO DE LONGO PRAZO', M, 748, 30, C.ink, 800);
  wrapped(ctx, 'Eu abriria uma parcela limitada dos fundos de pensão a startups de IA, com diversificação e controle de risco. E isentaria o ganho de quem investir.', M, 825, 850, 32, 43, C.ink, 500);
  rect(ctx, M, 1047, W - M * 2, 139, C.ink);
  faceText(ctx, 'Sem capital, boa ideia fica no laboratório.', M + 34, 1127, 33, C.cream, 700);
  faceText(ctx, 'PROPOSTA · DEPENDERIA DE REGRA E APROVAÇÃO', M, 1228, 19, C.gray, 600);
}

function slide6(ctx, a) {
  rect(ctx, 0, 0, W, H, C.ink);
  photoCover(ctx, a.solar, 0, 128, W, 575, 0.5, 0.61);
  rect(ctx, 0, 128, W, 575, 'rgba(14,15,18,.16)');
  rect(ctx, M, 605, 411, 54, 'rgba(14,15,18,.88)');
  faceText(ctx, 'IMAGEM GERADA · ILUSTRAÇÃO', M + 16, 642, 23, C.cream, 800);
  fade(ctx, 0, 515, W, 320, [[0, 'rgba(14,15,18,0)'], [1, C.ink]]);
  header(ctx, 6, false, 'ANO 1 / COMPUTAÇÃO');
  faceText(ctx, '03 / INFRAESTRUTURA', M, 737, 27, C.goldSoft, 800);
  lines(ctx, ['CHIP, ENERGIA', 'E CAPACIDADE', 'DE COMPUTAR.'], M, 836, 73, 84, C.cream, 900);
  wrapped(ctx, 'Eu negociaria chips e atrairia data centers para onde houver energia competitiva, rede e água disponíveis.', M, 1117, 930, 35, 48, C.cream, 500);
  faceText(ctx, 'IMAGEM ILUSTRATIVA · ENERGIA SOZINHA NÃO BASTA', M, 1225, 19, C.gray, 600);
  grain(ctx, 48);
}

function slide7(ctx, a) {
  rect(ctx, 0, 0, W, H, C.ink);
  ctx.drawImage(a.face, a.face.width * .15, a.face.height * .20,
    a.face.width * .70, a.face.height * .78, 570, 105, 510, 1015);
  rect(ctx, 570, 105, 510, 1015, 'rgba(14,15,18,.30)');
  fade(ctx, 385, 105, 520, 1015, [[0, C.ink], [.6, 'rgba(14,15,18,.75)'], [1, 'rgba(14,15,18,0)']], true);
  fade(ctx, 0, 920, W, 330, [[0, 'rgba(14,15,18,0)'], [1, C.ink]]);
  header(ctx, 7, false, 'O TESTE');
  faceText(ctx, 'A CONCLUSÃO', M, 257, 26, C.goldSoft, 800);
  lines(ctx, ['O TESTE', 'É PRODUTO.'], M, 368, 84, 98, C.cream, 900);
  wrapped(ctx, 'Não basta somar logins ou abrir data centers.', M, 632, 570, 39, 52, C.cream, 600);
  wrapped(ctx, 'Potência é ver empresas brasileiras criando produto e vendendo tecnologia para o mundo.', M, 773, 860, 44, 58, C.goldSoft, 700);
  rule(ctx, M, 1045, W - M, 1045, C.gold, 3);
  wrapped(ctx, 'Qual viria primeiro: gente, capital ou computação?', M, 1121, 930, 33, 45, C.cream, 600);
  faceText(ctx, 'COMENTA A SUA ESCOLHA ↓', M, 1225, 22, C.goldSoft, 800);
  grain(ctx, 73);
}

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const loaded = {};
  for (const [key, filename] of Object.entries(assetPaths)) loaded[key] = await loadImage(filename);
  const renderers = [slide1, slide2, slide3, slide4, slide5, slide6, slide7];
  const thumbs = [];
  for (let i = 0; i < renderers.length; i++) {
    const canvas = createCanvas(W, H);
    const ctx = canvas.getContext('2d');
    renderers[i](ctx, loaded);
    fs.writeFileSync(path.join(OUT, `${String(i + 1).padStart(2, '0')}.png`), canvas.toBuffer('image/png'));
    thumbs.push(canvas);
  }
  const scale = .25;
  const gap = 18;
  const cols = 4;
  const rows = 2;
  const sheet = createCanvas(cols * W * scale + (cols + 1) * gap, rows * H * scale + (rows + 1) * gap);
  const ctx = sheet.getContext('2d');
  rect(ctx, 0, 0, sheet.width, sheet.height, '#292A2D');
  thumbs.forEach((item, i) => {
    const x = gap + (i % cols) * (W * scale + gap);
    const y = gap + Math.floor(i / cols) * (H * scale + gap);
    ctx.drawImage(item, x, y, W * scale, H * scale);
  });
  fs.writeFileSync(path.join(ROOT, 'contact-sheet.png'), sheet.toBuffer('image/png'));
  process.stdout.write(`Exportados ${renderers.length} slides de ${W}x${H} em ${OUT}\n`);
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
