/* Reproducible local media job. Story: kiwify-2324-2411-primeiro-teste.story.md */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { createCanvas, GlobalFonts } = require('@napi-rs/canvas');
const dir = __dirname;
const root = path.resolve(dir, '../../..');
const ffmpeg = path.join(root, 'output/video-tools/node_modules/ffmpeg-static/ffmpeg.exe');
const transcript = JSON.parse(fs.readFileSync(path.join(dir, 'transcript.json'), 'utf8'));
GlobalFonts.registerFromPath('C:/Windows/Fonts/segoeuib.ttf', 'EditBold');
GlobalFonts.registerFromPath('C:/Windows/Fonts/segoeui.ttf', 'EditRegular');
const W = 1080, H = 1920, fps = 30;
const assets = path.join(dir, 'assets');
fs.mkdirSync(assets, { recursive: true });
const paper = '#f0eee7', ink = '#171d20', muted = '#6c7477', gold = '#edcf78';
const medium = [504,896,1066,134], close = [450,800,1094,172];
// Frame-accurate source ranges. Only repetition, hesitation and the following question removed.
const cuts = [
  [34,308,medium], [339,511,close], [511,740,medium],
  [748,870,close], [891,983,medium],
].map(([a,b,crop]) => ({start:a/fps,end:b/fps,crop}));
let cursor=0;
for(const cut of cuts){cut.offset=cursor;cursor+=cut.end-cut.start;}
const speechDuration=cursor, tail=2.4, duration=speechDuration+tail;
const time = x => {let n=Math.round(x*100);return `${Math.floor(n/360000)}:${String(Math.floor(n/6000)%60).padStart(2,'0')}:${String(Math.floor(n/100)%60).padStart(2,'0')}.${String(n%100).padStart(2,'0')}`;};
const srtTime = x=> {let n=Math.round(x*1000);return `${String(Math.floor(n/3600000)).padStart(2,'0')}:${String(Math.floor(n/60000)%60).padStart(2,'0')}:${String(Math.floor(n/1000)%60).padStart(2,'0')},${String(n%1000).padStart(3,'0')}`;};
function canvas(){ const c=createCanvas(W,H);return [c,c.getContext('2d')]; }
function font(ctx,size,bold=true){ctx.font=`${size}px ${bold?'EditBold':'EditRegular'}`;}
function text(ctx,str,x,y,size=48,color=ink,align='left',bold=true){font(ctx,size,bold);ctx.fillStyle=color;ctx.textAlign=align;ctx.fillText(str,x,y);}
function round(ctx,x,y,w,h,r,color){ctx.fillStyle=color;ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fill();}
function line(ctx,points,color='#bec4bf',width=3){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.stroke();}
function bg(ctx){ctx.fillStyle=paper;ctx.fillRect(0,0,W,H);ctx.strokeStyle='#e2e1d9';ctx.lineWidth=1;for(let x=0;x<W;x+=72){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}for(let y=0;y<H;y+=72){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}text(ctx,'NEGÓCIOS  /  VISÃO',100,210,27,muted);round(ctx,100,242,72,6,3,gold);text(ctx,'ILUSTRAÇÃO CONCEITUAL',100,1650,23,muted);}
function save(name,c){fs.writeFileSync(path.join(assets,name+'.png'),c.toBuffer('image/png'));}
// Bottom scrim maintains face visibility while making subtitles readable.
{
 const [c,ctx]=canvas();const grad=ctx.createLinearGradient(0,1000,0,H);grad.addColorStop(0,'rgba(6,10,12,0)');grad.addColorStop(.53,'rgba(6,10,12,.60)');grad.addColorStop(1,'rgba(6,10,12,.9)');ctx.fillStyle=grad;ctx.fillRect(0,1000,W,H);save('scrim',c);
}
{
 const [c,ctx]=canvas();round(ctx,94,1040,760,210,22,'rgba(13,19,22,.88)');round(ctx,94,1040,7,210,3,gold);text(ctx,'Sua marca vai além',130,1127,62,'#fff');text(ctx,'do infoproduto.',130,1205,66,gold);save('hook',c);
}
{
 const [c,ctx]=canvas();bg(ctx);text(ctx,'Uma marca.',100,405,81);text(ctx,'Um ecossistema.',100,510,81);
 const nodes=[[125,660,340,150,'CONTEÚDO'],[610,660,340,150,'PRODUTOS'],[125,1120,340,150,'COMUNIDADE'],[610,1120,340,150,'TECNOLOGIA']];
 for(const [x,y,w,h,label] of nodes)line(ctx,[[540,960],[x+w/2,y+h/2]],'#b5bdb7',4);
 for(const [x,y,w,h,label] of nodes){round(ctx,x,y,w,h,18,'#fff');text(ctx,label,x+w/2,y+91,30,ink,'center');}
 round(ctx,295,865,490,176,22,ink);text(ctx,'MARCA PESSOAL',540,972,42,paper,'center');save('ecosystem',c);
}
{
 const [c,ctx]=canvas();round(ctx,85,962,855,306,24,'rgba(16,23,26,.96)');text(ctx,'NOVAS POSSIBILIDADES',127,1025,25,gold);text(ctx,'IA + tecnologia',127,1106,67,'#fff');line(ctx,[[129,1153],[874,1153]],'#465456',2);
 for(let i=0;i<6;i++){round(ctx,133+i*124,1180,74,8,4,i<3?gold:'#465456');}
 text(ctx,'ILUSTRAÇÃO CONCEITUAL',128,1240,19,'#a2acaa');save('tech',c);
}
{
 const [c,ctx]=canvas();bg(ctx);text(ctx,'Além de',100,415,84);text(ctx,'um único funil.',100,519,84);
 ctx.fillStyle='#d5d9d1';ctx.beginPath();ctx.moveTo(210,660);ctx.lineTo(870,660);ctx.lineTo(624,908);ctx.lineTo(624,1040);ctx.lineTo(456,1040);ctx.lineTo(456,908);ctx.closePath();ctx.fill();
 text(ctx,'UMA ESTRATÉGIA',540,770,34,ink,'center');line(ctx,[[540,1070],[540,1140]],ink,4);line(ctx,[[520,1121],[540,1141],[560,1121]],ink,4);
 round(ctx,190,1190,700,153,20,ink);text(ctx,'EXPANSÃO DA MARCA',540,1284,41,paper,'center');save('funnel',c);
}
{
 const [c,ctx]=canvas();const grad=ctx.createLinearGradient(0,720,0,H);grad.addColorStop(0,'rgba(9,15,17,0)');grad.addColorStop(.45,'rgba(9,15,17,.82)');grad.addColorStop(1,'rgba(9,15,17,.97)');ctx.fillStyle=grad;ctx.fillRect(0,720,W,H);
 text(ctx,'NEGÓCIOS AI NATIVE',110,1080,30,gold);text(ctx,'IA no núcleo',110,1175,70,'#fff');text(ctx,'da operação.',110,1260,70,'#fff');round(ctx,110,1330,747,111,18,paper);text(ctx,'Acompanhe a construção  →',483,1401,37,ink,'center');save('cta',c);
}
let ass=`[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Main,Segoe UI,62,&H00FFFFFF,&H00FFFFFF,&H00101618,&H80000000,-1,0,0,0,100,100,0,0,1,2.5,1,2,100,170,482,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n`;
const mapped=[];
for(const cut of cuts){
 const words=transcript.words.filter(w=>w.start>=cut.start-.035 && w.end<=cut.end+.035).map(w=>({...w,word:w.word.trim().replace(/infoproducto/gi,'infoproduto').replace(/\.\.\./g,''),start:Math.max(0,w.start-cut.start+cut.offset),end:Math.min(speechDuration,w.end-cut.start+cut.offset)}));
 mapped.push(...words);
}
const groups=[];let g=[];
for(let i=0;i<mapped.length;i++){
 const w=mapped[i];g.push(w);let chars=g.map(q=>q.word).join(' ').length;
 if(g.length>=4||/[.!?,]$/.test(w.word)||chars>=27||(mapped[i+1] && mapped[i+1].start-w.end>.35)||i===mapped.length-1){groups.push(g);g=[];}
}
const keywords=/ecossistema|marca|pessoal|infoproduto|comunidade|tecnologia|tech|IA|funil|expansão|crescimento|não/i;
let srt='';
for(let i=0;i<groups.length;i++){
 const group=groups[i],start=group[0].start,end=Math.min(group.at(-1).end+.1,groups[i+1]?.[0]?.start??speechDuration);
 if(end<=start)continue;
 const center=(start+end)/2,light=(center>=5.15&&center<8.65)||(center>=23.35&&center<25.85);
 const highlighted=group.findIndex(w=>keywords.test(w.word));
 const body=group.map((w,j)=>j===highlighted?`{\\c&H${light?'376F93':'78CFED'}&}${w.word}{\\c&H${light?'201D17':'FFFFFF'}&}`:w.word).join(' ');
 ass+=`Dialogue: 3,${time(start)},${time(end)},Main,,0,0,0,,{\\fad(45,65)${light?'\\c&H201D17&\\3c&HE7EEF0&\\shad0':''}}${body}\n`;
 srt+=`${i+1}\n${srtTime(start)} --> ${srtTime(end)}\n${group.map(w=>w.word).join(' ')}\n\n`;
}
fs.writeFileSync(path.join(dir,'captions.ass'),ass);fs.writeFileSync(path.join(dir,'captions.srt'),srt);
const inserts=[{asset:'hook',start:0,end:2.8},{asset:'ecosystem',start:5.15,end:8.65},{asset:'tech',start:16.1,end:18.8},{asset:'funnel',start:23.35,end:25.85},{asset:'cta',start:speechDuration-.25,end:duration}];
const overlayNames=['scrim',...inserts.map(i=>i.asset)];
const inputs=['-hide_banner','-nostdin','-n','-threads','2','-i',path.join(dir,'kiwify-2324-2411-original.mp4')];
for(const name of overlayNames) inputs.push('-loop','1','-framerate','30','-i',path.join(assets,name+'.png'));
let filter=`[0:v]split=${cuts.length}${cuts.map((_,i)=>`[sv${i}]`).join('')};\n[0:a]asplit=${cuts.length}${cuts.map((_,i)=>`[sa${i}]`).join('')};\n`;
for(let i=0;i<cuts.length;i++){
 const cut=cuts[i], [w,h,x,y]=cut.crop;
 filter+=`[sv${i}]trim=start=${cut.start}:end=${cut.end},setpts=PTS-STARTPTS,crop=${w}:${h}:${x}+6*sin(t/3):${y},scale=${W}:${H}:flags=lanczos,setsar=1,eq=saturation=0.91:contrast=1.025:brightness=0.004[v${i}];\n`;
 filter+=`[sa${i}]atrim=start=${cut.start}:end=${cut.end},asetpts=PTS-STARTPTS,afade=t=in:d=0.006,afade=t=out:st=${(cut.end-cut.start-.008).toFixed(4)}:d=0.008[a${i}];\n`;
}
filter+=cuts.map((_,i)=>`[v${i}][a${i}]`).join('')+`concat=n=${cuts.length}:v=1:a=1[catv][cata];\n`;
filter+=`[catv]tpad=stop_mode=clone:stop_duration=${tail}[padded];\n`;
filter+=`[cata]highpass=f=75,acompressor=threshold=0.15:ratio=1.7:attack=12:release=180:makeup=1.15,loudnorm=I=-16:TP=-1.5:LRA=9,apad=pad_dur=${tail},atrim=duration=${duration}[aout];\n`;
filter+=`[padded][1:v]overlay=0:0:shortest=1[o0];\n`;
for(let i=0;i<inserts.length;i++){
 const ins=inserts[i];
 filter+=`[o${i}][${i+2}:v]overlay=0:0:shortest=1:enable='between(t,${ins.start},${ins.end})'[o${i+1}];\n`;
}
filter+=`[o${inserts.length}]ass=filename=captions.ass,format=yuv420p[vout]\n`;
fs.writeFileSync(path.join(dir,'filter.ffmpeg'),filter);
const manifest={source:'kiwify-2324-2411-original.mp4',originalStart:'00:23:24',originalEnd:'00:24:11',originalDuration:47,editedDuration:duration,speechDuration,tail,output:{width:W,height:H,fps},cuts,inserts,notes:['Fonte preservada. Cópia horizontal exata separada.','Teste editorial encerra na frase sobre expansão e crescimento.','Removidos início repetido, frase intermediária redundante, hesitação e continuação da apresentadora.','Inserts inteiramente conceituais, desenhados localmente. Sem CRM, produtos pessoais ou alegações de resultados.','CTA somente escrito, sobre frame congelado visível. Sem síntese de voz ou simulação labial.','Legendas via ASR local com normalização ortográfica. Revisão auditiva humana ainda recomendada para aprovação final.','Reenquadramento limitado à resolução 1080p original; exportação 1080x1920 não recupera detalhe inexistente.']};
fs.writeFileSync(path.join(dir,'edit-manifest.json'),JSON.stringify(manifest,null,2));
const args=[...inputs,'-filter_complex_threads','1','-filter_complex_script','filter.ffmpeg','-map','[vout]','-map','[aout]','-t',String(duration),'-c:v','libx264','-preset','veryfast','-crf','19','-threads','2','-r','30','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','kiwify-2324-2411-edit-v1.mp4'];
fs.writeFileSync(path.join(dir,'render-args.json'),JSON.stringify(args,null,2));
console.log(JSON.stringify({duration,speechDuration,captions:groups.length,inserts:inserts.length,output:path.join(dir,'kiwify-2324-2411-edit-v1.mp4')}));
if(process.argv.includes('--render')){
 const result=spawnSync(ffmpeg,args,{cwd:dir,stdio:'inherit',windowsHide:true});
 if(result.error)throw result.error;process.exit(result.status??1);
}
