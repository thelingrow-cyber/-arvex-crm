-- ============================================================================
-- Cérebro do coach — atualização do ICP para v2 (2026-08-05)
-- Base: 3 calls de venda + 15 lives/encontros da Cindy (~45 participantes),
-- destilados em docs/crm/sales-coach/conhecimento/icp-fontes/.
-- Substitui o bloco de ICP da v1 (que vinha só das 3 calls) e adiciona os dois
-- padrões que só apareceram com o volume das lives.
-- ============================================================================

-- fora do prompt o bloco antigo (mantido no banco como histórico, não apagado)
update sales_knowledge
   set ativo = false, updated_at = now()
 where tipo = 'icp'
   and titulo = 'Quem é o dono de ótica (perfil real, extraído de calls)';

insert into sales_knowledge (tipo, titulo, conteudo, fonte, tags, peso) values

('icp', 'Quem é o dono de ótica (v2 — 3 calls + 15 lives, ~45 participantes)',
$$QUEM É: mulher (≈35 de 45 participantes), 1 a 3 lojas, operando com o cônjuge ou a irmã. Divisão que se
repete: ELA no marketing/atendimento/financeiro, ELE na parte técnica/laboratório. NUNCA decide sozinha —
esposo, sócia, irmã ou mãe entram na decisão. Do Pará a Santa Catarina, capital e interior. Religiosidade
explícita entra na compra ("entramos na sua mentoria pela fé, parcelado em 2x"). Repertório prático, não
acadêmico: usa "markup" e "ticket médio" certo, mas erra o nome das ferramentas ("bicicleta" = biblioteca
de anúncios, "flow up" = follow-up). Tempo de ramo ≠ tempo de loja própria.

AS DORES, EM ORDEM:
1. FALTA DE DIREÇÃO (dor-mãe). Ele não é parado — roda tráfego, faz campanha, liga cliente a cliente —
   ele se move sem bússola e sabe: "a gente não sabe se tá fazendo certo", "sem estratégia a gente não
   chega a lugar nenhum". Vender esforço não funciona; vender critério funciona.
2. ESTAGNAÇÃO, não falência: "faturamos a mesma coisa do ano passado. Isso pra mim é inadmissível."
   O gatilho é orgulho ferido e medo de irrelevância — não aperto de caixa.
3. O LEAD QUE TRAVA NO WHATSAPP: "a pessoa gostou, mas parece que travou", "peço foto da receita, já nem
   manda mais", "visualizou e não respondeu". Já pagam gestor de tráfego e mesmo assim voltam pedindo
   criativo e resposta de WhatsApp. Fora do horário comercial ninguém responde.
4. O DONO É O GARGALO: "fico ali no WhatsApp, no WhatsApp e no WhatsApp"; "o maior motivo da minha
   mentoria era aprender a delegar"; "a gente não tem tempo com os filhos".
5. VERGONHA DE APARECER: "morro de vergonha", "filmei umas vinte vezes". Quem virou o jogo virou o rosto
   da loja: "eu sou a cara da minha ótica".
6. GUERRA DE PREÇO com a ótica da esquina (não com rede grande): "os quatro concorrentes do mesmo
   quarteirão estavam com a mesma campanha em dobro". Captador na porta do oftalmo rouba cliente.
7. REFÉM DE TERCEIROS: "estou sem o gestor, então não subi campanha nenhuma". Cada dependência externa
   custa um mês de faturamento.

ECONOMIA (confirmar antes de usar como benchmark — transcrição corrompe números): faturamento R$10k a
R$45k/loja/mês · ticket médio R$900 a R$1.600 · armação isca R$1-189, linha até R$650 · combo visão
simples ~R$249-399, multifocal ~R$449-599 · tráfego R$700-1.500/mês · custo por lead R$7-10 · base de
700 a 20.000 contatos. NINGUÉM, em 18 fontes, fala margem, lucro, CMV ou folha — ele raciocina em preço
de venda, não em resultado. O motor econômico é a LENTE DE MARCA PRÓPRIA, não a armação: Varilux+Crizal
~R$5.000 vira marca própria a R$3.800 com cliente satisfeita. Armação é isca; a margem está na lente.

VOCABULÁRIO DELE: guerra de preço · público chorão · cliente de porta · passante · captador · visão
simples/multifocal · marca própria vs grife · clip-on · o "ar" (antirreflexo) · exame de vista como
chamariz · feira de São Paulo · grupo VIP · campanha em dobro · "o mercado tá frio" · "grupo VIP
falecido" · "loja do precinho" · "querem o óculos pra ontem" · "quem sou eu na fila do pão".$$,
 'docs/crm/sales-coach/conhecimento/icp-dono-de-otica.md v2 — 3 calls + 15 lives (lotes 1-3 em icp-fontes/)',
 array['icp','otica','comprador'], 5),

('objecao', 'A objeção nº1 não é preço — é cicatriz de mentoria anterior',
$$Em 2 de 3 lotes de lives e em 2 calls, o que trava não é o valor: é ter comprado antes e não ter tido
retorno. Como sai da boca deles:
- "Estou bem doída de mentoria."
- "Toda resposta que eu tinha do mentor era: na mentoria de cinquenta mil eu ensino isso."
- "Foi uma mentoria muito genérica, porque não tinha um mercado definido — eram vários empresários, você
  tinha que traduzir pra sua realidade."
- "A gente fechou uma mentoria caríssima com outro rapaz e não vimos resultado. Foram meses e meses."
- "Eu seguia um coach de alta performance, paguei muito caro e não me trouxe o resultado."
- Ceticismo declarado: "detesto papo de coach e motivacional", "tá com muita firula, não?"

Vale o mesmo para curso: ele COMPRA E NÃO ASSISTE ("já comprei cursos que não consegui ver, o dia a dia
corrido, terminei perdendo"). Posicionar a entrega como treinamento reativa exatamente essa ferida.

O QUE DESTRAVA (razões declaradas de compra, palavras deles):
- Especificidade de nicho: "você vive a nossa realidade, vive no nosso mercado, chegou onde a gente
  quer chegar."
- Acompanhamento, não conteúdo: "é isso que eu preciso — não só de pensar, mas de alguém no meu pé."
- Entender o mecanismo, não copiar: "a pior coisa é pegar uma coisa pronta e não entender o que está por
  trás. Chega dezembro, a pessoa vai copiar de novo?"

REGRA PARA O COACH: se o closer apresentou a oferta sem perguntar o que o lead já comprou antes e por que
não funcionou, ele deixou a objeção mais forte da call intacta. Perguntar isso cedo entrega de graça a
estrutura do próprio pitch. Tratar isso como erro de diagnóstico, não de fechamento.$$,
 'docs/crm/sales-coach/conhecimento/icp-fontes/ (lotes 2 e 3) + calls reais',
 array['objecao','mentoria','diagnostico'], 5),

('metodo', 'Quem tira o medo do "é tudo online" é a autoridade, não o closer',
$$Padrão observado em live e confirmado em call: antes de fechar, o lead vai atrás da AUTORIDADE por conta
própria — não pede prova ao vendedor.

Evidência:
- "O meu maior medo foi não ter respaldo. Com vocês é tudo online, é tudo muito incerto."
- "Antes de fechar qualquer coisa, eu fui falar com a Cindy diretamente. Chamei ela no Instagram dela."
- "O [closer] sofreu um pouquinho na minha mão, porque eu sou bem desconfiada. Tanto que eu fui falar com
  a Cindy. E foi uma coisa que aliviou."
- Ela mesma explica a lógica com a própria loja: "é como nas nossas lojas — o cliente se sente muito mais
  seguro quando fala com a gente."
- Em call: a lead tinha ido olhar o Instagram da Cindy ANTES da reunião e reparou que só via "vendas do
  curso dela" — ou seja, foi buscar prova e não encontrou a prova certa.
- Outra: "teve uma menina que me chamou no WhatsApp perguntando se era confiável."

CONSEQUÊNCIAS PARA A CALL:
1. Prova social tem que vir ANTES do preço, não depois. Deixar o caso para "depois te mando os vídeos no
   WhatsApp" é entregar a decisão sem sustentação — erro registrado em call real.
2. O caso que convence é o do MESMO PORTE E REGIÃO: "quando a gente viu o depoimento da Amanda — a pessoa
   que a gente conhece — a gente chegou a chorar". Aluno-estrela de R$143 mil impressiona menos.
3. Aproximar a autoridade (áudio dela, DM, presença numa call) vale mais que qualquer bônus material.
   Se o closer respondeu a insegurança com desconto ou bônus em vez de aproximação/prova, aponte como
   erro estratégico.$$,
 'docs/crm/sales-coach/conhecimento/icp-fontes/lote-3 + call Djarla 04/08',
 array['metodo','prova-social','autoridade','confianca'], 5),

('metodo', 'A primeira vitória vem da base — com payback medido em dias',
$$Único mecanismo que aparece em TODAS as fontes (3 calls + 3 lotes de lives), sempre com o mesmo formato:
campanha sobre a carteira de clientes que a loja já tem, não sobre público novo.

NÚMEROS REAIS (usar como prova, confirmando antes):
- Fran (Curitiba, 8 anos): +R$9 mil em menos de 10 dias na 1ª campanha, só com clientes próprios; mês
  seguinte +R$12 mil. "Se a gente colocar na ponta do lápis, a gente já pagou em menos de dez dias."
- Kesia (10 anos de loja): 100 pessoas no grupo VIP em 20 dias; "em quatro dias vendemos o que vendemos
  em quinze, vinte dias de loja".
- Rafaela (Florianópolis): R$10-12 mil/mês → R$22 mil/mês.
- karen: R$9-10 mil em 8 vendas com campanha orgânica "malfeita" e brinde do próprio estoque (custo zero);
  "todos são clientes que já eram nossos".
- Astronildo: R$9 mil num único sábado.
- Miriam (Uberlândia): de <R$5 mil no mês inteiro para R$10 mil em 2 semanas.
- Danielle: "já paguei quase cem por cento da mentoria aplicando no segundo dia. E eu nem comecei."

POR QUE ISSO IMPORTA NA CALL: este é o único argumento que responde de uma vez a três objeções que
aparecem juntas — medo de não ter retorno, falta de caixa e cicatriz de mentoria anterior. E responde com
prazo curto (4 a 10 dias), não com promessa de 4 meses.

COMO USAR (o que os closers NÃO estão fazendo): parar de dizer "tem dinheiro parado na mesa" e FAZER A
CONTA ao vivo — "quantos clientes vocês têm no cadastro? Se 2% voltarem com o ticket de vocês, é R$ X numa
semana". Sem perguntar o tamanho da base, o argumento vira retórica. Em call real o closer identificou o
ouro, disse a frase certa e não perguntou o número: a call terminou sem decisão.$$,
 'docs/crm/sales-coach/conhecimento/icp-dono-de-otica.md §5 (8 casos independentes)',
 array['metodo','base','payback','prova'], 5)

on conflict do nothing;
