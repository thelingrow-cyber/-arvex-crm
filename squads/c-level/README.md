# 👔 C-LEVEL Squad

A camada executiva — o **"board"** da startup 1-person. Fica **ACIMA** dos squads operacionais. Os C-levels **decidem, priorizam e orquestram**; os squads **executam**. Este squad não produz trabalho de domínio (não escreve copy, não faz DDL, não fecha venda) — ele responde à pergunta "o que fazemos agora, quem faz e em que ordem".

## Organograma

```
                        ┌──────────────────────────────┐
                        │        C-LEVEL (board)        │
                        │                                │
                        │   Vision (cso)  ─ prioriza     │
                        │   Atlas  (coo)  ─ orquestra    │
                        │   Reign  (cmo)  ─ aquisição    │
                        │   Sterling (cfo) ─ CONVOCADO   │
                        │        de financas ↴           │
                        └───────────────┬────────────────┘
                                        │ roteia
        ┌────────────┬────────────┬─────┴──────┬────────────┬────────────┬────────────┐
        ▼            ▼            ▼            ▼            ▼            ▼            ▼
    security     marketing    comercial    research      financas     branding    webdesign
     (Vega)       (Maya)       (Blake)     (Darwin)     (Sterling)    (Iris)       (Leo)
```

## A "mesa" executiva

| Cadeira | Agente | Persona | De onde vem |
|---------|--------|---------|-------------|
| COO / Orchestrator | `coo-orchestrator` | **Atlas** | c-level (lead) |
| Chief Strategy Officer | `cso` | **Vision** | c-level |
| Chief Marketing Officer | `cmo` | **Reign** | c-level |
| Chief Financial Officer | *(ponte)* `Financas:cfo` | **Sterling** | **convocado de `squads/financas/`** |

### Ponte com Sterling / financas (princípio IDS — não duplicar)

O CFO da mesa executiva **não é um agente novo**. É o **Sterling**, lead do squad `financas` (`squads/financas/agents/cfo.md`), já criado. Toda decisão que envolve **capital** (investir em mídia, precificar oferta, aprovar custo, alocar budget) **convoca o Sterling** para a mesa — o c-level **referencia** o squad `financas`, não reimplementa finanças. Isso mantém uma única fonte de verdade para dinheiro e evita a duplicação de papel (IDS).

**A mesa completa = Atlas + Vision + Reign + Sterling-convocado.**

## Agentes (3 próprios)

| Agente | Persona | Função | Tasks |
|--------|---------|--------|-------|
| `coo-orchestrator` (lead) | Atlas | Roteia o trabalho entre os 7 squads; produz plano de execução; acompanha e desbloqueia | `rotear-demanda` · `acompanhar-execucao` · `remover-bloqueio` |
| `cso` | Vision | Estratégia, tese e priorização; guardião do anti-dispersão | `definir-prioridades` · `avaliar-oportunidade` · `revisar-tese` |
| `cmo` | Reign | Aquisição e marca macro; orquestra marketing+branding+webdesign | `estrategia-aquisicao` · `alinhar-marca-oferta` · `revisar-funil-macro` |

## Squads operacionais orquestrados (e seus leads)

| Squad | Lead | Persona | Domínio |
|-------|------|---------|---------|
| `security` | `appsec-auditor` | Vega | AppSec/OpSec, auditoria do stack |
| `marketing` | `marketing-director` | Maya | Aquisição, tráfego, copy, conteúdo, analytics |
| `comercial` | `sales-director` | Blake | Funil, closers, SDR, ofertas, propostas |
| `research` | `deep-researcher` | Darwin | Pesquisa profunda, inteligência competitiva |
| `financas` | `cfo` | Sterling | Capital, pricing, controladoria (também CFO da mesa) |
| `branding` | `brand-director` | Iris | Posicionamento, identidade, guardião da marca |
| `webdesign` | `creative-director` | Leo | Sites e landing pages que convertem |

## Como usar

```
@coo-orchestrator quero destravar a aquisição da oferta própria neste mês
```

Ou começando pela estratégia:

```
@cso o que eu priorizo agora: SaaS óptico, oferta própria ou marca pessoal?
```

## Workflow (5 passos)

1. **Priorizar** (`cso`/Vision) — Vitor traz o objetivo; o cso decide o foco do ciclo (anti-dispersão).
2. **Go/no-go** (`cso`/Vision) — se é frente nova, passa pelo veredito antes de rotear.
3. **Rotear** (`coo-orchestrator`/Atlas) — plano de execução: quais squads, em que ordem; se envolve aquisição/marca, o `cmo` desenha a estratégia macro; se envolve capital, convoca o Sterling (`financas`).
4. **Acompanhar** (`coo-orchestrator`/Atlas) — status por frente; remove bloqueios.
5. **Reportar + realimentar** (`coo-orchestrator` ∥ `cso`) — status consolidado ao Vitor + coerência com a tese; realimenta a fila de prioridades.

## Regras inegociáveis

- **Anti-dispersão (ameaça nº1):** toda priorização defende o foco único do ciclo — 1 build por vez; frente nova só entra se outra fechar ou pausar.
- **Tese como âncora:** priorização e revisão rastreiam a `docs/ecossistema/brand-book-marca-pessoal.md`.
- **IDS / não-duplicação:** capital é sempre do Sterling (`financas`); o c-level referencia, não reimplementa. Nenhum "CFO do c-level" é criado.
- **C-level decide, squad executa:** os agentes daqui não produzem entregável de domínio — produzem decisão, plano e orquestração.
- **Boundary L4:** o squad vive em `squads/c-level/` — nunca toca `.aiox-core/`.
