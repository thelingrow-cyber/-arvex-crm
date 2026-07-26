# 🔐 SECURITY Squad

Squad de segurança **defensiva** do stack ARVEX. Faz AppSec e OpSec contínuos sobre o que a ARVEX roda em produção — arvex-crm (Supabase + Vercel, dados reais de clientes), landings e plugins.

> **Não é pentest ofensivo.** Este squad audita o próprio stack — nunca ataca terceiros, explora sistemas externos ou faz engenharia social.

## Agentes (2)

| Agente | Persona | Função |
|--------|---------|--------|
| `appsec-auditor` (lead) | Vega | Auditoria de código (OWASP), RLS do Supabase, secrets, modelagem de ameaça |
| `opsec-guardian` | Locke | Controle de acessos, resposta a incidente, CVEs em dependências |

## Como usar

```
@appsec-auditor audite a segurança de [diff/PR, módulo, tabela ou feature nova]
```

A `appsec-auditor` (Vega) confirma o escopo, conduz as auditorias e aciona o `opsec-guardian` (Locke) para acessos, dependências e incidentes.

### Motor de auditoria de código

A task `audit-codigo` usa a skill nativa **`/security-review`** do Claude Code como motor da varredura OWASP Top-10.

## Workflow (4 passos)

1. **threat-model** (Vega) — só quando é feature nova (STRIDE-lite)
2. **audit-codigo ∥ audit-rls** (Vega) — paralelo
3. **audit-secrets ∥ dependency-audit** (Vega + Locke) — paralelo
4. **Relatório consolidado** com verdict **PASS / CONCERNS / FAIL** (mesmo vocabulário do @qa)

## Gancho no SDC

Stories que tocam **auth, RLS ou pagamento** DEVEM passar por `Security:agents:appsec-auditor` **antes do qa-gate**. É uma extensão documentada do Story Development Cycle — não altera o core (`.aiox-core/` permanece intocado).

## Regras

- **Verdict** sempre no vocabulário do @qa: `PASS` / `CONCERNS` / `FAIL`.
- **Secrets** (ADR-3.3): nunca expor valor em chat/arquivo — reportar localização + plano de rotação.
- **Autoridades:** push/PR/MCP continuam EXCLUSIVOS de @devops; este squad recomenda, @devops executa.
- **Boundary:** vive em `squads/` (L4) — nunca toca `.aiox-core/` (L1/L2).
