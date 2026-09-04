# Plano — Página de captura do Desafio Ótica +100K (CD-06)

> **Status:** plano. Nada de código antes das decisões da seção 5 estarem fechadas.
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

## 4. Estrutura proposta

**Princípio:** tráfego frio + oferta gratuita = **página curta**. Página longa é para venda, não
para captura. Mas o ICP exige uma dose mínima de prova, porque a objeção nº1 é cicatriz de
mentoria anterior e o medo de "é tudo online".

| Bloco | Conteúdo | Por quê |
|---|---|---|
| **1. Primeira dobra** | Logo do evento · headline · subhead de 1 linha · CTA · data e formato | Tudo visível no celular sem scroll (A2). É aqui que a página é ganha ou perdida |
| **2. O que você sai tendo** | 3 a 4 bullets do que ela leva embora — não do que vai ser ensinado | O ICP não quer aula, quer direção e algo aplicável |
| **3. Prova de par** | 1 a 3 casos de ótica do mesmo porte, com cidade e tempo de loja | *"Quando a gente viu o depoimento da Amanda — a pessoa que a gente conhece"*. Prova de par vale mais que aluno-estrela |
| **4. Quem é a Cindy** | Curto, 3 a 4 linhas + foto integrada | Resolve o medo de "é tudo online" — quem tira esse medo é a autoridade, não o vendedor |
| **5. CTA final** | Repetição do botão + a razão de entrar no grupo | O valor fica atrás da porta: a oferta especial só é liberada lá |

**Sem FAQ, sem contador regressivo, sem depoimento em vídeo pesado, sem seção de bônus.**
Escassez fabricada aumenta resistência em quem decide em dupla — e o público decide em dupla.

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
