# ARCHITECTURE — WhisperFlow Próprio

> Autor: análise Fable 5 · 2026-07-06 · CPU-only confirmado na máquina-alvo (auditado)
> **Substitui** o rascunho `../whisperflow-proprio-ARCHITECTURE.md` (Sonnet). Mantém o acerto central dele (Python leve, motor local, sem Electron) e corrige o que faltava: daemon residente, medição de latência como decisão, instância única, restauração de clipboard.

## 0. Ambiente real auditado (2026-07-06)

Python 3.12.10 · openai-whisper + torch instalados (usados pelo `.bat` — NÃO serão usados aqui, ver AD-2) · **sem GPU NVIDIA (CPU-only)** · ffmpeg presente (irrelevante — alimentamos áudio cru).

## 1. A decisão que define o produto

**AD-1 — Daemon residente com modelo carregado 1 única vez.**
O `.bat` atual recarrega o Whisper a cada uso (5-15s só de inicialização). Ditado exige resposta imediata → processo em background que carrega o modelo no boot e fica ouvindo o hotkey. TUDO deriva disso: escolha de libs, empacote, autostart, instância única. É a diferença entre "script" e "ferramenta".

## 2. Decisões técnicas

**AD-2 — Motor: `faster-whisper` (CTranslate2, int8), NÃO o openai-whisper já instalado.**
4-5× mais rápido em CPU, ~50% menos RAM, sem depender de torch (pesado) no runtime. Recebe **numpy array direto** do microfone → elimina ffmpeg e arquivos temporários. `vad_filter=True` (corta silêncio nas bordas, melhora qualidade e velocidade). `initial_prompt` em PT-BR pra induzir pontuação: `"Transcrição em português brasileiro, com pontuação correta."`

**AD-3 — Modelo default decidido POR MEDIÇÃO, não por opinião.**
CPU-only muda tudo. A story S2 roda benchmark na máquina real: `base` int8 vs `small` int8, frase padrão de ~8s, mede latência e qualidade. Regra de decisão: **o maior modelo que fica ≤3s** (CS1) vira default; o outro fica no config. Expectativa (não promessa): `small` int8 deve caber; se não, `base`. Download do modelo: primeiro uso, via HuggingFace, cache em `%LOCALAPPDATA%\WhisperFlow\models`.

**AD-4 — Stack Python mono-processo:**

| Função | Lib | Por quê |
|---|---|---|
| Hotkey global (hold/release) | `keyboard` | hooks low-level Windows, detecta press E release, sem admin na conta padrão |
| Captura de microfone | `sounddevice` | PortAudio, entrega numpy 16kHz mono float32 (formato nativo do Whisper) |
| Transcrição | `faster-whisper` | AD-2 |
| Clipboard | `pyperclip` | simples e confiável |
| Simular Ctrl+V | `keyboard.send('ctrl+v')` | mesma lib do hotkey, menos dependências |
| Beeps | `winsound` (stdlib) | zero dependência |
| Tray (V1.1) | `pystray` + `Pillow` | pausar/sair/status |

Sem Electron, sem web, sem servidor. 1 processo, ~500MB RAM com modelo carregado.

**AD-5 — Fluxo de colagem com restauração de clipboard.**
`transcreveu → salva clipboard atual → seta texto → Ctrl+V → espera 150ms → restaura clipboard anterior`. O usuário não perde o que tinha copiado — detalhe que separa ferramenta profissional de script. Config `paste_mode: "clipboard" | "type"` (o modo `type` digita caractere a caractere via `keyboard.write()` — fallback pra apps que bloqueiam paste; mais lento, desligado por padrão).

**AD-6 — Instância única.** Lock via socket local (`localhost:52700` bind exclusivo). Segunda instância detecta a porta ocupada e sai silenciosamente. Sem isso, autostart + execução manual = daemon duplicado = texto colado 2×.

**AD-7 — Push-to-talk com proteções:**
- Tap acidental (<300ms segurando) → descarta, sem beep de erro.
- Gravação máxima 120s (config) → para sozinha com beep duplo (proteção contra tecla presa).
- Transcrição vazia/só silêncio → não cola nada, sem beep de erro (comportamento neutro).
- Hotkey default: `ctrl+windows` (raro em apps; configurável em `config.json`).

**AD-8 — Config e dados em `%LOCALAPPDATA%\WhisperFlow\`:**
`config.json` (hotkey, model, language, max_seconds, paste_mode, beeps on/off) · `models\` (cache HF) · `logs\whisperflow.log` (rotativo 1MB×3) · `history.jsonl` (últimas 50 transcrições, V2 — útil pra recuperar texto colado no lugar errado).

**AD-9 — Autostart e empacote em 2 estágios:**
- **V1 (rodar do fonte):** `pythonw.exe main.py` (sem janela de console) + atalho na pasta Startup do usuário (`shell:startup`). Simples, sem admin, fácil de desfazer.
- **V1.1 (exe):** PyInstaller `--onefile --noconsole` (~120-180MB, modelo NÃO embutido — baixa no 1º uso). Necessário só quando for pro kit ou pra outra máquina.

**AD-10 — Tratamento de erro nunca derruba o daemon.**
Handler global no loop: qualquer exceção → log + beep triplo + volta a escutar. Microfone ausente/ocupado no início da gravação → beep triplo imediato. Modelo falhou ao carregar no boot → log + beep triplo contínuo 3× e aí sim encerra (único caso fatal).

## 3. O que foi avaliado e descartado (pro executor não "melhorar" de volta)

- **AutoHotkey pro hotkey/paste** — excelente no Windows, mas criaria 2 runtimes (AHK+Python) e 2 pontos de falha. Python `keyboard` cobre.
- **whisper.cpp (server C++)** — mais rápido ainda, porém build/manutenção hostis pra iteração via agente de IA; faster-whisper entrega 90% do ganho com 10% do atrito.
- **openai-whisper já instalado** — lento (torch/CPU) e exige ffmpeg+arquivo; seria a escolha "conveniente" e errada.
- **Electron/Tauri** — nada aqui precisa de janela.
- **API de nuvem como default** — mata o argumento "R$0/uso, 100% local" do kit. Fica como flag opcional de config (Groq) pra quem preferir latência mínima pagando centavos.
- **Toggle em vez de hold** — risco de microfone esquecido aberto; hold é autolimitante. Toggle pode entrar em V2 como segundo atalho.

## 4. Estrutura de código (pro executor)

```
whisperflow/
├── main.py            # entry: lock de instância, carrega config+modelo, registra hotkey, loop
├── recorder.py        # sounddevice: start/stop, buffer numpy, cap 120s
├── transcriber.py     # faster-whisper residente: load 1x, transcribe(np_array) -> str
├── paster.py          # clipboard save/set/paste/restore + modo type
├── feedback.py        # beeps (início, fim, erro)
├── config.py          # load/create default config.json em %LOCALAPPDATA%
├── config.default.json
└── requirements.txt   # faster-whisper, sounddevice, keyboard, pyperclip, numpy
```

Módulos pequenos e testáveis isoladamente — cada um com um `if __name__ == "__main__"` de teste manual (gravar 3s e tocar de volta; transcrever um wav fixo; colar "teste" no Notepad). Sem framework de teste na V1 — são 6 arquivos.

## 5. Riscos técnicos e mitigação

| Risco | Prob. | Mitigação |
|---|---|---|
| Latência CPU > 3s no `small` | média | AD-3: benchmark decide; fallback `base`; última carta: flag API Groq |
| `keyboard` exigir admin em algum contexto (apps elevados) | baixa | documentar: ditado em janela elevada (ex: regedit) não funciona — aceitável |
| Antivírus implicar com exe PyInstaller (V1.1) | média | assinar depois se virar kit; V1 roda do fonte e não tem esse problema |
| Beep incomodar em call | baixa | `beeps: false` no config; futuro: som só no fone |
