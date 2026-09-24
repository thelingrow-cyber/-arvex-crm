# task: montar-receita

**Agente:** editor-video · **Entrada:** take gravado + roteiro · **Saída:** `Downloads\<nome>.mp4` + folha de contato

## Passos

1. Transcrever o take e comparar com o roteiro — o falado nem sempre é o escrito.
2. Criar `tools/video-recut/videos/<nome>/camadas.json` com os tempos do vídeo **original** (o corte seco remapeia sozinho).
3. Gerar as artes necessárias (`gerar-artes.py`) — sempre originais.
4. Checar a RAM livre. Abaixo de 1 GB o render é morto; pedir para fechar o navegador.
5. Renderizar: `python tools\video-recut\camadas\camadas.py <nome>`
6. Conferir a folha de contato antes de entregar.

## Padrão da casa

- **Tese:** take único, legenda branca pequena, sem trilha, sem CTA, no máximo uma inserção, nada nos primeiros 12s.
- **Com dado:** card no topo acima da cabeça, trocando a cada 3 a 5 segundos; fonte no rodapé quando cita terceiro.
- **Nunca:** material de terceiro, música não livre, card com fonte em cima de número que não confere.

## Falhas conhecidas

- `blend` com `T` retorna NaN nesta build do ffmpeg — usar `N/30`.
- Card grande demais encosta no cabelo; card pequeno demais não se lê no celular (mínimo ~760 de largura).