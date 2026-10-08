# Montagem v14 — casaco aberto e gola cinza aberta

Entrega: [PNG final em cores, 1254 × 1254](../perfil-montagem-sueter-aberto-2026-09-12-v14.png).

O casaco preto da base aprovada permanece aberto. A peça interna tem gola erguida e aberta, inspirada na referência t2, tecido cinza discreto e pequena faixa da camiseta branca visível.

## Método

1. Doadora de roupa criada com a ferramenta nativa `image_gen`, usando a base aprovada e a t2 como referência de vestuário.
2. Refinamento somente do recorte da roupa para substituir o padrão ornamental por tecido simples. O ensaio de refino do retrato inteiro não foi selecionado.
3. Montagem convencional com máscara localizada sobre o PNG aprovado. Nenhum filtro, redimensionamento, ajuste de cor ou geração foi aplicado ao rosto da base. Apenas o recorte do tecido doador foi reduzido às dimensões necessárias.
4. Máscara refinada junto à gola e ao pescoço, mantendo a estrutura e a abertura originais do casaco.

[Prompts completos](prompts.txt) · [Script de montagem](../perfil-montagem-v14.cjs) · [Verificação numérica](verificacao.json).

## Verificação

PNG final reaberto e comparado em RGB: zero pixels diferentes na região protegida de rosto, cabelo e orelhas (793.660 pixels), contra a referência aprovada e contra a montagem v11. Alterações localizadas em 5,0786% da imagem, na roupa e transição do pescoço. Retrato completo e encaixe da gola inspecionados visualmente.

A preservação dos pixels mantém o acabamento existente da referência; não é uma afirmação de que toda percepção de imagem sintética foi eliminada. Versões anteriores mantidas, sem publicação ou commit.
