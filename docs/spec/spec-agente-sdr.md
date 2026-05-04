# Spec — Agente SDR com IA (ARVEX)
**Versão:** 1.1
**Data:** 2026-04-30
**Status:** APPROVED — Revisado por @qa (Quinn)
**Owner:** Morgan (@pm)
**Rastreabilidade:** PRD ARVEX v1.0 → Frente 1 / Mapa Operacional v1.0 / SOP Fluxo de Vendas v1.0

---

## 1. Problema

**Fonte:** PRD ARVEX — Frente 1 + Mapa Operacional — Gargalo #1

Vitor e Gabriel gastam 2–3h/dia cada fazendo SDR manualmente via WhatsApp:
- Primeiro contato com leads que chegam via formulário na landing page
- Qualificação por nicho (Cindy Batista: dono(a) de ótica com loja ativa)
- Agendamento de call com closer
- Confirmação D-1 de calls agendadas
- Reativação de leads sem resposta em 24h

Isso impede que os sócios foquem em estratégia, copy e fechamento — funções de maior valor para a ARVEX.

**Impacto atual:** ~4–6h/dia dos dois sócios consumidas em tarefas operacionais replicáveis.

---

## 2. Solução

Agente de IA que opera como SDR no WhatsApp, 24/7, executando o fluxo completo de qualificação e agendamento sem intervenção humana — entregando ao closer apenas leads qualificados com resumo completo.

O agente **não substitui** o closer. Ele elimina o trabalho pré-closer que hoje consome os sócios.

---

## 3. Requisitos Funcionais

### FR-1 — Recepção de Lead
O agente deve **abordar proativamente** o lead via WhatsApp assim que o registro cair no CRM (Supabase), com saudação personalizada e abertura natural (não robótica). O lead não inicia — o agente inicia.

### FR-2 — Qualificação por Nicho
O agente deve qualificar o lead com base no nicho do expert vinculado. Para leads da **Cindy Batista**, o critério é: **dono(a) de ótica com loja ativa**. A qualificação ocorre via conversa natural, sem parecer formulário.

O fluxo é idêntico para todos os experts — lead preenche formulário → cai no CRM → agente aborda. Os critérios variam por nicho:

**Cindy Batista — nicho óptico:**
- Possui ótica própria (não funcionário)
- Loja em operação (não ideia/projeto)
- Interesse em aumentar vendas ou estruturar o digital da loja

**Critério de desqualificação (Cindy):** Lead que é funcionário de ótica, não tem loja própria, ou está em fase de ideia/sem operação → agente encerra conversa com gentileza e registra como "Desqualificado" no CRM.

**Dr. Alex — nicho HOF:**
- *(critérios a confirmar com Vitor antes da implementação)*

**ARVEX Geral:**
- *(critérios a confirmar com Vitor antes da implementação)*

### FR-3 — Resposta a Perguntas Frequentes
O agente deve responder perguntas sobre o processo, os produtos e a ARVEX com base em base de conhecimento definida pelo time.

### FR-4 — Agendamento de Call
O agente deve coletar disponibilidade do lead, verificar agenda do closer via Google Calendar e confirmar horário — criando evento automaticamente.

**Fallback — sem slot disponível:** Se não houver horário disponível nos próximos 3 dias úteis, o agente informa o lead e escala para Gabriel definir horário manualmente via WhatsApp.

### FR-5 — Confirmação D-1
O agente deve enviar mensagem de confirmação automática 24h antes de cada call agendada.

### FR-6 — Reativação de Leads Inativos
O agente deve reativar automaticamente leads que não responderam, com no máximo **3 tentativas** em cadência:
- D+1 — primeiro follow-up
- D+3 — segundo follow-up
- D+7 — última tentativa

Após 3 tentativas sem resposta, o lead é arquivado no CRM com status **"Sem resposta"** e Gabriel é notificado.

### FR-7 — Atualização no CRM
O lead já existe no Supabase ao chegar (criado pelo formulário). O agente deve atualizar o registro em tempo real:
- Atualização de status a cada etapa da qualificação
- Registro do histórico de conversa em `activities` (JSONB)
- Atualização do campo `data_call` ao agendar

### FR-8 — Handoff para Closer
Ao qualificar um lead, o agente deve notificar Gabriel via WhatsApp com:
- Nome e contato do lead
- Resumo da qualificação (profissão, dor principal, interesse)
- Horário da call agendada
- Link para o lead no CRM

### FR-9 — Escalada Automática
O agente deve identificar situações fora do script (objeção complexa, lead de alto ticket, resposta inesperada) e escalar para Gabriel com contexto completo da conversa.

### FR-10 — Transcrição de Áudio
O agente deve transcrever mensagens de voz enviadas pelo lead via Whisper API e processar o texto como texto normal.

---

## 4. Requisitos Não-Funcionais

### NFR-1 — Disponibilidade
O agente deve operar 24/7, com uptime mínimo de 99% (Railway garante isso com restart automático).

### NFR-2 — Tempo de Resposta
Resposta ao lead em no máximo 30 segundos após receber mensagem.

### NFR-3 — Tom de Comunicação
O agente deve soar humano, próximo e profissional — nunca robótico. Nome do agente: **Carol** (persona feminina da ARVEX).

### NFR-4 — Segurança e LGPD
- Número WhatsApp dedicado (não o número principal dos sócios)
- Credenciais da Evolution API e Supabase armazenadas como variáveis de ambiente no Railway
- Nenhum dado sensível exposto nos logs do N8N
- **Opt-in obrigatório:** o formulário da landing page deve conter campo de consentimento explícito para contato via WhatsApp (LGPD), antes do agente abordar o lead

### NFR-5 — Rastreabilidade
Toda interação deve ser registrada no Supabase para auditoria e melhoria contínua do prompt.

---

## 5. Stack Técnica

| Componente | Tecnologia | Justificativa |
|-----------|-----------|--------------|
| WhatsApp | Evolution API (self-hosted, Railway) | Open source, sem aprovação Meta, gratuito |
| Orquestrador | N8N (self-hosted, Railway) | Flexibilidade total, node Supabase nativo |
| Inteligência | Claude API (claude-sonnet-4-6) | Melhor compreensão de contexto, conversas longas |
| Memória de conversa | Redis (Railway) | Contexto por número de telefone entre mensagens |
| CRM | Supabase — CRM próprio ARVEX | Já construído, tabela `leads` com todos os campos |
| Agendamento | Google Calendar API | Integração nativa N8N, elimina Calendly |
| Transcrição de áudio | Whisper API (OpenAI) | Leads enviam áudio no WhatsApp |

**Custo estimado:** R$ 75–105/mês

---

## 6. Fluxo Principal

```
Lead preenche formulário (Landing Page)
          ↓
Registro criado no Supabase (CRM ARVEX)
          ↓
N8N detecta novo lead (Supabase trigger)
          ↓
Agente (Carol) aborda lead proativamente
via Evolution API → WhatsApp
          ↓
Lead responde
          ↓
[Áudio?] → Whisper transcreve → texto
          ↓
Redis recupera contexto da conversa
          ↓
Claude API processa mensagem + contexto
          ↓
      [Decisão Claude]
     ↙      ↓       ↘
Qualificado  Conversa  Fora do script
     ↓       continua      ↓
Agendar call    ↓      Escalar Gabriel
     ↓      Responde       ↓
Google Calendar  ↓    WhatsApp Gabriel
cria evento      ↓         ↓
     ↓      Evolution   Contexto
Supabase    API envia   completo
atualiza    mensagem
status lead ao lead
     ↓
Notifica Gabriel
(resumo + link CRM)
```

---

## 7. Fluxo de Exceção — Escalada

**Triggers de escalada automática:**
- Lead faz pergunta técnica sobre o método que o agente não sabe responder
- Lead demonstra irritação ou urgência extrema
- 3 mensagens consecutivas sem qualificação avançando
- Lead solicita explicitamente falar com humano

**Ação:** Agente informa ao lead que vai conectar com especialista → notifica Gabriel com histórico completo → Gabriel assume a conversa.

---

## 8. Personas e Experts

O agente deve adaptar sua comunicação conforme o expert vinculado ao lead:

| Expert | Nicho | Tom do Agente |
|--------|-------|--------------|
| Cindy Batista | Óptico | Próximo, prático, foco em resultado na loja |
| Dr. Alex | HOF | Mais técnico, autoridade, foco em posicionamento |
| ARVEX Geral | Profissional liberal | Neutro, estratégico |

---

## 9. Base de Conhecimento Inicial

**Mecanismo:** System prompt estático injetado no Claude a cada conversa — resumo estruturado dos SOPs, produtos e tom. Sem RAG na v1 (contexto suficiente para o escopo do nicho Cindy).

**Conteúdo do system prompt:**
- Persona Carol: quem é, tom, missão
- Critério de qualificação Cindy (ótica com loja ativa)
- Produtos e tickets (Mentoria R$5k, Assessoria R$7k, Consultoria R$10k)
- Fluxo de qualificação resumido (baseado no SOP Fluxo de Vendas)
- Principais objeções e respostas (a validar com Gabriel antes da implementação)
- Quando escalar para Gabriel (triggers de escalada)

**Fontes-base:**
- `docs/processos/sop-fluxo-vendas.md`
- `docs/processos/playbook-rotina-sdr.md`

---

## 10. Critérios de Sucesso

| Métrica | Baseline Atual | Meta 90 dias |
|---------|---------------|-------------|
| Tempo de resposta ao lead | Horas (manual) | < 30 segundos |
| Horas/dia dos sócios em SDR | 4–6h | < 30 min (supervisão) |
| Taxa de leads qualificados/total | Não medida | Estabelecer baseline |
| Shows na call (presença) | Não medida | > 70% |
| Custo operacional SDR | R$3.000+ (SDR humano) | R$75–105/mês |

---

## 11. Fora do Escopo (v1)

- Integração com Instagram DM (v2)
- Relatórios automáticos de performance (v2)
- Múltiplos agentes simultâneos por expert (v2)
- Integração com tráfego pago (Meta Ads → agente) (v2)
- Fechamento automatizado (sempre humano)

---

## 12. Rastreabilidade de Requisitos

| Requisito | Fonte |
|-----------|-------|
| FR-1, FR-2, FR-3 | PRD Frente 1 — "Recepção e qualificação automática" |
| FR-4, FR-5 | Playbook SDR — "Confirmar calls D-1" |
| FR-6 | Playbook SDR — "Regra de ouro: nenhum lead sem contato 24h" |
| FR-7 | Mapa Operacional — CRM próprio ARVEX |
| FR-8, FR-9 | SOP Fluxo de Vendas — "SDR → Closer handoff" |
| FR-10 | Research @analyst — "Leads enviam áudio no WhatsApp" |
| NFR-3 | Mapa Operacional — "Peso mental constante" com tom robótico |

---

## 13. Dependências

- CRM ARVEX (Supabase) operacional — Story 2.1 ✅
- Número WhatsApp dedicado criado antes do desenvolvimento
- Script de qualificação validado com Gabriel antes da implementação
- Google Calendar do closer compartilhado para integração

---

*Spec Agente SDR v1.0 — ARVEX | Morgan (@pm) | 2026-04-30*
