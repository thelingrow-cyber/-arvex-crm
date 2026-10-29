"""One top photo, conservative silence cuts and remapped word captions."""
from pathlib import Path
import html
import json
import shutil
import subprocess
import sys
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SOURCE = REPO / 'tools/video-recut/videos/drive/ABAB5FBE-6150-48AE-AF90-DE7003E00CE1.mp4'
SOURCE_DURATION = 43.366667
EDITS = json.loads((ROOT/'cuts.json').read_text(encoding='utf-8')) if (ROOT/'cuts.json').exists() else None
KEEP = EDITS['keep'] if EDITS else [[0,SOURCE_DURATION]]
DURATION = sum(b-a for a,b in KEEP)

def mapped(t):
    offset=0.0
    for a,b in KEEP:
        if t < a:
            return offset
        if t <= b:
            return offset+t-a
        offset += b-a
    return offset

def run(args):
    subprocess.run(args, check=True, cwd=ROOT)

def stamp(t):
    c = round(t * 100)
    return f'{c // 360000}:{c // 6000 % 60:02}:{c // 100 % 60:02}.{c % 100:02}'

def prepare():
    assets = ROOT / 'assets'
    assets.mkdir(exist_ok=True)
    (assets / 'fonts').mkdir(exist_ok=True)
    im = Image.open(ROOT / 'ali-treino-original.jpg').convert('RGB')
    ImageOps.fit(im, (640, 540), Image.Resampling.LANCZOS, centering=(.5, 0)).save(assets / 'topo.jpg', quality=95)
    # Reuse a local font and the project's existing GSAP runtime.
    shutil.copy2('C:/Windows/Fonts/seguisb.ttf', assets / 'fonts/caption.ttf')
    shutil.copy2(REPO / 'tools/video-recut/assets/vendor/gsap.min.js', assets / 'gsap.min.js')
    if not (assets / 'source.mp4').exists():
        shutil.copy2(SOURCE, assets / 'source.mp4')
    raw = json.loads((ROOT / 'transcript-small.json').read_text(encoding='utf-8'))
    ws = [dict(w) for s in raw['segments'] for w in s['words']]
    fixes = json.loads((ROOT / 'correcoes.json').read_text(encoding='utf-8')) if (ROOT / 'correcoes.json').exists() else {}
    timing_fixes=json.loads((ROOT/'timing-corrections.json').read_text(encoding='utf-8')) if (ROOT/'timing-corrections.json').exists() else {}
    for w in ws:
        w['word'] = fixes.get(str(w['start']), w['word']).strip()
        correction=timing_fixes.get(str(w['start']))
        if correction:
            w['start'],w['end']=correction['start'],correction['end']
        w['source_start'],w['source_end']=w['start'],w['end']
        w['start'],w['end']=mapped(w['start']),mapped(w['end'])
    # Degenerate word timestamps are merged, preserving every spoken word.
    merged = []
    for w in ws:
        if merged and w['start'] <= merged[-1]['start']:
            merged[-1]['word'] += ' ' + w['word']
            merged[-1]['end'] = max(merged[-1]['end'], w['end'])
        else:
            merged.append(w)
    captions = []
    for i, w in enumerate(merged):
        next_start = merged[i+1]['start'] if i+1 < len(merged) else DURATION
        end = min(next_start, max(w['end'], w['start'] + .08) + .08, DURATION)
        if end > w['start']:
            captions.append({'text':w['word'], 'start':w['start'], 'end':end})
    (ROOT / 'captions.json').write_text(json.dumps(captions, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT / 'transcricao.txt').write_text(' '.join(x['text'] for x in captions), encoding='utf-8')
    ass = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Segoe UI Semibold,56,&H00FFFFFF,&H00FFFFFF,&H00151515,&H80000000,0,0,0,0,100,100,0,0,1,3,2,5,90,90,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    for c in captions:
        txt = c['text'].replace('{','').replace('}','').rstrip('.,?!;:').lower()
        ass += f"Dialogue: 0,{stamp(c['start'])},{stamp(c['end'])},Caption,,0,0,0,,{{\\pos(540,1430)}}{txt}\n"
    (ROOT / 'captions.ass').write_text(ass, encoding='utf-8-sig')
    cap_html = '\n'.join(f'<div id="caption-{i}" class="clip caption" data-track-index="2" data-start="{c["start"]:.3f}" data-duration="{c["end"]-c["start"]:.3f}"><span>{html.escape(c["text"].rstrip(".,?!;:").lower())}</span></div>' for i,c in enumerate(captions))
    source_rel = 'assets/source.mp4'
    clips=[]
    offset=0.0
    for i,(a,b) in enumerate(KEEP):
        clips.append(f'<video id="source-{i}" class="clip source" src="{source_rel}" data-start="{offset:.6f}" data-media-start="{a:.6f}" data-duration="{b-a:.6f}" data-track-index="0" data-has-audio="true"></video>')
        offset+=b-a
    composition = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Quanto mais você finge</title><script src="assets/gsap.min.js"></script><style>
@font-face{{font-family:Caption;src:url('assets/fonts/caption.ttf')}}*{{box-sizing:border-box}}html,body{{margin:0;width:100%;height:100%;overflow:hidden}}#root{{position:relative;width:100%;height:100%;overflow:hidden}}.source{{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}}.top{{position:absolute;left:220px;top:130px;width:640px;height:540px}}.caption{{position:absolute;left:90px;right:90px;top:1394px;height:72px;display:flex;align-items:center;justify-content:center;font-family:Caption,sans-serif;font-size:56px;color:white;text-shadow:0 2px 5px black;-webkit-text-stroke:1px #151515;z-index:2}}
</style></head><body><div id="root" data-composition-id="fingir" data-width="1080" data-height="1920" data-duration="{DURATION}">
{''.join(clips)}
<img id="top-photo" class="clip top" src="assets/topo.jpg" data-start="0" data-duration="{DURATION}" data-track-index="1" alt="Muhammad Ali e Rahaman Ali treinando">
{cap_html}</div><script>const tl=gsap.timeline({{paused:true}});window.__timelines['fingir']=tl;</script></body></html>'''
    (ROOT / 'index.html').write_text(composition, encoding='utf-8')
    (ROOT / 'hyperframes.json').write_text(json.dumps({'authoringSkill':'general-video'}), encoding='utf-8')
    assert all(0 <= c['start'] < c['end'] <= DURATION for c in captions)
    assert all(a['end'] <= b['start'] for a,b in zip(captions,captions[1:]))
    print(f'Prepared {len(captions)} caption events', flush=True)

def export(preview=False):
    output = 'preview.mp4' if preview else 'fingir-insercao-legendas-cortado.mp4'
    args = ['ffmpeg','-hide_banner','-y','-threads','2']
    if preview:
        args += ['-ss','11.7']
    args += ['-i',str(SOURCE),'-loop','1','-framerate','30','-i','assets/topo.jpg','-filter_complex_threads','1']
    shift = 'setpts=PTS+11.7/TB,' if preview else ''
    unshift = ',setpts=PTS-STARTPTS' if preview else ''
    selections='+'.join(f'between(n,{round(a*30)},{round(b*30)-1})' for a,b in KEEP)
    graph=[f"[0:v]select='{selections}',setpts=N/(30*TB)[base]",
           f'[base][1:v]overlay=220:130:shortest=1,{shift}ass=captions.ass:fontsdir=assets/fonts{unshift},format=yuv420p[v]',
           f'[0:a]asplit={len(KEEP)}'+''.join(f'[a{i}]' for i in range(len(KEEP)))]
    for i,(a,b) in enumerate(KEEP):
        graph.append(f'[a{i}]atrim=start={a:.9f}:end={b:.9f},asetpts=PTS-STARTPTS,afade=t=in:d=0.006,afade=t=out:st={b-a-.006:.9f}:d=0.006[cut{i}]')
    graph.append(''.join(f'[cut{i}]' for i in range(len(KEEP)))+f'concat=n={len(KEEP)}:v=0:a=1[a]')
    args += ['-filter_complex',';'.join(graph),
             '-map','[v]','-map','[a]','-t','5' if preview else str(DURATION),'-c:v','libx264','-preset','veryfast','-crf','18',
             '-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-progress','pipe:1','-nostats',output]
    with (ROOT / ('preview-render.log' if preview else 'render.log')).open('w',encoding='utf-8') as log:
        subprocess.run(args, check=True, cwd=ROOT, stdout=log, stderr=log)
    print(f'Exported {output}', flush=True)

if __name__ == '__main__':
    prepare()
    if '--render' in sys.argv:
        export()
    elif '--preview' in sys.argv:
        export(True)
