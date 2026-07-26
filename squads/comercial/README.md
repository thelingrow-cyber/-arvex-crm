# 🤝 COMERCIAL Squad

Squad comercial que converte leads em receita. Conecta os ativos reais que a ARVEX já opera — closers, SDR, Sales Coach e ofertas — em um único motor de fechamento.

## Contexto real ARVEX

- **Closers:** Gabriel e Thalita
- **SDR:** Carol (humana) + agente de IA no CRM (`docs/agente-sdr/carol-system-prompt.md`)
- **Sales Coach:** aba "Reuniões" do arvex-crm (Fases 1-2 no ar; Fase 3 especificada)
- **Transcrições de call:** plugin Meet Transcriber
- **Dados do funil:** pipeline no arvex-crm (acesso via `SUPABASE_DB_URL` por env — nunca colar credencial)

## Agentes (5)

| Agente | Persona | Função |
|--------|---------|--------|
| `sales-director` | Blake | Orquestrador — diagnóstico de funil, metas/forecast, rituais comerciais |
| `offer-strategist` | Grand | Desenho e auditoria de oferta (framework $100M, clone hormozi) |
| `closer-coach` | Wolf | Análise de call real, roleplay por objeção, playbook de fechamento |
| `sdr-playbook-manager` | Cady | Cadência de follow-up, qualificação ICP, dono do system prompt da Carol |
| `proposal-writer` | Quill | Proposta comercial, minuta de contrato, follow-up pós-envio |

## Como usar

```
@sales-director diagnostique o funil de vendas do último mês
```

O `sales-director` (Blake) conduz o diagnóstico e aciona os agentes do squad conforme necessário.

## Fontes de conhecimento

- **offer-strategist** → clone hormozi (`.claude/clones/hormozi/`) como fonte primária de ofertas e value equation
- **closer-coach** → transcrições do Meet Transcriber + Sales Coach (aba Reuniões) + Fase 3 (`docs/crm/sales-coach-fase3-ARCHITECTURE.md`)
- **sdr-playbook-manager** → dono do system prompt da Carol (`docs/agente-sdr/carol-system-prompt.md`)

## Workflow (6 passos)

1. **Diagnóstico de funil** (sales-director)
2. **Desenho de oferta** (offer-strategist)
3. **Playbook de fechamento + Cadência de follow-up** (closer-coach ∥ sdr-playbook-manager) — paralelo
4. **Proposta comercial** (proposal-writer)
5. **Metas + forecast** (sales-director)
6. **Loop mensal** — analise-call semanal (closer-coach) alimenta o funil, o playbook e a oferta no próximo ciclo

## Regras inegociáveis

- **No Invention (Art. IV):** todo número rastreia ao CRM; sem fonte, é estimativa marcada.
- **Contrato:** toda minuta de `contrato-base` carrega aviso destacado de **revisão jurídica humana obrigatória** — nunca é peça final.
- **Dados sensíveis:** leitura do CRM via `SUPABASE_DB_URL` por env; nunca colar credencial em chat ou arquivo.
- **Boundary L4:** o squad vive em `squads/comercial/` — nunca toca `.aiox-core/`.
