# Criador de Carrossel — Marca Pessoal (Arquiteto-Visionário)

Sistema pra gerar carrosséis de Instagram na SUA voz e no SEU visual, sem "cara de Claude".
Baseado no método dos 3 arquivos (Instruções = régua · Knowledge = identidade), com o
visual travado numa ferramenta pra nunca variar.

## Arquivos

| Arquivo | O que é | Onde vai |
|---------|---------|----------|
| `PROMPT-INSTRUCOES.md` | O prompt completo (a "régua") | Campo **Instruções** do Projeto |
| `knowledge/01-diretrizes-marca.md` | Cores, fonte, regras visuais | **Knowledge** do Projeto |
| `knowledge/02-voz.md` | Como você escreve (voz + frases + exemplos) | **Knowledge** do Projeto |
| `knowledge/03-referencias.md` | Seus melhores carrosséis (repertório) | **Knowledge** do Projeto |
| `index.html` | Ferramenta que vira o JSON em slides PNG 1080×1350 | Abre no navegador |

## Setup (uma vez só, ~10 min)

1. Claude → barra lateral **Projetos** → **Criar Novo Projeto** → nome "Criador de Carrossel".
2. **Instruções:** cole o conteúdo de `PROMPT-INSTRUCOES.md` (só o bloco dentro da caixa). Salva.
3. **Knowledge:** anexe os 3 arquivos de `knowledge/`.
4. Antes de usar de verdade, preencha os 2 "SUBSTITUIR/preencher":
   - `02-voz.md` → cole 3 textos/legendas seus que deram certo.
   - `03-referencias.md` → anexe 5 carrosséis de referência.

## Uso (todo dia) — fluxo padrão

1. No Projeto: **`Carrossel sobre [tema]`** (ou cole um artigo / transcrição de vídeo / lista).
2. Ele mostra o **roteiro** pra você aprovar → você aprova.
3. Ele monta o **artefato HTML** (com botões "Baixar PNG" / "Baixar todos") → você baixa e posta.
4. Post foi bem? Anexa ele no `03-referencias.md` do Projeto. O sistema aprende.

## Modo consistência (opcional) — `index.html`
No fluxo padrão o Claude desenha o artefato a cada vez (jeito do guia): simples, funciona
no plano grátis, mas o visual pode variar um pouco de post pra post ("cara de Claude" no design).

Quando a consistência do feed importar mais que a velocidade, use o `index.html`: peça ao
Projeto o **bloco JSON** (formato no fim do `PROMPT-INSTRUCOES.md`), cole na ferramenta,
**Renderizar** → **Baixar todos (PNG)**. O visual fica travado em código — todo carrossel sai
idêntico, no seu charcoal + gold + Inter, em 1080×1350 real. O Claude pensa e escreve;
a ferramenta cuida do pixel.
