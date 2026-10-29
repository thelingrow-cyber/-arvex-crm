# Dossiê de referências — Fábio Hansen

Status: Ready for Review — dossiê entregue com amostra limitada

## Objetivo
Estudar o criador do Reel indicado pelo usuário, `https://www.instagram.com/reel/DdbwbqdKmil/`, no padrão dos dossiês anteriores, com comparação dentro do perfil e mecanismos aplicáveis à marca pessoal.

## Critérios de aceitação
- [x] Identificar o autor pela referência pública: Fábio Hansen, @fabiohansen.
- [x] Executar coleta com alvo de 50 recentes e até 3 picos externos; documentar o resultado real e a limitação. Obtidos 16, sem picos externos independentes. **Alvo numérico não atingido:** ampliação recebeu HTTP 402 do Apify; o estudo não se apresenta como varredura completa.
- [x] Classificar os 16 obtidos; comparar fortes, medianos e fracos do mesmo perfil, identificando famílias de versões.
- [x] Inspecionar nove folhas: seis maiores e três controles; verificar bio e oferta em fontes primárias públicas.
- [x] Escrever ESTUDO.md com mecanismo, estrutura, linguagem, edição, posicionamento, limites e três briefings de teste para a marca pessoal.
- [x] Atualizar síntese/estudo de ganchos, índice de dossiês e handoff.

## Método e limites
- Analista: Bia, conforme definição do squad e task fechar-player.
- Coleta por ferramentas existentes do projeto (Apify, yt-dlp, Groq). Material de referência público, sem login ou conteúdo privado.
- Números descrevem a coleta de 28/10/2026. Alcance não prova causalidade. Views baixas não confirmam trial reel; informação indisponível fica marcada como indisponível.
- Não confundir homônimos encontrados em pesquisa web com o titular do @ identificado no Reel.
- Transcrições automáticas são material de análise; citações selecionadas precisam ser curtas e verificadas. Estudo final usa resumos/estruturas, sem reproduzir roteiros inteiros.

## File list
- `docs/stories/dossie-fabio-hansen-2026-10-28.story.md`
- `docs/conteudo/banco-roteiros/players/fabio-hansen/ESTUDO.md`
- `docs/conteudo/banco-roteiros/players/fabio-hansen/ANEXOS.md`
- `docs/conteudo/banco-roteiros/players/fabio-hansen/FONTES.md`
- `docs/conteudo/banco-roteiros/players/fabio-hansen/reels.json`, `perfil.json`, `resumo.json`, `resumo-auditado.json`, `classificacao.json`
- `docs/conteudo/banco-roteiros/players/fabio-hansen/auditar_dados.py`, `gerar_anexos.py`, `coletar_folhas_controle.py`
- `docs/conteudo/banco-roteiros/referencias/ref-fabiohansen-teu-valor-sendo-escrito-DdbwbqdKmil.md`
- `tools/roteiros/work/estudo/fabiohansen/` (cache local de coleta)
- `docs/conteudo/ESTUDO-GANCHOS.md`
- `docs/conteudo/DOSSIE-ROTEIROS.md`
- `docs/conteudo/banco-roteiros/players/SINTESE-FORMATOS.md`
- `docs/sessions/CURRENT.md`

## Validação
- Auditoria executada: 16 transcrições não vazias; 16 IDs classificados; mediana, total e base de 13 reproduzidos; nove folhas existentes e inspecionadas; ficha preenchida; links locais dos quatro documentos conferidos.
- Anexos gerados por script específico: sem chamar views baixas de trial reprovado, sem descartar o post antigo de 396 views e sem reproduzir roteiros integrais.
- Regra absoluta contra relato pessoal corrigida pelo contraexemplo da academia. Estética presente em fortes e fracos não foi tratada como causa do alcance.
- Formulário PERCEP não enviado. Inspeção de HTML e interface não equivale a teste do atendimento ou conversão.
- `npm run lint` e `npm run typecheck`: comandos tentados, scripts ausentes no package.json. `npm test` passou: handoff íntegro, referenciado e sem padrões de segredo.
- Alterações locais, sem commit/push. Nenhum roteiro publicado ou mensagem externa enviada nesta pesquisa.
