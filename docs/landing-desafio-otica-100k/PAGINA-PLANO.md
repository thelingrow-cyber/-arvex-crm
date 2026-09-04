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

## 5. Decisões travadas — precisam do Vitor antes de qualquer código

1. **Destino do CTA.** Hoje o botão vai direto para o link do grupo de WhatsApp. Isso maximiza
   entrada, mas **o contato não entra no CRM** — a ARVEX fica sem a lista e o comercial sem base
   de trabalho. A alternativa é um passo de captura (nome + WhatsApp) antes do redirecionamento:
   perde alguns pontos de conversão, ganha a lista. **É a decisão que mais muda a página.**
2. **Data e formato.** `{{DATA}}` e `{{DIAS}}` (4 ou 5) — travam a página e os 13 criativos.
3. **A headline.** A atual promete *"dobrar o seu faturamento"*. Nenhum dos 13 criativos faz
   promessa direta ao leitor — quem clica não vai encontrar a mesma história. Recomendo trocar por
   headline de mecanismo. **Isso é ad scent, não preferência estética.**
4. **Prova nomeável.** Quais casos podem ir ao ar com cidade e número (Fran/Curitiba, Kesia,
   Rafaela). Precisa de autorização e de número confirmado.
5. **Pixel Meta.** O `PIXEL_ID` está como placeholder desde sempre. Sem ele não há retargeting —
   e o retargeting é onde as peças M5 e M2 trabalham.
6. **Variante B.** Manter `index-b.html` só se houver teste A/B com volume para ler. Senão, sai.

---

## 6. Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| **Ad scent quebrado** (anúncio promete mecanismo, página promete faturamento) | CTR bom e entrada baixa — o pior cenário, porque parece problema de mídia | Decisão 3, resolvida antes de escrever |
| Primeira dobra estourando no mobile | Perda direta na maior fonte de tráfego | A2: validar em viewport de celular antes de entregar |
| Página bonita e vazia | Retrabalho e verba queimada | A7: julgar por conversão. Simplificar é a resposta padrão |
| Sem captura de contato | Lista fica só no WhatsApp, comercial trabalha às cegas | Decisão 1 |
| Sem Pixel | Retargeting impossível, 3 das 13 peças ficam sem público | Decisão 5, antes de subir tráfego |

---

## 7. Sequência de execução (depois das decisões)

1. `cro-analyst` fecha estrutura e ponto de atrito → 2. `molly-pittman` audita ad scent contra os
criativos → 3. `copywriter` escreve → 4. `copy-chief` revisa → 5. `web-designer` aplica o sistema
visual → 6. `frontend-developer` implementa com Pixel e evento de clique → 7. teste em mobile real
→ 8. publica → 9. `cro-analyst` lê o dado depois do primeiro dia de tráfego.
