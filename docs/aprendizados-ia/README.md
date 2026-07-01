# Aprendizados IA — Sistema Operacional

> Meu sistema para virar um dos melhores em **criar projetos de IA**.
> Não é uma biblioteca de aulas. É uma máquina de transformar aprendizado em ativo construído.

---

## A tese (leia toda vez que bater a ansiedade de "tô ficando pra trás")

Ninguém vira foda em IA por **consumir melhor**. Vira por **construir em volume, com feedback real.**
Consumo refinado te deixa informado. Reps de construção que encaram o mundo te deixam elite.

**Regra de ferro:** nenhum aprendizado entra aqui sem um projeto ativo onde ele aterrissa. Aula sem aplicação = acumulação disfarçada de progresso.

---

## As 2 engrenagens

```
┌─ ENGRENAGEM 1: CONSTRUÇÃO (primária) ──────────────┐
│  Sempre 1 projeto de IA sendo CONSTRUÍDO e SHIPPADO  │
│  Volume de builds > volume de aulas                  │
└──────────────────────────────────────────────────────┘
          ▲ alimenta                    │ gera a dúvida certa
          │                             ▼
┌─ ENGRENAGEM 2: CAPTURA (a serviço da 1) ───────────┐
│  inbox → destilar → aplicar HOJE num build ativo     │
└──────────────────────────────────────────────────────┘
```

A captura existe **para servir a construção**, nunca o contrário.

---

## Projeto âncora atual

**Carol — Agente SDR (Epic 3).** É o build mais avançado e o de maior retorno (clientes e dinheiro reais).
Status: vive em Railway, desligado. Falta: servidor sempre-ligado + gatilho webhook (WhatsApp → acorda → responde) + system prompt/refs/Redis.

> **Regra anti-dispersão:** 1 projeto âncora por vez. Quer 20 projetos no ano? Construa 1 de cada vez, 20 vezes. Em SÉRIE, nunca em paralelo — dispersão é a ameaça nº1.

---

## Como uso esta pasta

| Pasta | Para quê |
|-------|----------|
| `inbox/` | jogo aqui TODA aula/news/transcrição/PDF crua, sem processar |
| `aulas/` | destilados prontos: **resumo + delta de aplicação + 1 ação** |

**O loop, toda vez:**
1. **Capturar** → joga no `inbox/`
2. **Destilar** → resumo limpo + "o que isso muda no que EU faço" (sinal vs ruído)
3. **Aplicar** → 1 ação concreta num build ativo. Sem isso, não está concluído.

---

## Inventário — o que eu JÁ tenho rodando (não estou atrás)

As 3 camadas do AIOX já em produção:

| Camada | Meus ativos |
|--------|-------------|
| **Agentes** | 12 do framework AIOX que opero (dev, qa, architect, pm, devops…) |
| **Squad próprio** | **WebDesign** — 10 agentes especialistas + tasks + workflows (`squads/webdesign/`) |
| **Clones** | **Hormozi** e **Tay Dantas** — system + beliefs + heuristics + sources (`.claude/clones/`) |
| **Agente real** | **Carol** (SDR) — base de conhecimento + system prompt + provas sociais |
| **Memória** | `MEMORY.md` + memórias de projeto · **Handoffs** que compactam contexto (379 vs 5K tokens) |
| **AGENTS.md** | 65 linhas, à mão, em PT — já no padrão que estudo da ETH Zurich valida como o melhor |

---

## Trilha — próximos builds candidatos (em série, após Carol shippar)

- [ ] Carol 24/7 no ar (âncora atual)
- [ ] Agente que consulta o SecondBrain (Obsidian) via RAG/busca vetorial
- [ ] Agente-researcher de novidades de IA — curado, 1x/semana (só DEPOIS do loop rodando)
- [ ] Novos clones de experts (ratio do Alan: mais clones que squads)

---

*Sistema desenhado com @analyst (Atlas) — 2026-06-25*
