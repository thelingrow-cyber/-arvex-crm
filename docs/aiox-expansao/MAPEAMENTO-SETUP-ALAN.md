# MAPEAMENTO — Setup do Alan (aula) × Nosso setup (ARVEX)

> **Fonte:** 6 screenshots da aula do Alan Nicolas (AIOX Squad Prime), 2026-07-19 — telemetria real do ambiente dele (projetos: synkra-hub, allfluence, aiox-stage, academia, mmos).
> **Objetivo:** identificar o que ele tem em agentes/clones/mecanismos que NÃO temos, avaliar a fundo o que vale trazer pra ARVEX e o que ignorar.
> **Autor:** Orion (@aiox-master).

---

## 0. NOSSO INVENTÁRIO ATUAL (baseline)

- **Agentes core (12):** aiox-master, analyst, architect, data-engineer, dev, devops, pm, po, qa, sm, squad-creator, ux-design-expert
- **Squads (1):** webdesign (10 agentes)
- **Clones (2):** hormozi, tay-dantas
- **Tasks (203):** SDC completo, db-*, audit-*, security-checker etc.

---

## 1. O QUE O ALAN TEM (extraído das telas)

### Comandos / squads em uso (tela 1)
`po`, `devops`, `execute-story`, `dev`, **`squad-creator:squad-chief`**, `review-story`, **`sinkra-squad:sinkra-chief`**, `apply-qa-fixes`, `validate-story-draft`, `close-story`, `develop-story`, `architect`, `qa`, **`c-level:cso`**, **`clickup-ops-squad:clickup-chief`**, `sm`, `pm`, **`team-ops-squad:task-manager`**, `handoff`, **`c-level:cfo-architect`**, **`claude-code-mastery:skill-craftsman`**, **`db-sage-squad:db-sage`**, **`c-level:coo-orchestrator`**, **`roundtable`**, **`wave-execute`**

### Subagents (telas 3-4)
Explore, dev, general-purpose, devops, qa, analyst, architect, sm, pm, Plan, claude-code-guide, po, **`mmos-daniel/breno/tim/barbara`**, **`dr-orchestrator`**

### Shell runners (tela 2) — infra do framework dele
sinkra-map, validate-skill, validate-squad, sinkra-validate, runtime, mmos, pipeline-bootstrap, copy, loader, **books**, **metrics**, phase-execution

### Skills por namespace (tela 5)
AIOX:agents:* (mesmos nossos) + **`nano-banana-generator`** (em 3 namespaces: AIOX, AioxDesign, Brand) + **`Editais:{radar,scorer,regulamento,critic}`** + **`CourseCreator:course-architect`**

### Clones — biblioteca de mentores (telas 5-6)
hormozi-offers, hormozi-content, hormozi-copy, michael-gerber, eugene-schwartz, joe-mathews, design-chief, greg-nathan, dan-mall, naming-strategist, ries-positioning, ray-dalio, ads-analyst, molly-pittman, derek-sivers, cartographer, traffic-masters-chief, thiago-finch, patrick-lencioni, brene-brown, research-head, domain-scout, omar-santos, claudia-bittencourt, reid-hoffman, board-chair, simon-sinek, charlie-munger, oalanicolas, naval-ravikant, mark-siebert, peter-kim, marcus-carey, shannon-runner, dirber, busterer, fuzzer, ab-05/09/10, command-generator, etl-{extractor,chief,transformer}

---

## 2. MATRIZ DE DECISÃO — TRAZER / ADAPTAR / IGNORAR

### 🟢 CATEGORIA A — MECANISMOS DE ORQUESTRAÇÃO (maior lacuna, maior valor)
Não são agentes; são *padrões de execução*. É o que mais separa o setup dele do nosso.

| Item | O que faz | Temos? | Veredito |
|---|---|---|---|
| **`roundtable`** | Mesa redonda: N agentes/clones debatem uma decisão, cada um sua perspectiva, converge num veredito | ❌ | **TRAZER (P0)** — decisão estratégica multi-perspectiva. Casa com clones. Altíssimo valor. |
| **`wave-execute`** | Executa tarefas em "ondas" paralelas (fan-out de subagents coordenado) | ❌ | **TRAZER (P1)** — throughput. Nós já paralelizamos manualmente; formalizar. |
| **`dr-orchestrator`** | Deep Research orchestrator — coordena pesquisa multi-fonte | ❌ | **TRAZER = é o lead do squad `research`** que já planejei. Renomear deep-researcher→dr-orchestrator. |
| **Story-cmds** (`execute-story`, `review-story`, `close-story`, `develop-story`, `validate-story-draft`, `apply-qa-fixes`) | SDC como comandos slash diretos (não só tasks) | ⚠️ temos as *tasks*, não os *comandos* | **ADAPTAR (P1)** — criar os wrappers slash. Deixa o SDC fluido. |
| **`handoff`** como comando | Compacta contexto ao trocar de agente | ✅ (temos como *regra*) | Já coberto por `.claude/rules/agent-handoff.md`. |

### 🟢 CATEGORIA B — C-LEVEL SUITE (a camada que falta acima dos squads)
Exatamente a espinha da "startup 1-person completa". Ficam ACIMA dos squads — os executivos que decidem, os squads executam.

| Item | Papel | Temos? | Veredito |
|---|---|---|---|
| **`c-level:cso`** | Chief Strategy Officer — estratégia, prioridades, tese | ❌ | **TRAZER (P0)** — hoje esse papel é o próprio Vitor no chat. Formalizar. |
| **`c-level:coo-orchestrator`** | Chief Operating — orquestra execução entre squads | ❌ | **TRAZER (P0)** — o maestro dos 6 squads do plano anterior. |
| **`c-level:cfo-architect`** | Chief Financial — decisão de capital | ❌ | **ADAPTAR** — vira o lead `cfo` do meu squad `financas`, elevado a C-level. |
| (sugerido) `c-level:cmo` | Chief Marketing | ❌ | Lead do squad `marketing` elevado. |

→ **Decisão de arquitetura:** criar um **squad `c-level`** (o "board") como camada de topo. O COO orquestra os squads operacionais; CSO/CFO/CMO trazem a visão de cada eixo.

### 🟢 CATEGORIA C — CLONES DE MENTORES (temos 2, ele tem ~30)
Curadoria para ARVEX (co-produção de infoprodutos + marca pessoal + SaaS). Ignorados os irrelevantes.

| Clone | Domínio | Por que trazer pra ARVEX |
|---|---|---|
| **michael-gerber** (E-Myth) | Sistematizar negócio | ⭐ Perfeito p/ "1-person": transformar o Vitor-operador em sistema. |
| **eugene-schwartz** | Copy (níveis de consciência) | Copy chief de elite; alimenta squad marketing. |
| **molly-pittman** | Tráfego pago | Alimenta o media-buyer. |
| **ries-positioning** (Al Ries) | Posicionamento | Alimenta squad branding + mapa de posicionamento existente. |
| **charlie-munger** | Mental models / decisão | Membro de peso do `roundtable`. |
| **naval-ravikant** | Leverage, wealth, produto | Tese de ativos/alavancagem (venture builder). |
| **reid-hoffman** | Blitzscaling | Escala do SaaS. |
| **simon-sinek** | Propósito / narrativa | Branding institucional. |
| **dan-mall** | Design systems | Squad webdesign / SaaS UI. |
| **naming-strategist** | Naming | Já é dor recorrente (naming SaaS óptico). |
| **thiago-finch** | Creator BR | Contexto BR, marca pessoal. |
| **claudia-bittencourt** | (BR) | Avaliar quem é antes. |
| **hormozi-{offers,copy,content}** | Hormozi desmembrado por função | ⚠️ **ADAPTAR** — nós temos hormozi monolítico; desmembrar melhora precisão de uso. |
| ray-dalio, patrick-lencioni, brene-brown, board-chair | Princípios / times / liderança | **Backlog** — úteis no roundtable quando o time crescer. |

### 🟢 CATEGORIA D — CAPACIDADES / FERRAMENTAS
| Item | O que faz | Veredito |
|---|---|---|
| **`nano-banana-generator`** | Geração de imagem (Gemini "nano banana") — 3 namespaces | ⭐ **TRAZER (P0)** — criativos de anúncio, imagens de landing, thumbnails, assets de marca. Impacto imediato em marketing/webdesign. |
| **`CourseCreator:course-architect`** | Arquitetura de cursos | **TRAZER (P1)** — Vitor co-produz **infoprodutos**. Encaixa direto no core do negócio. |
| **`claude-code-mastery:skill-craftsman`** | Cria skills novas (meta) | **ADAPTAR** — parcialmente coberto por `@squad-creator` + `*create`. Avaliar o delta. |
| **`command-generator`** | Gera comandos slash | **TRAZER (P2)** — acelera criação dos story-cmds da Cat. A. |

### 🟡 CATEGORIA E — SEGURANÇA (bate com squad `security` P0 do plano)
Os clones **peter-kim** (Hacker Playbook), **omar-santos**, **marcus-carey**, e os runners **fuzzer / busterer / dirber / shannon-runner** formam um squad de **AppSec/pentest ofensivo**.

- **Veredito:** **ADAPTAR com cautela.** Nosso squad `security` planejado é *defensivo* (auditar nosso próprio CRM). Os clones ofensivos do Alan só entram se formos fazer pentest autorizado do nosso stack. Trazer peter-kim/omar-santos como *fontes de conhecimento* do appsec-auditor — sim. Ferramentas ofensivas (fuzzer/buster) — só com escopo de teste autorizado.

### 🔴 CATEGORIA F — IGNORAR (específico do negócio dele / já temos)
| Item | Motivo |
|---|---|
| **`Editais:{radar,scorer,regulamento,critic}`** | Licitações públicas — negócio do Alan, irrelevante pra ARVEX. |
| **`mmos-daniel/breno/tim/barbara`** | Clones de pessoas do time dele. |
| **`oalanicolas`** | Clone do próprio Alan. |
| **`sinkra-squad` / sinkra-*.sh / runtime.sh / loader.sh** | Infra interna do framework dele ("Sinkra"). Nós já temos o nosso core. |
| **`clickup-ops-squad`** | Integração ClickUp — Vitor usa Notion, não ClickUp. |
| **`db-sage-squad`** | Já temos @data-engineer (Dara) equivalente. |
| **`team-ops-squad:task-manager`** | Gestão de tarefas de time — reavaliar se/quando houver time operando no AIOX. |
| **`etl-{extractor,chief,transformer}`** | Pipelines ETL — só se surgir necessidade de dados em volume. |
| **`ab-05/09/10`, `busterer`, `dirber`** | Provável instrumentação interna/variantes de teste dele. |
| **`books.sh` / `metrics.sh`** | Telemetria própria do ambiente dele (o que gerou esses screenshots). |

---

## 3. PLANO DE ADOÇÃO (ordenado, encaixado no plano de squads existente)

**Onda 0 — Capacidades soltas de impacto imediato (não dependem de squad):**
1. **`nano-banana-generator`** — geração de imagem. Criar como skill/agente reutilizável (usável por marketing, webdesign, branding).
2. **`roundtable`** — mecanismo de decisão multi-clone. Requer ≥3 clones bons (já temos 2 + trazer munger/naval/gerber).

**Onda 1 — Camada C-level (o "board"):**
3. Squad **`c-level`**: coo-orchestrator (maestro dos squads) + cso + cfo + cmo. Fica acima dos 6 squads do `PLANO-SQUADS-STARTUP.md`.

**Onda 2 — Enriquecer os squads já planejados com os clones certos:**
4. `research`: adotar nome/estrutura `dr-orchestrator` + research-head + domain-scout.
5. `marketing`: molly-pittman, eugene-schwartz, ads-analyst como fontes/agentes.
6. `branding`: ries-positioning, simon-sinek, dan-mall.
7. Desmembrar `hormozi` → offers/copy/content.

**Onda 3 — Fluidez do SDC + meta:**
8. Story-cmds slash (`execute-story`, `review-story`, `close-story`…) via command-generator.
9. **`CourseCreator:course-architect`** — infoprodutos (avaliar como squad próprio).
10. `wave-execute` — formalizar paralelização.

**Backlog:** clones de liderança (dalio, lencioni, brené), squad security ofensivo (só com escopo autorizado), skill-craftsman (avaliar delta vs squad-creator).

---

## 4. LEITURA ESTRATÉGICA (o gap real)

O Alan não tem "mais agentes" só por ter — ele tem **três camadas que nós não temos**:

1. **Camada executiva (C-level)** acima dos squads — quem *decide*, não só quem *executa*. Nós paramos nos squads operacionais.
2. **Mecanismos de deliberação e paralelização** (`roundtable`, `wave-execute`, `dr-orchestrator`) — como os agentes *trabalham juntos*, não só individualmente.
3. **Biblioteca de clones como "conselho consultivo"** — 30 mentores que ele convoca sob demanda; nós temos 2.

A capacidade isolada de maior ROI imediato é **`nano-banana-generator`** (geração de imagem — vira criativo/asset toda hora). A mudança estrutural de maior alcance é a **camada C-level + roundtable**, porque é literalmente a "empresa que decide sozinha" que o Vitor está perseguindo.

**O que NÃO copiar:** a tentação de trazer os 30 clones e 10 squads de uma vez. Regra anti-dispersão continua: capacidade só entra quando um squad/decisão real vai consumi-la.
