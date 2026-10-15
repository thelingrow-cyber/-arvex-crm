# Referência: o guia que o Fabiano entrega no direct (colado pelo Vitor em 15/10)

> É material de terceiro e serve **só de referência interna**: estrutura do material e método das páginas. Não se publica nem se copia o texto.
> Tema dele: "Corrige a página, não o caso". É o método que esta máquina segue.

## O método (o que a máquina adota)

- **Um Claude lendo 12 páginas**, em vez de 12 agentes. A base é o guia da Anthropic "Building effective agents" (19/12/2024): padrões simples e componíveis, começar pelo mais simples que funciona.
- **5 padrões:** encadeamento · roteamento · paralelização · orquestrador e trabalhadores · avaliador e otimizador. A máquina usa **encadeamento** (etapas 1 a 11) mais **avaliador e otimizador** (roteiro ↔ revisor, com limite de voltas), e roda temas diferentes em paralelo.
- **Fluxo de trabalho, não agente:** a ordem das etapas é conhecida de antemão e fica no código (`maquina.py`).
- **Cada etapa tem 1 responsabilidade, um nome com verbo, e passa de etapa em etapa por arquivo.** Nenhuma conversa com a outra.
- **A página de etapa tem 7 seções fixas:** quando é usada · o que chega (exemplo real) · o que sai (exemplo real) · como fazer · regras que não se quebram (cada uma com o motivo) · critério de pronto · erros conhecidos (sintoma, causa, correção).
- **Revisão cega:** o revisor não vê o raciocínio de quem produziu ("se vê, compra o raciocínio"). Ele aprova, reprova com motivo ou escala para humano, e nunca produz o conteúdo final. O limite de voltas é obrigatório.
- **Quando sai errado, edita a página e não o caso.** Antes de editar, ache a etapa que errou; muitas vezes o erro nasceu na etapa anterior. Escreva a edição no formato antes e depois e confira se ela não quebra o que já funciona.
- **Índice:** a partir de 10 páginas, organizar por tipo de trabalho, não por ferramenta.
- **Medição:** 4 números por semana e um registro de incidente com 4 campos. Se o ciclo funciona, o mesmo erro para de voltar em 6 semanas. Sinal de falha: o mesmo erro voltando com outro nome.

## A estrutura do material (modelo para o `guia` de cada vídeo)

1. Selo "Guia exclusivo" + **título longo que promete o resultado**.
2. **Abertura:** a tese em uma frase forte + a fonte primária com data ("não é opinião de ninguém: está no guia oficial…").
3. O que o guia entrega, contado ("5 padrões, o método, o formato…, 7 prompts").
4. **3 números de destaque** (5 padrões · 19/12/2024 · 1 página).
5. **Passo a passo numerado (9 passos)** com caixa de marcar e progresso salvo. Cada passo tem explicação curta e um **"Atalho"** (a dica prática).
6. Blocos de conceito em cartões (os 5 padrões; fluxo × agente × nenhum; as 7 seções).
7. **Prompts prontos para copiar** (7), na ordem de uso, cada um com o que devolve.
8. **Checklist final** ("confira antes de considerar pronto", 8 itens).
9. **"Funciona no Brasil?"**, a adaptação local (LGPD).
10. **Links** das fontes primárias.
11. **"Dica do Fabiano"**, o fecho pessoal na voz dele.
- Formato: página web interativa, com botão "Baixar PDF" e caixas de progresso.
