# 🎭 BRANDING Squad

Squad que **governa e aplica** os ativos de marca já existentes da ARVEX e da marca pessoal do Vitor ("O Futuro Instalado"). Mantém brand book, posicionamento e sistema visual — **não recria do zero**.

## Agentes (3)

| Agente | Persona | Função |
|--------|---------|--------|
| `brand-director` | Iris | Orquestradora — guardiã do brand book, decisões de naming e arquitetura de marcas |
| `positioning-strategist` | North | Posicionamento — mapa de 12 players, tese "instalar o futuro", ângulos por ICP (fonte: clone tay-dantas) |
| `identity-keeper` | Forma | Sistema visual aplicado e auditoria de consistência dos materiais publicados |

## Como usar

```
@brand-director audite esta landing contra o brand book
```

A `brand-director` (Iris) conduz e aciona `positioning-strategist` (North) e `identity-keeper` (Forma) conforme a demanda.

## Workflow (ciclo trimestral de governança)

1. Tese narrativa — revalida a big idea "O Futuro Instalado" (positioning-strategist)
2. Guarda do brand book — reconcilia o brand book com a tese evoluída (brand-director)
3. Auditoria de consistência — varre os materiais do trimestre contra brand book + sistema visual (identity-keeper) — em loop trimestral

### Tasks sob demanda (fora do ciclo)

- `decisao-marca` (brand-director) — quando nasce iniciativa/produto/oferta que precisa de naming ou arquitetura de marca
- `mapa-posicionamento` (positioning-strategist) — quando um player relevante se mexe (insumo de `Research:competitive-intel`)
- `angulo-de-entrada` (positioning-strategist) — nova oferta/ICP (conecta `Comercial:offer-strategist` e Marketing)
- `sistema-visual` (identity-keeper) — novo material/landing precisa aplicar o sistema visual da casa

## Regra central — GOVERNA, não recria

Este squad opera **em cima de ativos que já existem**. As fontes de verdade:

- **Brand book:** `docs/ecossistema/brand-book-marca-pessoal.md` — categoria "O Futuro Instalado", verbo INSTALAR, oferta "A Instalação", roadmap F1-F4
- **Mapa de posicionamento:** `docs/ecossistema/mapa-posicionamento-marca.md` — 12 players, 5 eixos, 4 brechas
- **Sistema visual das landings:** regras em `docs/aprendizados-ia/` + feedback herdado de landing-cindy-vendas (Inter 900, gold+navy+verde; reprovado: serif, cutout, vw explosivo, firulas inventadas)
- **Fonte de posicionamento:** clone tay-dantas (`.claude/clones/tay-dantas/`) — usado pelo `positioning-strategist`

## identity-keeper × brand-strategist do WebDesign (ADAPT <30%)

- **WebDesign:brand-strategist (Stella)** CRIA identidade de marca do zero, por-projeto, no escopo de uma página.
- **Branding:identity-keeper (Forma)** GOVERNA as marcas da casa (ARVEX, Viziom, marca pessoal) — aplica e fiscaliza consistência dos ativos que já existem. Não cria marca nova.

Os papéis não se sobrepõem: um nasce marca para um projeto; o outro protege as marcas da empresa.

## Boundary

Squad L4 (mutável sempre). Vive em `squads/branding/` e `.claude/commands/Branding/` — nunca toca `.aiox-core/`. Push/PR/MCP permanecem EXCLUSIVOS de @devops.
