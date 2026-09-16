# Garfield no jornal — v1 (16/09/2026)

Edição **só com ffmpeg** (sem HyperFrames), no estilo da referência `@bitterbuilds` (ficha em
`docs/conteudo/banco-roteiros/referencias/ref-bitterbuilds-garfield-jornal.md`). Render ~1 min.

- **Take:** `Downloads/5FD8F678-0402-41F4-AC09-6D244AA1E0F2.mp4` (50,4s) → corte 39,30–44,98 ("ferramentas e AI e tudo") → 44,8s
- **Inserção 1 (0–3,93s):** `Downloads/pincus-citacao-com-audio.mp4` (Lenny's Podcast 51:25) acelerado 1,1286×, 580px, y=1290, voz dele a 14% sob a sua
- **Inserção 2 (25,90–27,84s):** caneca + camiseta recortadas do quadro 17,6s da referência, 270px de altura, y=1330
- **Legenda:** ASS gerado por `legenda-ass.cjs` — Segoe UI Bold 62, branca, sombra leve, `\pos(540,1330)` (1275 durante a inserção 2)
- **Trilha:** `fallen-asper-565.mp3` (Mixkit) a 0,16 com sidechain da voz · `loudnorm -16`

⚠️ **Legenda ASS no ffmpeg do winget precisa de `FONTCONFIG_FILE`** apontando para um `fonts.conf` com
`<dir>C:/Windows/Fonts</dir>` — sem isso o ffmpeg dá segfault (drawtext e subtitles).
⚠️ Não gerar o `.ass` por heredoc no Git Bash: as barras invertidas (`\N`, `\pos`) somem. Usar arquivo `.cjs`.
