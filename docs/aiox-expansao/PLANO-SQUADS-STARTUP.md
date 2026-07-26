# PLANO DE EXPANSÃO AIOX — A Startup 1-Person Completa

> **Autor:** Orion (@aiox-master) · 2026-07-19
> **Objetivo:** transformar o AIOX de "software house" em **empresa completa de 1 pessoa**: engenharia (já existe) + marketing + comercial + segurança + research + finanças + branding.
> **Como executar:** cada squad abaixo tem um blueprint resumido e um **prompt pronto** para rodar com Opus via `@squad-creator`. Rodar UM squad por vez (heurística do Vitor: 1 build por vez).

---

## 1. O QUE JÁ EXISTE (não recriar — IDS: REUSE > ADAPT > CREATE)

### Core AIOX (`.aiox-core/development/agents/` — L2, imutável, extend-only)
| Agente | Persona | Cobre |
|---|---|---|
| @aiox-master | Orion | Orquestração geral, criação de componentes |
| @dev, @qa, @architect, @devops, @data-engineer | Dex, Quinn, Aria, Gage, Dara | Engenharia completa |
| @pm, @po, @sm | Morgan, Pax, River | Produto e processo |
| @analyst | Alex | Pesquisa e análise (genérica, leve) |
| @ux-design-expert | Uma | UX/UI |
| @squad-creator | Craft | **A fábrica de squads — usar para criar tudo abaixo** |

### Squad WebDesign (`squads/webdesign/` — molde estrutural)
10 agentes, task-first, workflow 12 passos. **Já cobre:** copywriter (copy de páginas), brand-strategist (marca escopo-página), seo-specialist, cro-analyst, storytelling-expert.
→ Os novos squads NÃO duplicam esses papéis; referenciam ou adaptam (mudança <30%, regra IDS).

### Clones (`.claude/clones/`)
- **hormozi** — ofertas, LTGP:CAC, unit economics → fonte de conhecimento p/ Comercial e Finanças
- **tay-dantas** — marca de creator, posicionamento → fonte p/ Branding

### Padrão estrutural de squad (copiar do WebDesign)
```
squads/{nome}/
  squad.yaml              # manifest: name, namespace, agents, stats, distribution
  README.md
  agents/{id}.md          # YAML compacto: agent, persona (name/role/style/principles), tasks
squads/.designs/{nome}-blueprint.yaml   # blueprint completo: agents+tasks (input/output)+workflow
```
Cada agente vira skill `{Namespace}:agents:{id}` automaticamente. Squads são L4 (mutável sempre).

---

## 2. O MAPA — 6 SQUADS NOVOS + 2 BACKLOG

```
                        👑 @aiox-master (Orion)
                                │
   ┌──────────┬──────────┬──────┴─────┬───────────┬───────────┬──────────┐
   │ ENGENHARIA│ MARKETING│  COMERCIAL │ SEGURANÇA │  RESEARCH │ FINANÇAS │
   │ (core+    │ (novo)   │  (novo)    │ (novo)    │  (novo)   │ (novo)   │
   │ webdesign)│ 6 agentes│  5 agentes │ 2 agentes │  3 agentes│ 3 agentes│
   └──────────┴──────────┴────────────┴───────────┴───────────┴──────────┘
                                │
                          BRANDING (novo, 3 agentes)
              Backlog: LEGAL (1) · CUSTOMER SUCCESS (2)
```

### Ordem de criação recomendada (por impacto no negócio ARVEX)
| P | Squad | Por quê primeiro |
|---|---|---|
| P0 | **security** | CRM em produção com dados reais de clientes; menor squad (rápido); vira gate opcional no SDC |
| P0 | **marketing** | Media buyer é dor ativa (contas Google rodando); alimenta a máquina de aquisição |
| P1 | **comercial** | Closers/SDRs reais + Sales Coach + agente Carol já existem no CRM — o squad conecta tudo |
| P1 | **research** | Multiplica a qualidade de todos os outros (todo squad consome research) |
| P2 | **financas** | Módulo financeiro do CRM já especificado; squad opera em cima |
| P2 | **branding** | Brand book já existe (docs/ecossistema); squad mantém e aplica |

---

## 3. BLUEPRINTS DETALHADOS

---

### 3.1 SQUAD `security` 🔐 — namespace `Security` (P0)

**Missão:** segurança contínua de tudo que a ARVEX roda em produção (arvex-crm, landings, plugins, Supabase). Não é agente de pentest ofensivo — é AppSec + OpSec defensivo do próprio stack.

**Agentes (2):**

1. **`appsec-auditor`** (lead) — persona sugerida: *Vega, Sentinel*
   - Tasks:
     - `audit-codigo` — varredura OWASP top-10 no diff ou módulo indicado (XSS, injection, auth) · input: path/PR · output: relatório com severidade e fix sugerido
     - `audit-rls` — auditoria das policies RLS do Supabase (tabela a tabela, quem lê/escreve o quê) · output: matriz de acesso + gaps
     - `audit-secrets` — caça a secrets hardcoded no repo e histórico git · output: lista + plano de rotação (regra ADR-3.3: secret nunca no chat)
     - `threat-model` — modelagem de ameaça de feature nova (STRIDE-lite) · input: story/arquitetura · output: riscos priorizados
   - Integrações: skill `/security-review` nativa do Claude Code como motor do `audit-codigo`.

2. **`opsec-guardian`** — persona: *Locke*
   - Tasks:
     - `audit-acessos` — revisão de contas/roles (Supabase users, Vercel, Google) · output: quem tem acesso a quê + revogações sugeridas
     - `incident-runbook` — cria/mantém runbook de resposta a incidente (vazamento, conta comprometida)
     - `dependency-audit` — CVEs em dependências (npm audit / pip) · output: relatório com upgrades priorizados

**Workflow (4 passos):** threat-model (feature nova) → audit-codigo + audit-rls (paralelo) → audit-secrets + dependency-audit (paralelo) → relatório consolidado com verdict PASS/CONCERNS/FAIL (mesmo vocabulário do @qa).

**Gancho no SDC:** stories que tocam auth/RLS/pagamento DEVEM passar por `Security:agents:appsec-auditor` antes do qa-gate (documentar como extensão, sem alterar L2).

---

### 3.2 SQUAD `marketing` 📈 — namespace `Marketing` (P0)

**Missão:** aquisição completa — tráfego pago, conteúdo orgânico, e-mail, analytics. O braço que enche o topo do funil da ARVEX e da marca pessoal.

**Agentes (6):**

1. **`marketing-director`** (lead) — persona: *Maya*
   - Tasks: `briefing-campanha` (objetivo, verba, ICP, canal) · `plano-de-canal` (mix orgânico×pago) · `aprovacao-campanha` (revisa entregáveis antes de ir ao ar)

2. **`media-buyer`** — persona: *Buck* ⚠️ o mais operacional
   - Tasks:
     - `auditoria-conta` — audita conta ativa (Google Ads/Meta): estrutura, verba, CPA, quality score · output: relatório + quick wins
     - `estrutura-campanha` — desenha campanhas/conjuntos/anúncios · output: plano de campanha pronto p/ subir
     - `otimizacao-semanal` — rotina de leitura de métricas e realocação de verba · output: log de decisões
     - `plano-de-teste` — matriz de testes criativos (hipótese/métrica/verba)
   - **Pré-requisito de infra (EXCLUSIVO @devops):** instalar MCP de Google Ads (`*search-mcp google ads` → `*add-mcp`). Enquanto não houver MCP, o media-buyer opera em modo "co-piloto": gera o plano e o Vitor executa na plataforma. O blueprint deve declarar os dois modos.

3. **`copy-chief`** — persona: *Halbert* (homenagem)
   - Diferença do `copywriter` do WebDesign (que é copy DE PÁGINA): o copy-chief é **direct response cross-canal** — anúncios, e-mails, VSLs, scripts de vídeo, hooks de criativo — e **revisor final de todo copy da empresa** (chief).
   - Tasks: `copy-anuncios` (hooks+primary text+headlines por ângulo) · `copy-emails` (cadências) · `roteiro-vsl` · `review-copy` (nota+ajustes em qualquer copy, inclusive do WebDesign)
   - Fontes: clone hormozi (ofertas), catálogo de heurísticas do Vitor.

4. **`social-content-strategist`** — persona: *Nina*
   - Tasks: `calendario-conteudo` (alinhado à tese "20 vids/dia" da marca pessoal) · `roteiro-short` (reels/tiktok com hook-retencao-cta) · `repurpose` (1 conteúdo → N formatos)

5. **`email-crm-marketer`** — persona: *Reva*
   - Tasks: `cadencia-nutricao` (sequências por segmento) · `broadcast` (e-mails pontuais de campanha) · `automacao-fluxo` (desenho de fluxos — integração futura com CRM)

6. **`analytics-tracker`** — persona: *Dot*
   - Tasks: `plano-de-tracking` (UTMs, pixels, eventos) · `dashboard-kpis` (CPL, CPA, ROAS por canal) · `relatorio-semanal` (síntese executiva)

**Workflow (7 passos):** briefing-campanha → plano-de-canal → [estrutura-campanha ∥ copy-anuncios ∥ calendario-conteudo] → plano-de-tracking → aprovacao-campanha → (campanha no ar) → [otimizacao-semanal ∥ relatorio-semanal] em loop.

---

### 3.3 SQUAD `comercial` 🤝 — namespace `Comercial` (P1)

**Missão:** converter leads em receita. Conecta os ativos reais que já existem: closers (Gabriel/Thalita), SDR (Carol + agente IA no CRM), Sales Coach (aba Reuniões), módulo financeiro.

**Agentes (5):**

1. **`sales-director`** (lead) — persona: *Blake*
   - Tasks: `diagnostico-funil` (taxas etapa a etapa do pipeline no CRM) · `metas-forecast` (metas por closer + previsão) · `rituais-comerciais` (agenda de dailies/reviews do time real)

2. **`offer-strategist`** — persona: *Grand* (usa clone hormozi como fonte primária)
   - Tasks: `desenho-oferta` (value equation, garantias, bônus, naming) · `grand-slam-audit` (nota da oferta atual vs framework $100M) · `pricing-oferta` (âncoras, parcelamento, order bump)

3. **`closer-coach`** — persona: *Wolf*
   - Tasks: `analise-call` (transcreve/analisa call real via Sales Coach — objeções, momentos-chave) · `roleplay-script` (roteiros de treino por objeção) · `playbook-fechamento` (talk track por etapa)
   - Integração: transcrições do Meet Transcriber plugin + Sales Coach Fase 3 (memória do closer).

4. **`sdr-playbook-manager`** — persona: *Cady*
   - Tasks: `cadencia-followup` (regras de no-show, remarcação, não-resposta — dor mapeada nos ditados de 15/jul) · `prompt-agente-sdr` (mantém/evolui o system prompt da Carol IA) · `qualificacao-icp` (critérios de passagem SDR→closer)

5. **`proposal-writer`** — persona: *Quill*
   - Tasks: `proposta-comercial` (proposta formatada por oferta/ticket) · `contrato-base` (minuta padrão — revisão jurídica humana obrigatória) · `follow-up-proposta` (sequência pós-envio)

**Workflow (6 passos):** diagnostico-funil → desenho-oferta → [playbook-fechamento ∥ cadencia-followup] → proposta-comercial → metas-forecast → loop mensal (analise-call semanal alimenta tudo).

---

### 3.4 SQUAD `research` 🔬 — namespace `Research` (P1)

**Missão:** "The Deep Researcher" — revisão sistemática multi-fonte com síntese citada. Diferente do @analyst (leve, interno ao SDC): este squad produz relatórios de nível consultoria, com protocolo e citações verificáveis.

**Agentes (3):**

1. **`deep-researcher`** (lead) — persona: *Darwin*
   - Tasks:
     - `protocolo-revisao` — define pergunta, critérios de inclusão/exclusão de fontes, estratégia de busca (PRISMA-lite) · output: protocolo de 1 página
     - `busca-sistematica` — executa buscas em N fontes (EXA p/ web geral, Apify p/ sites/redes específicos, Context7 p/ docs técnicas) · output: corpus de fontes numeradas
     - `sintese-com-citacoes` — relatório final: achados numerados, cada afirmação com [n] apontando pra fonte, seção de limitações · output: `docs/research/{tema}-{data}.md`
   - Regra constitucional Art. IV (No Invention): **toda afirmação rastreia a uma fonte ou é marcada como inferência.**

2. **`evidence-auditor`** — persona: *Pierce*
   - Tasks: `qualidade-fontes` (classifica fontes: primária/secundária/opinião; vieses) · `checagem-citacoes` (amostra as citações do relatório e verifica se a fonte diz aquilo mesmo) · verdict APPROVED/NEEDS-REVISION no relatório

3. **`competitive-intel`** — persona: *Sun*
   - Tasks: `analise-concorrente` (REUSE: template `competitor-analysis-tmpl.yaml` do core) · `monitor-mercado` (mudanças de players — insumo p/ mapa de posicionamento já existente em docs/ecossistema)

**Workflow (5 passos):** protocolo-revisao → busca-sistematica → sintese-com-citacoes → checagem-citacoes (gate) → entrega. Material cru grande → subagente destila (heurística já registrada).

---

### 3.5 SQUAD `financas` 💰 — namespace `Financas` (P2)

**Missão:** caixa, unit economics e precificação da ARVEX (co-produção 50/50 + ofertas próprias).

**Agentes (3):**

1. **`cfo`** (lead) — persona: *Sterling*
   - Tasks: `visao-caixa` (posição consolidada, runway, projeção 90d) · `unit-economics` (LTGP:CAC por oferta/expert — framework do clone hormozi) · `decisao-investimento` (análise go/no-go de gasto: verba de tráfego, contratação, ferramenta)

2. **`controller`** — persona: *Ledger*
   - Tasks: `fluxo-caixa-mensal` (entradas/saídas categorizadas — integra módulo financeiro do CRM: vendas+parcelas) · `conciliacao` (CRM × extrato) · `relatorio-mensal` (DRE simplificado + comissões de closers)

3. **`pricing-analyst`** — persona: *Costa*
   - Tasks: `precificacao-oferta` (custo de entrega, margem, ancoragem) · `analise-margem` (margem real por expert/oferta) · `cenarios` (simulação: e se o ticket fosse X, churn Y)

**Workflow (4 passos):** fluxo-caixa-mensal → unit-economics → visao-caixa → relatorio-mensal (loop mensal); precificacao sob demanda quando nasce oferta (conecta `Comercial:offer-strategist`).

---

### 3.6 SQUAD `branding` 🎭 — namespace `Branding` (P2)

**Missão:** marca institucional ARVEX + marca pessoal do Vitor ("O Futuro Instalado"). Mantém e aplica o brand book existente — não recria do zero.

**Agentes (3):**

1. **`brand-director`** (lead) — persona: *Iris*
   - Tasks: `guardia-brand-book` (mantém `docs/ecossistema/brand-book-marca-pessoal.md` como fonte de verdade; audita conteúdo/página contra ele) · `decisao-marca` (naming, arquitetura de marcas ARVEX×Viziom×marca pessoal)

2. **`positioning-strategist`** — persona: *North* (usa clone tay-dantas como fonte primária)
   - Tasks: `mapa-posicionamento` (mantém o mapa de 12 players já existente) · `tese-narrativa` (evolui a big idea "instalar o futuro") · `angulo-de-entrada` (posicionamento por ICP/oferta)

3. **`identity-keeper`** — persona: *Forma*
   - Tasks: `sistema-visual` (mantém o sistema visual das landings — herda regras de `feedback_landing_cindy_sistema_visual`) · `audit-consistencia` (varre materiais publicados vs guidelines)
   - ADAPT (<30%) do `brand-strategist` do WebDesign: aquele cria marca por-projeto; este governa as marcas da casa.

**Workflow (3 passos):** tese-narrativa → guardia-brand-book → audit-consistencia (trimestral).

---

### 3.7 BACKLOG (não criar agora — registrar a intenção)

- **Squad `legal`** (1 agente: `contract-reviewer`) — minutas de co-produção 50/50, termos de uso do SaaS. Sempre com revisão humana de advogado.
- **Squad `customer-success`** (2 agentes: `cs-strategist`, `onboarding-designer`) — já existe módulo CS no CRM (Sabrina, kanban CS); criar quando a carteira crescer.

---

## 4. COMO CRIAR CADA SQUAD (processo padrão — repetir 6×)

**Pré-requisitos gerais (1× só):**
1. `@devops` — avaliar MCP de Google Ads p/ media-buyer (`*search-mcp` → `*add-mcp`). Não bloqueia: media-buyer nasce em modo co-piloto.
2. Nada mais — squads são L4, sem risco de boundary.

**Processo por squad (rodar com Opus, um por vez):**

```
Passo 1 — Ativar a fábrica:      /AIOX:agents:squad-creator
Passo 2 — Design:                *design-squad  (usar o prompt do squad abaixo; fonte = seção 3 deste doc)
                                 → gera squads/.designs/{nome}-blueprint.yaml
Passo 3 — Revisão do blueprint:  Vitor lê o blueprint (5 min) — ajusta personas/tasks se quiser
Passo 4 — Criação:               *create-squad → gera squads/{nome}/ completo (squad.yaml, agents/*.md, README)
Passo 5 — Validação:             *validate-squad (schema + padrões AIOX)
Passo 6 — Teste de fumaça:       ativar 1 agente do squad novo e rodar 1 task real pequena
Passo 7 — Registro:              @aiox-master *ids register squads/{nome}/squad.yaml
Passo 8 — Commit:                git commit (local; push só via @devops)
```

**Estimativa por squad:** 1 sessão de Opus (design+create+validate) + 1 teste real. Não paralelizar.

---

## 5. PROMPTS PRONTOS PARA O OPUS (copiar e colar, 1 por sessão)

### 5.1 Security
```
/AIOX:agents:squad-creator
*design-squad

Contexto: ARVEX roda em produção o arvex-crm (Supabase+Vercel, dados reais de
clientes), landings e plugins. Não existe nenhuma função de segurança.
Crie o squad "security" (namespace Security) conforme a spec na seção 3.1 de
docs/aiox-expansao/PLANO-SQUADS-STARTUP.md — 2 agentes (appsec-auditor lead,
opsec-guardian), tasks e workflow como especificado. Use squads/webdesign/ como
referência estrutural. O appsec-auditor deve integrar a skill /security-review
como motor da task audit-codigo. Verdict vocabulary igual ao @qa
(PASS/CONCERNS/FAIL). Depois *create-squad e *validate-squad.
```

### 5.2 Marketing
```
/AIOX:agents:squad-creator
*design-squad

Contexto: ARVEX compra tráfego (contas Google ativas), produz conteúdo orgânico
(tese 20 vids/dia da marca pessoal) e não tem função de marketing estruturada.
Crie o squad "marketing" (namespace Marketing) conforme seção 3.2 de
docs/aiox-expansao/PLANO-SQUADS-STARTUP.md — 6 agentes (marketing-director lead,
media-buyer, copy-chief, social-content-strategist, email-crm-marketer,
analytics-tracker). ATENÇÃO: media-buyer nasce em modo co-piloto (gera planos,
humano executa na plataforma) até @devops instalar MCP de ads; declarar os dois
modos no agente. copy-chief NÃO duplica o copywriter do WebDesign — é direct
response cross-canal e revisor final; fonte de conhecimento: clone hormozi
(.claude/clones/hormozi/) e docs/aprendizados-ia/heuristicas-vitor.md.
Depois *create-squad e *validate-squad.
```

### 5.3 Comercial
```
/AIOX:agents:squad-creator
*design-squad

Contexto: ARVEX tem operação comercial real — closers Gabriel e Thalita, SDR
Carol + agente IA no CRM (docs/agente-sdr/), Sales Coach na aba Reuniões,
transcrições de call via plugin Meet Transcriber. Crie o squad "comercial"
(namespace Comercial) conforme seção 3.3 de
docs/aiox-expansao/PLANO-SQUADS-STARTUP.md — 5 agentes (sales-director lead,
offer-strategist, closer-coach, sdr-playbook-manager, proposal-writer).
offer-strategist usa clone hormozi (.claude/clones/hormozi/) como fonte
primária. sdr-playbook-manager é dono do system prompt da Carol
(docs/agente-sdr/carol-system-prompt.md). contrato-base sempre com aviso de
revisão jurídica humana obrigatória. Depois *create-squad e *validate-squad.
```

### 5.4 Research
```
/AIOX:agents:squad-creator
*design-squad

Contexto: preciso de um "deep researcher" que rode revisão sistemática de várias
fontes e sintetize em relatório com citações verificáveis — nível acima do
@analyst do core. Crie o squad "research" (namespace Research) conforme seção
3.4 de docs/aiox-expansao/PLANO-SQUADS-STARTUP.md — 3 agentes (deep-researcher
lead, evidence-auditor, competitive-intel). Ferramentas de busca: EXA
(mcp__docker-gateway__web_search_exa), Apify (site específico), Context7 (docs
técnicas) — conforme .claude/rules/mcp-usage.md. Regra dura (Constituição Art.
IV): toda afirmação do relatório rastreia a uma fonte numerada ou é marcada
como inferência. Relatórios salvos em docs/research/. competitive-intel REUSA o
template competitor-analysis-tmpl.yaml do core. Material cru grande → destilar
via subagente, nunca ler tudo no contexto principal.
Depois *create-squad e *validate-squad.
```

### 5.5 Finanças
```
/AIOX:agents:squad-creator
*design-squad

Contexto: ARVEX é co-produção 50/50 com experts + ofertas próprias; módulo
financeiro do CRM (vendas+parcelas) já especificado/implantado. Crie o squad
"financas" (namespace Financas) conforme seção 3.5 de
docs/aiox-expansao/PLANO-SQUADS-STARTUP.md — 3 agentes (cfo lead, controller,
pricing-analyst). Frameworks de unit economics (LTGP:CAC) vêm do clone hormozi
(.claude/clones/hormozi/). controller integra os dados do módulo financeiro do
CRM. Nenhum agente executa pagamento/transferência — só analisa e recomenda.
Depois *create-squad e *validate-squad.
```

### 5.6 Branding
```
/AIOX:agents:squad-creator
*design-squad

Contexto: já existem brand book (docs/ecossistema/brand-book-marca-pessoal.md —
categoria "O Futuro Instalado"), mapa de posicionamento (12 players) e sistema
visual de landings validado. Crie o squad "branding" (namespace Branding)
conforme seção 3.6 de docs/aiox-expansao/PLANO-SQUADS-STARTUP.md — 3 agentes
(brand-director lead, positioning-strategist, identity-keeper). REGRA: este
squad GOVERNA e APLICA os ativos de marca existentes, não os recria.
positioning-strategist usa clone tay-dantas (.claude/clones/tay-dantas/) como
fonte primária. identity-keeper é ADAPT (<30%) do brand-strategist do
WebDesign: aquele cria marca por-projeto, este governa as marcas da casa.
Depois *create-squad e *validate-squad.
```

---

## 6. REGRAS TRANSVERSAIS (valem para todos os squads novos)

1. **Boundary:** squads vivem em `squads/` (L4) — nunca tocar `.aiox-core/` (L1/L2).
2. **Autoridades preservadas:** push/PR/MCP continuam EXCLUSIVOS de @devops; nenhum agente novo ganha essas permissões.
3. **IDS:** após criar cada squad, `*ids register`; antes de criar qualquer task nova em squad futuro, `*ids check`.
4. **No Invention (Art. IV):** agentes de research/finanças/comercial nunca inventam número ou citação — ou rastreia fonte, ou marca como estimativa.
5. **Dados sensíveis:** finanças e comercial leem dados do CRM via acesso já existente (SUPABASE_DB_URL por env — nunca colar credencial em chat/arquivo).
6. **Handoff entre squads:** usar o protocolo de `.claude/rules/agent-handoff.md` (artefato ≤500 tokens em `.aiox/handoffs/`).
7. **Anti-dispersão:** criar na ordem P0→P2 e SÓ avançar quando o squad anterior tiver rodado 1 entrega real. Squad criado e nunca usado = desperdício.

---

## 7. CHECKLIST MESTRE DE EXECUÇÃO

- [ ] P0 · Squad security criado, validado e com 1ª auditoria real (RLS do arvex-crm) rodada
- [ ] P0 · Squad marketing criado, validado e com 1ª auditoria de conta real do media-buyer
- [ ] · @devops avaliou MCP de Google Ads (paralelo, não bloqueia)
- [ ] P1 · Squad comercial criado, validado e closer-coach analisou 1 call real
- [ ] P1 · Squad research criado, validado e 1 revisão sistemática entregue com citações
- [ ] P2 · Squad financas criado, validado e 1º fluxo-caixa-mensal gerado do CRM
- [ ] P2 · Squad branding criado, validado e 1 audit-consistencia rodado
- [ ] Todos registrados no IDS (`*ids stats` confirma)
- [ ] Backlog legal + customer-success registrado (sem criar)
