# Montagem da camisa branca — v11

Composição convencional das imagens existentes, conforme o pedido de executar aqui a montagem proposta. Não houve nova geração de imagem nesta versão.

- Base: o retrato colorido da v5 reenviado e preferido pelo usuário.
- Peça inserida: camisa branca da v9, com transição suave na gola e abertura do peito.
- Método: máscara desenhada, composição RGB com Node.js, Sharp e PNGJS, e saída PNG sem perdas.
- Saída: `../perfil-montagem-camisa-branca-2026-09-12-v11.png`, 1254 × 1254.
- Reprodução: `../perfil-montagem-v11.cjs`.
- Máscara: `mascara-camisa.png`.
- Verificação numérica: `verificacao.json`.

O arquivo PNG final foi reaberto e comparado à base. A região inteira acima de y=740, que contém todo o rosto e cabelo, tem zero pixels RGB alterados. A alteração total é de 5,5743% da imagem, localizada entre x=356..656 e y=742..1253. Fundo e rosto permanecem como na base; a transição da camisa inclui uma pequena área do pescoço e da jaqueta.

Composição e encaixe da gola inspecionados visualmente. A montagem preserva a textura já existente na base; não constitui uma recriação ou recuperação de detalhes faciais.
