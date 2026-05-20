# Decisão White Label — SaaS Óptico
> Data: 2026-05-19

---

## A decisão

Compra de white label com código fonte por **R$1.500** de Victor Eder (lp.victoreder.com.br).

Produto: CRM Conversacional + WhatsApp + IA — já construído, pronto para customizar.

---

## Stack confirmada

| Componente | Tecnologia |
|------------|-----------|
| Banco de dados | Supabase (conta do Vitor — controle total) |
| IA | GPT-4.1 nano via OpenAI API (chave própria do Vitor) |
| WhatsApp | Evolution API/Baileys hoje → Meta oficial (em 10 dias) |
| Automação | Dentro do código (sem N8N externo) |
| Frontend/Backend | A confirmar após receber o código |

---

## O que o sistema já tem

| Módulo | Status |
|--------|--------|
| Dashboard conversas + métricas | ✅ Pronto |
| CRM Kanban multi-board | ✅ Pronto |
| Agente IA com tool calling | ✅ Pronto |
| Multi-WhatsApp com rotação | ✅ Pronto |
| Disparos em massa com IA | ✅ Pronto |
| Handoff humano configurável | ✅ Pronto |
| Áudio e imagem no agente | ✅ Pronto |
| Métricas por atendente | 🔜 Em breve |
| Contexto óptico nativo | ❌ A construir |

---

## O que construir por cima

### Semana 1 — Sem código (configuração)
- Renomear pipeline stages para o fluxo óptico
- System prompt do agente IA com contexto óptico
- Campanhas de disparo (prescrição vencendo, reativação, OS pronta)

### Semana 2+ — Com código
- Campos de prescrição no card CRM (OD/OE, grau, tipo de lente)
- Módulo OS (número, prazo, status, laboratório)
- Aviso automático quando OS está pronta
- Score de risco de inatividade
- Dashboard com métricas ópticas
- Preenchimento automático do card via conversa WhatsApp

---

## Pipeline óptico definido

```
Novo Lead → Qualificado → Consulta Agendada
→ Simulação Realizada → Venda Fechada
→ OS em Produção → Pronto para Retirada
→ Entregue/Ativo → Em Risco → Reativado
```

---

## Prompt do agente IA (pronto para usar)

```
## Identidade
Você é a assistente virtual da [NOME DA ÓTICA].
Seu nome é [NOME DO AGENTE].
Atende pelo WhatsApp com atenção, simpatia e linguagem simples.

## Papel
1. Identificar o que o cliente precisa
2. Qualificar se é lead real
3. Agendar consulta ou visita
4. Informar status de OS quando solicitado
5. Reativar clientes inativos

## Contexto óptico
- OS = Ordem de Serviço (pedido ao laboratório)
- Prescrição = receita médica. Vence em 1-2 anos
- OD = olho direito | OE = olho esquerdo
- Lentes: monofocal, bifocal, progressiva, fotossensível
- Laboratório: fabrica as lentes. Prazo: 7-15 dias úteis

## Fluxo
Saudação → Identificação → Qualificação → Agendamento ou Info

## Regras
- NUNCA invente status de OS
- NUNCA dê preço (transfere pro humano)
- SEMPRE transfira se cliente estiver irritado
- Máximo 3 mensagens sem resolver → transfere pro humano
```

---

## Campanhas prontas

**Prescrição vencendo:**
> "Oi [nome]! Sua receita dos óculos vence em breve. Quer agendar sua consulta? 👓"

**Reativação:**
> "Oi [nome]! Faz tempo que não aparece. Temos novidades em lentes e armações. Que tal uma visita?"

**OS pronta:**
> "[Nome], seus óculos chegaram! Pode retirar de seg-sáb das 9h às 18h. Te esperamos! 😊"

---

## Próximos passos

1. Fechar com Victor Eder (R$1.500)
2. Receber código + subir na VPS
3. Review de segurança do código
4. Configurar agente + pipeline + campanhas (sem código)
5. Demo para primeira ótica piloto (evento Cindy)
6. Construir módulo OS + campos de prescrição com feedback real
