const path = require('path');
const sharp = require('sharp');

const root = __dirname;
const jobs = [
  ['route-01-stacked.svg', 'route-01-stacked.png', 1024, 1024],
  ['route-02-system.svg', 'route-02-system.png', 1024, 1024],
  ['route-03-vx.svg', 'route-03-vx.png', 1024, 1024],
  ['arvex-directions-board.svg', 'arvex-directions-board.png', 1920, 1080],
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

