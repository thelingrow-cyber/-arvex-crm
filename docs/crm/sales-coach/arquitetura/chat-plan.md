# Plano — Chat do Sales Coach ("converse com a call")

**Autor:** Orion · Data: 2026-06-29 · Status: plano pronto p/ executar
**Refs:** sales-coach-vision.md (camada 4), arquitetura/infra já no ar (Edge Function analyze-meeting v4, tabela meetings, CRM aba "Reuniões").

## 1. Objetivo
Transformar a análise estática em **conversa**: dentro do detalhe da reunião, o closer pergunta e a IA responde **como diretor comercial, olhando a transcrição + a análise daquela call**. É o que faz o produto virar "mentor", não relatório.

## 2. Escopo
**IN (MVP):**
- Chat **sobre 1 reunião** (a aberta no detalhe).
- IA responde grounded na transcrição + scores/insights daquela call, na persona diretor.
- Histórico da conversa **persistido** na reunião.
- Pode referenciar o banco de conhecimento (casos) se relevante.

**OUT (fase 2):**
- Chat **geral** ("como tô evoluindo?", comparar N calls) → precisa de RAG sobre histórico (pgvector). Depois.
- Comparação automática com casos via embeddings (por enquanto, citação textual simples).

## 3. Arquitetura (reaproveita 100% a infra atual)
```
Front (detalhe da reunião)
  painel de chat: lista de mensagens + input
  → sb.functions.invoke('coach-chat', { meeting_id, pergunta })
        ↓
  Edge Function coach-chat (Deno, import npm:@supabase/supabase-js@2, verify_jwt=false)
    1. lê a meeting (transcript, scores, insights, chat) via service_role
    2. monta contexto: SYSTEM diretor + RESUMO da análise + transcript + histórico do chat
    3. chama Claude (multi-turn messages) → resposta
    4. faz append da pergunta+resposta em meetings.chat (jsonb)
    5. retorna a resposta
  → Front renderiza a resposta e atualiza o histórico
```

### 3.1 Dados (1 coluna nova, aditivo)
```sql
alter table meetings add column if not exists chat jsonb not null default '[]';
```
`chat` = array de `{role:'user'|'assistant', content:'...', at:timestamp}`.

### 3.2 Edge Function `coach-chat`
- Mesma "receita" da analyze-meeting (que já funciona): `import npm:@supabase/supabase-js@2`, `Deno.serve`, service_role, CORS, verify_jwt=false.
- Input: `{ meeting_id, pergunta }` (ou `messages` completo — mas servidor relê o histórico do banco p/ ser fonte da verdade).
- Contexto pro Claude:
  - **system:** persona diretor comercial (reutiliza o SYSTEM da analyze-meeting, adaptado pra modo conversa: "responda à pergunta do closer sobre ESTA call, baseado na transcrição e na análise; seja específico, cite trechos; tom de mentor").
  - **messages:** histórico (meetings.chat) + a nova pergunta. A transcrição + resumo da análise entram como contexto no 1º turn (ou no system) pra não reenviar a cada msg (otimização: pode truncar transcrição se muito longa).
- max_tokens ~1500, temperature ~0.3 (conversa um pouco mais natural que a análise).
- Persiste `chat` atualizado. Retorna `{ ok, resposta }`.

### 3.3 Front (painel no detalhe)
- No modal de detalhe (openMeeting), abaixo da análise, um bloco **"Converse sobre esta call"**:
  - lista de mensagens (user à direita, IA à esquerda), escapando HTML (esc) — anti-XSS.
  - input + botão enviar; Enter envia.
  - estado "digitando…" enquanto espera.
  - sugestões de perguntas (chips): "Onde perdi a venda?", "Negociei cedo?", "Qual pergunta faltou?", "Como você faria diferente?".
- Ao abrir o detalhe, carrega `meeting.chat` existente.
- Demo mode (?demo=1): chat simulado (respostas fixas) sem chamar a função.

## 4. Prompt / persona (consistência)
Mesmo "diretor comercial" da análise, em modo conversa. Regras: responder SÓ sobre esta call (grounded na transcrição/análise), citar trechos reais, ser direto e prático, no tom de mentor; se perguntarem comparação com caso conhecido, usar o que estiver no contexto. Não inventar dados fora da call.

## 5. Segurança
- `verify_jwt=false` (igual analyze-meeting, pra invocação chegar). Risco baixo (UUID-gated). TODO geral: reapertar auth das funções depois.
- service_role só na função. XSS: escapar tudo que vem do chat na renderização.
- Dado sensível (transcrição) não sai além da API do Claude.

## 6. Stories / tarefas
- **C1 — DB:** `alter table meetings add column chat jsonb default '[]'` (SQL via Management API, aditivo).
- **C2 — Edge Function `coach-chat`:** criar + deploy via Management API (import npm!, verify_jwt off). Validar boot (sem BOOT_ERROR) + 1 chamada real.
- **C3 — Front:** painel de chat no detalhe (lista, input, chips, estados, demo) no docs/crm/index.html. Validar headless ?demo=1.
- **C4 — Deploy front:** push pra -arvex-crm main com PROTOCOLO (fetch, diff aditivo, sem force).

## 7. Plano de testes
- C1: coluna existe, default [].
- C2: boot OK (sem BOOT_ERROR), responde a uma pergunta real grounded na call, persiste no chat.
- C3 (headless demo): painel renderiza, envia, mostra resposta, escapa XSS, chips funcionam.
- E2E: abrir reunião analisada → perguntar "onde perdi?" → resposta coerente → recarregar → histórico persiste.

## 8. Rollout
Banco (C1) → Função (C2, via API) → Front (C3+C4, push main protocolo). Tudo aditivo; rollback = restaurar index.html anterior / dropar coluna chat (isolada).

## 9. Custo
~centavos por mensagem (Claude, contexto da call). Irrelevante no volume.

---
**Pronto pra executar.** Ordem: C1 → C2 → C3 → C4. Mesma stack/receita que já está funcionando (npm import, Management API, protocolo de push seguro).
