# Plano de Implementação — Agente SDR ARVEX
**Versão:** 1.0
**Data:** 2026-04-30
**Owner:** Aria (@architect)
**Referência:** `docs/spec/spec-agente-sdr.md` v1.1

---

## Estrutura de Fases

```
FASE 1 — Infraestrutura      (2–3 dias)
FASE 2 — Integração WhatsApp (2–3 dias)
FASE 3 — Cérebro do Agente   (3–4 dias)
FASE 4 — Integrações CRM     (2–3 dias)
FASE 5 — Testes e Afinação   (3–5 dias)
```

---

## FASE 1 — Infraestrutura Base

**Objetivo:** Ambiente de produção funcionando antes de qualquer código de negócio.

| # | Tarefa | Tecnologia | Saída esperada |
|---|--------|-----------|----------------|
| 1.1 | Criar projeto no Railway | Railway | Projeto ARVEX-SDR criado |
| 1.2 | Deploy N8N self-hosted | Docker + Railway | N8N acessível via URL |
| 1.3 | Deploy Evolution API | Docker + Railway | Evolution API rodando |
| 1.4 | Deploy Redis | Railway plugin | Redis conectado ao N8N |
| 1.5 | Configurar variáveis de ambiente | Railway secrets | Todas as keys seguras |
| 1.6 | Criar número WhatsApp dedicado | WhatsApp | Número ativo e separado |
| 1.7 | Conectar número à Evolution API | Evolution API | QR Code lido, sessão ativa |

**Variáveis de ambiente necessárias:**
```
ANTHROPIC_API_KEY
SUPABASE_URL
SUPABASE_SERVICE_KEY
GOOGLE_CALENDAR_CLIENT_ID
GOOGLE_CALENDAR_CLIENT_SECRET
EVOLUTION_API_KEY
REDIS_URL
N8N_ENCRYPTION_KEY
```

---

## FASE 2 — Integração WhatsApp ↔ N8N

**Objetivo:** Mensagens chegando e saindo via WhatsApp com controle total do N8N.

| # | Tarefa | Saída esperada |
|---|--------|----------------|
| 2.1 | Configurar webhook Evolution API → N8N | N8N recebe eventos de mensagem |
| 2.2 | Criar fluxo N8N: receber mensagem | Log confirmando recebimento |
| 2.3 | Criar fluxo N8N: enviar mensagem | Mensagem enviada via Evolution API |
| 2.4 | Testar envio/recebimento ponta-a-ponta | WhatsApp ↔ N8N funcionando |
| 2.5 | Implementar detecção de áudio + Whisper | Áudio transcrito para texto |

---

## FASE 3 — Cérebro do Agente (Claude)

**Objetivo:** Carol conversando com inteligência, memória e critério de qualificação.

| # | Tarefa | Saída esperada |
|---|--------|----------------|
| 3.1 | Escrever system prompt inicial (Carol) | Persona + critérios Cindy definidos |
| 3.2 | Integrar Claude API no fluxo N8N | Claude respondendo às mensagens |
| 3.3 | Implementar memória via Redis | Contexto mantido entre mensagens |
| 3.4 | Implementar lógica de qualificação | Agente identifica perfil do lead |
| 3.5 | Implementar lógica de desqualificação | Agente encerra com gentileza |
| 3.6 | Implementar triggers de escalada | Escalada automática para Gabriel |
| 3.7 | Testar conversas completas | 10 cenários cobertos |

**Estrutura do system prompt:**
```
[PERSONA] Quem é Carol, tom, missão
[CONTEXTO] Cindy Batista, produto, tickets
[QUALIFICAÇÃO] Critérios dono de ótica
[FLUXO] Passos da conversa
[ESCALADA] Quando e como escalar
[PROIBIÇÕES] O que nunca dizer/prometer
```

---

## FASE 4 — Integrações CRM + Agenda

**Objetivo:** Lead registrado, agenda integrada, Gabriel notificado automaticamente.

| # | Tarefa | Saída esperada |
|---|--------|----------------|
| 4.1 | Trigger Supabase → N8N (novo lead) | N8N detecta lead novo no CRM |
| 4.2 | Atualização de status no Supabase | Status atualizado a cada etapa |
| 4.3 | Registro de atividades em `activities` | Histórico de conversa gravado |
| 4.4 | Integração Google Calendar | Agente verifica slots disponíveis |
| 4.5 | Criação automática de evento | Call agendada no Google Calendar |
| 4.6 | Confirmação D-1 automática | Mensagem enviada 24h antes |
| 4.7 | Reativação automática D+1, D+3, D+7 | Follow-up automático |
| 4.8 | Notificação handoff para Gabriel | WhatsApp com resumo + link CRM |

---

## FASE 5 — Testes, Afinação e Go-Live

**Objetivo:** Agente calibrado com conversas reais antes de ativar para todos os leads.

| # | Tarefa | Critério de sucesso |
|---|--------|-------------------|
| 5.1 | Testes internos (time ARVEX como leads) | 20 conversas sem erro crítico |
| 5.2 | Afinação do system prompt | Tom aprovado por Vitor |
| 5.3 | Teste de escalada | Gabriel recebe notificações corretas |
| 5.4 | Teste de agendamento | Call criada no Google Calendar |
| 5.5 | Ativar para 10% dos leads (piloto) | Taxa de resposta > 60% |
| 5.6 | Monitoramento 7 dias | Sem erros críticos em produção |
| 5.7 | Go-live 100% | Todos os leads da Cindy pelo agente |

---

## Dependências e Pré-requisitos

| Dependência | Responsável | Antes de |
|------------|------------|---------|
| Número WhatsApp dedicado criado | Vitor/Gabriel | Fase 1 |
| Google Calendar do closer compartilhado | Gabriel | Fase 4 |
| Opt-in LGPD adicionado ao formulário | Web Designer | Fase 4 |
| Script de objeções validado com Gabriel | Gabriel + Vitor | Fase 3 |
| CRM Supabase operacional (Story 2.1) | ✅ Já existe | — |

---

## Mapeamento para Stories

| Story | Fase | Escopo |
|-------|------|--------|
| Story 3.1 | Fase 1 | Infraestrutura Railway (N8N + Evolution API + Redis) |
| Story 3.2 | Fase 2 | Integração WhatsApp ↔ N8N + Whisper |
| Story 3.3 | Fase 3 | Cérebro Claude + memória Redis |
| Story 3.4 | Fase 4 | Integração CRM Supabase + Google Calendar |
| Story 3.5 | Fase 5 | Testes, afinação e go-live |

---

*Plano de Implementação Agente SDR v1.0 — ARVEX | Aria (@architect) | 2026-04-30*
