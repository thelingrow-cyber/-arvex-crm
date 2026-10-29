"""Generate a dated inventory, not a reproduction of third-party scripts."""
from pathlib import Path
import json

root = Path(__file__).resolve().parent
reels = json.loads((root / 'reels.json').read_text(encoding='utf-8'))
classes = json.loads((root / 'classificacao.json').read_text(encoding='utf-8'))['videos']
summary = json.loads((root / 'resumo-auditado.json').read_text(encoding='utf-8'))
subjects = {
    'DdSJsUEiJPv': 'Bolo, hambúrguer e advogado: decidir pela imagem',
    'DdbwbqdKmil': 'A Origem: percepção e ideias simples',
    'DbrHxedCxKG': 'Academia: comunicação visível no ambiente',
    'DevKYEAi4gg': 'Jobs e clareza na explicação',
    'DeSPEhui2EW': 'Relógio, café e arquiteto: sinais de valor',
    'DeMqYT0iwc4': 'Publicidade de apostas e reputação',
    'DekRYv9CzK1': 'Red Bull: demonstrar em vez de declarar',
    'DfCwGzbCkPB': 'Primeira impressão: versão de 54 segundos',
    'DexlbryiAFW': 'Escolhas de profissionais em níveis',
    'De2DKOxCVO7': 'Primeira impressão: versão de 68 segundos',
    'De2NWmyitqZ': 'Primeira impressão: versão de 64 segundos',
    'De68Z30ics2': 'Manifesto de identificação profissional',
    'DefMse1i-GT': 'Nespresso: construção de uma experiência',
    'DfCtqhzibe5': 'Manifesto de identificação: nova abertura',
    'DeC4lxgiMLh': 'Autoimagem e percepção externa: caso apresentado',
    'DfCzPIZCIVY': 'Três passos para construir marca pessoal',
}
assert set(subjects) == set(classes) == {r['shortCode'] for r in reels}
fmt = lambda n: f'{n:,}'.replace(',', '.')
lines = [
    '# Anexos — Fábio Hansen', '',
    'Coleta em **28/10/2026**. Inventário dos 16 obtidos; não é a lista completa do perfil. '
    'Views, curtidas e comentários são contagens públicas no momento da coleta. '
    'Título descritivo e classificação são editoriais; não são citações do autor.', '',
    '[Dossiê](ESTUDO.md) · [Fontes e reprodução](FONTES.md)', '',
    '## A. Inventário completo, por alcance observado', '',
    '| Reel / assunto resumido | Data | Segundos | Views | Curtidas | Comentários | Situação |',
    '|---|---|---:|---:|---:|---:|---|',
]
for r in sorted(reels, key=lambda x: -x['views']):
    code = r['shortCode']
    status = 'Publicado no dia' if code in summary['recent_ids'] else 'Pelo menos 3 dias'
    lines.append(f"| [{subjects[code]}]({r['url']}) | {r['data']} | {r['duracao']} | {fmt(r['views'])} | {fmt(r['curtidas'])} | {r['comentarios']} | {status} |")
lines += ['', '## B. Classificação de todos os vídeos', '',
          '| Reel | Formato | Entrada, em resumo | Fecho falado |',
          '|---|---|---|---|']
for r in sorted(reels, key=lambda x: (x['data'], x['shortCode'])):
    code = r['shortCode']
    form, hook, cta = classes[code]
    lines.append(f"| [{code}]({r['url']}) | {form} | {hook} | {cta} |")
lines += ['', '## C. Estruturas abstratas para reaproveitar', '',
    '| Estrutura | Encadeamento | Cuidado |', '|---|---|---|',
    '| Escolha visual | Alternativas → decisão do espectador → revelação do critério → aplicação ao trabalho | O contraste precisa ser legível; estética não garante resultado |',
    '| Referência cultural | Situação reconhecível → regra subjacente → consequência pessoal → decisão aplicável | Uma metáfora não é evidência de eficácia |',
    '| Auditoria cotidiana | Observação própria → detalhes visíveis → função de cada detalhe → descoberta transferível | Exige observação real; não inventar experiência |',
    '| Caso histórico ou de marca | Fato verificado → decisão do protagonista → princípio → aplicação | Verificar fatos e evitar inferir causalidade comercial |',
    '| Diagnóstico real | Artefato → diferença entre expectativa e observação → critério de correção | Não é garantia de alcance; preservar dados de clientes |', '',
    '## D. Versões e cautelas', '',
    '- Primeira impressão: `De2DKOxCVO7`, `De2NWmyitqZ` e `DfCwGzbCkPB` compartilham o argumento. '
    'As duas primeiras são do mesmo dia; a terceira tem outro corte. Sem aleatorização, não é teste A/B comprovado.',
    '- Manifesto: `De68Z30ics2` e `DfCtqhzibe5` têm texto muito próximo e alteração na abertura.',
    '- Três vídeos são de 28/10 e não entram na mediana com pelo menos três dias. '
    'O vídeo mais antigo com 396 views permanece na base. Status de trial, mídia paga e retenção são desconhecidos.',
    '- Nove folhas visuais inspecionadas: `DdSJsUEiJPv`, `DdbwbqdKmil`, `DbrHxedCxKG`, '
    '`DevKYEAi4gg`, `DeSPEhui2EW`, `DeMqYT0iwc4`, `DefMse1i-GT`, `DeC4lxgiMLh`, `DexlbryiAFW`.',
    '- As transcrições automáticas ficam nos dados de análise. Este anexo resume a estrutura; não reproduz roteiros integrais.', '',
]
(root / 'ANEXOS.md').write_text('\n'.join(lines), encoding='utf-8')
print(f'ANEXOS.md: {len(reels)} vídeos; {len(classes)} classificados.')
