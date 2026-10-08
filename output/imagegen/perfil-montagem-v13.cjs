const fs=require('node:fs');
const path=require('node:path');
const {createRequire}=require('node:module');
const runtimeRequire=createRequire('C:/Users/Vitor Simões/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/_portrait.cjs');
const sharp=runtimeRequire('sharp');
const {PNG}=runtimeRequire('pngjs');
const basePath='C:/Users/Vitor Simões/Downloads/exec-e90ea39a-46e8-48db-a7e2-5627c6713e25.png';
const outputDir=path.join(__dirname,'montagem-v13');
const donorPath=path.join(outputDir,'doadora-gola.png');
const finalPath=path.join(__dirname,'perfil-montagem-gola-alta-2026-09-12-v13.png');

async function diagnosticCrop(source,destination,roi,step=25){
  let svg=`<svg width="${roi.width}" height="${roi.height}" xmlns="http://www.w3.org/2000/svg">`;
  for(let x=Math.ceil(roi.left/step)*step;x<roi.left+roi.width;x+=step) svg+=`<path d="M ${x-roi.left} 0 V ${roi.height}" stroke="cyan" stroke-opacity="0.45"/><text x="${x-roi.left+2}" y="14" font-size="11" fill="red">${x}</text>`;
  for(let y=Math.ceil(roi.top/step)*step;y<roi.top+roi.height;y+=step) svg+=`<path d="M 0 ${y-roi.top} H ${roi.width}" stroke="cyan" stroke-opacity="0.45"/><text x="0" y="${y-roi.top+12}" font-size="11" fill="red">${y}</text>`;
  svg+='</svg>';
  await sharp(source).extract(roi).composite([{input:Buffer.from(svg)}]).png().toFile(path.join(outputDir,destination));
}
async function main(){
  const base=PNG.sync.read(fs.readFileSync(basePath));
  const donor=PNG.sync.read(fs.readFileSync(donorPath));
  if(base.width!==donor.width||base.height!==donor.height) throw new Error('Image dimensions differ.');
  if(process.argv.includes('--inspect')){
    for(const [name,source] of [['base',basePath],['doadora',donorPath]]) {
      await diagnosticCrop(source,`${name}-rosto-grade.png`,{left:400,top:600,width:400,height:225});
      await diagnosticCrop(source,`${name}-roupa-grade.png`,{left:100,top:675,width:700,height:579},50);
    }
    return;
  }
  const width=base.width,height=base.height;
  const garment=`M 414 630
    C 383 659 354 701 315 745
    C 283 775 246 794 215 817
    C 195 834 182 850 171 873
    L 144 925 L 118 1002 L 101 1060 L 91 1110 L 72 1180 L 57 1254
    L 1254 1254 L 1254 1020
    C 1240 938 1156 880 1070 830
    C 1012 776 929 730 865 685
    L 900 585 L 735 580 Z`;
  // A conservative protected region covers the whole face, chin, hair and ears.
  // It extends below the visible beard/jaw edge so the raised collar can be
  // placed alongside the neck without replacing any part of the approved face.
  const face=`M 0 0 H ${width} V 600 H 850
    L 822 625 L 804 650 L 787 665 L 760 681 L 734 693
    L 709 706 L 684 718
    L 642 723 L 610 730 L 573 734 L 537 729 L 501 716
    L 479 700 L 466 680 L 440 650 L 419 625 L 400 600 H 0 Z`;
  const svgFor=d=>Buffer.from(`<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="black"/><path d="${d}" fill="white"/></svg>`);
  const faceSvg=svgFor(face);
  const [outerMask,faceGuard,faceFeather]=await Promise.all([
    sharp(svgFor(garment)).removeAlpha().grayscale().blur(6).raw().toBuffer(),
    sharp(faceSvg).removeAlpha().grayscale().raw().toBuffer(),
    sharp(faceSvg).removeAlpha().grayscale().blur(4).raw().toBuffer()
  ]);
  const composed=new PNG({width,height}),maskPng=new PNG({width,height});
  base.data.copy(composed.data);
  let changedPixelsTotal=0,changedPixelsOutsideMask=0,protectedPixels=0;
  const bounds={left:width,top:height,right:0,bottom:0};
  for(let p=0;p<width*height;p++) {
    const o=p*4,x=p%width,y=Math.floor(p/width);
    const protectedPixel=faceGuard[p]>0;
    if(protectedPixel) protectedPixels++;
    const alphaByte=protectedPixel?0:Math.round(outerMask[p]*(1-faceFeather[p]/255));
    const a=alphaByte/255;
    for(let c=0;c<3;c++) {
      composed.data[o+c]=Math.round(base.data[o+c]*(1-a)+donor.data[o+c]*a);
      maskPng.data[o+c]=alphaByte;
    }
    maskPng.data[o+3]=255;
    if([0,1,2].some(c=>composed.data[o+c]!==base.data[o+c])) {
      changedPixelsTotal++;
      if(protectedPixel||!alphaByte) changedPixelsOutsideMask++;
      bounds.left=Math.min(bounds.left,x);bounds.right=Math.max(bounds.right,x);
      bounds.top=Math.min(bounds.top,y);bounds.bottom=Math.max(bounds.bottom,y);
    }
  }
  if(changedPixelsOutsideMask) throw new Error('Protected or unmasked pixels changed.');
  fs.writeFileSync(finalPath,PNG.sync.write(composed,{colorType:2,inputColorType:6}));
  fs.writeFileSync(path.join(outputDir,'mascara-roupa.png'),PNG.sync.write(maskPng));
  await sharp(faceSvg).png().toFile(path.join(outputDir,'protecao-rosto.png'));
  const saved=PNG.sync.read(fs.readFileSync(finalPath));
  const previous=PNG.sync.read(fs.readFileSync(path.join(__dirname,'perfil-montagem-gola-clara-2026-09-12-v12.png')));
  let faceChangesVsBase=0,faceChangesVsV12=0;
  for(let p=0;p<width*height;p++) if(faceGuard[p]>0) {
    if([0,1,2].some(c=>saved.data[p*4+c]!==base.data[p*4+c])) faceChangesVsBase++;
    if([0,1,2].some(c=>saved.data[p*4+c]!==previous.data[p*4+c])) faceChangesVsV12++;
  }
  if(faceChangesVsBase||faceChangesVsV12) throw new Error('The saved portrait changed the protected face.');
  const audit={method:'Conventional masked wardrobe composition with a protected face; no generated face pixels used',basePath,donorPath,finalPath,width,height,protectedPixels,faceChangesVsBase,faceChangesVsV12,changedPixelsOutsideMask,changedPixelsTotal,changedPercentage:100*changedPixelsTotal/(width*height),changedBounds:bounds,clothing:'Higher light-gray collar; black jacket closed farther up to show less sweater'};
  fs.writeFileSync(path.join(outputDir,'verificacao.json'),JSON.stringify(audit,null,2));
  await sharp(finalPath).extract({left:380,top:650,width:420,height:430}).png().toFile(path.join(outputDir,'montagem-detalhe.png'));
  await sharp(finalPath).extract({left:760,top:590,width:160,height:190}).resize(480,570).png().toFile(path.join(outputDir,'borda-direita.png'));
  console.log(JSON.stringify(audit,null,2));
}
main().catch(e=>{console.error(e);process.exit(1);});
