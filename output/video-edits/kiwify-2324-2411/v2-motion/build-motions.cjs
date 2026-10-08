/* Local motion assets for kiwify-2324-2411-primeiro-teste.story.md. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const { createCanvas, GlobalFonts } = require('@napi-rs/canvas');
const dir = __dirname;
const root = path.resolve(dir, '../../../..');
const ffmpeg = path.join(root, 'output/video-tools/node_modules/ffmpeg-static/ffmpeg.exe');
GlobalFonts.registerFromPath('C:/Windows/Fonts/segoeuib.ttf', 'MotionBold');
GlobalFonts.registerFromPath('C:/Windows/Fonts/segoeui.ttf', 'MotionRegular');
const W=1080,H=1920,FPS=30;
const C={paper:'#f0eee7',ink:'#171d20',muted:'#6c7477',gold:'#d2ae53',green:'#1d3d35',line:'#b7c0b5',white:'#fffefa'};
const clamp=x=>Math.max(0,Math.min(1,x));
const ease=x=>1-Math.pow(1-clamp(x),3);
function rr(ctx,x,y,w,h,r,fill){ctx.fillStyle=fill;ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fill();}
function text(ctx,s,x,y,size=48,color=C.ink,align='left',bold=true){ctx.fillStyle=color;ctx.textAlign=align;ctx.font=`${size}px ${bold?'MotionBold':'MotionRegular'}`;ctx.fillText(s,x,y);}
function line(ctx,a,b,p=1,color=C.line,width=4){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(a[0]+(b[0]-a[0])*clamp(p),a[1]+(b[1]-a[1])*clamp(p));ctx.stroke();}
function dot(ctx,x,y,r,color){ctx.fillStyle=color;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();}
function enter(ctx,t,start,dur,draw){const p=ease((t-start)/dur);if(p<=0)return;ctx.save();ctx.globalAlpha=p;ctx.translate(0,(1-p)*28);draw(p);ctx.restore();}
function background(ctx,t,label='ILUSTRAÇÃO CONCEITUAL'){
 ctx.fillStyle=C.paper;ctx.fillRect(0,0,W,H);
 ctx.fillStyle='#dfe1d8';for(let x=28;x<W;x+=56)for(let y=30;y<H;y+=56)dot(ctx,x,y,1.4,'#dfe1d8');
 const g=ctx.createRadialGradient(865+15*Math.sin(t),620,20,865,620,630);g.addColorStop(0,'rgba(222,204,156,.2)');g.addColorStop(1,'rgba(222,204,156,0)');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
 text(ctx,'NEGÓCIOS  /  VISÃO',100,210,27,C.muted);rr(ctx,100,243,72,6,3,C.gold);
 text(ctx,label,100,1650,23,C.muted);
}
function ecosystem(ctx,t){
 background(ctx,t);enter(ctx,t,0,.25,()=>{text(ctx,'Uma marca.',100,405,81);text(ctx,'Um ecossistema.',100,510,81);});
 const nodes=[{x:125,y:670,label:'CONTEÚDO'},{x:610,y:670,label:'PRODUTOS'},{x:125,y:1120,label:'COMUNIDADE'},{x:610,y:1120,label:'TECNOLOGIA'}];
 nodes.forEach((n,i)=>{const p=ease((t-.22-i*.17)/.46),center=[n.x+170,n.y+72];line(ctx,[540,959],center,p,C.line,4);if(p>.95){const k=((t*.37+i*.22)%1);dot(ctx,540+(center[0]-540)*k,959+(center[1]-959)*k,5,C.gold);}});
 nodes.forEach((n,i)=>enter(ctx,t,.31+i*.17,.4,()=>{ctx.save();ctx.shadowColor='rgba(18,33,25,.09)';ctx.shadowBlur=25;ctx.shadowOffsetY=9;rr(ctx,n.x,n.y,340,146,18,C.white);ctx.restore();rr(ctx,n.x+25,n.y+23,30,5,2,C.gold);text(ctx,n.label,n.x+170,n.y+91,30,C.ink,'center');}));
 enter(ctx,t,.1,.3,()=>{rr(ctx,295,868,490,176,22,C.green);text(ctx,'MARCA PESSOAL',540,974,42,C.paper,'center');});
}
function aiCreate(ctx,t){
 background(ctx,t,'SIMULAÇÃO VISUAL');enter(ctx,t,0,.2,()=>{text(ctx,'Da ideia',100,405,81);text(ctx,'à experiência.',100,510,81);});
 enter(ctx,t,.06,.24,()=>{
  ctx.save();ctx.shadowColor='rgba(18,33,25,.10)';ctx.shadowBlur=36;ctx.shadowOffsetY=15;rr(ctx,95,606,890,746,26,C.white);ctx.restore();
  rr(ctx,95,606,890,71,25,C.green);ctx.fillStyle=C.green;ctx.fillRect(95,640,890,37);[0,1,2].forEach(i=>dot(ctx,127+i*24,641,6,i===0?C.gold:'#8a9e92'));
  text(ctx,'CRIAÇÃO COM IA',550,650,22,C.paper,'center');
  rr(ctx,124,708,832,104,13,'#eceee7');
  const prompt='Criar uma experiência digital';const progress=clamp((t-.18)/.65),typed=prompt.slice(0,Math.floor(progress*prompt.length));
  text(ctx,typed,152,773,33,C.green,'left',false);
  ctx.font='33px MotionRegular';const cursorX=152+ctx.measureText(typed).width+5;
  if(t<1.2&&Math.floor(t*8)%2===0)rr(ctx,cursorX,742,3,38,0,C.gold);
  enter(ctx,t,.72,.27,()=>{rr(ctx,124,843,832,61,9,C.green);text(ctx,'EXPERIÊNCIA DIGITAL',155,883,23,C.paper);rr(ctx,790,865,131,16,8,'#667f69');});
  enter(ctx,t,.86,.3,()=>{rr(ctx,124,926,458,222,12,'#e5e8df');text(ctx,'Ideias que',151,1002,38,C.green);text(ctx,'ganham forma.',151,1054,38,C.green);rr(ctx,151,1093,175,25,12,C.gold);});
  enter(ctx,t,1.02,.36,()=>{rr(ctx,603,926,353,222,12,C.green);ctx.save();ctx.beginPath();ctx.roundRect(603,926,353,222,12);ctx.clip();const k=ease((t-1.02)/.65);dot(ctx,813,1040,79+4*Math.sin(t*3),C.gold);dot(ctx,754,994,67,'#69876c');ctx.strokeStyle=C.paper;ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(792,1039,116,53,-.4*k,0,Math.PI*2);ctx.stroke();ctx.restore();});
  for(let i=0;i<3;i++)enter(ctx,t,1.12+i*.1,.32,()=>{rr(ctx,124+i*286,1170,260,109,11,'#e5e8df');rr(ctx,145+i*286,1193,39,8,4,C.gold);rr(ctx,145+i*286,1219,171,9,4,'#a6b4a3');rr(ctx,145+i*286,1240,123,7,3,'#c4cbc0');});
  enter(ctx,t,1.59,.22,()=>{dot(ctx,150,1310,12,C.green);line(ctx,[144,1310],[149,1315],1,C.paper,3);line(ctx,[149,1315],[157,1305],1,C.paper,3);text(ctx,'Estrutura criada',174,1320,23,C.green);});
 });
}
function funnel(ctx,t){
 background(ctx,t);enter(ctx,t,0,.22,()=>{text(ctx,'Além de',100,405,84);text(ctx,'um único funil.',100,510,84);});
 enter(ctx,t,.07,.3,()=>{ctx.fillStyle='#d4dbd0';ctx.beginPath();ctx.moveTo(270,625);ctx.lineTo(810,625);ctx.lineTo(610,805);ctx.lineTo(610,875);ctx.lineTo(470,875);ctx.lineTo(470,805);ctx.closePath();ctx.fill();text(ctx,'UMA ESTRATÉGIA',540,716,32,C.ink,'center');});
 const xs=[243,540,837],labels=['MARCA','COMUNIDADE','TECNOLOGIA'];
 xs.forEach((x,i)=>{const p=ease((t-.38-i*.1)/.43);line(ctx,[540,879],[x,1011],p,C.gold,4);line(ctx,[x,1099],[540,1210],ease((t-.95-i*.08)/.38),C.line,3);enter(ctx,t,.58+i*.11,.3,()=>{rr(ctx,x-130,1010,260,90,16,C.white);text(ctx,labels[i],x,1066,24,C.green,'center');});});
 enter(ctx,t,1.12,.36,()=>{rr(ctx,190,1210,700,140,20,C.green);text(ctx,'EXPANSÃO DA MARCA',540,1297,41,C.paper,'center');});
}
async function render(name,seconds,draw){
 const output=path.join(dir,name+'.mp4');if(fs.existsSync(output)){console.log('Preserved existing '+output);return;}
 const frames=Math.round(seconds*FPS),canvas=createCanvas(W,H),ctx=canvas.getContext('2d');
 const args=['-hide_banner','-loglevel','error','-nostdin','-n','-f','rawvideo','-pixel_format','rgba','-video_size',`${W}x${H}`,'-framerate',String(FPS),'-i','pipe:0','-an','-frames:v',String(frames),'-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',output];
 const child=spawn(ffmpeg,args,{windowsHide:true,stdio:['pipe','ignore','pipe']});let errors='';child.stderr.on('data',v=>errors+=v.toString());const done=new Promise((resolve,reject)=>{child.once('error',reject);child.once('close',code=>code===0?resolve():reject(new Error(errors||`ffmpeg ${code}`)));});
 for(let i=0;i<frames;i++){draw(ctx,i/FPS);if(i===Math.round(frames*.7))fs.writeFileSync(path.join(dir,name+'-preview.png'),canvas.toBuffer('image/png'));if(!child.stdin.write(Buffer.from(ctx.getImageData(0,0,W,H).data)))await once(child.stdin,'drain');}
 child.stdin.end();await done;console.log(JSON.stringify({output,seconds:frames/FPS,frames,width:W,height:H,fps:FPS,audio:false}));
}
(async()=>{await render('ecosystem',2.7,ecosystem);await render('ai-create',2,aiCreate);await render('funnel',2.1,funnel);})().catch(e=>{console.error(e);process.exitCode=1;});
