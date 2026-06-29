# ARVEX Meet Transcriber

Extensão Chrome que **captura a transcrição do Google Meet** (lê as legendas/CC ao vivo — não grava áudio) e exporta em `.txt`. Própria, grátis, pro Sales Coach do ARVEX.

## Como instalar (modo desenvolvedor)
1. Abra `chrome://extensions` no Chrome (ou Edge).
2. Ligue o **"Modo do desenvolvedor"** (canto superior direito).
3. Clique em **"Carregar sem compactação" / "Load unpacked"**.
4. Selecione a pasta **`docs/plugin-meet-transcriber`** (esta pasta).
5. A extensão aparece na lista. Fixe o ícone na barra (opcional).

## Como usar
1. Entre numa reunião no **Google Meet**.
2. **Ligue a legenda (CC)** do Meet (botão de legendas / "Ativar legendas"). ⚠️ Sem a legenda ligada, não há o que capturar.
3. No canto inferior direito da página aparece o widget **"▶ Transcrever"** — clique pra iniciar.
   - (Ou abra o popup da extensão e clique **"Iniciar transcrição"**.)
4. Conforme as pessoas falam, a transcrição acumula (o contador sobe).
5. Ao terminar: **Copiar** (⧉) ou **Baixar .txt** (⤓) — no widget ou no popup.
6. Cole a transcrição na aba **"Reuniões"** do CRM → análise do Sales Coach.

## Notas
- A transcrição é salva localmente (`chrome.storage.local`) por reunião — sobrevive a F5.
- Idioma: funciona com legenda em PT-BR, EN e outros (detecta a região por `aria-label`).
- **Privacidade:** roda 100% local; nada é enviado a servidores (a não ser quando você colar no CRM).

## Manutenção (importante)
O Google Meet **não tem API pública** de legendas. A extensão lê o DOM via seletor semântico (`role="region"` + `aria-label`) com **fallback heurístico** (`caption-parser.js`). Se um dia parar de capturar, o Google provavelmente mudou o DOM → ajuste os seletores em **`caption-parser.js`** (funções `findRegion` e `parseRows`). É o único arquivo que precisa de manutenção nesse caso.

## Fase 2 (futuro)
Botão "Enviar pro CRM" → cria a reunião direto na aba Reuniões e dispara a análise (sem copiar/colar).
