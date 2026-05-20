# Definição do Produto
> Consolidado em: 2026-05-17

---

## O que é

**CRM Conversacional com IA que tem contexto óptico nativo.**

Não é ERP. Não é chatbot genérico. É a combinação dos dois com especialização no nicho óptico.

---

## A combinação fatal

```
IA (age como SDR — atende, qualifica, vende, informa)
+
CRM (registra tudo, organiza ciclo de vida do cliente)
+
Contexto óptico nativo (sabe o que é OS, prescrição, laboratório)
```

**Resultado:** A ótica atende, vende e retém cliente no automático — mesmo quando o dono não está.

---

## Como funciona

```
Cliente manda mensagem no WhatsApp
           │
           ▼
    IA atende como SDR da ótica
    Sabe quem é o cliente
    Sabe a prescrição dele
    Sabe se tem OS aberta
    Agenda, vende, informa, reativa
           │
           ▼
    Tudo salva no CRM automaticamente
    Stage do cliente atualiza sozinho
    Score de risco recalcula
    Dono vê no dashboard
```

---

## Arquitetura em 3 camadas

| Camada | O que é | O que entrega |
|--------|---------|---------------|
| **IA de Atendimento** | Claude + WhatsApp via Evolution API | Atende 24/7, qualifica, agenda, informa OS |
| **Reativação Automática** | N8N flows agendados | Reativa clientes inativos, avisa prescrição vencendo |
| **CRM Leve** | Supabase + dashboard | Organiza clientes, mostra score de risco, histórico |

---

## Ciclo de vida do cliente na ótica

```
Novo Lead → Consulta Agendada → Venda Fechada → OS no Lab → Entregue → Ativo → Em Risco → Reativado
```

Não é pipeline de vendas corporativo. É jornada do cliente óptico.

---

## O que o dono de ótica vê

**Dashboard simples com:**
- Clientes novos hoje
- Atendimentos feitos pela IA
- Clientes em risco (vermelho/amarelo/verde)
- Alertas: prescrições vencendo, OS atrasadas, clientes sumidos

**Ficha do cliente:**
- Nome, contato, histórico de compras
- Prescrição e data de vencimento
- Tipo de lente preferida
- Status atual + score de risco

---

## Por que ninguém faz isso

| Player | O que tem | O que falta |
|--------|-----------|-------------|
| ssOtica / Linx | Histórico do cliente | IA conversacional |
| Letalk / Chatclipy | IA no WhatsApp | Contexto óptico |
| Datacrazy | CRM + pipeline | Especialização no nicho |
| **Seu SaaS** | **Os três juntos** | **Nada** |

---

## Stack técnica

| Componente | Tecnologia |
|------------|-----------|
| IA conversacional | Claude (Anthropic) |
| WhatsApp | Evolution API |
| Automação | N8N |
| Banco de dados | Supabase |
| Frontend/Dashboard | A definir (Base44 para demo) |

Stack já existe no Epic 3 SDR da ARVEX — adaptação, não construção do zero.

---

## Posicionamento

**Categoria:** CRM Conversacional com IA
**Nicho de entrada:** Óticas
**Expansão:** Construtoras, drogarias, clínicas (mesmo padrão operacional)

**Tagline:** *"Sua ótica crescendo mesmo quando você não está"*

**Inimigo:** O sistema que vende bem e abandona depois

**Herói:** O dono de ótica que quer crescer sem depender de estar sempre presente

---

## Pricing de referência

| Plano | Preço/mês | Para quem |
|-------|-----------|-----------|
| Starter | R$197 | 1 loja, até 500 clientes ativos |
| Essencial | R$297 | 1 loja, clientes ilimitados |
| Pro | R$497 | Até 5 lojas |

Modelo: por loja/unidade — não por membro de equipe.
