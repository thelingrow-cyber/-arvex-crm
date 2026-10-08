'use strict';

// Proposta visual exploratória. Usa somente frames reais já fornecidos pelo Vitor.
const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage } = require('@napi-rs/canvas');

const OUT = __dirname;
const FRAMES = path.resolve(OUT, '../carrossel-01-arquitetura-2027-v2/assets');
const SLIDES = path.join(OUT, 'amostras');
fs.mkdirSync(SLIDES, { recursive: true });

const C = {
  coal: '#0D1113',
  coalSoft: '#192024',
  ivory: '#F2EFE8',
  ivoryDeep: '#E5DED2',
  gold: '#C8A96E',
  goldPale: '#D7C5A0',
  mutedDark: '#626A6B',
  mutedLight: '#B8B9B3',
};

const photo = (name) => `data:image/png;base64,${fs.readFileSync(path.join(FRAMES, name)).toString('base64')}`;
const P = { cover: photo('podcast-04.png'), detail: photo('podcast-06.png') };

function logo(x, y, scale, color) {
  return `<g transform="translate(${x} ${y}) scale(${scale})">
    <g fill="none" stroke="${color}" stroke-width="27" stroke-linecap="square" stroke-linejoin="miter">
      <path d="M14 128 58 12"/><path d="M80 12 126 128"/><path d="M38 92h64"/>
    </g>
    <g fill="${color}" fill-rule="evenodd">
      <path d="M160 140V0h58c38 0 61 20 61 51 0 23-13 40-35 47l39 42h-43l-34-38h-12v38Zm34-68h21c19 0 29-7 29-21 0-14-10-21-29-21h-21Z"/>
      <path d="M310 0h38l34 103L416 0h38l-55 140h-34Z"/>
      <path d="M480 0h114v30h-80v24h68v30h-68v26h80v30H480Z"/>
      <path d="M620 0h40l32 48 32-48h40l-50 70 50 70h-40l-32-48-32 48h-40l50-70Z"/>
    </g>
    <rect x="680" y="58" width="24" height="24" rx="2" fill="${C.gold}" transform="rotate(45 692 70)"/>
  </g>`;
}

function diamond(x, y, size = 16) {
  return `<rect x="${x-size/2}" y="${y-size/2}" width="${size}" height="${size}" fill="${C.gold}" transform="rotate(45 ${x} ${y})"/>`;
}

function header(editoria, page, light = true, withLogo = true) {
  const fg = light ? C.ivory : C.coal;
  const rule = light ? '#FFFFFF66' : '#0D111355';
  return `${withLogo ? logo(64, 54, .19, fg) : `<text x="64" y="100" fill="${fg}" class="micro" font-size="26" letter-spacing="2">ARVEX</text>`}
    <text x="1016" y="94" text-anchor="end" fill="${fg}" class="micro" font-size="22" letter-spacing="2.3">${editoria}  /  ${page}</text>
    <line x1="64" y1="132" x2="1016" y2="132" stroke="${rule}" stroke-width="2"/>`;
}

function footer(page, light = true, arrow = true) {
  const fg = light ? C.ivory : C.coal;
  const rule = light ? '#FFFFFF55' : '#0D111344';
  return `<line x1="64" y1="1253" x2="1016" y2="1253" stroke="${rule}" stroke-width="2"/>
    <text x="64" y="1306" fill="${fg}" class="micro" font-size="20" letter-spacing="2">ARVEX  /  ARQUITETURA DE NEGÓCIOS</text>
    <text x="1016" y="1306" text-anchor="end" fill="${fg}" class="micro" font-size="20" letter-spacing="1.8">${page} ${arrow ? ' →' : ''}</text>`;
}

function svg(body, defs = '') {
  return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1350" viewBox="0 0 1080 1350">
    <defs>
      <style>
        .display { font-family: Bahnschrift, Arial, sans-serif; font-weight: 700; }
        .body { font-family: Arial, Helvetica, sans-serif; font-weight: 400; }
        .micro { font-family: Bahnschrift, Arial, sans-serif; font-weight: 600; }
      </style>
      <filter id="mono" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="0"/></filter>
      <linearGradient id="coverFade" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="${C.coal}" stop-opacity="0"/>
        <stop offset=".35" stop-color="${C.coal}" stop-opacity=".05"/>
        <stop offset=".66" stop-color="${C.coal}" stop-opacity=".75"/>
        <stop offset="1" stop-color="${C.coal}" stop-opacity=".98"/>
      </linearGradient>
      <linearGradient id="detailFade" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="${C.coal}" stop-opacity=".85"/>
        <stop offset=".55" stop-color="${C.coal}" stop-opacity=".20"/>
        <stop offset="1" stop-color="${C.coal}" stop-opacity="0"/>
      </linearGradient>
      ${defs}
    </defs>${body}</svg>`;
}

function documentaryCover() {
  return svg(`
    <rect width="1080" height="1350" fill="${C.coal}"/>
    <image xlink:href="${P.cover}" x="0" y="0" width="1080" height="1350" preserveAspectRatio="xMidYMid slice" filter="url(#mono)"/>
    <rect width="1080" height="1350" fill="${C.coal}" opacity=".10"/>
    <rect width="1080" height="1350" fill="url(#coverFade)"/>
    ${header('TESE', '01', true)}
    <text x="64" y="745" fill="${C.ivory}" class="display" font-size="92" letter-spacing="-3.5">
      <tspan x="64">Não é sobre</tspan><tspan x="64" dy="93">ter IA.</tspan>
      <tspan x="64" dy="105">É sobre fazer a</tspan><tspan x="64" dy="93">empresa funcionar</tspan><tspan x="64" dy="93">com ela.</tspan>
    </text>
    <line x1="64" y1="1172" x2="460" y2="1172" stroke="${C.gold}" stroke-width="3"/>
    ${diamond(463, 1172, 15)}
    ${footer('01 / 03', true)}
  `);
}

function editorialThesis() {
  return svg(`
    <rect width="1080" height="1350" fill="${C.ivory}"/>
    <path d="M0 0H1080V1350H0Z" fill="#E6DFD4" opacity=".16"/>
    ${header('DIAGNÓSTICO', '02', false)}
    <text x="64" y="273" fill="${C.mutedDark}" class="micro" font-size="24" letter-spacing="2.4">O ERRO NÃO ESTÁ NO MODELO</text>
    <text x="64" y="460" fill="${C.coal}" class="display" font-size="104" letter-spacing="-4">
      <tspan x="64">Ferramenta</tspan><tspan x="64" dy="114">nova.</tspan>
    </text>
    <line x1="64" y1="674" x2="1016" y2="674" stroke="${C.gold}" stroke-width="3"/>
    ${diamond(520, 674, 19)}
    <text x="64" y="842" fill="${C.coal}" class="display" font-size="104" letter-spacing="-4">
      <tspan x="64">Gargalo</tspan><tspan x="64" dy="114">antigo.</tspan>
    </text>
    <text x="64" y="1095" fill="${C.coalSoft}" class="body" font-size="39">
      <tspan x="64">Se o contexto não acompanha o trabalho,</tspan>
      <tspan x="64" dy="52">a automação só acelera a confusão.</tspan>
    </text>
    ${footer('02 / 03', false)}
  `);
}

function operatingDiagram() {
  return svg(`
    <rect width="1080" height="1350" fill="${C.coal}"/>
    <image xlink:href="${P.detail}" x="520" y="160" width="560" height="690" preserveAspectRatio="xMidYMid slice" filter="url(#mono)" opacity=".50"/>
    <rect x="520" y="160" width="560" height="690" fill="url(#detailFade)"/>
    ${header('MECANISMO', '03', true)}
    <text x="64" y="319" fill="${C.ivory}" class="display" font-size="76" letter-spacing="-2.2">
      <tspan x="64">O trabalho muda</tspan>
      <tspan x="64" dy="82">quando a empresa</tspan>
      <tspan x="64" dy="82">guarda contexto.</tspan>
    </text>
    <text x="64" y="690" fill="${C.goldPale}" class="micro" font-size="26" letter-spacing="2">UMA ARQUITETURA, TRÊS FUNÇÕES</text>
    <path d="M80 800H995M80 940H995M80 1080H995" fill="none" stroke="${C.gold}" stroke-opacity=".55" stroke-width="2"/>
    ${diamond(80, 800, 15)}${diamond(80, 940, 15)}${diamond(80, 1080, 15)}
    <text x="112" y="776" fill="${C.ivory}" class="display" font-size="48">01  Contexto</text>
    <text x="112" y="916" fill="${C.ivory}" class="display" font-size="48">02  Decisão</text>
    <text x="112" y="1056" fill="${C.ivory}" class="display" font-size="48">03  Execução</text>
    <text x="112" y="831" fill="${C.mutedLight}" class="body" font-size="28">A informação certa acompanha cada etapa.</text>
    <text x="112" y="971" fill="${C.mutedLight}" class="body" font-size="28">Pessoas assumem o que exige julgamento.</text>
    <text x="112" y="1111" fill="${C.mutedLight}" class="body" font-size="28">Sistemas e IA fazem o restante andar.</text>
    ${footer('03 / 03', true, false)}
  `);
}

async function main() {
  const pages = [documentaryCover(), editorialThesis(), operatingDiagram()];
  const coverPhoto = await loadImage(path.join(FRAMES, 'podcast-04.png'));
  const detailPhoto = await loadImage(path.join(FRAMES, 'podcast-06.png'));
  const board = createCanvas(1456, 748);
  const ctx = board.getContext('2d');
  ctx.fillStyle = C.ivory;
  ctx.fillRect(0, 0, 1456, 748);
  ctx.fillStyle = C.coal;
  ctx.font = 'bold 36px Bahnschrift';
  ctx.fillText('ARVEX / PROPOSTA DE SISTEMA EDITORIAL', 64, 70);
  ctx.fillStyle = C.mutedDark;
  ctx.font = '19px Arial';
  ctx.fillText('Uma identidade, três composições. Fotografia original • traço estrutural • encontro dourado.', 64, 110);
  for (let i = 0; i < pages.length; i++) {
    const name = String(i + 1).padStart(2, '0');
    fs.writeFileSync(path.join(SLIDES, `${name}.svg`), pages[i]);
    const canvas = createCanvas(1080, 1350);
    const pageCtx = canvas.getContext('2d');
    let renderSvg = pages[i];
    if (i === 0 || i === 2) {
      pageCtx.fillStyle = C.coal;
      pageCtx.fillRect(0, 0, 1080, 1350);
      pageCtx.save();
      pageCtx.filter = 'grayscale(1)';
      if (i === 0) {
        const sourceWidth = coverPhoto.height * 1080 / 1350;
        pageCtx.drawImage(coverPhoto, (coverPhoto.width - sourceWidth) / 2 + 40, 0, sourceWidth, coverPhoto.height, 0, 0, 1080, 1350);
      } else {
        pageCtx.globalAlpha = .5;
        const sourceWidth = detailPhoto.height * 560 / 690;
        pageCtx.drawImage(detailPhoto, (detailPhoto.width - sourceWidth) / 2, 0, sourceWidth, detailPhoto.height, 520, 160, 560, 690);
      }
      pageCtx.restore();
      renderSvg = renderSvg.replace(/<image[^>]*\/>/, '').replace(`<rect width="1080" height="1350" fill="${C.coal}"/>`, '');
    }
    const image = await loadImage(Buffer.from(renderSvg));
    pageCtx.drawImage(image, 0, 0, 1080, 1350);
    fs.writeFileSync(path.join(SLIDES, `${name}.png`), await canvas.encode('png'));
    ctx.drawImage(canvas, 64 + 448 * i, 145, 432, 540);
  }
  ctx.fillStyle = C.coal;
  ctx.font = '19px Arial';
  ['01 / documental', '02 / tese', '03 / mecanismo'].forEach((label, i) => ctx.fillText(label, 64 + 448 * i, 716));
  fs.writeFileSync(path.join(OUT, 'prancha.png'), await board.encode('png'));
}

main().catch((err) => { console.error(err); process.exitCode = 1; });
