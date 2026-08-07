-- ============================================================================
-- Blocos adicionais do cérebro (sales_knowledge) — acumulativo.
-- Cada bloco é material externo DESTILADO em critério verificável numa call.
-- Regra: nada de teoria; se não dá para olhar a transcrição e dizer "aconteceu"
-- ou "não aconteceu", não entra.
-- ============================================================================

insert into sales_knowledge (tipo, titulo, conteudo, fonte, tags, peso) values

('metodo', 'Equação de valor aplicada à call (Hormozi, $100M Offers)',
$$Valor percebido = (Resultado dos Sonhos × Probabilidade Percebida) ÷ (Tempo até o resultado × Esforço exigido).
Use como CHECKLIST da apresentação. As 4 perguntas que o lead faz em silêncio, e que o closer precisa
ter respondido ANTES de falar preço:
1. "O que eu vou conseguir?" — resultado concreto, no vocabulário do lead (faturamento, fila na loja,
   sair da guerra de preço). Se o closer descreveu ENTREGAS (módulos, encontros, bônus) em vez de
   RESULTADO, ele apresentou catálogo, não oferta.
2. "Como eu sei que vai acontecer comigo?" — prova. Caso do MESMO porte e região vale mais que
   aluno-estrela. ERRO GRAVE E FREQUENTE: deixar a prova social para depois do fechamento, ou só
   mencionar que existe ("depois te mando os vídeos"). Prova depois do preço não sustenta o preço.
3. "Quanto tempo leva?" — precisa de vitória rápida além do resultado final. Na oferta da casa a
   vitória rápida é a campanha de reativação da base (primeira semana / até 15 dias). Se o closer só
   falou do horizonte de 4 meses, o denominador ficou alto.
4. "O que se espera de mim?" — esforço percebido. O dono de ótica JÁ comprou curso que não assistiu:
   o medo dele é ter mais uma tarefa. Reduzir esforço ("a Sabrina te aponta os 2 módulos do momento",
   "campanha vem pronta pra copiar e colar", "o gestor roda o tráfego") é o movimento certo.

REGRA DE JULGAMENTO: as melhores ofertas competem na PARTE DE BAIXO da equação (tempo e esforço).
Promessa grande qualquer um faz. Se o closer só inflou a promessa e não mexeu em tempo/esforço, a
apresentação foi fraca mesmo que animada.$$,
 'docs/clone-hormozi-pesquisa/resumos/livro-100m-offers.md (Alex Hormozi, $100M Offers)',
 array['metodo','valor','apresentacao','hormozi'], 5),

('objecao', 'Reversão de risco — a pergunta da garantia',
$$"Reverter o risco é a forma número um de aumentar a conversão de uma oferta." Quando o lead pergunta
QUAL A GARANTIA (e no nicho óptico ele pergunta com estas palavras: "qual a garantia que eu tenho de
que vai dar retorno?", "não é chegar, fazer e me cobrar; se der certo, deu certo"), ele está dizendo
que o risco percebido é maior que o valor percebido. Nesse momento:

- Responder com BÔNUS não resolve. Bônus aumenta o numerador (mais valor); a objeção é de risco.
  Registrado em call real: o lead perguntou pela garantia e recebeu "libero o gestor de tráfego por
  um mês" — a pergunta ficou sem resposta e a call terminou sem decisão.
- Responder com DESCONTO ou com SINAL SIMBÓLICO é pior: sinaliza que o preço era inflado e substitui
  o compromisso real por um compromisso de brinquedo.
- O que responde: garantia condicional ("se você aplicar X, Y e Z e não acontecer, eu faço A") ou
  garantia implícita de desempenho, que alinha incentivo. Se a casa não tem garantia formal, o
  substituto honesto é MOSTRAR O RISCO INVERTIDO COM NÚMERO: o que o lead já perde hoje por não fazer
  (base parada, lead sem resposta no WhatsApp) comparado ao valor do programa.

TIPOS DE GARANTIA (para reconhecer qual foi usada): incondicional (devolvo se pedir) · condicional
(garanto se você fizer X) · anti-garantia (venda final) · implícita/desempenho (se você não ganha, eu
não ganho — a mais forte).

AVISO: garantia não conserta produto ruim nem call mal conduzida. Se o valor não foi construído, a
garantia vira desespero.$$,
 'docs/clone-hormozi-pesquisa/resumos/livro-100m-offers.md + calls reais (Djarla 04/08)',
 array['objecao','garantia','risco','hormozi'], 5),

('metodo', 'Escassez e urgência: legítima x fabricada',
$$Escassez (limitar quantidade) e urgência (limitar tempo) só funcionam quando são VERDADE verificável.
No contexto da casa:
- LEGÍTIMA: exclusividade por cidade enquanto o contrato durar (a mesma campanha não pode rodar em
  duas óticas da mesma praça). O lead reconhece sozinho — em call real ele completou a frase do
  closer: "uma exclusividade, né?". Vaga limitada do gestor de tráfego também é legítima se for real.
- FABRICADA: "condição só hoje", "sinal para segurar o valor", prazo inventado para o dia seguinte.
  No perfil analítico do dono de ótica — que decide em dupla e está com o caixa organizado em planilha —
  pressão artificial AUMENTA a resistência em vez de acelerar.

REGRA DE JULGAMENTO: se o closer usou escassez, verifique se ela existe fora da call. Escassez que só
existe dentro da conversa é ruído e deve entrar como erro de condução, não como acerto de fechamento.$$,
 'docs/clone-hormozi-pesquisa/resumos/livro-100m-offers.md + calls reais',
 array['metodo','fechamento','escassez'], 4)

on conflict do nothing;
