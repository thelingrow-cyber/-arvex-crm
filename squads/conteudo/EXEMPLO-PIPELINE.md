# Exemplo de ponta a ponta — uma pauta virando roteiro gravável

> Teste real rodado em 2026-09-23 para provar a divisão de trabalho: **o clone opina, o roteirista escreve.**
> Nada aqui foi inventado: a pauta saiu do banco, a dor saiu de call real, o parecer saiu dos arquivos
> do clone `.claude/clones/michael-gerber/`, e o artefato citado existe no repositório.

---

## Etapa 1 — A pauta (vem de `docs/conteudo/banco-pautas/BANCO.md`)

| campo | valor |
|---|---|
| **Fonte** | dor `d-equipe` — "a equipe não converte" |
| **Palavra real do cliente** | *"minha equipe não está preparada"* · *"chega mensagem o dia todo e some todo mundo"* |
| **Família de gancho** | Pergunta com alvo concreto — pico medido **33.000**, a mais subutilizada por ele |
| **Função** | alcance |
| **Clone disponível** | ✅ michael-gerber (E-Myth está no banco, e o clone existe) |

---

## Etapa 2 — O clone opina (saída: parecer, NUNCA roteiro)

**Consulta:** `.claude/clones/michael-gerber/heuristics.md`, seção 5 (Pessoas e delegação).

> **Parecer do clone Gerber — 3 linhas:**
> 1. O impulso de "contratar alguém bom pra resolver o caos" é o erro; primeiro o sistema, depois a
>    pessoa comum que roda ele. *(heurística 5.1)*
> 2. Se um funcionário não performa, verifique primeiro se existe sistema claro pra ele seguir, antes
>    de culpar a pessoa. *(heurística 5.5)*
> 3. Depender de encontrar gente extraordinária é apostar na sorte. *(heurística 5.3)*
>
> **Termo nomeado por Gerber que é citável com segurança:** *gestão por abdicação*
> (verificado em `sources/index.md`, fonte 10).

**O que o clone entregou que a pauta sozinha não tinha:** a inversão da culpa. O dono acha que
precisa de gente melhor; a lente do Gerber diz que ele precisa de sistema. Isso liga direto com o
artefato do Vitor — e nenhuma linha acima é um roteiro.

> 🔁 A mesma pauta com outro clone daria outro ângulo: **Hormozi** veria oferta fraca chegando num
> atendimento certo; **Cialdini** veria falta de prova social no primeiro contato.

---

## Etapa 3 — O roteirista escreve (na voz do Vitor, `voz.md`)

**Artefato na tela:** o painel de notas por etapa da análise de calls — **tem que entrar antes dos 15s**,
porque a peça tem relato pessoal (regra 3 do squad).

```
Sabe qual é a pior hora pra contratar mais gente?

Quando chega mensagem o dia todo e some todo mundo.

Eu já tentei resolver isso contratando. Contratei.
Três meses depois o problema era o mesmo, só que com folha maior.

Tem um livro de 1995, o E-Myth, que deu nome pra isso: gestão por abdicação.
Você não delegou. Você largou.

Porque a pessoa nova chegou e não tinha roteiro, não tinha padrão,
não tinha onde olhar pra saber se fez certo.
Herdou o mesmo caos, com um crachá.

Aí eu parei de contratar e fiz o contrário.
Mandei transcrever todas as minhas calls de venda e dar nota por etapa.
A mesma etapa era o fundo da tabela em todas.

Não tinha vendedor ruim.
Tinha uma etapa que ninguém nunca tinha olhado.

Se o resultado muda conforme quem atende, o problema não é quem atende.
É que não existe o que seguir.
```

**~33 segundos. Sem CTA.**

---

## Etapa 4 — O portão de qualidade (12 testes do roteirista)

| # | Teste | |
|---|---|---|
| 1 | Gancho no primeiro segundo, sem aquecer | ✅ |
| 2 | Família entre as 9 que funcionam | ✅ pergunta com alvo |
| 3 | Dono de negócio entende sem saber o que é modelo de linguagem | ✅ |
| 4 | Artefato na tela em 15s | ⚠️ **instrução de edição** — painel entra aos 12s |
| 5 | Certeza serena, sem gritar urgência nem prometer faturamento | ✅ |
| 6 | Teste da boca — lido em voz alta, sem travar | ✅ |
| 7 | Caça-vício: tríade simétrica, travessão, "portanto" | ✅ o "não tinha… não tinha… não tinha" é **verbo repetido**, que é a assinatura dele, não tríade abstrata |
| 8 | Par em tensão | ✅ contratar × sistematizar |
| 9 | Autor pagou pedágio antes de apontar o dedo | ✅ "eu já tentei resolver contratando" vem antes |
| 10 | Autocorreção ou desmonte no meio | ✅ "Você não delegou. Você largou." |
| 11 | Fecho é linha divisória, não conselho | ✅ |
| 12 | Usou as palavras do cliente | ✅ "chega mensagem e some" é fala real |

**Checagem de fonte:** "livro de 1995, o E-Myth" — título e ano são fato conferido.
"Gestão por abdicação" — termo nomeado por Gerber, verificado na fonte do clone.
Nenhuma afirmação sobre o que o capítulo diz. Nenhum número inventado.

---

## O que este exemplo prova

1. **O clone como consultor funciona e não contamina a voz.** O parecer entrou como lente; o texto
   final não tem nenhuma frase que soe Gerber traduzido.
2. **Se o clone tivesse escrito, teria saído Gerber com sotaque** — e era esse o risco.
3. **O livro entrou do jeito seguro:** título e ano como fato, um termo nomeado verificado, e a
   resposta vindo do artefato próprio.
4. **A peça tem prova.** O painel de notas existe — não é argumento, é tela.

## Para repetir

1. Escolher a linha em `docs/conteudo/banco-pautas/BANCO.md`
2. Se a fonte tiver clone (`gerber` · `al-ries` · `hormozi` e os outros 8), pedir o **parecer de 3 linhas**
3. Entregar pauta + parecer ao roteirista (`@Conteudo:agents:roteirista`)
4. Rodar os 12 testes
5. Montar com `python tools\video-recut\camadas\camadas.py <nome>`
