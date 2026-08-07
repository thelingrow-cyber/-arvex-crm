-- ============================================================================
-- Cérebro do coach — bloco novo a partir do caso-07 (Ótica Vivalle, Londrina).
-- Erro estrutural que ainda não estava mapeado: apresentar preço para quem
-- avisou que não decide. Inclui também o tratamento de âncora de preço externa.
-- ============================================================================

insert into sales_knowledge (tipo, titulo, conteudo, fonte, tags, peso) values

('metodo', 'Se o lead nomeia outro decisor, a call vira agendamento — não apresentação',
$$Registrado em call real com resultado negativo. A dona de uma ótica de 13 anos avisou ANTES de qualquer
número: "até antes de você falar de valor comigo — porque tudo que a gente vai fazer é a minha filha. Ela
vai em primeiro lugar antes de mim, ela precisa vestir essa camisa. Antes da gente falar de valor, fechar,
falar qualquer coisa, eu vou trocar uma ideia com ela para ela conversar com você, porque ela precisa te
ouvir." O closer respondeu "tá ok, mas o que eu vou propor aqui..." e apresentou o preço assim mesmo.

POR QUE ISSO QUEIMA A VENDA:
- O preço é recusado por quem não decide, e chega ao decisor real já recusado e já descontado duas vezes.
- A negociação com o decisor começa do pior ponto possível: sem ter ouvido o valor, só o número.
- Neste caso a filha JÁ tinha falado com a equipe 2-3 meses antes — havia histórico que ninguém consultou,
  e a mãe percebeu a incoerência: "quando ela tava conversando com a pessoa, não era esse valor".

O MOVIMENTO CERTO: "perfeito, então o valor eu apresento com vocês duas juntas — quando ela pode?" A call
vira diagnóstico + agendamento. Vale a mesma regra quando aparece sócio, esposo, irmã ou mãe: no nicho
óptico NUNCA existe decisor solitário (aparece em 3 de 3 fontes do ICP).

REGRA DE JULGAMENTO: se o lead nomeou outro decisor e o closer apresentou preço assim mesmo, isso é ERRO
ESTRATÉGICO — não erro de fechamento. Perguntar "quem decide" no começo da call é requisito, não cortesia.

ÂNCORA DE PREÇO EXTERNA (mesma call): "a TV local mais forte da cidade está com campanha por 1.200 no mês,
30 dias, três inserções". E ela dividiu a oferta sozinha, em voz alta: "4.997 dividido por quatro meses dá
1.249 por mês, mais as campanhas... fugiu, e muito". Quando o lead compara CUSTO com CUSTO, a resposta é
comparar RETORNO com RETORNO: 13 anos de carteira própria (ativo que ele já pagou para construir) contra
30 dias de atenção alugada. Sem esse contraste, o anúncio barato continua parecendo o melhor negócio —
e responder só "é outra linha, não é só um anúncio" não desmonta a âncora.$$,
 'docs/crm/sales-coach/conhecimento/casos/caso-07-vivalle-londrina.md',
 array['metodo','decisor','ancora','preco'], 5)

on conflict do nothing;
