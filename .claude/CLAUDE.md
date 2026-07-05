# Synkra AIOX — Claude Code Rules

Meta-framework que orquestra agentes de IA para desenvolvimento full stack. Trabalhe sempre dentro desta arquitetura.

## Constitution — princípios inegociáveis

Gates automáticos bloqueiam violações. Documento completo: `.aiox-core/constitution.md`
I CLI First · II Agent Authority (NON-NEGOTIABLE) · III Story-Driven · IV No Invention · V Quality First (MUST) · VI Absolute Imports (SHOULD)

## Agentes

Ativação: `@agent` ou `/AIOX:agents:{agent}`. Master: `@aiox-master`. Comandos com prefixo `*` (`*help`, `*create-story`, `*task {name}`, `*exit`).
Com agente ativo: seguir a persona, os workflows e a perspectiva desse agente durante toda a interação.

| Agente | Persona | Escopo |
|--------|---------|--------|
| `@dev` | Dex | Implementação de código |
| `@qa` | Quinn | Testes e qualidade |
| `@architect` | Aria | Arquitetura e design técnico |
| `@pm` | Morgan | Product Management |
| `@po` | Pax | Product Owner, stories/epics |
| `@sm` | River | Scrum Master |
| `@analyst` | Alex | Pesquisa e análise |
| `@data-engineer` | Dara | Database design |
| `@ux-design-expert` | Uma | UX/UI design |
| `@devops` | Gage | CI/CD, git push (EXCLUSIVO) |

## Metodologia

- **Story-driven:** todo desenvolvimento parte de uma story em `docs/stories/`; marcar checkboxes [ ]→[x] ao concluir; manter a seção File List; implementar exatamente os acceptance criteria.
- **Qualidade:** seguir padrões existentes do codebase; error handling abrangente; testes para toda funcionalidade nova (incluindo edge cases); antes de marcar completo: `npm run lint` + `npm run typecheck` + testes.
- **Tasks/workflows de `.aiox-core/development/` são executáveis:** seguir as instruções à risca; `elicit: true` exige interação com o usuário (nunca pular por eficiência); apresentar opções claras e validar respostas.

## Estrutura

```
.aiox-core/development/  agents · tasks · workflows · templates · checklists
docs/                    stories · prd · architecture · guides
```

## Boundary framework × projeto (L1–L4)

| Camada | Mutabilidade | Paths |
|--------|-------------|-------|
| L1 Core | NEVER | `.aiox-core/core/`, `.aiox-core/constitution.md`, `bin/aiox.js`, `bin/aiox-init.js` |
| L2 Templates | NEVER (extend-only) | `.aiox-core/development/{tasks,templates,checklists,workflows}/`, `.aiox-core/infrastructure/` |
| L3 Config | Mutável | `.aiox-core/data/`, `agents/*/MEMORY.md`, `core-config.yaml` |
| L4 Runtime | SEMPRE | `docs/stories/`, `packages/`, `squads/`, `tests/` |

Toggle: `core-config.yaml → boundary.frameworkProtection` (default: true). Autoridades: `.claude/rules/agent-authority.md`.

## Rules e subsistemas

- Regras contextuais em `.claude/rules/` carregam automaticamente (frontmatter `paths:` = carga condicional).
- Code intelligence é opcional com graceful fallback (`isCodeIntelAvailable()` antes de operar; indisponível → resultado base sem falhar). Diagnóstico: `aiox doctor`.
- Graph dashboard: `aiox graph --deps|--stats [--format=ascii|json|html|mermaid|dot] [--watch [--interval=N]]`.

## Git & GitHub

- Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`) com story ID: `feat: implement IDE detection [Story 2.1]`. Commits atômicos e focados.
- `gh` CLI para PRs/issues (`gh auth status` para verificar). Push e criação/merge de PR são EXCLUSIVOS de @devops.

## Comandos comuns

- Master: `*help` · `*create-story` · `*task {name}` · `*workflow {name}` · `*execute-checklist {checklist}`
- Dev: `npm run dev` · `npm test` · `npm run lint` · `npm run build`
- Debug: `export AIOX_DEBUG=true` · logs em `.aiox/logs/agent.log` · trace: `npm run trace -- workflow-name`

## Diretrizes Claude Code

- Tools nativas sempre (Grep/Glob/Read/Write/Edit — nunca grep/find/cat via bash); batch de tool calls independentes em paralelo; preferir editar arquivo existente a criar novo.
- Atualizar checkboxes da story imediatamente após concluir tarefas; manter contexto da story ativa na sessão.
- Em falhas: reportar contexto do erro + sugestão de recuperação/rollback; documentar fixes manuais necessários.
- Docs sincronizadas com o comportamento real; breaking changes documentados com destaque.

---
*Synkra AIOX Claude Code Configuration v2.1 — boot otimizado 2026-07-05*
