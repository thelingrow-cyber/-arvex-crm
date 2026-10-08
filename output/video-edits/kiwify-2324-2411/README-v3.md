# V3 — cortes reais na fala, cenas de apoio e flashes visíveis

Feedback: a V2 não correspondeu ao pedido de inserts de cenas; seus flashes eram
fracos e a fala continuava repetitiva. Esta revisão altera efetivamente a montagem.

- Começa em “O expert hoje não é só mais um especialista...”. Retira toda a introdução
  sobre infoproduto/marca pessoal e duas retomadas de “pode ser explorado”.
- Seis blocos: 11,300–14,467; 14,467–16,867; 17,933–21,100;
  22,133–24,567; 24,933–29,033; 29,767–32,733 (relativos ao bruto de47s).
- 17,133s após velocidade moderada1,04–1,10×. Sem CTA e sem congelamento.
- Cenas filmadas de programação5,22–6,78s e colaboração8,717–10,467s. Não são
  telas do usuário nem prova de trabalho/clientes; rotuladas “CENA ILUSTRATIVA”.
- Card aprovado “Novas possibilidades / IA + tecnologia” mantido sobre o rosto.
- Flashes isolados em3,033s,5,22s e10,467s: pico claro88%, decaimento quente48%/19%,
  janela~0,27s. Aplicados sobre cenas/rosto, não disfarçados sobre cartões brancos.
- Música “Close Up”, Michael Ramir C./Mixkit, mesma mixagem discreta da V2.

Fontes das cenas, com Mixkit Stock Video Free License indicada para uso comercial/pessoal:

- https://mixkit.co/free-stock-video/programmer-working-with-codes-on-a-computer-41637/
- https://mixkit.co/free-stock-video/team-collaboration-in-a-colorful-workspace-100319/

Arquivos Full HD obtidos pelos downloads oficiais de cada página. Sem compra/publicação.
O primeiro mostra desenvolvimento genérico, não uma demonstração comprovada de geração
por IA. Legendas reconstituídas diretamente do ASR e dos novos cortes; conferência humana
das junções de fala continua pendente. Não alegar revisão auditiva realizada.

Reproduzir: `node build-v3.cjs --render`. Conferir: `node check-v3.cjs`.
`-n` preserva exportações existentes. V1/V2 e fonte continuam intactas.
Resultados em `validation-v3.json`; amostras de rosto, cenas e flashes em `qa-v3.jpg`.
Gates do projeto: lint/typecheck/build ausentes; teste de handoff mantém a falha
preexistente de títulos. Nenhuma alteração em package.json ou no produto.
