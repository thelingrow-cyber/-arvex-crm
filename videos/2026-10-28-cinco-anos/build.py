"""Cinco anos: corta pausas, duas fotos de época no topo, headline e legenda palavra a palavra.
Uso: python build.py [--preview|--render]"""
from pathlib import Path
import json, math, re, subprocess, sys
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SRC = ROOT / 'assets/source.mp4'
DUR = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(SRC)], text=True))
HEADLINE = ['“o pior de perder 5 anos', 'é usar isso como motivo', 'pra perder mais 5.”']
FIX = {'investir': 'investi'}


def plan_cuts():
    log = (ROOT / 'silence-safe.log').read_text(encoding='utf-8', errors='replace')
    sil = [(float(a), float(b)) for a, b in re.findall(r'silence_start: ([\d.]+).*?silence_end: ([\d.]+)', log, re.S)]
    cuts = []
    for s, e in sil:
        if e > DUR - .1:
            a, b = math.ceil((s + .4) * 30) / 30, round(DUR * 30) / 30
        else:
            a, b = math.ceil((s + .12) * 30) / 30, math.floor((e - .12) * 30) / 30
        if b - a >= .1:
            cuts.append([a, b])
    keep, cur = [], 0.0
    for a, b in cuts:
        if a > cur:
            keep.append([cur, a])
        cur = b
    if cur < DUR - .01:
        keep.append([cur, round(DUR * 30) / 30])
    (ROOT / 'cuts.json').write_text(json.dumps({'cuts': cuts, 'keep': keep, 'out': sum(b - a for a, b in keep)}, indent=1), encoding='utf-8')
    return keep


KEEP = plan_cuts()
OUT = sum(b - a for a, b in KEEP)


def mapped(t):
    off = 0.0
    for a, b in KEEP:
        if t < a:
            return off
        if t <= b:
            return off + t - a
        off += b - a
    return off


def stamp(t):
    c = round(t * 100)
    return f'{c // 360000}:{c // 6000 % 60:02}:{c // 100 % 60:02}.{c % 100:02}'


def topo():
    ov = Image.new('RGBA', (1080, 900), (0, 0, 0, 0))
    for name, x in [('img-1.jpg', 140), ('img-2.jpg', 540)]:
        im = ImageOps.fit(Image.open(ROOT / 'assets' / name).convert('RGB'), (400, 480), Image.Resampling.LANCZOS, centering=(.5, .5))
        ov.paste(im, (x, 130))
    font = ImageFont.truetype(str(REPO / 'tools/video-recut/assets/fontes/Inter-800.ttf'), 56)
    y0, lh = 636, 68
    sh = Image.new('RGBA', ov.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i, l in enumerate(HEADLINE):
        sd.text((540, y0 + i * lh), l, font=font, anchor='mt', fill=(0, 0, 0, 245), stroke_width=7, stroke_fill=(0, 0, 0, 245))
    ov = Image.alpha_composite(ov, sh.filter(ImageFilter.GaussianBlur(2)))
    d = ImageDraw.Draw(ov)
    for i, l in enumerate(HEADLINE):
        d.text((540, y0 + i * lh), l, font=font, anchor='mt', fill='white', stroke_width=3, stroke_fill=(0, 0, 0, 255))
    ov.save(ROOT / 'assets/topo-headline.png')


def legendas():
    raw = json.loads((ROOT / 'transcript.json').read_text(encoding='utf-8'))
    ws = []
    for w in raw['words']:
        txt = w['word'].strip().rstrip('.,?!;:').lower()
        txt = FIX.get(txt, txt)
        s, e = mapped(w['start']), mapped(w['end'])
        if ws and s <= ws[-1]['start']:
            ws[-1]['text'] += ' ' + txt
            ws[-1]['end'] = max(ws[-1]['end'], e)
        else:
            ws.append({'text': txt, 'start': s, 'end': e})
    caps = []
    for i, w in enumerate(ws):
        nxt = ws[i + 1]['start'] if i + 1 < len(ws) else OUT
        end = min(nxt, max(w['end'], w['start'] + .08) + .08, OUT)
        if end > w['start']:
            caps.append({**w, 'end': end})
    ass = ('[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n'
           '[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
           'Style: Caption,Segoe UI Semibold,56,&H00FFFFFF,&H00FFFFFF,&H00151515,&H80000000,0,0,0,0,100,100,0,0,1,3,2,5,90,90,0,1\n\n'
           '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
    for c in caps:
        ass += f"Dialogue: 0,{stamp(c['start'])},{stamp(c['end'])},Caption,,0,0,0,,{{\\pos(540,1430)}}{c['text']}\n"
    (ROOT / 'captions.ass').write_text(ass, encoding='utf-8-sig')
    (ROOT / 'transcricao.txt').write_text(' '.join(c['text'] for c in caps), encoding='utf-8')
    return len(caps)


def export(preview=False):
    out = 'previa.mp4' if preview else '2026-10-28-cinco-anos.mp4'
    sel = '+'.join(f'between(n,{round(a * 30)},{round(b * 30) - 1})' for a, b in KEEP)
    g = [f"[0:v]select='{sel}',setpts=N/(30*TB)[base]",
         "[base][1:v]overlay=0:0:shortest=1,ass=captions.ass,format=yuv420p[v]",
         f'[0:a]asplit={len(KEEP)}' + ''.join(f'[a{i}]' for i in range(len(KEEP)))]
    for i, (a, b) in enumerate(KEEP):
        g.append(f'[a{i}]atrim=start={a:.6f}:end={b:.6f},asetpts=PTS-STARTPTS,afade=t=in:d=0.006,afade=t=out:st={b - a - .006:.6f}:d=0.006[c{i}]')
    g.append(''.join(f'[c{i}]' for i in range(len(KEEP))) + f'concat=n={len(KEEP)}:v=0:a=1[a]')
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-threads', '2', '-i', str(SRC), '-loop', '1', '-framerate', '30',
            '-i', 'assets/topo-headline.png', '-filter_complex_threads', '1', '-filter_complex', ';'.join(g),
            '-map', '[v]', '-map', '[a]', '-t', '8' if preview else f'{OUT:.3f}', '-c:v', 'libx264', '-preset', 'veryfast',
            '-crf', '18', '-threads', '2', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out]
    subprocess.run(args, check=True, cwd=ROOT)
    print('ok', out)


if __name__ == '__main__':
    topo()
    n = legendas()
    print(f'fonte {DUR:.2f}s -> {OUT:.2f}s, {len(KEEP)} trechos, {n} legendas')
    if '--render' in sys.argv:
        export()
    elif '--preview' in sys.argv:
        export(True)
