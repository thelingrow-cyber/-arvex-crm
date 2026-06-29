# Plano — Extensão própria de transcrição do Meet ("Tactiq grátis")

**Autor:** Orion · Data: 2026-06-29 · Objetivo: extensão Chrome própria que captura a transcrição do Google Meet (igual Tactiq), sem pagar. Build autônomo em loop.

## Tese
O Tactiq não grava áudio — ele **lê as legendas ao vivo do Meet** (que já trazem quem falou). A extensão própria faz o mesmo: observa o DOM das legendas, acumula transcrição + falante, e exporta. Conecta com o Sales Coach (a transcrição vira upload na aba "Reuniões"). MVP: capturar + copiar/baixar. Fase 2: enviar direto pro CRM.

## Esteira de agentes (papéis — executados no loop)
| Etapa | Papel | Entrega |
|-------|-------|---------|
| 1 | @analyst | Pesquisa: como Tactiq/caption-scraping funciona, estrutura do DOM das legendas do Meet (2026), padrões Manifest V3, riscos de ToS/manutenção |
| 2 | @architect | Arquitetura da extensão MV3 (content script + popup + storage), estratégia de seletores robusta com fallback |
| 3 | @dev | Build: manifest.json, content.js (observer de legendas), popup, README |
| 4 | @qa | Revisão: sintaxe, lógica, robustez, anti-quebra; escreve prompt de melhoria |
| (loop) | auto | repetir 3-4 refinando até estável |

## Arquitetura (Manifest V3)
```
plugin-meet-transcriber/
  manifest.json        # MV3: permissions (activeTab, storage, downloads, clipboardWrite),
                       #      content_scripts em https://meet.google.com/*, action(popup)
  content.js           # injeta widget; MutationObserver no container de legendas;
                       #      extrai {falante, texto}; dedupe; acumula em memória + storage
  caption-parser.js    # lógica de achar o container de legendas (seletores + fallback heurístico)
  popup.html / popup.js# status (gravando/parado), nº de linhas, botões Copiar / Baixar .txt / Limpar
  styles.css
  README.md            # como carregar (chrome://extensions, modo dev, "Load unpacked") + como testar
```

### Captura (o coração)
- Ligar a legenda do Meet (CC). A extensão observa o DOM das legendas via `MutationObserver`.
- Cada bloco de legenda traz nome do falante + texto. Acumula **linhas únicas** (dedupe por falante+texto, porque o Meet reescreve a legenda enquanto a pessoa fala — pega a versão final).
- Guarda incrementalmente em `chrome.storage.local` (sobrevive a refresh).
- Widget flutuante: Iniciar/Parar, contador, Copiar, Baixar .txt.

### Risco conhecido (documentar)
- Seletores do DOM do Meet mudam → a extensão pode quebrar. Mitigar com **seletor por atributo/estrutura + fallback heurístico** (procurar a região com muitas mutações de texto + nomes). Documentar onde ajustar quando o Google mudar.
- Precisa da **legenda ligada** no Meet.

## Integração com o Sales Coach (fase 2, fora do MVP)
Botão "Enviar pro CRM" → POST pra uma função/endpoint que cria a `meeting` com a transcrição → análise automática. MVP: só Copiar/Baixar (o closer cola na aba Reuniões).

## Critérios de qualidade (auto-revisão do loop)
- manifest.json válido (MV3, sem campos inválidos).
- content.js / popup.js sem erro de sintaxe (node --check ou new Function).
- Lógica de dedupe correta; storage persiste; export gera .txt legível.
- Seletores com fallback e comentário de manutenção.
- README com passo-a-passo de carregar + testar numa call real.

## O que o loop NÃO consegue validar (fica pro Vitor)
Teste ao vivo numa reunião real do Meet (carregar a extensão + abrir call + ligar CC + ver a transcrição acumular). O loop entrega código revisado + guia; o "funcionou ao vivo" é teste manual.

## Loop (build → auto-analisar → prompt de melhoria → repetir)
1. Pesquisar (web) DOM atual das legendas do Meet + padrões MV3.
2. Construir os arquivos.
3. Auto-revisar (sintaxe + checklist de qualidade) → anotar problemas.
4. Escrever um **prompt de melhoria** (o que ajustar) e aplicar → nova versão.
5. Repetir 3-4 até estável (máx ~3-4 passes) ou travar 3x.
6. Escrever BUILD-REPORT.md (estado, como testar, riscos, prompts de melhoria usados) e encerrar.
```
