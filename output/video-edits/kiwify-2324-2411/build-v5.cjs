'use strict';
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const d=__dirname,assets=path.join(d,'v5-assets'),root=path.resolve(d,'../../..');
const revision=process.argv.includes('--v7')?'v7':process.argv.includes('--v6')?'v6':'v5',qualityPass=['v6','v7'].includes(revision),caseStudy=revision==='v7';
const ff=path.join(root,'output/video-tools/node_modules/ffmpeg-static/ffmpeg.exe');
const words=JSON.parse(fs.readFileSync(path.join(d,'transcript.json'),'utf8')).words.map(w=>({...w}));
// The first ASR pass swallowed the repeated word and hesitation. User correction + waveform.
for(const w of words){if(w.start===6.72){w.start=7.47;w.end=7.88;}if(w.start===7.16){w.start=7.88;w.end=7.98;}if(w.word.trim().startsWith('vai')&&w.start>27){w.end=28.06;w.word='vai';}if(w.word.trim()==='especialista')w.word='especialista.';}
const medium=[504,896,1066,134],close=[450,800,1094,172];let cursor=0;
const cuts=[
 ['opening',34,204,1.10,medium],['brand',224,257,1.10,close],
 ['expert',339,395,1.04,medium],['ecosystem',434,506,1.06,close],
 ['ia',538,569,1.10,medium],['tech',577,633,1.10,medium],
 ['building',664,737,1.06,close],['funnel',748,844,1.08,medium],['resolve',890,982,1.04,close]
].map(([name,a,b,speed,crop])=>{const start=a/30,end=b/30,frames=Math.round((b-a)/speed),duration=frames/30,c={name,start,end,crop,frames,duration,rate:(end-start)/duration,offset:cursor};cursor+=duration;return c;});
const duration=cursor,by=Object.fromEntries(cuts.map(c=>[c.name,c]));
const inserts=caseStudy?[
 {name:'ai-motion',start:by.ia.offset,end:by.building.offset,sourceStart:0,sourceEnd:3,crop:null},
 {name:'guday-case',assetDir:'v7-assets',start:by.building.offset+.10,end:by.building.offset+1.40,sourceStart:0,sourceEnd:1.30,sourcePage:'https://guday.com.br/pages/historia',attribution:'Official founder section; reuse rights unconfirmed.'},
 {name:'mrbeast-case',assetDir:'v7-assets',start:by.building.offset+1.43,end:by.building.offset+2.80,sourceStart:0,sourceEnd:1.37,sourcePage:'https://www.youtube.com/watch?v=jaRfBM7ESfc',attribution:'Official MrBeast 2 channel / Feastables commercial; reuse rights unconfirmed.'},
 {name:'funnel-motion',start:by.funnel.offset+.82,end:by.resolve.offset+.25,sourceStart:0,sourceEnd:2.5,crop:null}
]:[
 {name:'ai-motion',start:by.ia.offset,end:by.building.offset,sourceStart:0,sourceEnd:3,crop:null},
 {name:'guday-founder',start:by.building.offset+.10,end:by.building.offset+1.75,sourceStart:16.4,sourceEnd:18.05,crop:null,sourcePage:'https://guday.com.br/pages/historia',attribution:'Video embedded in UMA MENSAGEM DA NOSSA FUNDADORA / Olá, eu sou a Manu Cit. Not a modeling shoot. Reuse rights unconfirmed; draft only.'},
 {name:'funnel-motion',start:by.funnel.offset+.82,end:by.resolve.offset+.25,sourceStart:0,sourceEnd:2.5,crop:null}
];
const flashes=caseStudy?[by.expert.offset,by.ia.offset,by.building.offset+1.40]:[by.expert.offset,by.ia.offset,by.building.offset+1.75];
const ts=t=>{const n=Math.round(t*100);return `${Math.floor(n/360000)}:${String(Math.floor(n/6000)%60).padStart(2,'0')}:${String(Math.floor(n/100)%60).padStart(2,'0')}.${String(n%100).padStart(2,'0')}`;};
let ass=fs.readFileSync(path.join(d,'captions.ass'),'utf8').split('Dialogue:')[0],srt='',groups=[],spoken=[];
for(const c of cuts){const ww=words.filter(w=>w.start>=c.start-.02&&w.end<=c.end+.02).map(w=>({word:w.word.trim().replace(/\.\.\./g,'').replace(/infoproducto/gi,'infoproduto'),start:Math.max(c.offset,c.offset+(w.start-c.start)/c.rate),end:c.offset+(w.end-c.start)/c.rate}));spoken.push(ww.map(w=>w.word).join(' '));let g=[];for(let i=0;i<ww.length;i++){g.push(ww[i]);if(g.length===4||/[.,!?]$/.test(ww[i].word)||g.map(w=>w.word).join(' ').length>=26||i===ww.length-1){groups.push(g);g=[];}}}
for(let i=0;i<groups.length;i++){const g=groups[i],a=g[0].start,b=Math.min(duration,g.at(-1).end+.045,groups[i+1]?.[0].start??duration),plain=g.map(w=>w.word).join(' '),body=plain.replace(/(expert|ecossistema|especialista|marca|comunidade|tech|IA|funil|expansão|crescimento|não)/i,m=>`{\\c&H78CFED&}${m}{\\c&HFFFFFF&}`);ass+=`Dialogue: 3,${ts(a)},${ts(b)},Main,,0,0,0,,${body}\n`;srt+=`${i+1}\n0${ts(a).replace('.',',')}0 --> 0${ts(b).replace('.',',')}0\n${plain}\n\n`;}
fs.writeFileSync(path.join(d,`captions-${revision}.ass`),ass);fs.writeFileSync(path.join(d,`captions-${revision}.srt`),srt);
const args=['-hide_banner','-nostdin','-n','-threads','2','-i',path.join(d,'kiwify-2324-2411-original.mp4')];
for(const i of inserts)args.push('-threads','1','-i',path.join(d,i.assetDir||'v5-assets',i.name+'.mp4'));
args.push('-loop','1','-framerate','30','-i',path.join(d,'assets/scrim.png'),'-loop','1','-framerate','30','-i',path.join(d,'v4-assets/hook.png'),'-i',path.join(assets,'fallen-asper-565.mp3'));
let f=`[0:v]split=${cuts.length}${cuts.map((_,i)=>`[sv${i}]`).join('')};\n[0:a]asplit=${cuts.length}${cuts.map((_,i)=>`[sa${i}]`).join('')};\n`;
cuts.forEach((c,i)=>{const [w,h,x,y]=c.crop;const treatment=qualityPass?'hqdn3d=1.1:1.0:3.2:2.8,zscale=w=1080:h=1920:filter=spline36,colorbalance=gm=-0.025:gh=-0.012:bm=0.008,eq=saturation=1.00:contrast=1.05:brightness=0.004,cas=strength=0.22':'scale=1080:1920:flags=lanczos,eq=saturation=0.98:contrast=1.06:brightness=0.003,unsharp=3:3:0.20:3:3:0';f+=`[sv${i}]trim=start=${c.start}:end=${c.end},setpts=(PTS-STARTPTS)/${c.rate},crop=${w}:${h}:${x}+6*sin(t/3):${y},${treatment},setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=0.05,trim=duration=${c.duration}[v${i}];\n`;f+=`[sa${i}]atrim=start=${c.start}:end=${c.end},asetpts=PTS-STARTPTS,atempo=${c.rate},apad,atrim=duration=${c.duration},afade=t=in:d=0.005,afade=t=out:st=${c.duration-.007}:d=0.007[a${i}];\n`;});
f+=cuts.map((_,i)=>`[v${i}][a${i}]`).join('')+`concat=n=${cuts.length}:v=1:a=1[o0][cata];\n`;
inserts.forEach((i,j)=>{const rate=(i.sourceEnd-i.sourceStart)/(i.end-i.start),insertTreatment=qualityPass&&i.name==='guday-founder'?',hqdn3d=0.8:0.7:2.2:2.0,cas=strength=0.16':'';f+=`[${j+1}:v]trim=start=${i.sourceStart}:end=${i.sourceEnd},setpts=(PTS-STARTPTS)/${rate},scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920${insertTreatment},setsar=1,fps=30,setpts=PTS+${i.start}/TB[b${j}];\n[o${j}][b${j}]overlay=0:0:eof_action=pass:enable='gte(t,${i.start})*lt(t,${i.end})'[o${j+1}];\n`;});
const scrimInput=1+inserts.length,hookInput=scrimInput+1,musicInput=hookInput+1;
f+=`[o${inserts.length}][${scrimInput}:v]overlay=0:0:shortest=1[shaded];\n[${hookInput}:v]format=rgba,fade=t=in:d=0.10:alpha=1,fade=t=out:st=2.35:d=0.12:alpha=1[hook];\n[shaded][hook]overlay=0:0:shortest=1:enable='lt(t,2.5)'[headline];\n`;
const flashFilters=flashes.flatMap(t=>[`drawbox=x=0:y=0:w=iw:h=ih:color=0xfff4d6@0.88:t=fill:enable='gte(t,${t-.034})*lt(t,${t+.034})'`,`drawbox=x=0:y=0:w=iw:h=ih:color=0xffd78b@0.48:t=fill:enable='gte(t,${t+.034})*lt(t,${t+.100})'`,`drawbox=x=0:y=0:w=iw:h=ih:color=0xff7137@0.19:t=fill:enable='gte(t,${t+.100})*lt(t,${t+.234})'`]);
f+=`[headline]${flashFilters.join(',')},ass=filename=captions-${revision}.ass,format=yuv420p[vout];\n`;
f+='[cata]highpass=f=75,acompressor=threshold=0.15:ratio=1.7:attack=12:release=180:makeup=1.15,loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,asplit=2[voice][key];\n';
f+=`[${musicInput}:a]atrim=start=34:duration=${duration},asetpts=PTS-STARTPTS,highpass=f=70,lowpass=f=9000,equalizer=f=2300:t=q:w=0.8:g=-4,loudnorm=I=-28:TP=-8:LRA=8,aresample=48000,afade=t=in:d=0.5,afade=t=out:st=${duration-.55}:d=0.55[music];\n[music][key]sidechaincompress=threshold=0.06:ratio=2:attack=35:release=280:makeup=1[duck];\n[voice][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9,atrim=duration=${duration}[aout]\n`;
fs.writeFileSync(path.join(d,`filter-${revision}.ffmpeg`),f);args.push('-filter_complex_threads','1','-filter_complex_script',`filter-${revision}.ffmpeg`,'-map','[vout]','-map','[aout]','-t',String(duration),'-c:v','libx264','-preset',qualityPass?'slow':'veryfast','-crf',qualityPass?'14':'19','-tune','film','-profile:v','high','-threads','2','-r','30','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',`kiwify-2324-2411-edit-${revision}.mp4`);
const manifest={revision,duration,cuts,inserts,flashes,spoken,removed:['First dentro and adjacent pause: source 6.80–7.4667','em algo específico: source 13.1667–14.4667','IA pause: source 18.9667–19.2333','é and long pause after vai: source 28.1333–29.6667','Old AI stock footage and card','All added illustrative labels','CTA'],music:{title:'Fallen (Asper)',artist:'Eugenio Mininni',source:'https://mixkit.co/free-stock-music/mood/serious/',license:'Mixkit Stock Music Free License',catalogTags:'Atmospheres / Film Score / Mysterious / Documentary / Mystery',sourceOffset:34},grade:qualityPass?'quality-only pass: light spatial/temporal denoise, spline36 upscale, restrained green correction, contrast 1.05, CAS .22; source-derived render CRF14 slow':'contrast 1.06, saturation .98, subtle unsharp .20',humanListeningReview:'pending; source disfluencies identified by user; boundaries inferred from waveform and ASR'};
fs.writeFileSync(path.join(d,`edit-manifest-${revision}.json`),JSON.stringify(manifest,null,2));fs.writeFileSync(path.join(d,`render-args-${revision}.json`),JSON.stringify(args,null,2));console.log(JSON.stringify({revision,qualityPass,duration,spoken,inserts,flashes},null,2));
if(process.argv.includes('--render')){const r=spawnSync(ff,args,{cwd:d,stdio:'inherit',windowsHide:true});if(r.error)throw r.error;process.exit(r.status??1);}
