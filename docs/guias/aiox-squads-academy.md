# AIOX Squads — Resumo da Aula (Academia Lendária)

> Live com Lucas Charão | Academia Lendária
> Tema: Como criar squads dentro do AIOX

---

## O que é AIOX

Framework de orquestração de agentes de IA que roda sobre o Claude Code. Permite criar equipes de agentes especializados que se comunicam entre si, dividem tarefas e entregam resultados de forma autônoma.

**Diferença do Claude Code puro:** Claude Code sozinho é uma LLM focada em código. O AIOX adiciona orquestração — agentes chamam outros agentes, cada um com seu papel e suas tarefas definidas.

---

## As 3 Camadas do Sistema

### 1. Agentes Padrão AIOX (vêm instalados)

Os 8 agentes que acompanham o framework:

| Agente | Papel |
|--------|-------|
| `dev` | Desenvolvedor / implementação |
| `qa` | Testes e qualidade |
| `pm` | Product Manager |
| `po` | Product Owner |
| `sm` | Scrum Master |
| `architect` | Arquitetura técnica |
| `data-engineer` | Banco de dados |
| `devops` | Operações / git push exclusivo |

> **Nota:** `dev` pode fazer commit mas não push. Somente `devops` tem autoridade para push.

---

### 2. Squads (equipes customizadas)

Squad = equipe criada para um domínio específico. Cada squad tem namespace próprio, agentes próprios e tasks próprias.

**Exemplos do Alan (prints da live):**
```
Brand:agents:nano-banana-generator    → squad de branding
Editais:radar / scorer / critic       → squad para editais/licitações
CourseCreator:agents:course-architect → squad para criação de cursos
AioxDesign:agents:...                 → squad de design
```

---

### 3. Clones (personas ultra-leves de experts)

Arquivos pequenos (17–43 tokens) que injetam o raciocínio de um expert específico. Não têm workflows complexos — funcionam como "lentes" de perspectiva.

**Exemplos do Alan:**
```
hormozi-offers / hormozi-content / hormozi-copy
ray-dalio / naval-ravikant / charlie-munger / simon-sinek
gary-halbert / joe-sugarman / eugene-schwartz (copy)
molly-pittman / depesh-mandalia / ralph-burns (tráfego)
miller-sticky-brand / dan-harmon / joseph-campbell (branding)
```

---

## Como Criar um Squad

### Pré-requisitos
- Node.js instalado (sempre última versão)
- Claude Code instalado
- AIOX instalado via: `npx aiox-core install`

### Instalação do AIOX
```bash
npx aiox-core install
```
Wizard interativo em português:
- Modo: **Assistido** (recomendado)
- Tipo: **Greenfield** (projeto novo) ou **Brownfield** (projeto existente)
- LLM: Claude Code, Gemini CLI, Cursor, GitHub Copilot, Antigravity
- Linguagem: Next.js + React (recomendado) ou deixar o AIOX decidir

---

### Criar Squad via Squad Creator

**Comando no Claude Code:**
```
/AIOX:squad-creator
```

**Escolher escopo:**
- `user` → global, disponível em qualquer projeto
- `project` → apenas neste projeto

**Wizard de criação (5 etapas):**

#### Etapa 1 — Como fornecer o contexto
1. Colar texto ou documento existente
2. Indicar arquivos no computador
3. **Descrever o domínio verbalmente** ← mais usado
4. Google Drive
5. Outro

#### Etapa 2 — Descrever o domínio
O que informar para melhores resultados:
- **Domínio/nicho:** qual área de conhecimento o squad vai dominar
- **Objetivo principal:** o que o squad deve fazer
- **Agentes imaginados:** quais especialistas você quer na equipe
- **Workflows principais:** fluxos de trabalho esperados
- **Integrações:** APIs ou serviços externos
- **Público-alvo:** quem vai usar o squad

> Quanto mais detalhe, melhor o resultado. Input raso = output raso.

#### Etapa 3 — Revisar agentes propostos
O sistema propõe agentes baseados na descrição. Você pode:
- Aceitar todos
- Revisar individualmente
- Adicionar agentes novos (ex: "adicione um storytelling e um UX")

#### Etapa 4 — Revisar tasks
Para cada agente, o sistema cria tasks (funções específicas). Você pode:
- Aceitar todas
- Adicionar mais tasks

#### Etapa 5 — Gerar blueprint
O sistema gera o blueprint final com:
- Lista de agentes
- Quantidade de tasks
- Score de confiança (ex: 91%)

Squad pronto para uso.

---

### Usar o Squad

Chamar um agente pelo `@`:
```
@creative-director crie uma landing page para vender soluções de IA para empresários
```

O agente:
1. Faz perguntas de briefing
2. Aciona outros agentes do squad conforme necessário
3. Cada agente executa suas tasks em sequência
4. Entrega o resultado final

**Ver o output:**
- Rodar localmente: `localhost:3000` (para sites/landing pages)
- Abrir arquivo HTML diretamente
- Adicionar ao GitHub e subir num domínio

---

## O que a Aula NÃO Ensinou

- Como criar clones individualmente (só apareceram nos prints)
- O formato/estrutura interna de um clone
- Como clones se integram a squads programaticamente

> Para entender clones: ler o arquivo `tay-dantas` em `.claude/commands/AIOX/clone/`

---

## Diferença: Dev vs DevOps

| | Dev | DevOps |
|--|-----|--------|
| `git add` | Sim | Sim |
| `git commit` | Sim | Sim |
| `git push` | **Não** | **Sim (exclusivo)** |
| `gh pr create` | **Não** | **Sim (exclusivo)** |

---

## Economia de Tokens x Qualidade

| Modelo | Custo | Qualidade | Quando usar |
|--------|-------|-----------|-------------|
| Haiku | Baixo | Menor | Tarefas simples, rascunhos |
| Sonnet | Médio | Boa | Uso geral |
| Opus | Alto | Máxima | Desenvolvimento, projetos reais |

Trocar modelo no Claude Code: `/model`

> Se a IA demora para entregar, é porque está fazendo bem feito. Resultado rápido = resultado raso.

---

## Planos Claude Code

| Plano | Preço | Uso |
|-------|-------|-----|
| Básico | ~$17/mês | Poucos projetos simples |
| Intermediário | ~$100/mês | Uso regular |
| Pro | ~$200/mês | Uso intenso / múltiplos projetos |

Comparado a contratar um dev ou equipe: custo baixo.

---

*Fonte: Live Academia Lendária — Lucas Charão | 2026-05-14*
