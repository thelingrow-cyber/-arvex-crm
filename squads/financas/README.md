# 💰 FINANCAS Squad

Squad financeiro da ARVEX. Cuida de caixa, unit economics e precificação da operação — co-produção 50/50 com experts e ofertas próprias — em cima dos dados que o CRM já registra. **Analisa e recomenda; nunca executa pagamento ou transferência.**

## Contexto real ARVEX

- **Modelo:** co-produção 50/50 com experts + ofertas próprias
- **Fonte de dados:** módulo financeiro do arvex-crm (vendas + parcelas), já especificado/implantado
- **Unit economics:** LTGP:CAC pelo framework do clone hormozi (`.claude/clones/hormozi/`)
- **Acesso aos dados:** leitura do CRM via `SUPABASE_DB_URL` por env — nunca colar credencial em chat/arquivo
- **Regra dura:** nenhum agente movimenta dinheiro; a execução financeira é sempre humana

## Agentes (3)

| Agente | Persona | Função |
|--------|---------|--------|
| `cfo` | Sterling | Orquestrador — visão de caixa/runway, unit economics (LTGP:CAC), decisão go/no-go de investimento |
| `controller` | Ledger | Fluxo de caixa mensal (integra CRM), conciliação CRM × extrato, DRE + comissões/repasses |
| `pricing-analyst` | Costa | Precificação de oferta, margem real por expert/oferta, simulação de cenários |

## Como usar

```
@cfo gere a visão de caixa do mês e o unit economics por oferta
```

O `cfo` (Sterling) conduz e aciona `controller` e `pricing-analyst` conforme necessário.

## Fontes de conhecimento

- **cfo** → clone hormozi (`.claude/clones/hormozi/`) para LTGP:CAC e unit economics
- **controller** → módulo financeiro do CRM (vendas + parcelas) via `SUPABASE_DB_URL` + extrato bancário
- **pricing-analyst** → custo de entrega + receita do CRM; conecta `Comercial:offer-strategist` para oferta nova

## Workflow — loop mensal (4 passos)

1. **Fluxo de caixa mensal** (controller) — integra vendas + parcelas do CRM
2. **Análise de margem + Unit economics** (pricing-analyst ∥ cfo) — margem alimenta o LTGP:CAC
3. **Visão de caixa** (cfo) — runway e projeção 90d
4. **Relatório mensal** (controller) — DRE simplificado + comissões/repasses · **loop mensal**

Sob demanda, fora do loop:
- **precificacao-oferta** e **cenarios** (pricing-analyst) — quando nasce uma oferta (conecta `Comercial:offer-strategist`)
- **decisao-investimento** (cfo) — quando surge um gasto a avaliar (verba de tráfego, contratação, ferramenta)

## Regras inegociáveis

- **Não executa pagamento:** todo agente do squad analisa e recomenda; a movimentação de dinheiro é sempre humana.
- **No Invention (Art. IV):** todo número rastreia ao CRM/extrato; sem fonte, é estimativa marcada.
- **Dados sensíveis:** leitura do CRM via `SUPABASE_DB_URL` por env; nunca colar credencial em chat ou arquivo.
- **Margem real:** sempre líquida do split de co-produção 50/50, nunca só a bruta.
- **Boundary L4:** o squad vive em `squads/financas/` — nunca toca `.aiox-core/`.
