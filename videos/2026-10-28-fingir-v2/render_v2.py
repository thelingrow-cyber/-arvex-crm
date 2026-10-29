"""Replace the athlete insert; preserve user's music, captions and cuts."""
from pathlib import Path
import json
import shutil
import subprocess
import prepare_top

root=Path(__file__).resolve().parent
repo=root.parents[1]
assets=root/'assets'
source=assets/'source-musica.mp4'
final=root/'2026-10-28-fingir-musica-headline-v3.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(source)],text=True))
duration=float(probe['format']['duration'])
shutil.copy2(repo/'tools/video-recut/assets/vendor/gsap.min.js',assets/'gsap.min.js')
composition=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Quanto mais você finge</title><script src="assets/gsap.min.js"></script><style>html,body{{margin:0;width:100%;height:100%;overflow:hidden}}#root{{position:relative;width:100%;height:100%}}.source{{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}}.top{{position:absolute;left:0;top:0;width:1080px;height:900px}}</style></head><body><div id="root" data-composition-id="fingir-v2" data-width="1080" data-height="1920" data-duration="{duration}"><video id="source" class="clip source" src="assets/source-musica.mp4" data-start="0" data-duration="{duration}" data-track-index="0" data-has-audio="true"></video><img id="topo-headline" class="clip top" src="assets/topo-headline.png" data-start="0" data-duration="{duration}" data-track-index="1" alt="Duas imagens cinematográficas lado a lado e headline: quanto mais você finge, menos você finge."></div><script>const tl=gsap.timeline({{paused:true}});window.__timelines['fingir-v2']=tl;</script></body></html>'''
(root/'index.html').write_text(composition,encoding='utf-8')
(root/'hyperframes.json').write_text(json.dumps({'authoringSkill':'general-video'}),encoding='utf-8')
args=['ffmpeg','-hide_banner','-y','-threads','2','-i',str(source),'-loop','1','-framerate','30','-i',str(assets/'topo-headline.png'),'-filter_complex_threads','1','-filter_complex','[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v]','-map','[v]','-map','0:a:0','-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-c:a','copy','-movflags','+faststart','-progress','pipe:1','-nostats',str(final)]
with (root/'render-v3.log').open('w',encoding='utf-8') as log:
    subprocess.run(args,check=True,stdout=log,stderr=log)
print('Rendered:',final.name,flush=True)
