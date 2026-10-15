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
A gente apoia muito mais fácil quem erra do que quem acerta.
E todo mundo jura que não.
"Eu torço por todo mundo."
…
Quem erra ganha apoio. Quem acerta ganha silêncio.
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
2. Escolha no `06-Ganchos/ganchos.md` o gancho cujo **mecanismo** serve ao tema.
3. Para Regra e Identidade, escreva na estrutura da Luana:
   1. a lei;
   2. a fala de quem pensa o contrário, imitada, em 2 ou 3 frases entre aspas;
   3. o porquê, em tom de conversa;
   4. a objeção "Tá, Vitor, mas…" e a resposta;
   5. um exemplo concreto que qualquer pessoa reconhece;
   6. o fecho, com a lei de volta em 5 a 8 palavras.

   Para os outros moldes, siga a ficha do molde em `docs/conteudo/LINHA-EDITORIAL-FORMATOS.md`.
4. Confira todo fato com WebSearch na fonte primária e anote o link em "Fontes". Fato sem fonte sai.
5. Leia o roteiro em voz alta, na cabeça, e quebre toda frase que não sai numa respiração.
6. Se chegaram correções ou uma nota, aplique **todas**. A nota do Vitor vale mais que qualquer regra.

## Regras que não se quebram
- Tudo o que está em `_regras/proibido.md`. *Motivo: cada linha de lá veio de uma reprovação dele.*
- A primeira frase do gancho estrangeiro não é traduzida. *Motivo: tradução literal é transposição. O revisor pegou "Quando eu era criança, achava que…" copiado do Jett em 15/10.*
- Pedágio pessoal só com fato real do Vitor. *Motivo: inventar experiência dele é mentir no rosto dele.*
- Entre 20 e 45 segundos. *Motivo: é a faixa das referências que ele aprovou.*

## Critério de pronto
- [ ] O formato de saída está completo: título, molde, roteiro, título fixo, notas e fontes.
- [ ] A primeira linha é a lei, e a última é a lei de volta.
- [ ] O `checar_voz.py` não acusaria erro: sem travessão, sem palavra proibida, sem frase de mais de 22 palavras.
- [ ] Todo fato tem link.

## Erros conhecidos
| Sintoma | Causa | Correção |
|---|---|---|
| Ponte que o corpo do roteiro não prova (tema 4: "alguém que nunca existiu", mas a prova era sobre a criança) | o fecho foi escrito antes da prova | escrever a prova primeiro e tirar o fecho dela |
| Objeção ou abstração plantada ("dúvida, medo" ao lado de "boleto") | encaixar teste do `voz.md` como ingrediente | usar só coisa concreta |
