-- Ajuste de teto: o bloco da autoridade/prova social tinha sobreposição com o
-- DEF (prova social) e com o bloco de objeções (objeção silenciosa). Fica só o
-- que é exclusivo dele: quem resolve o medo do "é tudo online" não é o closer.

update sales_knowledge
   set conteudo = $$Padrão observado em live e confirmado em call: antes de fechar, o lead vai atrás da
AUTORIDADE por conta própria — não pede prova ao vendedor. "O meu maior medo foi não ter respaldo. Com
vocês é tudo online, é tudo muito incerto." / "Antes de fechar qualquer coisa, eu fui falar com a Cindy
diretamente. Chamei ela no Instagram dela. E foi uma coisa que aliviou." / "Teve uma menina que me chamou
no WhatsApp perguntando se era confiável." Em call real, a lead tinha ido olhar o Instagram da Cindy ANTES
da reunião e reparou que só via "vendas do curso dela" — foi buscar prova e não achou a prova certa.

CONSEQUÊNCIAS PARA A CALL:
1. Quando o lead PEDE nominalmente um caso ("vocês têm alguém aqui da minha cidade?"), pare a
   apresentação e entregue na hora. Registrado: uma lead pediu DUAS vezes falar com a mentorada de
   Curitiba e recebeu casos do Pará e de São Paulo, mais a promessa de mandar o vídeo depois.
2. Aproximar a autoridade (áudio dela, DM, presença numa call) vale mais que qualquer bônus material.
   Se o closer respondeu à insegurança com desconto ou bônus em vez de aproximação/prova, aponte como
   erro estratégico.$$,
       updated_at = now()
 where titulo = 'Quem tira o medo do "é tudo online" é a autoridade, não o closer';
