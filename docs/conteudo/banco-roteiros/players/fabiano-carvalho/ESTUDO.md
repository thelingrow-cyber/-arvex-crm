# Fabiano Carvalho (@fabianocarvalhojr) — estudo completo

**Base:** os 50 reels mais recentes sem fixados (08/10 → 14/10/2026: **50 posts em 7 dias**), métricas do Apify + transcrição Groq de todos, em `reels.json`. Folhas de contato dos 8 maiores. 3 picos de fora da janela transcritos. Coletado em 14/10/2026.
**Mediana:** 9.074 views (perfil com 254 mil seguidores, verificado). **Duração mediana:** 36s.
**Quem é / público:** fundador da **Lasy AI** (plataforma que cria app, sistema e landing page a partir de texto, a partir de R$ 197/mês) e da **Vibehub Academy** (trilhas Vibe Business, Vibe Coding e Vibe Marketing + comunidade, **R$ 147/mês no plano anual**, promessa *"5x menos humanos, 10x mais faturamento"*, para **fundadores, empresários, profissionais liberais, clínicas e agências**). **É o player mais próximo do ICP do Vitor até agora, e o concorrente mais direto:** vende IA para o mesmo dono de negócio.

**Como usar:** §1 e §2 para entender a máquina de volume (é o que o Vitor quer fazer); §3 para o esqueleto dos vídeos de ferramenta; §7 para o que levar e §8 para a leitura de concorrência.

---

## 1. O achado principal: ele já roda a máquina de 7 por dia, e diz como

| Dado | Número |
|---|---|
| Posts por dia (08 a 14/10) | 7, 7, 9, 9, 8, 6, 4 (média ~7) |
| Pedido de comentário na legenda | **48 de 50** |
| Comentários na semana | **27.375** (cada um vira uma conversa no direct) |
| Comentários por mil views (mediana) | 12,9 |

Ele contou a máquina num vídeo (`DeSN2nhFZr3`, 9,5 mil): *"esse é o fluxo que faz os reels que você tá assistindo agora. A cada dois dias, os reels mais recentes dos meus concorrentes são puxados, e um dos meus 12 agentes passa em cada um deles e escreve os temas que eu ainda não cobri. Essa ideia, por exemplo, veio dessa lista, de um reels que fez bastante view."*

É o mesmo processo que o Vitor quer (a IA gera o cardápio a partir das referências, ele aprova e grava), já rodando em escala. As legendas reforçam: todas têm a mesma estrutura, longa e factual, com número e fonte (*"158.478 estrelas no GitHub, licença MIT, está no ar desde outubro de 2025"*), o que indica texto feito pelo mesmo fluxo de agentes.

**O código no comentário rastreia cada post.** Toda legenda pede um código diferente de 5 caracteres (*"Comente 'EHYMR'"*). O último caractere muda pelo tipo: **R** nos vídeos falados, **H** nos posts de 8 segundos. A leitura mais provável é de que o código diz qual post gerou cada conversa no direct (não visto por dentro; inferido do padrão).

## 2. Views não são o objetivo: o que traz conversa é outra coisa

| Formato | Vídeos | Mediana de views | Comentários por mil views |
|---|---|---|---|
| Games / emulação (fora do nicho) | 4 | **179 mil** | 14,2 |
| Ferramenta ou repositório grátis que saiu | 18 | 16 mil | 21,1 |
| Tutorial na tela | 6 | 6 mil | 26,1 |
| **Método para negócio** (conselho de agentes, fluxo da Anthropic) | 2 | 9 mil | **35,8** |
| Resumo de notícia ou relatório | 5 | 5 mil | 6,1 |
| Vídeo de 8s sem fala (frase na tela, texto na legenda) | 14 | 5 mil | 1,9 |
| Esquete de humor | 1 | 12 mil | 0,5 |

- **O que mais alcança não é do nicho.** Os dois maiores da semana são sobre jogos de console rodando no PC (464 mil e 288 mil). Na legenda do maior ele vira o assunto para negócio: *"A pessoa comenta por acesso, não por explicação, e isso serve pra qualquer negócio"*. O vídeo pesca o público amplo; a legenda fala com o empresário.
- **O que mais converte é o que fala com o dono.** O método para negócio tem a menor audiência entre os falados, e a maior taxa de comentário (35,8 por mil). Dois vídeos só: é um sinal, não uma regra.
- **Picos de fora da janela** (03 a 06/10): 232 mil (*"Esse modelo grátis acabou de matar o Claude Code e o Codex"*), 183 mil (OpenAI e Claude juntos) e 114 mil (modelo gigante num notebook sem placa de vídeo). Os três são **ferramenta que saiu**, com abertura de choque. É o teto desse formato.
- **Os vídeos de 8s sem fala** (ele andando com o notebook, uma frase na tela, o conteúdo inteiro na legenda) são 14 dos 50 e quase não geram conversa (1,9 por mil). Servem para manter o volume.

## 3. O esqueleto do vídeo de ferramenta (o formato principal)

| Tempo | Etapa | Como ele faz (literal) |
|---|---|---|
| 0–5s | **Choque com a novidade** | *"Alguém soltou uma ferramenta no GitHub que quebra qualquer aplicativo"* · *"Esse modelo grátis acabou de matar o Claude Code"* · *"Eu sinceramente não sei como isso está disponível publicamente"* · *"Eu vou deletar esse vídeo em 24 horas"* |
| 5–15s | **Nome e o que faz** | *"Se chama Founder Skill e é totalmente de graça"* |
| 15–35s | **As partes, uma por frase** | *"Uma faz o papel de conselho… outra é o diretor de marketing… e uma é o CFO"* |
| ~35s | **"A parte mais louca"** | o detalhe que vira o vídeo (*"Mas a parte mais louca é a skill de consumidor"*) |
| 35–45s | **O ganho para quem tem negócio** | *"Em vez do seu negócio quebrar depois de gastar milhares, você tem um plano antes de lançar"* |
| fim | **"Comenta o código da legenda"** | o link e um guia vão para o direct |

A **legenda** é a segunda metade do vídeo: corrige o exagero da fala com número e limite (*"o próprio repositório avisa que comprador simulado tende a concordar, então a taxa de compra do painel é um teto"*) e lista o que vai no material.

## 4. Os formatos, por número

Tabela completa no Anexo A. Em resumo: **ferramenta que saiu** é o formato da casa (18 de 50, 9,9 mil comentários na semana); **games** é pesca de alcance; **vídeo de 8s sem fala** é volume; **método para negócio** é o que mais conversa.

## 5. Como ele grava (folhas de contato dos 8 maiores) — 14/10/2026

**Fonte:** `tools/roteiros/work/estudo/fabianocarvalhojr/folhas/` + a folha do reel que o Vitor mandou (`DeeqaAmAf9V`).

| Elemento | O que ele faz |
|---|---|
| Cenário | sala escura com luz quente, ar-condicionado na parede, sempre o mesmo. Camiseta preta. **Microfone de podcast no quadro**, com luz verde |
| Enquadramento | frontal, do peito para cima, olhando para a lente |
| Tela | **ele em cima, a tela embaixo** (repositório, terminal, página do GitHub), ou ele recortado sobre o print (tweet, vídeo do jogo) |
| Gancho na tela | caixa branca com texto preto no topo, estilo post de rede (*"Esse repositório do GitHub tem… mais de 280 agentes de IA TRABALHANDO PRA VOCÊ 24/7"*), ou selo vermelho *"NOTÍCIA URGENTE"* |
| Legenda | blocos curtos na caixa branca; fecho fixo *"Comenta o código da legenda que eu te mando"* |
| Vídeo de 8s | outro cenário (sala clara), ele de corpo inteiro fazendo algo (abrindo o notebook), uma frase na tela, sem fala |

**Dois níveis de edição:**
- **O barato, na maioria:** uma tomada + a tela embaixo + caixa de gancho. Dá para fazer 7 por dia.
- **O produzido, em alguns** (o do Sam Altman, o da Founder Skill): inserção a cada 2 ou 3 segundos, ilustração própria em pixel art com mascote, contador animado (*"400.000"*), título em serifa laranja (*"Número 1"*), tela dividida com etiqueta da palavra falada. Caro; não é o que sustenta o volume.

## 6. Linguagem: o que deixa natural

- **Aberturas de choque prontas,** quase todas no padrão dos perfis gringos de IA: *"Alguém acabou de soltar…"*, *"acabou de matar…"*, *"Notícia urgente"*, *"Eu vou deletar esse vídeo em 24 horas"*, *"não sei como isso está disponível publicamente"*.
- **Interjeição de espanto:** *"Massa, né?"*, *"Massa demais"*, *"insana"*, *"a parte mais louca"*.
- **Nome próprio e número em quase toda frase:** repositório, estrelas, parâmetros, empresa.
- **Fala curta e exagerada; a legenda corrige.** O vídeo promete (*"tirar o emprego de 280 pessoas"*); a legenda põe o limite (*"instalar os 200 é o mesmo que não instalar nenhum"*).

## 7. O que levar para o Vitor

1. **A prova de que 7 a 10 por dia é possível com o processo que ele quer:** concorrente puxado a cada dois dias → agente lista os temas ainda não cobertos → roteiro → gravação. É o `noticias.py` + `pautas.py` + cardápio, ligados.
2. **Um pedido de comentário em todo vídeo, com algo útil para entregar no direct** (guia, lista, prompt pronto), e um código por post para saber de onde veio cada conversa. Hoje o Vitor não tem nenhum funil no Reel.
3. **A legenda como a parte séria do vídeo:** o vídeo engancha; a legenda dá o número, a fonte e o limite. Combina com a regra de fonte do Vitor.
4. **O método para negócio** (*"o Claude vai destruir a sua ideia antes de você perder 6 meses"*) é o formato dele mais próximo do eixo do Vitor e o que mais conversa. Entra como variante do molde de Negócio ou de Regra.
5. **O formato de ferramenta que saiu** serve ao Bastidor (testar a ferramenta na tela, como no *Chegue atrasado*), mas não como linha principal: é o território dele e de dezenas de perfis.

## O que não copiar

- **O volume de novidade de ferramenta como identidade.** Ele já ocupa esse lugar, com 254 mil seguidores e produto (Lasy) para vender junto. O Vitor entraria como cópia menor.
- **Abertura exagerada** (*"matou o Claude Code"*, *"vou deletar em 24 horas"*): funciona para alcance, mas é o contrário da certeza serena da marca (Arquiteto).
- **Pescar com assunto fora do nicho** (games): traz número e público errado.
- **Vídeo de 8s sem fala:** mantém volume, quase não gera conversa.

## 8. Leitura de concorrência: onde ele está e onde fica a brecha

| | Fabiano | Vitor |
|---|---|---|
| Promessa | *"5x menos humanos, 10x mais faturamento"* | Negócio AI Native: a empresa que faz, não a que compra |
| Assunto | a ferramenta nova (o quê) | o dono e a decisão (o porquê e o que muda) |
| Tom | espanto, urgência, novidade | certeza serena, filosofia, história |
| Produto | plataforma (Lasy) + curso por assinatura (R$ 147/mês) | ainda em definição |
| Prova | números das ferramentas e da própria plataforma | as obras (CRM, agentes, editor de vídeo) |

**A brecha:** ele fala de ferramenta para quem já quer ferramenta. O dono que se sente atrasado, que é o herói do Vitor, não sabe qual ferramenta quer e se cansa de novidade. O Vitor fala com esse dono pelo lado da decisão e da história (o *Rei do gelo*, o *Chegue atrasado*), terreno que o Fabiano não ocupa.

**Limites do que foi visto:** a página da aula gratuita (`aula.vibehub.academy`) não abriu para leitura; os números da Vibehub e da Lasy são autodeclarados; o direct automático e o uso do código não foram vistos por dentro.

<!-- ANEXOS · gerado por tools/roteiros/estudo_anexos.py · não editar à mão daqui para baixo -->

---

## Anexo A — mediana por formato

Cada roteiro contado uma vez (repostagens fora). *Testes* = abaixo de 500 views.

| Formato | Vídeos | Mediana de views | Teto | Duração mediana | Testes reprovados |
|---|---|---|---|---|---|
| Games / emulação (fora do nicho) | 4 | 178.993 | 463.901 | 23s | 0 |
| Ferramenta ou repositório grátis que saiu | 18 | 16.055 | 45.733 | 43s | 0 |
| Esquete de humor | 1 | 11.657 | 11.657 | 31s | 0 |
| Método para negócio (agentes / prompt) | 2 | 9.049 | 9.529 | 80s | 0 |
| Tutorial na tela | 6 | 6.188 | 27.000 | 71s | 0 |
| Vídeo de 8s sem fala (frase na tela, texto na legenda) | 14 | 5.039 | 31.013 | 8s | 0 |
| Resumo de notícia ou relatório | 5 | 4.874 | 8.471 | 107s | 0 |

## Anexo B — os vídeos, com a abertura literal

Ordenados por views. 🔁 = repostagem · 🧪 = teste reprovado · ❤ -1 = curtidas ocultas.

| Views | ❤ | 💬 | Data | Dur. | Formato | Gancho (tipo) | Fecho | Abertura literal |
|---|---|---|---|---|---|---|---|---|
| [463.901](https://www.instagram.com/reel/DeVUzVGle0L/) | 22.307 | 8.990 | 2026-10-11 | 20s | Games / emulação (fora do nicho) | 'Notícia urgente, a situação do desbloqueio de todos os jogos piorou.' | comente "FYLXR" → o setup pra montar a lista do seu negócio com comentário que vira dire | Notícia urgente, a situação do desbloqueio de todos os jogos piorou. Agora dá pra jogar tipo a maioria dos COD, GTA V, Halo. E no Halo o pessoal já… |
| [287.736](https://www.instagram.com/reel/DeXlNtaFEx7/) | 15.730 | 4.924 | 2026-10-11 | 27s | Games / emulação (fora do nicho) | 'Abriram oficialmente o código de praticamente todos os consoles, como vocês podem ver aqui' | comente "U6WGR" → o caso conferido e o teste pra medir o que do seu software dá pra copi | Abriram oficialmente o código de praticamente todos os consoles, como vocês podem ver aqui. Mas antes de entrar nisso, o GTA V agora está totalmente… |
| [70.250](https://www.instagram.com/reel/DeVAQfjkjIh/) | 3.707 | 790 | 2026-10-10 | 41s | Games / emulação (fora do nicho) | 'O PS5 agora está sendo migrado para o PC e já está em 96% completo.' | comente "CGAHR" → o link do projeto e o que precisa pra testar | O PS5 agora está sendo migrado para o PC e já está em 96% completo. Mas tem um monte de desinformação por aí, então deixa eu te explicar o que isso… |
| [45.733](https://www.instagram.com/reel/DeUykdyATGu/) | 1.308 | 1.181 | 2026-10-10 | 46s | Ferramenta ou repositório grátis que saiu | 'O Sam Altman deve estar indignado agora porque alguém abriu o código dos agentes,' | comente "46PXR" → as 3 peças e a ordem certa de instalar | O Sam Altman deve estar indignado agora porque alguém abriu o código dos agentes, depois abriu o código da memória deles, depois abriu o código do… |
| [43.230](https://www.instagram.com/reel/DeXyvRyEeTi/) | 2.016 | 3.285 | 2026-10-11 | 51s | Ferramenta ou repositório grátis que saiu | 'Eu vou deletar esse vídeo em 24 horas porque a competição no mercado aumentou muito' | comente "D9TDR" → o link e o guia completo pra aplicar no seu negócio | Eu vou deletar esse vídeo em 24 horas porque a competição no mercado aumentou muito e eu não quero deixar esse repositório na mão de todo mundo. Esse… |
| [37.273](https://www.instagram.com/reel/DeZgxHciqye/) | 1.387 | 221 | 2026-10-12 | 20s | Games / emulação (fora do nicho) | 'O projeto NPS5 agora está 96% completo.' | comente "XDKYR" → o método do projeto aplicado ao sistema velho da sua empresa | O projeto NPS5 agora está 96% completo. E o NPS5 não é um emulador. É um projeto que os devs criaram para fazer jogo de PS5 rodar nativo no seu PC.… |
| [35.431](https://www.instagram.com/reel/DeUeAmbDOMH/) | 1.090 | 662 | 2026-10-10 | 27s | Ferramenta ou repositório grátis que saiu | 'Alguém soltou uma ferramenta no GitHub que quebra qualquer aplicativo' | comente "ATJGR" → o link do repositório e o guia completo de uso | Alguém soltou uma ferramenta no GitHub que quebra qualquer aplicativo e te entrega ele como código em Python. E esse é o Mimic. A ideia é simples,… |
| [31.013](https://www.instagram.com/reel/DeZ1KZCiPDR/) | 134 | 12 | 2026-10-12 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) 'Um vídeo com 6,9 milhões de visualizações disse que o PS5 está 96% pronto pra rodar no PC,…' | comente "23LVH" → o que os 96% medem de verdade, o número que ninguém citou e o método p | E… |
| [28.971](https://www.instagram.com/reel/DeVOCSPAtll/) | 985 | 412 | 2026-10-10 | 90s | Ferramenta ou repositório grátis que saiu | 'A China acabou de soltar a IA de código aberto mais rápida do mundo e você consegue baixar' | comente "GUENR" → os 2 lançamentos da semana que mudam rotina, com o setup dos dois, | A China acabou de soltar a IA de código aberto mais rápida do mundo e você consegue baixar e rodar de graça. E essa ferramenta nova Open Source deixa… |
| [27.000](https://www.instagram.com/reel/DeZ8HfSAWxK/) | 737 | 340 | 2026-10-12 | 48s | Tutorial na tela | 'Cloud, vai no Cloud, personalizar, clica personalizar, conectores, clica em conectores, ad' | comente "9GELR" → o passo a passo do conector | Cloud, vai no Cloud, personalizar, clica personalizar, conectores, clica em conectores, adicionar conector personalizado, conector personalizado, aba… |
| [26.257](https://www.instagram.com/reel/DechDEGCfcs/) | 615 | 499 | 2026-10-13 | 48s | Ferramenta ou repositório grátis que saiu | 'O Cloud agora consegue prever o quão viral o seu Rio vai ser antes mesmo de você postar.' | comente "UMYFR" → o passo a passo pra rodar isso nos seus vídeos | O Cloud agora consegue prever o quão viral o seu Rio vai ser antes mesmo de você postar. Se chama Virality Predictor. E tá dentro do Riggs Field, é… |
| [22.719](https://www.instagram.com/reel/DecFlAqgsl4/) | 647 | 890 | 2026-10-13 | 53s | Ferramenta ou repositório grátis que saiu | 'Essa atualização nova da meta está absolutamente insana.' | comente "QVJER" → o conector e o fluxo completo de montagem | Essa atualização nova da meta está absolutamente insana. Agora você pode conectar o MCP da meta direto no Cloud. E depois conecta o MCP do Riggs… |
| [21.487](https://www.instagram.com/reel/DeSpOVxlde4/) | 536 | 389 | 2026-10-09 | 49s | Ferramenta ou repositório grátis que saiu | 'Alguém acabou de soltar uma versão gratuita e de código aberto dos DOTS da OpenAI e ela já' | comente "RQHWR" → o link e o guia completo de uso | Alguém acabou de soltar uma versão gratuita e de código aberto dos DOTS da OpenAI e ela já está no ar agora. Já passou de 4 mil estrelas no GitHub e… |
| [18.871](https://www.instagram.com/reel/DeSUphJD8EP/) | 422 | 141 | 2026-10-09 | 30s | Ferramenta ou repositório grátis que saiu | 'O CloudFarm roda agentes do CloudCode a noite inteira sem comer o seu limite semanal.' | comente "MMTXR" → o link do repositório e o guia completo de uso | O CloudFarm roda agentes do CloudCode a noite inteira sem comer o seu limite semanal. É uma fazenda para os seus agentes de programação com IA. Roda… |
| [16.164](https://www.instagram.com/reel/DePv3aOj1rG/) | 405 | 215 | 2026-10-08 | 31s | Ferramenta ou repositório grátis que saiu | 'Agora você pode fazer seu próprio SEO sem entregar seus dados para ninguém.' | comente "GCXGR" → o acesso e o guia completo de uso | Agora você pode fazer seu próprio SEO sem entregar seus dados para ninguém. Se chama RankMeFast, uma auditoria roda 26 verificações no seu site e… |
| [15.946](https://www.instagram.com/reel/DecMds_knnN/) | 463 | 180 | 2026-10-13 | 32s | Ferramenta ou repositório grátis que saiu | 'O Coco é o companheiro de mesa de trabalho que transforma a sua borda da tela num centro d' | comente "YTTKR" → o link e o passo a passo completo | O Coco é o companheiro de mesa de trabalho que transforma a sua borda da tela num centro de controle ao vivo para os seus agentes de ar. Ele resolve… |
| [14.562](https://www.instagram.com/reel/DedFCIPPtO-/) | 157 | 9 | 2026-10-14 | 11s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) 'isso é revolucionário galera 🔥 #claude #vibecoding…' | sem pedido de comentário | Obrigado por… |
| [14.470](https://www.instagram.com/reel/DeaC4mTgMup/) | 556 | 413 | 2026-10-12 | 48s | Ferramenta ou repositório grátis que saiu | 'Eu sinceramente não sei como isso está disponível publicamente.' | comente "43FWR" → o link do repositório e o guia completo de uso | Eu sinceramente não sei como isso está disponível publicamente. Isso literalmente parece uma ferramenta ilegal. Chama Gods Eye e te dá uma visão em… |
| [13.331](https://www.instagram.com/reel/DeW7_HYFp0N/) | 431 | 575 | 2026-10-11 | 41s | Ferramenta ou repositório grátis que saiu | 'Essa ferramenta de IA gratuita transforma o seu Cloud Code literalmente num estúdio de pro' | comente "MWXCR" → o link e o guia completo de uso | Essa ferramenta de IA gratuita transforma o seu Cloud Code literalmente num estúdio de produção completo e é totalmente gratuita. Se chama… |
| [11.657](https://www.instagram.com/reel/DeTCDkLR-HM/) | 98 | 6 | 2026-10-10 | 31s | Esquete de humor | 'Você vendeu os dados da nossa empresa?' | sem pedido de comentário | Você vendeu os dados da nossa empresa? Da empresa não. Dos nossos clientes. Nossos clientes são hospitais. Você sabe o quanto isso é sensível? Os… |
| [10.552](https://www.instagram.com/reel/DeaXmSVD5jm/) | 326 | 691 | 2026-10-12 | 65s | Tutorial na tela | 'Olha como você pode transformar um áudio com a sua voz em uma máquina de conteúdo.' | comente "HYGNR" → as skills e a ordem de montagem completa | Olha como você pode transformar um áudio com a sua voz em uma máquina de conteúdo. A maioria dos criadores não percebe isso, mas você pode falar por… |
| [10.286](https://www.instagram.com/reel/DeUXJthDSZW/) | 278 | 238 | 2026-10-10 | 36s | Ferramenta ou repositório grátis que saiu | 'O Claudio acabou de fazer o que o Notebook LM não conseguiu,' | comente "6M9LR" → o guia completo pra transformar artigo em vídeo explicativo | O Claudio acabou de fazer o que o Notebook LM não conseguiu, transformar qualquer tema ou artigo num vídeo explicativo mesmo, não só apresentações… |
| [9.973](https://www.instagram.com/reel/DePbR71gVhh/) | 212 | 173 | 2026-10-08 | 36s | Ferramenta ou repositório grátis que saiu | 'Alguém acabou de lançar uma versão gratuita de código aberto do Jev e ela é bem mais rápid' | comente "4A4NR" → a instalação e o guia pra ajustar o modelo pro seu caso | Alguém acabou de lançar uma versão gratuita de código aberto do Jev e ela é bem mais rápida e mais barata. Se chama Layer e é um modelo classificador… |
| [9.529](https://www.instagram.com/reel/DeSN2nhFZr3/) | 267 | 326 | 2026-10-09 | 111s | Método para negócio (agentes / prompt) | 'A Antropic disse que talvez você não precise construir agentes de IA nenhum, e eu concordo' | comente "JPNJR" → o modelo das páginas e o guia completo | A Antropic disse que talvez você não precise construir agentes de IA nenhum, e eu concordo. A gente não deveria estar construindo um agente separado… |
| [9.489](https://www.instagram.com/reel/DeU5drplX16/) | 175 | 131 | 2026-10-10 | 28s | Ferramenta ou repositório grátis que saiu | 'Alguém acabou de criar um apresentador de IA para a sua empresa e essencialmente ele faz t' | comente "JFVTR" → as fontes e a rotina pra achar ferramenta nova antes de virar notícia | Alguém acabou de criar um apresentador de IA para a sua empresa e essencialmente ele faz tudo. De apresentador de VSL e muito mais, demonstrando para… |
| [8.659](https://www.instagram.com/reel/DeZun4GlOwf/) | 201 | 202 | 2026-10-12 | 48s | Ferramenta ou repositório grátis que saiu | 'A Cloudflare acabou de liberar uma skill de IA que encontra falhas de segurança no seu apl' | comente "UJLPR" → a skill e o passo a passo de instalação | A Cloudflare acabou de liberar uma skill de IA que encontra falhas de segurança no seu aplicativo feito com o Vibe Coding e é totalmente gratuita.… |
| [8.569](https://www.instagram.com/reel/DeZnvliipPG/) | 189 | 320 | 2026-10-12 | 49s | Método para negócio (agentes / prompt) | 'O Claude vai destruir a sua ideia de negócio antes de você desperdiçar 6 meses construindo' | comente "HNUMR" → os 4 agentes prontos do conselho | O Claude vai destruir a sua ideia de negócio antes de você desperdiçar 6 meses construindo ela. E aqui vai como? Monta um conselho do Claude com 4… |
| [8.471](https://www.instagram.com/reel/DeXeKnvAU-6/) | 168 | 131 | 2026-10-11 | 55s | Resumo de notícia ou relatório | 'A maior parte das animações que eu tenho visto não foram criadas por designers humanos.' | comente "NJMER" → o link da skill e o guia pra fazer motion design no Claude | A maior parte das animações que eu tenho visto não foram criadas por designers humanos. E a real é que a IA está ficando muito boa nisso. A galera… |
| [7.481](https://www.instagram.com/reel/DeZL-L2CNLl/) | 51 | 63 | 2026-10-12 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) '1 ano de Claude Team de graça e 1.000 dólares em crédito de API, perto de R$ 5 mil, é o qu…' | comente "G2U3H" → quem se encaixa nas regras, o passo a passo do pedido e o plano pra nã | Amém.… |
| [6.686](https://www.instagram.com/reel/DeRyXoigJdG/) | 124 | 41 | 2026-10-09 | 130s | Resumo de notícia ou relatório | 'A OpenAI acabou de soltar 25 lançamentos novos e aqui estão todos eles em 90 segundos.' | comente "DG3MR" → os 4 lançamentos que mexem na conta da sua empresa e o filtro pro rest | A OpenAI acabou de soltar 25 lançamentos novos e aqui estão todos eles em 90 segundos. Número 1 são os DOTS, são agentes de IA que moram no chat EPT.… |
| [6.536](https://www.instagram.com/reel/DeR5QvUlYL2/) | 123 | 214 | 2026-10-09 | 26s | Ferramenta ou repositório grátis que saiu | 'Alguém acabou de subir uma aula completa de 12 horas sobre IA Agêntica no YouTube.' | comente "UVGTR" → o método pra tirar resultado de aula longa sem assistir do começo ao f | Alguém acabou de subir uma aula completa de 12 horas sobre IA Agêntica no YouTube. E a melhor parte não é só uma visão geral básica. Ela te ensina a… |
| [6.440](https://www.instagram.com/reel/DecnsSVlBIC/) | 129 | 120 | 2026-10-13 | 42s | Tutorial na tela | '4 dicas para te diferenciar na criação de vídeos com o Cloud.' | comente "AEKXR" → a lista de projetos e o arquivo de marca pronto | 4 dicas para te diferenciar na criação de vídeos com o Cloud. Número 1, efeitos open source. O seu vídeo é o Cloud, então ele pode pegar emprestado… |
| [5.936](https://www.instagram.com/reel/DeXC6KXDM_7/) | 118 | 65 | 2026-10-11 | 77s | Tutorial na tela | 'Mais de 1.600 de vocês me mandaram mensagem sobre deixar sua IA rolar o feed' | comente "TQWQR" → o guia completo pra montar a sua base de conhecimento | Mais de 1.600 de vocês me mandaram mensagem sobre deixar sua IA rolar o feed para construir skills a partir dos seus Reels salvos. E a maioria de… |
| [5.628](https://www.instagram.com/reel/DeRdrPODX9i/) | 41 | 22 | 2026-10-09 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) '1 modelo aberto gera vídeo em 4K nativo, a até 50 quadros por segundo e até 20 segundos po…' | comente "NHGBH" → o requisito por tipo de máquina, a instalação e a conta que decide ent | E… |
| [5.419](https://www.instagram.com/reel/DeO4xRED4hL/) | 34 | 10 | 2026-10-08 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) '1 comando sobe na sua máquina um raspador do Google Maps que devolve nome, endereço, telef…' | comente "6D4RH" → a instalação com Docker, o limite técnico e a separação entre coletar  | Música… |
| [5.210](https://www.instagram.com/reel/DeXQ6_rk5Jq/) | 18 | 21 | 2026-10-11 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) '1 app grátis e aberto te coloca pra conversar em outro idioma com uma voz que corrige na h…' | comente "3UMUH" → a instalação nos dois sistemas, a estimativa de custo por conversa e a | Amém.… |
| [5.106](https://www.instagram.com/reel/DeWnNSGAQ7q/) | 27 | 10 | 2026-10-11 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) '5 perguntas derrubam quase todo prazo de lei que circula errado, aquele "a partir de tal d…' | comente "FWQ9H" → o método completo, onde consultar no Brasil e nos Estados Unidos e os  | E… |
| [4.973](https://www.instagram.com/reel/DebwwavCG_e/) | 25 | 8 | 2026-10-13 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) 'Agente que trabalha sozinho 24 horas por dia agora existe dentro do ChatGPT. A OpenAI lanç…' | comente "ZAF3H" → quais planos liberam, como escolher a primeira tarefa que roda sozinha | E… |
| [4.874](https://www.instagram.com/reel/DeQEeRiFRH5/) | 76 | 27 | 2026-10-08 | 152s | Resumo de notícia ou relatório | 'Como 700 agentes da OpenAI acabaram hackeando o Hugging Face?' | comente "366FR" → a linha do tempo conferida e os 7 prompts pra blindar suas metas e aut | Como 700 agentes da OpenAI acabaram hackeando o Hugging Face? A OpenAI acabou de publicar um relatório completo, ele é muito louco. Em julho, ela… |
| [4.819](https://www.instagram.com/reel/DePSUPXDKnW/) | 103 | 162 | 2026-10-08 | 80s | Tutorial na tela | 'Você devia deixar a IA ficar rolando o seu feed.' | comente "C9KVR" → o método e os 8 prompts pra transformar seus salvos em instrução pra I | Você devia deixar a IA ficar rolando o seu feed. E eu estou falando sério. Eu tinha visto um meme sobre deixar o agente de IA rolar o feed como… |
| [4.735](https://www.instagram.com/reel/DeUrkxaCi-i/) | 16 | 1 | 2026-10-10 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) 'Vaga que pede IA cresceu 69% em um ano, enquanto o mercado inteiro cresceu 9%, quase 8 vez…' | comente "RFF8H" → os dois trilhos do mercado, como saber em qual a sua função está e o q | E… |
| [4.532](https://www.instagram.com/reel/DeUCdtykdfC/) | 34 | 36 | 2026-10-10 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) '13 skills grátis pro Claude cuidam do trabalho chato do seu Instagram: escrevem o Reels, r…' | comente "TAJVH" → as skills com o pedido pronto, as fórmulas de gancho em português e a  | Música… |
| [4.462](https://www.instagram.com/reel/DePiCY6jcsG/) | 23 | 3 | 2026-10-08 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) 'Peça pro mesmo modelo escrever e depois revisar o próprio código, e ele aprova, pelo mesmo…' | comente "3YT6H" → a instalação, as quatro fases e como levar a revisão cruzada pra propo | E… |
| [4.344](https://www.instagram.com/reel/DeSG2_SlYm5/) | 23 | 4 | 2026-10-09 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) '10 anúncios gerados de uma vez, cada um salvo do lado do prompt exato que criou ele, e um…' | comente "UDJMH" → a instalação, a configuração do teto e como usar o registro de prompt  | Música… |
| [3.599](https://www.instagram.com/reel/DeeqaAmAf9V/) | 80 | 92 | 2026-10-14 | 53s | Ferramenta ou repositório grátis que saiu | 'Agora dá pra testar negócios inteiros dentro do Cloud sem gastar um real.' | comente "EHYMR" → o link e o guia completo da Founder Skill | Agora dá pra testar negócios inteiros dentro do Cloud sem gastar um real. Chama Founderskill e é totalmente de graça e não é só uma skill, são 11.… |
| [3.340](https://www.instagram.com/reel/DeXXWI2geYo/) | 47 | 11 | 2026-10-11 | 107s | Resumo de notícia ou relatório | 'A gente analisou mais de mil artigos de IA para ver para onde a pesquisa de IA foi esse mê' | comente "RKCJR" → o método pra pegar resposta de IA que parece certa e não é | A gente analisou mais de mil artigos de IA para ver para onde a pesquisa de IA foi esse mês. E aqui estão os cinco movimentos de pesquisa principais… |
| [3.171](https://www.instagram.com/reel/DecZ9qmDnPw/) | 23 | 11 | 2026-10-13 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) 'Existe uma nota de 0 a 100 pra quanto a IA entende o seu site, e ela é grátis. É o Is Agen…' | comente "8ALXH" → como rodar a checagem no seu site, como a nota é formada e o que corri | E… |
| [2.923](https://www.instagram.com/reel/DeeVlHIFsiM/) | 22 | 18 | 2026-10-14 | 8s | Vídeo de 8s sem fala (frase na tela, texto na legenda) | (legenda) 'O Claude Code aceita mod agora, desde a versão 2.1.287 do começo de outubro. Mod é um peda…' | comente "TKQ4H" → como instalar, o que um mod consegue alcançar na sua máquina e a checa | E… |
| [2.633](https://www.instagram.com/reel/DePo9ClinbW/) | 33 | 26 | 2026-10-08 | 101s | Resumo de notícia ou relatório | 'O Sam Altman disse, estou convencido de que a destruição dos empregos nas próximas duas dé' | comente "FUUAR" → o guia completo pra montar seu primeiro agente sempre ligado | O Sam Altman disse, estou convencido de que a destruição dos empregos nas próximas duas décadas vai ser massiva. E nessa mesma semana a OpenAI acabou… |
| [1.783](https://www.instagram.com/reel/DeexJGQjIQQ/) | 55 | 64 | 2026-10-14 | 90s | Tutorial na tela | 'O maior problema de usar IA para fazer site é que mesmo se você der ótimas referências par' | comente "DPFLR" → a skill e o guia completo de uso | O maior problema de usar IA para fazer site é que mesmo se você der ótimas referências para ela, o resultado ainda sai com cara de IA. Antes era… |

---

## Anexo C — roteiros completos dos maiores

Transcrição automática (Whisper), uma frase por linha para ler o ritmo da fala. Pode ter palavra trocada ou acento faltando; o conteúdo é fiel.

### 463.901 views · 20s · 2026-10-11 · [link](https://www.instagram.com/reel/DeVUzVGle0L/)

```
Notícia urgente, a situação do desbloqueio de todos os jogos piorou.
Agora dá pra jogar tipo a maioria dos COD, GTA V, Halo.
E no Halo o pessoal já tá começando a ver salas de 128 jogadores lotadas e o pessoal tá jogando de verdade.
Multiplayer com microfone aberto e ainda muito mais jogos, galera.
Comenta o código que tá aqui na legenda que eu te mando e podem esperar muito mais jogos saindo no futuro próximo.
```

### 287.736 views · 27s · 2026-10-11 · [link](https://www.instagram.com/reel/DeXlNtaFEx7/)

```
Abriram oficialmente o código de praticamente todos os consoles, como vocês podem ver aqui.
Mas antes de entrar nisso, o GTA V agora está totalmente jogável na web.
O pessoal desbloqueou oficialmente os seus jogos favoritos e agora dá para jogar tudo na web.
E eles usaram o IA para fazer isso.
O pessoal está começando a abrir o código das bibliotecas inteiras dos jogos.
E a gente está vivendo num mundo onde tudo vai ser código aberto, replicado, desmontado por uma engenharia reversa e criado num único notebook.
Se você quer o acesso e mais detalhes, comente o código da legenda que eu te mando no direct.
```

### 70.250 views · 41s · 2026-10-10 · [link](https://www.instagram.com/reel/DeVAQfjkjIh/)

```
O PS5 agora está sendo migrado para o PC e já está em 96% completo.
Mas tem um monte de desinformação por aí, então deixa eu te explicar o que isso significa e como agora você vai conseguir jogar jogo de PS5 diretamente no seu PC.
A primeira coisa que todo mundo está errando é dizer que é um emulador.
Não é um emulador.
É uma decomposição completa do PS5 e uma recompilação em executáveis de Windows e Linux.
Isso significa que o jogo agora está rodando nativo no seu computador.
Você não está fingindo ser um PS5.
Você está rodando o jogo no seu PC E como resultado o desempenho vai ser absurdamente melhor Vai rodar como um jogo normal de PC E a gente vai conseguir jogar basicamente Qualquer jogo de PS5 no PC nativo E está tudo nesse repositório aqui Se você quer saber como jogar, comenta o código da legenda que eu te mando no direct
```

### 45.733 views · 46s · 2026-10-10 · [link](https://www.instagram.com/reel/DeUykdyATGu/)

```
O Sam Altman deve estar indignado agora porque alguém abriu o código dos agentes, depois abriu o código da memória deles, depois abriu o código do gerente que roda todos eles e não tem como colocar de volta.
Número 1, Agency Agent.
230 especialistas de uma instalação.
Engenharia, design, venda, segurança.
Você para de fazer prompt e começa a delegar.
Número 2, Codebase Memory MCP.
Ele lê o seu repositório inteiro e transforma num grafo.
Cinco perguntas vão custar 3 mil tokens ao invés de 400 mil.
99% a menos.
O seu agente nunca mais esquece a sua base de código.
Número 3, Orca.
Esse é o que ninguém está usando.
Ele roda todos ao mesmo tempo.
Agentes em paralelo na sua própria assinatura.
Uma janela só.
Você para de olhar um chat e começa a olhar um time.
Agora, comenta o código da legenda que eu te mando os 3 links e um guia completo de uso.
```

### 43.230 views · 51s · 2026-10-11 · [link](https://www.instagram.com/reel/DeXyvRyEeTi/)

```
Eu vou deletar esse vídeo em 24 horas porque a competição no mercado aumentou muito e eu não quero deixar esse repositório na mão de todo mundo.
Esse repositório do GitHub tem mais de 280 agentes de IA que vão trabalhar para você 24 horas por dia, 7 dias por semana, até enquanto você dorme.
Massa, né?
Eu não sei se você entendeu, mas esses agentes agora podem tirar o emprego de 280 pessoas.
E por que eu estou falando isso?
Porque se você está pensando em abrir um negócio ou já está tocando o seu negócio, talvez você precisa de um sócio, de um co-founder, de um gerente de marketing, de um engenheiro de software, de funcionários diferentes para segmentos diferentes.
E todos esses funcionários, até mesmo o CEO e outros funcionários importantes, estão guardados dentro desses repositórios como agente de IA.
E é isso que você consegue ver na tela.
Massa demais, né?
Talvez se esse vídeo chegar a mil curtidas, eu mantenha ele, porque eu não quero ser uma pessoa egoísta, então talvez eu mantenha.
Mas se você quer acesso a esse repositório e um guia completo de uso para aplicar no seu negócio, comenta o código da legenda que eu te mando no direct.
```

### 37.273 views · 20s · 2026-10-12 · [link](https://www.instagram.com/reel/DeZgxHciqye/)

```
O projeto NPS5 agora está 96% completo.
E o NPS5 não é um emulador.
É um projeto que os devs criaram para fazer jogo de PS5 rodar nativo no seu PC.
Ele traduz o código do jogo direto na sua CPU.
E hoje tem exatamente 96,48% dos shaders de GPU do PS5.
É Playstation, pai.
Comenta o código da legenda que eu te mando no direct.
```

### 35.431 views · 27s · 2026-10-10 · [link](https://www.instagram.com/reel/DeUeAmbDOMH/)

```
Alguém soltou uma ferramenta no GitHub que quebra qualquer aplicativo e te entrega ele como código em Python.
E esse é o Mimic.
A ideia é simples, ele observa como o aplicativo funciona por dentro, captura as requisições dele e o Cláudio analisa e monta sozinho uma biblioteca em Python pronta.
Você só pega e roda por conta própria.
E olha que loucura, em poucos dias ele já tem mais de 700 estrelas.
E isso é a mágica que muita gente estava esperando.
Qualquer aplicativo vira seu código pessoal.
Quer o link do repositório e um guia completo de uso?
Comenta o código da legenda que eu te mando no direct.
```

### 28.971 views · 90s · 2026-10-10 · [link](https://www.instagram.com/reel/DeVOCSPAtll/)

```
A China acabou de soltar a IA de código aberto mais rápida do mundo e você consegue baixar e rodar de graça.
E essa ferramenta nova Open Source deixa agentes de IA rodarem qualquer tarefa no seu celular a partir de um único prompt.
E não é só isso.
Aqui tá tudo o que aconteceu em IA essa semana em 60 segundos.
Número 6, o Open Viking resolve o problema de memória dos agentes de IA.
É um banco de dados de contexto Open Source que dá ao agente um lugar só para guardar conhecimento, memórias do usuário e experiência reutilizável.
Número 5, o Google abriu o código da Artemis que transforma prompts em automações reais em celular.
Ele se conecta direto no Codex, no Codecode ou no Antigravity por MCP e captura logs e captura de tela enquanto trabalha.
Número 4, a Prisma ML lançou o Ternary Bonsai 2, um modelo de raciocínio de 27 bilhões de parâmetros com contexto de 272 mil tokens.
E a compressão Ternary encolhe o suficiente para rodar na sua própria máquina com programação matemática, tool call e entendimento de imagem.
Número 3, a AWS abriu o código do PizzaBot, uma caixa de entrada para agentes de IA em segundo plano.
Seus agentes continuam rodando enquanto você faz outra coisa e tudo que eles terminam ou precisa que você aprove aparece como e-mail.
Funciona em Mac, Windows e Linux.
Número 2, a CAI soltou o GLM 5.3 Flash X.
Vem com 327 bilhões de parâmetros nativamente multimodal, 1 milhão de tokens de janela de contexto, 200 tokens por segundo e é gratuito e privado no seu próprio hardware.
E número 1, o Unslosh Studio agora te deixa treinar mais de 500 modelos abertos num Google Collab gratuito.
Sem código, é só escolher um modelo, subir os seus dados e apertar treinar, depois exportar e rodar localmente.
Quer dar uma olhada neles?
Comenta o código da legenda que eu te mando o link para testar todos.
```

### 27.000 views · 48s · 2026-10-12 · [link](https://www.instagram.com/reel/DeZ8HfSAWxK/)

```
Cloud, vai no Cloud, personalizar, clica personalizar, conectores, clica em conectores, adicionar conector personalizado, conector personalizado, aba nova, aba nova, vai rigsfield.ai barra mcp, rigsfield.ai barra mcp, tá aqui comigo ainda?
Copia link, copia o link, volta pro Cloud, volta, cola o link, cola o link, continuar, continuar, Digita o prompt no cloud Shorts infantis do YouTube Shorts infantis do YouTube Posta nos shorts do YouTube Imprimindo dinheiro, chega trabalho Dinheiro pelo celular Quer passo a passo do conector?
Comenta código da legenda que eu te mando
```

### 26.257 views · 48s · 2026-10-13 · [link](https://www.instagram.com/reel/DechDEGCfcs/)

```
O Cloud agora consegue prever o quão viral o seu Rio vai ser antes mesmo de você postar.
Se chama Virality Predictor.
E tá dentro do Riggs Field, é só conectar direto no Cloud Code.
Você dá ali 15 segundos de imagem e ele vai prever como o cérebro humano responde àquilo segundo a segundo.
E ele foi treinado com mais de mil horas de escaneamento cerebral.
Por exemplo, eu passei seis hooks diferentes no meu último Rio e ele deu a nota em cada um de 0 a 100.
E ele também te dá um gráfico de retenção prevista pra te mostrar exatamente onde as pessoas iriam embora.
Você pode conectar o Rig Spirits no Code Code e rodar cada vídeo nele antes de postar e é totalmente gratuito O único problema é que ele não te diz o que está errado, ele só te diz quando as coisas dão errado Então eu fiz uma skill gratuita que faz o resto Ela passa pelo rio, encontra os pontos mortos e te diz exatamente o que mudar Quer o passo a passo para rodar isso aí nos seus vídeos?
Comenta o código da legenda que eu te mando no direct
```

### Picos de fora da janela

#### 232.272 views · 45s · 2026-10-03 · [link](https://www.instagram.com/reel/DeC-mAXknYX/)

```
Esse modelo grátis acabou de matar o Cloud Code e o Codex.
A NVIDIA acabou de soltar o Nemotron 3 Ultra de código aberto completamente gratuito.
Um milhão de tokens de janela de contexto.
Tenha em mente, essa coisa roda cinco vezes mais rápido que qualquer outro modelo aberto que existe e eu vou te provar.
Eu dei um prompt pra ele construir uma landing page premium com objetos tridimensionais brilhantes.
Ele planejou, programou, testou, depurou tudo sozinho em minutos.
Nenhum humano tocou em uma linha sequer e essa é a parte que me pega.
E tá aqui como você vai usar.
Instala o OpenCode com uma linha no seu terminal Escolhe o Nemotron 3 Ultra da lista E é isso, você não precisa pagar mais pelo CodeCode nem pelo Codex E eu te prometo, depois que você testar isso, você não vai querer mais voltar atrás Se você quiser o setup completo e o guia de uso, comenta o código da legenda que eu te mando no direct
```

#### 183.234 views · 37s · 2026-10-05 · [link](https://www.instagram.com/reel/DeIV3XIE9cA/)

```
A Antropica acabou de conectar oficialmente o cloud com o chat GPT.
A partir de agora, você pode usar os dois modelos mais potentes trabalhando juntos.
Existe um plugin oficial da OpenAI que te permite botar todos os modos do chat GPT diretamente no seu cloud e fazer eles trabalharem juntos.
Funciona assim, um modelo constrói e o outro revisa.
Os dois encontram erros que nenhum teria encontrado separado.
E isso faz sentido porque os modelos já são péssimos revisando o próprio trabalho.
E esse é exatamente o problema que esse plugin resolve.
Assim, no fim, o que você tem são dois desenvolvedores sênior trabalhando em todos os seus projetos.
Se você quer o guia de configuração completo, comenta o código que está aqui na legenda que eu te mando no direct.
```

#### 114.357 views · 64s · 2026-10-06 · [link](https://www.instagram.com/reel/DeKD6UxH_2c/)

```
Alguém acabou de rodar um modelo de GA de 744 bilhões de parâmetros num notebook sem placa de vídeo.
Um desenvolvedor na Itália conseguiu isso com o GLM 5.2, um modelo aberto que bate os que você paga.
A proposta inteira da NVIDIA é que você precisa das placas deles pra uma coisa dessas.
E esse cara acabou de provar que não precisa.
O projeto se chama Colibri e funciona porque só uns 10 gigas do modelo estão realmente pensando a cada momento.
Então o Colibri mantém essa parte na sua RAM e transmite o resto direto do seu disco rígido conforme precisa.
Do mesmo jeito que a Netflix transmite filme em vez de te obrigar a baixar.
E rodar é mais fácil do que parece.
Você clona o repositório e roda em um arquivo de setup.
A coisa toda se constrói sozinha a partir daí.
A única parte pesada é o download do modelo que ocupa 370GB do seu disco.
Depois disso é só digitar KLE no chat e você já vai estar conversando com ele completamente offline.
Se você constrói aplicativos, digita KLE Serve e em vez disso ele vira uma endpoint da OpenAI.
Você muda uma linha no seu código e a sua conta de token vai a zero porque nada nunca sai da sua máquina.
Se você quer o link do GitHub com o guia completo de instalação, comenta o código da legenda que eu te mando no direct
```

