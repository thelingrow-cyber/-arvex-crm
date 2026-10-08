'use strict';
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const {createCanvas,GlobalFonts}=require('@napi-rs/canvas');
const d=__dirname,edit=path.dirname(d),root=path.resolve(edit,'../../..');
const ff=path.join(root,'output/video-tools/node_modules/ffmpeg-static/ffmpeg.exe');
GlobalFonts.registerFromPath('C:/Windows/Fonts/segoeuib.ttf','CaseBold');
function label(name,text,gradient=false){const c=createCanvas(1080,1920),x=c.getContext('2d');if(gradient){const g=x.createLinearGradient(0,1320,0,1920);g.addColorStop(0,'rgba(6,11,14,0)');g.addColorStop(.62,'rgba(6,11,14,.72)');g.addColorStop(1,'rgba(6,11,14,.86)');x.fillStyle=g;x.fillRect(0,1320,1080,600);}x.fillStyle='rgba(10,17,20,.86)';x.beginPath();x.roundRect(54,118,620,102,17);x.fill();x.fillStyle='#e6c982';x.fillRect(54,118,7,102);x.font='37px CaseBold';x.fillStyle='#f7f4ec';x.fillText(text,88,184);fs.writeFileSync(path.join(d,name+'.png'),c.toBuffer('image/png'));}
label('label-guday','MANU CIT  ×  GUDAY');label('label-mrbeast','MRBEAST  ×  FEASTABLES',true);
function run(args){const r=spawnSync(ff,args,{cwd:d,stdio:'inherit',windowsHide:true});if(r.error)throw r.error;if(r.status)process.exit(r.status);}
if(!fs.existsSync(path.join(d,'guday-case.mp4')))run(['-hide_banner','-loglevel','error','-n','-ss','16.4','-t','1.4','-i',path.join(edit,'v5-assets/guday-founder.mp4'),'-loop','1','-framerate','30','-i','label-guday.png','-filter_complex','[0:v]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,hqdn3d=0.8:0.7:2.2:2.0,cas=strength=0.16,fps=30[base];[base][1:v]overlay=0:0:shortest=1,format=yuv420p[v]','-map','[v]','-an','-t','1.4','-c:v','libx264','-preset','medium','-crf','14','-threads','2','guday-case.mp4']);
if(!fs.existsSync(path.join(d,'mrbeast-case.mp4')))run(['-hide_banner','-loglevel','error','-n','-t','1.4','-i','mrbeast-feastables.mp4','-loop','1','-framerate','30','-i','label-mrbeast.png','-filter_complex',"[0:v]crop=506:900:x='min(707,300+290*t)':y=0,scale=1080:1920:flags=lanczos,fps=30[base];[base][1:v]overlay=0:0:shortest=1,format=yuv420p[v]",'-map','[v]','-an','-t','1.4','-c:v','libx264','-preset','medium','-crf','14','-threads','2','mrbeast-case.mp4']);
console.log('Case-study inserts ready.');
