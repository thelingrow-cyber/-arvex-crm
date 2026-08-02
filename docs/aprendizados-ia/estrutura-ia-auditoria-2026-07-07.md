# Auditoria da Estrutura de IA — ARVEX/AIOX

> Auditoria arquitetural com Fable 5 · 2026-07-07 (último dia da janela)
> Método: inventário real do filesystem vs. o que o harness declara — não confiança na documentação.
> Lentes: aulas Alan (Fable 5, AIOX squads/clones) + Perissé (arquitetura de agentes) + heurísticas do Vitor.

---

## 1. O diagnóstico em uma frase

**A estrutura não sofre de falta — sofre de fachada + subaproveitamento.** O harness gasta ~7-8k tokens de boot descrevendo maquinaria que não existe no repo, enquanto os ativos reais (memória, heurísticas, clones, personas) carregam a operação sem estarem formalmente ligados ao harness.

"Ficar mais completo" ≠ adicionar agentes. = fazer o **declarado** e o **real** convergirem, e ligar o que já é forte.

---

## 2. Inventário: declarado vs. real

| Camada | O que o harness declara | O que existe de verdade | Veredito |
|---|---|---|---|
| **AIOX core** | `.aiox-core/development/` com tasks, templates, workflows, checklists, constitution, KB, IDS registry | **1 arquivo só** (`core-config.yaml`). Todo o resto: inexistente | 🔴 Fachada — rules inteiras (ids-principles, workflow-execution, story-lifecycle em parte) apontam pro vazio |
| **Agentes AIOX** | 12 agentes com dependências executáveis | 12 **personas** em `.claude/commands/AIOX/agents/` — funcionam como lentes+autoridade, não como máquinas de task | 🟡 Real, mas é persona pura; as "tasks" referenciadas não existem |
| **Squad WebDesign** | 10 agentes, 35 tasks, 12 workflow steps (squad.yaml) | 10 personas .md; `tasks/` e `workflows/` **vazias** | 🟡 As personas entregam (landings saem e convertem), mas o yaml mente |
| **Clones** | — | `hormozi` + `tay-dantas`, estrutura completa (system/beliefs/heuristics/context/briefing/sources) | 🟢 Real e bem-feito. Só 2 de 7 do roadmap de maio |
| **Skills próprias** | — | `.claude/skills/` **vazia** | 🔴 Zero skills apesar de procedimentos repetidos toda semana |
| **Hooks** | 3 hooks .cjs | Existem E estão ligados em settings.local.json (PreCompact, PreToolUse, UserPromptSubmit) | 🟢 Real |
| **Memória + heurísticas** | — | MEMORY.md + ~45 memórias + catálogo de 23 heurísticas (extraído de 780 msgs reais) | 🟢 **O ativo mais forte.** É o que o Alan faz com as 200+ heurísticas dele |
| **Handoffs** | Compactação 379 vs 5k tokens | Funciona, 12 artefatos em `.aiox/handoffs/` | 🟢 Real — é o "isolamento de contexto" da Perissé aplicado |

**Boot atual:** CLAUDE.md (4,3KB) + 10 rules (23KB) = ~27KB ≈ **7-8k tokens por sessão**, grande parte descrevendo o que está 🔴 acima.

---

## 3. Por que isso importa (o insight do Alan aplicado)

A aula do Fable 5: *"quanto melhor o modelo, MENOS harness ele precisa"* e *"otimize PARA o modelo que fica"*. O custo da fachada não é só token — é **atenção**: o modelo lê "execute a task X conforme `.aiox-core/development/tasks/X.md`", vai buscar, não encontra, improvisa. Instrução que aponta pro vazio é pior que instrução nenhuma, porque treina o modelo a tratar o harness como decoração.

O que os melhores fazem (Alan, e o estudo ETH Zurich citado pela Perissé): harness **curto, à mão, 100% verdadeiro** (<200 linhas aumenta sucesso; gerado/inflado reduz 3% e encarece 20%).

---

## 4. Plano — 5 fases, EM SÉRIE (C7: 1 build por vez)

### F1 — Harness verdade 🎯 (HOJE, com Fable — janela fecha 07/07)
Reescrever `CLAUDE.md` + rules descrevendo **só o que existe**:
- **Cortar:** referências a constitution/gates, IDS (ids-principles.md inteira), workflow engine/chains, graph dashboard, code-intel, `npm run trace`, tasks executáveis inexistentes. CodeRabbit: manter só se ainda usado (verificar).
- **Manter (enxuto):** autoridades dos agentes (quem pode push — isso é real e valioso), handoff, mcp-usage, memória.
- **Ligar o forte ao harness:** heurísticas A1–A7 viram rule **condicional** (`paths: docs/landing*` — carrega só quando mexe em landing); B-série (protocolo de sessão) entra resumida no CLAUDE.md novo. B8 vira rule de delegação a subagente.
- Meta: boot de ~8k → ~3k tokens, 100% verdadeiro, otimizado pro Sonnet/Opus (os que ficam).

### F2 — Clone Gary Halbert (a lacuna de negócio)
Roadmap de maio dizia Miller→Halbert→Brunson. **Atualização:** a mensagem da marca já foi definida no brand book ("O Futuro Instalado") — Miller perdeu urgência. **Halbert primeiro:** copy de resposta direta serve as landings da Cindy (dinheiro real hoje) e os 20 vids/dia. Método já documentado (aula 2026-05-25 §4). Validar no primeiro asset real antes do próximo clone.

### F3 — Skills próprias (procedimento repetido → skill invocável)
1. `destilar-aula` — o loop inbox→resumo/delta/ação que já rodou 4× à mão. Formato exato já existe nos destilados.
2. `landing-cindy` — sistema visual herdado + heurísticas A1–A7 + checklist mobile como procedimento.
É isso que "os maiores" fazem: o Alan não relembra o procedimento toda vez — invoca.

### F4 — Squad: consertar antes de criar
**NÃO criar squad de copy** — WebDesign já tem copywriter/storytelling-expert/cro-analyst (duplicar = anti-padrão reusar-não-recriar). Decisão em duas portas:
- Personas puras bastam (evidência: bastaram até hoje) → limpar squad.yaml (tirar stats falsos) e seguir.
- Squad NOVO só quando a operação 20 vids/dia virar gargalo real → aí sim squad **Conteúdo** (roteiro/ganchos/distribuição) usando clones como lentes.

### F5 — Autonomia noturna (loop confiável)
Já desenhado (2026-07-07): **cloud routine** (claude.ai/code/routines) é a única opção que sobrevive fechar o laptop; cron mínimo 1h = checkpoint natural por ciclo (fazer→revisar→commitar, padrão B6). Fable arquiteta o plano de véspera → routine com Sonnet 5 executa de noite → revisão de manhã. Pré-requisito: F1 (a routine parte do harness — harness fachada = agente noturno confuso sem ninguém pra corrigir).

---

## 5. O que NÃO fazer (ruído descartado)

- LangGraph/grafos nível 4 (Perissé) — AIOX já abstrai o nível 3; overengineering.
- 7 clones de uma vez — 1 por vez, validado em asset real.
- Recriar `.aiox-core` completo — a operação real deste repo é docs+landings+CRM; o framework completo vive no repo do AIOX/Lingrow, não aqui.
- Squad de copy paralelo ao WebDesign.
- `/loop` ou rotinas com modelo caro (Fable) — loop é pra execução mecânica barata.

---

## 6. Métricas de sucesso

| Fase | Métrica |
|---|---|
| F1 | Boot ≤3k tokens · zero referências a arquivo inexistente · nada de função perdida |
| F2 | Clone Halbert usado num asset real (landing/carrossel) com output aprovado sem retrabalho de copy |
| F3 | Próxima aula destilada via skill em 1 comando · próxima landing passa checklist A1–A7 sem reprovação mobile |
| F4 | squad.yaml verdadeiro OU 1º workflow real preenchido |
| F5 | 1 noite de routine com commits revisáveis de manhã, zero intervenção |

---

*Auditoria: Orion (@aiox-master) com Fable 5 · fontes: filesystem real + aulas destiladas + heuristicas-vitor.md*
