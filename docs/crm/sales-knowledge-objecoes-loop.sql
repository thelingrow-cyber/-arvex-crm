-- ============================================================================
-- Cérebro do coach — mecânica de tratamento de objeção (Looping Script da ACQ)
-- adaptada ao nosso comprador, com as respostas prontas para as 5 objeções que
-- realmente aparecem nas nossas 6 calls.
--
-- DESCARTADO DO ORIGINAL (e registrado no bloco, para o coach não recomendar):
--   · a manobra de passar por cima do cônjuge ("e se ele disser não? você iria
--     mesmo assim?") — no nicho óptico decidir em dupla é cultura, não formalidade
--   · o tom de pressão ("seria loucura?", "você seria contra?")
--   · a sondagem de caixa disponível ("quanto você tem em caixa agora?")
--   · "é bom que seja caro"
-- ============================================================================

insert into sales_knowledge (tipo, titulo, conteudo, fonte, tags, peso) values

('objecao', 'Como tratar objeção: isolar antes de responder (loop) + respostas prontas',
$$A MECÂNICA — nunca responder a primeira objeção que aparece. Primeiro ISOLAR:
1. CONFIRMAR: "Ahh, entendi — então o principal é [objeção]?"
2. ISOLAR: "**Além de [objeção], tem mais alguma coisa te segurando?**"
3. Só depois de o lead dizer que não há mais nada, RESOLVER.
4. REPERGUNTAR: "isso resolve pra você? Então podemos seguir?"
Repetir o loop até sobrar uma objeção só. Sem isolar, o closer trata três objeções e não fecha nenhuma —
foi o que aconteceu em 4 das 6 calls.

Se o lead responde vago ("é...", "não sei"), SONDAR antes: "hmm, você não parece muito confiante — qual
seria sua principal preocupação?" · "é mais [tipo A] ou [tipo B]?"

AS 5 OBJEÇÕES E O QUE FAZER COM CADA UMA:

1) CICATRIZ DE MENTORIA ("já fiz e não deu certo") — A NOSSA Nº1, e a que o script americano não tem.
Não defenda. Investigue: "o que exatamente você contratou e o que faltou lá?" A resposta entrega a
estrutura do seu pitch. Se ela já tentou o que você vende (ex.: grupo VIP que ninguém quis), pergunte
COMO ela fez — quase sempre ela adicionou as pessoas sem convidar e mandou oferta direto, sem os dias de
antecipação. O fracasso dela vira a prova de que o método importa.

2) DINHEIRO / CAIXA. Separe VALOR de CAPACIDADE: "se a parte do investimento estivesse resolvida, tem
mais alguma coisa te impedindo de começar?"
· Se responder que não → é capacidade: resolva com CALENDÁRIO (entrada menor amarrada ao início da
  execução, restante em data combinada), nunca com desconto. Foi o que fechou a única call ganha.
· Se responder que sim → é valor: volte à Implicação, não mexa no preço.
⚠️ NÃO perguntar "quanto você tem em caixa hoje?" — no nosso nicho isso quebra a confiança (uma lead
desconversou duas vezes só sobre o faturamento).

3) DECISOR ("preciso falar com meu marido / minha filha / meu sócio"). Ele não precisa de PERMISSÃO,
precisa de APOIO. Pergunte: "qual seria a maior preocupação dele(a)?" — e trate ESSA objeção, que é a
real. Depois: "além de falar com ela, tem mais alguma coisa te segurando?"
⚠️ REGRA DA CASA, e ela SUBSTITUI a versão agressiva do script americano: **não se pergunta "e se ele
disser não, você faria mesmo assim?" e não se apresenta preço para quem avisou que não decide.** O
movimento certo é agendar a conversa COM o decisor presente. No nicho óptico decidir em dupla é cultura
(irmãs sócias, casal sócio, cartão da mãe emprestado), não formalidade.

4) "VOU PENSAR" / "analiso até sexta". Isso é falta de método de decisão, não falta de informação. Seja
direto, sem pressão: "posso ser sincero? Normalmente quando alguém precisa pensar é por um de dois
motivos: ou não ficou claro o valor — e aí eu prefiro esclarecer agora — ou é a parte prática, de como
encaixar. Qual dos dois é o seu caso?" Depois de resolver, marque data. **Nunca estimule "pensa mais uma
semana"** e nunca aceite "vou pensar" como próximo passo.

5) PREFERÊNCIA ("dá pra fazer só o tráfego?", "posso pular essa parte?"). Ele quer o seu resultado do
jeito dele: "se você muda as variáveis, muda o resultado. Você quer o resultado? Então essa parte é a
que não dá pra pular." Sem ironia e sem desafio — no nosso comprador, provocação gera recuo.

REGRA DE SAÍDA (BAMFAM): não encerrar call sem próxima reunião marcada com DIA E HORA e objetivo
declarado ("na próxima a gente vai [X]"). Se o lead não fecha e não marca, a call foi CONTINUAÇÃO —
ou seja, fracasso, por mais simpática que tenha sido. 5 das nossas 6 calls terminaram assim.$$,
 'Roteiro ACQ (Looping Script) adaptado ao ICP óptico + as 6 calls da ARVEX',
 array['objecao','loop','isolamento','decisor','bamfam'], 5)

on conflict do nothing;
