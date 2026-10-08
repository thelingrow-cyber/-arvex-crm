const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/Vitor Simões/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');

const ROOT = __dirname;
const ASSETS = path.join(ROOT, 'assets');
const BACKGROUND = path.join(ASSETS, 'showroom-key-base.png');
const LOGO_SOURCE = path.join(ASSETS, 'aa-logo-reference.jpg');
const LOGO_CUTOUT = path.join(ASSETS, 'aa-logo-white.png');
const OUTPUT = path.join(ROOT, 'aa-dia-do-cliente-story.png');
const PREVIEW = path.join(ROOT, 'aa-dia-do-cliente-preview.png');

const W = 1080;
const H = 1920;

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

async function buildLogoCutout() {
  const left = 178;
  const top = 55;
  const width = 630;
  const height = 537;
  const { data, info } = await sharp(LOGO_SOURCE)
    .extract({ left, top, width, height })
    .removeAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });

  const rgba = Buffer.alloc(info.width * info.height * 4);
  for (let i = 0, p = 0; i < data.length; i += 3, p += 4) {
    const luminance = 0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2];
    const alpha = clamp(Math.round((luminance - 7) * 2.25), 0, 255);
    rgba[p] = 244;
    rgba[p + 1] = 244;
    rgba[p + 2] = 241;
    rgba[p + 3] = alpha;
  }

  await sharp(rgba, {
    raw: { width: info.width, height: info.height, channels: 4 },
  }).png().toFile(LOGO_CUTOUT);
}

function overlaySvg() {
  return Buffer.from(`
  <svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <defs>
      <linearGradient id="topShade" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#050608" stop-opacity="0.82"/>
        <stop offset="0.48" stop-color="#07080A" stop-opacity="0.56"/>
        <stop offset="0.64" stop-color="#07080A" stop-opacity="0.18"/>
        <stop offset="1" stop-color="#07080A" stop-opacity="0"/>
      </linearGradient>
      <linearGradient id="leftShade" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#050608" stop-opacity="0.58"/>
        <stop offset="0.72" stop-color="#050608" stop-opacity="0.06"/>
        <stop offset="1" stop-color="#050608" stop-opacity="0"/>
      </linearGradient>
      <linearGradient id="silver" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#FFFFFF"/>
        <stop offset="0.55" stop-color="#D9DBDC"/>
        <stop offset="1" stop-color="#B7AA9B"/>
      </linearGradient>
      <filter id="softGlow" x="-30%" y="-30%" width="160%" height="160%">
        <feGaussianBlur stdDeviation="8" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>

    <rect width="${W}" height="1180" fill="url(#topShade)"/>
    <rect width="${W}" height="1160" fill="url(#leftShade)"/>
    <path d="M705 430 Q860 305 1015 430" fill="none" stroke="#EEF0F1" stroke-opacity="0.10" stroke-width="2"/>
    <circle cx="860" cy="430" r="4" fill="#EEE9E1" fill-opacity="0.40"/>

    <g font-family="Segoe UI, Arial, sans-serif">
      <text x="996" y="252" text-anchor="end" fill="#F4F4F1" font-size="24" font-weight="700" letter-spacing="4">15 DE SETEMBRO</text>
      <text x="996" y="292" text-anchor="end" fill="#B9BDC2" font-size="18" font-weight="600" letter-spacing="3.2">DIA DO CLIENTE</text>
      <line x1="792" y1="318" x2="996" y2="318" stroke="#F2EEE8" stroke-opacity="0.42" stroke-width="2"/>

      <text x="82" y="568" fill="#F7F7F4" font-family="Bahnschrift, Arial, sans-serif" font-size="106" font-weight="700" letter-spacing="-1.2">CONFIANÇA</text>
      <text x="86" y="654" fill="#C7CACD" font-family="Bahnschrift, Arial, sans-serif" font-size="54" font-weight="400" letter-spacing="1.8">NÃO SE ANUNCIA.</text>
      <text x="82" y="767" fill="url(#silver)" font-family="Bahnschrift, Arial, sans-serif" font-size="82" font-weight="700" letter-spacing="0.8">SE CONQUISTA.</text>

      <line x1="86" y1="837" x2="86" y2="982" stroke="#EAE7E0" stroke-opacity="0.78" stroke-width="3"/>
      <text x="116" y="866" fill="#E5E6E4" font-size="29" font-weight="400">
        <tspan x="116" dy="0">Obrigado por escolher a AA Multimarcas para</tspan>
        <tspan x="116" dy="42">comprar, vender ou financiar com segurança</tspan>
        <tspan x="116" dy="42">e transparência.</tspan>
        <tspan x="116" dy="54" fill="#FFFFFF" font-weight="700">É a sua confiança que move cada negócio.</tspan>
      </text>
    </g>

    <line x1="82" y1="1692" x2="998" y2="1692" stroke="#FFFFFF" stroke-opacity="0.28" stroke-width="2"/>
    <text x="82" y="1748" fill="#F4F4F1" font-family="Segoe UI, Arial, sans-serif" font-size="23" font-weight="700" letter-spacing="3.7">FELIZ DIA DO CLIENTE</text>
    <text x="998" y="1748" text-anchor="end" fill="#D1D2D2" font-family="Segoe UI, Arial, sans-serif" font-size="20" font-weight="600" letter-spacing="2.8">AA MULTIMARCAS</text>
  </svg>`);
}

async function build() {
  await buildLogoCutout();

  const background = await sharp(BACKGROUND)
    .resize(W, H, { fit: 'cover', position: 'centre' })
    .modulate({ saturation: 0.88, brightness: 0.93 })
    .linear(1.03, -3)
    .png()
    .toBuffer();

  const logo = await sharp(LOGO_CUTOUT)
    .resize({ width: 300 })
    .png()
    .toBuffer();

  await sharp(background)
    .composite([
      { input: overlaySvg(), top: 0, left: 0 },
      { input: logo, top: 168, left: 80 },
    ])
    .withMetadata({ density: 144 })
    .png({ compressionLevel: 9 })
    .toFile(OUTPUT);

  await sharp(OUTPUT)
    .resize({ width: 540 })
    .png({ compressionLevel: 9 })
    .toFile(PREVIEW);

  const meta = await sharp(OUTPUT).metadata();
  const stats = await sharp(OUTPUT).stats();
  fs.writeFileSync(path.join(ROOT, 'validation.json'), JSON.stringify({
    output: path.basename(OUTPUT),
    width: meta.width,
    height: meta.height,
    format: meta.format,
    space: meta.space,
    channels: meta.channels,
    isOpaque: stats.isOpaque,
    source: 'AI-generated photo composited with original AA logo and deterministic SVG typography',
  }, null, 2));
}

build().catch((error) => {
  console.error(error);
  process.exit(1);
});
