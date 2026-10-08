const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const runtimeRequire = createRequire('C:/Users/Vitor Simões/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/_portrait.cjs');
const sharp = runtimeRequire('sharp');
const { PNG } = runtimeRequire('pngjs');

const basePath = 'C:/Users/Vitor Simões/Downloads/exec-e90ea39a-46e8-48db-a7e2-5627c6713e25.png';
const donorPath = path.join(__dirname, 'montagem-v12/doadora-gola.png');
const outputDir = path.join(__dirname, 'montagem-v12');
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
  if (process.argv.includes('--inspect')) return;

  // Local conventional reduction of overly busy donor fabric texture.
  // The ribbed collar and central zipper are protected from this adjustment.
  const softened=await sharp(donorPath).ensureAlpha().median(5).blur(0.7).raw().toBuffer();
  const panelPath=`M 461 914 C 492 911 559 915 602 919 L 600 950 L 573 999
    L 538 1060 L 501 1122 L 462 1190 L 425 1254 L 390 1254
    L 400 1163 L 414 1041 L 429 962 Z`;
  const panelSvg=`<svg width="${base.width}" height="${base.height}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="black"/><path d="${panelPath}" fill="white"/></svg>`;
  const panelMask=await sharp(Buffer.from(panelSvg)).removeAlpha().grayscale().blur(8).raw().toBuffer();
  const smooth=value=>{const t=Math.max(0,Math.min(1,value));return t*t*(3-2*t);};
  for(let y=900;y<base.height;y++) for(let x=355;x<665;x++) {
    const pixel=y*base.width+x, offset=pixel*4;
    const zipperX=534-(y-900)*0.18;
    const zipperProtection=(1-smooth((Math.abs(x-zipperX)-13)/10))*(1-smooth((y-1046)/20));
    const weight=0.7*(panelMask[pixel]/255)*(1-zipperProtection);
    for(let c=0;c<3;c++) donor.data[offset+c]=Math.round(donor.data[offset+c]*(1-weight)+softened[offset+c]*weight);
  }

  // The garment patch follows the new upright collar and covers the old neckline.
  // All face and hair pixels remain above the protected boundary.
  const outline = `M 473 744
    C 453 758 431 796 414 830
    C 405 851 422 879 421 911
    C 416 970 402 1028 393 1078
    C 382 1140 370 1195 359 1254
    L 454 1254
    C 470 1200 500 1154 531 1100
    C 568 1038 609 973 635 924
    C 651 890 659 842 652 793
    L 640 788
    C 613 798 592 794 575 798
    C 566 799 563 807 560 819
    L 551 843
    C 546 850 538 845 530 832
    C 512 811 494 798 480 794
    C 476 789 470 770 473 744 Z`;
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
  const finalPath=path.join(__dirname,'perfil-montagem-gola-clara-2026-09-12-v12.png');
  fs.writeFileSync(finalPath,PNG.sync.write(composed,{colorType:2,inputColorType:6}));
  fs.writeFileSync(path.join(outputDir,'mascara-gola.png'),PNG.sync.write(maskRgba));
  const saved=PNG.sync.read(fs.readFileSync(finalPath));
  let changedInSavedFace=0;
  for(let y=0;y<740;y++) for(let x=0;x<base.width;x++) {
    const offset=(y*base.width+x)*4;
    if([0,1,2].some(c=>saved.data[offset+c]!==base.data[offset+c])) changedInSavedFace++;
  }
  if(changedInSavedFace) throw new Error('Saved PNG changed the protected face/hair region.');
  const previousComposite=PNG.sync.read(fs.readFileSync(path.join(__dirname,'perfil-montagem-camisa-branca-2026-09-12-v11.png')));
  let faceChangesVersusV11=0;
  for(let p=0;p<base.width*740;p++) if([0,1,2].some(c=>saved.data[p*4+c]!==previousComposite.data[p*4+c])) faceChangesVersusV11++;
  if(faceChangesVersusV11) throw new Error('Face/hair differ from the previous approved composition.');
  const audit={method:'Conventional masked composition of generated garment donor onto the approved portrait; original face pixels retained',basePath,donorPath,finalPath,width:base.width,height:base.height,protectedRegion:{left:0,top:0,width:base.width,height:740},changedPixelsInProtectedRegion:changedInSavedFace,changedFacePixelsVersusV11:faceChangesVersusV11,changedPixelsTotal:changed,changedPercentage:100*changed/(base.width*base.height),changedBounds:bounds,maskFeatherSigma:2.2,fabricFinish:'Local median/softening of donor knit panel; collar and zipper excluded; original face untouched',metadata};
  fs.writeFileSync(path.join(outputDir,'verificacao.json'),JSON.stringify(audit,null,2));
  await sharp(finalPath).extract(roi).png().toFile(path.join(outputDir,'montagem-detalhe.png'));
  console.log(JSON.stringify(audit,null,2));
}
main().catch(e=>{console.error(e);process.exit(1);});
