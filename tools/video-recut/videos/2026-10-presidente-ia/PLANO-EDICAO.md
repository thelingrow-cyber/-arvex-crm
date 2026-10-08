# Plano de edição — "Se eu fosse presidente" (2026-10-presidente-ia)

**Bruto:** `Downloads\FE55C986-B422-4E8F-86E1-7ACC24B82C9F.mp4` · 100,97s · 1080×1920 HEVC 30fps · take único
**Transcrição:** `work/2026-10-presidente-ia/words.json` (Groq whisper-large-v3, por palavra)
**Roteiro:** `docs/conteudo/banco-pautas/roteiro-presidente-ia.md` (v8)

## Layout
- **Topo (teto vazio, y ~0–620):** inserções — sempre presentes, trocando com o tempo, sem entrada exagerada (corte seco ou fade curto).
- **Meio:** rosto livre.
- **Peito:** legenda nativa, pequena, branca.
- **Fecho (93–97s):** topo vazio — só rosto e frase.

## Tipos e origem
- 🎬 **IA** = gerado (Higgsfield / Kie.ai) — original.
- 🎨 **Motion** = arte/animação nossa (camadas/HyperFrames).
- 📹 **Stock** = vídeo de banco livre (Pexels/Mixkit, licença conferida e anotada em CREDITOS.txt).
- 🖼️ **Foto** = domínio público/CC0 ou gerada.
- ❌ Sem logo, manchete ou print de terceiro. Fonte vai escrita no rodapé do card.

## Linha do tempo v2 — com respiro (pedido do Vitor: v1 "encheu demais")

Regra: inserção só onde ela **prova** algo ou marca capítulo. Entre elas, **respiro** = só rosto + legenda, topo vazio. ~14 inserções, ~55% do tempo com algo no topo.

| # | Tempo | Fala | Topo | Tipo |
|---|---|---|---|---|
| 1 | 0,0–2,5 | "Se eu fosse o próximo presidente" | Vitor recebendo a faixa — tela cheia | 🎬 IA |
| · | 2,5–6,2 | "três maiores potências… em usar já está" | **respiro** | — |
| 2 | 6,3–12,3 | "terceiro que mais usa ChatGPT… EUA e Índia" | Ranking 🇺🇸 🇮🇳 🇧🇷 · "OpenAI, ago/2025" | 🎨 |
| 3 | 12,6–19,3 | "35º… cliente que não fabrica nada" | **3º EM USAR × 35º EM CRIAR** · "Global AI Index" | 🎨 |
| · | 19,4–23,3 | "não é falta de gente boa… indo embora" | **respiro** | — |
| 4 | 23,3–30,9 | "70%… nem a pau… dá pra entender" | 10 bonecos, 7 saem · "Revista Pesquisa FAPESP, 2026" | 🎨 |
| 5 | 31,0–37,6 | "primeiro dia… IR zero por 10 anos… construir aqui" | **DIA 1** · "IR 0% · 10 ANOS" | 🎨 |
| · | 37,6–40,1 | "brasileiro ou gringo, tanto faz" | **respiro** | — |
| 6 | 40,1–44,9 | "primeiro mês… dinheiro pra quem fabrica" | **MÊS 1** · "DINHEIRO PRA QUEM FABRICA" | 🎨 |
| · | 45,2–51,5 | "sofre pra achar investidor… EUA em 79" | **respiro** | — |
| 7 | 51,8–58,3 | "aposentadoria não podia… liberaram um pedaço" | Cofre com cadeado → abre, fatia sai | 🎨 |
| 8 | 58,3–62,8 | "startups… Vale do Silício" | Aérea de cidade de tecnologia | 📹 |
| · | 62,8–68,8 | "aqui faço igual… não paga imposto" | **respiro** | — |
| 9 | 68,8–74,7 | "primeiro ano… chip que só empresa americana vende" | **ANO 1** (2s) → chip em close | 🎨 + 📹 |
| · | 74,7–78,9 | "data center… chip eles têm, energia a gente" | **respiro** | — |
| 10 | 78,9–82,9 | "desligou um terço da energia solar" | Parque solar, 1/3 apagando · "34% · 3º tri 2025 (ONS/BTG)" | 📹 + 🎨 |
| · | 82,9–87,2 | "sentava com os americanos… acordo" | **respiro** | — |
| 11 | 87,2–93,1 | "data center… Nordeste… vira IA rodando" | Data center ao lado de parque eólico no sertão | 🎬 IA |
| — | (se regravar) | objeção do "privilégio" | **respiro** (é frase de rosto) | — |
| 12 | 93,2–96,9 | fecho | **topo vazio** · frase "SÓ CLIENTE NÃO ENTRA NO TOP 3" | — |
| 13 | 97,2–100,8 | CTA | "QUAL VOCÊ APROVARIA? 👇" | 🎨 |

Respiros mais longos (≥4s) caem em frases de opinião/ação dele — é onde o rosto convence mais que a imagem.
Cortados da v1: pódio, USAR ✓, cliente/fabricante, engenheiros, avião, engenheiro programando, passaportes, fundador no notebook, calendário 1979, gráfico anos 80, imposto 0%, data center corredor, split chip/energia, aperto de mão, raio de energia.

## Correções de legenda (fala × ASR)
- "13 maiores" → **três maiores** (conferido com 2º modelo)
- "investir em a brasileira" → **investir em IA brasileira**
- "e a roda num chip" → **IA roda num chip**
- "viria rodando" → **vira IA rodando**
- "Aqui eu falo igual" → **Aqui eu faço igual** (confirmar)
- Fecho e CTA: confirmar com o Vitor a fala exata

## Pendências
- [ ] Vitor: posição da legenda (peito?) e fala exata do fecho/CTA
- [ ] Vitor: regravar a linha do "privilégio" (opcional)
- [ ] Gerar #1 (faixa) no Higgsfield — precisa de 1–2 fotos de frente
- [ ] Gerar #11 (data center no sertão, IA)
- [ ] Baixar stocks (#8, #9 chip, #10 solar) com licença anotada
- [ ] RAM livre estava 0,4 GB — fechar navegador antes do render
