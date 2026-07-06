# PRD — WhisperFlow Próprio (nome de trabalho: "Ditto")

> Autor: análise Fable 5 · 2026-07-06 · para execução por Sonnet/Opus (@dev)
> Docs irmãos: `ARCHITECTURE.md` (decisões técnicas) · `IMPLEMENTATION-PLAN.md` (stories)

## 1. O problema

Vitor digita o dia inteiro — WhatsApp Web (SDR/closer da operação), briefings pro Claude Code, Notion, e-mails. Falar é 3-4× mais rápido que digitar, mas as ferramentas de ditado boas (Wispr Flow, Willow) custam ~$12-15/mês **por algo cujo motor (Whisper) é open source e já roda de graça na máquina dele** — tese que ele mesmo já validou com o `transcrever-instagram.bat`.

O ditado nativo do Windows (Win+H) existe mas é fraco em PT-BR informal, exige internet em parte dos casos e não é confiável em qualquer campo de texto.

## 2. O usuário

- **V1: o próprio Vitor** (1 máquina, Windows 11, CPU sem GPU dedicada). Uso: mensagens de WhatsApp Web, prompts longos pro Claude, anotações.
- **V3 (futuro): clientes da oferta de implementação de IA** — a ferramenta vira peça do "kit de ferramentas próprias" instalável na empresa do cliente. Implicação AGORA: nada de gambiarra atada à máquina do Vitor; tudo configurável por arquivo de config.

## 3. O job a ser feito

> "Estou com o cursor num campo de texto qualquer, em qualquer app. Seguro uma tecla, falo, solto — e o que eu disse aparece escrito ali, pontuado, em 1-3 segundos. Sem janela nova, sem copiar/colar, sem internet."

## 4. Critérios de sucesso (mensuráveis)

| # | Critério | Meta |
|---|----------|------|
| CS1 | Latência soltar-tecla → texto colado (fala de ~8s) | ≤ 3s na máquina do Vitor (CPU) |
| CS2 | Funciona nos 3 apps-alvo do dia a dia | WhatsApp Web (Chrome), campo do Claude Code/terminal desabilitado é aceitável, Notion, Bloco de Notas |
| CS3 | Qualidade PT-BR | Frase de teste padrão transcrita sem erro que mude o sentido; pontuação presente |
| CS4 | Sobrevive ao reboot | Liga com o Windows, sem terminal visível, sem ação manual |
| CS5 | Custo por uso | R$ 0 (100% local após instalação) |
| CS6 | Confiabilidade do daemon | 1 dia inteiro de uso sem travar; falhas nunca derrubam o processo (beep de erro + log) |

**Teste de aceitação final (o "daily driver test"):** Vitor passa 1 dia usando a ferramenta pra TODAS as mensagens de WhatsApp Web. Se no fim do dia ele não voltou a digitar, o produto está pronto.

## 5. Escopo V1 (dentro)

- Push-to-talk global: **segurar** hotkey → grava · **soltar** → transcreve e cola. (Segurar é superior a toggle pra ditado: impossível esquecer o microfone aberto.)
- Feedback sonoro (beep curto ao iniciar/parar gravação; beep triplo = erro). Sem UI.
- Transcrição local (PT-BR com pontuação), modelo residente em memória.
- Colagem automática no app em foco, preservando o clipboard anterior do usuário.
- Config por arquivo (`config.json`): hotkey, modelo, idioma, duração máxima.
- Autostart com o Windows.

## 6. Fora do escopo V1 (explícito, com o porquê)

- ❌ **Mobile** — hotkey global + paste em app arbitrário é outra ordem de complexidade em Android/iOS; o ditado nativo do celular cobre. Se um dia: bot Telegram com o mesmo motor (V-futuro).
- ❌ **UI gráfica / tela de config** — config.json basta pro Vitor; GUI só na versão kit (V3).
- ❌ **Pós-processamento por LLM** (correção de crase, formatação) — Whisper já pontua bem; camada de polimento é V2, opcional e desligada por padrão (custaria API).
- ❌ **Transcrição de reunião** — já existe (plugin Meet Transcriber). Esta ferramenta é DITADO, não ata de reunião. Não misturar.
- ❌ **Nuvem, conta, sync, telemetria** — "100% local" é o argumento de venda do kit.

## 7. Caminho pro kit (V3, não construir agora — só não bloquear)

Instalador simples (Inno Setup) + primeira execução pede o atalho preferido + README de 1 página. Licenças: faster-whisper e modelos Whisper são MIT — **redistribuição livre, zero custo de licenciamento no kit**. Decisão de preço/posicionamento no kit: exclusiva do Vitor, não é bloqueio técnico.

## 8. Riscos de produto

1. **Latência CPU decepcionar** (o único risco que mata o produto) → mitigação: escolha de modelo POR MEDIÇÃO na máquina real (story S2 do plano), não por opinião. Se nem o modelo mais leve satisfizer: flag de config para API Groq/OpenAI como motor alternativo (centavos/uso, decisão do usuário).
2. **Atalho conflitar com apps existentes** → hotkey configurável + default incomum (`Ctrl+Win`).
3. **Campo-alvo rejeitar Ctrl+V simulado** (terminais, apps exóticos) → documentar limitação; modo alternativo "digitação simulada" via config.
