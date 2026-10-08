# Análise do enquadramento — 23:24–24:11

Fonte: 1920×1080, H.264, 30 fps. Alvo: participante de camiseta preta à direita, definido pelo contexto da tarefa; nenhuma comparação de identidade feita.

## Cortes recomendados

Coordenadas na fonte, no formato FFmpeg `crop=w:h:x:y`:

- Principal: `crop=504:896:1066:134`.
- Aproximação discreta de 1,12×: `crop=450:800:1094:172`.
- Ambos têm proporção 9:16 exata. Rostos alheios ficam fora. Rosto, tronco e a maior parte dos gestos do alvo são preservados.
- Legendas podem ocupar a região inferior do tronco/mesa, preservando olhos e boca.

Foram extraídos e inspecionados frames em +0, +6, +12, +18, +24, +30 e +36 segundos. Os arquivos `full-N.jpg` mantêm 1920×1080; `medium-N.jpg` e `close-N.jpg` ilustram os crops a 720×1280.

## Acompanhamento opcional

O rosto oscila pouco e os crops fixos já funcionam. Para acompanhamento discreto, interpolar suavemente o x do plano principal por estes valores aproximados, estimados visualmente:

| Tempo relativo | x principal | x close |
|---|---:|---:|
| 0 s | 1066 | 1094 |
| 6 s | 1056 | 1084 |
| 12 s | 1060 | 1088 |
| 18 s | 1074 | 1102 |
| 24 s | 1068 | 1096 |
| 30 s | 1072 | 1100 |
| 36 s | 1066 | 1094 |
| 38,8 s | 1066 | 1094 |

Manter y estável. Suavizar entre os pontos, sem reagir a cada pequeno movimento da cabeça. Os pontos são direção visual; não são coordenadas de rastreamento automático medidas.

## Mudança de câmera

Única mudança no intervalo: **+38,800 s, ou 24:02.800 da fonte**, para a apresentadora.

- `boundary-01.jpg`: último frame dos convidados, 24:02.7667.
- `boundary-02.jpg`: primeiro frame da apresentadora, 24:02.8000.
- Confirmado por detecção de cena (`scene > 0.20`) e inspeção dos dois frames contíguos.
- De 24:02.800 a 24:11 o alvo fica fora da imagem. Para manter o foco visual nele, é necessário encerrar antes dessa troca ou usar insert/capa editorial conforme a narrativa e o áudio. Não se consegue revelar a câmera do alvo nesse intervalo apenas por crop.

## Limites e acabamento

- 720×1280 exige upscale 1,43× no plano principal e 1,60× no close. 1080×1920 exige 2,14× e 2,40× respectivamente; entrega Full HD pode servir para títulos/legendas nítidos, porém não recupera detalhe do rosto.
- Os braços e mãos do participante à esquerda invadem o canto inferior esquerdo em alguns momentos. Um gradiente discreto de rodapé reduz a distração; eliminar completamente exigiria um crop mais apertado, com perda de gestos e maior ampliação.
- Monitor verde e microfone permanecem no cenário. Ajustar saturação com moderação e evitar sharpening forte, pois a fonte já está comprimida (~1,9 Mbps de vídeo).
- Não aplicar crop principal após +38,8 s: enquadraria o fundo vazio do novo plano.

Análise local. Nenhum corte final, arquivo fonte ou CURRENT.md alterado nesta subtarefa.
