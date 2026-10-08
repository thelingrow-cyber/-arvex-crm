# Montagem com gola clara — v12

Peça de malha clara com gola curta e zíper inspirada na referência t2, aplicada por composição convencional sobre a foto preferida pelo usuário.

- Imagem final: `../perfil-montagem-gola-clara-2026-09-12-v12.png`.
- Base do rosto e do restante do retrato: versão colorida v5 reenviada pelo usuário.
- Doadora da roupa: `doadora-gola.png`, gerada com a ferramenta nativa image_gen.
- Prompts e registro da seleção: `prompts-gola.txt`.
- Composição reproduzível: `../perfil-montagem-v12.cjs`.
- Máscara: `mascara-gola.png`; verificação: `verificacao.json`.

A máscara preserva a região completa acima de y=740. O PNG final foi reaberto e comparado: zero pixels RGB alterados nessa região, que contém rosto e cabelo, em relação à foto-base e à montagem v11. A alteração total é de 5,4957% da imagem e está restrita à peça interna, gola, transição do pescoço e pequena borda da jaqueta. O fundo permanece o da base.

Foi aplicado um acabamento convencional somente no painel de malha da doadora para suavizar a textura excessiva; a gola canelada e o zíper foram excluídos desse ajuste. O rosto não passou por esse processamento nem foi substituído pelo da doadora.

Saída: PNG colorido sem perdas, 1254 × 1254. Inspeção visual do retrato completo e do encaixe da gola concluída. A imagem preserva o acabamento facial da versão aprovada; não há alegação de eliminação de características já existentes nela.
