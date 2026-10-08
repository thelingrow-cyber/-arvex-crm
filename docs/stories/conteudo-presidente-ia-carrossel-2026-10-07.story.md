# Story — Carrossel da marca pessoal: Brasil potência em IA

**Status:** Ready for Review  
**Data-alvo:** 07/10/2026  
**Solicitante:** Vitor  
**Executor sugerido:** produção de conteúdo/design da marca pessoal  
**Quality gate:** revisão editorial, factual e visual independente

## Story

Como criador da marca pessoal, quero transformar a tese do vídeo “Se eu fosse presidente” em um carrossel complementar e publicável hoje, para ampliar a conversa sobre o Brasil construir IA — sem entregar apenas uma transcrição do vídeo ou confundir propostas políticas com fatos estabelecidos.

## Contexto e direção

O vídeo parte da tensão **usar IA × construir IA no Brasil** e organiza propostas em três horizontes: talento, capital, infraestrutura (chips e energia). O carrossel deve escolher um recorte que acrescente uma camada ao vídeo: tornar visíveis as escolhas, seus mecanismos ou seus custos, e fechar com uma consequência para quem constrói empresas. A capa precisa funcionar sozinha no feed e não repetir literalmente “Se eu fosse presidente”. Preservar a opinião do Vitor como opinião, sem simular um plano de governo aprovado ou resultado garantido.

O artefato pertence à **marca pessoal do Vitor**, não ao perfil institucional ARVEX. Usar o sistema pessoal já documentado: fundo carvão `#0E0F12`, off-white `#F4F0E6`, cinza `#9C978C`, dourado pontual `#C9A24B`, Inter; visual “atelier do futuro”, sem serifa, neon, robô ou ornamento gratuito. Não importar automaticamente a paleta petróleo/serifa do carrossel ARVEX. [Fonte: `docs/carrossel-marca-pessoal/knowledge/01-diretrizes-marca.md`]

## Critérios de aceitação

- [x] Sequência curta com capa, desenvolvimento e fecho, exportada em **PNG 1080 × 1350 px** por lâmina, pronta para Instagram; numeração/ordem inequívoca e contact sheet para revisão.
- [x] Capa com gancho **complementar**, concreto e legível em miniatura, sem repetir a primeira frase ou transformar o vídeo em cards de transcrição.
- [x] Uma ideia principal por lâmina; o corpo mostra o mecanismo e ao menos uma tensão/objeção real, não apenas três promessas soltas. O último slide oferece uma conclusão nova e uma pergunta que convide debate.
- [x] Toda afirmação factual, ranking, porcentagem, data e comparação tem fonte e recorte temporal anotados em arquivo de checagem. Separar explicitamente **fato verificado**, **inferência** e **proposta/opinião**. Se um número não puder ser reconfirmado em fonte confiável, reescrever sem o número.
- [x] Redação preserva o eixo e a voz do Vitor, sem atribuir a ele fala não presente no vídeo como citação literal. O carrossel conversa com donos/empresários, não é uma peça de política pública técnica.
- [x] Identidade visual segue as diretrizes da marca pessoal e contém variação de composição entre lâminas. Imagem gerada, se usada, é claramente editorial e não se passa por foto documental de acontecimento real. Fotos/frames de terceiros exigem licença e crédito verificados.
- [x] Legenda pronta em português, acrescentando contexto ou provocação em vez de recontar todas as lâminas; não inclui dado novo sem checagem.
- [x] PNGs reabertos e inspecionados em tamanho integral e miniatura: texto, contraste, acentos, margens, cortes e artefatos visuais. Registrar validação e lista de arquivos efetivamente produzidos antes de marcar Done.

## Tarefas / subtarefas

- [x] Selecionar um ângulo editorial complementar ao vídeo e escrever o roteiro slide a slide (AC 2–5).
- [ ] Conferir a fala final do vídeo contra o roteiro v8 antes de usar formulações como citações; checar independentemente os fatos escolhidos (AC 4–5).
- [x] Produzir o sistema de layouts em 1080 × 1350 e exportar PNGs + contact sheet (AC 1, 6).
- [x] Escrever a legenda e revisar ortografia e precisão (AC 4, 7).
- [x] Fazer revisão visual no tamanho de feed e registrar as correções/validação (AC 8).

## Notas para execução

- Roteiro vigente de origem: `docs/conteudo/banco-pautas/roteiro-presidente-ia.md`, seção **“B — Se eu fosse presidente — v8”**. As versões anteriores no mesmo arquivo são histórico descartado; não misturar medidas de versões diferentes.
- Plano visual e localização do bruto/transcrição: `tools/video-recut/videos/2026-10-presidente-ia/PLANO-EDICAO.md`. O plano registra pendências de confirmação da fala final; portanto não presumir que o vídeo publicado é idêntico ao script.
- O número **35º** está sinalizado no próprio roteiro como edição de **2023** do Global AI Index e exige atualização ou contextualização. O dado de **mais de 70%** refere-se a pesquisadores brasileiros no exterior em geral, não especificamente a profissionais de IA. A energia solar cortada é recorte do **3º trimestre de 2025**, não percentual atual ou anual. Esses dados não são pré-aprovados para a arte. [Fonte: `roteiro-presidente-ia.md`, “Checagem v8”]
- A biblioteca de formatos recomenda traduzir a fronteira da IA para o dono/empresário, em vez de usar linguagem de desenvolvedor. [Fonte: `docs/carrossel-marca-pessoal/knowledge/04-formatos.md`, “Regra de ouro”]
- Não prometer que medidas isoladas colocariam o país no top 3; isso é tese/proposta do vídeo, não projeção demonstrada.
- Saída sugerida: `output/carrossel-marca-pessoal/presidente-ia-2026-10-07/`. Esse caminho é apenas organização de entrega, não exige ferramenta nova.

## Validação

- Revisão editorial: comparação lado a lado com vídeo/roteiro, confirmando complementaridade.
- Revisão factual: tabela por afirmação com fonte, data, qualificação e decisão de uso.
- Revisão visual: contato geral + inspeção de cada PNG no celular/miniatura.
- `npm run lint`, `npm run typecheck` e `npm test` são quality gates do repositório **se houver mudança de código**; registrar resultado ou motivo de não aplicabilidade para uma entrega puramente editorial.

**Execução em 07/10/2026:** sete PNGs 1080 × 1350 foram renderizados e reabertos individualmente e em miniatura. Revisão QA independente: **Ready for Review** após correção de contraste, ressalva prudencial no slide 5, rótulos de imagens geradas nos slides 4/6 e frame de olhos abertos no slide 7. O ranking usado foi checado na fonte primária da OpenAI; dados antigos/ambíguos do roteiro foram excluídos. A conferência editorial usou roteiro v8 e transcrição do bruto; não houve comparação com o vídeo final já publicado, portanto a subtarefa acima permanece aberta. `node --check build.cjs` e o build dos PNGs passaram. `npm run lint` e `npm run typecheck` não estão definidos no `package.json`; `npm test` foi executado e seu resultado final está no handoff de sessão.

## File List

- `docs/stories/conteudo-presidente-ia-carrossel-2026-10-07.story.md` — esta story.
- `output/carrossel-marca-pessoal/presidente-ia-2026-10-07/build.cjs` — fonte reproduzível.
- `output/carrossel-marca-pessoal/presidente-ia-2026-10-07/README.md` — sequência, legenda, checagem factual, origem das imagens e limites.
- `output/carrossel-marca-pessoal/presidente-ia-2026-10-07/contact-sheet.png` — visão geral.
- `output/carrossel-marca-pessoal/presidente-ia-2026-10-07/slides/01.png` a `07.png` — exportações finais.
- `docs/sessions/CURRENT.md` — handoff desta entrega.

## Change Log

| Data | Versão | Descrição | Autor |
|---|---|---|---|
| 07/10/2026 | 0.1 | Story editorial criada a partir do pedido e dos artefatos vigentes. | @sm |
| 07/10/2026 | 0.2 | Sete artes, legenda e checagem produzidas; QA visual/factual revisou e liberou para revisão do Vitor. | Codex |

## 🤖 CodeRabbit Integration

> **CodeRabbit Integration**: Disabled. A configuração do projeto não habilita CodeRabbit; esta entrega editorial requer revisão manual de texto, fontes e imagens.
