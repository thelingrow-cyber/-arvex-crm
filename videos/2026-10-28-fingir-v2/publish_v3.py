"""Publish only the reduced v3 explicitly authorized in the Codex chat."""
from pathlib import Path
import datetime as dt
import json
import sys
import urllib.request
import uuid

root=Path(__file__).resolve().parent
repo=root.parents[1]
sys.path.insert(0,str(repo/'tools/maquina'))
import insta

record_path=root/'publication-v3.json'
final=root/'2026-10-28-fingir-musica-headline-v3.mp4'
caption=(repo/'docs/conteudo/maquina/02-Rascunhos/2026-10-28-codex-fingir-v2/legenda.txt').read_text(encoding='utf-8').strip()

def save(r):
    record_path.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    validation=json.loads((root/'validation-v3.json').read_text(encoding='utf-8'))
    assert validation['audio_and_music_identical'] and not validation['decode_errors']
    record=json.loads(record_path.read_text(encoding='utf-8')) if record_path.exists() else {
        'idempotency_key':str(uuid.uuid4()),'status':'prepared','account':'@vitorsimoesb',
        'account_id':insta.CONTA_IG,'file':final.name,'caption':caption,
        'authorization':'User explicitly requested smaller images/headline and authorized posting in Codex on 2026-10-28.',
        'created_at':dt.datetime.now(insta.FUSO).isoformat()}
    if record.get('post_id'):
        result=insta.situacao(record['post_id'])
        record.update(result)
        save(record)
        print(json.dumps({'post_id':record['post_id'],**result},ensure_ascii=True),flush=True)
        raise SystemExit(0)
    save(record)
    if not record.get('media_url'):
        record['media_url']=insta.subir(str(final))
        save(record)
    body={'content':caption,'mediaItems':[{'type':'video','url':record['media_url']}],
          'platforms':[{'platform':'instagram','accountId':insta.CONTA_IG,'platformSpecificData':{'shareToFeed':True}}],
          'publishNow':True,'timezone':'America/Sao_Paulo'}
    (root/'publication-request-v3.json').write_text(json.dumps(body,ensure_ascii=False,indent=2),encoding='utf-8')
    record['status']='publishing'
    save(record)
    req=urllib.request.Request(insta.API+'/posts',data=json.dumps(body).encode(),method='POST',headers={
        'Authorization':'Bearer '+insta._env('ZERNIO_API_KEY'),'Content-Type':'application/json',
        'Idempotency-Key':record['idempotency_key']})
    try:
        with urllib.request.urlopen(req,timeout=300) as response:
            result=json.load(response)
    except Exception as e:
        record.update({'status':'publication_uncertain','error_type':type(e).__name__,'http_code':getattr(e,'code',None)})
        save(record)
        print(json.dumps({'status':record['status'],'error_type':record['error_type'],'http_code':record['http_code']},ensure_ascii=True),flush=True)
        raise SystemExit(1)
    post=result.get('post') or result
    platform=next((p for p in post.get('platforms',[]) if p.get('platform')=='instagram'),{})
    record.update({'post_id':post.get('_id') or post.get('id'),'status':post.get('status'),
                   'url':platform.get('platformPostUrl'),'platform_status':platform.get('status'),
                   'published_at':post.get('publishedAt'),'completed_at':dt.datetime.now(insta.FUSO).isoformat()})
    save(record)
    print(json.dumps({k:record.get(k) for k in ['post_id','status','url','platform_status','published_at']},ensure_ascii=True),flush=True)
