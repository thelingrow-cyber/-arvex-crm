const path = require('path');
const sharp = require('sharp');

const root = __dirname;
const jobs = [
  ['arvex-avatar-light.svg', 'arvex-avatar-light.png', 2048, 2048],
  ['arvex-avatar-dark.svg', 'arvex-avatar-dark.png', 2048, 2048],
  ['arvex-wordmark-light.svg', 'arvex-wordmark-light.png', 1528, 280],
  ['arvex-wordmark-dark.svg', 'arvex-wordmark-dark.png', 1528, 280],
  ['arvex-brand-board.svg', 'arvex-brand-board.png', 1920, 1080],
];

async function main() {
  for (const [input, output, width, height] of jobs) {
    await sharp(path.join(root, input), { density: 192 })
      .resize(width, height, { fit: 'contain' })
      .png({ compressionLevel: 9 })
      .toFile(path.join(root, output));
    process.stdout.write(`${output}\n`);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

