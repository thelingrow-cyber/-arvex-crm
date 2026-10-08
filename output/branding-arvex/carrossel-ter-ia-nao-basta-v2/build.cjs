'use strict';

const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage, GlobalFonts } = require('@napi-rs/canvas');

const ROOT = __dirname;
const SLIDES = path.join(ROOT, 'slides');
const IMG = path.resolve(ROOT, '../sistema-editorial-v1/assets/maquete-escritorios-conexao-dourada-v1.png');
const LOGO = path.resolve(ROOT, '../logo-v1');
const W = 1080, H = 1350;
const P = {
  ink: '#171B18', green: '#23362F', greenDeep: '#14231E', paper: '#EFE9DD',
  cream: '#F7F2E8', brass: '#BA9860', brassLight: '#D5BB86', muted: '#69726B',
  white: '#F6F2E9', hair: '#A9A79E',
};

GlobalFonts.registerFromPath('C:/Windows/Fonts/georgia.ttf', 'Arvex Serif');
GlobalFonts.registerFromPath('C:/Windows/Fonts/georgiab.ttf', 'Arvex Serif Bold');
GlobalFonts.registerFromPath('C:/Windows/Fonts/georgiai.ttf', 'Arvex Serif Italic');
GlobalFonts.registerFromPath('C:/Windows/Fonts/bahnschrift.ttf', 'Arvex Sans');
fs.mkdirSync(SLIDES, { recursive: true });
const assets = {};

function font(ctx, px, family='Arvex Sans', weight='normal') { ctx.font = `${weight} ${px}px "${family}"`; }
function txt(ctx, s, x, y, px, color, family='Arvex Sans', weight='normal', align='left') {
  ctx.fillStyle=color; ctx.textAlign=align; font(ctx,px,family,weight); ctx.fillText(s,x,y); ctx.textAlign='left';
}
function lines(ctx, arr, x, y, px, leading, color, family='Arvex Sans', weight='normal') {
  arr.forEach((s,i)=>txt(ctx,s,x,y+i*leading,px,color,family,weight));
}
function rule(ctx,x1,y1,x2,y2,color=P.brass,width=2){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();}
function joint(ctx,x,y,r=8,color=P.brass){ctx.fillStyle=color;ctx.fillRect(x-r/2,y-r/2,r,r);}
function circle(ctx,x,y,r,color,width=2){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.stroke();}
function bg(ctx,color=P.paper){ctx.fillStyle=color;ctx.fillRect(0,0,W,H);}
function grain(ctx,seed=1,n=12000){let s=seed;ctx.fillStyle='rgba(24,31,26,.055)';for(let i=0;i<n;i++){s=(s*1664525+1013904223)>>>0;const x=s%W;s=(s*1664525+1013904223)>>>0;const y=s%H;ctx.fillRect(x,y,1,1);}}
function imageCover(ctx,img,x,y,w,h,sx=0,sy=0,sw=img.width,sh=img.height){
  const sourceRatio=sw/sh,target=w/h;let cx=sx,cy=sy,cw=sw,ch=sh;
  if(sourceRatio>target){cw=sh*target;cx=sx+(sw-cw)/2;}else{ch=sw/target;cy=sy+(sh-ch)/2;}
  ctx.drawImage(img,cx,cy,cw,ch,x,y,w,h);
}
function imageTreatment(ctx,x,y,w,h){
  ctx.save();ctx.globalCompositeOperation='multiply';ctx.fillStyle='rgba(50,67,51,.16)';ctx.fillRect(x,y,w,h);ctx.restore();
}
function logo(ctx,dark=false,x=64,y=54,w=160){const img=dark?assets.logoLight:assets.logoDark;ctx.drawImage(img,x,y,w,w*img.height/img.width);}
function folio(ctx,page,section,dark=false){
  const fg=dark?P.white:P.ink,thin=dark?'rgba(247,242,232,.40)':'rgba(23,27,24,.32)';
  logo(ctx,dark);txt(ctx,`ARVEX / ${section}`,1016,82,21,fg,'Arvex Sans','normal','right');
  rule(ctx,64,128,1016,128,thin,1);rule(ctx,64,1256,1016,1256,thin,1);
  txt(ctx,'CADERNO DE ARQUITETURA DE NEGÓCIOS',64,1301,19,fg);
  txt(ctx,`${String(page).padStart(2,'0')} / 07`,1016,1301,20,fg,'Arvex Sans','normal','right');
}
function tag(ctx,s,x,y,dark=false){txt(ctx,s,x,y,23,dark?P.brassLight:P.green,'Arvex Sans');}
function arrow(ctx,x,y,color=P.brass){rule(ctx,x,y,x+45,y,color,3);rule(ctx,x+45,y,x+32,y-10,color,3);rule(ctx,x+45,y,x+32,y+10,color,3);}

function cover(ctx){
  bg(ctx,P.greenDeep);
  imageCover(ctx,assets.model,0,0,W,1050);
  imageTreatment(ctx,0,0,W,1050);
  const g=ctx.createLinearGradient(0,370,0,1160);
  g.addColorStop(0,'rgba(15,25,20,0)');g.addColorStop(.45,'rgba(15,25,20,.27)');g.addColorStop(.78,'rgba(15,25,20,.91)');g.addColorStop(1,P.greenDeep);
  ctx.fillStyle=g;ctx.fillRect(0,370,W,790);
  logo(ctx,true);txt(ctx,'ENSAIO / 01',1016,82,23,P.white,'Arvex Sans','normal','right');
  rule(ctx,64,128,1016,128,'rgba(246,242,233,.54)',1);
  tag(ctx,'UMA TESE SOBRE ARQUITETURA DE NEGÓCIOS',64,724,true);
  lines(ctx,['Ter IA não','basta.'],64,850,114,119,P.white,'Arvex Serif Bold');
  rule(ctx,64,1055,1016,1055,P.brassLight,2);joint(ctx,610,1055,15,P.brassLight);
  lines(ctx,['A empresa precisa funcionar','com ela.'],64,1120,43,54,P.white,'Arvex Serif Italic');
  rule(ctx,64,1256,1016,1256,'rgba(246,242,233,.35)',1);
  txt(ctx,'ARVEX / ARQUITETURA DE NEGÓCIOS',64,1301,19,P.white);
  txt(ctx,'ARRASTE PARA O LADO',1016,1301,19,P.brassLight,'Arvex Sans','normal','right');
  grain(ctx,17,17000);
}

function slide2(ctx){
  bg(ctx);folio(ctx,2,'TESE');tag(ctx,'01 / A ARMADILHA',64,217);
  lines(ctx,['Ferramenta','nova.'],64,368,105,111,P.ink,'Arvex Serif Bold');
  lines(ctx,['Gargalo','antigo.'],64,608,105,111,P.green,'Arvex Serif Italic');
  rule(ctx,64,765,1016,765,P.brass,3);joint(ctx,455,765,14);
  txt(ctx,'O problema não é falta de software.',64,847,43,P.ink,'Arvex Sans');
  lines(ctx,['Processos e decisões separados fazem a IA','encontrar a mesma operação fragmentada.'],64,916,32,47,P.muted,'Arvex Sans');
  ctx.fillStyle=P.green;ctx.fillRect(64,1060,952,137);
  txt(ctx,'A arquitetura vem antes da automação.',91,1144,43,P.white,'Arvex Serif Bold');
  grain(ctx,29);
}

function slide3(ctx){
  bg(ctx,P.green);folio(ctx,3,'DIAGNÓSTICO',true);tag(ctx,'02 / ONDE COMEÇAR',64,220,true);
  lines(ctx,['Encontre o','ponto de perda.'],64,357,94,105,P.white,'Arvex Serif Bold');
  txt(ctx,'Antes de automatizar, observe a operação.',64,557,34,P.brassLight);
  const blocks=[
    ['01','Onde o lead','deixa de avançar?'],['02','O que se repete','todos os dias?'],
    ['03','O que depende','do dono?'],['04','Onde o contexto','se perde?']
  ];
  const xs=[64,555],ys=[665,920];
  blocks.forEach((b,i)=>{
    const x=xs[i%2],y=ys[Math.floor(i/2)];
    rule(ctx,x,y-35,x+451,y-35,'rgba(246,242,233,.43)',1);
    txt(ctx,b[0],x,y+30,61,P.brassLight,'Arvex Serif Italic');
    lines(ctx,[b[1],b[2]],x,y+94,38,51,P.white,'Arvex Sans');
    joint(ctx,x+451,y-35,10,P.brassLight);
  });
  txt(ctx,'O gargalo revela a primeira peça.',64,1194,47,P.brassLight,'Arvex Serif Italic');
  grain(ctx,41);
}

function annotation(ctx,num,x,y,toX,toY){
  circle(ctx,x,y,27,P.brassLight,2);txt(ctx,num,x,y+10,27,P.white,'Arvex Sans','normal','center');
  rule(ctx,x+27,y,toX,toY,P.brassLight,2);joint(ctx,toX,toY,9,P.brassLight);
}
function slide4(ctx){
  bg(ctx);folio(ctx,4,'REARQUITETAR');tag(ctx,'03 / O DESENHO DA OPERAÇÃO',64,214);
  lines(ctx,['Dê um papel claro','a cada parte.'],64,320,82,93,P.ink,'Arvex Serif Bold');
  ctx.save();ctx.beginPath();ctx.rect(64,480,952,467);ctx.clip();imageCover(ctx,assets.model,64,480,952,467);imageTreatment(ctx,64,480,952,467);
  ctx.fillStyle='rgba(18,30,23,.29)';ctx.fillRect(64,480,952,467);ctx.restore();
  annotation(ctx,'1',166,581,297,646);annotation(ctx,'2',925,585,826,674);annotation(ctx,'3',557,877,555,634);
  const roles=[['01','PESSOAS','julgamento, relação','e exceções'],['02','SISTEMAS','regras, dados','e contexto'],['03','IA','execução, resposta','e monitoramento']];
  roles.forEach((r,i)=>{
    const x=64+i*326;rule(ctx,x,984,x+300,984,P.brass,2);joint(ctx,x,984,11);
    txt(ctx,r[0],x,1031,25,P.brass,'Arvex Serif Italic');
    txt(ctx,r[1],x,1082,32,P.green,'Arvex Sans');
    lines(ctx,[r[2],r[3]],x,1128,28,36,P.ink,'Arvex Sans');
  });
  grain(ctx,53);
}

function slide5(ctx){
  bg(ctx,P.cream);folio(ctx,5,'APLICAÇÃO');tag(ctx,'04 / NA PRÁTICA',64,215);
  lines(ctx,['Menos memória.','Mais continuidade.'],64,334,81,92,P.green,'Arvex Serif Bold');
  txt(ctx,'ANTES',64,577,24,P.muted);txt(ctx,'DEPOIS',592,577,24,P.green);
  const rows=[['Espera','Resposta'],['Dependência','Continuidade'],['Controle total','Exceções']];
  rows.forEach((r,i)=>{
    const y=682+i*148;rule(ctx,64,y-61,1016,y-61,P.hair,1);
    txt(ctx,r[0],64,y,45,P.muted,'Arvex Serif Italic');
    rule(ctx,448,y-12,545,y-12,P.brass,3);joint(ctx,545,y-12,12);
    txt(ctx,r[1],592,y,47,P.ink,'Arvex Serif Bold');
  });
  rule(ctx,64,1065,1016,1065,P.hair,1);
  ctx.fillStyle=P.green;ctx.fillRect(64,1102,15,95);
  lines(ctx,['Autonomia libera pessoas para julgamento,','relação e exceções.'],104,1143,32,45,P.ink,'Arvex Sans');
  grain(ctx,67);
}

function slide6(ctx){
  bg(ctx,P.ink);folio(ctx,6,'IMPLEMENTAR',true);tag(ctx,'05 / A ORDEM IMPORTA',64,217,true);
  lines(ctx,['Uma peça','por vez.'],64,347,103,113,P.white,'Arvex Serif Bold');
  txt(ctx,'Comece pelo gargalo identificado.',64,546,34,P.brassLight);
  const steps=[['01','DIAGNOSTICAR','encontrar o ponto de perda'],['02','REDESENHAR','definir o novo fluxo'],['03','IMPLEMENTAR','colocar a peça para funcionar'],['04','MEDIR','verificar antes de ampliar']];
  const ys=[645,790,935,1080];
  rule(ctx,113,665,113,1097,P.brass,3);
  steps.forEach((s,i)=>{
    const y=ys[i];circle(ctx,113,y,19,P.brassLight,2);ctx.fillStyle=P.ink;ctx.fillRect(106,y-8,14,17);
    txt(ctx,s[0],113,y+8,19,P.brassLight,'Arvex Sans','normal','center');
    txt(ctx,s[1],172,y+1,37,P.white);
    txt(ctx,s[2],172,y+46,27,P.brassLight);
  });
  txt(ctx,'Cada peça funciona antes da próxima.',64,1194,43,P.white,'Arvex Serif Italic');
  grain(ctx,79);
}

function slide7(ctx){
  bg(ctx,P.greenDeep);
  imageCover(ctx,assets.model,0,0,W,775,assets.model.width*.18,0,assets.model.width*.64,assets.model.height*.75);
  imageTreatment(ctx,0,0,W,775);
  const fade=ctx.createLinearGradient(0,330,0,900);fade.addColorStop(0,'rgba(20,35,30,0)');fade.addColorStop(.7,'rgba(20,35,30,.86)');fade.addColorStop(1,P.greenDeep);ctx.fillStyle=fade;ctx.fillRect(0,330,W,570);
  logo(ctx,true);txt(ctx,'FECHO / 07',1016,82,22,P.white,'Arvex Sans','normal','right');rule(ctx,64,128,1016,128,'rgba(246,242,233,.50)',1);
  tag(ctx,'A ARQUITETURA É A VANTAGEM',64,565,true);
  lines(ctx,['Ter IA é só','o começo.'],64,688,102,109,P.white,'Arvex Serif Bold');
  lines(ctx,['Faça a empresa','funcionar com ela.'],64,942,70,81,P.brassLight,'Arvex Serif Italic');
  rule(ctx,64,1081,1016,1081,P.brassLight,2);joint(ctx,670,1081,14,P.brassLight);
  txt(ctx,'Qual parte ainda depende de você?',64,1144,35,P.white);
  txt(ctx,'CONHEÇA A ARVEX',64,1207,25,P.brassLight);arrow(ctx,329,1198,P.brassLight);
  rule(ctx,64,1256,1016,1256,'rgba(246,242,233,.35)',1);
  txt(ctx,'CADERNO DE ARQUITETURA DE NEGÓCIOS',64,1301,19,P.white);
  txt(ctx,'07 / 07',1016,1301,20,P.white,'Arvex Sans','normal','right');
  grain(ctx,91,17000);
}

async function main(){
  [assets.model,assets.logoDark,assets.logoLight]=await Promise.all([
    loadImage(IMG),loadImage(path.join(LOGO,'arvex-wordmark-light.png')),
    loadImage(path.join(LOGO,'arvex-wordmark-dark.png'))
  ]);
  const renderers=[cover,slide2,slide3,slide4,slide5,slide6,slide7];
  const images=[];
  for(let i=0;i<7;i++){
    const c=createCanvas(W,H);renderers[i](c.getContext('2d'));
    const file=path.join(SLIDES,`${String(i+1).padStart(2,'0')}.png`);
    fs.writeFileSync(file,await c.encode('png'));images.push(c);
  }
  const sheet=createCanvas(1452,912),ctx=sheet.getContext('2d');bgSheet(ctx,sheet.width,sheet.height);
  images.forEach((c,i)=>ctx.drawImage(c,40+(i%4)*350,38+Math.floor(i/4)*435,324,405));
  fs.writeFileSync(path.join(ROOT,'contact-sheet.png'),await sheet.encode('png'));
  const figs=images.map((_,i)=>`<figure><img src="slides/${String(i+1).padStart(2,'0')}.png" alt="Slide ${i+1}"><figcaption>${String(i+1).padStart(2,'0')} / 07</figcaption></figure>`).join('');
  fs.writeFileSync(path.join(ROOT,'index.html'),`<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ARVEX — Ter IA não basta · v2</title><style>*{box-sizing:border-box}body{margin:0;background:#14231e;color:#f6f2e9;font-family:Georgia,serif}header{padding:36px 4vw;border-bottom:1px solid #ba9860}h1{margin:0;font-size:40px}p{color:#d5bb86}.grid{padding:32px 4vw;display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:26px}figure{margin:0}img{display:block;width:100%}figcaption{padding:10px 0;color:#d5bb86;font:16px Arial}</style></head><body><header><h1>Ter IA não basta.</h1><p>ARVEX · edição mineral editorial v2 · 1080 × 1350</p></header><main class="grid">${figs}</main></body></html>`);
  process.stdout.write(`${path.join(ROOT,'contact-sheet.png')}\n`);
}
function bgSheet(ctx,w,h){ctx.fillStyle=P.paper;ctx.fillRect(0,0,w,h);}
main().catch(e=>{console.error(e);process.exitCode=1;});
