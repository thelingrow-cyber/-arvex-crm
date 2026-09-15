# video-recut — edição de Reels com motion (grátis)

Pega um vídeo de celular (talking-head) e entrega um Reels 9:16 com corte, tratamento de cor, zoom de câmera,
legenda palavra a palavra, cards animados e inserts de motion graphics.

**Stack (tudo grátis):** ffmpeg · [HyperFrames](https://github.com/heygen-com/hyperframes) (HTML → MP4, headless Chrome) · Groq Whisper (transcrição, plano free, chave `GROQ_API_KEY` do WhisperFlow) · GSAP.

**Instalação em máquina nova:** `winget install Gyan.FFmpeg` · Node 22+ · Chrome · `npx skills experimental_install` na raiz do repo
(restaura as skills do HyperFrames a partir do `skills-lock.json`; a pasta `.claude/skills/` não é versionada, 19 MB de terceiros).

Primeiro vídeo feito com isto: `videos/2026-09-convite-cindy-100k/` (convite Desafio Ótica +100K, aprovado na v2).

## Fluxo (3 comandos)

```powershell
# 1. Preparar: corte + cor + transcrição + legenda agrupada + folha de contato
.\tools\video-recut\prep.ps1 -Video "C:\Users\...\Downloads\IMG_1234.MOV" -Nome "2026-10-meu-video" -Inicio 2.5 -Fim 48

# 2. Montar conteúdo: copiar o modelo e declarar câmera, cards, inserts
mkdir tools\video-recut\videos\2026-10-meu-video
copy tools\video-recut\videos\_modelo\build.cjs tools\video-recut\videos\2026-10-meu-video\
#   → corrigir work\2026-10-meu-video\legenda.json se a transcrição errou algo

# 3. Conferir em frames (segundos) e renderizar (~8 min por 43 s nesta máquina)
.\tools\video-recut\render.ps1 -Nome "2026-10-meu-video" -Previa -Em "3,8,15,30"
.\tools\video-recut\render.ps1 -Nome "2026-10-meu-video"          # final vai para Downloads\<nome>.mp4
```

Para achar o `-Inicio`/`-Fim` (tirar take errado): rode o prep sem eles, leia a transcrição e rode de novo com o corte.

## Peças disponíveis (`lib.cjs`)

| Função | O que faz |
|---|---|
| `camera([[ini, fim, s0, s1], …])` | Push lento de `s0`→`s1`; mudar `s0` entre segmentos = corte com zoom (usar nas ênfases) |
| `cardTitulo(id, ini, fim, {kicker, titulo, gold, tituloAt, goldAt})` | Painel navy no topo, abre do centro, texto sobe por máscara, brilho dourado na palavra `gold` |
| `cardLista(id, ini, fim, {kicker, itens:[[texto, t]], extra})` | Itens trocam no tempo em que são falados + contador + barra de progresso |
| `cardCTA(id, ini, {kicker, texto, popAt})` | Botão verde com pulso, brilho e seta até o fim do vídeo |
| `insertCirculo({start, end, kicker, blocos, rodape, selo, faceX, faceY})` | Tela navy, pessoa num círculo com anel dourado, blocos virando em 3D (datas/números curtos) |
| `insertCrescimento({start, end, kicker, selo, seloAt})` | Gráfico de barras douradas + linha desenhada + selo com brilho |
| `legenda(groups)` | Legenda Inter 900 com contorno, palavra falada em dourado com "pulo" |

Estilo em `estilo.css` (sistema visual Cindy: Inter 900, navy `#14172E`, dourado `#C9963F/#DDB870`, CTA `#25D366`).
Para outro cliente/marca: trocar as cores em `:root` e nos gradientes.

## Layout 9:16 validado

- Cards no topo: `top: 130px` (acima da cabeça). Legenda: faixa `y 1210–1450` (peito), fora da UI do Instagram (rodapé > 1600, botões à direita).
- Rosto de quem fala ~ `y 380–800`. Se o enquadramento for diferente, olhar `work\<nome>\contato.jpg` e ajustar `faceX/faceY` do insert círculo.

## Regras que já custaram retrabalho

- **Vídeo de entrada precisa GOP 30** (o prep já faz). GOP esparso congela o quadro no render.
- **Não setar `visibility` em elementos `.clip`** (lint bloqueia) — o HyperFrames controla pelo `data-start/data-duration`.
- **Estado inicial explícito:** toda animação que começa depois do início do bloco usa `immediateRender:false` + `tl.set` no início (senão pisca antes de animar).
- **Não usar `transform` no CSS de elementos que o GSAP anima com `xPercent/yPercent`** — soma deslocamento em dobro.
- **Render de agente:** comandos morrem em 10 min; o render leva ~8. Agente usa `render.ps1 -NaoEsperar` e acompanha `work\<nome>\render.log`.
- **Disco:** render precisa ~1 GB livre; o prep aborta abaixo de 1,5 GB.
- **Número de faturamento** em card só como prova de terceiros (regra de lançamento). Nome de evento com número ("+100K") pode.
- **Prints/fotos de baixa qualidade não entram como insert** — preferir motion criado.
- **`embedded-captions` (legenda atrás da pessoa) é inviável aqui** — gera GBs de frames e horas de CPU (Ryzen 3500U, 6 GB RAM).

## Economia de tokens (para o agente)

Não reler as SKILL.md do HyperFrames (este README cobre o necessário). Não fazer versão "simples" antes: ir direto no nível
do exemplo, **1 rodada de prévia (`-Previa`) + 1 render**. Custo alvo: ~30–40k tokens por vídeo.

## Ideias para evoluir (backlog)

- Novos inserts: comparação antes/depois, contador (count-up), citação/depoimento em tipografia, mapa, lista em cascata.
- Trilha e whoosh nos cortes (SFX livre de direitos) — mixagem via `/hyperframes-audio`.
- Cortar silêncios automaticamente (jump cut) a partir dos timestamps de palavra.
- Presets de marca por cliente (`estilo-<marca>.css`).
