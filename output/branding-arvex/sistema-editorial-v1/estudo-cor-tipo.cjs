'use strict';

// Exploração não generativa: modifica apenas valores de cor do frame original.
const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage, GlobalFonts } = require('@napi-rs/canvas');

const OUT = __dirname;
const PHOTO = path.resolve(OUT, '../carrossel-01-arquitetura-2027-v2/assets/podcast-04.png');
const LOGO = path.resolve(OUT, '../logo-v1/arvex-wordmark-dark.png');
const W = 1080;
const H = 1350;
const GOLD = '#C8A96E';
const IVORY = '#F2F0EA';
const COAL = '#0D1113';

GlobalFonts.registerFromPath('C:/Windows/Fonts/bahnschrift.ttf', 'ARVEX Display');

const clamp = (v, min = 0, max = 255) => Math.max(min, Math.min(max, v));
const mix = (a, b, t) => a * (1 - t) + b * t;

function applyGrade(ctx, treatment) {
  const frame = ctx.getImageData(0, 0, W, H);
  const px = frame.data;
  for (let i = 0; i < px.length; i += 4) {
    const r = px[i];
    const g = px[i + 1];
    const b = px[i + 2];
    const light = .24 * r + .68 * g + .08 * b;
    const green = clamp((g - Math.max(r, b) * .90 - 12) / 88, 0, 1);
    const strength = treatment === 'petrol' ? .78 : .85;
    let rr = r * 1.018 + 2;
    let gg = g * .985;
    let bb = b * .958;
    if (treatment === 'petrol') {
      rr = mix(rr, light * .42, green * strength);
      gg = mix(gg, light * .71, green * strength);
      bb = mix(bb, light * .76, green * strength);
    } else {
      rr = mix(rr, light * .67, green * strength);
      gg = mix(gg, light * .56, green * strength);
      bb = mix(bb, light * .43, green * strength);
    }
    px[i] = clamp(rr);
    px[i + 1] = clamp(gg);
    px[i + 2] = clamp(bb);
  }
  ctx.putImageData(frame, 0, 0);
}

function drawBase(ctx, photo, logo, treatment) {
  const sourceWidth = photo.height * W / H;
  const sx = (photo.width - sourceWidth) / 2 + 40;
  ctx.drawImage(photo, sx, 0, sourceWidth, photo.height, 0, 0, W, H);
  applyGrade(ctx, treatment);

  const fade = ctx.createLinearGradient(0, 360, 0, H);
  fade.addColorStop(0, 'rgba(13,17,19,0)');
  fade.addColorStop(.29, 'rgba(13,17,19,.11)');
  fade.addColorStop(.53, 'rgba(13,17,19,.72)');
  fade.addColorStop(1, 'rgba(13,17,19,.98)');
  ctx.fillStyle = fade;
  ctx.fillRect(0, 0, W, H);

  ctx.drawImage(logo, 64, 53, 158, 29);
  ctx.fillStyle = IVORY;
  ctx.textAlign = 'right';
  ctx.font = '600 22px ARVEX Display';
  ctx.fillText('TESE / 01', 1016, 90);
  ctx.textAlign = 'left';
  ctx.strokeStyle = 'rgba(242,240,234,.45)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(64, 132);
  ctx.lineTo(1016, 132);
  ctx.stroke();
}

function drawCopy(ctx, typography) {
  const lines = ['Não é sobre', 'ter IA.', 'É sobre fazer a', 'empresa funcionar', 'com ela.'];
  ctx.fillStyle = IVORY;
  ctx.textAlign = 'left';
  if (typography === 'editorial') {
    ctx.fillStyle = GOLD;
    ctx.font = '600 24px ARVEX Display';
    ctx.fillText('UMA TESE SOBRE ARQUITETURA DE NEGÓCIOS', 64, 755);
    ctx.fillStyle = IVORY;
    ctx.font = '600 84px ARVEX Display';
    ['Ter IA não basta.', 'A empresa precisa', 'funcionar com ela.'].forEach((line, index) => ctx.fillText(line, 64, 865 + index * 102));
  } else {
    ctx.font = '400 92px Arial';
    lines.forEach((line, index) => ctx.fillText(line, 64, 745 + index * 92));
  }

  ctx.strokeStyle = GOLD;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(64, 1172);
  ctx.lineTo(465, 1172);
  ctx.stroke();
  ctx.save();
  ctx.translate(465, 1172);
  ctx.rotate(Math.PI / 4);
  ctx.fillStyle = GOLD;
  ctx.fillRect(-8, -8, 16, 16);
  ctx.restore();

  ctx.strokeStyle = 'rgba(242,240,234,.34)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(64, 1253);
  ctx.lineTo(1016, 1253);
  ctx.stroke();
  ctx.fillStyle = IVORY;
  ctx.font = '600 20px ARVEX Display';
  ctx.fillText('ARVEX / ARQUITETURA DE NEGÓCIOS', 64, 1305);
  ctx.textAlign = 'right';
  ctx.fillText('ARRASTE PARA O LADO', 1016, 1305);
  ctx.textAlign = 'left';
}

async function main() {
  const photo = await loadImage(PHOTO);
  const logo = await loadImage(LOGO);
  const specimens = [
    { id: 'mineral-quente', treatment: 'warm', typography: 'atual', label: '01 / mineral quente + tipo atual' },
    { id: 'petroleo', treatment: 'petrol', typography: 'atual', label: '02 / petróleo + tipo atual' },
    { id: 'mineral-editorial', treatment: 'warm', typography: 'editorial', label: '03 / mineral + tipo editorial' },
  ];
  const board = createCanvas(1456, 749);
  const b = board.getContext('2d');
  b.fillStyle = IVORY;
  b.fillRect(0, 0, board.width, board.height);
  b.fillStyle = COAL;
  b.font = '700 34px ARVEX Display';
  b.fillText('ARVEX / ESTUDO DE COR E TIPOGRAFIA', 64, 69);
  b.fillStyle = '#626A6B';
  b.font = '20px Arial';
  b.fillText('Mesmo frame original. Sem geração: apenas balanço de cor, contraste e composição.', 64, 109);

  for (let i = 0; i < specimens.length; i++) {
    const item = specimens[i];
    const canvas = createCanvas(W, H);
    const ctx = canvas.getContext('2d');
    drawBase(ctx, photo, logo, item.treatment);
    drawCopy(ctx, item.typography);
    fs.writeFileSync(path.join(OUT, `${item.id}.png`), await canvas.encode('png'));
    b.drawImage(canvas, 64 + 448 * i, 145, 432, 540);
    b.fillStyle = COAL;
    b.font = '19px Arial';
    b.fillText(item.label, 64 + 448 * i, 718);
  }
  fs.writeFileSync(path.join(OUT, 'estudo-cor-tipo.png'), await board.encode('png'));

  const alternatePhoto = await loadImage(path.resolve(OUT, '../carrossel-01-arquitetura-2027-v2/assets/podcast-02.png'));
  const cover = createCanvas(W, H);
  const coverCtx = cover.getContext('2d');
  drawBase(coverCtx, alternatePhoto, logo, 'warm');
  drawCopy(coverCtx, 'editorial');
  fs.writeFileSync(path.join(OUT, 'capa-mineral-frame02.png'), await cover.encode('png'));
}

main().catch(error => { console.error(error); process.exitCode = 1; });
