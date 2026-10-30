# Cliente: amigo do carro

**Status:** cliente desde 30/10/2026, o primeiro teste da ARVEX como empresa AI native (serviço entregue por software).
**Nome / @:** _pendente_. Pedir ao Vitor.
**Nicho:** SUVs grandes e picapes, com foco em lançamentos, híbridos e chineses (GWM, BYD/Denza) contra os "queridinhos" (SW4, H9, Hilux, Ranger, Amarok, S10, Defender).

## O que a ARVEX entrega

| Etapa | Quem faz | Base |
|---|---|---|
| Pauta (lançamentos, comparativos, polêmicas) | pauteiro | `pautas.md` + `referencias.md` |
| Roteiro de ~1 min na voz dele | roteirista | `voz.md` + `referencias.md` |
| Gravação | ele, no carro, com iPhone | — |
| Edição (clipes em cima, ele embaixo, headline vermelha) | editor-video | `molde/montar.py` |
| Entrega | Drive `Carros/Prontos` | — |

## Fluxo de arquivos

1. Ele sobe o bruto em **Drive → `Carros/Crus`**.
2. O Vitor manda o link da referência.
3. A ARVEX baixa (`rclone copy drive:Carros/Crus/<arquivo> ~/Downloads`), limpa (`tools/video-recut/limpar.cjs`), monta (cópia de `molde/montar.py` em `tools/video-recut/work/AAAA-MM-DD-amigo-<carro>/`) e entrega em **`Carros/Prontos/AAAA-MM-DD Modelo - tema.mp4`**.

Detalhes do molde:
- O bruto vem do iPhone em HDR. O `montar.py` já faz o tonemap; sem isso o rosto sai branco.
- Ele grava com legenda própria, que fica na faixa de baixo (crop `y=740`).
- Acervo de clipes já baixado:
  - `tools/video-recut/work/2026-10-29-amigo-carro/clipes`: Hilux nova, Ranger, Amarok, S10.
  - `tools/video-recut/work/2026-10-23-amigo-3/clipes`: Denza, Defender.
  - `tools/video-recut/videos/2026-10-amigo-carro-2/clipes`: Tank 400, H9, SW4, Pajero.
- Baixar só trechos curtos: `yt-dlp --download-sections`.

## Entregues

| Data | Vídeo | Referência |
|---|---|---|
| 16/10 | react (1º) | — |
| 17/10 | react Roadster | — |
| 22/10 | Tank 400 × SW4/H9 | Ronan `Dc7MgQRixax` |
| 23/10 | Denza B5 × Defender | Ronan `DexrQ-zicTh` |
| 29/10 | Hilux 2027 "já nasceu velha?" | Ronan `DdXN8QFCS1C` |

## Pendências para virar cliente de verdade

- [ ] Nome e @ dele, e acesso às métricas do Instagram (prova do teste).
- [ ] Combinar o escopo: quantos vídeos por semana e se ele quer pauta e roteiro ou só edição.
- [ ] Preço, mesmo que de amigo. A tese só fica provada se ele pagar pelo resultado mais de uma vez.
- [ ] Linha de base: seguidores e views médias **antes** da ARVEX, para medir depois.
