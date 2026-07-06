# IMPLEMENTATION-PLAN — WhisperFlow Próprio

> Autor: análise Fable 5 · 2026-07-06 · executor: @dev com Sonnet/Opus
> Regras pro executor: seguir `ARCHITECTURE.md` sem redecidir nada (seção 3 lista o que já foi descartado — não reintroduzir). 1 story por vez, em ordem. Cada story termina com o critério de pronto VERIFICADO de fato (rodar, observar, mostrar evidência) — nunca declarar pronto sem executar.
> Código em: `tools/whisperflow/` no repo ARVEX (novo). Commits: `feat(whisperflow): S{n} — {resumo}`.

---

## S0 — Esqueleto e fundações (½ sessão)

**Fazer:** estrutura de pastas da seção 4 da ARCHITECTURE · `requirements.txt` + venv local (`tools/whisperflow/.venv`, gitignored) · `config.py` que cria `%LOCALAPPDATA%\WhisperFlow\config.json` default na 1ª execução · logging rotativo (1MB×3) · lock de instância única via socket 52700 (AD-6).

**Pronto quando:**
- [ ] `python main.py` sobe, loga "daemon iniciado", e uma 2ª execução simultânea sai em silêncio com log "instância já ativa".
- [ ] `config.json` criado no local certo com defaults (hotkey `ctrl+windows`, model `small`, language `pt`, max_seconds 120, paste_mode `clipboard`, beeps true).

## S1 — Gravação push-to-talk (½ sessão)

**Fazer:** `recorder.py` (sounddevice, 16kHz mono float32) + registro do hotkey em `main.py`: segurar → beep curto + grava; soltar → beep curto + entrega buffer. Proteções AD-7: tap <300ms descarta; cap 120s com beep duplo. Flag `debug_save_wav: true` salva o áudio em `%LOCALAPPDATA%\WhisperFlow\debug\` pra inspeção.

**Pronto quando:**
- [ ] Segurar/falar/soltar gera WAV audível no debug com a fala completa (ouvir o arquivo, não presumir).
- [ ] Tap rápido não gera nada; 120s+ para sozinho.
- [ ] Mic ocupado/ausente → beep triplo, daemon segue vivo.

## S2 — Transcrição residente + BENCHMARK DECISÓRIO (1 sessão) ⭐

**Fazer:** `transcriber.py`: carrega faster-whisper 1× no boot (int8, `vad_filter=True`, `initial_prompt` PT-BR conforme AD-2) e expõe `transcribe(np_array) -> str`. Conectar: soltar tecla → transcrever → log do texto + latência medida.

**Benchmark (obrigatório, decide o default — AD-3):** gravar 1 frase padrão de ~8s (ex: *"Bom dia, tudo bem? Quero confirmar nossa reunião de amanhã às quinze horas, e aproveitar pra te mandar a proposta atualizada com os dois planos que a gente conversou."*). Rodar 3× em `base` int8 e 3× em `small` int8. Tabela: modelo · latência média · texto produzido. **Regra: maior modelo com média ≤3s vira default no config.** Registrar a tabela no commit e em `BENCH.md`.

**Pronto quando:**
- [ ] Falar → texto correto no log com pontuação, latência impressa.
- [ ] `BENCH.md` com a tabela e a decisão aplicada ao `config.default.json`.
- [ ] 2ª transcrição seguida NÃO recarrega o modelo (latência de load só no boot — verificar no log).

## S3 — Colagem no cursor (½ sessão)

**Fazer:** `paster.py` conforme AD-5: salvar clipboard → setar texto → `ctrl+v` → 150ms → restaurar clipboard. Implementar também `paste_mode: "type"` (keyboard.write) como fallback configurável. Transcrição vazia → não cola (AD-7).

**Pronto quando (testar nos 4, de verdade):**
- [ ] Bloco de Notas · WhatsApp Web (Chrome) · Notion · campo de texto do navegador comum — texto aparece no cursor.
- [ ] Conteúdo copiado ANTES do ditado continua no clipboard DEPOIS (copiar "abc", ditar, Ctrl+V manual → "abc").

## S4 — Robustez de daemon (½ sessão)

**Fazer:** handler global (AD-10): exceção em qualquer etapa → log stacktrace + beep triplo + volta a escutar. Testar induzindo falhas (desconectar mic no meio, corromper config, modelo ausente na 1ª execução → baixa sozinho com log de progresso).

**Pronto quando:**
- [ ] Nenhum cenário de falha derruba o processo (exceto falha de load do modelo no boot, o único fatal por design).
- [ ] Log conta a história de cada falha de forma legível.

## S5 — Autostart + modo invisível (½ sessão)

**Fazer:** rodar via `pythonw.exe` (sem console) · atalho na pasta Startup (`shell:startup`) apontando pro pythonw+main.py · verificar que beeps/hotkey funcionam sem console. Guia de 5 linhas no README (como pausar: matar processo; como desinstalar: apagar atalho+pasta).

**Pronto quando:**
- [ ] **Reiniciar o Windows de verdade** → sem abrir nada, segurar hotkey e ditar no Bloco de Notas funciona.
- [ ] Nenhuma janela visível em momento algum.

## S6 — Daily driver test (1 dia de uso real — critério final do PRD)

Vitor usa o dia inteiro pra WhatsApp Web. Coletar: travou? latência incomodou? erros de transcrição relevantes? → ajustes pontuais OU aprovação. **Só depois disso** considerar V1 concluída.

---

## V1.1 (depois do S6 aprovado) — backlog imediato
- Tray icon (pystray): status/pausar/sair.
- PyInstaller `--onefile --noconsole` (necessário só pra levar a outra máquina).
- `history.jsonl` (últimas 50 transcrições).

## V2 — backlog
- Segundo atalho em modo toggle (ditados longos).
- Polimento opcional por LLM (flag, API, desligado por padrão).
- Motor alternativo API Groq (flag) se latência local incomodar.

## V3 — kit (decisão de negócio do Vitor)
- Inno Setup + primeira execução com escolha de atalho + README de 1 página + (se for vender) assinatura de código.

---

## Mapa de dependências

`S0 → S1 → S2 → S3 → S4 → S5 → S6` (estritamente serial; S2 é o único com decisão embutida, e ela é por medição, não por julgamento).

## Estimativa total V1

3-4 sessões de @dev (Sonnet). Nenhuma etapa exige Fable — todas as decisões arquiteturais já estão tomadas neste dossiê.
