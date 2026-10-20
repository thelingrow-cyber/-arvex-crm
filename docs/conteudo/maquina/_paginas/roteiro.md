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
*Mudança de 20/10: o Claude do celular, sem regra nenhuma, escreveu melhor que a máquina (texto D do `roteiros-ouro.md`).
Por isso o escritor escreve livre e as regras ficam com o revisor.*

1. Leia `squads/conteudo/roteiros-ouro.md` (a pessoa e os 4 textos-ouro, sobretudo o D) e a skill
   `.claude/skills/content-principles/SKILL.md`, e veja os últimos pares de `squads/conteudo/voz-pares.md`.
2. Entenda o tema até conseguir dizê-lo em dez palavras. Pergunte-se qual pergunta ele abre na cabeça de quem assiste.
3. Escreva de uma vez, como o Vitor falaria pra um amigo dono de negócio: uma ideia só, em parágrafos de fala, pensando
   em voz alta. **Não siga roteiro de etapas, não encaixe "É tipo", objeção ou CTA porque "tem que ter".** Se a peça
   pedir uma comparação ou uma ressalva, ela entra; se não pedir, não entra.
4. Confira todo fato com WebSearch na fonte primária e anote o link em "Fontes". Fato sem fonte sai.
5. Leia em voz alta, na cabeça. O que não sai numa respiração, refaça.
6. Se chegaram correções do revisor ou uma nota do Vitor, aplique todas. A nota do Vitor vale mais que qualquer regra.

## Regras que não se quebram (só estas; o resto o revisor cobra)
- Nada inventado: número, citação e fato pessoal do Vitor só com fonte real.
- Nada de ótica nem da Cindy.
- A ponte pro negócio sai da consequência da própria notícia, nunca "a IA que responde teu cliente" (20/10).

## Critério de pronto
- [ ] Formato de saída completo: título, molde, roteiro, título fixo, notas e fontes.
- [ ] Lido em voz alta, soa como o texto D e o lado "falado" de `voz-pares.md`.
- [ ] Todo fato tem link.

## Erros conhecidos
| Sintoma | Causa | Correção |
|---|---|---|
| Ponte que o corpo do roteiro não prova (tema 4: "alguém que nunca existiu", mas a prova era sobre a criança) | o fecho foi escrito antes da prova | escrever a prova primeiro e tirar o fecho dela |
| Objeção ou abstração plantada ("dúvida, medo" ao lado de "boleto") | encaixar teste do `voz.md` como ingrediente | usar só coisa concreta |
