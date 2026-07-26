# 🔬 RESEARCH Squad

Squad "The Deep Researcher" — revisão sistemática multi-fonte com síntese citada, nível consultoria. Diferente do `@analyst` do core (leve, interno ao SDC), este squad produz relatórios com protocolo, fontes numeradas e citações verificáveis.

## Agentes (3)

| Agente | Persona | Função |
|--------|---------|--------|
| `deep-researcher` (lead) | Darwin | Protocolo de revisão, busca sistemática multi-fonte, síntese com citações. Alias: `dr-orchestrator` |
| `evidence-auditor` | Pierce | Qualidade das fontes, checagem de citações, gate anti-invenção (APPROVED/NEEDS-REVISION) |
| `competitive-intel` | Sun | Análise de concorrente (reusa template do core), monitoramento de mercado |

## Como usar

```
@deep-researcher pesquise [tema] e me entregue um relatório com citações
```

O `deep-researcher` (Darwin) define o protocolo antes de buscar, executa a busca, sintetiza e só entrega após o gate do `evidence-auditor`.

## Workflow (5 passos)

1. **Protocolo** (deep-researcher) — pergunta, critérios de inclusão/exclusão, estratégia de busca (PRISMA-lite)
2. **Busca sistemática** (deep-researcher ∥ competitive-intel, se houver concorrentes) — corpus de fontes numeradas
3. **Qualidade das fontes** (evidence-auditor) — classificação e vieses
4. **Síntese com citações** (deep-researcher) — relatório com achados numerados
5. **Gate anti-invenção** (evidence-auditor) — checagem de citações + lacunas → APPROVED entrega · NEEDS-REVISION volta ao passo 4

## Regras duras

- **No Invention (Constituição Art. IV):** toda afirmação de relatório rastreia a uma fonte numerada `[n]` ou é marcada como inferência/estimativa. Número sem lastro é proibido.
- **Saída:** relatórios salvos em `docs/research/{tema}-{data}.md`.
- **Ferramentas de busca** (`.claude/rules/mcp-usage.md`): EXA (`mcp__docker-gateway__web_search_exa`) para web geral · Apify para site/rede específica · Context7 para docs técnicas.
- **Material cru grande** (PDFs, páginas longas, transcrições, dumps): destilado por subagente, nunca lido no contexto principal.
- **Análise competitiva:** `competitive-intel` REUSA o template `.aiox-core/product/templates/competitor-analysis-tmpl.yaml` do core — referencia, não recria.

## Boundary

Squad L4 (mutável). Vive em `squads/research/` e `.claude/commands/Research/`. Nunca toca `.aiox-core/` (L1/L2).
