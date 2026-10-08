'use strict';
// Story: kiwify-2324-2411-primeiro-teste. Real B-roll and new speech assembly.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const {createCanvas,GlobalFonts}=require('@napi-rs/canvas');
const revision=process.argv.includes('--v4')?'v4':'v3',restoreOpening=revision==='v4';
const d=__dirname,root=path.resolve(d,'../../..'),assets=path.join(d,revision+'-assets');
const stockAssets=path.join(d,'v3-assets');fs.mkdirSync(assets,{recursive:true});
const ff=path.join(root,'output/video-tools/node_modules/ffmpeg-static/ffmpeg.exe');
const transcript=JSON.parse(fs.readFileSync(path.join(d,'transcript.json'),'utf8'));
const medium=[504,896,1066,134],close=[450,800,1094,172];
let cursor=0;
const cuts=[
 ...(restoreOpening?[[34,257,1.10,medium]]:[]),
 [339,434,1.04,medium],[434,506,1.06,close],
 [538,633,1.10,medium],[664,737,1.06,close],
 [748,871,1.08,medium],[893,982,1.04,close]
].map(([a,b,speed,crop])=>{const start=a/30,end=b/30,frames=Math.round((b-a)/speed),duration=frames/30,c={start,end,crop,frames,duration,rate:(end-start)/duration,offset:cursor};cursor+=duration;return c;});
const duration=cursor;
const lead=restoreOpening?1:0;
const inserts=[
 {name:'technology',start:cuts[lead+2].offset-.08,end:cuts[lead+2].offset+1.48,sourceStart:2,sourceEnd:3.8,crop:[608,1080,766,0],sourcePage:'https://mixkit.co/free-stock-video/programmer-working-with-codes-on-a-computer-41637/'},
 {name:'community',start:cuts[lead+3].offset+.55,end:cuts[lead+3].offset+2.30,sourceStart:2,sourceEnd:4.05,crop:[608,1080,710,0],sourcePage:'https://mixkit.co/free-stock-video/team-collaboration-in-a-colorful-workspace-100319/'}
];
const tech={start:inserts[0].end+.03,end:cuts[lead+3].offset+.30};
const flashes=[cuts[lead+1].offset,inserts[0].start,inserts[1].end];
GlobalFonts.registerFromPath('C:/Windows/Fonts/segoeuib.ttf','EditBold');
function asset(name,draw){const c=createCanvas(1080,1920),x=c.getContext('2d');draw(x);fs.writeFileSync(path.join(assets,name+'.png'),c.toBuffer('image/png'));}
asset('hook',x=>{x.fillStyle='rgba(12,18,20,.85)';x.beginPath();x.roundRect(94,1040,810,212,18);x.fill();x.fillStyle='#edcf78';x.fillRect(94,1040,7,212);x.font='bold 62px EditBold';x.fillStyle='white';x.fillText(restoreOpening?'Sua marca vai além':'Você não é só',130,1128);x.fillStyle='#edcf78';x.fillText(restoreOpening?'do infoproduto.':'um especialista.',130,1207);});
asset('stock-label',x=>{x.font='bold 23px EditBold';x.fillStyle='rgba(255,255,255,.72)';x.fillText('CENA ILUSTRATIVA',102,1650);});
const ts=t=>{const n=Math.round(t*100);return `${Math.floor(n/360000)}:${String(Math.floor(n/6000)%60).padStart(2,'0')}:${String(Math.floor(n/100)%60).padStart(2,'0')}.${String(n%100).padStart(2,'0')}`;};
const srtTs=t=>'0'+ts(t).replace('.',',')+'0';
let ass=fs.readFileSync(path.join(d,'captions.ass'),'utf8').split('Dialogue:')[0],srt='',groups=[],spoken=[];
for(const cut of cuts){
 const words=transcript.words.filter(w=>w.start>=cut.start-.02&&w.end<=cut.end+.02).map(w=>({word:w.word.trim().replace(/\.\.\./g,'').replace(/infoproducto/gi,'infoproduto'),start:cut.offset+(w.start-cut.start)/cut.rate,end:cut.offset+(w.end-cut.start)/cut.rate}));
 spoken.push(words.map(w=>w.word).join(' '));let group=[];
 for(let i=0;i<words.length;i++){group.push(words[i]);if(group.length>=4||/[.,!?]$/.test(words[i].word)||group.map(w=>w.word).join(' ').length>=26||i===words.length-1){groups.push(group);group=[];}}
}
for(let j=0;j<groups.length;j++){
 const g=groups[j],a=Math.max(0,g[0].start),b=Math.min(duration,g.at(-1).end+.045,groups[j+1]?.[0].start??duration),plain=g.map(w=>w.word).join(' ');
 const body=plain.replace(/(expert|ecossistema|especialista|marca|comunidade|tech|IA|funil|expansão|crescimento|não)/i,m=>`{\\c&H78CFED&}${m}{\\c&HFFFFFF&}`);
 ass+=`Dialogue: 3,${ts(a)},${ts(b)},Main,,0,0,0,,${body}\n`;
 srt+=`${j+1}\n${srtTs(a)} --> ${srtTs(b)}\n${plain}\n\n`;
}
fs.writeFileSync(path.join(d,`captions-${revision}.ass`),ass);fs.writeFileSync(path.join(d,`captions-${revision}.srt`),srt);
const args=['-hide_banner','-nostdin','-n','-threads','2','-i',path.join(d,'kiwify-2324-2411-original.mp4')];
for(const i of inserts)args.push('-threads','1','-i',path.join(stockAssets,i.name+'.mp4'));
for(const p of [path.join(d,'assets/scrim.png'),path.join(assets,'hook.png'),path.join(d,'assets/tech.png'),path.join(assets,'stock-label.png')])args.push('-loop','1','-framerate','30','-i',p);
args.push('-i',path.join(d,'music-close-up-1167.mp3'));
let f=`[0:v]split=${cuts.length}${cuts.map((_,i)=>`[sv${i}]`).join('')};\n[0:a]asplit=${cuts.length}${cuts.map((_,i)=>`[sa${i}]`).join('')};\n`;
for(let i=0;i<cuts.length;i++){
 const c=cuts[i],[w,h,x,y]=c.crop;
 f+=`[sv${i}]trim=start=${c.start}:end=${c.end},setpts=(PTS-STARTPTS)/${c.rate},crop=${w}:${h}:${x}+6*sin(t/3):${y},scale=1080:1920:flags=lanczos,setsar=1,eq=saturation=0.91:contrast=1.025:brightness=0.004,fps=30,tpad=stop_mode=clone:stop_duration=0.05,trim=duration=${c.duration}[v${i}];\n`;
 f+=`[sa${i}]atrim=start=${c.start}:end=${c.end},asetpts=PTS-STARTPTS,atempo=${c.rate},apad,atrim=duration=${c.duration},afade=t=in:d=0.007,afade=t=out:st=${c.duration-.009}:d=0.009[a${i}];\n`;
}
f+=cuts.map((_,i)=>`[v${i}][a${i}]`).join('')+`concat=n=${cuts.length}:v=1:a=1[o0][cata];\n`;
for(let j=0;j<inserts.length;j++){
 const i=inserts[j],[w,h,x,y]=i.crop,rate=(i.sourceEnd-i.sourceStart)/(i.end-i.start);
 f+=`[${j+1}:v]trim=start=${i.sourceStart}:end=${i.sourceEnd},setpts=(PTS-STARTPTS)/${rate},crop=${w}:${h}:${x}:${y},scale=1080:1920:flags=lanczos,setsar=1,eq=saturation=0.72:contrast=1.06:brightness=-0.012,fps=30,setpts=PTS+${i.start}/TB[b${j}];\n`;
 f+=`[o${j}][b${j}]overlay=0:0:eof_action=pass:enable='gte(t,${i.start})*lt(t,${i.end})'[o${j+1}];\n`;
}
f+='[o2][3:v]overlay=0:0:shortest=1[shaded];\n';
f+='[4:v]format=rgba,fade=t=in:d=0.10:alpha=1,fade=t=out:st=2.35:d=0.12:alpha=1[hook];\n';
f+="[shaded][hook]overlay=0:0:shortest=1:enable='lt(t,2.5)'[headline];\n";
f+=`[5:v]format=rgba,fade=t=in:d=0.12:alpha=1,fade=t=out:st=${tech.end-tech.start-.12}:d=0.12:alpha=1,setpts=PTS+${tech.start}/TB[tech];\n`;
f+=`[headline][tech]overlay=0:0:shortest=1:enable='between(t,${tech.start},${tech.end})'[card];\n`;
f+=`[card][6:v]overlay=0:0:shortest=1:enable='${inserts.map(i=>`between(t,${i.start},${i.end})`).join('+')}'[labelled];\n`;
// Three isolated film-like flashes: visible peak and warm decay, NOT repetitive strobing.
const flashFilters=flashes.flatMap(t=>[
 `drawbox=x=0:y=0:w=iw:h=ih:color=0xfff4d6@0.88:t=fill:enable='gte(t,${t-.034})*lt(t,${t+.034})'`,
 `drawbox=x=0:y=0:w=iw:h=ih:color=0xffd78b@0.48:t=fill:enable='gte(t,${t+.034})*lt(t,${t+.100})'`,
 `drawbox=x=0:y=0:w=iw:h=ih:color=0xff7137@0.19:t=fill:enable='gte(t,${t+.100})*lt(t,${t+.234})'`
]);
f+=`[labelled]${flashFilters.join(',')},ass=filename=captions-${revision}.ass,format=yuv420p[vout];\n`;
f+='[cata]highpass=f=75,acompressor=threshold=0.15:ratio=1.7:attack=12:release=180:makeup=1.15,loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,asplit=2[voice][key];\n';
f+=`[7:a]atrim=start=8:duration=${duration},asetpts=PTS-STARTPTS,highpass=f=100,lowpass=f=8500,equalizer=f=2300:t=q:w=0.8:g=-3,loudnorm=I=-31:TP=-8:LRA=7,aresample=48000,afade=t=in:d=0.35,afade=t=out:st=${duration-.4}:d=0.4[music];\n`;
f+=`[music][key]sidechaincompress=threshold=0.06:ratio=2:attack=35:release=280:makeup=1[duck];\n[voice][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9,atrim=duration=${duration}[aout]\n`;
fs.writeFileSync(path.join(d,`filter-${revision}.ffmpeg`),f);
args.push('-filter_complex_threads','1','-filter_complex_script',`filter-${revision}.ffmpeg`,'-map','[vout]','-map','[aout]','-t',String(duration),'-c:v','libx264','-preset','veryfast','-crf','19','-threads','2','-r','30','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',`kiwify-2324-2411-edit-${revision}.mp4`);
fs.writeFileSync(path.join(d,`edit-manifest-${revision}.json`),JSON.stringify({revision,restoreOpening,duration,cuts,inserts,tech,flashes,spoken,removed:[restoreOpening?'Only redundant personal-brand clarification after restored ecosystem opening':'Intro about infoproducts and uncertain opening','Repeated pode ser explorado','Hesitation between vai and resolver'],stockLicense:'Mixkit Stock Video Free License, confirmed on each source page',music:'Close Up - Michael Ramir C. / Mixkit',humanListeningReview:'pending'},null,2));
fs.writeFileSync(path.join(d,`render-args-${revision}.json`),JSON.stringify(args,null,2));
console.log(JSON.stringify({duration,spoken,inserts,flashes},null,2));
if(process.argv.includes('--render')){const r=spawnSync(ff,args,{cwd:d,stdio:'inherit',windowsHide:true});if(r.error)throw r.error;process.exit(r.status??1);}
