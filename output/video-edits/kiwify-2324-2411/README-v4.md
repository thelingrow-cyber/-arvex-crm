# V4 — abertura sobre criar um ecossistema restaurada

Pedido: voltar ao mesmo início das primeiras versões porque a fala sobre criar um
ecossistema precisa permanecer. Restaurado o bruto1,133–8,567s: começa em “vou fazer
conteúdo...” e inclui “vou criar um ecossistema dentro da minha marca”. Mantém palavras
completas segundo ASR; retira apenas a explicação repetida “que é a minha marca pessoal”.
Depois continua a V3 enxuta, sem as retomadas de “pode ser explorado”.

Duração prevista23,900s. Cenas filmadas, card aprovado, música e flashes da V3 mantidos,
com tempos remapeados. Hook inicial volta a “Sua marca vai além do infoproduto”.
Sem CTA; nenhuma alteração nos MP4s anteriores. Licenças das cenas/música: README-v3.md.

Reproduzir: `node build-v3.cjs --v4 --render`.
Conferir: `node check-v3.cjs --v4`.
O modo padrão desses scripts continua sendo V3; a opção `--v4` gera só arquivos V4.
Sem sobrescrever vídeos existentes (`-n`). Novos overlays em `v4-assets/`; cenas V3
reutilizadas sem duplicação. Metadados/cortes: `edit-manifest-v4.json`.
Resultados: `validation-v4.json`, `qa-v4.jpg`. Conferência auditiva humana ainda pendente.
