"""Public low-performing comparison clips; never require Instagram login."""
from pathlib import Path
import json
import subprocess
import urllib.request

repo=Path(__file__).resolve().parents[5]
cache=repo/'tools/roteiros/work/estudo/fabiohansen'
folder=cache/'folhas'
folder.mkdir(exist_ok=True)
items={i['shortCode']:i for i in json.loads((cache/'apify.json').read_text(encoding='utf-8'))}
for sc in ['DefMse1i-GT','DeC4lxgiMLh','DexlbryiAFW']:
    image=folder/f'folha-{sc}.png'
    if image.exists():
        continue
    video=folder/f'controle-{sc}.mp4'
    req=urllib.request.Request(items[sc]['videoUrl'],headers={'User-Agent':'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req,timeout=60) as response,video.open('wb') as target:
            while chunk:=response.read(1024*1024):
                target.write(chunk)
        duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(video)],text=True))
        step=duration/16
        subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-i',str(video),'-vf',f'fps=1/{step:.4f},scale=240:-1,tile=8x2','-frames:v','1',str(image)],check=True)
        print(sc,round(duration,1),'seconds',flush=True)
    finally:
        if video.exists():
            video.unlink()
