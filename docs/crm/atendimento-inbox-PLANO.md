# Atendimento — Plano de evolução do inbox

> Autor: @aiox-master (Orion) · 2026-07-29
> Origem: benchmark contra SaaS de atendimento de linhagem Chatwoot (print trazida pelo Vitor)
> Escopo: módulo Atendimento do `arvex-crm` (`docs/crm/index.html` + `supabase/functions/evolution-proxy`)

---

## 1. Ponto de partida (medido, não suposto)

Estado em 2026-07-30:

| Item | Hoje |
|---|---|
| Fonte da conversa | `agente_sdr_historico` (Evolution → sync nos 2 sentidos, escopo lead-ou-nova) |
| Volume | 112+ msgs · 14 conversas · número da Thalita |
| Estado da conversa | ✅ `conversa_estado` + abas Geral/Aguardando/IA derivadas |
| Mídia recebida | corrigida na v18 (busca a mensagem inteira antes do base64) — **aguarda confirmação na tela** |
| Mídia enviada | ❌ só texto sai do CRM |
| Latência | ⚠️ até 25s (polling, e só com a aba aberta) |
| Nome do contato | ⚠️ número cru quando não há lead com aquele telefone |
| Responsável | ✅ dono do número conectado (`profileName`) |
| Carol | `agente_sdr.ativo = false` (desligada) |
| Edge | `evolution-proxy` v18 · actions: qr · status · send · disconnect · sync_out · diag · media |

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

### ✅ Fase 1 — Leitura do chat — ENTREGUE (main `0c70fc3` · `38322b6`)
Separador de dia · hora curta · avatar de iniciais · mídia com cara de player + autoload das últimas 8 · chat ocupando a tela (`100vh - 132px`) · áudio 260px e imagem até 320px.

### ✅ Fase 2 — Estado + abas — ENTREGUE (main `16d3cdd` · `9b8e091`)
`conversa_estado` (session_id PK) · botão Resolver/Reabrir · abas **Geral · Aguardando · IA** todas DERIVADAS · reabertura automática por comparação de timestamp (sem trigger) · contador de não-lida em destaque por aba · poll recarrega estados (inbox compartilhado).

### ⏳ Fase 2.1 — Mídia recebida — CORRIGIDA, aguarda confirmação (edge v18)
Estava quebrada: mandava só `{key:{id}}` e o Evolution respondia `400 Cannot read properties of null (reading 'ephemeralMessage')`. Agora busca a mensagem inteira no `findMessages` antes de pedir o base64.
- **Verificação (bloqueia a Fase 3):** abrir a conversa da Thainá (2 áudios de 29/07 20:41) e uma com imagem → tocar/ver. Falha nova fica em `_evo_sync_debug` com `acao='media'`.

---

### Fase 3 — Enviar mídia pelo CRM ⭐ prioridade
**Por quê:** hoje só texto sai daqui. Em óptica o cliente manda receita e a SDR precisa mandar foto de armação — sem isso ela volta pro celular, e todo o controle que construímos evapora junto.
- **Executor:** `@dev` (Dex) · **Edge:** nova action no `evolution-proxy`
- **Entrega:** botão de anexo (foto/arquivo) · gravar áudio no próprio CRM (`MediaRecorder`)
- **Endpoints Evolution:** `/message/sendMedia/{inst}` (imagem/documento) · `/message/sendWhatsAppAudio/{inst}` (áudio, base64)
- **AC:**
  - [ ] anexar foto e enviar → chega no WhatsApp do cliente
  - [ ] gravar áudio no CRM e enviar → chega como áudio (não como arquivo)
  - [ ] a mensagem enviada aparece no histórico com `wa_id` (o `send` já grava; estender para mídia)
  - [ ] limite de tamanho tratado com erro claro, não falha muda
- **Risco conhecido:** o `send` atual grava o turno do operador em `agente_sdr_historico`; a versão com mídia precisa gravar `additional_kwargs.media` para o balão renderizar player em vez de texto vazio

### Fase 4 — Tempo real (matar o atraso de 25s)
**Por quê:** chat que demora 25s parece quebrado. E o polling só roda com a aba aberta.
- **Decisão:** `@architect` (Aria) — Realtime do Supabase na `agente_sdr_historico` (a tabela **já está** na publicação `supabase_realtime`, feito na Fase 1 de 2026-07-24) × manter polling só como fallback. Definir também se o `sync_out` continua em 25s ou afrouxa para 60s quando o Realtime estiver ativo.
- **Executor:** `@dev`
- **AC:**
  - [ ] mensagem que chega no WhatsApp aparece no chat em < 3s, sem recarregar
  - [ ] a lista reordena sozinha (conversa sobe para "Geral")
  - [ ] reconecta sozinho depois de perder rede
  - [ ] o polling continua existindo como rede de segurança — Realtime caído não pode significar inbox parado

### Fase 5 — Identidade do contato (barata, vai junto com 3 ou 4)
Metade do inbox mostra número cru quando não há lead com aquele telefone.
- **Executor:** `@dev`
- **Entrega:** guardar o `pushName` do WhatsApp no sync e usá-lo como nome quando não houver lead
- **AC:**
  - [ ] conversa sem lead mostra o nome do WhatsApp, não o número
  - [ ] havendo lead, o nome do lead continua ganhando (é o dado curado)
- **Verificar antes:** confirmar que o `findMessages` do Evolution v2.3.7 devolve `pushName` nos registros

### Fase 6 — Respostas rápidas por `/`
- **Executor:** `@dev` · **Conteúdo:** `Comercial:sdr-playbook-manager` (as mensagens padrão são ativo comercial, não texto solto de dev)
- **AC:**
  - [ ] `/` no composer abre a lista e filtra por digitação; Enter insere
  - [ ] editável sem deploy (tabela, não hardcoded — mesma lição do `CS_SUBS`)

### Fase 7 — Higiene do inbox
- **Schema:** `@data-engineer` · **Executor:** `@dev`
- **Entrega:**
  1. **não-lida no banco** (hoje é `localStorage`: a Thalita perde ao trocar de máquina e o Vitor não vê o que ela já leu — num inbox compartilhado isso é furo)
  2. **botão "não é atendimento"** → remove a conversa e alimenta `evo_sync_state.ignorados` (a coluna já existe). Fecha o furo conhecido: pela regra, toda conversa NOVA entra, inclusive pessoal
- **AC:**
  - [ ] marcar lido numa máquina reflete na outra
  - [ ] conversa ignorada some e não volta no próximo sync

### Fase 8 — Histórico completo
- `findMessages` traz 300 mensagens e não há "carregar mais" ao rolar para cima; conversa antiga fica cortada.
- **Executor:** `@dev` · **AC:** rolar para o topo carrega o lote anterior sem perder a posição

### Fase 9 — Multi-conta (quando o número deixar de ser só o da Thalita)
- **Executor:** `@architect` + `@data-engineer` + `@dev`
- Uma instância Evolution por pessoa (`arvex-thalita`, `arvex-vitor`), origem gravada por mensagem, filtro por caixa. Hoje 1 instância = 1 número — foi isso que misturou as conversas da Thalita com as do Vitor.

### Fora do plano por enquanto (registrado para não voltar como "esqueceu")
Busca dentro do texto das mensagens · status de entregue/lido · waveform no player de áudio (exige decodificar no cliente) · notificação sonora.

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

```
✅ 1 Leitura  →  ✅ 2 Estado/abas  →  ⏳ 2.1 Mídia recebida (CONFIRMAR na tela)
                                          │
                                          ▼
                        3 Enviar mídia  +  5 Nome do contato      ← próximo
                                          │
                                          ▼
                        4 Tempo real (decisão de @architect)
                                          │
                                          ▼
                        6 Respostas rápidas  →  7 Higiene  →  8 Histórico
                                          │
                                          ▼
                        9 Multi-conta (quando o Vitor decidir)
```

**Gate único antes de seguir:** a Fase 2.1 precisa ser confirmada na tela. Não faz sentido construir envio de mídia (Fase 3) se receber mídia ainda estiver quebrado — seria construir por cima de fundação não verificada, que foi exatamente o erro que gerou o incidente das 76.145 linhas.

**Por que 3 antes de 4:** enviar mídia decide se a Thalita usa o CRM ou volta pro celular; tempo real melhora a experiência de quem já está usando. Adoção antes de polimento.

**Ritmo:** uma fase por vez, publicando ao fim de cada uma (`project_crm_deploy_flow`). Nada de acumular três fases num deploy só — foi assim que o sync foi ligado junto com a mudança de escopo e virou incidente.
