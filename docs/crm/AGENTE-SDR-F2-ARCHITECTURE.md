# Agente SDR ARVEX — F2 (cérebro conversacional) — arquitetura para build

> Autor: execução autônoma noturna (Sonnet 5) · 2026-07-14
> Status: **ESPECIFICADO, NÃO CONSTRUÍDO NO N8N.** Precisa de sessão ao vivo com credencial OpenAI real para montar e testar — ver seção 5.
> Pré-requisitos que já estão prontos: F0 (RLS fechada), F1 (ponte com path secreto, verificada), F4-schema (`sdr_followups` + `agente_sdr.cadencia`, aplicado).

## 1. Por que isto não foi construído às cegas esta noite

O kernel extraído do HUBLABEL (`n8n-agente-sdr-f2-kernel.json`) **não é reaproveitável verbatim**, ao contrário do que eu esperava antes de ler o arquivo com atenção. Todo o corpo do agente está amarrado ao schema multi-tenant do HUBLABEL: tabelas `SAAS_AgentesIA`, `SAAS_Conhecimentos`, `SAAS_Historico_AgenteIA`, `SAAS_Conversas_Agentes`, e um sistema de créditos/billing (`maxCreditos`, `MaxTokensIA`) — nada disso existe no banco do CRM ARVEX. Importar aquele JSON verbatim quebraria nó por nó.

O que **é** aproveitável de verdade, e o que este documento herda:
- Os **tipos de nó certos**: `@n8n/n8n-nodes-langchain.agent`, `lmChatOpenAi`, `memoryPostgresChat`, `embeddingsOpenAi`.
- A **sintaxe exata das conexões LangChain** (`ai_languageModel`, `ai_memory`, `ai_tool`, `ai_embedding`) — isto é o que mais erra de cabeça em n8n, e agora há prova concreta de como o n8n espera cada uma (ver seção 3).
- O padrão de **o agente ler a própria config do banco antes de rodar** — já é exatamente o desenho de `agente_sdr` (AD-3 do VIZIOM-INTEGRATION-PLAN: "o CRM comanda o agente").
- O código do node `REQUISICAO_DINAMICA` (ferramenta HTTP genérica) — sem dependência de schema, portável como está.

Decisão de escopo tomada aqui: **sem vector store / RAG na V1.** `agente_sdr.conhecimento` é `text` simples (confirmado no banco), não uma base fragmentada — entra direto no system prompt como contexto estático, igual a `instrucoes`. Construir um pipeline de embeddings + `pgvector` (que nem está instalado no banco — confirmado: `select extname from pg_extension` não lista `vector`) seria infraestrutura nova para um problema que não existe ainda (um único agente, uma base de conhecimento pequena). Se `conhecimento` crescer a ponto de estourar o context window, aí sim vale reabrir esta decisão.

## 2. O que precisa existir antes de qualquer teste

1. **Credencial OpenAI no n8n** (Vitor) — a HUBLABEL já tem uma ("OpenAi HUBLABEL"), mas reusá-la fere o AD-1 do VIZIOM-PLAN ("não fundir, não reescrever" — o HUBLABEL é produto de revenda, isolado). Criar credencial nova "OpenAI ARVEX SDR".
2. **F1 e outbound com credenciais reais** (Evolution + Supabase já resolvido na F1; outbound falta só a instância Evolution — ver relatório da madrugada).
3. **`agente_sdr` com uma linha real**: `instrucoes`, `conhecimento`, `qualificacao`, `mensagem_abertura` escritos por Vitor. Sem isso não há o que testar — e não é este documento nem eu quem inventa esse conteúdo (Constituição AIOX, Art. IV — No Invention).

## 3. Desenho dos nós (para a sessão de build)

Cadeia: `Webhook Evolution` (F1, já existe) → `Extrair Dados Evolution` (F1, já existe) → **a partir daqui, o que falta:**

| Node | Tipo | O que faz |
|---|---|---|
| `Cancelar Followup Pendente` | `httpRequest` PATCH | Se existir `sdr_followups` com `status='pendente'` pro `lead_id`, marca `cancelado` — o lead respondeu, a cadência para. |
| `Buscar Config Agente` | `httpRequest` GET (Supabase, mesma credencial da F1) | `agente_sdr?ativo=eq.true&limit=1` — mesmo padrão do `BUSCAR AGENTE` do kernel, mas lendo `agente_sdr` em vez de `SAAS_AgentesIA`. |
| `AI Agente` | `@n8n/n8n-nodes-langchain.agent` (typeVersion 1.7) | `promptType: define`, `text: ={{ $json.texto }}` (a mensagem do lead, do node `Extrair Dados Evolution`). System message interpola `instrucoes` + `conhecimento` + `qualificacao` do node anterior — ver esqueleto no fim deste doc. |
| `OpenAI Chat Model` | `lmChatOpenAi` (typeVersion 1.2) | `model.value = ={{ $('Buscar Config Agente').item.json.modelo }}` (campo já existe em `agente_sdr`). Credencial: "OpenAI ARVEX SDR". |
| `Postgres Chat Memory` | `memoryPostgresChat` (typeVersion 1.3) | `tableName: "agente_sdr_historico"` (nova, dedicada — **verificar ao vivo se o node cria a tabela sozinho ou se precisa de DDL manual antes; não confirmei isto sem testar**). `sessionKey: ={{ $json.tel }}` — telefone do lead como chave de sessão. |
| `Enviar Resposta (Evolution)` | `httpRequest` POST | Mesmo shape do node `Enviar Mensagem (Evolution)` do workflow outbound — reusar a mesma credencial Header Auth "Evolution ARVEX SDR" já criada na F1/outbound. |
| `Registrar Resposta no CRM` | `httpRequest` POST (rpc `registrar_evento_lead`) | `p_autor: 'agente'`, `p_texto` = a resposta gerada pela IA. **Response Format = Text** (mesmo fix aplicado na F1 — a RPC devolve escalar). |

### Conexões LangChain (copiar exatamente esta sintaxe — validada no kernel extraído):
```json
"OpenAI Chat Model": { "ai_languageModel": [[{ "node": "AI Agente", "type": "ai_languageModel", "index": 0 }]] },
"Postgres Chat Memory": { "ai_memory": [[{ "node": "AI Agente", "type": "ai_memory", "index": 0 }]] }
```

### Esqueleto do system prompt (sem inventar tom/conteúdo — só a estrutura):
```
INSTRUÇÕES:
{{ $('Buscar Config Agente').item.json.instrucoes }}

CONHECIMENTO:
{{ $('Buscar Config Agente').item.json.conhecimento }}

QUALIFICAÇÃO (o que perguntar antes de marcar call):
{{ $('Buscar Config Agente').item.json.qualificacao }}

REGRA DE ESCALONAMENTO:
{{ $('Buscar Config Agente').item.json.escalar_ativo === true ? $('Buscar Config Agente').item.json.escalar_instrucoes : 'Nunca escale — resolva pela conversa.' }}
```

## 4. F4 — processamento da cadência (ainda não construído, schema pronto)

O workflow outbound de hoje **enfileira** em `sdr_followups` (toque 0, +4h) mas não processa os toques seguintes nem encerra. Isso é outro branch do mesmo scheduleTrigger de 15min, ou um workflow separado — decisão de layout para a sessão de build, não arquitetural.

**Atualizado 2026-07-14:** cadência decidida com o Vitor tem 4 toques (não 3) — default agora é `toques_horas:[4,24,48,168]` (o último em 7 dias), `encerra_horas:192`. A lógica abaixo generaliza pra N toques (**não hardcode um índice fixo — leia o array inteiro**):

```
buscar sdr_followups where status='pendente' and agendado_para <= now()
para cada linha:
  se lead.status != 'contato' (respondeu e avançou) → status='cancelado', pula
  senão:
    toques = agente_sdr.cadencia.toques_horas  (array, hoje [4,24,48,168])
    proximo_indice = tentativa + 1
    se proximo_indice < toques.length:
      mandar toque, tentativa = proximo_indice,
      agendado_para = now() + toques[proximo_indice] horas
    senão:
      marcar leads.obs='sem resposta', sdr_followups.status='concluido'
```

Escrever a lógica assim (lendo `.length` do array em vez de contar 0/1/2 fixo) evita que uma futura mudança de cadência no jsonb quebre o workflow.

Cada "toque" precisa de um TEXTO — hoje `agente_sdr` só tem `mensagem_abertura`. Decisão pendente para a sessão de build: ou Vitor escreve 3 textos de toque (`cadencia` viraria armazenar os textos, não só as horas), ou o `AI Agente` da F2 gera o toque na hora (mais natural, mas exige F2 pronta primeiro). **Recomendo esperar a F2 estar viva e deixar o próprio agente gerar os toques de follow-up** — é menos trabalho de configuração pro Vitor e mais coerente (o agente lembra o contexto da conversa via `Postgres Chat Memory`).

## 5. Ordem recomendada da próxima sessão

1. Vitor cria credencial OpenAI + escreve `agente_sdr` (instrucoes/conhecimento/qualificacao/mensagem_abertura).
2. `@dev` monta os nós desta seção 3, importa INATIVO, testa com `Execute workflow` manualmente (não publicado) mandando mensagem de um número de teste.
3. Iterar: quase certo que vai ter 1-2 bugs reais só visíveis em execução (foi o padrão em F1 hoje — 2 bugs que só apareceram testando de verdade). Não estranhar, é o processo normal.
4. Só depois de uma conversa real ida-e-volta funcionando, publicar e ativar.
5. F4 (processamento de cadência) entra depois, com a F2 já viva.
