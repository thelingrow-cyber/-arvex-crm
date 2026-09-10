# Oferta v1 — o que vender, e como funciona

> Complemento operacional de [`posicionamento-v1-negocio-nativo.md`](posicionamento-v1-negocio-nativo.md).
> Responde: **o que dá para vender de fato hoje**, com que modelo econômico, e onde está a brecha.
> Tudo aqui parte do que **já existe construído e rodando** — nada depende de construir do zero.
> Preços são **faixa de trabalho para testar**, não tabela fechada. Ver §06.

---

## 01 — O frame que muda a conversa: funcionário de IA

O cliente não sabe comparar preço de "automação". Sabe comparar preço de **gente**.

> **"Isso é um funcionário que não falta, não esquece de dar follow-up e não dorme."**

Por que esse enquadramento vence:

- **Ancoragem em salário, não em software.** Um SDR custa R$2.500-3.500/mês + encargos (~70% a mais)
  + treinamento + turnover. Um atendente de IA a R$1.500-2.500/mês é *barato* nessa régua e *caro*
  na régua de "app". A régua escolhida decide a objeção.
- **É tangível.** "Agente de IA" é abstrato; "o funcionário que responde seu WhatsApp" não é.
- **Tem lastro internacional** — *AI Employees* é o frame que a pesquisa de junho já apontou como
  arbitragem EUA→BR, e ainda não pegou no Brasil.
- **Cabe na categoria.** Contratar funcionário de IA é o primeiro passo de virar Negócio Nativo.

⚠️ **Não prometer substituição de pessoa.** A promessa é a função executada, não a demissão de
alguém. Ver a linha vermelha no §07 da v1.

---

## 02 — O catálogo (só o que já está construído)

| # | Funcionário / peça | O que faz | Substitui / libera | Prazo | Base pronta |
|---|---|---|---|---|---|
| 0 | **Raio-X** | audita as conversas e o funil e mostra onde o dinheiro vaza | — | **48h** | Sales Coach + diagnóstico de funil |
| 1 | **Campanha de base** | reativa quem já comprou | mídia nova | dias | case Fran: R$9k em <10 dias |
| 2 | **Atendente** | responde, qualifica, escala pro humano, não deixa lead morrer | recepção/secretária no WhatsApp | 14 dias | Carol no ar |
| 3 | **SDR** | prospecta, qualifica, agenda, faz follow-up sem falhar | SDR júnior | 21 dias | arquitetura F1-F4 + n8n |
| 4 | **Analista de call** | pontua cada call do closer e devolve plano de treino | supervisor comercial | 7 dias | Sales Coach, 10 calls reais |
| 5 | **Memória da operação** | CRM com pipeline, histórico e visibilidade | planilha e cabeça do dono | 14 dias | arvex-crm em produção |
| 6 | **Secretário de reunião** | transcreve, resume e registra as reuniões | anotação manual | 3 dias | plugin Meet em produção |

**A ordem de venda não é a ordem da tabela.** É: **0 → 1 → 2 → 5 → 3/4**.
Raio-X cria o gap. Campanha de base traz caixa em dias e paga a confiança. Atendente é o coração.
CRM dá visibilidade. SDR e Analista são expansão.

---

## 03 — Como funciona o modelo

**Duas receitas, sempre juntas:**

| | O que é | Faixa de trabalho | Função |
|---|---|---|---|
| **Setup** | instalação, integração, treino do sistema com o negócio dele | **R$ 8.000 – 15.000** | caixa dos 90 dias |
| **Mensalidade** | operação, ajuste, infra, tokens, evolução | **R$ 1.500 – 3.000/mês** | MRR |

**Por que as duas e não uma:**
- só setup = projeto com começo e fim, sem MRR, e recomeça do zero todo mês;
- só mensalidade = demora demais para pagar R$50k em 90 dias;
- as duas = o setup financia dezembro e a mensalidade viaja com ele na turnê.

**A conta dos R$ 50k:** 5 clientes × R$12k de setup = R$60k, e cada um deixa R$2k/mês.
5 clientes = **R$10k/mês de MRR** ao fim do trimestre. É esse MRR que sustenta a turnê, não o setup.

**Escada de entrada:** o Raio-X pode ser vendido barato (R$ 500 – 1.500) ou dado numa negociação
avançada. Ele não é conteúdo grátis — é o que **cria o gap**: o cliente vê, com as próprias
conversas, onde está perdendo. Depois disso o setup se vende sozinho.

---

## 04 — Onde está a brecha, e ela não é o produto

O Vitor está certo: **tem gente, mas mal posicionada**. Mapeando quem já ocupa o espaço:

| Quem | O que vende | Por que não fecha a porta |
|---|---|---|
| **Plataformas** (Letalk, Kommo, BotConversa, Zenvia) | software self-service | vendem a ferramenta; a operação continua com o dono. Sem rosto |
| **Viver de IA** (146k, 2.500 empresas) | plataforma + **plug and play** + formação | escala exige superficialidade — não redesenha nada |
| **Alan Nicolas** (15 mil formados) | formar quem instala agente | forma concorrente médio em massa, que vende agente avulso |
| **Verticais de comercial** (advogado, plano de saúde) | processo humano — script, cadência, treino | escala com gente; vão plugar ferramenta de terceiro |
| **Vinícius Troncoso** | setup de IA para o operador solo | ensina o indivíduo; não entra em empresa |

🎯 **A brecha real tem duas partes, e a segunda é a mais barata de ocupar:**

**1. Ninguém constrói — todos plugam.** Ferramenta de terceiro num processo antigo. O diferencial
não é "eu uso IA" (todos vão usar em 12 meses); é **arquitetura própria versus ferramenta plugada**.

**2. Ninguém publica escopo e preço.** É tudo *"agende uma reunião"*, *"solicite um orçamento"*,
*"fale com um especialista"*. Num mercado queimado por promessa vaga, **oferta clara com escopo,
prazo, preço e garantia é diferenciação pura — custa zero e é percebida em três segundos.**

> **A jogada:** *"Atendente instalado em 14 dias. R$ X de setup + R$ Y por mês. Se em 14 dias não
> estiver respondendo, qualificando e fazendo follow-up sozinho, eu devolvo."*
>
> Escopo, prazo, preço e reversão de risco numa frase. Nenhum dos cinco acima faz isso.

---

## 05 — É o melhor modelo? Sim, com uma trava

**Por que sim:**
- vende o que **já existe** — custo marginal baixo, entrega rápida, prova imediata;
- gera caixa (setup) e ativo (MRR) ao mesmo tempo;
- cada entrega vira case, e ele hoje tem prova pública zero;
- o MRR é operável de qualquer lugar — condição da turnê;
- promessa 100% dentro do que ele controla.

**O risco único e real: o setup consome ele.** É a pergunta da capacidade em paralelo, ainda sem
resposta. Se cada instalação toma o Vitor por inteiro, isso não é oferta — é emprego novo com
vários chefes.

> **A trava, e ela é inegociável até haver dado: no máximo 3 instalações simultâneas.**
> Cliente 4 entra em fila com data. E cronometrar a instalação nº 1 e a nº 2 — se a segunda não
> custar menos, **o problema não é venda, é produto**, e nada de posicionamento resolve isso.

---

## 06 — O que ainda precisa ser testado

| # | Pergunta | Como responder |
|---|---|---|
| 1 | O preço aguenta? | levar R$12k a 3 conversas e ouvir a objeção real |
| 2 | O Raio-X cria gap? | rodar em 2 negócios e ver se pedem o próximo passo |
| 3 | Quanto custa a instalação nº 2? | cronometrar a 1ª e a 2ª |
| 4 | "Funcionário de IA" pega? | ver se o cliente devolve a expressão sem indução |
| 5 | Preço público ajuda ou queima? | publicar em uma peça e medir a qualidade do lead |

---

*v1 — 2026-09-09. Ajusta com evidência de campo; log de mudanças no arquivo de posicionamento.*
