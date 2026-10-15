# Corrigir a página, não o caso

## Quando esta página é usada
Quando o Vitor reprova um roteiro ou outra saída da máquina e a nota dele entra como PENDENTE em `docs/conteudo/maquina/_regras/INCIDENTES.md`. Comando: `maquina.py corrigir <pasta>`.

## O que chega
- A saída errada: o `roteiro.md`, ou as versões `roteiro-v*.md` da pasta.
- A nota do Vitor: o `notas-do-vitor.md` da pasta. Exemplo real de 14/10: "ficou muita historinha".
- As páginas das etapas, em `docs/conteudo/maquina/_paginas/`, e as regras, em `docs/conteudo/maquina/_regras/`.

## O que sai
```
## Etapa que errou
4 · roteiro, porque … (ou: "o erro nasceu na etapa 2 · temas, porque o tema já pedia uma história")

## Trecho que permitiu
"<a frase da página, ou: faltava a regra>"

## Edição
Arquivo: docs/conteudo/maquina/_paginas/roteiro.md · seção "Regras que não se quebram"
ANTES: …
DEPOIS: …

## Risco
O que essa edição pode quebrar no que hoje funciona, e como testar (ex.: rodar `maquina.py roteiro 8` e ver se ainda passa).

## Linha do INCIDENTES.md
| 15/10 | 4 · roteiro | … | roteiro.md: … |
```

## Como fazer
1. Leia a nota do Vitor e a saída errada.
2. Ache a etapa que produziu o erro. Confira a etapa anterior antes de culpar a última: um tema mal escolhido (etapa 2) aparece como roteiro ruim (etapa 4).
3. Ache na página dessa etapa a frase ambígua, a regra que faltava ou o caso que ninguém previu.
4. Escreva a edição no formato antes e depois: a menor mudança que impede o erro **em todos os próximos casos**.
5. Diga o que a edição pode quebrar e qual teste prova que não quebrou.
6. Escreva a linha pronta para o `INCIDENTES.md`.

## Regras que não se quebram
- Você **não** entrega o roteiro corrigido, só a edição da página. *Motivo: corrigir o caso conserta uma vez; corrigir a página conserta sempre (método do Fabiano).*
- Você não aplica a edição. Quem edita é o Orion ou o Vitor, depois de ler. *Motivo: edição de página muda todos os próximos vídeos.*
- Reprovação de gosto pessoal do Vitor vira regra com a data e as palavras dele. *Motivo: é assim que o `proibido.md` foi montado.*

## Critério de pronto
- [ ] As 5 seções de saída estão presentes.
- [ ] O ANTES é um trecho que existe de verdade na página, ou está escrito "faltava".
- [ ] A edição é geral, não um remendo para este roteiro.

## Erros conhecidos
| Sintoma | Causa | Correção |
|---|---|---|
| (vazio: anotar aqui quando aparecer) | | |
