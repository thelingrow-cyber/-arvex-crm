# WhisperFlow — Refatoração "nível mercado" (2026-07-19) — ADR-14 a 17, S7-S10

> Continua a numeração do `IMPLEMENTATION-PLAN.md` (S0-S6, V1 concluído e ATIVADO em produção
> real desde 2026-07-17). Este documento NÃO redecide nada do V1. Revisado por Fable em
> 2026-07-19 (v2 — corrige um bug de design da fila de refino, fecha as decisões que estavam
> em aberto e adiciona os gotchas de implementação). Decisões já tomadas com o Vitor:
> motor de polish = Groq/Llama (grátis); refino assíncrono só grava no histórico, nunca recola.
>
> **Executor:** @dev (Sonnet/Opus), fases em série, 1 commit por fase
> (`feat(whisperflow): S{n} — {resumo}`). Todas as decisões estão tomadas aqui — não redecidir.

## Diagnóstico (código lido linha a linha, 1591 linhas / 10 módulos)

1. **O "tratamento de prompt automático" pedido já existe.** `polish.py` limpa vício de fala e
   já distingue instrução-pra-IA (organiza como prompt) de mensagem comum — mas está
   `polish_enabled: false` por padrão e nunca foi validado em uso real.
2. **Qualidade de transcrição nunca foi validada com a voz real do Vitor.** `base` foi escolhido
   só por orçamento de latência síncrona (≤3s, `BENCH.md`), com áudio SAPI sintético.
3. **Zero interface.** Histórico é um `.jsonl` de 50 linhas sem UI — não dá pra buscar nem revisar.
4. **Dívida conhecida:** `install_autostart.py` corrompe o path com acento (cscript lê `.vbs`
   como ANSI) — o autostart em produção hoje é um atalho criado manualmente; rodar o script de
   novo falha igual.

## ADR-14 — Refino assíncrono de dois estágios

**Decisão:** ao soltar a tecla, o fluxo atual continua idêntico (`base` transcreve, cola).
Em paralelo, um **worker serial** reprocessa o mesmo buffer de áudio com o modelo **`small`**
(decisão fechada — não testar `medium`: no bench desta máquina `small` já roda a 0.55x
tempo-real; `medium` seria >1.5x tempo-real E ~1.5GB extras de RAM residente; ganho marginal
não paga) e grava o resultado no histórico. Nunca recola, nunca notifica.

**Correção sobre a v1 deste plano (bug de design):** a fila NÃO é "profundidade 1, descarta o
anterior". Cada refino pertence a um ditado DIFERENTE — descartar o refino do ditado N porque
o N+1 chegou deixaria N sem versão refinada pra sempre, sem nenhum ganho em troca. Design
correto:

- Worker **serial** (1 refino por vez, nunca 2 simultâneos) consumindo `queue.Queue(maxsize=5)`.
- Cada job = `(entry_id, audio_np)`. O resultado faz `UPDATE entries SET refined_text=? WHERE id=?`.
- Fila cheia (6º ditado com 5 pendentes — cenário raro de rajada): descarta o job MAIS ANTIGO
  da fila (get_nowait + put) e loga. Job em execução nunca é cancelado (faster-whisper não
  suporta cancelamento; deixar terminar e gravar).
- Áudio em RAM por job: ≤120s @16kHz float32 ≈ 7.7MB — 5 jobs ≈ 38MB, aceitável.

**Contenção de CPU (obrigatório):** o modelo de refino é criado com
`cpu_threads = max(2, os.cpu_count() // 2)` — o `base` síncrono do próximo ditado sempre tem
folga de CPU. O refiner é **lazy**: carrega no primeiro refino (não no boot — boot continua
2-6s), fica residente depois (~400-500MB RAM extra; se algum dia incomodar, unload-por-idle é
a extensão natural, não construir agora).

**Interação com polish:** quando `polish_enabled`, o worker também passa o texto refinado pelo
`polish()` (contexto assíncrono — latência irrelevante; 1 chamada Groq extra por ditado, dentro
do free tier pra uso pessoal). O que vai pro histórico como `refined_text` é a MELHOR versão
disponível: `polish(refino)` se o polish rodou, senão o refino cru. Falha de polish no refino →
grava o refino cru (mesmo espírito AD-10: nunca perder o dado por causa do passo opcional).

## ADR-15 — Polish ligado por padrão, SÍNCRONO (decisão fechada)

A v1 deste plano deixou em aberto "o polish síncrono soma a latência do Groq ao paste — decidir
depois". **Decidido agora: fica síncrono.** Razão: o texto MELHORADO ser o que cola é
exatamente o produto que o Vitor pediu ("quando eu falo ele processa e já faz uma melhoria") —
polish assíncrono colaria o texto cru e derrotaria o propósito. O custo real é baixo: Groq LPU
responde ~0.5-1s pra textos de ditado; total esperado ≈ 1.4s (base) + ~1s ≈ 2.4s, dentro do
teto de 3s.

Mudanças concretas:
- `polish_enabled: true` no `config.default.json` e no `DEFAULT_CONFIG` de `config.py`.
- `TIMEOUT_SECONDS` em `polish.py`: 5.0 → **3.5** (pior caso raro: 1.4 + 3.5 ≈ 5s e cai pro
  texto cru — comportamento de fallback já existe, só encurta o teto).
- Logar a latência do polish separada da latência do Whisper em toda transcrição (já existe
  parcialmente — garantir que dá pra auditar o orçamento no S10 com o log).

## ADR-16 — Histórico: `.jsonl`(50) → SQLite

**Decisão:** `%LOCALAPPDATA%\WhisperFlow\history.db`, stdlib `sqlite3`, sem cap. Schema
(3 versões de texto no máximo — não 4; "refined" já embute polish quando houver, ver ADR-14):

```sql
CREATE TABLE IF NOT EXISTS entries (
  id INTEGER PRIMARY KEY,
  created_at TEXT NOT NULL,        -- ISO 8601 UTC
  raw_text TEXT,                   -- saída crua do Whisper base (NULL nas entradas migradas do .jsonl)
  pasted_text TEXT NOT NULL,       -- o que foi efetivamente colado (polished ou raw)
  was_polished INTEGER NOT NULL,   -- 0/1: pasted_text passou pelo polish?
  refined_text TEXT,               -- melhor versão assíncrona (small [+polish]), chega depois
  duration_ms INTEGER,             -- duração do áudio ditado
  tags TEXT                        -- CSV simples; volume de 1 pessoa não justifica junção
);
```

**Disciplina de acesso (obrigatório — daemon e UI leem/escrevem o mesmo arquivo):**
`PRAGMA journal_mode=WAL` na criação; toda operação abre conexão própria de vida curta
(abre → executa → fecha), nunca conexão compartilhada entre threads. Com WAL isso é seguro e
elimina a classe inteira de erro `check_same_thread`/lock.

**Migração:** `migrate_history.py` (script avulso, roda 1x, não vive no daemon): cada linha do
`.jsonl` vira `pasted_text` + `was_polished` + `created_at`; `raw_text`/`refined_text` NULL.

## ADR-17 — Interface web local + tray icon

**Decisão:** FastAPI + uvicorn (dependências novas, pinadas no `requirements.txt`) em
`127.0.0.1:52701`, rodando numa thread do próprio daemon. Front: HTML/CSS/JS vanilla servido
de `tools/whisperflow/static/` — dark, radius 14/8, system-ui, destaque violeta `#8b7dff`
(herdado do overlay — identidade própria da ferramenta, não o azul do Meet Transcriber).
Zero build step, zero framework.

**Gotchas de implementação (vão morder se não estiverem escritos):**
- uvicorn em thread secundária: usar `uvicorn.Server(config)` com
  `config = uvicorn.Config(app, host="127.0.0.1", port=52701)` e **desativar signal handlers**
  (`server.install_signal_handlers = lambda: None` ou equivalente da versão) — signal handler
  só funciona na main thread; sem isso o boot da UI derruba o daemon.
- `pystray`: rodar via `icon.run_detached()` (ou thread própria) — `run()` bloqueia. Convive
  com o mainloop Tk do overlay porque cada um tem sua thread; não compartilhar objetos Tk.
- Tray com DOIS itens: "Abrir histórico" (`webbrowser.open`) e "Encerrar WhisperFlow"
  (resolve a dívida "só dá pra parar pelo Gerenciador de Tarefas"): `keyboard.unhook_all()` →
  `lock.close()` → `os._exit(0)` (crude mas correto pra ferramenta pessoal; as threads são
  todas daemon).
- Ícone do tray: gerar um PNG simples do orb violeta via Pillow em runtime OU embutir um `.ico`
  estático em `static/` — decisão livre do executor, não gastar tempo nisso.

**Funcionalidades da UI (lista fechada):**
1. Lista cronológica (recente primeiro): `pasted_text` em destaque, `refined_text` ao lado
   quando existir (badge "refinada"), `raw_text` expansível.
2. Busca por texto (`LIKE` em pasted/refined/raw — sem FTS, volume não justifica).
3. Tags: adicionar/remover, filtrar.
4. Copiar qualquer versão com 1 clique.
5. Apagar entrada (sem edição de texto — histórico é registro, não editor).
6. **Editar `custom_vocabulary`** (lê/grava o config.json; UI avisa "aplica no próximo boot" —
   o initial_prompt é montado no load do modelo). Alinhado com "que entenda bem o que falo":
   é o mecanismo existente de ensinar nomes/jargão ao Whisper, hoje só editável na mão.

**Vetado:** login/conta, sync, export além de copiar, edição de texto, paginação server-side.

## Plano de execução

> Ordem alterada vs v1: UI (agora S8) vem ANTES da validação do polish (agora S9) — validar
> qualidade de polish lendo `.db` na mão é atrito desnecessário quando a UI que resolve isso
> está a uma fase de distância. Ferramenta de validação antes da validação.

### S7 — SQLite + refino assíncrono + fix do autostart (ADR-14 + ADR-16)
**Fazer:** migrar `history.py` pra SQLite (WAL, conexões curtas) · `migrate_history.py` ·
worker serial de refino (fila maxsize=5, descarte do mais antigo, lazy-load do `small` com
`cpu_threads=os.cpu_count()//2`, polish do refino quando habilitado) · plugar em `main.py`
(gravar entry no paste, enfileirar job com o áudio) · **reescrever a criação do atalho em
`install_autostart.py` via PowerShell COM (`WScript.Shell.CreateShortcut`), eliminando o `.vbs`
intermediário** — é a correção da causa raiz já diagnosticada (cscript lê `.vbs` como ANSI e
corrompe "Simões"); o workaround manual de 2026-07-17 usou exatamente esse caminho e funcionou.
**Pronto quando:**
- [ ] Ditado normal continua colando com a mesma latência percebida (comparar log antes/depois).
- [ ] `refined_text` da entrada certa aparece no `.db` segundos depois, com o daemon livre.
- [ ] 3 ditados em rajada → 3 entradas, cada uma com SEU refino (nenhum descartado indevidamente).
- [ ] `.jsonl` migrado sem perda; arquivo antigo renomeado `.jsonl.bak`.
- [ ] `python install_autostart.py` num path com acento cria atalho válido (testar de verdade).

### S8 — Interface web + tray (ADR-17)
**Fazer:** FastAPI (rotas: listar/buscar/tags/apagar/vocabulário) · front vanilla ·
uvicorn em thread (signal handlers OFF) · pystray com Abrir/Encerrar.
**Pronto quando:**
- [ ] `http://127.0.0.1:52701` lista o histórico real; busca e tags funcionam.
- [ ] Ditar COM a UI aberta → entrada aparece (refresh manual basta; live update não é requisito).
- [ ] Editar vocabulário pela UI altera o config.json e o aviso de "próximo boot" aparece.
- [ ] "Encerrar" no tray mata o daemon limpo (porta 52700 liberada — verificar com netstat).

### S9 — Polish por padrão + validação com dado real (ADR-15)
**Fazer:** defaults `polish_enabled: true` · timeout 3.5s · logging de latência separado ·
alguns dias de uso real revisando pela UI do S8.
**Pronto quando:**
- [ ] 15+ ditados reais revisados na UI; heurística prompt-vs-mensagem sem erro grosseiro
      (reescrever demais uma mensagem comum = erro grosseiro).
- [ ] p50 da latência total (whisper+polish) ≤3s no log; fallback pro cru observado ao menos
      1x sem quebrar nada (dá pra forçar desligando a rede).

### S10 — Dia de uso real com tudo ligado (gate final)
Mesmo critério do S6 original: um dia inteiro ditando com refino+polish+UI ativos. Qualquer
incômodo (latência, CPU, qualidade do polish) volta pra fase respectiva COM o dado do log —
não ajustar por sensação.

## O que NÃO fazer

- ❌ Trocar o motor de polish pra Claude — decisão do Vitor foi Groq (rever só se a qualidade
  reprovar no S9 com exemplos concretos em mãos).
- ❌ Recolar/substituir texto automaticamente com a versão refinada — decisão do Vitor.
- ❌ `medium`/`large` no refino — RAM e tempo-real não pagam nesta máquina (decidido aqui, v2).
- ❌ Framework de front, build step, login/sync, FTS, live-update por WebSocket na UI.
- ❌ Cancelamento de refino em andamento — faster-whisper não suporta; deixar terminar.
- ❌ Segundo processo/serviço pra UI — é thread do daemon; um processo só, um lock só.
