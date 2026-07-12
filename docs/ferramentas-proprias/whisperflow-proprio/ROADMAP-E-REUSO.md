# ROADMAP — Melhorias Futuras + Reaproveitamento no Ecossistema ARVEX

> Autor: Orion (aiox-master) · 2026-07-10 · gerado a partir da comparação com o Wispr Flow oficial (sessão do mesmo dia) + estado real do V1 (S0-S5 verificado com deploy/teste real, S6 — dia de uso real — pendente)
> Fonte de verdade do produto em si continua sendo `PRD.md`/`ARCHITECTURE.md`/`IMPLEMENTATION-PLAN.md` nesta pasta — este documento NÃO redecide nada de lá, só organiza o que vem depois do V1.

## 1. Roadmap de melhorias, priorizado

### V1.1 — baixo esforço, já estava no plano original (`IMPLEMENTATION-PLAN.md`)

| Item | Resolve | Esforço |
|---|---|---|
| Tray icon (`pystray`) | Hoje só dá pra parar matando processo no Gerenciador de Tarefas | ~meio dia |
| `history.jsonl` (últimas 50 transcrições) | Recuperar texto colado no lugar errado | ~1h |
| PyInstaller `--onefile` | Só necessário se for levar pra outra máquina/kit — não urgente pra uso pessoal | ~meio dia |

### V2 — esforço médio, evolução real de produto (novidade desta análise)

| Item | Gap que fecha (vs Wispr Flow oficial) | Esforço | Nota |
|---|---|---|---|
| **Polimento por LLM** (flag opcional, desligado por padrão) | Maior gap de qualidade percebida — hoje sai cru, com "é, tipo, então" | médio | usar API barata (Groq/Haiku), nunca como default — quebraria a tese de R$0 |
| **Vocabulário pessoal** (lista de termos no `config.json` injetada no `initial_prompt`) | Wispr aprende nomes/jargão; o nosso usa só um prompt estático em PT-BR | baixo-médio | não é ML de verdade, é lista manual — mas resolve 80% da dor |
| **Toggle mode** (2º atalho, ditado longo sem segurar) | Já cogitado e adiado no `ARCHITECTURE.md` (seção 3) | baixo | risco documentado: mic esquecido aberto — precisa de timeout visível |
| **Corrigir bug do modo `type`** (come 1ª palavra) | Robustez do fallback secundário | baixo | já documentado como conhecido, não bloqueante |

### V3 / não vale a pena agora

Multiplataforma mobile, sync em nuvem, comandos de edição por voz, tier enterprise — todos contrariam a tese central do projeto (R$0, 100% local, uso pessoal) ou são decisões já descartadas explicitamente no `ARCHITECTURE.md`. Não reabrir sem motivo novo.

## 2. Quanto disso reaproveita na sua estrutura (ARVEX)

Resposta honesta: **nem tudo é código compartilhável.** Três categorias diferentes:

**A) Já está no plano de outro projeto — reuso real, documentado antes de hoje.**
O Meet Transcriber (`docs/plugin-meet-transcriber/`) tem um "Plano B" registrado: se o Google matar as legendas do Meet, o fallback vira `tabCapture+Whisper` — e a própria memória do projeto já diz "motor é o do WhisperFlow". Ou seja, `transcriber.py` (faster-whisper residente, load 1x) já é o candidato natural pra esse fallback, sem reescrever nada. Não é hipótese — já estava escrito.

**B) Reaproveitável com adaptação — mesma peça, config diferente.**
O script `transcrever-instagram.bat` (Desktop) usa yt-dlp + Whisper e é a semente da ideia "SaaS Transcrição IG" (hoje sem data, "agregar como feature de SaaS maior"). Diferença chave: ele processa vídeo já gravado, então **não tem** a restrição de ≤3s que fez o WhisperFlow escolher o modelo `base` — pode usar `small`/`medium` (mais precisão, mais lento, tudo bem em lote). Reaproveitável direto: `transcriber.py` inteiro + o padrão de `config.py` (`%LOCALAPPDATA%`, load/create defaults). NÃO reaproveitável: `recorder.py` (push-to-talk ao vivo) nem `paster.py` (colar no cursor) — esse SaaS não precisa de nenhum dos dois.

**C) Padrão, não código — não dá pra importar, só copiar a ideia.**
"Polimento por LLM" (V2 acima) é *conceitualmente* a mesma operação que o Sales Coach já faz hoje no CRM (`ingest-meeting` → `analyze-meeting` via Anthropic): pegar transcrição crua e passar por um LLM pra virar algo limpo/estruturado. Mas são implementações diferentes por natureza — Sales Coach usa Anthropic (pago, já no orçamento do CRM), o WhisperFlow V2 precisa de algo mais barato pra não furar a tese de custo zero do ditado pessoal. Dá pra copiar o *padrão* (prompt de limpeza pós-transcrição), não o código.
O daemon residente + autostart (modelo carregado 1×, lock de instância única via socket) também é um padrão de infra que qualquer ferramenta desktop futura da ARVEX vai precisar reinventar — vale documentar como receita quando aparecer uma 2ª ferramenta desktop, não antes.

## 3. Veredito — o que fazer agora vs esperar

Regra anti-dispersão (1 build por vez, construção > consumo): **não extrair nada como lib compartilhada agora** — seria otimização prematura pra um único usuário e um único caso de uso ativo.

1. Terminar o **S6** do WhisperFlow (dia inteiro de uso real) antes de qualquer item deste roadmap.
2. Se/quando "SaaS Transcrição IG" virar prioridade de verdade (ainda não é — sem data), **copiar** `transcriber.py`+`config.py` como ponto de partida, não criar um pacote interno compartilhado agora (são 2 arquivos pequenos; duplicar é mais simples e mais barato que abstrair cedo).
3. O fallback `tabCapture+Whisper` do Meet Transcriber só entra em cena se o Google matar as legendas — não é urgente, já está documentado como Plano B, não precisa de ação hoje.
