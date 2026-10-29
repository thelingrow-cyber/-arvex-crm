"""Send the requested self-WhatsApp preview, registering the existing approval flow."""
from pathlib import Path
import datetime as dt
import json
import sys
import time

root=Path(__file__).resolve().parent
repo=root.parents[1]
sys.path.insert(0,str(repo/'tools/maquina'))
import insta
import zap

if __name__=='__main__':
    today=str(dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).date())
    occupied={v.get('codigo') for v in zap.estado()['itens'].values() if v.get('dia')==today}
    code=next(f'R{n}' for n in list(range(90,100))+list(range(60,90)) if f'R{n}' not in occupied)
    package='docs/conteudo/maquina/02-Rascunhos/2026-10-28-codex-fingir-v2'
    caption=(repo/package/'legenda.txt').read_text(encoding='utf-8').strip()
    next_time=insta.proximo_horario()
    body=(f'🎬 *{code} · FINGIR V2*\nAchei a versão com música em Prontos. As duas imagens estão lado a lado e a headline está acima/sobre o boné. Música, voz, cortes e legendas foram preservados.\n\n'
          '⚠️ Observe a transição perto de 21 s: a distorção na imagem já vinha no arquivo com música enviado pelo Drive. Se quiser corrigir antes de postar, diga o ajuste.\n\n'
          f'*Legenda proposta:*\n{caption}\n\n'
          f'*Próximo horário livre consultado:* {insta.quando_br(next_time)} (Brasília).\n\n'
          f'Responda em cima desta mensagem: *{code} PODE* = aprova vídeo e legenda e agenda no Instagram @vitorsimoesb no próximo horário livre. Ou me diga o que ajustar.')
    result=zap.video(str(root/'previa-whatsapp.mp4'),body)
    mid=result.get('key',{}).get('id')
    if not mid:
        raise RuntimeError('WhatsApp response contained no message ID; approval flow was not registered.')
    zap.registrar(mid,{'tipo':'video','codigo':code,'pasta':package,'status':'previa','dia':today,'molde':'Regra','origem':'Codex fingir v2, arquivo do usuário com música','horario_consultado':next_time.isoformat()})
    proof={'message_id':mid,'status':result.get('status'),'codigo':code,'sent_at':int(time.time()),'package':package,'approval_required':True,'next_time_consulted':next_time.isoformat(),'caption':caption,'known_source_issue':'Distorção visual em torno de 21s já presente no arquivo do usuário, sinalizada na mensagem de aprovação.'}
    (root/'whatsapp-aprovacao.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':proof['status'],'codigo':code,'message_id':mid,'approval_required':True},ensure_ascii=True))
