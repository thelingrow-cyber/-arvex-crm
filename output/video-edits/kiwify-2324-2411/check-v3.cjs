'use strict';
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const revision=process.argv.includes('--v7')?'v7':process.argv.includes('--v6')?'v6':process.argv.includes('--v5')?'v5':process.argv.includes('--v4')?'v4':'v3';
const d=__dirname,root=path.resolve(d,'../../..'),video=path.join(d,`kiwify-2324-2411-edit-${revision}.mp4`);
const ff=path.join(root,'output/video-tools/node_modules/ffmpeg-static/ffmpeg.exe');
const fp=path.join(root,'output/video-tools/node_modules/ffprobe-static/bin/win32/x64/ffprobe.exe');
function run(bin,args){const r=spawnSync(bin,args,{cwd:d,encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.error)throw r.error;if(r.status)throw Error(r.stderr);return r;}
const p=JSON.parse(run(fp,['-v','error','-show_streams','-show_format','-of','json',video]).stdout);
run(ff,['-v','error','-xerror','-threads','2','-i',video,'-f','null','-']);
const meter=run(ff,['-hide_banner','-nostats','-threads','2','-i',video,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']).stderr;
const frames=['v5','v6'].includes(revision)?[30,171,185,260,337,413,528,609]:revision==='v7'?[30,171,185,260,337,407,450,609]:revision==='v4'?[15,150,195,294,375,425,490,701]:[88,91,95,168,222,279,314,495];
run(ff,['-v','error','-n','-threads','2','-i',video,'-vf',`select='${frames.map(n=>`eq(n,${n})`).join('+')}',scale=270:480,tile=4x2`,'-frames:v','1','-q:v','2',`qa-${revision}.jpg`]);
const result={duration:p.format.duration,bytes:p.format.size,streams:p.streams.map(s=>({type:s.codec_type,codec:s.codec_name,width:s.width,height:s.height,frames:s.nb_frames,duration:s.duration})),decode:'pass',loudness:JSON.parse(meter.slice(meter.lastIndexOf('{'))),qaFrames:frames,visualReview:'pending contact-sheet inspection',humanListeningReview:'pending; ASR-derived word joins not confirmed by listening'};
fs.writeFileSync(path.join(d,`validation-${revision}.json`),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
