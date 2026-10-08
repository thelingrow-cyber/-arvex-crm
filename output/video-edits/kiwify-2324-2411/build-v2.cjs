'use strict';
// Local revision of story kiwify-2324-2411-primeiro-teste; V1 stays unchanged.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const dir=__dirname,root=path.resolve(dir,'../../..');
const ffmpeg=path.join(root,'output/video-tools/node_modules/ffmpeg-static/ffmpeg.exe');
const old=JSON.parse(fs.readFileSync(path.join(dir,'edit-manifest.json'),'utf8'));
const rates=[1.10,1.06,1.12,1.12,1.04];
let cursor=0;
const cuts=old.cuts.map((c,i)=>{
 const frames=Math.round((c.end-c.start)/rates[i]*30),duration=frames/30;
 const n={...c,v1Offset:c.offset,offset:cursor,duration,frames,rate:(c.end-c.start)/duration};cursor+=duration;return n;
});
const duration=cursor;
function map(t){const c=cuts.find(c=>t<c.v1Offset+c.end-c.start-0.00001)||cuts.at(-1);return Math.max(0,Math.min(duration,c.offset+(t-c.v1Offset)/c.rate));}
const inserts=[
 {name:'ecosystem',start:map(5.05),duration:2.7},
 {name:'ai-create',start:map(16.00),duration:2.0},
 {name:'funnel',start:map(23.3),duration:2.1}
].map(i=>({...i,end:i.start+i.duration}));
const tech={start:inserts[1].end+.03,end:inserts[1].end+2.10};
const flashes=[inserts[0].start,inserts[1].start,inserts[2].end];
const timestamp=t=>{const n=Math.round(t*100);return `${Math.floor(n/360000)}:${String(Math.floor(n/6000)%60).padStart(2,'0')}:${String(Math.floor(n/100)%60).padStart(2,'0')}.${String(n%100).padStart(2,'0')}`;};
const seconds=t=>t.split(':').reduce((a,v)=>a*60+Number(v),0);
const oldAss=fs.readFileSync(path.join(dir,'captions.ass'),'utf8');
let ass=oldAss.split('Dialogue:')[0],srt='',count=0;
const srtTime=t=>timestamp(t).replace(/^0:/,'00:').replace('.',',')+'0';
for(const line of oldAss.split(/\r?\n/).filter(l=>l.startsWith('Dialogue:'))){
 const parts=line.split(','),a=map(seconds(parts[1])),b=map(seconds(parts[2]));
 const plain=parts.slice(9).join(',').replace(/\{[^}]*\}/g,'');
 const boundaries=[a,...inserts.flatMap(i=>[i.start,i.end]).filter(t=>t>a+.015&&t<b-.015),b].sort((x,y)=>x-y);
 for(let j=0;j<boundaries.length-1;j++){
  const start=boundaries[j],end=boundaries[j+1],mid=(start+end)/2;
  const light=inserts.some(i=>mid>=i.start&&mid<i.end),base=light?'201D17':'FFFFFF',accent=light?'376F93':'78CFED';
  const body=plain.replace(/\b(ecossistema|marca|pessoal|infoproduto|comunidade|tecnologia|tech|IA|funil|expansão|crescimento|não)\b/i,m=>`{\\c&H${accent}&}${m}{\\c&H${base}&}`);
  ass+=`Dialogue: 3,${timestamp(start)},${timestamp(end)},Main,,0,0,0,,{\\c&H${base}&\\3c&H${light?'E7EEF0':'101618'}&\\shad${light?'0':'1'}}${body}\n`;
 }
 srt+=`${++count}\n${srtTime(a)} --> ${srtTime(b)}\n${plain}\n\n`;
}
fs.writeFileSync(path.join(dir,'captions-v2.ass'),ass);fs.writeFileSync(path.join(dir,'captions-v2.srt'),srt);
const args=['-hide_banner','-nostdin','-n','-threads','2','-i',path.join(dir,old.source)];
for(const name of ['scrim','hook','tech'])args.push('-loop','1','-framerate','30','-i',path.join(dir,'assets',name+'.png'));
for(const i of inserts)args.push('-threads','1','-i',path.join(dir,'v2-motion',i.name+'.mp4'));
args.push('-i',path.join(dir,'music-close-up-1167.mp3'));
let f=`[0:v]split=5${cuts.map((_,i)=>`[sv${i}]`).join('')};\n[0:a]asplit=5${cuts.map((_,i)=>`[sa${i}]`).join('')};\n`;
for(let i=0;i<cuts.length;i++){
 const c=cuts[i],[w,h,x,y]=c.crop;
 f+=`[sv${i}]trim=start=${c.start}:end=${c.end},setpts=(PTS-STARTPTS)/${c.rate},crop=${w}:${h}:${x}+6*sin(t/3):${y},scale=1080:1920:flags=lanczos,setsar=1,eq=saturation=0.91:contrast=1.025:brightness=0.004,fps=30,tpad=stop_mode=clone:stop_duration=0.05,trim=duration=${c.duration}[v${i}];\n`;
 f+=`[sa${i}]atrim=start=${c.start}:end=${c.end},asetpts=PTS-STARTPTS,atempo=${c.rate},apad,atrim=duration=${c.duration},afade=t=in:d=0.005,afade=t=out:st=${c.duration-.006}:d=0.006[a${i}];\n`;
}
f+=cuts.map((_,i)=>`[v${i}][a${i}]`).join('')+'concat=n=5:v=1:a=1[catv][cata];\n';
f+='[catv][1:v]overlay=0:0:shortest=1[base];\n';
f+='[2:v]format=rgba,fade=t=in:d=0.16:alpha=1,fade=t=out:st=2.35:d=0.18:alpha=1[hook];\n';
f+="[base][hook]overlay=0:0:shortest=1:enable='lt(t,2.55)'[o0];\n";
for(let j=0;j<inserts.length;j++){
 const i=inserts[j];
 f+=`[${4+j}:v]setpts=PTS-STARTPTS+${i.start}/TB[ins${j}];\n`;
 f+=`[o${j}][ins${j}]overlay=0:0:eof_action=pass:enable='gte(t,${i.start})*lt(t,${i.end})'[o${j+1}];\n`;
}
f+=`[3:v]format=rgba,fade=t=in:d=0.18:alpha=1,fade=t=out:st=${tech.end-tech.start-.18}:d=0.18:alpha=1,setpts=PTS-STARTPTS+${tech.start}/TB[tech];\n`;
f+=`[o3][tech]overlay=0:'18*max(0,1-(t-${tech.start})/0.2)':shortest=1:enable='between(t,${tech.start},${tech.end})'[cards];\n`;
const flashFilters=flashes.flatMap(t=>[
 `drawbox=x=0:y=0:w=iw:h=ih:color=0xffe5b5@0.28:t=fill:enable='between(t,${t},${t+.065})'`,
 `drawbox=x=0:y=0:w=iw:h=ih:color=0xffb978@0.10:t=fill:enable='between(t,${t+.066},${t+.145})'`
]);
f+=`[cards]${flashFilters.join(',')},ass=filename=captions-v2.ass,format=yuv420p[vout];\n`;
f+='[cata]highpass=f=75,acompressor=threshold=0.15:ratio=1.7:attack=12:release=180:makeup=1.15,loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,asplit=2[voice][key];\n';
f+=`[7:a]atrim=start=8:duration=${duration},asetpts=PTS-STARTPTS,highpass=f=100,lowpass=f=8500,equalizer=f=2300:t=q:w=0.8:g=-3,loudnorm=I=-31:TP=-8:LRA=7,aresample=48000,afade=t=in:d=0.6,afade=t=out:st=${duration-.65}:d=0.65[music];\n`;
f+=`[music][key]sidechaincompress=threshold=0.06:ratio=2:attack=35:release=280:makeup=1[duck];\n[voice][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9,atrim=duration=${duration}[aout]\n`;
fs.writeFileSync(path.join(dir,'filter-v2.ffmpeg'),f);
args.push('-filter_complex_threads','1','-filter_complex_script','filter-v2.ffmpeg','-map','[vout]','-map','[aout]','-t',String(duration),'-c:v','libx264','-preset','veryfast','-crf','19','-threads','2','-r','30','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','kiwify-2324-2411-edit-v2.mp4');
const manifest={duration,cuts,inserts,tech,flashes,music:{title:'Close Up',author:'Michael Ramir C.',provider:'Mixkit',source:'https://assets.mixkit.co/music/1167/1167.mp3',license:'https://mixkit.co/license/#musicFree'},notes:['V1 and original preserved.','No CTA or promotional freeze.','Moderate pitch-preserving tempo changes, matching video and captions.','Conceptual motion only; no personal CRM or product footage.','Visual and numeric audio checks; human listening review remains pending.']};
fs.writeFileSync(path.join(dir,'edit-manifest-v2.json'),JSON.stringify(manifest,null,2));
fs.writeFileSync(path.join(dir,'render-args-v2.json'),JSON.stringify(args,null,2));
console.log(JSON.stringify({duration,inserts,tech,flashes,captions:count}));
if(process.argv.includes('--render')){const r=spawnSync(ffmpeg,args,{cwd:dir,stdio:'inherit',windowsHide:true});if(r.error)throw r.error;process.exit(r.status??1);}
