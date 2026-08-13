# 🗂️ BACKLOG MESTRE — todas as frentes

**Fonte única.** Toda atividade de qualquer projeto entra aqui. A semana (`docs/semanas/`) é uma *seleção* deste arquivo, nunca uma lista paralela.
**Painel visual:** `docs/gestao/painel.html`
**Última atualização:** 2026-08-03 · **56 atividades**

---

## Legenda

| Marca | Significado |
|---|---|
| 🤖 | **Eu executo** — você só aprova o resultado |
| 👤 | **Só você** — presença, voz, rosto, assinatura ou decisão sua |
| 🤝 | Misto — eu preparo, você decide ou apresenta |
| ↳ | **Travado** — só começa depois do item citado |
| P / M / G / XG | ≤1h · meio dia · 1-2 dias · semanas |

**Status:** `[ ]` backlog · `[>]` em execução · `[x]` feito · `[~]` congelado
**Dentro de cada trilha, a ordem da lista é a ordem de execução.**

---

## 🔧 As 5 máquinas

As 56 atividades não são 56 coisas — são **5 máquinas repetidas** em frentes diferentes:

| | Máquina | Quem consome |
|---|---|---|
| **M1** | Conteúdo — linha editorial → calendário → roteiro → gravar → postar | Lingrow · Viziom · Marca pessoal · Oferta |
| **M2** | Página + copy | Lingrow · Cindy · Oferta |
| **M3** | Comercial + CRM | Cindy · Viziom · Oferta · Lingrow |
| **M4** | Produto / dev | Lingrow · Viziom · Cindy |
| **M5** | Posicionamento + oferta — **upstream, trava M1 e M2** | Viziom · Marca pessoal · Oferta |

**Ordem que não se quebra sem retrabalho:** `M5 → M1 → M2 → M3`

---

# 🔵 LINGROW · pré-lançamento na loja

> Mudou de retrato: não é "app no ar, foco captação" — é **app indo para a loja**, com caminho crítico de publicação.

### Trilha 1 — Lançamento na loja *(caminho crítico, nesta ordem)*

- [ ] **LG-09** Aplicar migration 008 no SQL Editor do Supabase — 👤 · P · M4
- [ ] **LG-12** Decidir: completar 600 frases **ou** ajustar a promessa — 👤 · P · *decide o que a ficha da loja promete; vem antes de LG-14*
- [ ] **LG-10** Contrato de apps pagos Apple (pessoa jurídica + DSA/UE + banco + W-8BEN) — 👤 · M · ⚠️ **maior espera externa; sem ele o app não cobra — comece por aqui**
- [ ] **LG-11** Terminar RevenueCat e entregar a chave `appl_…` + segredo do webhook — 👤 · M · ↳ LG-10
- [ ] **LG-13** QA manual do fluxo no Expo Go — 👤 · M · ↳ LG-09
- [ ] **LG-14** Aprovar ficha da loja e screenshots — 👤 · P · ↳ LG-12

### Trilha 2 — Demanda *(encher antes de publicar)*

- [ ] **LG-15** Montar landing de waitlist — 🤖 · M · M2 · ⚠️ *possível duplicata de LG-04*
- [ ] **LG-04** Página de captura e venda — 🤖 · M · M2 · *confirmar se é a mesma coisa que LG-15 ou a página pós-lançamento*
- [ ] **LG-16** Gravar 4 vídeos do build-in-public — 👤 · M · M1
- [ ] **LG-17** Entrar em 15-20 comunidades ajudando — 👤 · M · M3 · *canal mais barato e mais lento — comece cedo*
- [ ] **LG-01** Linha editorial — formatos de conteúdo — 🤖 · M · M1
- [ ] **LG-02** Criar roteiros — 🤖 · M · M1 · ↳ LG-01
- [ ] **LG-03** Postar — 👤 · P · M1 · recorrente
- [ ] **LG-07** Abordar 10 influencers — 👤 · M · M3 · ↳ LG-15
- [ ] **LG-08** Definir a métrica que a semana move — 👤 · P · *waitlist? download? assinante?*

### Trilha 3 — Produto

- [ ] **LG-05** Atualizar o PostHog para revisar onde clicam — 🤖 · M · M4 · *confirmar se "postgate" é PostHog*
- [ ] **LG-06** Fazer melhorias no produto — 🤝 · G · M4 · ⚠️ *escopo indefinido — precisa virar lista*

---

# 🟣 VIZIOM · onda 1 comercial começando

> Também mudou: já **está vendendo** (onda 1 de mensagens, contrato de closer, agente com falhas observadas). Não é mais "produto parado esperando decisão".

### Trilha 1 — Comercial *(onda 1 em andamento)*

- [ ] **VZ-12** Preencher e assinar o contrato do closer — 👤 · P · M3 · *antes de treinar alguém*
- [ ] **VZ-11** Disparar as 15 mensagens da onda 1 — 8 longas, 7 curtas, manual — 👤 · P · M3 · *manual de propósito: é teste A/B de formato, não volume*
- [ ] **VZ-08** Coletar lista de leads p/ continuar o processo comercial — 🤝 · M · M3 · *a onda 1 já consome lista; isto é reabastecer*
- [ ] **VZ-05** Treinamento com vendedor — 👤 · M · M3 · ↳ VZ-12

### Trilha 2 — Agente de IA *(aprende com a onda 1)*

- [ ] **VZ-10** Ajustar o system prompt em cima das falhas — 🤖 · P · M3 · **me mande as falhas observadas — sem elas isto é chute**

### Trilha 3 — Produto

- [ ] **VZ-06** Estressar a plataforma (teste próprio) — 👤 · G · ⚠️ **virou urgente: você já está vendendo antes de ter testado**
- [ ] **VZ-04** Criar o CRM da operação — 🤖 · G · M3 · ⚠️ **D-1** abaixo
- [ ] **VZ-09** Rotacionar a API Key do Evolution — 🤖 · P · ⚠️ *vazou no chat em 14/07; essa infra sustenta o atendimento da Cindy*
- [ ] **VZ-07** Iniciar migração do produto para estrutura própria — 🤖 · **XG** · M4 · ⚠️ **D-2** abaixo

### Trilha 4 — Marca *(só depois do posicionamento)*

- [ ] **VZ-02** Definir posicionamento e linhas de conteúdo — 🤝 · M · M5 · *destrava VZ-01 e VZ-03*
- [ ] **VZ-01** Criar calendário editorial — 🤖 · M · M1 · ↳ VZ-02
- [ ] **VZ-03** Criar carrosséis e roteiros de Reels — 🤖 · M · M1 · ↳ VZ-02

### ⚠️ D-1 — "criar o CRM da operação"

Você **já tem** o `arvex-crm` rodando. (a) mesmo CRM com marcação de origem = zero build · (b) segunda instância, banco separado ≈ 1 dia · (c) CRM novo = semanas **[descartar]**.

### ⚠️ D-2 — migração para estrutura própria é o item mais caro de todos

Refazer um SaaS é trabalho de **meses**. **Gate:** só começa com **cliente pagando** no Viziom.

---

# 🟢 CINDY · paga o mês

### Trilha 1 — Caixa *(vem antes de qualquer build)*

- [ ] **CD-01** Fazer as calls — 👤 · P · M3 · recorrente
- [ ] **CD-07** Resolver os 5 leads quentes parados 17-19 dias — 👤 · P · M3 · ⚠️ *dinheiro parado; sua janela de fechamento é de 1 dia*
- [ ] **CD-08** Limpar os 21 leads mortos do bolsão "contato" — 🤖 · P · M3

### Trilha 2 — CRM *(gates primeiro, depois os 3 builds em fila)*

- [ ] **CD-09** Fechar os 3 gates (mídia · prompt da Carol · `agente_pausado`) — 🤝 · M · M3
- [ ] **CD-02** Agente de IA de atendimento — 🤖 · G · M3 · ↳ CD-09
- [ ] **CD-04** Módulo financeiro — 🤖 · G · M3 · *2ª da fila · Proposta C aprovada*
- [ ] **CD-03** Sistema de IA do closer — 🤖 · G · M3 · *3ª da fila · o mais sofisticado, o menos urgente*

### Trilha 3 — Lançamento

- [ ] **CD-05** Escrever copy criativo do lançamento — 🤖 · M · M2 · *precisa da data*
- [ ] **CD-06** Criar página do lançamento — 🤖 · M · M2 · ↳ CD-05

---

# 🟡 MARCA PESSOAL

### Trilha 1 — Base *(destrava a produção)*

- [x] **MP-04** Refinar posicionamento — 👤 · M · M5 · *13/08: conflito 25/07 (nichar) × 13/07 (horizontal) resolvido — marca horizontal, vertical vive no registro OBRA. Ver `docs/ecossistema/linha-editorial-e-calendario.md` §01*
- [ ] **MP-05** Criar o Projeto do carrossel no Claude — 👤 · **P (15 min)** · M1 · *prompt e tool prontos, parados esperando só isso* · ⚠️ **bloqueia o bloco de produção de MP-02/MP-03**

### Trilha 2 — Produção

- [x] **MP-01** Criar calendário de conteúdo — 🤖 · M · M1 · *13/08: grade semanal fixa 7/sem (5 VISÃO : 2 OBRA), piso de 3 na semana ruim, regime de lote e banco de 28 pautas em `docs/ecossistema/linha-editorial-e-calendario.md`*
- [ ] **MP-02** Escrever roteiros — 🤖 · M · M1 · ↳ MP-01
- [ ] **MP-03** Gravar vídeos — 👤 · M · M1 · *recorrente · o único gargalo que não terceiriza*

---

# 🔴 OFERTA (ARVEX)

### Trilha 1 — Definir *(trava tudo abaixo)*

- [ ] **OF-01** Refinar a oferta definitiva — 🤝 · M · M5 · **🎯 primeiro dominó — destrava OF-02 a OF-05**
- [ ] **OF-09** Decidir de onde vem o próximo lead da oferta — 👤 · P · M3 · *hoje o pipeline próprio tem 1 nome*

### Trilha 2 — Construir

- [ ] **OF-02** Criar o primeiro funil: webinário — 🤝 · G · M2 · ↳ OF-01
- [ ] **OF-05** Escrever copy do criativo — 🤖 · M · M2 · ↳ OF-01
- [ ] **OF-03** Gravar ou criar criativo — 👤 · M · M1 · ↳ OF-01
- [ ] **OF-04** Criar página — 🤖 · M · M2 · ↳ OF-01

### Trilha 3 — Distribuir

- [ ] **OF-06** Primeiros posts do perfil ARVEX (carrossel + vídeos com IA) — 🤖 · M · M1
- [ ] **OF-07** Sequência de stories 2×/semana com CTA "me chama para implementar" — 🤝 · P · M1 · recorrente

### Trilha 4 — Pipeline

- [ ] **OF-08** Letícia Wendy: última chamada ou enterrar — 👤 · P · M3 · ⚠️ *call foi 30/06 — 34 dias; sua janela histórica máxima é 13*

---

# ⚪ PESSOAL / VIDA

*Baixo esforço, alto alívio. Fazem-se nos intervalos — não competem com as frentes de trabalho.*

### Trilha 1 — Vender
- [ ] **PS-01** Criar anúncio da mesa e dos 2 monitores — 🤝 · P
- [ ] **PS-02** Colocar o iPhone X na OLX — 🤝 · P

### Trilha 2 — Viagem
- [ ] **PS-03** Criar plano EUA e pesquisar passagens — 🤝 · M · *quanto mais perto, mais caro — tem prazo implícito*
- [ ] **PS-04** Rio: pesquisar locais e falar com pessoas para ficar 1 mês — 🤝 · M

---

## 📊 Leitura do backlog

| | Itens |
|---|---|
| **Total** | **56** (LG 17 · VZ 12 · CD 9 · MP 5 · OF 9 · PS 4) |
| 🤖 **Eu executo sozinho** | 22 |
| 👤 **Só você** | 23 |
| 🤝 **Mistos** | 11 |
| ↳ **Travados por outro item** | 16 |
| ⚠️ **Escopo/decisão em aberto** | LG-04 vs LG-15 · LG-06 · VZ-04 (D-1) · VZ-07 (D-2) |

**34 dos 56 passam por você.** Com teto de 5 itens 👤 por semana, são **≈7 semanas de calendário** só na sua parte. As 12 atividades novas trouxeram 10 suas e 2 minhas — lançar app é assim: contrato, banco, fiscal e aprovação de loja não terceirizam.

**Os 3 dominós:** `OF-01` destrava 4 · `VZ-02` destrava 2 · `MP-04` destrava 2. Uma hora cada.
