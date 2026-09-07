# Contexto atual — Codex ↔ Claude

> Ponto de retomada compartilhado e versionado. Leia antes de agir e atualize
> ao concluir um bloco relevante, antes de compactar ou ao trocar de ferramenta.
> Não registrar segredos, tokens, dados pessoais ou transcript integral.

## Objetivo ativo

Aprimorar o WhisperFlow, ferramenta global de ditado em português para Windows,
mantendo baixa fricção, boa transcrição e feedback visual profissional.

## Estado atual

- Branch publicada para retomada no Cloud: `codex/whisperflow-handoff`.
- Código: `tools/whisperflow/`.
- Ativação local: um toque em `Ctrl+Win` inicia; novo toque encerra; após fala,
  1,5 segundo de silêncio também encerra automaticamente.
- Transcrição principal: Groq `whisper-large-v3-turbo`, com fallback local no
  modelo `base` quando rede ou API estiver indisponível.
- Polimento: Groq `openai/gpt-oss-120b`.
- Overlay: janela em camadas do Windows com alpha real por pixel; estados de
  escuta, processamento e conclusão; fallback para Tk se o caminho Win32 falhar.
- Configuração da máquina: `%LOCALAPPDATA%\WhisperFlow\config.json`.
- Daemon e configuração são locais ao Windows; o Cloud só recebe código e docs.

## Evidência de uso real

- Em 07/09/2026, um ditado de 13 segundos foi transcrito em aproximadamente
  1,08 segundo, corretamente, onde o motor local anterior errava frases curtas.
- O log fica em `%LOCALAPPDATA%\WhisperFlow\logs\whisperflow.log`.
- O histórico fica em `%LOCALAPPDATA%\WhisperFlow\history.db`.

## Decisões

1. Priorizar `large-v3-turbo` remoto nesta máquina: Ryzen 5 3500U, 5,9 GB de
   RAM e sem CUDA tornam modelos locais maiores lentos.
2. Manter fallback local carregado para o ditado continuar sem rede.
3. Não subir o refinador `small` quando o motor remoto estiver ativo: ele gasta
   memória e gera resultado inferior ao texto já colado.
4. Usar alpha real do Windows no overlay; transparência por cor-chave do Tk
   criava borda escura e rasgos transparentes.
5. Troca entre Codex e Claude usa este arquivo mais Git; chats não sincronizam
   entre fornecedores.

## Commits relevantes

- `6ff131a` — cria a ponte versionada de contexto Codex ↔ Claude.
- `f1ccd63` — overlay respeita DPI e ganha posição/tamanho configuráveis.
- `f6ada23` — motor Groq large-v3 com fallback local e polimento corrigido.
- `7a6f52c` — modo toggle e parada automática por silêncio.
- `d4c7fb8` — overlay em três estados.
- `30df1c9` — alpha real por pixel em janela Win32.
- `15b82fa` — núcleo visual maior após teste do Vitor.

## Validação

- `tools/whisperflow/test_activation.py`: 3/3 cenários passaram.
- Daemon confirmou no log: motor remoto, overlay em camadas e hotkey ativos.
- Overlay foi inspecionado em fundo claro e escuro para verificar halo e arcos.

## Bloqueios e riscos

- O áudio sai da máquina quando o motor Groq está ativo.
- Falhas do motor remoto e do polimento ainda degradam silenciosamente; falta
  um indicador de saúde após falhas consecutivas.
- O Claude Cloud precisa abrir a branch `codex/whisperflow-handoff`; a `master`
  remota não recebeu este conjunto porque a `master` local tinha outros 20
  commits paralelos que não foram incluídos sem revisão.
- Há alterações não relacionadas já existentes no working tree; não misturar
  `docs/qg/*`, `package*.json`, `.agents/`, `.codex/` ou `output/` neste trabalho.

## Próximo passo recomendado

Implementar aviso de saúde para falhas consecutivas do motor remoto/polimento.
Depois, adicionar polimento contextual conforme o aplicativo em foco (IA,
WhatsApp, e-mail ou editor), com comportamento configurável e fallback neutro.

## Como retomar

No Claude Cloud, selecione a branch `codex/whisperflow-handoff` e peça ao agente:
**“Leia `docs/sessions/README.md` e `docs/sessions/CURRENT.md`, confira o Git e
continue do próximo passo sem reabrir decisões já registradas.”**
