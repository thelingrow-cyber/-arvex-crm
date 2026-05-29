# ARVEX CRM — Direção Criativa (v1)

**Squad:** WebDesign · **Autor:** Leo (Creative Director) · **Data:** 2026-05-29
**Referência:** Linear / Attio (dark, minimalista, denso, técnico)
**Alvo:** elevar o CRM de "protótipo/IA" para padrão de produto profissional
**Restrição:** single-file `docs/crm/index.html`, vanilla, sem build → SVG inline, zero libs

---

## 1. Princípios de design (o norte)

1. **Cor é informação, não decoração.** Fundos neutros; cor só onde comunica estado/ação.
2. **Zero emoji na interface.** Todo emoji vira ícone SVG de família única (Lucide), traço 1.5px, `currentColor`, 16px.
3. **Densidade com respiro.** Linear é denso mas legível — ritmo de espaçamento 4/8, hierarquia tipográfica firme.
4. **Hierarquia por tipografia e peso, não por caixa colorida.**
5. **Consistência radical.** Um botão, um card, um badge, um input — definidos uma vez, reusados em tudo.

---

## 2. Sistema de cor disciplinado

### Superfícies (neutras, frias — base navy mantida e calibrada)
```
--bg        #08:0C14   /* fundo do app */
--surface-1 #0E1420    /* cards, sidebar, colunas */
--surface-2 #151C2B    /* elevado: modais, dropdowns, hover */
--border    rgba(255,255,255,.07)   /* hairline */
--border-2  rgba(255,255,255,.12)   /* hover/focus */
```

### Texto (escala de 3 níveis)
```
--text-1 #E7ECF5   /* títulos, valores */
--text-2 #9AA7BC   /* corpo, labels */
--text-3 #5C6878   /* meta, placeholder, desabilitado */
```

### Acento (UM primário + dourado como marca pontual)
```
--accent     #5B6CFF   /* índigo Linear-like — ações primárias, item ativo, foco */
--accent-dim rgba(91,108,255,.14)   /* fundo sutil de seleção */
--gold       #C8A96E   /* RESERVADO: logo + sinal "premium/meta" pontual, NÃO espalhar */
```

### Status (dessaturados — só em dots/badges pequenos, nunca fundo de coluna)
```
--ok      #3FB950   --warn   #D29922   --danger #F85149   --info #58A6FF
```
> Cada status aparece como **dot de 6–8px** + texto, no estilo Attio. Nada de fundo inteiro colorido.

---

## 3. Tipografia (Inter — mantida)

| Uso | Tamanho / Peso | Tratamento |
|-----|----------------|-----------|
| Título de página | 20px / 700 | `--text-1` |
| Título de card/seção | 13px / 600 | `--text-1` |
| Corpo | 13px / 450 | `--text-2` |
| Label/meta | 11px / 550 | UPPERCASE, tracking .04em, `--text-3` |
| Números/métricas | 22–24px / 700 | `font-variant-numeric: tabular-nums` |

---

## 4. Substituição emoji → ícone (Lucide, SVG inline)

| Hoje (emoji) | Vira (ícone Lucide) |
|--------------|---------------------|
| Sidebar: Dashboard / Pipeline / CS / Financeiro / Leads | `layout-dashboard` / `kanban` / `headset` / `wallet` / `users` |
| Coluna kanban (🟢🔵🟡⭐🚀✅🔴) | **dot de status colorido** (6px) + label — sem ícone/emoji |
| `🔥 Quente` | dot âmbar + "Quente" (peso 600) |
| `🤝 Em CS` | badge texto "CS" (pill discreta) ou ícone `link-2` |
| `🎁 bônus` | `gift` (16px, `--text-3`) |
| `✅ Respondeu` / `❌ Sem resposta` | botão com `check` / `x` (ícone + texto) |
| `💬 WhatsApp` | `message-circle` (mantém reconhecível; verde só no ícone) |
| `🎯 Meta` | `target` (16px) |
| `⏰ HOJE` / `⚠️ ATRASADO` | `clock` / `alert-triangle` |

> Ícones Lucide são MIT, copiáveis como `<svg>` inline. Criar um helper `icon(name)` no JS que retorna o markup — define uma vez, usa em tudo.

---

## 5. Tratamento do Kanban (o maior ganho visual)

**Antes:** cada coluna com fundo colorido (azul/roxo/laranja/dourado/ciano/verde/vermelho) = arco-íris.

**Depois (Linear/Attio):**
- Todas as colunas com fundo **uniforme** (`--surface-1`) e header neutro.
- Identidade da fase por um **dot colorido de 8px** ao lado do nome + a contagem.
- Card limpo: nome em `--text-1`, metadados em `--text-3`, separadores hairline.
- Acento (índigo) só no card em foco / drag-over.

---

## 6. Microdetalhes que "vendem" profissionalismo

- **Raio menor:** cards 8px, inputs/botões 6px (hoje 12–16px é "bubbly").
- **Hover states** sutis e consistentes (`--surface-2` / `--border-2`).
- **Foco visível** com ring `--accent` (acessibilidade + cara de produto).
- **Sombra** quase imperceptível em elementos elevados (modais/dropdown).
- **Transições** 120–150ms ease — já existe, padronizar.

---

## 7. Escopo de aplicação (ordem sugerida)

1. **Tokens + tipografia + ícones** (base — afeta tudo) → maior ROI
2. **Kanban** (Pipeline + CS) → tela mais visível, maior impacto percebido
3. **Sidebar + topbar + métricas**
4. **Modais/detalhe + Financeiro + Dashboard**

---

## 8. Decisão de acento — ✅ APROVADA (Vitor, 2026-05-29)

**Opção A:** índigo `#5B6CFF` é o acento de produto (ações, seleção, foco, item ativo). O dourado `#C8A96E` fica **reservado à marca** (logo) e a sinais pontuais de "meta/premium" — não se espalha pela UI.

---

## Próximos passos (squad)

- `@web-designer` → especifica os componentes (botão, badge, card, kanban, input) com os tokens acima
- `@frontend-developer` → implementa no `index.html` na ordem do item 7
- Validação visual a cada etapa antes de avançar
