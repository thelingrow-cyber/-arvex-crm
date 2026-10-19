# Curadoria da manhã (notícias de mercado)

## Quando esta página é usada
Todo dia de madrugada, com o comando `maquina.py noticias <N>` (ou `dia`), antes dos roteiros 📰 Mercado das 7h.

## O que chega
- O arquivo de pautas do dia, gerado por `tools/roteiros/noticias.py --salvar` (`docs/conteudo/pautas/AAAA-MM-DD.md`).
- A lista do que já virou roteiro (para não repetir).
- Quantas notícias escolher.

## O que sai
Exatamente N blocos neste formato, e nada além disso:
~~~
### N1 · bending-spoons-buffett
**Título:** A empresa do Buffett coloca mais US$ 330 mi na Bending Spoons
**Data da notícia:** 2026-10-14
**Fatos conferidos:** Berkshire compra 10 mi de ações a US$ 33 (US$ 330 mi), ~4% · já tinha entrado com US$ 600 mi no IPO de julho · ação fechou +41% no dia (CNBC; 34–45% conforme a fonte) · Airtable concluído em 04/09 · Miro assinado, sem conclusão
**Não confere / não usar:** a "alta de 35%" de um resumo secundário (a CNBC diz 41%)
**Fontes:** https://investors.bendingspoons.com/… · https://www.cnbc.com/…
**E daí pro dono:** o dinheiro grande está indo para quem arruma o que já existe, não só para a novidade
~~~

## Como fazer
1. Leia o arquivo de pautas inteiro. Se vier fraco, busque na web: big techs, IA aplicada a negócio, movimentos de mercado e de grandes empresas que um dono de negócio entende.
2. **Filtro do Caio:** *e daí, para o dono de uma loja de R$ 200 mil por mês?* Sem resposta em uma frase, descarte.
3. **Frescor:** a notícia tem no máximo **3 dias** (5, só se for muito forte e ainda pouco falada no Brasil). Marque a data.
4. **Nada batido:** se todo mundo no Brasil já falou e já tem empresa fazendo, descarte. *Motivo: o Vitor reprovou CAFEIA "batida" (muita cobertura é sinal contra).*
5. **Confira cada número na fonte primária** (o site de quem publicou o dado: a empresa, o regulador, o veículo original). Se as fontes divergem, registre a faixa e qual vale. Número que não confere vai para "Não confere / não usar". *Motivo: em 19/10 o N3 dizia "35%" e o fechamento real foi 41%.*
6. Varie: no máximo uma notícia por empresa, e não repita assunto da lista de "já usados".
7. Nada de ótica, nem nada sobre a Cindy (travas de `squads/conteudo/voz.md`). Sem cripto, sem bolsa como dica de investimento.
8. Ordene da mais forte para a mais fraca.
