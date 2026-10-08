const sharp = require('sharp');
const path = require('path');

const files = [
  ['route-02a-v-core.svg', 'route-02a-v-core.png', 2048, 2048],
  ['route-02b-v-negative.svg', 'route-02b-v-negative.png', 2048, 2048],
  ['arvex-system-v-lockup.svg', 'arvex-system-v-lockup.png', 2100, 630],
  ['arvex-system-v-board.svg', 'arvex-system-v-board.png', 1920, 1080],
  ['avatar-reduction-test.svg', 'avatar-reduction-test.png', 1200, 360],
];

Promise.all(files.map(([input, output, width, height]) =>
  sharp(path.join(__dirname, input))
    .resize(width, height)
    .png()
    .toFile(path.join(__dirname, output))
)).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
