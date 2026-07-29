# Atendimento — Plano de evolução do inbox

> Autor: @aiox-master (Orion) · 2026-07-29
> Origem: benchmark contra SaaS de atendimento de linhagem Chatwoot (print trazida pelo Vitor)
> Escopo: módulo Atendimento do `arvex-crm` (`docs/crm/index.html` + `supabase/functions/evolution-proxy`)

---

## 1. Ponto de partida (medido, não suposto)

Estado em 2026-07-29, depois de o sync entrar no ar:

| Item | Hoje |
|---|---|
| Fonte da conversa | `agente_sdr_historico` (Evolution → sync nos 2 sentidos) |
| Volume | 112 msgs · 14 conversas · número da Thalita |
| Estado da conversa | **não existe** — lista única, cresce para sempre |
| Mídia | áudio/imagem por clique (`action media`, base64 on-demand) |
| Responsável | dono do número conectado (`profileName`) |
| Carol | `agente_sdr.ativo = false` (desligada) |

## 2. Benchmark — o que adotar e o que recusar

**Adotar:**
1. Conversa com **estado** (Aberto / Aguardando / Fechado / IA) + contadores e filtro.
2. **Leitura limpa**: separador de data por dia, hora curta no balão, avatar com iniciais, mídia com cara de player.
3. **Respostas rápidas** por `/` no composer.
4. **Gravar áudio** dentro do CRM.

**Recusar (com motivo):**
- Etiquetas no contato → o pipeline (`leads.status`) já classifica; duas taxonomias competindo viram lixo.
- Nota privada no chat → o lead já tem campo de notas; duplicar espalha a informação.
- Notificação sonora → o contador de não-lida já existe e resolve.
- Deal board paralelo → o kanban é a fonte de verdade (mesma decisão do `SALES-COACH-V2-FABLE.md`).

**A vantagem que NÃO se deve perder copiando o Chatwoot:** aqui a conversa vive no mesmo banco do lead, da venda e do pipeline. "Assumir", "Transferir", "Ver lead" e pausar a Carol são joins, não integrações. Nenhuma mudança de inbox pode quebrar isso.

## 3. Fases, agentes e gates

Metodologia: SDC (`workflow-execution.md` §1). Multi-camada (schema + edge + front) → justifica ciclo completo nas fases 2+; Fase 1 é front puro e vai por `@dev` direto (padrão ~80% do Vitor, `feedback_sdc_decision_pattern`).

### Fase 1 — Leitura do chat (front puro, sem schema)
- **Executor:** `@dev` (Dex) · **Revisão visual:** `@ux-design-expert` (Uma) se algo fugir dos tokens
- **Entrega:** separador de data por dia · hora curta (HH:MM) no balão · avatar com iniciais por autor · mídia com aparência de player + autoload limitado das últimas 8 mídias da conversa aberta
- **AC:**
  - [ ] a data aparece UMA vez por dia, não em cada balão
  - [ ] balão mostra só `HH:MM`
  - [ ] avatar com 2 letras identifica lead / Carol / responsável
  - [ ] áudio e imagem da conversa aberta carregam sem clique (até 8); acima disso, sob demanda
  - [ ] mobile: nada estoura a largura (heurística A2 — mobile é o juiz)
- **Verificação:** abrir uma conversa com áudio + imagem + mensagens de 2 dias distintos, desktop e mobile

### Fase 2 — Estado da conversa (o que dá controle)
- **Decisão arquitetural:** `@architect` (Aria) — **a conversa não tem tabela própria hoje** (é agrupamento por `session_id` em `agente_sdr_historico`). Decidir: tabela `conversas` própria × coluna em `leads` × tabela leve `conversa_estado(session_id, estado, ...)`. Impacta multi-conta futura e o SaaS Viziom.
- **Schema:** `@data-engineer` (Dara) — DDL, índices, RLS por role (padrão `is_admin()` / `is_cs_or_admin()` já existente)
- **Implementação:** `@dev` (Dex) — abas com contadores, filtro, ação de fechar/reabrir/pôr em espera
- **Gate:** `@qa` (Quinn) — 7 checks; atenção a RLS (SDR não pode fechar conversa de outro, se a regra for essa)
- **AC:**
  - [ ] abas Aberto / Aguardando / Fechado / IA com contagem correta
  - [ ] fechar conversa a remove de "Aberto" sem apagar histórico
  - [ ] mensagem nova do cliente reabre a conversa automaticamente
  - [ ] estado sobrevive ao polling de 25s e ao reload

### Fase 3 — Produtividade da SDR
- **Executor:** `@dev` (Dex) · **Conteúdo das respostas:** `Comercial:sdr-playbook-manager` (as mensagens padrão são ativo comercial, não texto solto de dev)
- **Entrega:** respostas rápidas por `/` (atalho → texto) · gravar áudio no CRM (`MediaRecorder` → `sendWhatsAppAudio` no Evolution)
- **AC:**
  - [ ] `/` abre a lista e filtra por digitação; Enter insere no composer
  - [ ] áudio gravado no CRM chega no WhatsApp do cliente e aparece no histórico
- **Dependência:** áudio precisa de nova action no `evolution-proxy` (`/message/sendWhatsAppAudio`)

### Fase 4 — Multi-conta (só quando o Vitor decidir)
- **Executor:** `@architect` + `@data-engineer` + `@dev`
- Uma instância Evolution por pessoa (`arvex-thalita`, `arvex-vitor`), origem gravada por mensagem, filtro por caixa. Hoje é 1 instância = 1 número; foi isso que misturou as conversas da Thalita com as do Vitor.

## 4. Autoridades respeitadas

- `git push` / deploy de produção: **`@devops` (Gage)** — exclusivo (`agent-authority.md`)
- Publicação segue `project_crm_deploy_flow`: cópia `docs/crm/index.html` → raiz na `main`, **nunca** merge, reconciliando antes
- Edge function: deploy via Management API, sempre com o fonte commitado no repo primeiro (o repo já ficou atrás do deploy uma vez — ver `project_crm_divergencia_master_main`)

## 5. Travas que não podem ser removidas

Herdadas do incidente das 76.145 linhas (2026-07-29):
1. índice único em `agente_sdr_historico.wa_id` — duplicação barrada pelo banco
2. disjuntor de 500 candidatos por ciclo no `sync_out`
3. regra de escopo (lead OU conversa nova) — sem ela o sync despeja a caixa pessoal
4. todo `.select()` de guard com `.limit()` explícito (PostgREST trunca em 1000 em silêncio)

## 6. Ordem de execução

`Fase 1 (agora, front puro) → Fase 2 (decisão de @architect primeiro) → Fase 3 → Fase 4 (quando o número deixar de ser só da Thalita)`
