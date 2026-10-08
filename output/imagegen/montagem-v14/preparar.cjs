const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');
const requireRuntime = createRequire('C:/Users/Vitor Simões/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/_portrait.cjs');
const sharp = requireRuntime('sharp');
const donor = 'C:/Users/Vitor Simões/.codex/generated_images/01a0936b-0db6-77c2-b860-dd28e0ea4ef4/exec-034f1352-adbd-462a-8f13-a2bae5607e4a.png';
async function main() {
  fs.copyFileSync(donor, path.join(__dirname, 'doadora-gola.png'));
  await sharp(donor).extract({left:350,top:740,width:340,height:514}).png().toFile(path.join(__dirname,'roupa-recorte.png'));
  const roi={left:350,top:695,width:340,height:559};
  let grid='<svg width="340" height="559" xmlns="http://www.w3.org/2000/svg">';
  for(let x=350;x<=675;x+=25) grid+=`<line x1="${x-350}" y1="0" x2="${x-350}" y2="559" stroke="cyan" stroke-opacity=".4"/><text x="${x-350+1}" y="14" fill="red" font-size="10">${x}</text>`;
  for(let y=700;y<=1250;y+=25) grid+=`<line x1="0" y1="${y-695}" x2="340" y2="${y-695}" stroke="cyan" stroke-opacity=".4"/><text x="0" y="${y-695+11}" fill="red" font-size="10">${y}</text>`;
  grid+='</svg>';
  for(const [name,file] of [['doadora',donor],['base','C:/Users/Vitor Simões/Downloads/exec-e90ea39a-46e8-48db-a7e2-5627c6713e25.png']])
    await sharp(file).extract(roi).composite([{input:Buffer.from(grid)}]).png().toFile(path.join(__dirname,`${name}-grade.png`));
  console.log('Donor saved and garment crop prepared.');
}
main().catch(e=>{console.error(e);process.exit(1);});
