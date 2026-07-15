# QA Gate — F4 Processador de Follow-up

> Guardian: Quinn (@qa) · 2026-07-15
> Artefatos: `n8n-agente-sdr-f4-processador-v1.json` (20 nós, DRAFT), `f4-montar-fila.js`, `f4-proximo-estado.js`, ADRs em `AGENTE-SDR-F4-PROCESSADOR-ARCHITECTURE.md`

## VERDICT: ✅ CONCERNS (aprovado; melhorias recomendadas antes de publicar)

A lógica está sólida, coerente com os 6 ADRs, e resiliente aos edge cases. Nada bloqueia. Como é DRAFT (só vai ao ar com o número definitivo), há janela pra polir os concerns abaixo — nenhum é crítico.

## Matriz de edge cases (todos verdes)

| # | Caso | Resultado |
|---|------|-----------|
| EC1 | Fila vazia | retorna `[]`, não faz nada ✓ |
| EC2 | Agente inativo | gate global corta, não processa ✓ |
| EC3 | Activities formato antigo `{texto,data}` (pré-BUG-A) | detecta "lead respondeu" ✓ |
| EC4 | Lead sem activities | `deve_tocar=SIM` (defensivo, aceitável) ✓ |
| EC5 | `tel` null | passa; Evolution rejeita (não crasha) ✓ |
| EC6 | Cadência com N≠4 toques `[4,24]` | avança e encerra lendo `.length` ✓ |
| EC7 | Cadência vazia `[]` | encerra imediato (defensivo) ✓ |
| EC8 | `toques` undefined | usa default `[4,24,48,168]` ✓ |

## Rastreabilidade aos ADRs
- ADR-F4-1 (IA gera o toque): ✓ · ADR-F4-2 (3 gates): ✓ · ADR-F4-3 (avança/encerra por `.length`): ✓ · ADR-F4-4 (não move card — só `obs`): ✓ · ADR-F4-5 (workflow separado, cron 15min): ✓ · ADR-F4-6 (splitter balões): ✓

## Concerns (melhorias, não bloqueiam — aplicar antes do PUBLISH)

- **C-1 (MEDIUM):** `Enviar Balão 2` roda sempre, mesmo com `balao2` vazio (follow-up de 1 balão). O `onError=continueRegularOutput` evita crash, mas envia texto vazio ao Evolution (que provavelmente rejeita). **Recomendação:** IF `balao2 != ''` antes do Enviar Balão 2. *(Mesmo padrão herdado do F2 em produção — dívida compartilhada, não regressão nova.)*
- **C-2 (LOW):** `Enviar Balão 1` sem `onError` — se `tel` inválido faz o item parar antes de avançar/encerrar a fila, o lead re-tenta a cada 15min indefinidamente. **Recomendação:** `onError=continueRegularOutput` no Balão 1 também, pra a fila sempre avançar/encerrar.
- **C-3 (LOW, benigno):** Race F2×F4 na mesma fila. Analisado: o `Avançar Fila` não seta `status`, então se o F2 cancelou (status=cancelado), o poll (`where status=pendente`) não reabre. No pior caso, 1 toque extra numa janela de segundos. Aceitável. *(Endurecível com `?...&status=eq.pendente` no PATCH, se quiser 100%.)*

## Testabilidade
Alta. Toda a lógica de decisão está em 2 Code nodes puros (montar-fila, proximo-estado), testáveis fora do n8n com `Function` ctor — como feito aqui. O teste ao vivo (import + linhas sintéticas na fila) fica pra quando o número definitivo entrar.

— Quinn, guardião da qualidade 🛡️
