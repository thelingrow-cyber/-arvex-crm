# 🗂️ BACKLOG MESTRE — todas as frentes

**Fonte única.** Toda atividade de qualquer projeto entra aqui. A semana (`docs/semanas/`) é uma *seleção* deste arquivo, nunca uma lista paralela.
**Última atualização:** 2026-08-03

---

## Legenda

| Marca | Significado |
|---|---|
| 🤖 | **Eu executo** — você só aprova o resultado |
| 👤 | **Só você** — presença, voz, rosto ou decisão sua |
| 👥 | Equipe / terceiro (Gabriel, Thalita, closer, editor) |
| 🔒 | **Travado** — depende de outro item ou de um gate |
| P / M / G / XG | ≤1h · meio dia · 1-2 dias · semanas |

**Status:** `[ ]` backlog · `[>]` em execução · `[x]` feito · `[~]` congelado

---

## 🔧 As 5 máquinas (o eixo que importa)

Você listou ~30 atividades em 6 projetos. Mas elas não são 30 coisas diferentes — **são 5 máquinas repetidas 4 vezes cada**:

| Máquina | Quem consome | O que é |
|---|---|---|
| **M1 Conteúdo** | Lingrow · Viziom · Marca pessoal · Oferta | linha editorial → calendário → roteiro → gravar/design → postar |
| **M2 Página + Copy** | Cindy · Oferta · Lingrow | copy → landing → pixel → teste |
| **M3 Comercial + CRM** | Cindy · Viziom · Oferta | CRM → lista de leads → script → treinamento → follow-up |
| **M4 Produto / Dev** | Lingrow · Viziom · Cindy | melhorias, analytics, testes, migração |
| **M5 Posicionamento + Oferta** | Viziom · Marca pessoal · Oferta | é **upstream** — trava M1 e M2 |

**A consequência prática:** "criar calendário editorial" aparece em 4 frentes da sua lista. Isso não é 4 tarefas — é **1 processo com 4 conteúdos diferentes**. Construir a máquina uma vez e rodá-la 4 vezes é a diferença entre uma semana e um trimestre.

---

## 🚦 Ordem obrigatória (o que trava o quê)

```
M5 posicionamento/oferta  →  M1 conteúdo  →  M2 página  →  M3 comercial
```

Três dominós que, parados, param tudo atrás deles:

1. **OF-01 (refinar a oferta definitiva)** trava os outros 6 itens de OFERTA. Copy, página, criativo e stories de uma oferta indefinida = retrabalho garantido.
2. **MP-04 (refinar posicionamento)** trava calendário, roteiro e gravação da marca pessoal. *Atenuante: o brand book já existe — pode ser 1h de revisão, não uma semana.*
3. **VZ-06 (estressar a plataforma você mesmo)** trava treinar vendedor e coletar leads. **Não se vende o que não se usou** — e é isso que também responde o gate G4 (existe ótica usando de verdade?).

---

# 🔵 LINGROW

**Estado:** app no ar · foco = captação

- [ ] **LG-01** Linha editorial — formatos de conteúdo — 🤖 · M · M1 · *trava LG-02*
- [ ] **LG-02** Criar roteiros — 🤖 · M · 🔒 LG-01
- [ ] **LG-03** Postar — 👤 · P (recorrente)
- [ ] **LG-04** Página de captura e venda — 🤖 · M · M2 · *pendente desde abril; sem ela, influencer manda tráfego pra lugar nenhum*
- [ ] **LG-05** Atualizar o PostHog para ver onde clicam — 🤖 · M · M4 *(assumi PostHog no "postgate" — confirme)*
- [ ] **LG-06** Produto: melhorias — 👤 define o quê / 🤖 executa · G · *"melhorias" não é escopo — precisa virar lista*
- [ ] **LG-07** Abordar 10 influencers — 👤 · M · 🔒 LG-04 · M3
- [ ] **LG-08** Definir a métrica que a semana move (downloads? cadastros? pagantes?) — 👤 · P · *sem isso, "captação" não tem alvo*

---

# 🟣 VIZIOM

**Estado:** produto adquirido · uso real ainda não confirmado (gate G4)

- [ ] **VZ-01** Calendário editorial — 🤖 · M · M1 · 🔒 VZ-02
- [ ] **VZ-02** Posicionamento + linhas de conteúdo — 🤖 propõe / 👤 decide · M · M5 · *trava VZ-01 e VZ-03*
- [ ] **VZ-03** Carrosséis + roteiros de Reels — 🤖 · M · 🔒 VZ-02
- [ ] **VZ-04** CRM da operação — 🤖 · G · M3 · ⚠️ **ver decisão D-1 abaixo**
- [ ] **VZ-05** Treinamento com vendedor — 👤 · M · 🔒 VZ-06
- [ ] **VZ-06** Estressar a plataforma (teste próprio) — 👤 · G · **faça primeiro; responde o G4**
- [ ] **VZ-07** Migração do produto para estrutura própria — 🤖 · **XG** · ⚠️ **ver decisão D-2 abaixo**
- [ ] **VZ-08** Coletar lista de leads p/ processo comercial — 🤖 + 👤 · M · 🔒 VZ-06
- [ ] **VZ-09** Rotacionar a API Key Global do Evolution — 🤖 · P · *vazou no chat em 14/07, nunca trocada; essa infra sustenta o atendimento da Cindy*

### ⚠️ D-1 — "criar o CRM da operação" (decisão antes de codar)

Você **já tem** o `arvex-crm` rodando (pipeline, atendimento, CS, financeiro, IA). Três caminhos:
- **(a) Usar o mesmo CRM** com uma marcação de origem — zero build, mistura as duas operações
- **(b) Segunda instância** do mesmo código, banco separado — ~1 dia, 2 códigos para manter
- **(c) CRM novo** — semanas de trabalho **[recomendo descartar]**

Sem escolher, "criar o CRM" é um item aberto que pode custar 1 dia ou 1 mês.

### ⚠️ D-2 — migração para estrutura própria é o item mais caro da lista inteira

Refazer um SaaS é trabalho de **meses**, não de semana. **Gate proposto:** só começa quando houver **cliente pagando** no Viziom. Migrar antes disso é construir para ninguém — e é exatamente o risco que quase matou a agenda passada.

---

# 🟢 CINDY

**Estado:** é a frente que paga o mês

- [ ] **CD-01** Fazer as calls — 👤 · recorrente · **prioridade sobre qualquer build**
- [ ] **CD-02** CRM: agente de IA de atendimento — 🤖 · G · *Fase 3 (enviar mídia) já especificada; 🔒 gate do áudio*
- [ ] **CD-03** CRM: sistema de IA do closer — 🤖 · G · *Sales Coach Fase 3 já arquitetada em doc*
- [ ] **CD-04** CRM: financeiro — 🤖 · G · *Proposta C aprovada; 4 dúvidas em aberto antes de codar*
- [ ] **CD-05** Copy criativo do lançamento — 🤖 · M · M2 · 🔒 data do lançamento
- [ ] **CD-06** Página do lançamento — 🤖 · M · M2 · 🔒 CD-05
- [ ] **CD-07** Resolver os 5 leads quentes parados 17-19 dias — 👤/👥 · P · *dinheiro parado*
- [ ] **CD-08** Limpar os 21 leads mortos do bolsão "contato" — 🤖 · P
- [ ] **CD-09** Os 3 gates do CRM (mídia toca? · `||` no prompt da Carol? · kernel checa `agente_pausado`?) — 🤖 + 👤 · M

> **Nota:** CD-02, CD-03 e CD-04 são **três builds grandes tratados como um item só** ("otimizar CRM"). Cada um é uma semana. Rodar os três em paralelo não vai acontecer — escolha a ordem. *Recomendo: atendimento → financeiro → closer* (o primeiro decide se a Thalita usa o CRM; o último é o mais sofisticado e o menos urgente).

---

# 🟡 MARCA PESSOAL

- [ ] **MP-01** Calendário de conteúdo — 🤖 · M · 🔒 MP-04
- [ ] **MP-02** Escrever roteiros — 🤖 · M (recorrente) · 🔒 MP-01
- [ ] **MP-03** Gravar vídeos — 👤 · recorrente · **o único gargalo que não terceiriza**
- [ ] **MP-04** Refinar posicionamento — 👤 · M · M5 · *o brand book já existe — isto é revisão, não criação do zero*
- [ ] **MP-05** Criar o Projeto do carrossel no Claude — 👤 · **P (15 min)** · *prompt, Knowledge e tool de PNG já prontos, parados esperando só isso*

---

# 🔴 OFERTA (ARVEX)

- [ ] **OF-01** Refinar a oferta definitiva — 👤 decide / 🤖 estrutura · M · M5 · **🎯 primeiro dominó: trava OF-02 a OF-07**
- [ ] **OF-02** Primeiro funil: webinário — 🤖 estrutura / 👤 apresenta · G · 🔒 OF-01
- [ ] **OF-03** Gravar ou criar criativo — 👤 (ou 🤖 se for IA) · M · 🔒 OF-01
- [ ] **OF-04** Criar a página — 🤖 · M · M2 · 🔒 OF-01
- [ ] **OF-05** Escrever copy do criativo — 🤖 · M · 🔒 OF-01
- [ ] **OF-06** Primeiros posts do perfil da ARVEX (carrossel + vídeos com IA) — 🤖 · M · M1
- [ ] **OF-07** Sequência de stories 2×/semana vendendo a ideia + CTA "me chama para implementar" — 🤖 escreve / 👤 posta · P (recorrente)
- [ ] **OF-08** Letícia Wendy: última chamada ou enterrar — 👤 · P · *call foi 30/06, 34 dias; sua janela histórica máxima é 13*
- [ ] **OF-09** De onde vem o próximo lead da oferta? — 👤 · P · *hoje o pipeline próprio tem 1 nome*

---

# ⚪ PESSOAL / VIDA

*Não competem com as frentes de trabalho — são de baixo esforço e alto alívio. Fazem-se nos intervalos.*

- [ ] **PS-01** Anúncio da mesa + 2 monitores — 🤖 escreve / 👤 fotografa e publica · P
- [ ] **PS-02** iPhone X na OLX — 🤖 escreve / 👤 publica · P
- [ ] **PS-03** Plano EUA + pesquisar passagens — 🤖 pesquisa / 👤 decide · M · *quanto mais perto, mais caro — tem prazo implícito*
- [ ] **PS-04** Rio: pesquisar locais e falar com pessoas para ficar 1 mês — 🤖 pesquisa / 👤 conversa · M

---

## 📊 Leitura do backlog

| | Itens |
|---|---|
| **Total** | 35 |
| 🤖 **Eu executo (você só aprova)** | ~18 |
| 👤 **Exigem você** | ~14 |
| 🔒 **Travados por outro item** | ~10 |
| ⚠️ **Escopo indefinido** (LG-06, VZ-04, VZ-07, CD-01 agrupado) | 4 |

**O que isso significa:** a lista *parece* 35 semanas de trabalho seu. Metade é executável por mim; um terço está travado por 3 decisões que levam uma hora cada (OF-01, VZ-04/D-1, MP-04).

**Seu gargalo real não é execução — é decisão e presença**: gravar vídeo, fazer call, testar plataforma, treinar vendedor, falar com influencer. **Essas 5 coisas são o teto da semana.** Tudo o mais escala comigo.
