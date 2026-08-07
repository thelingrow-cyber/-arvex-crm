-- ============================================================================
-- Cérebro do coach — entrada de SPIN + DEF e curadoria para caber no teto (24k).
--
-- SAI (desativado, preservado no banco):
--   · "Objeções reais x cortinas"      (1295) ─┐ fundidos num bloco único
--   · "Reversão de risco / garantia"   (1524) ─┤ de objeções, sem a sobreposição
--   · "A objeção nº1 — cicatriz"       (1627) ─┘
--   · "Escassez legítima x fabricada"   (892)  → absorvido no bloco do DEF (fechamento)
--
-- ENTRA:
--   · Objeções do nicho óptico (consolidado)
--   · SPIN — as 4 perguntas + a régua de resultado da call (avanço x continuação)
--   · DEF — arquitetura da call, escuta ativa, verificação e isolamento
-- ============================================================================

update sales_knowledge set ativo = false, updated_at = now()
 where titulo in (
   'Objeções reais x cortinas no nicho óptico',
   'Reversão de risco — a pergunta da garantia',
   'A objeção nº1 não é preço — é cicatriz de mentoria anterior',
   'Escassez e urgência: legítima x fabricada'
 );

insert into sales_knowledge (tipo, titulo, conteudo, fonte, tags, peso) values

('objecao', 'Objeções do dono de ótica — reais, cortinas e como tratar',
$$A OBJEÇÃO Nº1 NÃO É PREÇO — É CICATRIZ DE MENTORIA ANTERIOR. Nas palavras deles: "estou bem doída de
mentoria"; "toda resposta do mentor era: na mentoria de cinquenta mil eu ensino isso"; "foi muito genérica,
não tinha um mercado definido, você tinha que traduzir pra sua realidade"; "paguei muito caro e não me
trouxe resultado". Vale o mesmo para curso: ele COMPRA E NÃO ASSISTE ("o dia a dia corrido, terminei
perdendo"). Posicionar a entrega como treinamento reativa essa ferida.
→ Se o closer apresentou sem perguntar O QUE ELE JÁ COMPROU ANTES E POR QUE NÃO FUNCIONOU, deixou a
objeção mais forte da call intacta. Isso é erro de DIAGNÓSTICO, não de fechamento.

GENUÍNAS (mantêm a mesma narrativa do início ao fim): caixa comprometido por evento recente (reforma,
dívida com fornecedor, nova loja, carro); compromisso ativo com concorrente ("faz dois meses que entrei
em outra mentoria e tenho um ano ainda").

CORTINAS (mudam de forma ao longo da call): "vou analisar", "vou ver o orçamento" quando o valor ainda
não foi construído. SINTOMA-CHAVE: o lead pergunta o preço ANTES da apresentação.

A PERGUNTA DA GARANTIA. Quando ele pergunta "qual a garantia que eu tenho de que vai dar retorno?" ou
"não é chegar, fazer e me cobrar; se der certo, deu certo", ele está dizendo que o RISCO percebido é
maior que o VALOR percebido. Responder com BÔNUS não resolve (bônus mexe no valor, a objeção é de risco);
responder com DESCONTO é pior (sinaliza preço inflado). Registrado em call real: o lead perguntou pela
garantia e recebeu "libero o gestor de tráfego por um mês" — a pergunta ficou sem resposta e a call
terminou sem decisão. O que responde: garantia condicional ("se você aplicar X, Y e Z e não acontecer,
eu faço A"), garantia de desempenho, ou — na falta de garantia formal — INVERTER O RISCO COM NÚMERO:
o que ele já perde hoje por não fazer (base parada, lead sem resposta no WhatsApp) contra o valor do
programa.

OBJEÇÃO SILENCIOSA, presente em todas: "como eu sei que funciona pra MIM, na MINHA cidade?". Ele vai
atrás da prova sozinho. Prova social do MESMO PORTE E REGIÃO vale mais que aluno-estrela.

TRAVA DE CAIXA ≠ TRAVA DE VALOR. "Não tenho limite no cartão" / "tô com compromissos até o dia 10" é
capacidade de pagamento — resolve-se com CALENDÁRIO (data da parcela, entrada menor amarrada ao início
da execução), nunca com desconto. Em call real o preço caiu 4 vezes para uma trava de cartão e não
fechou; noutra o preço ficou de pé, o prazo mudou, e fechou.$$,
 'docs/crm/sales-coach/conhecimento/ (calls Djarla, Anderson, Tatiane, Aline, Vivalle, Wal Leite) + $100M Offers',
 array['objecao','preco','risco','mentoria'], 5),

('metodo', 'SPIN — as 4 perguntas e a régua de resultado da call',
$$SEQUÊNCIA: Situação → Problema → IMPLICAÇÃO → Necessidade de Solução.

O QUE A PESQUISA MOSTRA (Rackham, 35 mil visitas):
· Em venda GRANDE, o número de problemas descobertos (Necessidades Implícitas) NÃO prevê sucesso. O que
  prevê é quantas viram Necessidades EXPLÍCITAS — o lead declarando vontade/intenção de agir.
· Perguntas de Situação em excesso são NEGATIVAMENTE ligadas ao sucesso: entediam o lead. Colete o mínimo
  necessário e avance.
· Perguntas de Implicação são as mais ligadas ao sucesso em venda grande — e as mais raras: 1 em cada 20
  perguntas numa call média. Nas 6 calls da ARVEX analisadas: ZERO ocorrências.

POR QUE ISSO IMPORTA AQUI: sem Implicação, o preço encosta num problema que o lead ainda não mediu — e
qualquer valor parece caro. A Implicação não cria problema novo; ela mostra o tamanho do que já existe.

PERGUNTAS DE IMPLICAÇÃO NA LINGUAGEM DO DONO DE ÓTICA (usar 3-4):
· "Há quanto tempo o faturamento está nesse mesmo número?" → "e o que isso te custou nesse período?"
· "Se continuar exatamente assim por mais 12 meses, o que acontece com a loja?"
· "Desses clientes que chegam no WhatsApp e somem — quantos por semana? Se cada um vale [ticket dele],
  quanto isso dá no mês?"
· "Você falou que fica dividido entre [X] e [Y]. Quantas vendas perde por semana por causa disso?"
· "Quanto já colocou em tráfego/agência sem retorno? Somando tudo, dá quanto?"
· "Quando você faz uma ação e não vende, o que você faz pra descobrir onde errou?"

NECESSIDADE DE SOLUÇÃO (faz o LEAD dizer o benefício, em vez de o closer): "se você conseguisse [X], o
que mudaria na sua semana?" · "por que resolver isso agora é importante?" · "de que outra forma ajudaria?"

⭐ RÉGUA DE RESULTADO — como julgar se a call teve sucesso (4 desfechos):
· PEDIDO — compromisso firme de compra.
· AVANÇO — ação concreta acordada que move a venda (reunião marcada com data, acesso ao outro decisor,
  valor e data de pagamento definidos). EM VENDA GRANDE, O ALVO NORMAL DA CALL É O AVANÇO.
· CONTINUAÇÃO — a venda "continua" mas SEM ação acordada: "vou pensar", "me manda no WhatsApp", "adorei,
  a gente se fala". ISSO É FRACASSO, por mais simpático que tenha sido o lead. Elogio não é sinal de compra.
· RECUSA.
→ Ao analisar a call, classifique o desfecho por AÇÃO ACORDADA, nunca pelo clima da conversa. Nas calls
da ARVEX, 5 de 6 terminaram em Continuação disfarçada de otimismo.$$,
 'Neil Rackham, SPIN Selling (cap. 2 a 4) + as 6 calls da ARVEX',
 array['metodo','perguntas','implicacao','spin','avanco'], 5),

('metodo', 'DEF — arquitetura da call: descoberta, encantamento, fechamento',
$$ARQUITETURA: Descoberta 15 min (sem tela) → Encantamento ~12 min → Fechamento ~8 min. Call inteira ≤ 1h.
Desequilíbrio observado nas nossas calls: 4-8 min ouvindo contra 15-25 min falando. A única que fechou
inverteu isso — o lead falou mais que o closer.

ABERTURA: contrato da call COM TAKEAWAY — "a gente vê se faz sentido caminhar junto, OU NÃO; se eu achar
que não é a hora, eu vou ser o primeiro a falar". O "ou não" baixa a guarda de quem entrou defendido.
E logo depois: "além de você, quem mais participa dessa decisão?" — SE FALTA DECISOR, a call vira
diagnóstico + agendamento e NÃO se apresenta preço.

DESCOBERTA — 4 objetivos: aumentar conexão · coletar insumos para o encantamento · antecipar objeções ·
obter micro compromissos.
· ESCUTA ATIVA O TEMPO TODO (não é uma fase): a cada resposta relevante, parafrasear — "deixa eu ver se
  entendi: você [palavras dele]. É isso?". Depois de o lead responder, USE O SILÊNCIO em vez de emendar a
  próxima pergunta. Três frases que fazem ele continuar sozinho: "como assim?" · "me conta mais sobre
  isso" · "e o que mais?".
· NÃO DEFENDER TESE. Educar sobre mercado/método na descoberta corta o fluxo do lead e você chega ao
  encantamento com menos munição. Leve por pergunta, não por afirmação.
· EXPRESSÃO GRÁVIDA: quando ele diz algo importante mas vago ("não sei se tô fazendo certo", "preciso
  organizar a casa"), pare e abra: "o que exatamente hoje está mais desorganizado pra você?".
· ENGENHARIA REVERSA DOS ENTREGÁVEIS: para cada um dos 3 pilares do produto, tenha uma pergunta de
  descoberta que faça o lead verbalizar a dor que aquele pilar resolve. O insumo do encantamento é
  criado de propósito, não por sorte.

ENCANTAMENTO — no máximo 3 PILARES (mais que isso o lead não assimila; só ~20% do que o closer fala é
retido). Cada pilar com a estrutura: dor NAS PALAVRAS DELE → entregável → o que ele ganha/como se sente.
· Monólogo acima de 2 minutos quebra a conexão: a cada bloco, uma pergunta ("isso faz sentido pro teu
  caso?") — isso também gera micro compromisso.
· Não mostrar o catálogo inteiro: excesso de entregável vira "isso é demais pra mim", sobretudo em quem
  ainda não teve resultado. O resto vira menção de uma linha.
· Slide é apoio, não vendedor: um item por vez; texto na tela compete com a narrativa.
· Prova social no começo ou no fim, nunca no meio — mas se o lead sinalizar desconfiança ("é tudo online,
  né?", "tem alguém aqui da minha cidade?"), PARE e entregue na hora.

TRANSIÇÃO (o que falta em 6 de 6 calls nossas):
1. PERGUNTA DE VERIFICAÇÃO, ABERTA e com o slide FORA DA TELA: "de tudo que eu falei, o que mais fez
   sentido pra você?". Jamais a versão fechada ("fez sentido?"), que só rende um "sim" sem insumo.
   RÉGUA: citou 1 dos 3 pilares = mal ancorado, VOLTE e reforce, não vá ao preço · citou 2 = reforce o
   terceiro · citou 3 = siga.
2. ISOLAMENTO DE VARIÁVEIS: "o que falta pra você começar com a gente?" → "então sobre o programa está
   tudo certo, é só a questão do investimento?" → "se a gente viabilizar essa parte, você começa agora?".
   Isto SUBSTITUI o pedido de sinal simbólico: obtém compromisso sem cobrar nada e sem sinalizar que o
   preço era inflado. O sinal simbólico apareceu em 5 das 6 calls, com 3 closers, e converteu zero.

FECHAMENTO: a decisão de COMPRA é tomada no encantamento; no fechamento só se decide PAGAMENTO. Ancore
antes do número (a conta da base: o dinheiro que já está na carteira dele). Preço uma vez só, fechamento
presumido — "fica melhor à vista ou parcelado?", não "o que você acha?". Comando final com ação imediata
("abre o link que eu te mandei, preenche que eu fico em linha e já marco tua primeira reunião").
NUNCA estimular "pense mais uma semana". Escassez só se for verdade verificável fora da call
(exclusividade por cidade é legítima; "condição só hoje" num comprador que decide em dupla aumenta a
resistência).$$,
 'Método DEF (Vendas Pro, revisão do closer do Ladeira) + docs/crm/sales-coach/conhecimento/metodo-def.md',
 array['metodo','estrutura','fechamento','isolamento','escuta-ativa'], 5)

on conflict do nothing;
