'use strict';
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process'),{once}=require('node:events');
const {createCanvas,GlobalFonts}=require('@napi-rs/canvas');
const ff=path.resolve(__dirname,'../../../video-tools/node_modules/ffmpeg-static/ffmpeg.exe');
GlobalFonts.registerFromPath('C:/Windows/Fonts/segoeuib.ttf','Bold');
const W=1080,H=1920,gold='#e6c982',white='#f5f2e9',muted='#9fa9ab';
const clamp=x=>Math.min(1,Math.max(0,x)),ease=x=>1-(1-clamp(x))**3;
function text(x,s,a,b,size,color=white){x.font=`${size}px Bold`;x.fillStyle=color;x.fillText(s,a,b);}
function line(x,pts,color=gold,width=3){x.beginPath();x.moveTo(...pts[0]);pts.slice(1).forEach(p=>x.lineTo(...p));x.strokeStyle=color;x.lineWidth=width;x.stroke();}
function dot(x,a,b,r,color=gold){x.beginPath();x.arc(a,b,r,0,Math.PI*2);x.fillStyle=color;x.fill();}
function bg(x,t){x.fillStyle='#10191e';x.fillRect(0,0,W,H);const g=x.createRadialGradient(540,830,5,540,830,800);g.addColorStop(0,'#263a3c');g.addColorStop(1,'#10191e');x.fillStyle=g;x.fillRect(0,0,W,H);x.globalAlpha=.10;for(let i=-8;i<16;i++)line(x,[[i*110+t*16,0],[i*110-650+t*16,H]],'#acbab8',1);x.globalAlpha=1;line(x,[[100,290],[170,290]],gold,5);}
function cube(x,cx,cy,s,p,alpha=1){x.save();x.globalAlpha=alpha;const h=s*.55,pts=[[cx,cy-h],[cx+s,cy],[cx,cy+h],[cx-s,cy],[cx,cy-h]];line(x,pts,gold,2.4);line(x,[[cx-s,cy],[cx-s,cy+s*p],[cx,cy+s*p+h],[cx+s,cy+s*p],[cx+s,cy]],gold,2.4);line(x,[[cx,cy+h],[cx,cy+s*p+h]],gold,2.4);x.restore();}
function ai(x,t){bg(x,t);const p=ease(t/.4);x.save();x.globalAlpha=p;text(x,'Da ideia',100,445,86);text(x,'à criação.',100,547,86);x.restore();
 for(let i=0;i<7;i++){const a=i*Math.PI*2/7+t*.13,sx=540+400*Math.cos(a),sy=930+330*Math.sin(a);line(x,[[sx,sy],[540,930]],'#4d6567',1.5);const q=(t*.65+i*.17)%1;dot(x,sx+(540-sx)*q,sy+(930-sy)*q,4);}
 const cells=[[-1,0],[0,-1],[1,0],[0,1],[0,0]];cells.forEach(([a,b],i)=>{const q=ease((t-.12-i*.16)/.6);cube(x,540+a*138,820+b*104+(1-q)*190,120*q,q,q);});
 const scan=705+(t*.55%1)*540;x.save();x.globalAlpha=.25;line(x,[[220,scan],[860,scan]],gold,2);x.restore();
 const k=ease((t-1.15)/.5);x.save();x.globalAlpha=k;text(x,'IA × TECNOLOGIA',100,1280,51,gold);x.restore();
}
function funnel(x,t){bg(x,t);text(x,'Além de',100,445,86);text(x,'um único funil.',100,547,82);const p=ease(t/.55);x.save();x.globalAlpha=p;
 x.strokeStyle=gold;x.lineWidth=4;x.beginPath();x.ellipse(540,730,290,72,0,0,Math.PI*2);x.stroke();
 line(x,[[250,730],[465,1010],[465,1080]],gold,4);line(x,[[830,730],[615,1010],[615,1080]],gold,4);
 for(let i=0;i<4;i++){const q=((t*.5+i*.24)%1),y=758+q*270,r=270*(1-q)+74*q;x.strokeStyle=`rgba(230,201,130,${.18+.4*q})`;x.lineWidth=2;x.beginPath();x.ellipse(540,y,r,24+38*(1-q),0,0,Math.PI*2);x.stroke();}
 x.restore();const xs=[245,540,835],labels=['MARCA','COMUNIDADE','TECH'];xs.forEach((a,i)=>{const q=ease((t-.6-i*.12)/.45);x.save();x.globalAlpha=q;line(x,[[540,1080],[a,1160],[a,1210]],gold,3);x.strokeStyle='#658180';x.lineWidth=2;x.beginPath();x.roundRect(a-128,1210,256,92,15);x.stroke();x.font='25px Bold';x.fillStyle=white;x.textAlign='center';x.fillText(labels[i],a,1267);x.restore();});
}
async function render(name,seconds,draw){const output=path.join(__dirname,name+'.mp4');if(fs.existsSync(output))return;const c=createCanvas(W,H),x=c.getContext('2d'),n=Math.round(seconds*30);const proc=spawn(ff,['-hide_banner','-loglevel','error','-n','-f','rawvideo','-pixel_format','rgba','-video_size',`${W}x${H}`,'-framerate','30','-i','pipe:0','-an','-frames:v',String(n),'-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p',output],{windowsHide:true,stdio:['pipe','ignore','pipe']});let err='';proc.stderr.on('data',d=>err+=d);const done=new Promise((resolve,reject)=>{proc.on('error',reject);proc.on('close',code=>code?reject(Error(err)):resolve());});for(let i=0;i<n;i++){draw(x,i/30);if(i===Math.round(n*.7))fs.writeFileSync(path.join(__dirname,name+'-preview.png'),c.toBuffer('image/png'));if(!proc.stdin.write(Buffer.from(x.getImageData(0,0,W,H).data)))await once(proc.stdin,'drain');}proc.stdin.end();await done;console.log(name+' rendered');}
(async()=>{await render('ai-motion',3,ai);await render('funnel-motion',2.5,funnel);})().catch(e=>{console.error(e);process.exitCode=1;});
