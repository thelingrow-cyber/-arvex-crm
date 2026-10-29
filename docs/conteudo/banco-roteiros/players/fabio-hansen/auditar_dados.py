"""Recompute descriptive metrics without calling low views 'failed trials'."""
from pathlib import Path
from datetime import datetime,date,timezone,timedelta
from collections import defaultdict
import json
from statistics import median

root=Path(__file__).resolve().parent
reels=json.loads((root/'reels.json').read_text(encoding='utf-8'))
today=date(2026,10,28)
classification={
'DdSJsUEiJPv':['Escolha visual → diagnóstico','Pergunta com decisão imediata','Seguir'],
'DdbwbqdKmil':['Cinema → princípios aplicados','Objeto cultural + promessa de aprendizado','Seguir'],
'DbrHxedCxKG':['Auditoria visual no cotidiano','Experiência própria + descoberta concreta','Seguir'],
'DevKYEAi4gg':['Fato histórico → regra de comunicação','Paradoxo sobre inteligência','Seguir'],
'DeSPEhui2EW':['Escolha visual → diagnóstico','Pergunta com decisão imediata','Seguir'],
'DeMqYT0iwc4':['Opinião → consequência reputacional','Provocação a ser reavaliada','Seguir'],
'DekRYv9CzK1':['Caso de marca → aplicação','Marca como referência de competência','Seguir'],
'DfCwGzbCkPB':['Experimento → aplicação','Curiosidade sobre tempo de julgamento','Seguir'],
'DexlbryiAFW':['Escolha visual → diagnóstico','Desafio de julgamento com níveis','Seguir'],
'De2DKOxCVO7':['Experimento → aplicação','Curiosidade sobre tempo de julgamento','Seguir'],
'De2NWmyitqZ':['Experimento → aplicação','Pesquisa como abertura','Seguir'],
'De68Z30ics2':['Identificação → convite','Desejos em tensão','Acolhimento'],
'DefMse1i-GT':['Caso de marca → aplicação','Marca como referência de competência','Seguir'],
'DfCtqhzibe5':['Identificação → convite','Desejos em tensão','Acolhimento'],
'DeC4lxgiMLh':['Caso de cliente → diagnóstico','Analogia visual de reputação','Seguir'],
'DfCzPIZCIVY':['Lista educativa','Promessa de três passos','Seguir'],
}
families=[{'name':'Experimento sobre primeira impressão','ids':['De2DKOxCVO7','De2NWmyitqZ','DfCwGzbCkPB'],'note':'Mesmo argumento e grandes blocos de fala; versões/cortes, não três ideias independentes.'},
          {'name':'Manifesto de identificação','ids':['De68Z30ics2','DfCtqhzibe5'],'note':'Texto muito próximo, abertura ligeiramente alterada.'}]
assert set(classification)=={x['shortCode'] for x in reels}
recent=[x for x in reels if (today-date.fromisoformat(x['data'])).days<3]
mature=[x for x in reels if x not in recent]
by_format=defaultdict(list)
for x in reels:
    by_format[classification[x['shortCode']][0]].append(x)
def med(xs,key='views'):
    values=[x[key] for x in xs if x.get(key) is not None and x[key]>=0]
    return median(values) if values else None
dedup=[x for x in mature if x['shortCode']!='De2NWmyitqZ']
total=sum(x['views'] or 0 for x in reels)
ranked=sorted(reels,key=lambda x:-(x['views'] or 0))
summary={'collected_on':'2026-10-28','collected_timezone':'America/Sao_Paulo','target_n':50,'obtained_n':len(reels),'window':[min(x['data'] for x in reels),max(x['data'] for x in reels)],
'sampling_limit':'Reel scraper returned 16 despite limit 100. Second generic collection refused with HTTP 402 Payment Required; no claim of exhaustive profile coverage or independent historical peaks.',
'median_views_all':med(reels),'median_views_at_least_3_days':med(mature),'n_at_least_3_days':len(mature),'median_views_mature_one_early_version_per_family':med(dedup),'n_mature_deduplicated':len(dedup),
'median_duration_all_seconds':med(reels,'duracao'),'median_duration_mature_seconds':med(mature,'duracao'),'recent_ids':[x['shortCode'] for x in recent],
'low_views_under_500':[x['shortCode'] for x in reels if x.get('views') is not None and x['views']<500],
'low_views_interpretation':'Low public view counts; trial status, ad spend and distribution unavailable. Low older post remains in baseline.',
'total_views_observed':total,'top3_views_share':sum(x['views'] for x in ranked[:3])/total,
'spoken_follow_cta_count':sum(classification[x['shortCode']][2]=='Seguir' for x in reels),
'ratios':{'quiz_september_vs_october_9':233151/12155,'quiz_september_vs_october_21':233151/1613,'origin_vs_nespresso':158055/1007,'origin_vs_mature_median':158055/med(mature),'gym_vs_mature_median':69317/med(mature)},
'formats':[],'families':families}
for label,items in by_format.items():
    eligible=[x for x in items if x in mature]
    summary['formats'].append({'format':label,'n':len(items),'median_all':med(items),'max_views':max(x['views'] for x in items),'n_mature':len(eligible),'median_mature':med(eligible)})
(root/'classificacao.json').write_text(json.dumps({'usuario':'fabiohansen','videos':classification,'repostagens':[],'picos':[],'familias_de_versoes':families,'note':'Do not infer trial reels from a threshold or consider same-argument versions independent.'},ensure_ascii=False,indent=2),encoding='utf-8')
(root/'resumo-auditado.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
