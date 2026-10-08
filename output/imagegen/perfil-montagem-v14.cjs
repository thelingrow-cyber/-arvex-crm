const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {createRequire} = require('node:module');
const runtimeRequire = createRequire('C:/Users/Vitor Simões/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/_portrait.cjs');
const sharp = runtimeRequire('sharp');
const {PNG} = runtimeRequire('pngjs');
const dir = path.join(__dirname,'montagem-v14');
const basePath = 'C:/Users/Vitor Simões/Downloads/exec-e90ea39a-46e8-48db-a7e2-5627c6713e25.png';
const donorPath = path.join(dir,'doadora-gola.png');
const cropSource = 'C:/Users/Vitor Simões/.codex/generated_images/01a0936b-0db6-77c2-b860-dd28e0ea4ef4/exec-4e124fe9-d101-48c0-abef-076533020734.png';
const finalPath = path.join(__dirname,'perfil-montagem-sueter-aberto-2026-09-12-v14.png');
const smooth = v => {const t=Math.max(0,Math.min(1,v));return t*t*(3-2*t);};

async function main() {
  const base = PNG.sync.read(fs.readFileSync(basePath));
  const donor = PNG.sync.read(fs.readFileSync(donorPath));
  if(base.width!==1254 || base.height!==1254 || donor.width!==1254 || donor.height!==1254) throw Error('Unexpected source dimensions');
  fs.copyFileSync(cropSource,path.join(dir,'doadora-tecido-recorte.png'));
  const crop = await sharp(cropSource).resize(340,514,{fit:'fill',kernel:'lanczos3'}).ensureAlpha().raw().toBuffer();
  // Only the donor garment crop is downsampled. The approved portrait is never resized.
  for(let y=0;y<514;y++) for(let x=0;x<340;x++) {
    const i=((y+740)*1254+x+350)*4, j=(y*340+x)*4;
    const a=smooth(y/9);
    for(let c=0;c<3;c++) donor.data[i+c]=Math.round(donor.data[i+c]*(1-a)+crop[j+c]*a);
  }
  fs.writeFileSync(path.join(dir,'doadora-roupa-final.png'),PNG.sync.write(donor,{colorType:2,inputColorType:6}));
  const outline=`M 476 710
    C 464 718 449 735 427 752
    C 416 760 409 766 410 774
    C 414 787 435 810 447 835
    C 437 850 421 870 419 899
    C 416 970 402 1028 393 1078
    C 382 1140 370 1195 359 1254
    L 454 1254
    C 470 1200 500 1154 531 1100
    C 568 1038 609 973 635 924
    C 644 888 645 844 640 803
    L 628 806
    C 618 805 603 802 593 812
    C 585 821 580 830 577 843
    C 551 849 523 846 502 836
    C 488 822 481 800 480 773
    C 477 750 476 729 476 710 Z`;
  const guardOutline=`M 0 0 H 1254 V 600 H 850
    L 822 625 L 804 650 L 787 665 L 760 681 L 734 693 L 709 706 L 684 718
    L 642 723 L 610 730 L 573 734 L 537 729 L 501 716 L 479 700 L 466 680
    L 440 650 L 419 625 L 400 600 H 0 Z`;
  const svg = d => Buffer.from(`<svg width="1254" height="1254" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="black"/><path d="${d}" fill="white"/></svg>`);
  const mask=await sharp(svg(outline)).removeAlpha().grayscale().blur(1.25).raw().toBuffer();
  const guard=await sharp(svg(guardOutline)).removeAlpha().grayscale().raw().toBuffer();
  const guardFeather=await sharp(guard,{raw:{width:1254,height:1254,channels:1}}).grayscale().blur(2).raw().toBuffer();
  if([mask,guard,guardFeather].some(m=>m.length!==1254*1254)) throw Error('Mask must have one channel');
  const composed = new PNG({width:1254,height:1254}); base.data.copy(composed.data);
  const maskPng = new PNG({width:1254,height:1254});
  for(let y=0;y<1254;y++) for(let x=0;x<1254;x++) {
    const p=y*1254+x, i=p*4;
    let a=mask[p]/255;
    // Original neck is retained above the clothing join; feather only below it.
    if(y>=805 && y<960 && x>=479 && x<=642) {
      const neckBlend=smooth((y-805)/75)*smooth((x-479)/22)*(1-smooth((x-614)/28))*(1-smooth((y-930)/30));
      a=Math.max(a,neckBlend);
    }
    a=guard[p]>0 ? 0 : a*(1-guardFeather[p]/255);
    for(let c=0;c<3;c++) {
      composed.data[i+c]=Math.round(base.data[i+c]*(1-a)+donor.data[i+c]*a);
      maskPng.data[i+c]=Math.round(a*255);
    }
    maskPng.data[i+3]=255;
  }
  fs.writeFileSync(finalPath,PNG.sync.write(composed,{colorType:2,inputColorType:6}));
  fs.writeFileSync(path.join(dir,'mascara-roupa.png'),PNG.sync.write(maskPng));
  await sharp(guard,{raw:{width:1254,height:1254,channels:1}}).png().toFile(path.join(dir,'protecao-rosto.png'));
  const saved = PNG.sync.read(fs.readFileSync(finalPath));
  const v11=PNG.sync.read(fs.readFileSync(path.join(__dirname,'perfil-montagem-camisa-branca-2026-09-12-v11.png')));
  let protectedPixels=0,faceChanges=0,faceChangesVsV11=0,changes=0;
  const bounds={left:1254,top:1254,right:0,bottom:0};
  for(let p=0;p<1254*1254;p++) {
    const i=p*4, different=[0,1,2].some(c=>saved.data[i+c]!==base.data[i+c]);
    if(guard[p]>0) {
      protectedPixels++;
      if(different) faceChanges++;
      if([0,1,2].some(c=>saved.data[i+c]!==v11.data[i+c])) faceChangesVsV11++;
    }
    if(different) {
      changes++;const x=p%1254,y=Math.floor(p/1254);
      bounds.left=Math.min(bounds.left,x);bounds.right=Math.max(bounds.right,x);
      bounds.top=Math.min(bounds.top,y);bounds.bottom=Math.max(bounds.bottom,y);
    }
  }
  if(faceChanges || faceChangesVsV11) throw Error('Protected face differs from approved base or v11');
  if(changes<50000 || changes>150000) throw Error('Garment coverage outside expected range');
  const audit={method:'Conventional masked garment montage over approved v5; no resize or filter applied to the approved portrait',basePath,baseSha256:crypto.createHash('sha256').update(fs.readFileSync(basePath)).digest('hex'),finalPath,donorPath,cropSource,width:1254,height:1254,protectedPixels,changedFacePixelsVsApprovedBase:faceChanges,changedFacePixelsVsV11:faceChangesVsV11,changedPixelsTotal:changes,changedPercentage:100*changes/(1254*1254),changedBounds:bounds,maskFeatherSigma:1.25};
  fs.writeFileSync(path.join(dir,'verificacao.json'),JSON.stringify(audit,null,2));
  await sharp(finalPath).extract({left:350,top:695,width:340,height:559}).png().toFile(path.join(dir,'montagem-detalhe.png'));
  console.log(JSON.stringify(audit,null,2));
}
main().catch(e=>{console.error(e);process.exit(1);});
