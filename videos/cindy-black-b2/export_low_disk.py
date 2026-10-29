"""Low-disk delivery encoder for the verified HyperFrames composition.
Uses staged shots and same timed cards/captions; no temporary video frames.
"""
import json,re,subprocess
from pathlib import Path
from PIL import ImageFont

P=Path(__file__).resolve().parent
timing=json.loads((P/'timing.json').read_text(encoding='utf-8'))
b=timing['beats'];words=timing['words'];TOTAL=45
font=ImageFont.truetype(str(P/'assets/Inter-800.ttf'),56)
def stamp(t):
    cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
def txt(s):return s.replace('\\','').replace('{','').replace('}','')
events=[]
def event(s,e,style,body,layer=2):
    events.append(f'Dialogue: {layer},{stamp(s)},{stamp(e)},{style},,0,0,0,,{body}')
def rect(s,e,x,y,w,h,color='2E1714',layer=0):
    event(s,e,'Base',f'{{\\an7\\pos(0,0)\\p1\\1c&H{color}&\\bord0}}m {x} {y} l {x+w} {y} {x+w} {y+h} {x} {y+h}',layer)
def label(s,e,x,y,size,text,color='F6FDFF',layer=2):
    event(s,e,'Base',f'{{\\an7\\pos({x},{y})\\fs{size}\\1c&H{color}&\\bord0}}'+txt(text),layer)

rect(0,TOTAL,78,260,924,63)
label(0,TOTAL,101,276,24,'CINDY BATISTA','70B8DD')
event(0,TOTAL,'Base',r'{\an9\pos(979,276)\fs24\1c&H70B8DD&\bord0}BLACK RECORDE')
rect(0,TOTAL,78,1500,874,75)
event(0,TOTAL,'Base',r'{\an5\pos(515,1537)\fs29\1c&H70B8DD&\bord0}27 OUT   ·   20H   ·   AO VIVO E GRATUITO')

cards=[('hook',0,b['discount'],'MESMO DESCONTO.',['POR QUE ESCOLHER','A SUA ÓTICA?']),
('price',b['discount']+.25,b['before'],'VENDER MAIS',['E SOBRAR','MENOS?']),
('early',b['before'],b['invite'],'A BLACK COMEÇA',['ANTES DE','NOVEMBRO.']),
('event',b['workshop']-.5,b['plan'],'WORKSHOP',['OPERAÇÃO','BLACK RECORDE']),
('plan',b['plan'],b['promise'],'VAMOS MONTAR JUNTOS',['OFERTA.','CAMPANHA.']),
('promise',b['promise'],b['cta'],'BUSQUE UM NOVO RECORDE',['OS MAIORES','60 DIAS DO ANO.']),
('cta',b['cta'],TOTAL,'27/10 · 20H · GRATUITO',['ENTRE NO','GRUPO VIP'])]
for ident,s,e,kicker,lines in cards:
    size=70 if ident=='event' else 64
    lh=round(size*1.13);bottom=432+2*lh+59
    rect(s,e,78,350,924,bottom-350)
    rect(s,e,78,bottom-3,924,3,'70B8DD')
    label(s,e,114,385,25,kicker,'70B8DD')
    for j,line in enumerate(lines):
        y=432+j*lh;delay=j*.11
        body=f'{{\\an7\\move(114,{y+85},114,{y},0,{240-j*30})\\clip(114,{y},966,{y+lh})\\fs{size}\\bord0}}'+txt(line)
        event(s+delay,e,'Base',body)
    rect(s+.14,e,114,bottom-35,120,5,'70B8DD')

groups=[];cur=[]
for word in words:
    if cur and (len(' '.join(w['text'] for w in cur+[word]))>30 or len(cur)>=5):groups.append(cur);cur=[]
    cur.append(word)
    if re.search(r'[.!?…]$',word['text']):groups.append(cur);cur=[]
if cur:groups.append(cur)
for i,g in enumerate(groups):
    s=g[0]['start'];e=min(g[-1]['end']+.12,groups[i+1][0]['start'] if i+1<len(groups) else 44)
    lines=[];line=''
    for word in g:
        trial=(line+' '+word['text']).strip()
        if line and font.getlength(trial)>824:lines.append(line);line=word['text']
        else:line=trial
    if line:lines.append(line)
    rich=r'\N'.join(txt(x) for x in lines)
    rich=re.sub(r'\b(desconto|lucro|Black|oferta|campanha|Recorde|gratuito|sessenta|VIP)\b',lambda m:r'{\1c&H70B8DD&}'+m[0]+r'{\1c&HF6FDFF&}',rich,flags=re.I)
    event(s,e,'Caption',r'{\an5\pos(515,1387)}'+rich,4)

header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,Inter ExtraBold,64,&H00F6FDFF,&H00F6FDFF,&H002E1714,&H002E1714,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Caption,Inter ExtraBold,56,&H00F6FDFF,&H00F6FDFF,&H002E1714,&H002E1714,0,0,0,0,100,100,0,0,3,18,0,5,78,128,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
(P/'delivery.ass').write_text(header+'\n'.join(events)+'\n',encoding='utf-8-sig')
shots=[f"file 'assets/shot-{i:02}{'-sdr' if i==5 else ''}.mp4'" for i in range(12)]
(P/'delivery-concat.txt').write_text('\n'.join(shots),encoding='utf-8')
cmd=['ffmpeg','-hide_banner','-y','-loglevel','info','-threads','2','-f','concat','-safe','0','-i','delivery-concat.txt','-i','assets/mix.wav','-vf','ass=delivery.ass:fontsdir=assets','-t','45','-r','30','-c:v','libx264','-preset','fast','-crf','19','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-progress','render-progress.txt','-nostats','cindy-black-recorde-45s.mp4']
with (P/'render-low-disk.log').open('w',encoding='utf-8') as log:
    subprocess.run(cmd,cwd=P,stdout=log,stderr=log,check=True)
print('MP4 exported: cindy-black-recorde-45s.mp4',flush=True)
