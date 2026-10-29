"""Shorten silence interiors, preserving 120 ms on either side of speech."""
from pathlib import Path
import json
import math
import re

root=Path(__file__).resolve().parent
duration=43.366667
log=(root/'silence-safe.log').read_text(encoding='utf-8',errors='replace')
silences=[(float(a),float(b)) for a,b in re.findall(r'silence_start: ([\d.]+).*?silence_end: ([\d.]+)',log,re.S)]
cuts=[]
for start,end in silences:
    if start < .5:
        continue  # Keep all of the opening, including the first word.
    if 12 < start < 13:
        continue  # Keep the question's delivery; ASR spans this gap with 'atletas'.
    if end > duration-.1:
        a=math.ceil((start+.4)*30)/30
        b=round(duration*30)/30
    else:
        a=math.ceil((start+.12)*30)/30
        b=math.floor((end-.12)*30)/30
    if b-a >= .12:
        cuts.append([a,b])
keep=[]
cursor=0.0
for start,end in cuts:
    if start>cursor:
        keep.append([cursor,start])
    cursor=end
if cursor < duration-.01:
    keep.append([cursor,round(duration*30)/30])
result={'source_duration':duration,'fps':30,'silence_threshold_db':-38,'speech_margin_seconds':.12,'tail_after_speech_seconds':.4,'cuts':cuts,'keep':keep,'output_duration':sum(b-a for a,b in keep),'repeated_phrases_removed':0,'opening_repetition':'intentional, preserved','all_spoken_words':'preserved; only silence interiors removed'}
(root/'cuts.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
