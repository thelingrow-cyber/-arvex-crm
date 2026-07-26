# 📈 MARKETING Squad

Squad de aquisição completa — tráfego pago, conteúdo orgânico, e-mail e analytics. O braço que enche o topo do funil da ARVEX e da marca pessoal.

## Agentes (6)

| Agente | Persona | Função |
|--------|---------|--------|
| `marketing-director` | Maya | Orquestradora — briefing de campanha, mix de canais, aprovação final |
| `media-buyer` | Buck | Tráfego pago — auditoria, estrutura, otimização, testes ⚠️ modo co-piloto |
| `copy-chief` | Halbert | Direct response cross-canal (ads, e-mails, VSL, scripts) + revisor final de todo copy |
| `social-content-strategist` | Nina | Conteúdo orgânico — calendário, roteiros de short-form, repurpose |
| `email-crm-marketer` | Reva | E-mail marketing — nutrição, broadcast, automação de fluxo |
| `analytics-tracker` | Dot | Mensuração — tracking, dashboard de KPIs, relatório semanal |

## Como usar

```
@marketing-director crie uma campanha de aquisição para [oferta/produto]
```

A `marketing-director` (Maya) conduz o briefing de campanha e aciona os agentes do squad conforme o workflow.

## Workflow

1. Briefing de campanha (marketing-director)
2. Plano de canal — mix orgânico × pago (marketing-director)
3. Estrutura de campanha + copy de anúncios + calendário de conteúdo (media-buyer + copy-chief + social-content-strategist) — paralelo
4. Plano de tracking (analytics-tracker)
5. Aprovação da campanha (marketing-director)
6. Campanha no ar — execução co-piloto humano na plataforma até o MCP de ads existir
7. Otimização semanal + relatório semanal (media-buyer + analytics-tracker) — paralelo, em loop

## Notas importantes

### media-buyer nasce em modo co-piloto ⚠️

O `media-buyer` (Buck) opera em **dois modos**:

- **Co-piloto (ativo hoje):** gera os planos e o Vitor executa manualmente na plataforma (Google Ads / Meta). Sem acesso direto à conta.
- **Operador (pendente):** aplica mudanças direto na conta. Depende de **@devops instalar o MCP de Google Ads** (`*search-mcp google ads` → `*add-mcp`). Autoridade de MCP é EXCLUSIVA de @devops.

### copy-chief não duplica o copywriter do WebDesign

O `copy-chief` (Halbert) é **direct response cross-canal** (anúncios, e-mails, VSL, scripts) e **revisor final de todo o copy da casa** — inclusive o copy que o WebDesign produz. O copywriter do WebDesign faz copy DE PÁGINA (landing/hero/seções); os papéis não se sobrepõem.

Fontes de conhecimento do copy-chief:
- `.claude/clones/hormozi/` — ofertas, value equation, hooks
- `docs/aprendizados-ia/heuristicas-vitor.md` — voz e critérios do Vitor

## Boundary

Squad L4 (mutável sempre). Vive em `squads/marketing/` e `.claude/commands/Marketing/` — nunca toca `.aiox-core/`. Push/PR/MCP permanecem EXCLUSIVOS de @devops.
