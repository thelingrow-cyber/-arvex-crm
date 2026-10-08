'use strict';

const path = require('path');
const sharp = require('sharp');

const root = __dirname;
const input = path.join(root, 'assets', 'podcast-04.png');
const output = path.join(root, 'assets', 'podcast-04-documental-mineral-grade-v4.png');

const clamp = (value, min = 0, max = 255) => Math.max(min, Math.min(max, value));
const mix = (from, to, amount) => from + (to - from) * amount;

function hashNoise(x, y) {
  let n = (x * 374761393 + y * 668265263) >>> 0;
  n = (n ^ (n >>> 13)) >>> 0;
  n = Math.imul(n, 1274126177) >>> 0;
  return ((n ^ (n >>> 16)) & 1023) / 1023 - 0.5;
}

async function grade() {
  const { data, info } = await sharp(input)
    .removeAlpha()
    .toColourspace('srgb')
    .raw()
    .toBuffer({ resolveWithObject: true });

  const out = Buffer.alloc(data.length);
  const cx = (info.width - 1) / 2;
  const cy = (info.height - 1) / 2;
  const maxRadius = Math.hypot(cx, cy);

  for (let y = 0; y < info.height; y += 1) {
    for (let x = 0; x < info.width; x += 1) {
      const i = (y * info.width + x) * 3;
      let r = data[i];
      let g = data[i + 1];
      let b = data[i + 2];

      // Neutraliza apenas a dominante verde do estúdio, preservando textura e desenho.
      let lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
      const greenDominance = clamp((g - Math.max(r, b) - 1) / 42, 0, 1);
      const neutralize = greenDominance * 0.98;
      const greenHighlight = clamp((lum - 148) / 92, 0, 1) * 0.58;
      const targetR = mix(lum * 0.32, lum * 0.69, greenHighlight);
      const targetG = mix(lum * 0.39, lum * 0.58, greenHighlight);
      const targetB = mix(lum * 0.44, lum * 0.46, greenHighlight);
      r = mix(r, targetR, neutralize);
      g = mix(g, targetG, neutralize);
      b = mix(b, targetB, neutralize);

      // Saturação contida, sem apagar os tons naturais de pele.
      lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
      const skinLike = clamp((r - b - 8) / 55, 0, 1) * clamp((r - g + 16) / 55, 0, 1);
      const saturation = 0.72 + skinLike * 0.18;
      r = mix(lum, r, saturation);
      g = mix(lum, g, saturation);
      b = mix(lum, b, saturation);

      // Curva de densidade: médios mais firmes e highlights macios.
      const tone = (channel) => {
        let t = channel / 255;
        t = Math.pow(t, 1.075);
        t = 0.5 + (t - 0.5) * 1.13;
        t = t / (1 + 0.16 * Math.max(0, t - 0.7));
        return clamp(t * 255);
      };
      r = tone(r);
      g = tone(g);
      b = tone(b);

      lum = clamp((0.2126 * r + 0.7152 * g + 0.0722 * b) / 255, 0, 1);
      const shadow = Math.pow(1 - lum, 2.15);
      const highlight = Math.pow(lum, 2.25);

      // Split tone ARVEX: petróleo mineral nas sombras, bronze nas luzes.
      r += -5.2 * shadow + 9.0 * highlight;
      g += 1.0 * shadow + 4.1 * highlight;
      b += 6.2 * shadow - 7.2 * highlight;

      // Vinheta óptica quase imperceptível e sem recorte artificial.
      const radius = Math.hypot(x - cx, y - cy) / maxRadius;
      const vignette = 1 - 0.105 * Math.pow(Math.max(0, radius - 0.28) / 0.72, 1.65);
      r *= vignette;
      g *= vignette;
      b *= vignette;

      // Grão determinístico fino: textura, não reconstrução generativa.
      const grain = hashNoise(x, y) * (2.2 + 2.0 * shadow);
      out[i] = Math.round(clamp(r + grain));
      out[i + 1] = Math.round(clamp(g + grain));
      out[i + 2] = Math.round(clamp(b + grain));
    }
  }

  await sharp(out, { raw: info })
    .png({ compressionLevel: 9 })
    .withMetadata({ density: 72 })
    .toFile(output);

  console.log(output);
  console.log(`${info.width}x${info.height}; geometry preserved; RGB-only deterministic grade`);
}

grade().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
