# Sales Coach — Auditoria de ponta a ponta (2026-08-07)

> Escopo: o agente de coach de closer inteiro — ingestão, análise, memória, UI, segurança, operação.
> Referências de mercado: Gong, Attention, Fireflies/tl;dv. Referência interna: padrão de agente AIOX
> (fonte + ferramenta + escopo + memória + workflow + QA).

---

## 1. O que o sistema É hoje (mapa de ponta a ponta)

```
INGESTÃO                     ANÁLISE                      MEMÓRIA                      SAÍDA
─────────                    ────────                     ────────                     ──────
Plugin Meet (auto, bugado)   analyze-meeting (Sonnet 4.6) sales_knowledge (11 blocos,  Modal da call (notas,
Colar no modal (manual)      · rubrica 8 dimensões          27.7k chars, curada à mão)   diretor, missão)
tools/coach-import (lote,    · julgamento-raiz + missão   histórico por closer (12     Chat com a call
  dedupe, só eu rodo)        · JSON estrito, temp 0         últimas análises, auto)     (grounded + histórico)
                             · cérebro + histórico        conhecimento/ (7 casos, ICP,  Tela Cérebro (destilar
                               injetados no prompt          2 roteiros, DEF)             e gerir blocos)
                             coach-chat (idem)                                          Seletor por closer (admin)

SEGURANÇA: JWT + ownership + RLS ✅        CUSTO: ~R$0,45/análise ✅        DEPLOY: manual, sem testes ⚠️
```

**Estado dos dados no momento da auditoria:** 9 meetings — **3 analisadas, 6 pendentes**. As 6 pendentes
incluem TODAS as importadas nesta semana. Ou seja: **o cérebro novo (11 blocos) nunca rodou uma análise.**

## 2. Nota por camada

| Camada | Nota | Justificativa |
|---|---|---|
| **Conhecimento (cérebro)** | **9/10** | Único no mercado nesse nicho: ICP de 3 calls + 15 lives com citação, método da casa + SPIN + DEF + CLOSER curados contra evidência, antipadrões próprios (sinal simbólico 5/6 = 0). Gong não tem isso nem para enterprise sem meses de setup. |
| **Análise (prompt/função)** | 7/10 | Sólida: gold-standard validado, JSON estrito, auth real. Perde ponto por: modelo antigo (Sonnet 4.6), duplicação entre o SYSTEM (sequência vencedora hardcoded) e o cérebro (DEF), e **zero avaliação de qualidade** — ninguém mediu se a análise com cérebro é melhor que sem. |
| **Memória longitudinal** | 6/10 | Histórico por closer entrou ontem (bom desenho: continuidade de missão, erro repetido). Mas `stats_closer()` (spec 06/07), `closer_profiles` e métricas determinísticas **não existem**. Memória é 100% narrativa, 0% numérica. |
| **Ingestão** | **3/10** | O calcanhar. Plugin captura mal (a versão Tactiq foi melhor nas 5 calls reais); o fluxo que funcionou foi **colar transcrição no chat comigo** — não escala e não é produto. Diagnóstico do doc V2 (19/07) segue válido: "o gargalo não é análise, é ingestão". |
| **Loop de desfecho** | **2/10** | `resultado` é manual, trigger meeting→venda (ADR-19) nunca foi criada. O coach analisa e **nunca descobre se acertou**. Sem isso, "aprendizado" é acúmulo de opinião. |
| **Visão de gestão** | 2/10 | Seletor por closer entrou ontem (bom). Aba Direção (ADR-22), radar do time, conversão real: nada construído. |
| **Ação/proatividade** | **1/10** | O coach não age. Não notifica pós-call (ADR-23), não gera briefing pré-call, não cobra missão, não alerta call em risco. É 100% reativo: só existe quando alguém clica. |
| **Operação/organização** | 4/10 | 8 arquivos `.sql` acumulativos soltos em `docs/crm/`, docs de planejamento de 3 gerações misturados (mvp-brief, vision, V2, fase3), roteiro v0 e v1 coexistindo, SOP de vendas com preços errados, deploy manual sem teste. Funciona porque eu carrego o mapa na cabeça — isso é risco. |

## 3. Contra os grandes do mercado

| Capacidade | Gong | Attention | Fireflies/tl;dv | **Nosso coach** |
|---|---|---|---|---|
| Captura automática de toda call | ✅ bot em tudo | ✅ | ✅ (é o produto deles) | ❌ manual |
| Métricas determinísticas (talk ratio, monólogo, nº perguntas) | ✅ código | ✅ | parcial | ❌ (spec ADR-20 parada) |
| Scorecard por metodologia | ✅ genérico/configurável | ✅ | ❌ | ✅ **e calibrado no nicho** |
| Feedback qualitativo nível diretor | parcial (genérico) | parcial | ❌ | ✅ **melhor que todos** |
| Conhecimento profundo do comprador do nicho | ❌ | ❌ | ❌ | ✅ **único** |
| Memória longitudinal do rep | ✅ numérica | parcial | ❌ | ✅ narrativa / ❌ numérica |
| Ligação call → deal → receita | ✅ nativo | ✅ | ❌ | ❌ (a FK existe, a trigger não) |
| Dashboard de gestor | ✅ | ✅ | parcial | ❌ |
| Alertas e follow-up automático | ✅ | ✅ (e-mail pós-call) | parcial | ❌ |
| Coaching chega onde o rep vive (email/Slack/Zap) | ✅ | ✅ | ✅ | ❌ |

**Leitura honesta:** em **inteligência de coaching específica do nicho**, estamos acima de todos eles —
nenhum Gong da vida sabe o que é "campanha em dobro", "cicatriz de mentoria" ou que sinal simbólico
converteu 0 em 5. Em **tudo que é automação, captura, métrica e loop de receita**, estamos 2 a 3 anos
atrás. Somos um cérebro de elite dentro de um corpo que ainda depende de alguém colar texto numa caixa.

## 4. Contra o padrão de agente AIOX

Critério da casa (memória `feedback_criterio_valor_agente`): **agente = fonte + ferramenta + escopo
estreito**. Persona sozinha não produz nada.

| Elemento AIOX | Coach tem? |
|---|---|
| Persona definida | ✅ diretor comercial, calibrado em gold-standard |
| Fonte de verdade | ✅ calls + cérebro + histórico |
| Escopo estreito | ✅ calls de venda do nicho óptico |
| **Ferramentas / ações próprias** | ❌ não envia, não agenda, não cobra, não alerta |
| **Workflow** (pré-call → call → pós-call → follow-up) | ❌ só existe o meio |
| Memória | ✅ narrativa (cérebro + histórico) / ❌ numérica |
| **QA loop / avaliação** | ❌ nenhum eval; qualidade nunca medida |
| Governança de evolução | parcial — cérebro curado com aprovação (bom), mas sem processo escrito |

**Veredito:** hoje é um **analista especializado com memória** — excelente nisso — mas ainda não é um
agente no padrão AIOX. Falta a metade "age sozinho dentro de um workflow".

## 5. O problema de organização (concreto)

1. **Migrations soltas:** 8 `.sql` acumulativos em `docs/crm/` sem numeração nem registro do que já foi
   aplicado. Quem não for eu não sabe reproduzir o banco.
2. **3 gerações de docs coexistindo** sem marcação do que está vivo: `mvp-brief` (jun), `vision` (jun),
   `fase3-ARCHITECTURE` (jul/06), `SALES-COACH-V2-FABLE` (jul/19) — e nada aponta para o estado atual
   (cérebro, histórico, CLOSER), que só existe em mensagens de commit.
3. **Roteiro duplicado:** `roteiro-call-arvex-v0.md` e `roteiro-call-v1-TESTE.md` — v0 deveria estar
   arquivado.
4. **SOP oficial de vendas com preços errados** (5/7/10k vs 4.997/2.500/12.500 reais das calls).
5. **Duplicação de verdade no prompt:** a "sequência vencedora" hardcoded no SYSTEM do analyze-meeting
   sobrepõe o bloco DEF do cérebro — duas fontes para a mesma regra.

## 6. Plano recomendado (em ordem, com critério)

### P0 — esta semana (destrava tudo)
1. **Rodar as 6 análises pendentes** e ler as 6 contra o gold-standard (caso-02). O sistema está armado
   e não disparado; qualquer melhoria antes disso é especulação. *(única etapa que depende do teu login)*
2. **Desfecho real (ADR-19):** trigger venda→meeting + closer marca fechou/não/quando. É o que separa
   coach que acha de coach que sabe.
3. **Faxina de organização:** `docs/crm/sales-coach/` com `README.md` (mapa vivo do sistema),
   `migrations/` numeradas, `arquivo/` para docs mortos, v0 arquivado, SOP corrigido ou marcado como
   desatualizado.

### P1 — próximas 2 semanas
4. **Métricas determinísticas (ADR-20):** talk ratio, monólogo máximo, nº de perguntas do closer,
   % Implicação — em código, custo zero, por call. Teria pego os monólogos de 15-25 min sozinho.
5. **Briefing pré-call** (task #4 aberta): antes da reunião, o closer recebe lead + histórico + ICP +
   "as 3 perguntas que não podem faltar". Muda o coach de retrovisor para copiloto — e é o que nenhum
   concorrente entrega calibrado no nicho.
6. **Decidir a fonte de captura:** Tactiq bateu o plugin nas 5 calls reais. Ou conserta o parser do
   plugin, ou oficializa Tactiq→modal como fluxo. Uma fonte, não três.

### P2 — depois (com dados rodando)
7. Aba Direção (ADR-22) + `stats_closer()` (ADR-21) — comparar time exige análises acumuladas.
8. Notificação pós-call no WhatsApp (ADR-23) — o coaching indo até o closer.
9. Evolução do cérebro com aprovação (propostas geradas por lote de calls; você aprova na tela Cérebro).
10. Testar Sonnet 5 no analyze-meeting reanalisando o gold-standard (permitido pelo V2 §ADIADO).
11. Remover a duplicação SYSTEM × cérebro (uma fonte de verdade por regra).

## 7. Resumo executivo

**O que construímos até aqui é o cérebro mais especializado do mercado para call de venda de ótica —
dentro de um corpo que ainda não anda sozinho.** A distância para os grandes não está na inteligência
(aí estamos na frente); está em captura automática, métrica de código, loop de desfecho e proatividade.
Pelo padrão AIOX, é um analista de elite, não um agente completo: falta ele **agir** — briefar antes,
cobrar depois, aprender com o resultado real. O caminho P0→P2 acima transforma exatamente isso, nessa
ordem, sem inflar escopo.
