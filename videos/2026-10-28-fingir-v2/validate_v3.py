from pathlib import Path
import json
import subprocess
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parent
source=root/'assets/source-musica.mp4'
final=root/'2026-10-28-fingir-musica-headline-v3.mp4'
def out(args):
    return subprocess.check_output(args,text=True,encoding='utf-8')
probes={name:json.loads(out(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)])) for name,path in [('source',source),('final',final)]}
v=next(s for s in probes['final']['streams'] if s['codec_type']=='video')
assert (v['width'],v['height'],v['r_frame_rate'])==(1080,1920,'30/1')
assert v['codec_name']=='h264'
assert abs(float(probes['source']['format']['duration'])-float(probes['final']['format']['duration']))<.04
hashes={name:out(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).strip() for name,path in [('source',source),('final',final)]}
assert hashes['source']==hashes['final'],'User music/audio changed'
decode=subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(final),'-f','null','-'],capture_output=True,text=True)
assert decode.returncode==0 and not decode.stderr.strip(),decode.stderr
sheet=Image.new('RGB',(1080,505),'#161616')
for i,t in enumerate([1.5,9,21,33]):
    target=root/f'check-v3-{i}.jpg'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(final),'-frames:v','1','-vf','scale=270:480',str(target)],check=True)
    sheet.paste(Image.open(target),(i*270,25))
    ImageDraw.Draw(sheet).text((i*270+10,7),str(t)+'s',fill='white')
sheet.save(root/'contact-v3.jpg',quality=94)
report={'duration':probes['final']['format']['duration'],'bytes':final.stat().st_size,'width':1080,'height':1920,'fps':'30/1','audio_sha256':hashes,'audio_and_music_identical':True,'decode_errors':decode.stderr,'images':2,'headline':'“quanto mais você finge, menos você finge.”','source_captions':'preserved, not re-created'}
(root/'validation-v3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True,indent=2))
