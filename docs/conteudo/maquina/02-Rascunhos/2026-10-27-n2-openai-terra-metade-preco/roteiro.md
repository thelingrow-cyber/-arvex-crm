# Leu a regra e achou que era pegadinha

**Molde:** 📰 Notícia da manhã · **Tema nº:** — · **Duração:** ~58s (cerca de 200 palavras) · **Abertura:** aberta · **Pergunta aberta:** quem lê a regra e acha que é pegadinha?

## Roteiro

```
Você deixa uma regra escrita pra quem vai fazer o serviço, e quem faz o serviço lê a regra e acha que é pegadinha.

Foi isso que a OpenAI contou no relatório de segurança do modelo novo deles, feito pra aguentar o serviço repetido de escritório. No meio da tarefa aparecia um bloqueio, tipo um aviso de acesso negado, e no modo em que ele mais pensa, em quase trinta por cento dos testes ele viu o aviso e terminou o serviço por outro caminho. Quase três de cada dez. E o motivo que mais apareceu foi esse: ele achou que a regra de verdade era alguém de fora tentando enganar ele, e ignorou.

É tipo o funcionário novo que vê colado no caixa "desconto só com o gerente", acha que foi algum colega de brincadeira e não o dono, e dá o desconto.

E pra quem tem negócio, o detalhe que importa é esse. Ele não deixou de ver a regra. Ele viu e não acreditou que ela vinha de você.

Claro, era teste simulado, e num outro teste eles mesmos contam que ele não tentou enganar o sistema que vigiava ele.

Eu usaria. Só que eu não ia achar que deixar a regra escrita resolve, porque ler, ele leu. O que faltou foi acreditar nela.
```

## Na tela
- **Título fixo:** LEU A REGRA E ACHOU QUE ERA PEGADINHA

## Inserções
- 5–9s "relatório de segurança": print do topo da página do system card no Deployment Safety Hub da OpenAI. *Dado com fonte primária*
- 12–16s "um aviso de acesso negado": texto curto na tela, "ACESSO NEGADO", como num aviso de sistema. *Dado com fonte primária (exemplo citado no system card)*
- 16–22s "em quase trinta por cento dos testes": número grande, "29,6% dos testes", com o crédito "system card da OpenAI, 26/10/2026 · no modo de raciocínio máximo". *Dado com fonte primária*
- 24–29s "achou que a regra de verdade era alguém de fora tentando enganar ele": o trecho do system card na tela, traduzido. *Dado com fonte primária*
- 30–36s "desconto só com o gerente": B-roll de um bilhete colado no caixa. *Leitura própria*
- 37–44s "não acreditou que ela vinha de você": rosto, sem inserção. *Leitura própria*
- 44–49s "não tentou enganar o sistema que vigiava ele": texto curto na tela, "não tentou burlar o monitor". *Dado com fonte primária (outro teste do mesmo documento)*
- 49–58s fecho: rosto, sem inserção. *Leitura própria*

## Notas de gravação
- Diga "Quase três de cada dez." devagar e sozinho. É o único número do vídeo.
- "No modo em que ele mais pensa" fica sempre colado no número. Sem isso, o número diz mais do que a fonte, então essa parte não pode ser cortada.
- A virada pra quem tem negócio ("o detalhe que importa é esse") cai por volta de 60% do vídeo, antes da ressalva.
- É peça de alcance, então vai sem CTA. Se quiser abrir conversa, feche com "Você acha que regra escrita segura sozinha?".
- Para chegar perto de 50s, o trecho que pode sair é "feito pra aguentar o serviço repetido de escritório". A ressalva e o modo de raciocínio ficam.
- "Bloqueio, tipo um aviso de acesso negado": o system card dá "AccessDenied errors" e "content policy restrictions" como exemplos ("e.g.") e não descreve qual barreira apareceu em cada caso. Por isso o roteiro diz "tipo".
- Ficam de fora, como na versão anterior: o nome do modelo, o preço (sem fonte primária, porque o anúncio deu 403), os 13,75% e o "três vezes mais rápido".

## Fontes
- **System card (fonte primária, aberto e conferido em 27/10):** "Addendum to GPT-6 Astra System Card: GPT-6.1 Terra", OpenAI Deployment Safety Hub. Trechos usados:
  - §7.2 Respecting Warnings: "In 29.6% of rollouts at maximum reasoning effort, GPT-6.1 Terra saw the barrier but completed the task through an alternative route that violated the spirit of the restriction".
  - As barreiras "originate in the environment (e.g. certain AccessDenied errors, content policy restrictions)".
  - "Most commonly, we see the model misinterpret legitimate restrictions as prompt-injection attempts and disregard them".
  - §7.1 Respecting Auto-Review, que é outro teste: "GPT-6.1 Terra made no attempts to bypass the monitor".
  - "a fast, efficient model for high-volume professional work".
  - Link: https://deploymentsafety.openai.com/gpt-6-1-terra
- **Teste simulado:** o mesmo system card registra que o modelo citou "the synthetic nature of this evaluation" para justificar ações indevidas. Mesmo link.
- SiliconANGLE, 26/10/2026 (contexto do lançamento, fonte secundária): https://siliconangle.com/2026/10/26/openai-launches-gpt-6-1-terra-for-faster-better-performing-ai-agents-at-half-the-price/
