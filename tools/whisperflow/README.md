# WhisperFlow

Ditado por voz global no Windows: segure `Ctrl+Win`, fale, solte — o texto
transcrito (PT-BR, local, sem internet) aparece colado no cursor. Ver
`docs/ferramentas-proprias/whisperflow-proprio/` (PRD, ARCHITECTURE,
IMPLEMENTATION-PLAN) para o desenho completo do produto.

## Instalar (autostart com o Windows)

```
tools/whisperflow/.venv/Scripts/python.exe tools/whisperflow/install_autostart.py
```

Isso cria um atalho em `shell:startup` que roda `pythonw.exe main.py` (sem
janela de console) toda vez que o Windows liga. Rodar de novo é seguro
(sobrescreve o atalho existente).

## Rodar manualmente (sem instalar autostart)

```
tools/whisperflow/.venv/Scripts/pythonw.exe tools/whisperflow/main.py
```

## Pausar / parar

Matar o processo (`pythonw.exe` rodando `main.py`) pelo Gerenciador de
Tarefas, ou `taskkill /IM pythonw.exe /F` (cuidado: mata TODOS os
`pythonw.exe`, não só o WhisperFlow, se houver outros rodando).

## Desinstalar (remover autostart)

```
tools/whisperflow/.venv/Scripts/python.exe tools/whisperflow/install_autostart.py --uninstall
```

Ou manualmente: apagar `WhisperFlow.lnk` da pasta Startup (`Win+R` →
`shell:startup`) e apagar a pasta `%LOCALAPPDATA%\WhisperFlow\` (config,
modelo em cache, logs).

## Config

`%LOCALAPPDATA%\WhisperFlow\config.json` — hotkey, modelo (`base`/`small`),
idioma, `paste_mode` (`clipboard` default / `type` fallback), beeps.
Editar e reiniciar o processo para aplicar.
