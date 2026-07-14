# Agente SDR × Pipeline — Arquitetura completa (estado alvo de primeira linha)

> Autor: Aria/@architect via Fable 5 · 2026-07-14
> Escopo: como o agente SDR (Carol) vive DENTRO do pipeline do CRM — cadência de follow-up,
> movimentação automática de cards, takeover humano, escalação e UX de primeira qualidade.
> Complementa (não substitui): `VIZIOM-INTEGRATION-PLAN.md` (visão geral F0-F4) e
> `AGENTE-SDR-F2-ARCHITECTURE.md` (cérebro conversacional — construído, draft `h8Ka2arQgTvl92oD`).
> Benchmark de mercado usado: Apollo/HubSpot Sequences (cadência como objeto), Kommo/Pipedrive
> (automação move cards + rotting), SleekFlow/Umbler/Zaia (human takeover — recurso universal
> que ainda não temos).

## 0. Princípios (extraídos do que os líderes de mercado convergiram)

1. **O kanban é a única fonte de verdade.** O agente MOVE cards — o time enxerga o trabalho
   do robô no mesmo lugar onde já trabalha. Nenhuma aba paralela de "follow-up" (estado
   duplicado = um dos dois sempre mentindo).
2. **Cadência é overlay, não coluna.** O lead em cadência automática MORA em Contato e
   CARREGA um badge (`toque 2/4 · próx. 14h`). Padrão Apollo/HubSpot: enrollment ortogonal
   ao estágio.
3. **Humano sempre pode assumir em 1 clique.** `Pausar agente` por lead. Sem isso a Carol
   responde por cima da Thalita — é o recurso nº 1 de toda ferramenta conversacional BR.
4. **Saída automática da cadência.** Lead respondeu / mudou de coluna / fechou → cadência
   cancela sozinha (parcialmente construído: F2 já cancela ao responder).
5. **Nada de estado inventado no front.** Badge lê `sdr_followups` real; timeline lê
   `activities` real. Zero espelhos.

## 1. Estado atual (verificado no código em 2026-07-14)

| Peça | Estado | Onde |
|---|---|---|
| Pipeline 8 colunas | ✅ vivo | `index.html` `COLS` (linha ~1342): novo, contato, qualificado (fase SDR) · call, followup, quente (fase Closer) · fechado, perdido |
| F1 ponte inbound | ✅ produção | workflow n8n publicado, path secreto |
| F2 cérebro (IA + memória) | ✅ construído, DRAFT | `n8n-agente-sdr-f1-f2-completo.json` (`h8Ka2arQgTvl92oD`) — testado com Claude real; falta QR do WhatsApp + publicar |
| Outbound abertura | ✅ construído, DRAFT | `n8n-agente-sdr-outbound-v1.json` (`JfDuGjH32zoqQpCt`) |
| Fila de cadência | ✅ schema aplicado, populada, **ninguém consome** | `sdr_followups` + `agente_sdr.cadencia` `{"toques_horas":[4,24,48,168],"encerra_horas":192}` |
| `registrar_evento_lead` RPC | ✅ produção | grava em `leads.activities` (jsonb), cria lead se não existe |
| `status_history` | ✅ trigger no banco | UPDATE em `leads.status` registra transição sozinho (`origem='trigger'`) — o n8n NÃO precisa gravar histórico manualmente |
| SLA badge "Xh sem contato" | ✅ vivo (só status novo) | `getSLABadge()` (~linha 2636) |
| Realtime no board | ✅ vivo | render represado durante drag (`aplicarRenderPendente`) |

### 1.1 BUGS DE INTEGRAÇÃO encontrados nesta análise (corrigir na Fase B)

**BUG-A — formato de `activities` incompatível (as mensagens do agente NÃO aparecem no modal hoje).**
- O front grava/lê `{ text, date }` com `date` em epoch-ms (`index.html` ~2944: `a.text`, `fmtDate(a.date)`).
- A RPC `registrar_evento_lead` grava `{ autor, texto, data }` com `data` ISO (`setup-agente-sdr-bridge-v1.sql`).
- Resultado: evento do agente renderiza `undefined` na timeline do lead.
- Fix (duplo, obrigatório): (a) RPC passa a gravar `{ text, date (epoch ms), autor }` —
  compatível com o front e adiciona `autor`; (b) front ganha `normAct()` que aceita ambos
  os formatos (há linhas antigas já gravadas no formato ISO que não podem sumir).

**BUG-B — a coluna "Follow Up" é da fase CLOSER, não SDR.**
- `COLS`: `{ id:'followup', phase:'closer' }` — semântica atual = follow-up do closer pós-call.
- Decisão arquitetural: a cadência automática da Carol **NUNCA usa essa coluna**. Cadência
  SDR = badge sobre o card em `contato`. A coluna followup continua intocada para o closer.

## 2. Modelo de dados — delta (arquivo: `setup-sdr-pipeline-v3.sql`, aditivo/idempotente)

```sql
-- 2.1 Human takeover + estado de escalação
alter table leads add column if not exists agente_pausado boolean not null default false;
alter table leads add column if not exists agente_escalado_em timestamptz; -- null = nunca

-- 2.2 RPC corrigida (BUG-A): grava no formato do front + autor
--     (substitui o corpo de registrar_evento_lead; assinatura idêntica → n8n não muda)
--     v_evento := jsonb_build_object('text', p_texto, 'date', (extract(epoch from now())*1000)::bigint, 'autor', p_autor);

-- 2.3 RPC de movimentação pelo agente (o trigger de status_history cuida do histórico)
create or replace function agente_mover_status(p_lead_id uuid, p_status text)
returns void language sql security definer as $$
  update leads set status = p_status where id = p_lead_id
    and status not in ('fechado','perdido');          -- agente NUNCA mexe em resultado final
$$;
-- grants: service_role apenas (a UI não usa)

-- 2.4 View para o front (1 fetch = todos os badges do board)
create or replace view v_cadencia_ativa as
  select f.lead_id, f.tentativa, f.agendado_para, f.status,
         l.agente_pausado, l.agente_escalado_em
  from sdr_followups f join leads l on l.id = f.lead_id
  where f.status = 'pendente';
-- RLS: herdada de leads via security_invoker
```

Regras duras: `agente_mover_status` só transita dentro de {novo→contato, contato→qualificado};
fechado/perdido/call/quente são EXCLUSIVOS de humano. Cadência esgotada NÃO move card
(ver Decisão D-1).

## 3. Motor n8n

### 3.1 Upgrades no F2 (draft `h8Ka2arQgTvl92oD` — editar o draft, continua não-publicado)

1. **Gate de takeover** (novo IF logo após `Buscar Config Agente`): se
   `lead.agente_pausado = true` → registra o evento do lead (RPC) e responde 200 **sem
   chamar a IA**. O humano está na conversa; o CRM continua logando tudo.
2. **Marcadores estruturados na resposta da IA** (padrão de mercado para bot→CRM):
   o system prompt instrui a Carol a terminar a resposta com, quando aplicável:
   - `[QUALIFICADO]` → Code node detecta, remove do texto antes de enviar, chama
     `agente_mover_status(lead, 'qualificado')` + notifica Thalita (3.4).
   - `[ESCALAR] motivo` → remove do texto, seta `agente_pausado=true` +
     `agente_escalado_em=now()`, notifica Thalita com o motivo. O card ganha badge vermelho.
   Sem marcador → fluxo normal. (Não usar function-calling aqui: 2 regex no Code node
   resolvem, zero dependência nova.)
3. **Cancelamento ampliado**: já cancela followup quando o lead responde ✅. Nada a fazer.

### 3.2 F4 — Processador de cadência (workflow NOVO, o gap nº 1)

Cron 15min (pode ser 2º branch do scheduleTrigger do outbound — decisão de layout na build):

```
buscar v_cadencia_ativa where agendado_para <= now()
para cada linha:
  lead ← GET leads/{lead_id}
  se lead.status != 'contato' OU lead.agente_pausado → followup.status='cancelado', pula
  toques ← agente_sdr.cadencia.toques_horas        (ler .length — NUNCA hardcode)
  proximo ← tentativa + 1
  se proximo < toques.length:
    texto ← AI Agente gera o toque (MESMA sessionKey=tel → memória da conversa inteira;
             prompt: "gere um follow-up curto e natural retomando o último assunto")
    enviar via Evolution (janela de horários do agente respeitada — grid já aprovado)
    registrar_evento_lead(tel, nome, texto, 'agente')
    followup: tentativa=proximo, agendado_para = now() + toques[proximo] horas
  senão:
    followup.status='concluido' · leads.obs='sem resposta (cadência esgotada)'
    (card FICA em contato com badge cinza — ver D-1)
```

O toque gerado pela IA com memória (em vez de 4 templates fixos) é o diferencial sobre
Apollo/HubSpot — follow-up que cita o assunto real da conversa converte mais e não soa robô.

### 3.3 Upgrade no outbound (draft `JfDuGjH32zoqQpCt`)

Após enviar a abertura com sucesso: `agente_mover_status(lead, 'contato')`. O card sai de
Novo sozinho — e o SLA badge de "Xh sem contato" (que só existe em novo) apaga, coerente.

### 3.4 Notificação à Thalita (escalação e qualificação)

Mensagem WhatsApp via a MESMA instância Evolution para `agente_sdr.notificar_contato`
(campo já existe, está NULL — preencher com o número real da Thalita, Decisão D-3):
`"🔔 [Carol] Lead {nome} ({tel}) — {qualificado para call | escalado: motivo}. Abrir: {link do CRM}"`.
V1 é isso; e-mail/painel de notificações é fase de polish.

### 3.5 Takeover automático (fase E — polish)

O webhook Evolution recebe `fromMe=true` quando UM HUMANO responde pelo celular/Web do
número da Carol. Se `fromMe=true` e o texto não é a última resposta que o próprio agente
enviou → `agente_pausado=true` por 24h. Padrão SleekFlow. Exige deduplicação cuidadosa
(a própria Carol gera fromMe=true ao enviar) — por isso fica pra fase E, com teste dedicado.

## 4. UX no CRM (`index.html`) — o que faz parecer produto de R$ 500/mês

### 4.1 Badge de agente no card (fase SDR apenas)

Novo badge abaixo do `getSLABadge()`, lendo `v_cadencia_ativa` (1 fetch no load + realtime):

| Estado | Visual |
|---|---|
| Em cadência | `🤖 Carol · toque 2/4 · próx. 14h` — dourado (`--gold2`), discreto |
| Escalado | `🔴 Escalado p/ humano · há 2h` — vermelho, chama o olho |
| Pausado (takeover) | `⏸ Agente pausado · Thalita na conversa` — cinza |
| Cadência esgotada | `✗ Sem resposta (4 toques)` — cinza, some quando humano agir |

Mesmo padrão visual dos badges existentes (`sla-badge`) — reusar classes, não inventar
sistema novo.

### 4.2 Modal do lead (`openDetail`) — seção "Conversa · Agente SDR"

- **Timeline estilo chat** (a killer feature visual): `activities` com `autor` renderiza
  como bolhas — lead à esquerda (navy), Carol à direita (dourado suave), humano à direita
  (verde). Sem autor (notas manuais antigas) → linha neutra atual. É o WhatsApp dentro do
  CRM, sem sair da tela.
- **Barra de controle do agente** no topo da seção:
  `[⏸ Pausar agente] / [▶ Retomar]` (toggle `agente_pausado`) ·
  `[✕ Cancelar cadência]` (PATCH followup→cancelado) ·
  estado atual em texto ("Carol ativa · próximo toque em 14h").
- Botões só aparecem para leads com `origem='whatsapp-agente-sdr'` ou followup existente.

### 4.3 Lista de Leads + Dashboard

- Filtro novo no select de status da lista: "🤖 Em cadência" (client-side, via set de
  lead_ids da view — não é um status real, não mexe no enum).
- Dashboard: card "Com a Carol agora: N" + "Escalados aguardando: N" (este pisca se > 0
  há mais de 1h — é fila de trabalho da Thalita).

### 4.4 Painel do Agente (fase E)

Dentro da config existente do agente: taxa de resposta por toque (1º/2º/3º/4º),
tempo médio até resposta, escalações/semana, conversões contato→qualificado atribuídas.
Alimentado por `activities` + `status_history` — dados já existem, é só agregar.

## 5. Fases de implementação (ordem de dependência)

| Fase | Entrega | Esforço | Depende de |
|---|---|---|---|
| **A — Ir ao ar** | QR escaneado + despublicar F1 antigo + publicar F1+F2 combinado | Vitor (QR) + 10min | — |
| **B — Fundação** | `setup-sdr-pipeline-v3.sql` (BUG-A fix, `agente_pausado`, `agente_mover_status`, view) + `normAct()` no front | 1 sessão | A |
| **C — Motor completo** | F4 processador + upgrades F2 (takeover gate, marcadores, notificação Thalita) + outbound move card | 1-2 sessões | B |
| **D — UX** | Badges no card + timeline chat + barra de controle + filtro + cards do dashboard | 1-2 sessões | B (roda em paralelo a C) |
| **E — Polish** | Auto-pause fromMe · painel de métricas · digest diário | depois de C+D vivos | C, D |

Cada fase: testar em draft/transação antes de publicar (protocolo que já usamos — F2 foi
testado com ROLLBACK e Test URL antes de qualquer coisa encostar em produção).

## 6. Decisões de negócio (defaults recomendados — Vitor confirma ou troca)

- **D-1 · Cadência esgotada:** card FICA em `contato` com badge "✗ sem resposta" + entra no
  filtro "Em cadência" como esgotado. NÃO vai pra Perdido automático — lead frio ≠ lead
  perdido, e o filtro vira lista de re-ataque manual/campanha. (Perder automático limpa o
  board mas esconde dinheiro.)
- **D-2 · Toques gerados pela IA** (não templates fixos): recomendado e assumido na seção 3.2.
- **D-3 · Número da Thalita** em `agente_sdr.notificar_contato` — está NULL de propósito
  (Art. IV, não inventamos). Sem ele, escalação/qualificação notifica ninguém.
- **D-4 · Qualificado move automático** com notificação (sem revisão prévia): a revisão
  humana acontece NA coluna Qualificado — é exatamente pra isso que ela existe.
