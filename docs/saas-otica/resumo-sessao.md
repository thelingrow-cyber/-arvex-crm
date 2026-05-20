# Resumo da Sessão — SaaS Óptico
> Data: 2026-05-17 | Sessão com Orion (AIOX) + Clone Tay Dantas

---

## O que foi construído nessa sessão

### 1. Pesquisa de Mercado Completa
- Mapeamento de ERPs do nicho óptico (ssOtica, PWI Vixen, Linx, TekÓtica, ERP Varejo BR)
- Gaps priorizados por impacto + urgência
- Modelos de SaaS de outros mercados adaptados ao nicho
- Reclame Aqui: voz real do cliente óptico
- Análise de SaaS genéricos brasileiros e globais (Datacrazy, Letalk, Chatclipy, Umbler Talk, HubSpot, etc.)
- Screenshots internas do Datacrazy (produto + pricing)

### 2. Decisões Estratégicas Tomadas

| Decisão | Definição |
|---------|-----------|
| Tipo de produto | Plataforma de crescimento com IA — não ERP |
| Posicionamento de marca | Horizontal (construtoras, óticas, drogarias) |
| Execução go-to-market | Vertical — entra pelas óticas primeiro |
| Cindy Batista | Não sócia. Parceria comercial: 25% recorrente por cliente |
| Stack técnica | N8N + Evolution API + Claude + Supabase (já existe no Epic 3) |
| Modelo de cobrança | Por loja/unidade — R$197/297/497 |

### 3. Hero Brand Definido

**Herói:** Dono de ótica que quer crescer sem depender de presença constante

**Inimigo:** O ERP (e SaaS genérico) que abandona o cliente depois da venda

**Mentor (a marca):** Plataforma que fica ao lado — atende, retém e cresce com a ótica

**Dor concreta:** Lead perdido no WhatsApp, suporte que some, sistema que trava

**Dor cultural:** "Me tratam como número depois que assino"

**Promessa:** *"Sua ótica crescendo mesmo quando você não está"*

**Atributo único:** Parceiro de crescimento — não some depois da venda

### 4. Mapa de Posicionamento

```
                    CRESCIMENTO / RESULTADO
                              |
              [SEU SAAS]      |
                              |
GENÉRICO ————————————————————+———————————— ESPECIALIZADO
                              |
     ManyChat / Umbler        |    ssOtica / Linx / PWI
                              |
                        BACK-OFFICE / GESTÃO
```

Território livre: Especializado + Crescimento = ninguém ocupa

### 5. Arquitetura do Produto (3 módulos)

| Módulo | O que faz |
|--------|-----------|
| Aquisição | Funil de leads via WhatsApp, qualificação automática, agendamento |
| Conversão | IA 24/7 que responde, qualifica e agenda (WhatsApp, Instagram, site) |
| Retenção | Fluxos pós-venda, score de risco de inatividade, campanhas de renovação |

### 6. Go-to-Market

- **Entrada:** Parceria com Cindy Batista — 25% recorrente, sem equity
- **Evento de lançamento:** "IA para ótica" — narrativa inexistente no mercado
- **Estrutura do evento:** Mentoria Cindy + implementação de IA + venda do SaaS ao público
- **Demo:** Criada via Base44 com dados fictícios de ótica real (Ótica Visão Clara)
- **Prazo alvo:** ~20 dias

### 7. Referência de Pricing

| Plano | Preço/mês | Por quê |
|-------|-----------|---------|
| Entrada | R$197 | Abaixo do genérico (R$297 Datacrazy) |
| Essencial | R$297 | Equivalente ao genérico com especialização |
| Pro | R$497 | Redes de 2-5 lojas |

---

## O que ainda falta definir

- [ ] Nome do produto
- [ ] Tagline final
- [ ] ICP formal (perfil exato do primeiro cliente)
- [ ] PRD completo
- [ ] Contrato formal com Cindy

---

## Arquivos nessa pasta

| Arquivo | Conteúdo |
|---------|---------|
| `pesquisa-mercado.md` | Mapa completo do mercado óptico + concorrentes + gaps |
| `pesquisa-saas-outros-nichos.md` | Análise de 14+ SaaS genéricos e brasileiros |
| `handoff-tay.md` | Handoff estruturado para sessão com clone Tay Dantas |
| `prompt-demo-base44.md` | Prompt pronto para criar demo no Base44 |
| `resumo-sessao.md` | Este arquivo — visão geral de tudo |
| `concorrentes/` | Screenshots internas do Datacrazy (kanban, funil, dashboard, pricing) |
