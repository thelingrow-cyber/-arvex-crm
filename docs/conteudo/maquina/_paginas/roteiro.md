# Escrever o roteiro

## Quando esta página é usada
- Na etapa 4, quando o comando `maquina.py roteiro <N>` recebe um tema numerado.
- Na etapa 5, quando o revisor manda refazer.
- Na etapa 6, quando o Vitor manda reescrever com a nota dele.

## O que chega
- Uma linha da lista de temas: `| 8 | A gente perdoa quem erra muito mais rápido do que perdoa quem dá certo. | Identidade | paradoxo | @jettfranzen … | 176.737 |`.
- Ou: o roteiro atual com as correções do revisor.
- Ou: o roteiro atual com a nota do Vitor.

## O que sai
O `roteiro.md` neste formato (exemplo real de 15/10, tema 8):
```
# Quem acerta ganha silêncio

**Molde:** Identidade (estrutura da Luana) · **Tema nº:** 8 · **Duração:** ~38s · **Gancho modelado:** nº 21, @jettfranzen. Mecanismo levado: inverter a moral esperada.

## Roteiro

​```
A gente perdoa muito mais rápido quem erra do que quem dá certo, e todo mundo jura que não, que torce por todo mundo, que quer ver geral crescendo.

É só você pensar naquele amigo que abriu um negócio e quebrou. …

… Se você é esse amigo, escuta o silêncio, porque ele quer dizer que você saiu do lugar.
​```

## Na tela
- **Título fixo:** QUEM ACERTA GANHA SILÊNCIO

## Notas de gravação
- …

## Fontes
- nenhum fato a conferir
```

## Como fazer
1. Cumpra a lista de verificação `docs/conteudo/maquina/_regras/checklists/roteiro.md` e abra todos os arquivos que ela aponta.
2. Leia `.claude/skills/content-principles/SKILL.md` e `squads/conteudo/roteiros-ouro.md` (a pessoa, as 3 decisões, os princípios) e **aplique em silêncio**: nada disso vira lista nem seção no roteiro.
3. **Abertura:** escreva numa linha a pergunta que **este** tema abre na cabeça da pessoa; a primeira frase faz ela segurar essa pergunta. Só depois consulte `06-Ganchos/ganchos.md` pra entender **por que** famílias parecidas prenderam, nunca pra adaptar a frase de outro (decisão 3 do `roteiros-ouro.md`; vale sobre a linha "Os ganchos vêm daqui" da lista de verificação). No cabeçalho, em vez de "Gancho modelado", anote **"Pergunta aberta:"**.
4. **Antes de escrever, leia `squads/conteudo/voz.md` inteiro e os últimos pares de `squads/conteudo/voz-pares.md`** (o que ele escreveu × o que ele disse na câmera). Escreva já como ele diria, em **parágrafos de fala** (um por ideia, frases corridas ligadas por "e", "mas", "porque", "então"), nunca uma frase curta por linha.
   Para Regra e Identidade, a ordem é:
   1. a lei, dita como afirmação de conversa;
   2. a fala de quem pensa o contrário, imitada sem cerimônia ("Repara que a pessoa fala, …");
   3. o porquê, com uma ressalva ou comentário de passagem;
   4. um exemplo concreto que qualquer pessoa reconhece ("É só você pensar em…");
   5. a objeção na boca de quem assiste ("Tá, beleza, mas…") e a resposta;
   6. o fecho: pode ter uma frase afiada, mas termina numa frase falada.

   Para os outros moldes, siga a ficha do molde em `docs/conteudo/LINHA-EDITORIAL-FORMATOS.md`.
5. Confira todo fato com WebSearch na fonte primária e anote o link em "Fontes". Fato sem fonte sai.
6. Leia o roteiro em voz alta, na cabeça, e quebre toda frase que não sai numa respiração.
7. Se chegaram correções ou uma nota, aplique **todas**. A nota do Vitor vale mais que qualquer regra.

## Regras que não se quebram
- Tudo o que está em `_regras/proibido.md`. *Motivo: cada linha de lá veio de uma reprovação dele.*
- A primeira frase do gancho estrangeiro não é traduzida. *Motivo: tradução literal é transposição. O revisor pegou "Quando eu era criança, achava que…" copiado do Jett em 15/10.*
- Pedágio pessoal só com fato real do Vitor. *Motivo: inventar experiência dele é mentir no rosto dele.*
- Entre 20 e 45 segundos. *Motivo: é a faixa das referências que ele aprovou.*

## Critério de pronto
- [ ] O formato de saída está completo: título, molde, roteiro, título fixo, notas e fontes.
- [ ] A primeira frase é a lei, e a última é falada (não aforismo espelhado).
- [ ] Lido em voz alta, soa como os pares de `voz-pares.md` do lado "falado".
- [ ] O `checar_voz.py` não acusaria erro: sem travessão, sem palavra proibida, sem frase de mais de 30 palavras.
- [ ] Todo fato tem link.

## Erros conhecidos
| Sintoma | Causa | Correção |
|---|---|---|
| Ponte que o corpo do roteiro não prova (tema 4: "alguém que nunca existiu", mas a prova era sobre a criança) | o fecho foi escrito antes da prova | escrever a prova primeiro e tirar o fecho dela |
| Objeção ou abstração plantada ("dúvida, medo" ao lado de "boleto") | encaixar teste do `voz.md` como ingrediente | usar só coisa concreta |
