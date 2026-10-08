# Story — AA Multimarcas | Dia do Cliente

## Objetivo

Criar uma arte vertical de Dia do Cliente para a AA Multimarcas, usando a publicação da Omega apenas como referência de categoria e superando-a em acabamento, hierarquia, concisão e fidelidade de marca.

## Critérios de aceite

- [x] Entrega em 1080 × 1920 px, proporção 9:16.
- [x] Fotografia automotiva premium, autoral e sem marca de fabricante identificável.
- [x] Identidade dominante em preto, grafite, prata e champagne discreto.
- [x] Nenhum elemento de interface do screenshot de referência.
- [x] Logo AA derivado do arquivo fornecido e aplicado após a geração da fotografia.
- [x] Headline e copy em português revisadas e legíveis em tela móvel.
- [x] Conteúdo essencial dentro da zona segura de Story.
- [x] Arquivo final reaberto e inspecionado visualmente.
- [x] Metadados de resolução e formato registrados.

## Copy aprovada para a execução

> Confiança não se anuncia. Se conquista.
>
> Obrigado por escolher a AA Multimarcas para comprar, vender ou financiar com segurança e transparência. É a sua confiança que move cada negócio.

## File list

- `output/aa-multimarcas-dia-cliente/aa-dia-do-cliente-story.png`
- `output/aa-multimarcas-dia-cliente/aa-dia-do-cliente-preview.png`
- `output/aa-multimarcas-dia-cliente/build-art.cjs`
- `output/aa-multimarcas-dia-cliente/final-prompt.txt`
- `output/aa-multimarcas-dia-cliente/README.md`
- `output/aa-multimarcas-dia-cliente/validation.json`
- `output/aa-multimarcas-dia-cliente/assets/showroom-key-base.png`
- `output/aa-multimarcas-dia-cliente/assets/aa-logo-reference.jpg`
- `output/aa-multimarcas-dia-cliente/assets/aa-logo-white.png`

## Validação

- PNG reaberto: 1080 × 1920, sRGB, opaco.
- Inspeção visual em resolução integral concluída.
- Logo, data, acentuação, copy, carro, chave, reflexos e margens conferidos.
- `node --check output/aa-multimarcas-dia-cliente/build-art.cjs` passou.
- `npm run lint` e `npm run typecheck` não existem no projeto; `npm test` mantém a falha preexistente do contrato de seções de `CURRENT.md`.
- Sem publicação, commit ou alteração do arquivo original em Downloads.
