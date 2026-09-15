# Agente SDR + Lembrete de call — revisão de ponta a ponta

> Revisão pedida pelo Vitor em 2026-09-15 (loop noturno). Tudo abaixo foi **verificado
> no banco de produção e no código**, não deduzido de documentação anterior.
> Complementa `AGENTE-SDR-PIPELINE-ARCHITECTURE.md` (estado alvo, 2026-07-14) e
> `atendimento-inbox-PLANO.md`. Onde os dois divergem do que está rodando, vale este.

## 1. O que roda hoje, de fato (verificado 2026-09-15)

| Peça | Estado real | Evidência |
|---|---|---|
| Lead novo entra pelo formulário | ✅ produção | `respondi-webhook` insere em `leads` |
| Mensagem de abertura automática | ⚠️ existe, mas **nunca dispara** | `respondi-webhook` só manda se `agente_sdr.ativo = true`; hoje `ativo = false` |
| **Resposta automática da Carol** | ❌ **não existe em lugar nenhum** | nenhuma edge function chama IA para conversa; das 3.429 mensagens `type='ai'` no histórico, **3.415 têm `operator = 'Equipe (WhatsApp)'` e 14 são de `viktorsimoess`/`thalitacloseroliveira`** — ou seja, 100% escritas por humano |
| Sync da conversa do WhatsApp | ⚠️ só roda com o CRM aberto | `evolution-proxy action=sync_out`, chamado pelo front; última mensagem sincronizada é de **09/09**, seis dias atrás |
| Takeover pelo CRM | ✅ funciona | `evolution-proxy action=send` grava e faz `agente_pausado = true` |
| Takeover pelo celular | ❌ não existe | ninguém observa mensagem `fromMe` fora do CRM |
| Cadência de follow-up | ⚠️ fila existe, **ninguém consome** | `sdr_followups` populada; nenhum worker |
| Lembrete de call | ⚠️ construído, **nada armado** | `cron.job` vazio, Vault sem segredo, `lembretes_config.ativo = false` |

**Conclusão dura:** hoje o "agente" é um cadastro no banco com um prompt bem escrito. Ele não
responde ninguém. Quem responde os leads é a Thalita, na mão — inclusive escrevendo
literalmente *"Oi Lohany! Em 30 min já envio o link da nossa chamada"* (histórico, 09/09),
que é exatamente a mensagem que o lembrete automatiza.

## 2. Furos do processo, por ordem de dano

**F1 — Nada está armado.** O lembrete depende de 3 passos manuais que nunca foram dados
(Vault, jobs de cron, `ativo=true`). Enquanto isso, zero lembretes saem.

**F2 — O agente não tem gatilho de entrada.** Para a Carol responder, alguém precisa avisá-la
que chegou mensagem. Hoje o único caminho é o `sync_out`, que depende de um humano com o CRM
aberto — o oposto de automático. **Falta o webhook do Evolution (`messages.upsert`) apontando
para uma edge function.** Essa é a peça central que falta; sem ela nenhuma outra melhoria
importa.

**F3 — O handoff só cobre metade dos casos.** "Humano pegou → agente sai" funciona quando o
humano responde *pelo CRM*. Se a Thalita responder pelo WhatsApp do celular — que é como ela
trabalha hoje — nada pausa o agente, e a Carol escreveria por cima dela. É o risco nº 1 de
ligar o agente do jeito que está.

**F4 — Lembrete e humano podem duplicar.** O lembrete de 30 min não olha se alguém do time já
falou com aquele lead há pouco. Como a Thalita já manda essa mensagem na mão, o lead pode
receber duas vezes seguidas.

**F5 — Conversa e lembrete não se conversam.** Se o lead responder ao lembrete ("não vou
poder, dá pra remarcar?"), ninguém trata. Sem F2 resolvido, essa resposta fica parada até
alguém abrir o CRM.

## 3. Desenho enxuto (o que estas iterações constroem)

Um único ponto de entrada, quatro travas antes de qualquer mensagem sair:

```
Evolution (WhatsApp)
        │  webhook messages.upsert
        ▼
┌──────────────────────────────────────────────────────┐
│ edge function  sdr-webhook                           │
│ 1. grava a mensagem no histórico (wa_id = dedupe)    │
│ 2. se fromMe (humano respondeu pelo celular)         │
│        → agente_pausado = true  → FIM   [trava H]    │
│ 3. travas antes de responder:                        │
│      · agente_sdr.ativo                   [trava A]  │
│      · lead.agente_pausado = false        [trava B]  │
│      · lead.atendente is null             [trava C]  │
│      · dentro da janela de horário        [trava D]  │
│ 4. chama Claude com instrucoes + histórico do lead   │
│ 5. envia em balões, grava como 'ai', regista evento  │
└──────────────────────────────────────────────────────┘
```

Regras que não se negociam:
- **O humano sempre vence.** Qualquer sinal de humano na conversa pausa o agente para
  sempre naquele lead. Despausar é ato explícito no CRM.
- **O agente nasce desligado**, como o lembrete. Ligar é decisão do Vitor, com teste no
  próprio número antes.
- **Idempotência é do banco**, não do código: `wa_id` único no histórico, como o índice
  único do lembrete.
- **O lembrete cala a boca se o humano acabou de falar** (F4): se houve mensagem enviada
  pelo time para aquele telefone nos últimos N minutos, pula.

## 4. Divisão do trabalho

**Dá para fazer sem o Vitor** (feito ou em andamento no loop): revisão, correções de código,
a edge function `sdr-webhook` nascendo desligada, a trava anti-duplicação do lembrete, e este
documento.

**Só o Vitor pode fazer** (nada disso é contornável por aqui):
1. Rodar `setup-lembrete-call-v1-cron.sql` no SQL Editor com a service_role key (Vault + jobs).
2. Rodar o bloco de textos/30 min/coluna de imagem.
3. Mandar a imagem de prova social para o lembrete da manhã.
4. Apontar o webhook do Evolution para a nova function (precisa da API key do Evolution).
5. Ligar cada coisa (`lembretes_config.ativo`, `agente_sdr.ativo`) depois de testar no próprio número.

## 5. Pergunta aberta que a revisão não resolve sozinha

A arquitetura de julho (`AGENTE-SDR-PIPELINE-ARCHITECTURE.md`) coloca o cérebro da Carol em
workflows n8n que **nunca foram publicados** (drafts). A decisão registrada depois foi trazer o
SDR para dentro do CRM. Este plano segue o caminho do CRM (edge function), porque é o que já
tem infraestrutura viva aqui — mas se a intenção ainda era n8n, o trabalho muda de lugar.
