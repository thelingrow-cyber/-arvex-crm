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

## Vários takes + áudio separado (montagem, sem `prep.ps1`)

Quando o áudio é uma narração à parte e os takes são B-roll (ex.: `videos/2026-09-boas-vindas/`):

1. **Áudio:** cortar repetições com `atrim`+`concat` (crossfade de 0,2 s), `loudnorm=I=-16`.
   Trilha grátis gerada aqui: 4 acordes de `sine` (2 sines por nota, desafinadas ~0,35 Hz), `volume=0.14`,
   `acrossfade` entre acordes, `lowpass=2600`+`aecho`, loop com `-stream_loop`. Mixar com **ducking**:
   `sidechaincompress=threshold=0.04:ratio=6:attack=15:release=420` (voz na chain) + `alimiter`.
2. **Transcrever o áudio já editado** (Groq, igual ao prep) → `agrupar.cjs` → `legenda.json`.
3. **Takes:** `ffmpeg -ss X -i take.MOV -t D -an -vf "fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,<cor>"`
   com GOP 30, um arquivo por corte; depois `-f concat` + `-map 1:a` do áudio final → `public/input-video.mp4`.
   ⚠️ A lista do concat precisa ser **UTF-8 sem BOM** (`[IO.File]::WriteAllText`) — `Out-File -Encoding ascii` quebra caminho com acento.
4. Seguir daí igual: `build.cjs` → `render.ps1`.

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
| `legendaDinamica(groups, {destaques})` | Cada palavra entra quando é falada; 4 entradas alternadas (pop / giro 3D / deslize / impacto), linha inclinada, palavras de `destaques` maiores com brilho e sublinhado dourado |
| `flash(times)` | Flash curto de luz no corte (impacto sem SFX) |
| `insertCiclo({start, end, kicker, ate, zeroAt, rodape})` | Pessoa no círculo, anel enche com contador DIA 1→N e volta a zero (vermelho, alarme, tremida) |
| `insertEtapas({start, end, kicker, etapas:[[texto, t]]})` | Círculo menor no rosto + 3 etapas em fila que acendem em dourado no tempo falado |
| `insertTitulo({start, end, kicker, linhas:[[texto, t]]})` | Título em tela cheia com raios girando; linhas batem uma a uma, última dourada com estouro de partículas e zoom-through na saída |
| `cardContraste(id, ini, fim, {k1, t1, riscoAt, virarAt, k2, t2, t2At})` | "NÃO É SOBRE X" risca em vermelho → vira em 3D → "É SOBRE Y" dourado |
| `shake(times, {forca, alvo})` · `filtro(ini, fim)` | Tremida de câmera no impacto · dessaturar/escurecer o vídeo num trecho |

Cards (todos) entram tombando em 3D e "respiram" enquanto estão na tela (desde 2026-09-18).
**Jump cut + trilha/SFX:** ver `videos/2026-09-cindy-captacao-desafio/` — `cortar.cjs` (pausas via `silencedetect`, porque o Groq estica o fim das palavras)
e `build.cjs --mix` (trilha Am–F–C–G + kick gerada, whoosh/hit/riser, ducking) roda depois do render.
⚠️ No PowerShell 5.1, os `.ps1` precisam estar em UTF-8 **com BOM** (sem BOM os acentos quebram o parse).

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

## Modo camadas — fundo atrás da pessoa (sem HyperFrames)

Aprovado e postado em 2026-09-19 (`videos/2026-09-plano-vs-prova/`, referência @bitterbuilds). Edição "limpa":
talking-head + **faixa de cenas rolando de lado atrás da pessoa, 50% transparente** + B-roll literal em tela cheia +
card pequeno com foto + legenda branca simples. Python + ffmpeg + PIL; recorte com torchvision (pesos oficiais do PyTorch).

```powershell
# 1. criar videos\<nome>\camadas.json (copiar o do plano-vs-prova e trocar arquivos/tempos)
# 2. rodar tudo (transcrever → recorte → fundo → card → legenda → compor → previa)
python tools\video-recut\camadas\camadas.py 2026-10-meu-video
# refazer só uma parte (transcrição e recorte ficam em cache em work\<nome>\)
python tools\video-recut\camadas\camadas.py 2026-10-meu-video legenda compor previa
```

| Chave do `camadas.json` | O que faz |
|---|---|
| `principal`, `saida`, `pasta` | vídeo falado; saída e busca de arquivos em `pasta` (padrão Downloads), depois `videos\<nome>\` e `work\<nome>\` |
| `cor` | filtro ffmpeg no vídeo principal (padrão aprovado = menos luz: `curves` descendo realces) |
| `transcricao.prompt/remover/trocar` | vocabulário p/ o Whisper; palavras a tirar ou trocar na legenda |
| `fundo.inicio/fim/opacidade/cenas` | janela do fundo (s), transparência e as cenas `[arquivo, início, duração do loop]` |
| `apoio` | cenas em tela cheia `[arquivo, início no arquivo, entra em, duração, filtro extra]` |
| `card` | foto + nome, entra/sai (s), `y`, `escala` — pequeno, NUNCA tela cheia (pedido do Vitor) |
| `musica` | `null` = sem trilha (padrão: o Vitor põe a música no app) |

**Custos e pegadinhas (todas já resolvidas no código):**
- Recorte ≈ **1 quadro/s** → só o trecho do fundo é recortado (~9 s de vídeo = ~5 min). Borda do cabelo sai suave; com o fundo semitransparente não aparece.
- **RAM 6 GB:** o blend em `gbrp` do vídeo inteiro foi morto por falta de memória → só o trecho do fundo passa por ele, com `-threads 2`. Fechar Chrome/ChatGPT antes.
- **`blend` com `T` retorna NaN** nesta build do ffmpeg → a transparência usa `N/30`.
- RobustVideoMatting (`torch.hub`) recorta melhor, mas executa código baixado → bloqueado pelo classificador. Não tentar de novo.
- Fundo some quando entra a cena de apoio seguinte: na volta à tela grande fica só a pessoa (pedido do Vitor).

## Economia de tokens (para o agente)

Não reler as SKILL.md do HyperFrames (este README cobre o necessário). Não fazer versão "simples" antes: ir direto no nível
do exemplo, **1 rodada de prévia (`-Previa`) + 1 render**. Custo alvo: ~30–40k tokens por vídeo.

## Ideias para evoluir (backlog)

- Novos inserts: comparação antes/depois, contador (count-up), citação/depoimento em tipografia, mapa, lista em cascata.
- Trilha e whoosh nos cortes (SFX livre de direitos) — mixagem via `/hyperframes-audio`.
- Cortar silêncios automaticamente (jump cut) a partir dos timestamps de palavra.
- Presets de marca por cliente (`estilo-<marca>.css`).
