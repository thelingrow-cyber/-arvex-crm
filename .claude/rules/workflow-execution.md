# Workflow Execution — 4 Workflows Primários

**Task-first:** workflows são tasks conectadas (definições em `.aiox-core/development/tasks/`), não agentes conectados. Task validada é lei: executar conforme configurada, com todas as dependências, independente do executor. Agentes abaixo são os executores padrão.

## 1. Story Development Cycle (SDC) — primário

| Fase | Agente | Task | Saída/Decisão |
|------|--------|------|---------------|
| Create | @sm | create-next-story | `{epicNum}.{storyNum}.story.md` (Draft) |
| Validate | @po | validate-next-story | checklist 10 pontos: GO (≥7) ou NO-GO com fixes |
| Implement | @dev | dev-develop-story | modos Interactive/YOLO/Pre-Flight · CodeRabbit self-healing ≤2 iterações |
| QA Gate | @qa | qa-gate | 7 checks: PASS / CONCERNS / FAIL / WAIVED |

Status: Draft → Ready → InProgress → InReview → Done (detalhes: `story-lifecycle.md`).

## 2. QA Loop — review iterativo pós-gate

`@qa review → verdict → @dev fix → re-review` · máx 5 iterações (`autoClaude.qaLoop.maxIterations`) · estado em `qa/loop-status.json`.
Comandos: `*qa-loop {storyId}` · `*qa-loop-review` · `*qa-loop-fix` · `*stop-qa-loop` · `*resume-qa-loop` · `*escalate-qa-loop`.
Verdicts: APPROVE → Done · REJECT → @dev corrige · BLOCKED → escala imediato.
Triggers de escalation: max_iterations_reached · verdict_blocked · fix_failure · manual_escalate.

## 3. Spec Pipeline — pré-implementação

Fases: 1 Gather (@pm → requirements.json) → 2 Assess (@architect → complexity.json; skip se source=simple) → 3 Research (@analyst → research.json; skip se SIMPLE) → 4 Spec (@pm → spec.md) → 5 Critique (@qa → critique.json) → 6 Plan (@architect → implementation.yaml; se APPROVED).
Complexidade = 5 dimensões 1-5 (scope, integration, infrastructure, knowledge, risk): ≤8 SIMPLE (gather→spec→critique) · 9-15 STANDARD (6 fases) · ≥16 COMPLEX (6 fases + ciclo de revisão).
Critique: ≥4.0 APPROVED → Plan · 3.0-3.9 NEEDS_REVISION → 5b · <3.0 BLOCKED → @architect.
Gate constitucional (Art. IV — No Invention): toda afirmação do spec.md rastreia a FR-*/NFR-*/CON-*/research finding. Nada inventado.

## 4. Brownfield Discovery — assessment de legado (10 fases)

Coleta 1-3: @architect (system-architecture.md) · @data-engineer (SCHEMA.md + DB-AUDIT.md, se houver DB) · @ux-design-expert (frontend-spec.md).
Draft/validação 4-7: @architect (technical-debt-DRAFT.md) → reviews @data-engineer + @ux → @qa (qa-review.md; gate APPROVED | NEEDS WORK → volta à fase 4).
Finalização 8-10: @architect (assessment final) → @analyst (TECHNICAL-DEBT-REPORT.md executivo) → @pm (epic + stories prontas).

## Seleção de workflow

Nova story de epic → SDC · QA achou issues → QA Loop · Feature complexa → Spec Pipeline + SDC · Projeto existente → Brownfield Discovery · Bug fix simples → SDC (YOLO).
