# Kiwify — revisão V7, casos de autoridade

V7 preserva a montagem, tratamento de imagem, áudio e duração de 21,067s da V6.
O antigo insert único de 1,65s foi substituído por dois casos identificados, totalizando
2,67s: Manu Cit × Guday e MrBeast × Feastables. A fala não foi alterada.

## Sequência

- 12,967–14,267s: Manu Cit × Guday.
- 14,267s: flash quente de transição.
- 14,297–15,667s: MrBeast × Feastables; rosto, barra e fechamento no produto.
- 15,987s: motion do funil, preservado.

O enquadramento do comercial exclui a legenda inglesa grande da fonte. Os identificadores
usam a mesma linguagem preto/dourado da edição; não há rótulo de “cena ilustrativa”.

## Fontes

- Guday, página oficial da fundadora: https://guday.com.br/pages/historia
- MrBeast 2, comercial oficial Feastables: https://www.youtube.com/watch?v=jaRfBM7ESfc
- Relação MrBeast/Feastables confirmada pela própria marca: https://feastables.com/

As fontes são públicas, mas não apresentam licença de reutilização. Crédito/identificação
não substitui autorização; confirmar direitos antes de publicação comercial. O áudio original
dos casos não é utilizado e não é sugerida parceria ou endosso.

## Validação

```powershell
node output/video-edits/kiwify-2324-2411/v7-assets/prepare-cases.cjs
node output/video-edits/kiwify-2324-2411/build-v5.cjs --v7 --render
node output/video-edits/kiwify-2324-2411/check-v3.cjs --v7
```

Decodificação completa, metadados, loudness, contact sheet e dois quadros integrais
conferidos. Arquivos auxiliares: `v7-assets/`, captions, filtro, args, manifesto,
`validation-v7.json` e `qa-v7.jpg`. Versões anteriores preservadas.
