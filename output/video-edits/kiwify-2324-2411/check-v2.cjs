'use strict';
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const d=__dirname,r=path.resolve(d,'../../..'),video=path.join(d,'kiwify-2324-2411-edit-v2.mp4');
const ff=path.join(r,'output/video-tools/node_modules/ffmpeg-static/ffmpeg.exe');
const fp=path.join(r,'output/video-tools/node_modules/ffprobe-static/bin/win32/x64/ffprobe.exe');
function run(bin,args){const p=spawnSync(bin,args,{cwd:d,encoding:'utf8',windowsHide:true,maxBuffer:8*1024*1024});if(p.error)throw p.error;if(p.status!==0)throw Error(p.stderr||p.stdout);return p;}
const probe=JSON.parse(run(fp,['-v','error','-show_streams','-show_format','-of','json',video]).stdout);
run(ff,['-hide_banner','-v','error','-xerror','-threads','2','-i',video,'-f','null','-']);
const meter=run(ff,['-hide_banner','-nostats','-threads','2','-i',video,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']).stderr;
const loudness=JSON.parse(meter.slice(meter.lastIndexOf('{')));
const frames=[15,150,186,447,489,531,675,797];
run(ff,['-hide_banner','-v','error','-n','-threads','2','-i',video,'-vf',`select='${frames.map(n=>`eq(n,${n})`).join('+')}',scale=270:480,tile=4x2`,'-frames:v','1','-q:v','2',path.join(d,'qa-v2.jpg')]);
const streams=probe.streams.map(s=>({type:s.codec_type,codec:s.codec_name,width:s.width,height:s.height,fps:s.avg_frame_rate,frames:s.nb_frames,duration:s.duration,sampleRate:s.sample_rate}));
const result={file:video,duration:probe.format.duration,size:probe.format.size,streams,decode:'pass',loudness,visualFrames:frames,visualReview:'contact sheet generated; review in session',humanListeningReview:'pending; ASR wording and subjective music/voice balance need playback'};
fs.writeFileSync(path.join(d,'validation-v2.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
