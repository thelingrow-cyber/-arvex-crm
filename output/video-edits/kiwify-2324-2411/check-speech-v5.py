"""Local word-timing check for the two user-identified disfluencies; no uploads."""
import os, json
from pathlib import Path
from faster_whisper import WhisperModel
root=Path(__file__).resolve().parent
snap=Path(os.environ['LOCALAPPDATA'])/'WhisperFlow/models/models--Systran--faster-whisper-small/snapshots'
model=WhisperModel(str(next(snap.glob('*/model.bin')).parent),device='cpu',compute_type='int8',cpu_threads=2,local_files_only=True)
for name,offset in [('full',0)]:
    segments,_=model.transcribe(str(root/'source.wav'),language='pt',beam_size=5,word_timestamps=True,vad_filter=False,condition_on_previous_text=False)
    result=[]
    for s in segments:
        result.extend({'word':w.word,'start':round(w.start+offset,3),'end':round(w.end+offset,3),'p':round(w.probability,3)} for w in s.words or [])
    print(json.dumps({'clip':name,'words':result},ensure_ascii=False),flush=True)
