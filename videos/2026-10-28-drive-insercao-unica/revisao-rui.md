# Revisão Rui — depuração do take

Data: 28/10/2026. Fonte: `tools/video-recut/videos/drive/ABAB5FBE-6150-48AE-AF90-DE7003E00CE1.mp4`, 43,366667 s.

## Parecer

Não encontrei evidência de frase refeita ou falso começo na comparação das transcrições locais base e small. A intervenção indicada é retirar o miolo das pausas e preservar todas as palavras, com respiro nas emendas.

- **Manter integralmente o gancho 0–3,86 s:** “Quanto mais você finge, menos você finge. É assim que funciona.” As duas ocorrências de “finge” são a ideia do gancho; não são tentativa repetida.
- **Manter “E é assim que funciona para todo o resto”, 27,28–29,40 s.** É uma transição de aplicação, não uma nova tentativa da frase inicial.
- **Manter as ocorrências seguintes de “finge/fingir”.** Desenvolvem a mesma tese; não há duas tomadas concorrentes da mesma frase.
- Não usar seleção automática de palavras por blocos VAD se ela descartar palavras cujo timestamp foi esticado sobre pausas. A montagem deve cortar intervalos físicos do áudio e remapear os eventos existentes.

## Pausas detectadas no áudio

Análise inicial: `silencedetect=noise=-33dB:d=0.30`. Critério final acordado com o montador: **-38 dB, duração mínima 0,32 s**, log `silence-safe.log`. Preservar 120 ms de cada lado da pausa, quantizar os pontos de corte para dentro do intervalo seguro em quadros de 30 fps e ignorar remoções menores que 120 ms. Não cortar silêncio inicial. Preservar a pausa dentro da pergunta dos atletas e 400 ms após a última fala. Valores em segundos do **bruto**, não da primeira montagem.

| Silêncio detectado | Núcleo sugerido para remoção | Observação |
|---|---|---|
| 0,000000–0,352676 | Manter | Proteger a primeira palavra |
| 2,704240–3,035941 | Manter | Núcleo quantizado menor que 120 ms |
| 3,842630–4,204626 | Manter | Núcleo quantizado menor que 120 ms |
| 11,283583–11,718277 | 11,433333–11,566667 | Antes da pergunta dos atletas |
| 12,322766–12,734649 | Manter | Não picotar a pergunta dos atletas |
| 17,166780–18,125805 | 17,300000–18,000000 | Pausa longa antes de “contando” |
| 19,980295–20,462948 | 20,133333–20,333333 | Antes de “e se você” |
| 22,273968–22,730499 | 22,400000–22,600000 | Antes de “uma hora dessas” |
| 26,011111–27,424989 | 26,133333–27,300000 | Pausa longa antes da aplicação |
| 29,377007–29,777052 | 29,500000–29,633333 | Antes de “você só precisa” |
| 30,732109–31,929615 | 30,866667–31,800000 | Pausa longa alinhada erroneamente dentro de “escolher” |
| 32,534059–33,144739 | 32,666667–33,000000 | Antes de “o que mais” |
| 35,998844–36,394490 | 36,133333–36,266667 | Trecho de comunicação |
| 38,895397–39,417234 | 39,033333–39,266667 | Antes do fecho “finge” |
| 41,131723–41,738050 | 41,266667–41,600000 | Antes de “e faça”; não perder essas palavras |
| 42,154354–43,373424 | 42,566667–43,366667 | Cauda, com 400 ms após a fala |

Os núcleos acima somam aproximadamente **5,40 s**, levando a um corte de aproximadamente **37,97 s**. A duração final deve ser a soma dos intervalos mantidos, com quantização por quadro a 30 fps. O ganho é menor que a limpeza automática agressiva, mas preserva as palavras e as pausas curtas da fala.

## Ponto crítico: “escolher”

O base alinhou “escolher” em 30,48–32,48 s; o small em 30,92–32,90 s. Rechecagem local adicional apenas de 29,4–35,6 s (faster-whisper small int8, sem upload ou arquivo intermediário) retornou 30,62–32,52 s. Os três reconhecimentos esticam a palavra sobre o silêncio físico de 30,718912–31,963469 s.

Isso não prova que existe fala no miolo dessa pausa. No critério final, cortar apenas 30,866667–31,800000 s, preservando todos os trechos audíveis dos dois lados, e **manter o evento “escolher”**, remapeando seu início e fim. Não excluir a palavra só porque o timestamp inicial caiu num intervalo removido. A montagem deve continuar dizendo “Você só precisa escolher o que mais você precisa fingir no momento”.

Para a legenda, associar “escolher” à retomada acústica por volta de 31,93–32,52 s e limitar o evento anterior “precisa” até cerca de 30,73 s é coerente com os três reconhecimentos e o silêncio medido. Esses limites corrigem alinhamento, não constituem confirmação por escuta humana; conferir a emenda na prévia. Preservar “o que” após a pausa seguinte, sem filtrar palavras por um timestamp isolado.

## Trechos pouco claros que não se resolvem apagando palavras

- 4,34–6,28 s: os reconhecimentos locais concordam em “Se você fingisse aquilo o tempo todo”. Não substituir por “fingir ser” sem escuta humana confirmada.
- 35,36–39,24 s: a fala reconhecida é “Comunicação, o que você precisa fingir ser o gênio de algo”. O enunciado é solto; não há retomada posterior que permita escolher uma versão melhor. Preservar a fala, usar pontuação discreta e não inventar palavras.
- A análise acima foi feita por transcrições e detecção acústica. Não representa escuta humana integral do material.

## Conferência da versão montada

1. Conferir especialmente as emendas de 12,3 s e 30,7–33,1 s do bruto para que “atletas”, “treinam”, “escolher” e “o que” permaneçam completos.
2. Manter a mesma foto única no topo e legenda branca; recalcular todos os tempos após os cortes.
3. Não usar hash de áudio idêntico ao bruto como critério da nova versão: a depuração autorizada altera o fluxo. Verificar sincronismo, continuidade e ausência de sílaba truncada nas emendas.

Sem render, alteração no exportador, story ou handoff por este agente. Fonte e primeira montagem preservadas. Nenhuma transmissão externa de mídia.
