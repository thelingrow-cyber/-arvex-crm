> ⚠️ **DOCUMENTO ARQUIVADO — não use como referência.**
> Superado pelo estado atual do sistema. Ponto de entrada: [../README.md](../README.md)
> Mantido só como registro histórico.

# Visão Completa — Sales Coach como MENTOR (não transcritor)

**Autor:** Vitor + Orion · Data: 2026-06-27 · Status: visão/roadmap (NÃO altera o escopo do MVP)
**Princípio-mãe:** a IA **nunca analisa uma call isolada**. Sempre responde *"comparado às suas últimas N reuniões, você evoluiu ou regrediu?"*. Isso transforma avaliação em **mentor personalizado** que acompanha o closer por meses/anos.

> Estes exemplos são ilustrativos — o conteúdo exato vai sendo refinado com o uso.

---

## É um AGENTE (memória + estado), não um prompt
- **MVP:** análise de 1 call isolada (chamada estruturada ao Claude). Sem memória.
- **Visão:** lê histórico + **perfil que evolui**, analisa no contexto, e **reescreve o perfil**. Memória persistente = agente.
- O que faz virar agente não é IA mais esperta — é **memória do closer**.

## Duas bases de conhecimento (não confundir)
1. **Sales Brain** — playbook Cindy + frameworks → "o que é uma boa reunião". (pgvector, Fase 2)
2. **Memória do Closer** — histórico das calls + **perfil cognitivo evolutivo** → "quem ESTE closer é". (tabela `closer_profiles`, Fase 3) ← maior diferencial

## Comparação longitudinal = matemática + narrativa
- Deltas (+8% rapport vs últimas 20) = **determinístico** (média/subtração das notas já armazenadas). Barato e confiável.
- A IA entra só pra **narrar o padrão** ("negocia desconto cedo"). 
- **MVP já é forward-compatible:** guardamos nota/dimensão + closer_id + resultado desde a 1ª call → a memória se constrói depois sem retrabalho.

---

## Fluxo completo (3 momentos)
### 1. Pré-call (Coach) — Fase 4
Input: Instagram do lead, formulário, faturamento, tipo de negócio, origem, produto a ofertar.
Output: resumo do lead · perfil comportamental provável · hipóteses de dor · objeções prováveis · perguntas recomendadas · armadilhas · cases parecidos · objetivo da call.

### 2. Durante (Copilot) — Fase 5
Tempo real, 2ª tela: "interrompeu 3x", "lead citou equipe 4x — explore", "buying signal", "ainda não perguntou faturamento", "hora de transicionar". (Precisa de streaming dedicado — projeto à parte.)

### 3. Pós-call (o núcleo) — relatório em 11 blocos
1. **Resumo executivo** (objetivo, resultado, produto, objeções, próximos passos)
2. **Notas por dimensão** (rapport, escuta, diagnóstico, controle, construção de valor, transição, fechamento, objeções, confiança percebida, naturalidade, comunicação) — *MVP começa com 8; expande*
3. **Linha do tempo** (minuto a minuto: conexão, dor entregue, apresentou cedo, objeção, negociação) — *requer timestamps na transcrição*
4. **O que fez muito bem**
5. **Oportunidades perdidas** (ex.: lead citou "2ª unidade" e você mudou de assunto)
6. **Perguntas que faltaram**
7. **Comparação com você mesmo** (↑↓ % vs últimas N) ← genial, determinístico
8. **Perfil do closer** (pontos fortes / atenção — evolui no tempo)
9. **Exercício da semana** (treino, não curso: "5s de silêncio após o preço")
10. **Biblioteca inteligente** (calls parecidas: Marília, João…)
11. **Próxima reunião** (corrige o erro de hoje)

### Relatório mensal (Fase 3)
Conversão · ticket médio · objeções principais · tempo médio · maior evolução · maior gargalo · plano do próximo mês.

---

## Modelo Cognitivo do Closer (o maior diferencial — Fase 3)
Tabela `closer_profiles` que a IA atualiza após cada call, identificando padrões profundos:
- "Evita perguntas que geram desconforto."
- "Cria conexão rápido, mas demora a assumir controle."
- "Excelente em diagnóstico, perde valor ao negociar cedo."
- "Vende melhor para perfis analíticos que impulsivos."
- "Nas últimas 40 calls, confiança subiu; próximo salto = sustentar valor antes de conceder desconto."

Deixa de ser avaliação de reunião → vira **mentor que acompanha por meses/anos**. Esse é o fosso real.

---

## v2 da EXPERIÊNCIA — "mentor, não relatório" (Vitor, 28/06)
A experiência deve parecer que o closer saiu da call e foi conversar com um **diretor comercial experiente**. Análise em CAMADAS, não relatório estático.

**🔑 PADRÃO-RAIZ (o mais importante):** antes de qualquer análise, a IA responde *"Se eu fosse o diretor comercial e tivesse acabado de assistir essa reunião, qual o feedback MAIS importante pra esse closer?"*. **Toda a análise nasce dessa resposta** → coerência e priorização (uma voz, não um painel de métricas). É a 1ª etapa do prompt.

**Camadas (ordem que o closer vê):**
1. **Tela executiva** — primeiro uma MENSAGEM (não notas): o feedback do "diretor" + 🟢 probabilidade de fechamento % + 📈 comparado às últimas 20 (+X%).
2. **4 cartões** — 🟢 maior acerto · 🔴 maior erro · 💡 oportunidade perdida · 🎯 próximo treino (1 só).
3. **Replay inteligente** — timeline clicável (00:00 abertura · 08:32 1ª dor · 17:44 oportunidade · 28:15 interrompeu · 36:52 buying signal · 44:11 apresentação · 48:39 objeção). ⚠️ exige timestamps na transcrição (legenda do Meet tem; texto colado não).
4. **Chat com a IA sobre a call** 🔥 — closer pergunta ("onde perdi a venda?", "negociei cedo?", "compara com a Marília", "qual pergunta faltou?") e a IA responde olhando a call inteira. É o que vira AGENTE de verdade; feature mais viciante.
5. **Evolução** — barras de progresso (não notas), +% por dimensão; "sua maior evolução foi diagnóstico".
6. **Perfil cognitivo** — estilo do closer aprendido das últimas ~60 calls (constrói confiança rápido / evita confrontar objeção / negocia cedo / vende melhor p/ experientes). Fase 3.
7. **Comparação consigo** (não ranking) — Março 7,2 → Hoje 9,1; a IA narra o salto e prevê o próximo.
8. **Biblioteca inteligente** — "essa call lembra Marília, Carlos, Eduardo — clique p/ comparar".
9. **Plano da próxima call** — UMA missão só (ex.: "descubra impacto financeiro+emocional+urgência ANTES de apresentar").

**Notas técnicas:** probabilidade % é estimada pela IA — só fica confiável quando CALIBRADA contra resultados reais (mais um motivo do rótulo obrigatório). Chat = endpoint que recebe pergunta + transcrição + análise como contexto (simples). Replay depende de timestamps → reforça captura via legendas do Meet (Fase 2). North star do produto: o closer sai pensando "agora sei exatamente o que fazer na próxima call".

## Mapa de fases (não inchar o MVP)
| Fase | Entrega | Status |
|------|---------|--------|
| 1-2 (MVP) | loop: 1 call → 8 notas + insights + resultado. **Acumula o dataset.** | planejado (S1-S4) |
| 3 | comparação longitudinal + relatório mensal + `closer_profiles` (modelo cognitivo) + 11 blocos | visão |
| 4 | Coach pré-call | visão |
| 5 | Copilot tempo real | visão |

**Regra:** o MVP prova o loop e alimenta o ativo; a inteligência de mentor (Fase 3) só faz sentido depois que há dados acumulados. Construir o MVP certo = habilitar tudo isso sem retrabalho.
