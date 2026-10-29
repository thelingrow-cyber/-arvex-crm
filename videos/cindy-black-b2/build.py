"""Build approved Cindy B2. Local media only; never calls paid providers."""
import json, math, re, shutil, struct, subprocess, wave
from pathlib import Path
from html import escape

P=Path(__file__).resolve().parent
R=P.parents[1]
A=P/'assets'; A.mkdir(exist_ok=True)
D=Path.home()/'Downloads'
VOICE=R/'docs/lancamento-black-recorde/voz/b2-aprovado-45s.mp3'
alignment=json.loads(VOICE.with_name('b2-aprovado-45s-alignment.json').read_text(encoding='utf-8'))['alignment']
RATE=.94; OFFSET=.1; TOTAL=45
def run(*args):
    subprocess.run([str(x) for x in args],check=True)
def ff(*args):
    run('ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2',*args)
def ts(i,end=False):
    return alignment['character_end_times_seconds' if end else 'character_start_times_seconds'][i]/RATE+OFFSET
text=''.join(alignment['characters'])
words=[dict(text=m.group(),start=ts(m.start()),end=ts(m.end()-1,True)) for m in re.finditer(r'\S+',text)]
def at(phrase):
    i=text.casefold().find(phrase.casefold())
    if i<0: raise ValueError(phrase)
    return ts(i)
beats={k:at(v) for k,v in {'discount':'Se tudo','before':'Por isso','invite':'Dia vinte','workshop':'Workshop','free':'Ao vivo','plan':'Vamos montar','promise':'Pra você','sixty':'sessenta','cta':'Clica','link':'O link'}.items()}
(P/'timing.json').write_text(json.dumps({'duration':TOTAL,'beats':beats,'words':words},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(beats,ensure_ascii=False),flush=True)

# Short source ranges, each independently seekable. Preserve actual camera movement.
b=beats
cuts=[(0,3.2,'IMG_4929.MOV',.6),(3.2,b['discount'],'IMG_4931.MOV',2),
(b['discount'],9.5,'IMG_4930.MOV',1.5),(9.5,b['before'],'IMG_4928.MOV',6),
(b['before'],b['invite'],'IMG_4937.MOV',2),
(b['invite'],b['workshop'],'IMG_4934.MOV',.2),
(b['workshop'],b['plan'],'IMG_4928.MOV',12),
(b['plan'],b['promise'],'IMG_4930.MOV',6),
(b['promise'],b['sixty'],'IMG_4931.MOV',7),
(b['sixty'],b['cta'],'IMG_4935.MOV',6),
(b['cta'],b['link'],'IMG_4937.MOV',8),
(b['link'],TOTAL,'IMG_4928.MOV',15)]
for i,(s,e,src,ss) in enumerate(cuts):
    if e<=s: raise ValueError(('bad cut',s,e))
    out=A/(f'shot-{i:02}-sdr.mp4' if i==5 else f'shot-{i:02}.mp4')
    if not out.exists():
        print('Preparing',i,src,round(e-s,2),flush=True)
        vf='fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1'
        if i==5:
            vf='zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,'+vf
        ff('-ss',ss,'-i',D/src,'-t',e-s,'-an','-vf',vf,'-c:v','libx264','-preset','fast','-crf','19','-threads','2','-g','30','-pix_fmt','yuv420p','-movflags','+faststart',out)

# Original ambient score: soft chords, no external recording or marked beat.
if not (A/'bed.wav').exists():
    sr=24000; chords=[[110,164.81,220,261.63],[87.31,130.81,174.61,220],[130.81,196,261.63,329.63],[98,146.83,196,246.94]]
    data=bytearray()
    for n in range(sr*TOTAL):
        t=n/sr; block=int(t/5.6); local=t%5.6
        env=min(1,local/.8)*min(1,(5.6-local)/.8)*min(1,t/1.5)*min(1,(TOTAL-t)/2)
        val=sum(math.sin(2*math.pi*f*t)+.2*math.sin(2*math.pi*f*1.003*t) for f in chords[block%4])*.012*env
        data.extend(struct.pack('<h',int(max(-1,min(1,val))*32767)))
    with wave.open(str(A/'bed.wav'),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(data)
if not (A/'voice.wav').exists():
    ff('-i',VOICE,'-af',f'atempo={RATE},loudnorm=I=-16:TP=-1.5:LRA=8,adelay=100:all=1,apad','-t',TOTAL,'-ar','48000',A/'voice.wav')
if not (A/'mix.wav').exists():
    # Broad spectral space for speech plus sidechain duck; baked identical in preview/render.
    ff('-i',A/'voice.wav','-i',A/'bed.wav','-filter_complex','[0:a]asplit=2[v][sc];[1:a]lowpass=f=700,equalizer=f=400:t=q:w=1:g=-5,equalizer=f=1600:t=q:w=1:g=-9,volume=0.55[m];[m][sc]sidechaincompress=threshold=0.025:ratio=5:attack=15:release=400[duck];[v][duck]amix=inputs=2:normalize=0,alimiter=limit=0.93:level=false[out]','-map','[out]','-t',TOTAL,'-ar','48000',A/'mix.wav')
shutil.copy2(R/'tools/video-recut/assets/fontes/Inter-800.ttf',A/'Inter-800.ttf')
shutil.copy2(R/'tools/video-recut/work/2026-09-boas-vindas/public/vendor/gsap.min.js',A/'gsap.min.js')

groups=[]; cur=[]
for word in words:
    candidate=' '.join(w['text'] for w in cur+[word])
    if cur and (len(candidate)>30 or len(cur)>=5): groups.append(cur);cur=[]
    cur.append(word)
    if re.search(r'[.!?…]$',word['text']):groups.append(cur);cur=[]
if cur:groups.append(cur)
caps=[]
for i,g in enumerate(groups):
    s=g[0]['start'];e=min(g[-1]['end']+.12,groups[i+1][0]['start'] if i+1<len(groups) else 44)
    label=' '.join(w['text'] for w in g)
    rich=re.sub(r'\b(desconto|lucro|Black|oferta|campanha|Recorde|gratuito|sessenta|VIP)\b',r'<b style="color:#DDB870">\1</b>',escape(label),flags=re.I)
    caps.append(f'<div id="caption-{i}" class="clip caption" data-start="{s:.4f}" data-duration="{e-s:.4f}" data-track-index="4"><span>{rich}</span></div>')

# All cards share the film's continuous visual space; no nested media timing.
cards=[('hook',0,b['discount'],'MESMO DESCONTO.',['POR QUE ESCOLHER','A SUA ÓTICA?']),
('price',b['discount']+.25,b['before'],'VENDER MAIS',['E SOBRAR','MENOS?']),
('early',b['before'],b['invite'],'A BLACK COMEÇA',['ANTES DE','NOVEMBRO.']),
('event',b['workshop']-.5,b['plan'],'WORKSHOP',['OPERAÇÃO','BLACK RECORDE']),
('plan',b['plan'],b['promise'],'VAMOS MONTAR JUNTOS',['OFERTA.','CAMPANHA.']),
('promise',b['promise'],b['cta'],'BUSQUE UM NOVO RECORDE',['OS MAIORES','60 DIAS DO ANO.']),
('cta',b['cta'],TOTAL,'27/10 · 20H · GRATUITO',['ENTRE NO','GRUPO VIP'])]
cardhtml=[]; motion=[]
for ident,s,e,kicker,lines in cards:
    linehtml=''.join(f'<div class="line-mask"><div id="{ident}-line-{j}" class="card-line">{escape(line)}</div></div>' for j,line in enumerate(lines))
    cardhtml.append(f'<section id="{ident}" class="clip card {ident}" data-start="{s:.4f}" data-duration="{e-s:.4f}" data-track-index="2"><div class="card-inner"><div class="kicker">{escape(kicker)}</div>{linehtml}<div class="rule"></div></div></section>')
    for j in range(len(lines)):
        motion.append(f'tl.fromTo("#{ident}-line-{j}",{{y:100}},{{y:0,duration:{.24-j*.03},ease:"power4.out",immediateRender:false}},{s+j*.11:.4f});')
    motion.append(f'tl.fromTo("#{ident} .rule",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"power2.out",immediateRender:false}},{s+.14:.4f});')
videos='\n'.join(f'<video id="shot-{i}" class="clip shot" src="assets/shot-{i:02}{"-sdr" if i==5 else ""}.mp4" data-start="{s:.4f}" data-duration="{e-s:.4f}" data-track-index="0" muted playsinline></video>' for i,(s,e,_,_) in enumerate(cuts))
html='''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=1080,height=1920"><title>Cindy — Operação Black Recorde</title><script src="assets/gsap.min.js"></script>
<style>@font-face{font-family:Inter;src:url('assets/Inter-800.ttf');font-weight:800}*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#14172E}#root{position:relative;width:100%;height:100%;overflow:hidden;font-family:Inter,sans-serif;font-weight:800;color:#fffdf6}.shot{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.brand{position:absolute;left:78px;right:78px;top:260px;display:flex;justify-content:space-between;font-size:24px;letter-spacing:3px;background:#14172E;padding:17px 23px;color:#DDB870}.card{position:absolute;left:78px;right:78px;top:350px;z-index:2}.card-inner{background:#14172E;padding:35px 36px 27px;border-bottom:3px solid #DDB870}.kicker{font-size:25px;letter-spacing:3px;margin-bottom:17px;color:#DDB870}.card-line{font-size:64px;line-height:1.13;letter-spacing:-2px}.line-mask{overflow:hidden}.rule{width:120px;height:5px;background:#DDB870;margin-top:24px;transform-origin:left}.hook .card-line:last-child{color:#fffdf6}.event .card-line{font-size:70px}.promise .card-line{font-size:64px}.cta .card-inner{border:3px solid #DDB870}.caption{position:absolute;left:78px;right:128px;top:1305px;height:164px;display:flex;align-items:center;justify-content:center;z-index:4;text-align:center;font-size:56px;line-height:1.16}.caption span{display:block;background:#14172E;padding:15px 25px;border-radius:8px;max-width:100%}.footer{position:absolute;left:78px;right:128px;top:1500px;background:#14172E;padding:20px 18px;z-index:5;display:flex;justify-content:center;gap:28px;font-size:29px;color:#DDB870}.progress{position:absolute;left:0;right:0;bottom:0;height:7px;background:#DDB870;transform-origin:left;z-index:6}</style></head><body>
<div id="root" data-composition-id="cindy-b2" data-start="0" data-duration="45" data-width="1080" data-height="1920">'''+videos+'''
<div class="brand"><span>CINDY BATISTA</span><span>BLACK RECORDE</span></div>'''+''.join(cardhtml)+''.join(caps)+'''
<div class="footer"><span>27 OUT</span><span>20H</span><span>AO VIVO E GRATUITO</span></div><div class="progress"></div><audio id="master" class="clip" src="assets/mix.wav" data-start="0" data-duration="45" data-track-index="6" data-volume="1"></audio></div>
<script>const tl=gsap.timeline({paused:true});'''+''.join(motion)+'''tl.fromTo('.progress',{scaleX:0},{scaleX:1,duration:45,ease:'none'},0);window.__timelines['cindy-b2']=tl;</script></body></html>'''
(P/'index.html').write_text(html,encoding='utf-8')
(P/'hyperframes.json').write_text(json.dumps({'authoringSkill':'general-video','paths':{'assets':'assets','blocks':'compositions','components':'compositions/components'},'media':{'autoProxy':True}},indent=2),encoding='utf-8')
(P/'CREDITOS.md').write_text('# Fontes\n\nVoz: Cindy Batista, voz existente no ElevenLabs, gerada para a copy aprovada.\nImagem: takes locais fornecidos anteriormente para as peças da Cindy.\nTrilha: síntese original neste build, sem gravações de terceiros.\nInter: fonte local existente.\n\nA fala foi desacelerada em 6%, preservando pitch; composição 45 s.\n',encoding='utf-8')
print('BUILD READY: 45s; '+str(len(cuts))+' shots; '+str(len(groups))+' caption groups',flush=True)
