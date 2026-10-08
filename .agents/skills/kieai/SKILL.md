---
name: kieai
description: Gera imagem ou vídeo por IA via API do Kie.ai (Nano Banana, Seedance 2, e qualquer outro modelo do catálogo) e salva o arquivo em output/midia/. Use quando o Vitor pedir para gerar/criar imagem, B-roll, clipe, criativo de anúncio, fundo de slide, thumbnail ou animar uma imagem. Carrega o padrão visual da marca certa antes de escrever o prompt.
---

# Kie.ai — geração de mídia

A chave vive em `KIEAI_API_KEY` (variável de usuário do Windows; no Cloud, secret do ambiente). **Nunca** pedir, ler em voz alta ou gravar a chave em arquivo/chat.

## Fluxo

1. **Marca primeiro.** O valor está na instrução, não na chave. Antes de escrever o prompt, ler o padrão visual de quem vai usar a peça:
   | Uso | Ler |
   |---|---|
   | Marca pessoal do Vitor (carrossel, vídeo, B-roll) | `docs/ecossistema/brand-book-marca-pessoal.md` + `docs/carrossel-marca-pessoal/knowledge/01-diretrizes-marca.md` |
   | Instagram ARVEX | `docs/carrossel-arvex/direcao-visual-v1-proposta.md` |
   | Landings/criativos da Cindy (ótica) | sistema visual de `docs/landing-cindy-vendas/` (Inter 900, gold + navy + verde; nada de serif) |
   Sem marca definida → perguntar qual.
2. **Prompt em inglês**, descritivo (sujeito, cena, luz, enquadramento, estilo, paleta). Texto que deve aparecer na imagem fica entre aspas, no idioma original.
3. **Custo.** Imagem: rodar direto. Vídeo: avisar modelo + duração + resolução e esperar o ok. O custo real sai no campo `creditos` do resultado — citar ao Vitor.
4. **Gerar:**
   ```bash
   python .Codex/skills/kieai/scripts/gerar.py --modelo imagem --prompt "..." --params '{"aspect_ratio":"4:5"}' --nome slug-curto
   python .Codex/skills/kieai/scripts/gerar.py --modelo video  --prompt "..." --params '{"duration":5}'
   python .Codex/skills/kieai/scripts/gerar.py --saldo
   ```
5. **Mostrar** o arquivo salvo (Read na imagem) e o custo. Iterar ajustando o prompt, não trocando de modelo à toa.

## Modelos

| Apelido | Modelo Kie | Padrão | Observação |
|---|---|---|---|
| `imagem` | `google/nano-banana` | 1:1, png | `aspect_ratio`: 1:1, 9:16, 16:9, 3:4, 4:3, 4:5, 2:3, 3:2, 21:9 |
| `video` | `bytedance/seedance-2` | 480p, 9:16, 5s, sem áudio | `resolution` 480p/720p/1080p · `duration` 4–15 · `first_frame_url` anima uma imagem (precisa URL pública) |

Outro modelo: passar o id do Kie direto em `--modelo` e os parâmetros da doc (`docs.kie.ai/market/...`) em `--params`.

## Limites conhecidos

- **Não substitui o Vitor gravando.** Vídeo gerado é B-roll, criativo ou ilustração — a marca é o FAZER observável.
- Personagem consistente entre cenas é fraco via API.
- Resultado e custo de cada geração ficam em `output/midia/ledger.jsonl` — é o dado para decidir, em ~2 meses, se alguma assinatura pode ser cancelada.
