# WhisperFlow Próprio — Arquitetura

> Autor: @architect (Aria) · 2026-07-06 · análise com Fable 5 (janela)
> Executor previsto: @dev (Sonnet/Opus) — este documento é autossuficiente
> Objetivo do Vitor: ferramenta pessoal de ditado — falar → transcrever → colar em qualquer app, desktop + celular, **sem pagar terceiros** (referência de mercado: Wispr Flow/Willow, ~$12-15/mês).

---

## 1. O que já existe (reusar, não recriar)

- **`transcrever-instagram.bat`** (Desktop do Vitor): yt-dlp + **Whisper local** (modelo `small`, português) — prova que Whisper roda offline na máquina dele, de graça, com qualidade aceitável em PT-BR. Motor de transcrição já resolvido.
- **Plugin Meet Transcriber** (`docs/plugin-meet-transcriber/`): extensão Chrome funcional que já captura texto ao vivo e envia pro CRM — arquitetura de captura+painel já validada em produção, mesmo que o alvo (legenda do Meet) seja diferente daqui (aqui é microfone livre, qualquer app).

## 2. O problema real (por que não é trivial)

WhisperFlow-like = 3 capacidades que **nenhuma já tem pronta**, e que são justamente as decisões difíceis:
1. **Hotkey global** (funciona com qualquer app em foco, não só browser) — Chrome extension NÃO alcança isso; precisa de app nativo/daemon no OS.
2. **Captura de áudio do microfone sob demanda** (não é ler legenda como no Meet plugin — é gravar áudio real).
3. **"Colar" o texto no app ativo** — simular digitação/paste no app que está em foco no momento (Word, WhatsApp Web, Notion, o que for).

Por isso isto é diferente do Meet plugin (que vive dentro do browser) — precisa rodar como programa no sistema operacional.

## 3. Decisões arquiteturais

### AD-1 — Stack: Python + `pynput`/`keyboard` (não Electron)
Electron dá UI bonita mas é pesado (~150MB+) pra uma ferramenta que só precisa de: hotkey listener + gravação + transcrição + paste. Python com `keyboard` (hotkey global) + `sounddevice`/`pyaudio` (gravação) + `pyautogui`/`pyperclip` (paste) resolve em <20MB, roda em background, empacota com PyInstaller em 1 `.exe`. Reserva UI gráfica só se ele quiser um indicador visual (ícone na bandeja) — não é essencial pro MVP.

### AD-2 — Motor de transcrição: local Whisper primeiro, API como upgrade opcional
- **V1 (grátis, já provado):** `faster-whisper` (biblioteca, 4x mais rápido que o Whisper original, CPU-friendly) modelo `small` ou `base`, português. Zero custo por uso, zero dependência de internet.
- **V2 (opcional, se latência incomodar):** trocar por API (OpenAI Whisper API ou Groq Whisper — Groq é extremamente rápido e barato) via flag de config. Não é a via padrão — só se o Vitor sentir que o modelo local demora demais pra frases longas.
- **Por que local primeiro:** é literalmente a tese dele ("Whisper é grátis, empresas cobram R$100-300/mês em cima disso") — WhisperFlow/Willow cobram por transcrição em nuvem; ele já tem o motor de graça rodando na própria máquina.

### AD-3 — Fluxo de uso (desktop)
`Segura hotkey (ex: Ctrl+Win) → grava enquanto segura → solta → transcreve local (~1-3s pra frases curtas) → texto vai pro clipboard → cola automático no app em foco (pyautogui.hotkey('ctrl','v'))`. Sem soltar em app errado por engano: feedback sonoro curto (beep) ao começar/parar gravação, já que não há tela.

### AD-4 — Mobile: NÃO nativo, usa o que já existe
Recriar isto como app mobile (hotkey global + acessibilidade + paste em qualquer app) é ordem de magnitude mais complexo no Android/iOS (permissões de acessibilidade, revisão de loja, manutenção dupla) — **não vale o esforço pro ganho**. Alternativa pragmática: no celular, usar o teclado de ditado nativo do Android/iOS (ambos já usam reconhecimento de voz decente) OU, se ele quiser algo próprio, um atalho simples: gravar áudio → mandar pro Telegram/WhatsApp de um bot próprio → bot transcreve (mesmo motor Whisper, rodando de um servidor pequeno) → devolve o texto pra copiar. Fase 2, não MVP.

### AD-5 — Distribuição: uso pessoal primeiro, "kit" depois
V1 roda só na máquina do Vitor (script Python + `.exe` compilado). Se funcionar bem e ele quiser oferecer como parte do kit de implementação pra clientes: empacotar como instalador simples (Inno Setup) com config de hotkey na primeira execução. Não overengenheirar isso agora — provar valor pessoal primeiro.

## 4. Riscos

1. **Falso-positivo de hotkey** (atalho conflita com outro programa) — mitigar com combinação incomum (ex: `Ctrl+Shift+Space`) configurável.
2. **Ruído de fundo prejudica transcrição** — modelo `small`/`base` já é razoavelmente robusto; se virar problema, trocar pra `medium` (mais lento, mais preciso) via config.
3. **Paste em campo errado** (usuário mudou de janela durante a gravação) — aceitável no V1; feedback sonoro reduz o risco.

## 5. Fases de implementação

| Fase | O quê | Esforço |
|------|-------|---------|
| **V1** | Script Python: hotkey + grava + faster-whisper local + clipboard + auto-paste + beep de feedback | 1 sessão @dev |
| **V1.1** | Empacotar `.exe` (PyInstaller) + rodar no boot do Windows (registro/atalho na pasta Startup) | curto |
| **V2** | Config pra trocar motor (local↔API), ícone na bandeja, histórico das últimas transcrições | 1 sessão |
| **V3 (kit)** | Instalador (Inno Setup) + tela simples de config de hotkey | quando for oferecer a clientes |

## 6. O que NÃO fazer

- ❌ Electron/app pesado — desnecessário pro escopo.
- ❌ App mobile nativo — custo/benefício ruim; usar ditado nativo do celular.
- ❌ Depender de API paga por padrão — motor local já resolve de graça.
- ❌ Nuvem/sincronização entre dispositivos no V1 — feature de depois, se fizer sentido.
