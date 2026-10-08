const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const runtimeRequire = createRequire('C:/Users/Vitor Simões/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/_portrait.cjs');
const sharp = runtimeRequire('sharp');
const { PNG } = runtimeRequire('pngjs');

const basePath = 'C:/Users/Vitor Simões/Downloads/exec-e90ea39a-46e8-48db-a7e2-5627c6713e25.png';
const donorPath = path.join(__dirname, 'perfil-colorido-camisa-branca-2026-09-12-v9.png');
const outputDir = path.join(__dirname, 'montagem-v11');
fs.mkdirSync(outputDir, { recursive: true });

async function main() {
  const base = PNG.sync.read(fs.readFileSync(basePath));
  const donor = PNG.sync.read(fs.readFileSync(donorPath));
  if (base.width !== donor.width || base.height !== donor.height) throw new Error('Image dimensions differ; registration required.');
  const metadata = {width:base.width,height:base.height,baseMetadata:await sharp(basePath).metadata(),donorMetadata:await sharp(donorPath).metadata()};
  const roi = {left:350,top:700,width:390,height:554};
  let grid = '<svg width="390" height="554" xmlns="http://www.w3.org/2000/svg">';
  for(let x=350;x<=700;x+=50) grid += `<line x1="${x-350}" y1="0" x2="${x-350}" y2="554" stroke="cyan" stroke-opacity="0.5"/><text x="${x-350+2}" y="18" fill="red" font-size="13">${x}</text>`;
  for(let y=700;y<=1250;y+=50) grid += `<line x1="0" y1="${y-700}" x2="390" y2="${y-700}" stroke="cyan" stroke-opacity="0.5"/><text x="0" y="${y-700+13}" fill="red" font-size="13">${y}</text>`;
  grid += '</svg>';
  if (process.argv.includes('--diagnostics')) {
    for(const [name, imagePath] of [['base',basePath],['camisa',donorPath]]) {
      await sharp(imagePath).extract(roi).composite([{input:Buffer.from(grid)}]).png().toFile(path.join(outputDir, `${name}-grade.png`));
    }
  }

  // The garment patch includes the small new chest opening below the old sweater.
  // Its upper boundary follows the collar, keeping all face/hair pixels protected.
  const outline = `M 473 744
    C 453 758 431 796 414 830
    C 405 851 422 879 421 911
    C 416 970 402 1028 393 1078
    C 382 1140 370 1195 359 1254
    L 454 1254
    C 470 1200 500 1154 531 1100
    C 568 1038 609 973 635 924
    C 651 890 659 842 652 793
    L 638 801
    C 626 817 615 839 601 850
    C 574 855 548 860 528 860
    C 508 860 490 854 482 839
    C 474 818 471 788 473 744 Z`;
  const svg = `<svg width="${base.width}" height="${base.height}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="black"/><path d="${outline}" fill="white"/></svg>`;
  const mask = await sharp(Buffer.from(svg)).removeAlpha().grayscale().blur(2.2).raw().toBuffer();
  const composed = new PNG({width:base.width,height:base.height});
  base.data.copy(composed.data);
  const maskRgba = new PNG({width:base.width,height:base.height});
  let changed=0, protectedChanges=0;
  let bounds={left:base.width,top:base.height,right:0,bottom:0};
  for(let y=0;y<base.height;y++) {
    for(let x=0;x<base.width;x++) {
      const pixel=y*base.width+x, offset=pixel*4;
      let alphaByte = y<740 ? 0 : mask[pixel];
      // Blend only existing neck skin on both sources to avoid a horizontal seam.
      // The entire face/hair area above y=740 remains strictly protected.
      if(y>=740 && y<905 && x>=454 && x<=660) {
        const smooth = value => {const t=Math.max(0,Math.min(1,value));return t*t*(3-2*t);};
        const neckBlend=smooth((y-755)/80)*smooth((x-454)/23)*(1-smooth((x-635)/25))*(1-smooth((y-855)/50));
        alphaByte=Math.max(alphaByte,Math.round(255*neckBlend));
      }
      const alpha=alphaByte/255;
      for(let c=0;c<3;c++) {
        composed.data[offset+c]=Math.round(base.data[offset+c]*(1-alpha)+donor.data[offset+c]*alpha);
        maskRgba.data[offset+c]=alphaByte;
      }
      maskRgba.data[offset+3]=255;
      const different=[0,1,2].some(c=>composed.data[offset+c]!==base.data[offset+c]);
      if(different) {
        changed++;
        bounds.left=Math.min(bounds.left,x); bounds.right=Math.max(bounds.right,x);
        bounds.top=Math.min(bounds.top,y); bounds.bottom=Math.max(bounds.bottom,y);
        if(y<740 || alphaByte===0) protectedChanges++;
      }
    }
  }
  if(protectedChanges) throw new Error('Protected pixels changed.');
  const finalPath=path.join(__dirname,'perfil-montagem-camisa-branca-2026-09-12-v11.png');
  fs.writeFileSync(finalPath,PNG.sync.write(composed,{colorType:2,inputColorType:6}));
  fs.writeFileSync(path.join(outputDir,'mascara-camisa.png'),PNG.sync.write(maskRgba));
  const saved=PNG.sync.read(fs.readFileSync(finalPath));
  let changedInSavedFace=0;
  for(let y=0;y<740;y++) for(let x=0;x<base.width;x++) {
    const offset=(y*base.width+x)*4;
    if([0,1,2].some(c=>saved.data[offset+c]!==base.data[offset+c])) changedInSavedFace++;
  }
  if(changedInSavedFace) throw new Error('Saved PNG changed the protected face/hair region.');
  const audit={method:'Deterministic masked composition; no new image generation',basePath,donorPath,finalPath,width:base.width,height:base.height,protectedRegion:{left:0,top:0,width:base.width,height:740},changedPixelsInProtectedRegion:changedInSavedFace,changedPixelsTotal:changed,changedPercentage:100*changed/(base.width*base.height),changedBounds:bounds,maskFeatherSigma:2.2,metadata};
  fs.writeFileSync(path.join(outputDir,'verificacao.json'),JSON.stringify(audit,null,2));
  await sharp(finalPath).extract(roi).png().toFile(path.join(outputDir,'montagem-detalhe.png'));
  console.log(JSON.stringify(audit,null,2));
}
main().catch(e=>{console.error(e);process.exit(1);});
