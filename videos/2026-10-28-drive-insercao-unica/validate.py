"""Check cut delivery, caption preservation, decoding and review frames."""
from pathlib import Path
import json
import subprocess
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent
final = root / 'fingir-insercao-legendas-cortado.mp4'

def output(args):
    return subprocess.check_output(args, cwd=root, text=True, encoding='utf-8')

probe = json.loads(output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(final)]))
video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
audio = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
cuts=json.loads((root/'cuts.json').read_text(encoding='utf-8'))
assert (video['width'], video['height']) == (1080,1920)
assert video['codec_name'] == 'h264'
assert video['r_frame_rate'] == '30/1'
assert abs(float(video['duration'])-cuts['output_duration']) < .04
assert abs(float(audio['duration'])-float(video['duration'])) < .05
captions=json.loads((root/'captions.json').read_text(encoding='utf-8'))
raw=json.loads((root/'transcript-small.json').read_text(encoding='utf-8'))
before=' '.join(w['word'].strip() for s in raw['segments'] for w in s['words'])
after=' '.join(c['text'].strip() for c in captions)
assert before==after, 'Caption words were removed or changed'
assert all(0 <= c['start'] < c['end'] <= cuts['output_duration'] for c in captions)
decode = subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(final),'-f','null','-'],capture_output=True,text=True)
assert decode.returncode == 0 and not decode.stderr.strip(), decode.stderr
times=[1.5,8.9,12.8,17.5,23.8,27.4,31.9,36.8]
sheet = Image.new('RGB',(1080,1010),'#161616')
draw=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
    frame=root / f'check-{i}.jpg'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(final),'-frames:v','1','-vf','scale=270:480',str(frame)],check=True)
    x,y=(i%4)*270,(i//4)*505
    sheet.paste(Image.open(frame),(x,y+25))
    draw.text((x+10,y+7),f'{t:.1f}s',fill='white')
sheet.save(root/'contact-sheet.jpg',quality=94)
subprocess.run(['ffmpeg','-v','error','-y','-ss','27.4','-i',str(final),'-frames:v','1','-vf','scale=540:960',str(root/'preview-final.jpg')],check=True)
report={'duration_seconds':float(probe['format']['duration']),'video_duration_seconds':float(video['duration']),'expected_duration_seconds':cuts['output_duration'],'source_duration_seconds':cuts['source_duration'],'removed_seconds':cuts['source_duration']-cuts['output_duration'],'pause_cuts':len(cuts['cuts']),'bytes':final.stat().st_size,'video':{'codec':video['codec_name'],'width':1080,'height':1920,'fps':video['r_frame_rate'],'frames':video.get('nb_frames')},'audio':{'codec':audio['codec_name'],'duration':audio['duration']},'decode_errors':decode.stderr,'caption_events':len(captions),'all_transcript_words_preserved':before==after,'photo_count':1,'review_seconds':times}
(root/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
