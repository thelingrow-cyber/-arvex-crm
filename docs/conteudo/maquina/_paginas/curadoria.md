# Curadoria da manhã (notícias de mercado)

## Quando esta página é usada
Todo dia de madrugada, com o comando `maquina.py noticias <N>` (ou `dia`), antes dos roteiros 📰 Mercado das 7h.

## O que chega
- O arquivo de pautas do dia, gerado por `tools/roteiros/noticias.py --salvar` (`docs/conteudo/pautas/AAAA-MM-DD.md`).
- A lista do que já virou roteiro (para não repetir).
- Quantas notícias escolher.
- **O que os concorrentes postaram nos últimos 3 dias** (coleta da manhã: perfil, data, views, abertura e legenda).

## O que sai
Exatamente N blocos neste formato, e nada além disso:
~~~
### N1 · bending-spoons-buffett
**Título:** A empresa do Buffett coloca mais US$ 330 mi na Bending Spoons
**Data da notícia:** 2026-10-14
**Fatos conferidos:** Berkshire compra 10 mi de ações a US$ 33 (US$ 330 mi), ~4% · já tinha entrado com US$ 600 mi no IPO de julho · ação fechou +41% no dia (CNBC; 34–45% conforme a fonte) · Airtable concluído em 04/09 · Miro assinado, sem conclusão
**Não confere / não usar:** a "alta de 35%" de um resumo secundário (a CNBC diz 41%)
**Concorrentes:** ninguém deu · (ou) @beprecht deu em 18/10 com 40 mil views; nosso ângulo: …
**Fontes:** https://investors.bendingspoons.com/… · https://www.cnbc.com/…
**E daí pro dono:** o dinheiro grande está indo para quem arruma o que já existe, não só para a novidade
~~~

## Como fazer
1. Leia o arquivo de pautas inteiro. Se vier fraco, busque na web: big techs, IA aplicada a negócio, movimentos de mercado e de grandes empresas que um dono de negócio entende. **Vale também (22/10, pedido do Vitor) notícia do mundo ou uma curiosidade que aconteceu**, do tipo que a pessoa conta numa mesa ("uma academia/um evento proibiu quem faz vibe coding"): fato estranho, decisão inesperada, regra nova de alguém conhecido. O critério é dar uma ideia e uma opinião do Vitor em ~1 minuto. *Motivo: "pode ser uma notícia do mundo ou uma curiosidade… criar um roteiro mais humanizado, com tom de fala normal, já com uma ideia e opinião."*
2. **Filtro do Caio:** *e daí, para o dono de uma loja de R$ 200 mil por mês?* Sem resposta em uma frase, descarte. Na curiosidade, a resposta pode ser uma ideia sobre gente, trabalho ou decisão (não precisa ser dinheiro), desde que caiba em uma frase.
2b. **Escolha as mais fortes:** a máquina gera uma a mais e manda só as 3 de melhor nota; ordene pensando em qual a pessoa contaria pra alguém depois de ver.
3. **Frescor:** a notícia tem no máximo **3 dias** (5, só se for muito forte e ainda pouco falada no Brasil). Marque a data.
4. **Nada batido:** se todo mundo no Brasil já falou e já tem empresa fazendo, descarte. *Motivo: o Vitor reprovou CAFEIA "batida" (muita cobertura é sinal contra).*
5. **Olhe a lista dos concorrentes** antes de fechar a escolha (é o que o Fabiano faz: "a cada dois dias os reels dos concorrentes são puxados"):
   - notícia que **2 ou mais brasileiros já postaram** = batida: descarte, ou fique só se tiver um ângulo pro dono que nenhum deles deu (escreva qual na linha **Concorrentes**);
   - notícia que **um player de fora ou um só brasileiro** postou e foi bem de views = sinal a favor (o assunto puxa público e ainda está aberto aqui);
   - um concorrente que deu a notícia **não é fonte**: confira o fato na fonte primária como qualquer outro.
   *Motivo: o Vitor pediu em 20/10 "puxe dos concorrentes também, pra ver se eles postaram alguma notícia".*
6. **Confira cada número na fonte primária** (o site de quem publicou o dado: a empresa, o regulador, o veículo original). Se as fontes divergem, registre a faixa e qual vale. Número que não confere vai para "Não confere / não usar". *Motivo: em 19/10 o N3 dizia "35%" e o fechamento real foi 41%.*
7. Varie: no máximo uma notícia por empresa, e não repita assunto da lista de "já usados". **Atendimento, chatbot ou WhatsApp com IA: no máximo 1 por semana.** O ângulo pro dono nunca é "a IA que responde teu cliente": procure dinheiro, preço, decisão, contratação, concorrência. *Motivo: o Vitor pediu em 20/10 "sair desse vício de ficar fazendo sobre atendimento".*
8. Nada de ótica, nem nada sobre a Cindy (travas de `squads/conteudo/voz.md`). Sem cripto, sem bolsa como dica de investimento.
9. Ordene da mais forte para a mais fraca.
