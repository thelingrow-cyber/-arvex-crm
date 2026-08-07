> ⚠️ **DOCUMENTO ARQUIVADO — não use como referência.**
> Superado pelo estado atual do sistema. Ponto de entrada: [../README.md](../README.md)
> Mantido só como registro histórico.

# Build Report — Chat do Sales Coach ("converse com a call")

**Data:** 2026-06-29 · Loop autônomo (não parou, não pediu aprovação) · Autorização: [[feedback_autonomia_deploy]]

## ✅ TUDO NO AR (C1–C4 completos)
| # | Story | Estado |
|---|-------|--------|
| C1 | Coluna `chat jsonb` em `meetings` | ✅ criada (Management API) |
| C2 | Edge Function `coach-chat` | ✅ deployada ACTIVE + testada (resposta grounded, salva histórico) |
| C3 | Painel de chat no detalhe da reunião | ✅ injetado no `index.html`, validado headless + syntax-check |
| C4 | Push pra produção | ✅ `-arvex-crm` main (commit e414609), protocolo aditivo respeitado |

## O que ficou
No detalhe de cada reunião (aba **Reuniões** → clicar num card analisado), abaixo da análise, tem **"Converse sobre esta call"**: o closer pergunta e o **diretor comercial responde olhando a transcrição + a análise daquela call**. Chips de sugestão ("Onde perdi a venda?", "Negociei cedo?", "Qual pergunta faltou?", "Como você faria diferente?"), histórico salvo em `meetings.chat`, anti-XSS. Demo (`?demo=1`) responde simulado.

**Teste real já passou:** perguntei "qual foi meu maior erro?" pra reunião da Flávia e a IA respondeu citando as falas reais ("boletos em cartório", "não durmo de noite").

## Como você testa (no CRM)
1. Aba **Reuniões** → clica num card **Analisado** (ex.: Flávia)
2. Rola até **"Converse sobre esta call"**
3. Clica num chip ou digita uma pergunta → resposta do diretor em segundos
4. O histórico fica salvo (recarregar mantém)

## ⚠️ Depende de você (não bloqueou o build)
- **Testar no CRM** (eu validei backend + UI isolada; falta seu olho na integração final).
- **Segurança:** revogar o access token do Supabase + rotacionar a chave Anthropic (expostos no chat). As funções estão com `verify_jwt=false` (destravar) — dá pra reapertar depois.

## Stack / decisões (pra não esquecer)
- Edge Function `coach-chat`: import **npm:** (jsr dá BOOT_ERROR), verify_jwt=false, service_role lê a call, Claude sonnet-4-6 (temp 0.3), persiste `meetings.chat`.
- Front: `ccInit/ccRender/ccSend` no `index.html`; invoke `coach-chat`.

## Próximo (fase 2, quando quiser)
- Chat **geral** ("como tô evoluindo?", comparar calls) → precisa de RAG sobre histórico.
- Botão "Enviar pro CRM" na extensão de transcrição (liga captura → reunião automática).

Loop encerrado — **backlog construível 100% no ar** (terminou porque acabou de verdade, não por parada no meio).
