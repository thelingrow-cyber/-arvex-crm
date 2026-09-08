# Contexto atual — Codex ↔ Claude

> Ponto de retomada compartilhado e versionado. Leia antes de agir e atualize
> ao concluir um bloco relevante, antes de compactar ou ao trocar de ferramenta.
> Não registrar segredos, tokens, dados pessoais ou transcript integral.

## Objetivo ativo

Finalizar e validar as páginas de captura A e B do **Desafio Ótica +100K** da
Cindy Batista, priorizando a A curta que está rodando e preparando a B longa
para teste com tráfego frio.

## Estado atual

- Branch local: `master`, HEAD `09a962e`.
- A curta: `docs/landing-desafio-otica-100k/index.html`.
- B longa: `docs/landing-desafio-otica-100k/index-b.html`.
- A publicada: `https://cindyb.com.br/desafio-otica-100k/`.
- A publicada ainda mostra a subheadline e a microcopy anteriores. A versão
  local removeu a microcopy e reforçou que somente o grupo recebe a oferta.
- B ainda não está publicada em `/desafio-otica-100k-b/` (404 em 08/09/2026).
- O link correto do Grupo VIP está nos dois arquivos:
  `https://chat.whatsapp.com/HvCkrHesa3C8KDopm8j2Md`.

## O que o Claude alterou após o refinamento da A (`9373847`)

### Página A

- Limpou o hero: removeu a microcopy abaixo do CTA.
- Subheadline local atual: “Entre no Grupo VIP. Só quem estiver no grupo recebe
  o acesso à oferta especial do desafio.”
- A estrutura de uma dobra, estética e foto da Cindy foram preservadas.

### Página B

- Reescreveu a B para voltar a ser página de captura, mantendo uma única ação:
  entrada no Grupo VIP.
- Hero alinhado à A, seguido de agenda dos três dias, provas reais, bloco “Como
  funciona”, autoridade da Cindy e CTA final.
- Entrega principal nomeada como **Plano de Fim de Ano**.
- Agenda atual:
  - Dia 1: “Para de brigar por preço”.
  - Dia 2: “A campanha que a sua base já está esperando”.
  - Dia 3: “O modelo que permite faturar mais sem depender da sua presença o
    tempo todo”.
- Provas usadas:
  - Michaella: +R$ 30 mil com os conteúdos do desafio.
  - Galeria de Óculos: 16k → 63k.
  - Duas lojas: R$ 143.323 e R$ 134.906, ambas em recorde; imagem embutida em
    base64 para funcionar no WordPress sem upload adicional.
- Bio oficial aplicada: 10 anos no ramo óptico, 3 óticas próprias e mais de
  10.000 pares de lentes vendidos.

## Decisões preservadas

1. A curta é a página principal para rodar agora.
2. B é uma variante longa para teste com público frio; não substituir a A sem
   validação.
3. Não usar contador ou “vagas limitadas” sem escassez real.
4. Manter CTA direto para o Grupo VIP, sem formulário intermediário.
5. Preservar a foto da Cindy; integração visual é feita por CSS.
6. O Pixel Meta `904293195276149` já é injetado pelo PixelYourSite. Não criar
   outro `fbq('init')` no HTML.

## Commits relevantes

- `9373847` — refinamento estético da página A.
- `a2a70e5` — B recebe provas com print da landing de vendas.
- `a0acfb7` — reescrita da copy pós-primeira dobra da B.
- `1be7d2d` — B volta a ser captura, com prova no hero e entrega nomeada.
- `512938a` — prova de teto de R$ 143 mil entra na B.
- `3972865` — terceira prova embutida em base64.
- `a9cf5b4` — limpeza do hero nas páginas A e B.
- `e07a94c` — entrega passa a ser Plano de Fim de Ano.
- `bf6f621` — título da agenda ajustado ao blueprint.
- `d80db1c` — bio oficial da Cindy.
- `09a962e` — headline da campanha vira título do Dia 3.

## Validação observada

- Em 08/09/2026, a A publicada abriu com foto e link correto do Grupo VIP.
- A publicada ainda não recebeu a última limpeza de copy existente no arquivo
  local.
- `/desafio-otica-100k-b/` retornou página não encontrada.
- As alterações recentes da B estão commitadas localmente; não há prova de que
  foram enviadas ao remoto ou ao WordPress.

## Bloqueios e riscos

- Confirmar com a Cindy se as lives serão realmente às 19h e se duram cerca de
  duas horas.
- Confirmar a ordem dos pilares/temas por dia.
- Confirmar autorização e identificação da terceira prova de resultado.
- A B ainda contém link de política de privacidade sem destino real.
- `master` local está 47 commits à frente de `origin/master`; não afirmar que o
  Cloud ou remoto recebeu essas mudanças.
- Existem alterações não relacionadas no working tree; não misturar
  `docs/ecossistema/*`, `package*.json`, `.agents/`, `.codex/`, `docs/research/`
  ou `output/` neste trabalho.

## Próximo passo recomendado

Revisar visualmente a B atual em mobile e desktop, corrigir apenas falhas reais
e validar com o Vitor. Depois, publicar a B em uma URL separada e decidir a
divisão de tráfego entre A e B. Se a prioridade imediata for a A, atualizar o
código no WordPress com a versão local e limpar o LiteSpeed Cache.

## Como retomar

> Leia `docs/sessions/README.md` e `docs/sessions/CURRENT.md`, confira o Git e
> continue da próxima ação sem reabrir decisões já registradas.
