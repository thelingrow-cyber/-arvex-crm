'use strict';

const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage, GlobalFonts } = require('@napi-rs/canvas');

const ROOT = __dirname;
const IMAGE = path.join(ROOT, 'assets', 'maquete-escritorios-conexao-dourada-v1.png');
const LOGO = path.resolve(ROOT, '../logo-v1/arvex-wordmark-dark.png');
const OUTPUT = path.join(ROOT, 'capa-conceitual-mineral-v1.png');
const WIDTH = 1080;
const HEIGHT = 1350;
const IVORY = '#F2F0EA';
const GOLD = '#C8A96E';
const COAL = '#0D1113';

GlobalFonts.registerFromPath('C:/Windows/Fonts/bahnschrift.ttf', 'ARVEX Display');

async function main() {
  const [background, logo] = await Promise.all([loadImage(IMAGE), loadImage(LOGO)]);
  const canvas = createCanvas(WIDTH, HEIGHT);
  const ctx = canvas.getContext('2d');

  // Corte ancorado no topo para preservar a maquete e o espaço escuro da headline.
  const sourceHeight = Math.min(background.height, background.width * HEIGHT / WIDTH);
  ctx.drawImage(background, 0, 0, background.width, sourceHeight, 0, 0, WIDTH, HEIGHT);

  const fade = ctx.createLinearGradient(0, 705, 0, HEIGHT);
  fade.addColorStop(0, 'rgba(13,17,19,0)');
  fade.addColorStop(.30, 'rgba(13,17,19,.18)');
  fade.addColorStop(.72, 'rgba(13,17,19,.58)');
  fade.addColorStop(1, 'rgba(13,17,19,.86)');
  ctx.fillStyle = fade;
  ctx.fillRect(0, 705, WIDTH, HEIGHT - 705);

  ctx.drawImage(logo, 64, 53, 158, 29);
  ctx.fillStyle = IVORY;
  ctx.textAlign = 'right';
  ctx.font = '600 22px ARVEX Display';
  ctx.fillText('TESE / 01', 1016, 90);
  ctx.textAlign = 'left';
  ctx.strokeStyle = 'rgba(242,240,234,.46)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(64, 132);
  ctx.lineTo(1016, 132);
  ctx.stroke();

  ctx.fillStyle = GOLD;
  ctx.font = '600 24px ARVEX Display';
  ctx.fillText('UMA TESE SOBRE ARQUITETURA DE NEGÓCIOS', 64, 807);

  const headline = ['Ter IA não basta.', 'A empresa precisa', 'funcionar com ela.'];
  let size = 84;
  while (size > 72) {
    ctx.font = `600 ${size}px ARVEX Display`;
    if (Math.max(...headline.map(line => ctx.measureText(line).width)) <= 952) break;
    size -= 1;
  }
  ctx.fillStyle = IVORY;
  headline.forEach((line, index) => ctx.fillText(line, 64, 917 + index * 102));

  ctx.strokeStyle = GOLD;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(64, 1192);
  ctx.lineTo(465, 1192);
  ctx.stroke();
  ctx.save();
  ctx.translate(465, 1192);
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

  fs.writeFileSync(OUTPUT, await canvas.encode('png'));
  const thumbnail = createCanvas(324, 405);
  thumbnail.getContext('2d').drawImage(canvas, 0, 0, 324, 405);
  fs.writeFileSync(path.join(ROOT, 'capa-conceitual-mineral-v1-miniatura.png'), await thumbnail.encode('png'));
  process.stdout.write(`${OUTPUT}\n`);
}

main().catch(error => { console.error(error); process.exitCode = 1; });
