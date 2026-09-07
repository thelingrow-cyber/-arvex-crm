# Auditoria da página de captura — Desafio Ótica +100K

> **Data:** 07/09/2026 · **Arquivo auditado:** `index.html` (commit `bc5c283`, modelo minimalista)
> **Squad:** 📊 Cro (CRO Analyst) · ✍️ Cole (Copywriter) · 🖌️ Vera (Web Designer) · condução: 👑 Orion
> **Contexto do funil:** tráfego pago frio → página → grupo VIP de WhatsApp → sequência no grupo →
> live 22-24/09 → call com a Cindy (`sop-fluxo-vendas.md`, Fluxo 1 — Webinário)

---

## 0. Benchmark — o que fazem as páginas de captura que mais convertem hoje

Fontes consultadas em 07/09/2026 (links no fim do documento).

| Dado | Número | Consequência para nós |
|---|---|---|
| Conversão média de página de captura de webinário | **~22%** | É o piso, não a meta |
| Páginas bem otimizadas | **35-45%** | Existe teto alto — o formato não é o limitador |
| Formulário de 2 campos vs. formulário longo | **+34%** | Nosso zero-campo já ganha esse jogo |
| CTA claro e único | **+28%** de registro | Temos um CTA claro. Ponto forte |
| "Vagas limitadas" | +24% de urgência percebida | **Não aplicamos, de propósito** — ver §1.4 |
| Contador regressivo | +13% | **Não aplicamos, de propósito** — ver §1.4 |
| Anúncio em vídeo | +34% de registro | Vale para a mídia, não para a página |
| Diagnóstico do mercado | Abaixo de 20% = fricção ou message mismatch, **não falta de demanda** | Nosso 50% de perda é fricção, não público |

**O padrão estrutural das páginas de maior conversão nesse nicho** (webinário / lançamento de
infoproduto) é estável e curto:

1. Barra com **data e horário**
2. Headline com transformação específica
3. Subhead com o mecanismo
4. **O que você vai aprender / sair tendo** — 3 bullets
5. **Data, horário e formato explícitos** ("terça, 20h, ao vivo, online")
6. Prova mínima (autoridade ou caso)
7. CTA único e repetido
8. Rodapé com política de privacidade

Nossa página hoje entrega **1, 2, 3, 7** e meio de **5** (data sim, horário não). Faltam **4, 6, 8**.

---

## 1. 📊 Parecer do Cro — CRO Analyst

### 1.1 Score por elemento

| Elemento | Nota | Leitura |
|---|---|---|
| Topbar com a data | **8** | Melhorou muito. Data é urgência honesta. **Falta o horário** |
| Logo do evento | **8** | Ancora o nome, dá identidade de evento. Mantém |
| Eyebrow "Online e gratuito · para donos de ótica" | **7** | Qualifica público e remove risco percebido. Correto para tráfego frio |
| Headline | **8** | Benefício + mecanismo + prazo, sem prometer faturamento. Passa no A6 |
| Subhead | **6** | "Oferta especial" é o único motivo dado para entrar. É um motivo comercial, não um motivo de valor. Ver §2 |
| CTA (verde, verbo claro) | **8** | Bom contraste, bom verbo, largura cheia no mobile. **Sem ícone do WhatsApp** — perde o sinal de "1 clique, sem formulário" |
| Micro-CTA | **7** | "É no grupo que o desafio acontece" faz o trabalho certo: explica por que o grupo |
| Foto | **7** | Local, integrada com máscara. Não flutua (A5 ok) |
| **O que acontece no evento** | **0** | **Ausente.** A pessoa não sabe o que vai receber. É o buraco nº1 |
| **Horário** | **0** | **Ausente.** Data sem horário custa comparecimento e cria dúvida na hora de decidir |
| **Prova social** | **0** | **Ausente.** Objeção nº1 do ICP é cicatriz de mentoria |
| **Política de privacidade** | **0** | **Ausente.** Risco de reprovação do anúncio no Meta |
| Rodapé | **5** | Só copyright. Não trabalha |

### 1.2 Fricções, em ordem de gravidade

1. **A animação `reveal` voltou para a primeira dobra.** Logo, eyebrow, headline, subhead, CTA e
   foto começam com `opacity:0` e só aparecem quando o IntersectionObserver dispara. No 4G do
   interior isso atrasa exatamente o que precisa aparecer primeiro — e **se o JS falhar ou for
   bloqueado, a página fica em branco**. É o pior defeito técnico da página e custa 5 minutos.
2. **`og:image` com caminho relativo.** Quando alguém compartilha o link no WhatsApp — que neste
   funil é canal orgânico de verdade — o preview quebra. Precisa ser URL absoluta do domínio onde
   a página for publicada.
3. **Ninguém sabe o que vai acontecer nos 3 dias.** Sem os bullets de entrega, a decisão de entrar
   no grupo é feita só na confiança da headline.
4. **Sem horário.** "22, 23 e 24 de setembro" sem hora deixa a pessoa sem conseguir se programar,
   e programação é o que faz comparecer.
5. **Duas animações infinitas competindo** (o `dot` pulsando na topbar e o `pulse-glow` do botão).
   Movimento permanente em dois pontos divide a atenção em vez de dirigi-la.
6. **6 pesos da fonte Inter carregados** (400 a 900) para uma página que usa quatro. Custa
   render-blocking no 4G.

### 1.3 Hierarquia visual — o olhar vai para o CTA?

**Vai, e esse é o maior acerto da página.** Coluna única, centralizada, sem menu, sem link de fuga,
sem segunda coluna. O único elemento verde da página é o botão. A foto vem **depois** do CTA, o que
está certo: ela apoia, não disputa.

**Ressalva:** com a headline em `clamp(25px,6vw,38px)` e a logo do evento acima, em telas de 360px
de largura o CTA fica **no limite da primeira dobra**. Precisa de print de celular real para
confirmar — é exatamente o teste da heurística A2, e é o único item desta auditoria que eu não
consigo fechar sem o aparelho.

### 1.4 Urgência, escassez e prova — por que contrariamos o benchmark

O mercado diz que "vagas limitadas" dá +24% e contador dá +13%. **Mantenho a recomendação de não
usar nenhum dos dois**, e o motivo não é estético:

- Esses números vêm majoritariamente de webinário B2B americano, com público que não foi queimado.
- Nosso ICP tem cicatriz de mentoria documentada (`icp-dono-de-otica.md`) e **decide em dupla**.
  Pressão artificial dá ao cônjuge cético o argumento de graça: *"tá vendo, é golpe"*.
- Vaga limitada em grupo de WhatsApp gratuito é uma mentira verificável em dois segundos.

**A urgência que funciona aqui é a real:** a data. E ela fica mais forte com horário e com o
argumento de que a primeira aula não se repete.

**Prova: obrigatória.** É o item que mais separa nossa página do padrão de mercado, e o que o ICP
mais precisa. Uma linha de autoridade resolve 80% (ver §2).

### 1.5 Hipóteses de teste — impacto × facilidade

| # | Hipótese | Impacto | Facilidade | Veredito |
|---|---|---|---|---|
| 1 | **Tirar o `reveal` da primeira dobra** | Alto | Altíssima | **Não é teste. É correção. Fazer.** |
| 2 | **Nome + foto do grupo de WhatsApp** batendo com o evento | **Muito alto** | Alta | **Não é teste. Ver §4** |
| 3 | Adicionar horário + 3 bullets de entrega | Alto | Alta | Aplicar direto |
| 4 | Adicionar 1 linha de prova/autoridade | Alto | Alta | Aplicar direto |
| 5 | Ícone do WhatsApp dentro do botão | Médio | Altíssima | Aplicar direto |
| 6 | Página de uma dobra × página com bullets e prova | Alto | Média | **O único A/B que vale rodar** |
| 7 | CTA "Entrar no grupo VIP" × "Quero participar do desafio" | Médio | Alta | Só com volume |

**Ressalva honesta que repito da auditoria anterior:** com o tráfego de um lançamento de 3 dias,
provavelmente não haverá amostra para ler 6 e 7 com confiança. Aplicar 1-5 como correção e usar 6
como leitura qualitativa, não estatística.

---

## 2. ✍️ Parecer do Cole — Copywriter

### 2.1 O que está certo

A headline **passa no teste A6**: benefício (rota dos +100K), mecanismo (criar a estratégia em 3
dias, com ela), emoção (o "comigo" tira o medo de "é tudo online"). É curta, é tangível e — o mais
importante — **promete a direção, não o resultado**, que é o que o público queimado aceita.

O eyebrow faz o trabalho de qualificação sem prometer nada. O micro-CTA explica o grupo. Nada aqui
precisa mudar.

### 2.2 O furo de copy: a página não diz o que acontece

Entre a headline e o botão existe um vazio de argumento. A pessoa lê a promessa e é convidada a
entrar num grupo, sem nenhuma frase que responda **"o que eu vou receber?"**. Nas páginas que
convertem nesse nicho, esse espaço é ocupado por três bullets — e nós já temos o conteúdo deles
escrito e aprovado nos criativos:

> **Nos 3 dias você vai:**
> ✦ Montar comigo, ao vivo, uma campanha pronta pra rodar na sua base de clientes
> ✦ Sair sabendo o que fazer primeiro na sua loja — e por quê
> ✦ Aprender a fazer quem já comprou voltar a comprar, sem gastar mais em anúncio

Três linhas. Não transforma a página em página de vendas, e fecha o maior buraco de argumento.

### 2.3 A subhead está pagando o preço errado

> *"Entre no Grupo VIP e garanta acesso à oferta especial do desafio."*

**"Oferta especial" é a única razão que a página dá para entrar no grupo.** O problema: para um
público com cicatriz de mentoria, anunciar oferta no primeiro contato confirma a suspeita de que o
evento é a isca de uma venda. Estamos entregando a objeção de graça.

Três alternativas, do mais seguro ao mais ousado:

1. *"Entre no Grupo VIP — é lá que sai o link das aulas ao vivo e o material de cada dia."*
   → Motivo prático, verdadeiro, sem gatilho de venda.
2. *"Entre no Grupo VIP e receba o passo a passo de cada dia, ao vivo, com a Cindy."*
   → Reforça a autoridade presente, que é o antídoto do medo de "é tudo online".
3. *"3 dias, ao vivo e de graça. É no Grupo VIP que tudo acontece."*
   → A mais curta. Repete o formato e ancora o grupo como o lugar do evento.

**Recomendo a 1.** A oferta continua existindo — ela só é apresentada dentro do grupo, onde a
pessoa já entrou, e não na porta.

### 2.4 Três headlines alternativas (a atual continua sendo minha recomendação)

Entrego por dever de ofício, para você ter o comparativo — mas **a headline atual é a melhor das
quatro** e está fechada por você:

- **Ângulo mecanismo:** *"Em 3 dias, comigo, você monta a campanha que faz a sua própria base de clientes voltar a comprar."*
- **Ângulo dor:** *"A sua ótica não precisa de mais gente na rua. Precisa de uma estratégia. Vamos criar a sua em 3 dias."*
- **Ângulo prova:** *"A mesma ordem que colocou +R$ 9 mil em uma ótica de Curitiba em dez dias. Em 3 dias, ao vivo, comigo."*

O terceiro só vai ao ar depois da autorização da Cindy.

### 2.5 O que falta de copy, em uma linha cada

- **Horário:** *"Sempre às 20h"* (ou o horário real). Sem isso a data não vira compromisso.
- **Autoridade:** *"Com Cindy Batista, que já mentorou mais de 500 óticas no Brasil."* Uma linha
  abaixo da foto resolve a prova mínima sem virar seção.
- **Rodapé:** política de privacidade. Não é copy de conversão, é copy de sobrevivência do anúncio.

---

## 3. 🖌️ Parecer da Vera — Web Designer

### 3.1 O sistema visual está correto

Inter 900, dourado + navy + verde WhatsApp, fundo claro, coluna única centralizada. É o sistema da
casa, aplicado sem invenção. A foto está integrada com `mask-image` e degradê nas bordas — cumpre a
regra A5, não flutua, e a transição para o rodapé é suave. **Nada a refazer aqui.**

### 3.2 Wireframe atual × wireframe recomendado

```
HOJE                          RECOMENDADO
─────────────────────         ─────────────────────
topbar (data)                 topbar (data + horário)
logo do evento                logo do evento
eyebrow                       eyebrow
HEADLINE                      HEADLINE
subhead                       subhead (sem "oferta")
[ CTA ]                       [ ✆ CTA ]
micro-cta                     micro-cta
foto                          ─ 3 bullets de entrega ─
rodapé                        foto
                              linha de autoridade
                              rodapé + política
```

A página cresce cerca de uma dobra e meia. Continua sendo página curta — e continua sem nenhuma
seção que peça scroll antes do CTA.

### 3.3 Especificações do que entra

**Bullets de entrega** — entram **depois** do CTA e **antes** da foto. Por quê: quem já se
convenceu clica no primeiro botão sem precisar deles; quem hesitou encontra o argumento no caminho
e reencontra o CTA no fim.
- Lista simples, alinhada à esquerda dentro do container centralizado, `max-width: 30ch`
- Marcador `✦` em `var(--gold)`, texto em `var(--muted)`, `font-size: clamp(14px,3.8vw,16px)`
- `gap: 10px` entre itens, `margin: 26px auto`
- Sem card, sem borda, sem fundo. Bullet com caixa vira seção; nós queremos uma respiração

**Ícone do WhatsApp no botão** — SVG inline de 20px, `fill: currentColor`, antes do texto. O `gap:9px`
já está no CSS esperando por ele. Sinaliza "um clique, sem formulário" antes da pessoa ler o botão.

**Linha de autoridade** — abaixo da foto, centralizada, 13px, `var(--muted)`, com o nome em
`var(--text)` e peso 700. Uma linha, não um bloco.

**Segundo CTA:** **não.** Com uma dobra e meia, um botão só continua sendo o certo — a regra é um
CTA a cada dobra e meia. Se a página crescer mais que isso, aí sim.

### 3.4 Correções de implementação

1. **Remover `reveal` de tudo que está na primeira dobra.** Se quiser manter a animação, ela pode
   ficar só nos bullets e na linha de autoridade. O padrão seguro é o inverso do atual: conteúdo
   visível por padrão, animação como enfeite progressivo.
2. **Reduzir a fonte para 4 pesos** (400, 700, 800, 900) e adicionar `&display=swap` — já está.
3. **Uma animação infinita só.** Sugiro manter o `pulse-glow` do botão e tirar o pulso do `dot`, ou
   o contrário. Duas competem.
4. **`og:image` absoluto** assim que o domínio de publicação estiver definido.

---

## 4. 👑 O ponto cego — a página não termina na página

Todos os três pareceres apontam para o mesmo lugar quando se pergunta onde estão os 50% perdidos
(16 marcados, 8 entraram): **existe uma segunda página de captura neste funil, e ela é a tela do
WhatsApp.**

Quem clica não entra no grupo direto. Vê uma tela do WhatsApp com o **nome do grupo**, a **foto do
grupo**, a contagem de participantes e um botão "Entrar no grupo". Essa tela decide tanto quanto a
nossa — e não está sob nosso controle de código, mas está sob nosso controle de configuração.

**Antes de qualquer otimização de página, garantir:**
- Nome do grupo = **"Desafio Ótica +100K"** (não "Grupo VIP 3", não o nome do evento anterior)
- Foto do grupo = a logo/identidade do evento
- Descrição do grupo dizendo a data e o horário
- Primeira mensagem de boas-vindas já configurada, para quem entra não achar um grupo mudo

Se o link cair num grupo com nome genérico ou visual de outro evento, **a página pode estar
perfeita e a perda continuar em 50%**. Custa dez minutos e é o item de maior retorno da lista.

---

## 5. Veredito consolidado — o que fazer, em ordem

| # | Ação | Quem | Esforço | Por quê |
|---|---|---|---|---|
| 1 | Nome, foto e descrição do grupo de WhatsApp | Vitor/Cindy | 10 min | Maior retorno da lista. É onde a perda provavelmente mora |
| 2 | Tirar o `reveal` da primeira dobra | Dev | 5 min | Página em branco se o JS falhar; atraso no 4G |
| 3 | Horário do evento na topbar e na copy | Vitor confirma | 5 min | Data sem hora não vira compromisso |
| 4 | 3 bullets de entrega + linha de autoridade | Dev | 20 min | Fecha o maior buraco de argumento da página |
| 5 | Trocar a subhead da "oferta especial" | Dev | 2 min | Entrega a objeção de graça para um público queimado |
| 6 | Ícone do WhatsApp no botão | Dev | 5 min | Sinaliza "1 clique, sem formulário" |
| 7 | Política de privacidade no rodapé | Vitor | 10 min | Risco de reprovação do anúncio no Meta |
| 8 | `og:image` absoluto | Dev | 2 min | Preview quebrado no compartilhamento por WhatsApp |
| 9 | Print de celular real da primeira dobra | Vitor | 2 min | A2 — o único item que não fecha sem o aparelho |

**Não fazer:** contador regressivo, "vagas limitadas", FAQ, depoimento em vídeo, segunda dobra de
venda. O benchmark de mercado apoia os dois primeiros; o nosso ICP os reprova, e o ICP ganha.

**O que ainda bloqueia a publicação:** link do grupo VIP novo e `PIXEL_ID` — ambos marcados dentro
do HTML.

---

## Fontes do benchmark (consultadas em 07/09/2026)

- [Webinar Conversion Rate Benchmarks 2026 (Avg + High-Ticket) — aevent](https://aevent.com/average-webinar-conversion-rate/)
- [Webinar Statistics 2026: 60 Stats You Need to Know — Contrast](https://www.getcontrast.io/learn/webinar-statistics)
- [Landing Page Conversion Rate Benchmarks by Industry [2026 Data] — LanderLab](https://landerlab.io/blog/landing-page-conversion-rate)
- [Webinar Conversion Rate: Stop Losing Leads (2026 Guide) — LearnyBox](https://learnybox.com/en/blog/webinar-conversion-rate/)
- [7 Webinar Landing Page Examples to Convert More in 2026 — Wojo Media](https://www.thewojomedia.com/post/webinar-landing-page-examples)
- [Grupo de WhatsApp ainda funciona para Lançamento de Infoproduto? — Agência 365](https://agencia365.com.br/artigos/grupo-whatsapp-lancamento)
- [Página de vendas para infoproduto: estrutura que converte — Leo Kattah](https://leokattah.com.br/pagina-de-vendas-para-infoproduto-estrutura-que-converte/)

**Fontes internas:** `docs/aprendizados-ia/heuristicas-vitor.md` (A1-A7) ·
`docs/crm/sales-coach/conhecimento/icp-dono-de-otica.md` · `docs/processos/sop-fluxo-vendas.md` ·
`criativos-ad-grid.md` · `PAGINA-PLANO.md`
