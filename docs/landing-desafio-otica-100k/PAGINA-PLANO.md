# Plano — Página de captura do Desafio Ótica +100K (CD-06)

> **Status:** estrutura fechada pelo CRO em 04/09. Pronto para copy e build.
> Falta antes de subir tráfego: link do grupo VIP, prova nomeável e Pixel.
> **Story/atividade:** CD-06 · ↳ CD-05 (criativos, prontos) · ↳ CD-12 (nome, fechado)

---

## 1. Objetivo e métrica

**A página tem um trabalho só:** transformar clique de anúncio em contato dentro do grupo VIP.
Não é página de venda, não é institucional, não apresenta a Cindy para o mundo.

**Métrica única:** *taxa de entrada no grupo* = pessoas que entram no grupo ÷ visitantes únicos.
Nada de tempo na página, scroll depth ou bounce como critério de sucesso.

**Benchmark do próprio histórico:** na última medição conhecida deste funil, **16 leads marcados e
só 8 entraram** — cerca de 50% de perda entre o clique e a entrada. É esse número que a nova
página precisa bater, e é por isso que simplificar vence embelezar.

---

## 2. O que já existe (inventário — reusar, não recriar)

| Ativo | Onde | Como usar |
|---|---|---|
| **Sistema visual aprovado** | `docs/landing-cindy-vendas/index.html` | **Fonte da verdade visual.** Inter 900, dourado + navy + verde WhatsApp. Herdar tokens daqui |
| Página de captura curta anterior | `docs/landing-cindy-desafio/index.html` | Estrutura hero + bottom. Referência de enxugamento |
| Página atual do +100K | `docs/landing-desafio-otica-100k/index.html` | Já renomeada. Base a evoluir, não a substituir |
| Variante B nunca testada | `docs/landing-desafio-otica-100k/index-b.html` | Só faz sentido manter se houver teste A/B de verdade |
| Material "Desafio 100K Ótica v3" | `docs/materiais-cindy/100k-otica.html` | Origem do nome. Usa Playfair Display — **não herdar tipografia daqui** |
| **Os 13 criativos** | `criativos-ad-grid.md` | A página tem que continuar a frase que o anúncio começou |
| **Swipe das peças que converteram** | `docs/materiais-cindy/swipe-criativos.md` | Vocabulário e ritmo |
| **ICP real** | `docs/crm/sales-coach/conhecimento/icp-dono-de-otica.md` | Verdade de público |
| **Heurísticas do Vitor** | `docs/aprendizados-ia/heuristicas-vitor.md` | A1-A7 são lei nesta entrega |

**Restrições visuais já reprovadas** (não repetir): serif no corpo, cutout flutuando sobre o fundo,
tipografia em `vw` explosivo, transição brusca entre seções.

**Heurísticas que governam esta página:**
- **A1** — referência é contrato: replicar estrutura, trocar conteúdo. Não "melhorar".
- **A2** — mobile é o juiz: headline + CTA na primeira dobra do celular, sem scroll.
- **A5** — foto integrada ao fundo, nunca flutuando.
- **A6** — headline com benefício + mecanismo + emoção, curta e tangível.
- **A7** — a página se julga por conversão. Se estiver ruim: simplificar, não embelezar.

---

## 3. O time — quem faz o quê, nesta ordem

| # | Quem | Entrega | Por que nessa posição |
|---|---|---|---|
| 1 | **`WebDesign:agents:cro-analyst`** | Estrutura da página, hierarquia e ponto de atrito | Decide a arquitetura **antes** de existir copy ou layout. Estrutura errada não se conserta com design |
| 2 | **`AIOX:clone:molly-pittman`** | Auditoria de **ad scent** — anúncio → página | O maior risco desta entrega é a página contar história diferente do criativo. Entra cedo, não no fim |
| 3 | **`WebDesign:agents:copywriter`** | Copy da página (hero, seções, CTA, microcopy) | É o dono de copy **de página**. O Halbert é de anúncio — a fronteira existe e vale |
| 4 | **`Marketing:agents:copy-chief`** | Revisão final da copy | Papel de chief: nenhum copy da casa sai sem revisão |
| 5 | **`WebDesign:agents:web-designer`** | Layout herdando o sistema visual da landing de vendas | Sistema já aprovado — o trabalho é aplicar, não criar identidade |
| 6 | **`WebDesign:agents:frontend-developer`** | HTML/CSS, mobile-first, Pixel e evento de clique | Implementação só depois de copy e layout fechados |
| 7 | **`WebDesign:agents:cro-analyst`** | Validação pós-publicação | Fecha o ciclo com dado real, não com opinião |

**Fora do time, de propósito:** SEO (página com `noindex`, tráfego é 100% pago), motion designer
(animação aumenta peso e atrasa a primeira dobra no 4G do interior), storytelling-expert (a
narrativa longa é da live, não da captura).

---

## 4. Estrutura — fechada pelo CRO em 04/09

### 4.1 Auditoria da página atual

A construção técnica está boa: mobile-first de verdade, `clamp()` em toda tipografia, media query
única em 820px, `prefers-reduced-motion` respeitado. O problema não é código — é conteúdo e
credibilidade.

| Elemento | Nota | Leitura |
|---|---|---|
| Logo do evento | **8** | Dá identidade e ancora o nome. Mantém |
| CTA (verde WhatsApp, verbo claro) | **8** | Bom contraste e bom verbo. Mas é o único da página |
| Subhead ("garanta acesso à oferta especial") | **7** | O valor atrás da porta está certo |
| Topbar "Desafio ao vivo · Online" | **6** | Ocupa o espaço mais nobre da tela com informação, não com persuasão. Deveria carregar a **data** |
| Foto da Cindy | **5** | Carregada de `cindyb.com.br` — **URL externa** com latência e risco de quebra, existindo cópia local na pasta |
| Eyebrow "Sua ótica faturando 2x" | **3** | Promessa numérica solta, sem mecanismo, no primeiro contato — exatamente onde a cicatriz de mentoria reage |
| Micro-CTA "Vagas limitadas" | **2** | **Escassez fabricada em evento online e gratuito.** Ninguém acredita em vaga limitada em grupo de WhatsApp, e o ICP registra que pressão artificial aumenta a resistência de quem decide em dupla |
| Prova social | **0** | Não existe. Para um público cuja objeção nº1 é cicatriz de mentoria, é o maior buraco da página |
| Data do evento | **ausente** | O evento tem data e a página não diz. Falha básica de página de captura |

### 4.2 O achado mais importante: o furo pode não estar na página

O benchmark é **16 leads marcados, 8 entraram**. Metade se perde — mas *entre o quê e o quê*?
Hoje não dá para saber, porque não existe evento de clique no CTA. As duas hipóteses têm soluções
opostas:

- **Se ela não clica** → o furo é a página (headline, prova, credibilidade).
- **Se ela clica e não entra** → o furo é a passagem para o WhatsApp: abrir o app, ver um grupo de
  desconhecidos, decidir entrar. Nesse caso, mexer na página não resolve nada.

**Antes de otimizar qualquer coisa, instrumentar o clique.** É meia hora de trabalho e separa dois
problemas que exigem respostas diferentes. Sem isso, toda melhoria vira palpite.

### 4.3 A estrutura aprovada

**Princípio:** tráfego frio + oferta gratuita = **página curta**. Página longa é para venda. Mas o
ICP exige uma dose mínima de prova, porque a objeção nº1 é cicatriz de mentoria e o medo de "é
tudo online".

| Bloco | Conteúdo | Função na conversão |
|---|---|---|
| **1. Primeira dobra** | Barra com a **data** · logo do evento · headline · subhead · CTA | Tudo visível no celular sem scroll (A2). É aqui que a página é ganha ou perdida |
| **2. O que você sai tendo** | 3 bullets do que ela **leva embora** — não do que vai ser ensinado | O ICP não quer aula, quer direção e algo aplicável. Reduz esforço percebido |
| **3. Prova de par** | 1 a 3 casos de ótica do mesmo porte, com cidade e tempo de loja | Responde à cicatriz. Prova de par vale mais que aluno-estrela |
| **4. Quem é a Cindy** | 3 a 4 linhas + foto **local**, integrada ao fundo (A5) | Resolve o medo de "é tudo online": quem tira esse medo é a autoridade |
| **5. CTA final** | Botão repetido + a razão de entrar no grupo | Segundo ponto de conversão para quem rolou a página |

**Regra de CTA:** um a cada dobra e meia. Com cinco blocos, são dois botões — hero e fechamento.
Mais que isso vira ruído.

**Sai da página:** "vagas limitadas", contador regressivo, FAQ, seção de bônus, depoimento em
vídeo pesado, imagem hospedada fora.

**Fica de fora também a animação `reveal` na primeira dobra.** Conteúdo que entra por
IntersectionObserver com `data-delay` atrasa o que precisa aparecer primeiro — e o público está no
4G do interior. Animação só do bloco 2 para baixo.

### 4.4 Urgência, escassez e prova — o que é legítimo aqui

- **Urgência: sim, e ela é real.** O evento tem data — 22, 23 e 24 de setembro. Data é urgência
  honesta e não precisa de contador para funcionar.
- **Escassez: não.** Evento gratuito e online não tem vaga limitada, e o público sente a mentira.
  Escassez legítima neste nicho existe (exclusividade por cidade), mas é argumento de venda da
  mentoria, não de entrada em grupo.
- **Prova: obrigatória, e do mesmo porte.** Um caso com cidade e tempo de loja vale mais que três
  números grandes sem rosto.

### 4.5 Hipóteses de teste, por impacto × facilidade

| # | Hipótese | Impacto | Facilidade |
|---|---|---|---|
| 1 | **Instrumentar o clique no CTA** (não é teste, é pré-requisito) | Alto — separa dois problemas distintos | Alta |
| 2 | Trocar o eyebrow "Sua ótica faturando 2x" pela **data do evento** | Alto — tira a promessa solta do primeiro contato | Alta |
| 3 | Remover "vagas limitadas" | Médio-alto — credibilidade com público queimado | Alta |
| 4 | Página com prova × página de uma dobra só | Alto | Média |
| 5 | CTA "Entrar no grupo VIP" × "Quero participar do desafio" | Médio | Alta |

**Ressalva honesta:** A/B só se lê com volume. Com o tráfego previsto para um lançamento de 3 dias,
provavelmente não haverá amostra para separar 2, 3 e 5 com confiança. Recomendo **aplicar 1, 2 e 3
direto** — são correções, não apostas — e reservar o teste real para 4, que é a única decisão
estrutural em aberto.

---

## 5. Decisões

### Fechadas em 04/09

**1. Destino do CTA: direto para o grupo de WhatsApp.** Sem passo de captura antes.
Decisão do Vitor, com a consequência conhecida e aceita: **o contato não entra no CRM** — a lista
vive dentro do grupo, e o comercial trabalha a partir de lá. Efeito prático no build: nenhum
formulário, nenhuma validação, nenhum backend. A página fica mais simples e mais rápida, o que
joga a favor da conversão.
*Se depois quiserem a lista no CRM, o caminho de menor atrito é coletar dentro do grupo (mensagem
de boas-vindas), não voltar a pôr formulário na página.*

**2. Data e formato: 22, 23 e 24 de setembro — terça, quarta e quinta. 3 dias.**
Não 4 (como a peça de abril) nem 5 (como a página atual dizia). Já aplicado nas 13 peças e neste
plano. **A página ainda diz 5 dias** — corrigir no build.
*Contexto de calendário: o Dia do Cliente é 15/09, uma semana antes. A live do dia 04/09 aquece,
o Dia do Cliente entrega a primeira vitória, e o desafio entra na sequência.*

**3. Headline: fechada pelo Vitor em 04/09.**

> ### Crie em 3 dias comigo a estratégia que vai colocar a sua loja na rota dos +100K por mês.
>
> **Ênfase visual em duas partes** (padrão das headlines anteriores): `3 dias` e `+100K por mês`.
> **Eyebrow:** Ao vivo · 22, 23 e 24 de setembro
> **Subhead:** Entre no Grupo VIP e garanta acesso à oferta especial do desafio.

*Por que ela funciona:* obedece o molde das três headlines que já rodaram — **duração + verbo de
construção + ativo nomeado + resultado** (*"Crie em 3 dias a estratégia que vai levar a sua loja ao
recorde de faturamento em maio"* · *"3 dias criando a campanha de Maio mais lucrativa da sua ótica"*).
O "comigo" vem da variante B (*"Descubra em 5 dias, comigo…"*) e faz o trabalho que o ICP pede:
quem tira o medo de "é tudo online" é a autoridade presente, não o método.

E resolve a tensão que vinha travando essa decisão: **"na rota dos +100K" promete a direção, não o
resultado.** Ancora o nome do evento sem prometer faturamento a ela — não há o que a entrega
desminta, e não reativa a cicatriz de mentoria.

**Nota de calibragem, para não repetir o erro:** as páginas anteriores da Cindy sempre prometeram
resultado direto ("recorde de faturamento", "mais lucrativa", "dobrar"), e isso não é erro — é a
função da página. No anúncio, promessa direta queima, porque o público está no scroll e já se
queimou antes. Na página, ela já clicou e quer saber do evento: a promessa é o que faz entrar no
grupo. O que precisa bater entre anúncio e página é o **mecanismo**, não o nível de promessa.

### Ainda abertas

**4. Prova nomeável.** Quais casos podem ir ao ar com cidade e número (Fran/Curitiba, Kesia,
Rafaela). Precisa de autorização e de número confirmado. **Bloqueia o bloco 3 da página.**

**5. Pixel Meta.** O `PIXEL_ID` está como placeholder desde sempre. Sem ele não há retargeting —
e é lá que M5, M2 e M10 trabalham. **Bloqueia a subida de tráfego, não o build.**

**6. Variante B.** Manter `index-b.html` só se houver teste A/B com volume para ler. Senão, sai.

---

## 6. Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Ad scent quebrado (anúncio e página contando histórias diferentes) | CTR bom e entrada baixa — o pior cenário, porque parece problema de mídia | Resolvido na decisão 3: a headline promete a ROTA aos +100K, que é a direção que os criativos sustentam |
| Primeira dobra estourando no mobile | Perda direta na maior fonte de tráfego | A2: validar em viewport de celular antes de entregar |
| Página bonita e vazia | Retrabalho e verba queimada | A7: julgar por conversão. Simplificar é a resposta padrão |
| Lista vive só no grupo de WhatsApp | Comercial sem base no CRM; quem sai do grupo some | Aceito na decisão 1. Mitigar coletando dentro do grupo, não na página |
| Sem Pixel | Retargeting impossível, 3 das 13 peças ficam sem público | Decisão 5, antes de subir tráfego |

---

## 7. Sequência de execução (depois das decisões)

1. `cro-analyst` fecha estrutura e ponto de atrito → 2. `molly-pittman` audita ad scent contra os
criativos → 3. `copywriter` escreve → 4. `copy-chief` revisa → 5. `web-designer` aplica o sistema
visual → 6. `frontend-developer` implementa com Pixel e evento de clique → 7. teste em mobile real
→ 8. publica → 9. `cro-analyst` lê o dado depois do primeiro dia de tráfego.
