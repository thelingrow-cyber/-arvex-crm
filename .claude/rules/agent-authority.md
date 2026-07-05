# Agent Authority — Delegation Matrix

## Operações EXCLUSIVAS

| Agente | Exclusivo |
|--------|-----------|
| @devops (Gage) | `git push` (qualquer forma) · `gh pr create/merge` · MCP add/remove/config · pipelines CI/CD · releases |
| @pm (Morgan) | `*create-epic` · `*execute-epic` · EPIC-{ID}-EXECUTION.yaml · requirements gathering · spec writing |
| @po (Pax) | `*validate-story-draft` (checklist 10 pontos) · contexto de stories em epics · priorização de backlog |
| @sm (River) | `*draft`/`*create-story` a partir de epic/PRD · seleção de template de story |
| @aiox-master | Governança do framework; executa qualquer task; pode sobrepor boundaries quando necessário |

## @dev (Dex)

- PODE: `git add/commit/status/branch/checkout/merge` (local), `stash/diff/log`; atualizar File List e checkboxes da story.
- BLOQUEADO: `git push` e `gh pr *` (→ @devops); gestão de MCP; alterar AC/escopo/título da story.

## @architect (Aria) × @data-engineer (Dara)

- Aria: arquitetura de sistema, seleção de tecnologia, data architecture de alto nível, padrões de integração, complexity assessment.
- Dara (delegado de Aria): DDL detalhado, query optimization, RLS, estratégia de índices, migrations. NÃO faz: arquitetura de sistema, código de aplicação, frontend, git.

## Fluxos de delegação

- Push: qualquer agente → `@devops *push`
- Schema: @architect decide tecnologia → @data-engineer implementa DDL
- Story: `@sm *draft → @po *validate → @dev *develop → @qa *qa-gate → @devops *push`
- Epic: `@pm *create-epic → *execute-epic → @sm *draft` (por story)

## Escalation

1. Agente não completa task → @aiox-master. 2. Quality gate falha → volta a @dev com feedback específico. 3. Violação constitucional → BLOCK até corrigir. 4. Conflito de boundary → @aiox-master media.
