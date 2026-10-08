# Kiwify — revisão 2

Revisão solicitada em 13/09/2026: mais ritmo, motions nos inserts, criação por IA,
flashes pontuais, música discreta e encerramento direto. V1 e fonte preservadas.

## Edição

- 27,067s previstos, 1080×1920, 30fps. Mesmas falas e cortes-base da V1.
- Velocidades aproximadamente 1,10 / 1,06 / 1,12 / 1,12 / 1,04× por bloco.
  Vídeo, áudio e legendas remapeados juntos; `atempo` preserva a altura da voz.
- Ecossistema 2,7s, criação por IA 2s e expansão do funil 2,1s: animações por etapas,
  não zoom em PNG. Somam 6,8s; rosto permanece em cerca de 75% da edição.
- Card aprovado “Novas possibilidades / IA + tecnologia” preservado sobre a pessoa,
  com entrada/saída suaves, após a sequência de criação.
- Três pulsos quentes de cerca de 0,15s; sem flash em cada corte.
- Sem CTA, sem frame congelado promocional. Termina em “seu crescimento”.
- Não há CRM, produto pessoal, resultado fictício ou fala sintetizada.

## Música

“Close Up”, Michael Ramir C., item 1167 do Mixkit. Seleção pelo catálogo de
rhythmic underscore/positive/futuristic, não por identificação da faixa da referência.
Fonte: https://mixkit.co/free-stock-music/tag/technology/
Arquivo público: https://assets.mixkit.co/music/1167/1167.mp3
Licença indicada: https://mixkit.co/license/#musicFree
FAQ oficial permite uso em vídeos, podcasts e redes sociais:
https://mixkit.co/free-stock-music/

Trecho começa em 8s da música; cama normalizada a -31 LUFS antes de redução automática
pela voz, com EQ para abrir espaço à fala e fades nas pontas. Mix final alvo -16 LUFS.
Não foi extraída música de vídeo alheio. Não houve compra, cadastro ou publicação.

## Referências e limites da análise

- Referência local da Luana: um light leak composto em ~10,63–10,97s; aos20,30s há
  corte seco, não segundo flash. Ver `analysis-v2/diagnostico-referencia.md`.
- Short Modern Wisdom, “Por que as pessoas bem-sucedidas são tão produtivas”:
  https://www.youtube.com/watch?v=L1pI-bxewHQ . Página consultada em13/09 exibia
  122 mil visualizações e publicação há8 dias. Quadros amostrados mostram B-roll,
  tipografia em movimento e imagens ilustrando termos da fala. Não constitui ranking
  de viralidade. Só parte dessa densidade foi adotada para manter o rosto como foco.
- Anthony Smith, entrevista publicada em29/07/2026: descrição oficial aborda narrativa,
  música/sound design e o risco de copiar a identidade de outro podcast:
  https://podcasts.apple.com/gb/podcast/diary-of-a-ceo-trailer-editor-anthony-smith/id1883368447?i=1000778823730
- Números de ritmo/tempo desta edição são decisões editoriais próprias, não parâmetros
  medidos nos podcasts americanos. Não houve audição dos vídeos pelo modelo.

## Reprodução e conferência

Executar `node build-v2.cjs --render` nesta pasta (ou pelo caminho completo). O comando
usa `-n`: não sobrescreve a V2 existente. Motions: `node v2-motion/build-motions.cjs`.
Manifesto: `edit-manifest-v2.json`. Legendas: `captions-v2.ass`/`.srt`.
Ver `validation-v2.json` e `qa-v2.jpg` para verificações finais.

As legendas continuam baseadas no ASR local da V1; permanece pendente a conferência
auditiva humana, especialmente “Você pode ser explorado...”. A validação numérica
não substitui ouvir timbre, música e emendas na reprodução.

Gates do repositório repetidos: lint/typecheck/build inexistentes; `npm test` falha
no contrato pré-existente dos títulos de CURRENT.md. Sem alteração em package.json.
