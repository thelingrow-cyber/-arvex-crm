# Agente SDR (Carol) — Plano Mestre de Execução

> Autor: Opus 4.8 · 2026-07-14 (atualizado após go-live real)
> Este é o roadmap ÚNICO do que falta pra Carol ficar completa. O "como" técnico de
> cada peça está nos docs de arquitetura (`AGENTE-SDR-PIPELINE-ARCHITECTURE.md`,
> `AGENTE-SDR-F2-ARCHITECTURE.md`, `VIZIOM-INTEGRATION-PLAN.md`). Aqui é a ORDEM, o
> STATUS e as DECISÕES.
> Objetivo final: Carol que **aborda, conversa, qualifica, agenda, faz follow-up,
> lembra da call e escala** — tudo visível e controlável no CRM.

## ✅ O que JÁ está no ar (baseline — 2026-07-14)

- **F0** — RLS fechada (segurança do banco).
- **F1** — Ponte inbound: mensagem que chega no WhatsApp vira lead + evento no CRM.
- **F2** — Cérebro: a Carol responde de verdade (Claude + memória por lead, 20 msgs de
  contexto). Tom ajustado (sem "estrategista óptico", abertura fiel ao texto real).
  **Balões com pausa "digitando"** ("Oi, tudo bom?" → ~2,5s → corpo).
- **Infra** — Instância WhatsApp conectada (número de TESTE), webhook ativo, workflow
  publicado. **A Carol atende leads reais que escrevem primeiro.**

**O que a Carol AINDA NÃO faz:** abordar lead novo sozinha, puxar quem não respondeu,
lembrar da call, mover card no kanban, escalar pra humano, aparecer direito no CRM.

---

## Roadmap — 5 fases, por valor de negócio × dependência

### FASE 1 — Carol CAÇADORA (não só atende, aborda) 🎯 maior valor imediato
**Problema que resolve:** hoje a Carol só responde quem escreve primeiro. Lead novo do
formulário fica esperando alguém abordar.
**Entrega:** publicar + testar o workflow **Outbound** (já construído, DRAFT
`JfDuGjH32zoqQpCt`). A cada 15 min ele pega leads novos e manda a mensagem de abertura,
com pausa anti-ban entre um e outro.
**Esforço:** 1 sessão (já existe, falta publicar + teste real + ajuste fino).
**Depende de:** nada. **Pode ser a próxima coisa.**

### FASE 2 — Carol que NÃO ESQUECE (follow-up automático) 🎯 segundo maior valor
**Problema que resolve:** lead que não respondeu a abertura hoje esfria e ninguém puxa.
**Entrega:** o **processador de cadência (F4)** — a fila `sdr_followups` JÁ é populada,
mas ninguém a consome. Construir o robô que puxa o lead em 4h → 24h → 48h → 7 dias, com
a própria Carol gerando o toque na hora (ela lembra a conversa). Para sozinho quando o
lead responde ou a call é marcada.
**Esforço:** 1-2 sessões (construir do zero, padrão já desenhado na arquitetura).
**Depende de:** Fase 1 no ar (a cadência começa na abertura).

### FASE 3 — Lembrete de Call com prova social (Fluxo C) 📸 ✅ CONSTRUÍDO 2026-07-15
**Problema que resolve:** lead marca call e sói (no-show). Falta o lembrete no dia.
**Entregue (DRAFT, não vai ao ar até o número definitivo):**
- `docs/crm/n8n-agente-sdr-lembrete-call-v1.json` — workflow 10 nós: cron **9h** →
  busca calls de hoje (parse robusto dos 3 formatos de `data_call`) → sendText
  (lembrete, texto do Fluxo C real) → sendMedia (prova social) → registra + jitter.
- `sdr_midias` (banco): 2 provas em base64, **alternadas** a cada envio.
- Decisões do Vitor aplicadas: as 2 imagens alternando · 9h da manhã · texto aprovado.
- Lógica validada com casos sintéticos (ISO/BR, com/sem hora, alternância ok).
**Falta pra ligar:** importar no n8n + número definitivo conectado.

### FASE 4 — Carol INTEGRADA ao pipeline (visível e controlável) 🖥️ vira produto
**Problema que resolve:** hoje o trabalho da Carol é invisível no CRM e não dá pra um
humano assumir. Sem isso, quando escalar, vira bagunça.
**Entrega:**
1. ✅ **Fix BUG-A** (fundação) — FEITO 2026-07-14. RPC grava `{text,date,autor}`; front
   normaliza os 2 formatos. As mensagens da Carol voltam a aparecer no modal.
2. ✅ **Chat de atendimento (bolhas)** — FEITO 2026-07-14 (front, no master). O histórico
   do lead virou conversa estilo WhatsApp: lead à esquerda, Carol à direita (dourado),
   humano à direita (verde), nota interna ao centro. **Falta publicar em produção.**
3. **Responder pelo chat** — campo que envia mensagem real ao lead via Evolution (não só
   nota interna). Depende de EDGE FUNCTION (proxy seguro) + número definitivo.
4. **Conexão do WhatsApp DENTRO do CRM** — botão "Conectar WhatsApp" na aba Agente SDR
   que mostra o QR ali (sem abrir o painel Evolution). Depende da MESMA edge function
   (a chave do Evolution não pode ir pro front).
5. **Card se move sozinho** — Carol abre → move Novo→Contato; qualifica → move pra
   Qualificado e **notifica a Thalita**; escala → marca vermelho e pausa.
6. **Takeover humano** — botão "Pausar agente" por lead (a Thalita assume, a Carol cala).
7. **Visual** — badge no card (`🤖 toque 2/4 · próx. 14h`), filtro "Em cadência" na
   lista, cards no dashboard.
**Esforço:** 2-3 sessões (SQL + edge function + n8n + front). **Depende de:** Fases 1-2.
**Peça-chave:** a **edge function `evolution-proxy`** (guarda a chave do Evolution como
secret e repassa QR/envio pro CRM) destrava os itens 3 e 4 de uma vez.

### FASE 5 — Polish premium ✨ o que faz "pagar caro"
- Painel de métricas do agente (taxa de resposta por toque, conversão, escalações).
- Auto-pause quando um humano responde pelo celular do número da Carol.
- Splitter de bolhas mais fino (N balões, não só 2).
**Esforço:** 1-2 sessões. **Depende de:** Fases 1-4 vivas.

---

## Decisões que são SUAS (travam algumas fases)

| # | Decisão | Trava | Default recomendado |
|---|---|---|---|
| D-1 | **Número definitivo do WhatsApp** da Carol (hoje é teste) | ir 100% ao ar | — (seu, quando quiser) |
| D-2 | **Número da Thalita** pra escalação/notificação | Fase 2, 3, 4 | — (não invento número) |
| D-3 | **Lembrete de call**: usa qual imagem? (16k→63k / Naty / as duas?) | Fase 3 | as duas, alternando |
| D-4 | **Texto do lembrete** que acompanha a imagem | Fase 3 | eu monto no tom da Carol p/ você aprovar |
| D-5 | **Cadência esgotada** (7 dias sem resposta): card vai pra Perdido ou fica marcado "sem resposta"? | Fase 2 | fica marcado (lead frio ≠ perdido) |

## Ordem recomendada de execução

**1 → 2 → 3 → 4 → 5.** Fase 1 dá o maior salto (Carol vira caçadora) e não depende de
nada. Fase 2 fecha o ciclo de captura. Fase 3 (seu pedido do lembrete) pode furar a fila
e vir antes da 2 se você priorizar reduzir no-show agora — é independente.

Cada fase: construir em DRAFT → testar sem tocar no que já funciona → publicar só quando
redondo (protocolo que já usamos a noite toda).
