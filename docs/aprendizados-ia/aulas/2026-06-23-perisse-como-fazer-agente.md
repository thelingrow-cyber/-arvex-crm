# Como fazer um agente de IA — Júlia Perissé (Bom d.ia)

> Fonte: newsletter "Bom d.ia" (@perissejul.ia) · 23/06/2026
> Tipo: aula introdutória de arquitetura de agentes
> Destilado em: 2026-06-25 · com @analyst (Atlas)

---

## 1. Resumo

- **Pare de usar "finja que você é X"** — persona rasa sem dados/ferramentas/definição técnica gera um especialista que finge saber.
- **As 4 peças de qualquer agente:** cérebro (LLM) · ferramentas (descrição + execução) · instruções (`.md`/`.py`) · memória (`.md` simples → banco relacional → banco vetorial/RAG).
- **Escada de arquitetura (4 níveis):** ① loop único → ② linha de montagem sequencial (erro se propaga) → ③ **orquestrador centralizado** (gerente valida e manda refazer) → ④ grafos de estado cíclicos (LangGraph, determinístico).
- **Por que orquestrador economiza token:** contexto cresce de forma quadrática (cada passo relê tudo). Resolve com **isolamento de contexto**, **exposição seletiva de ferramentas** e **prefix caching**.
- **Rodar 24/7:** onde (VPS vs serverless) + gatilho (horário fixo, **webhook**, fila, chamada direta).
- **Dado de ouro (estudo ETH Zurich):** `AGENTS.md` gerado por IA reduz sucesso 3% e encarece 20%. Curto e à mão (<200 linhas) aumenta sucesso 4%.

---

## 2. Delta de aplicação — o que muda pro MEU sistema

**Eu não sou o aluno dessa aula. Sou o estudo de caso dela.** ~80% do que ela ensina eu já opero no AIOX:

| A news ensina | Eu já tenho |
|---|---|
| Não usar "finja ser X", dar dados técnicos | Clones com `beliefs + heuristics + sources` |
| Orquestrador centralizado (nível 3) | `aiox-master` orquestrando os agentes |
| Subagentes especialistas | Squad WebDesign (10 agentes focados) |
| Isolamento de contexto p/ poupar token | `agent-handoff.md` já compacta persona (379 vs 5K) |
| Memória `.md` lida/escrita pelo agente | `MEMORY.md` + memórias de projeto |
| `AGENTS.md` curto e à mão > gerado por IA | Meu AGENTS.md: 65 linhas, à mão, em PT |
| RAG/vetorial buscando no Obsidian | SecondBrain — semente, ainda não conectado |

**Sinais reais (novo/acionável):**
1. 🎯 "Rodar 24/7 + webhook" = o mapa exato do problema travado da **Carol** (Railway desligado → falta servidor + gatilho webhook WhatsApp).
2. 💸 Tática "rascunhar agente no ChatGPT, finalizar no Claude" — economia de token.
3. 🧠 RAG no Obsidian — semente p/ build futuro.

**Ruído pra mim agora:** LangGraph / grafos cíclicos / montar agente do zero em Python (nível 4). O AIOX já abstrai. Overengineering pro momento.

---

## 3. Ação aplicada

- ✅ Este destilado inaugurou a pasta `aprendizados-ia/` e o loop de captura.
- ✅ Confirmado: o trecho "24/7 + webhook" é a especificação do que falta na Carol → entra como referência no build do projeto âncora.
