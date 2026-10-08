'use strict';

const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage, GlobalFonts } = require('@napi-rs/canvas');

const OUT = __dirname;
const SLIDES = path.join(OUT, 'slides');
const BRAND = path.resolve(OUT, '../logo-v1');
const EDITORIAL = path.resolve(OUT, '../sistema-editorial-v1');
const W = 1080;
const H = 1350;
const C = {
  coal: '#111411',
  coalDeep: '#0D1113',
  ivory: '#F2F0EA',
  paper: '#EEE9DF',
  gold: '#C8A96E',
  goldDark: '#A37D44',
  lightMuted: '#C9C8BE',
  darkMuted: '#555C58',
};

GlobalFonts.registerFromPath('C:/Windows/Fonts/bahnschrift.ttf', 'ARVEX Display');
fs.mkdirSync(SLIDES, { recursive: true });

const assets = {};

function setFont(ctx, size, weight = 600, family = 'ARVEX Display') {
  ctx.font = `${weight} ${size}px ${family}`;
}

function drawLines(ctx, lines, x, y, size, leading, color, weight = 600, family = 'ARVEX Display') {
  ctx.fillStyle = color;
  ctx.textAlign = 'left';
  setFont(ctx, size, weight, family);
  lines.forEach((line, i) => ctx.fillText(line, x, y + i * leading));
}

function rule(ctx, x1, y1, x2, y2, color, width = 2) {
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();
}

function diamond(ctx, x, y, size = 15) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(Math.PI / 4);
  ctx.fillStyle = C.gold;
  ctx.fillRect(-size / 2, -size / 2, size, size);
  ctx.restore();
}

function background(ctx, dark) {
  ctx.fillStyle = dark ? C.coal : C.paper;
  ctx.fillRect(0, 0, W, H);
  const wash = ctx.createRadialGradient(dark ? 835 : 105, dark ? 105 : 75, 50, 550, 250, 1150);
  if (dark) {
    wash.addColorStop(0, 'rgba(118,93,55,.16)');
    wash.addColorStop(1, 'rgba(17,20,17,0)');
  } else {
    wash.addColorStop(0, 'rgba(255,255,247,.60)');
    wash.addColorStop(1, 'rgba(226,217,201,.20)');
  }
  ctx.fillStyle = wash;
  ctx.fillRect(0, 0, W, H);
}

function chrome(ctx, page, section, headerDark, footerDark = headerDark) {
  const headerColor = headerDark ? C.ivory : C.coalDeep;
  const footerColor = footerDark ? C.ivory : C.coalDeep;
  const logo = headerDark ? assets.logoWhite : assets.logoDark;
  ctx.drawImage(logo, 64, 53, 158, 29);
  ctx.fillStyle = headerColor;
  ctx.textAlign = 'right';
  setFont(ctx, 22);
  ctx.fillText(`${section} / ${String(page).padStart(2, '0')}`, 1016, 90);
  ctx.textAlign = 'left';
  rule(ctx, 64, 132, 1016, 132, headerDark ? 'rgba(242,240,234,.37)' : 'rgba(13,17,19,.30)');
  rule(ctx, 64, 1253, 1016, 1253, footerDark ? 'rgba(242,240,234,.28)' : 'rgba(13,17,19,.25)');
  ctx.fillStyle = footerColor;
  setFont(ctx, 20);
  ctx.fillText('ARVEX / ARQUITETURA DE NEGÓCIOS', 64, 1305);
  ctx.textAlign = 'right';
  ctx.fillText(`${String(page).padStart(2, '0')} / 07`, 1016, 1305);
  ctx.textAlign = 'left';
}

function eyebrow(ctx, label, y = 207, dark = true) {
  ctx.fillStyle = dark ? C.gold : C.goldDark;
  setFont(ctx, 25);
  ctx.fillText(label, 64, y);
}

function page2(ctx) {
  background(ctx, false);
  eyebrow(ctx, 'O ERRO MAIS COMUM', 225, false);
  drawLines(ctx, ['Ferramenta nova.', 'Gargalo antigo.'], 64, 366, 97, 120, C.coalDeep, 600);
  rule(ctx, 64, 585, 1016, 585, C.goldDark, 3);
  diamond(ctx, 540, 585, 17);
  drawLines(ctx, [
    'Quando processos e decisões continuam',
    'separados, a IA encontra a mesma operação',
    'fragmentada.'
  ], 64, 690, 37, 56, C.coalDeep, 400, 'Arial');
  drawLines(ctx, ['A arquitetura vem antes', 'da automação.'], 64, 1075, 63, 76, C.coalDeep, 600);
  chrome(ctx, 2, 'TESE', false);
}

function page3(ctx) {
  background(ctx, true);
  eyebrow(ctx, '01 / DIAGNOSTICAR');
  drawLines(ctx, ['Descubra onde o', 'trabalho trava.'], 64, 326, 81, 91, C.ivory, 600);
  drawLines(ctx, ['Antes de automatizar, responda:'], 64, 495, 36, 45, C.lightMuted, 400, 'Arial');
  const questions = [
    'Onde o lead deixa de avançar?',
    'O que se repete todos os dias?',
    'O que ainda depende do dono?',
    'Onde o contexto se perde?',
  ];
  questions.forEach((q, i) => {
    const y = 603 + i * 134;
    rule(ctx, 64, y - 50, 1016, y - 50, 'rgba(242,240,234,.24)');
    ctx.fillStyle = C.gold;
    setFont(ctx, 36);
    ctx.fillText(String(i + 1).padStart(2, '0'), 64, y);
    ctx.fillStyle = C.ivory;
    setFont(ctx, 38);
    ctx.fillText(q, 170, y);
  });
  rule(ctx, 64, 1087, 1016, 1087, 'rgba(242,240,234,.24)');
  drawLines(ctx, ['O gargalo revela', 'a primeira peça.'], 64, 1151, 49, 56, C.gold, 600);
  chrome(ctx, 3, 'MÉTODO', true);
}

function coverImageTop(ctx, image, x, y, width, height) {
  const cropHeight = Math.min(image.height, image.width * height / width);
  ctx.drawImage(image, 0, 0, image.width, cropHeight, x, y, width, height);
}

function page4(ctx) {
  background(ctx, true);
  eyebrow(ctx, '02 / REARQUITETAR');
  drawLines(ctx, ['Dê um papel claro', 'a cada parte.'], 64, 325, 78, 91, C.ivory, 600);
  ctx.save();
  ctx.beginPath();
  ctx.rect(530, 485, 550, 640);
  ctx.clip();
  coverImageTop(ctx, assets.model, 530, 485, 550, 640);
  const photoFade = ctx.createLinearGradient(530, 0, 875, 0);
  photoFade.addColorStop(0, C.coal);
  photoFade.addColorStop(.52, 'rgba(17,20,17,.35)');
  photoFade.addColorStop(1, 'rgba(17,20,17,0)');
  ctx.fillStyle = photoFade;
  ctx.fillRect(530, 485, 550, 640);
  ctx.restore();
  const roles = [
    ['Pessoas', 'julgamento, relação', 'e exceções'],
    ['Sistemas', 'regras, dados', 'e contexto'],
    ['IA', 'execução, resposta', 'e monitoramento'],
  ];
  roles.forEach((role, i) => {
    const y = 573 + i * 171;
    ctx.fillStyle = C.gold;
    setFont(ctx, 42);
    ctx.fillText(role[0], 64, y);
    drawLines(ctx, [role[1], role[2]], 64, y + 43, 28, 36, C.ivory, 400, 'Arial');
    if (i < 2) rule(ctx, 64, y + 102, 488, y + 102, 'rgba(242,240,234,.22)');
  });
  rule(ctx, 64, 1119, 1016, 1119, C.gold, 2);
  diamond(ctx, 710, 1119, 15);
  drawLines(ctx, ['A IA passa a fazer parte do fluxo.'], 64, 1187, 42, 48, C.ivory, 600);
  chrome(ctx, 4, 'ARQUITETURA', true);
}

function page5(ctx) {
  background(ctx, false);
  eyebrow(ctx, 'O QUE MUDA NA OPERAÇÃO', 220, false);
  drawLines(ctx, ['Menos memória.', 'Mais continuidade.'], 64, 345, 88, 103, C.coalDeep, 600);
  ctx.fillStyle = C.darkMuted;
  setFont(ctx, 25);
  ctx.fillText('ANTES', 64, 560);
  ctx.fillStyle = C.goldDark;
  ctx.fillText('DEPOIS', 594, 560);
  const changes = [
    ['Espera', 'Resposta'],
    ['Dependência', 'Continuidade'],
    ['Controle total', 'Exceções'],
  ];
  changes.forEach((pair, i) => {
    const y = 670 + i * 145;
    rule(ctx, 64, y - 62, 1016, y - 62, 'rgba(13,17,19,.23)');
    ctx.fillStyle = C.darkMuted;
    setFont(ctx, 39);
    ctx.fillText(pair[0], 64, y);
    rule(ctx, 440, y - 12, 535, y - 12, C.goldDark, 3);
    diamond(ctx, 535, y - 12, 13);
    ctx.fillStyle = C.coalDeep;
    setFont(ctx, 43);
    ctx.fillText(pair[1], 594, y);
  });
  rule(ctx, 64, 1035, 1016, 1035, 'rgba(13,17,19,.23)');
  drawLines(ctx, ['Autonomia libera pessoas para', 'julgamento, relação e exceções.'], 64, 1120, 39, 49, C.coalDeep, 600);
  chrome(ctx, 5, 'APLICAÇÃO', false);
}

function page6(ctx) {
  background(ctx, true);
  eyebrow(ctx, '03 / IMPLEMENTAR');
  drawLines(ctx, ['Uma peça', 'por vez.'], 64, 332, 105, 110, C.ivory, 600);
  drawLines(ctx, ['Comece pelo gargalo identificado.'], 64, 515, 36, 45, C.lightMuted, 400, 'Arial');
  rule(ctx, 100, 583, 100, 1055, C.gold, 3);
  const steps = [
    ['Diagnosticar', 'encontrar o ponto de perda'],
    ['Redesenhar', 'definir o novo fluxo'],
    ['Implementar', 'colocar a peça para funcionar'],
    ['Medir', 'verificar antes de ampliar'],
  ];
  steps.forEach((step, i) => {
    const y = 608 + i * 143;
    diamond(ctx, 100, y, 17);
    ctx.fillStyle = C.ivory;
    setFont(ctx, 47);
    ctx.fillText(step[0], 162, y + 10);
    ctx.fillStyle = C.lightMuted;
    setFont(ctx, 31, 400, 'Arial');
    ctx.fillText(step[1], 162, y + 55);
  });
  drawLines(ctx, ['Cada peça funciona', 'antes da próxima.'], 64, 1161, 46, 52, C.gold, 600);
  chrome(ctx, 6, 'MÉTODO', true);
}

function page7(ctx) {
  background(ctx, false);
  ctx.fillStyle = C.coal;
  ctx.fillRect(0, 870, W, H - 870);
  eyebrow(ctx, 'A ARQUITETURA É A VANTAGEM', 224, false);
  drawLines(ctx, ['Ter IA é só', 'o começo.'], 64, 352, 99, 116, C.coalDeep, 600);
  drawLines(ctx, ['Faça a empresa', 'funcionar com ela.'], 64, 628, 80, 93, C.goldDark, 600);
  rule(ctx, 64, 785, 1016, 785, C.goldDark, 3);
  diamond(ctx, 615, 785, 17);
  drawLines(ctx, ['Qual parte da sua empresa', 'ainda depende de você?'], 64, 993, 58, 70, C.ivory, 600);
  ctx.fillStyle = C.gold;
  setFont(ctx, 31);
  const cta = 'CONHEÇA A ARVEX';
  ctx.fillText(cta, 64, 1174);
  const arrowX = 64 + ctx.measureText(cta).width + 24;
  rule(ctx, arrowX, 1164, arrowX + 42, 1164, C.gold, 3);
  rule(ctx, arrowX + 42, 1164, arrowX + 30, 1154, C.gold, 3);
  rule(ctx, arrowX + 42, 1164, arrowX + 30, 1174, C.gold, 3);
  chrome(ctx, 7, 'PRÓXIMO PASSO', false, true);
}

async function main() {
  [assets.logoWhite, assets.logoDark, assets.model, assets.cover] = await Promise.all([
    loadImage(path.join(BRAND, 'arvex-wordmark-dark.png')),
    loadImage(path.join(BRAND, 'arvex-wordmark-light.png')),
    loadImage(path.join(EDITORIAL, 'assets', 'maquete-escritorios-conexao-dourada-v1.png')),
    loadImage(path.join(EDITORIAL, 'capa-conceitual-mineral-v1.png')),
  ]);
  const renderers = [
    (ctx) => ctx.drawImage(assets.cover, 0, 0, W, H),
    page2, page3, page4, page5, page6, page7,
  ];
  const output = [];
  for (let i = 0; i < renderers.length; i++) {
    const canvas = createCanvas(W, H);
    renderers[i](canvas.getContext('2d'));
    const name = String(i + 1).padStart(2, '0');
    const file = path.join(SLIDES, `${name}.png`);
    fs.writeFileSync(file, await canvas.encode('png'));
    output.push(canvas);
  }

  const thumbs = createCanvas(1452, 912);
  const board = thumbs.getContext('2d');
  board.fillStyle = C.paper;
  board.fillRect(0, 0, thumbs.width, thumbs.height);
  output.forEach((slide, i) => board.drawImage(slide, 40 + (i % 4) * 350, 38 + Math.floor(i / 4) * 435, 324, 405));
  fs.writeFileSync(path.join(OUT, 'contact-sheet.png'), await thumbs.encode('png'));

  const figures = output.map((_, i) => `<figure><img src="slides/${String(i + 1).padStart(2, '0')}.png" alt="Slide ${i + 1}"><figcaption>${String(i + 1).padStart(2, '0')} / 07</figcaption></figure>`).join('');
  fs.writeFileSync(path.join(OUT, 'index.html'), `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ARVEX — Ter IA não basta</title><style>*{box-sizing:border-box}body{margin:0;background:#111411;color:#f2f0ea;font-family:Arial,sans-serif}header{padding:36px 4vw;border-bottom:1px solid #5b503d}h1{margin:0 0 8px;font-size:40px}p{margin:0;color:#c9c8be}.grid{padding:32px 4vw;display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:26px}figure{margin:0}img{display:block;width:100%}figcaption{padding:10px 0;color:#c8a96e}</style></head><body><header><h1>Ter IA não basta.</h1><p>Carrossel ARVEX · direção mineral editorial · 1080 × 1350</p></header><main class="grid">${figures}</main></body></html>`);
  process.stdout.write(`${path.join(OUT, 'contact-sheet.png')}\n`);
}

main().catch(error => { console.error(error); process.exitCode = 1; });
