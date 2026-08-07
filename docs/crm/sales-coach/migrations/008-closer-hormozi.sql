-- ============================================================================
-- Cérebro do coach — framework CLOSER (Hormozi) + curadoria para caber no teto.
--
-- SAI: "Se o lead nomeia outro decisor..." (2.060) — absorvido pelo novo bloco
--      (a etapa E do CLOSER trata decisor com um reframe melhor: é APOIO, não
--      permissão). A âncora de preço externa, que era a outra metade daquele
--      bloco, migra para o bloco de objeções.
-- ENCOLHE: "Equação de valor (Hormozi)" 1.585 → ~1.000, sem o que o SPIN já cobre.
-- ENTRA: CLOSER — as 6 etapas + a taxonomia das 5 objeções + o pós-fechamento.
-- ============================================================================

update sales_knowledge set ativo = false, updated_at = now()
 where titulo = 'Se o lead nomeia outro decisor, a call vira agendamento — não apresentação';

update sales_knowledge set ativo = false, updated_at = now()
 where titulo = 'Equação de valor aplicada à call (Hormozi, $100M Offers)';

update sales_knowledge
   set conteudo = conteudo || $$

ÂNCORA DE PREÇO EXTERNA (registrado em call real): a lead comparou a oferta com "a TV local mais forte da
cidade está com campanha por R$1.200 no mês, 30 dias, três inserções" — e dividiu a nossa sozinha em voz
alta: "4.997 por quatro meses dá 1.249 por mês, mais as campanhas... fugiu, e muito". Quando o lead compara
CUSTO com CUSTO, responder "é outra linha, não é só um anúncio" não desmonta nada. A resposta é comparar
RETORNO com RETORNO: X anos de carteira própria (ativo que ele já pagou para construir) contra 30 dias de
atenção alugada.$$,
       updated_at = now()
 where titulo = 'Objeções do dono de ótica — reais, cortinas e como tratar';

insert into sales_knowledge (tipo, titulo, conteudo, fonte, tags, peso) values

('metodo', 'CLOSER (Hormozi) — as 6 etapas e a taxonomia das 5 objeções',
$$C — CLARIFY. Comece pelo motivo declarado: "o que te fez responder / marcar essa call?". Você só
conversa com quem levantou a mão, então o motivo existe — e é munição para o resto da call. Nas nossas
calls essa pergunta não aparece: começamos por "como estão as vendas?" em vez de "o que te trouxe aqui?".

L — LABEL. Rotule o problema em voz alta e peça confirmação: "então o que eu tô ouvindo é que [problema].
É isso?". É a escuta ativa em forma de diagnóstico — e cada "é isso" é um micro compromisso.

O — OVERVIEW das tentativas passadas. Não é UMA pergunta, é um CICLO, repetido: "o que você já tentou?"
→ "como funcionou?" → "o que foi bom nisso?" → "o que foi ruim?" → "e o que mais você já fez?". A cada
volta, amarre ao que a sua solução resolve. O objetivo declarado é aumentar a PRIORIDADE do problema no
curto prazo. Aqui é onde a cicatriz de mentoria anterior aparece — e onde ela deixa de ser objeção e
vira argumento.

S — SELL THE VACATION, não o voo. Venda o destino (como fica quando o problema está resolvido), não o
método para chegar lá. Regras duras: (a) NO MÁXIMO 3 pontos, cada um com uma anedota curta de cliente
real — nunca a lista completa de entregáveis; (b) o pitch inteiro em MENOS DE ~320 PALAVRAS. Se o
diagnóstico foi bem feito, o pitch é fácil e curto: "então você tá travado em A, B e C; resolvendo A
destrava isso, resolvendo B destrava aquilo. É isso mesmo? Então a gente consegue te ajudar."
→ CRITÉRIO VERIFICÁVEL: conte as palavras do bloco de apresentação. Nas nossas calls ele passa de 2.000.

E — EXPLAIN AWAY. Só existem 5 objeções, e todas são erro de raciocínio, não fato:
· TEMPO ("tenho muita coisa agora") → não é tempo, é PRIORIDADE.
· DINHEIRO ("não acho que vale") → não é dinheiro, é VALOR percebido.
· DECISOR ("preciso falar com meu sócio/marido/filha") → ele não precisa de PERMISSÃO, precisa de APOIO.
  Use acordos anteriores dele: "seu sócio sabe que a loja está estagnada há um ano, certo? Você acha que
  ele quer que continue assim?". ⚠️ ADAPTAÇÃO OBRIGATÓRIA AO NOSSO ICP: aqui o decisor costuma ser
  cônjuge/filha/irmã e o comprador RECUA com pressão. Se o decisor não está na call, o certo continua
  sendo transformar a call em diagnóstico + agendamento COM ele presente — nunca apresentar preço para
  quem avisou que não decide.
· STALL ("vou pensar") → a pessoa não sabe DECIDIR. Ela tem 5-10 conversas de compra por ano; você tem
  5 por dia. Cabe a você conduzir a decisão, não devolver o problema.
· PREFERÊNCIA ("dá pra fazer só o tráfego?", "posso pular essa parte?") → ele quer o SEU resultado do
  jeito DELE. Resposta: "se você muda as variáveis, muda o resultado. Você quer o resultado? Então não
  mude as variáveis." E a pergunta honesta: "[fazer do seu jeito] é mais importante do que [o resultado
  que você quer]?" — se a resposta for sim, nada vai mudar, e é melhor saber agora.
· REGRA: depois de tratar CADA objeção, PERGUNTE DE NOVO — "isso resolve pra você? Então podemos seguir?".
  Sem isso você acumula objeções tratadas e nenhuma fechada.

R — REINFORCE (as 24h depois do sim). A decisão é refeita na cabeça do comprador nas primeiras 24 horas;
é ali que nasce o arrependimento ou a relação. Amarre os próximos passos aos objetivos que ELE declarou:
"você disse que queria A, B e C — os três primeiros passos são estes, e a gente se fala [dia/hora]".
→ APLICAÇÃO DIRETA AQUI: a única call que fechamos terminou com pagamento prometido para a quarta e
reunião marcada. É exatamente essa janela que derruba venda no nosso funil. Confirmação no WhatsApp
ANTES da data combinada, com os passos amarrados ao que ele disse querer.$$,
 'Alex Hormozi — framework CLOSER (aula transcrita) + adaptações ao ICP do nicho óptico',
 array['metodo','estrutura','objecao','fechamento','hormozi'], 5),

('metodo', 'Equação de valor — por que o preço "parece caro"',
$$Valor percebido = (Resultado dos Sonhos × Probabilidade Percebida) ÷ (Tempo até o resultado × Esforço
exigido). O lead não compara preço com preço: ele pesa a GRAVIDADE DO PROBLEMA contra o CUSTO DA SOLUÇÃO.
Se o problema parece pequeno e o custo alto, não compra — por isso a etapa de Implicação vem ANTES do preço.

AS 4 PERGUNTAS QUE ELE FAZ EM SILÊNCIO, e que a apresentação precisa responder:
1. "O que eu vou conseguir?" — resultado no vocabulário dele. Se o closer descreveu ENTREGAS (módulos,
   encontros, bônus) em vez de RESULTADO, apresentou catálogo, não oferta.
2. "Como eu sei que vai acontecer comigo?" — prova do MESMO porte e região. Prova depois do preço não
   sustenta o preço.
3. "Quanto tempo leva?" — precisa de vitória rápida além do resultado final. Aqui é a campanha de
   reativação da base (4 a 10 dias). Falar só do horizonte de 4 meses deixa o denominador alto.
4. "O que se espera de mim?" — o dono de ótica JÁ comprou curso que não assistiu; o medo dele é ganhar
   mais uma tarefa. Reduzir esforço percebido é movimento de venda.

REGRA DE JULGAMENTO: as melhores ofertas competem na PARTE DE BAIXO da equação (tempo e esforço).
Promessa grande qualquer um faz. Se o closer só inflou a promessa e não mexeu em tempo/esforço, a
apresentação foi fraca mesmo que animada.$$,
 'Alex Hormozi, $100M Offers — versão enxuta (o que o SPIN já cobre foi removido)',
 array['metodo','valor','apresentacao','hormozi'], 5)

on conflict do nothing;
