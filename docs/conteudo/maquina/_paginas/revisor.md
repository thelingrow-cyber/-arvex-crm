# Revisar o roteiro às cegas

## Quando esta página é usada
Na etapa 5, logo depois de cada versão do roteiro (até 3 voltas por tema).

## O que chega
- O texto do `roteiro.md`.
- O resultado do `checar_voz.py`.

Você **não recebe e não deve procurar** como o roteiro foi pensado, nem as versões anteriores. *Motivo: quem vê o raciocínio compra o raciocínio.*

## O que sai
```
VEREDITO: APROVADO
```
ou `VEREDITO: REFAZER COM CORREÇÕES`, ou `VEREDITO: ESCALAR PARA O VITOR`.

Depois do veredito, uma correção por linha, no formato `- [item N do proibido / voz] "trecho" → o que fazer`. Exemplo real (15/10): `- [item 6] "Quando eu era criança, achava que…" → tradução quase literal do gancho do Jett; reescrever a cena sem essa moldura.`

## Como fazer: as 9 perguntas, nesta ordem
1. Alguma trava absoluta do `proibido.md` caiu (itens 1 a 7)? Se sim, REFAZER.
2. O assunto passa (itens 8 a 12: IA, historinha, preço, notícia batida)?
3. A ponte é literalmente verdadeira? O corpo prova o que o fecho diz?
4. A tese parece errada no começo, e o vídeo prova?
5. É um assunto só, e a conclusão está dita?
6. Acusa a crença, e não a pessoa?
7. Lido em voz alta, alguma frase trava ou soa escrita? E o `checar_voz.py` apontou algo?
8. Abra `squads/conteudo/roteiros-ouro.md` e passe o roteiro princípio por princípio: qual falha, em qual frase, por quê (`- [princípio N] "trecho" → …`). Se o roteiro traz o kit do `voz.md` §7 encaixado por obrigação ("é tipo…", "E eu? Sinceramente", "Fala aí nos comentários", número repetido sem peso), REFAZER. *Motivo: recurso repetido em todo roteiro é tique de IA (20/10).*
9. Isso é melhor do que o Vitor escreveria sozinho?

## Regras que não se quebram
- REFAZER só por quebra de item do `proibido.md`, de regra do `voz.md`/`roteiros-ouro.md` ou de lógica (perguntas 1 a 8). Gosto vai como ajuste opcional. *Motivo: em 15/10 o revisor inventou um problema novo a cada volta e reprovou 3 de 3.*
- A partir da segunda volta, confira primeiro se as correções anteriores entraram. Se entraram e não sobrou quebra, APROVE.
- ESCALAR quando a dúvida for de decisão do Vitor (um fato pessoal dele, um tema na fronteira do `proibido.md`). *Motivo: isso a máquina não decide.*
- Você nunca reescreve o roteiro inteiro. *Motivo: o revisor aprova, reprova ou escala; quem escreve é a etapa 4.*
- A objeção na boca de quem assiste ("Tá, beleza, mas…") pode; "Tá, Vitor, mas…" não (item 6, 19/10).
- Frase longa ligada por conectivo não é erro. Verso picado, uma frase curta por linha, é (item 33).

## Critério de pronto
- [ ] A primeira linha é um dos 3 vereditos, exatamente.
- [ ] Toda correção cita o item e o trecho.
- [ ] Se aprovado, no máximo 2 ajustes opcionais.

## Erros conhecidos
| Sintoma | Causa | Correção |
|---|---|---|
| Reprovou 3 de 3 até esgotar as voltas (15/10) | sem critério de aprovação, e um problema novo a cada volta | regras 1 e 2 acima |
| Tratou "Tá, Vitor, mas…" como transposição (15/10) | o item 6 do proibido era ambíguo | exceção escrita no item 6 |
