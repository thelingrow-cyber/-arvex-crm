-- ============================================================================
-- Cérebro do coach — o que separa a call que FECHA das que não fecham.
-- Base: 4 calls reais (1 ganha, 1 perdida, 2 em aberto). Substitui a leitura
-- anterior, que só tinha derrota e por isso só sabia descrever fracasso.
-- ============================================================================

insert into sales_knowledge (tipo, titulo, conteudo, fonte, tags, peso) values

('metodo', 'O que a call que FECHOU fez de diferente (4 calls comparadas)',
$$Em 4 calls transcritas — 1 ganha, 1 perdida, 2 em aberto — cinco diferenças separam a que fechou:

1. O CLOSER FALOU MENOS E O LEAD FORMULOU O ARGUMENTO. Na call ganha o lead disse sozinho: "a pessoa que
   vai fazer a campanha tem que trabalhar naquele segmento específico… se trabalha com vários nichos vira
   um profissional genérico, e aí é o problema, não é verdade?". Nas calls perdidas esse mesmo argumento
   é ENTREGUE pelo closer. Argumento que sai da boca do lead não gera objeção. Ao julgar a call, verifique
   quem formulou os argumentos-chave — se foi sempre o closer, ele apresentou; não vendeu.

2. A PERGUNTA DA BASE FOI ATÉ O FIM. Sequência completa na call ganha: "quantos anos tem a loja?" →
   "e você tem o número desses clientes, em algum sistema?" → "bom demais, é isso que a gente vai usar" →
   nome do mecanismo ("campanha de saque rápido"). Nas duas calls em aberto a pergunta foi feita pela
   metade (uma delas o lead nem ouviu, e o closer não retomou) — e o maior argumento da oferta morreu ali.

3. PROVA SOCIAL DO MESMO PORTE, DE PREFERÊNCIA RECONHECIDA PELO LEAD. Na ganha, o lead citou a aluna
   sozinho: "ela começou com 15 mil, passou pra 35, 50, 70 — o faturamento dela era próximo do meu".
   Caso de porte igual converte; aluno-estrela de R$143 mil não.

4. QUANDO A TRAVA É CAIXA, MEXER NO CALENDÁRIO — NUNCA NO PREÇO. Call ganha: preço mantido em R$2.500,
   dividido como "R$1.000 na quarta para dar o start + R$1.500 na quarta seguinte", com a 1ª parcela
   amarrada ao início da execução. O lead fechou a própria proposta em voz alta. Call em aberto (mesmo
   tipo de trava): o preço caiu QUATRO vezes (4.997 → 12×516 → 4.500 → entrada 2.500 → sinal 100) e não
   fechou, porque o problema era limite de cartão, e desconto não cria limite de cartão. Diagnostique
   antes de mexer no preço: falta de VALOR PERCEBIDO x falta de MEIO DE PAGAMENTO são coisas diferentes.

5. NÃO HOUVE PEDIDO DE SINAL SIMBÓLICO. O sinal ("R$100 pra segurar a condição", "um valor simbólico pra
   reservar a vaga") aparece em 3 calls, com 2 closers diferentes, e em NENHUMA delas houve fechamento.
   Na única que fechou não foi usado — no lugar dele: valor real, data real e agenda marcada com a
   consultora. Trate o pedido de sinal simbólico como ERRO DE FECHAMENTO até prova em contrário: ele
   substitui o "sim" grande por um "sim" pequeno e sinaliza que o preço era inflado.

OBSERVAÇÃO DE FUNIL: a call que fechou foi com quem JÁ tinha comprado o produto de entrada (R$297 +
Restart Óptico ≈ R$2.800) e já acompanhava a mentora. É o mesmo mecanismo que a casa vende às óticas —
vender para a base é mais fácil que captar frio.$$,
 'docs/crm/sales-coach/conhecimento/casos/caso-06-wal-leite-GANHA.md (comparativo das 4 calls)',
 array['metodo','fechamento','call-ganha','pagamento'], 5)

on conflict do nothing;
