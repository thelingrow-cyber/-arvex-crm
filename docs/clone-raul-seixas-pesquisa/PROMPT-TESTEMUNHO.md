# Prompt de Extração — Fontes de Testemunho (v1)

> Para material em que **outra pessoa fala sobre o Raul** — Paulo Coelho, Kika
> Seixas, Marcelo Nova, biógrafos, jornalistas.
> Não confundir com `PROMPT-EXTRACAO.md` (v2), que é para o Raul falando.
> Saída em `.claude/clones/raul-seixas/sources/testemunho-{quem}-{slug}.md`.

---

## Por que separar

Uma fonte de testemunho **não alimenta os mesmos arquivos** que uma entrevista:

| Alimenta | Não alimenta |
|---|---|
| `context.md` — episódios, pessoas, cronologia | `heuristics.md` — gatilhos de conversa |
| `system.md` — como ele era percebido de fora | Padrão de fala, sintaxe, marcadores |
| Verificação cruzada de fatos entre fontes | Vocabulário e bordões |
| Comportamento observado por outro | Citações verbatim |

**Regra dura:** nada de uma fonte de testemunho entra no clone como fala do Raul.
Terceiro citando o Raul de memória, anos depois, é reconstrução — não registro.

## As três camadas a separar

Todo testemunho mistura três coisas. Marque cada achado com uma:

- **`[OBSERVADO]`** — comportamento concreto que a pessoa presenciou. "Ele fazia X",
  "estávamos em Y e ele Z". É o que mais vale.
- **`[INTERPRETADO]`** — o que a testemunha acha que ele pensava ou sentia.
  Registrar como leitura dela, nunca como estado mental do Raul.
- **`[CITADO]`** — fala atribuída ao Raul pela testemunha. Sempre marcar
  "atribuída por {quem}, {quantos anos depois}". Nunca vai para verbatim.

## Vieses a declarar antes de extrair

Abra o arquivo respondendo, explicitamente:

1. **Que interesse a testemunha tem nesta história?** Coautoria, herança, direitos,
   livro a vender, reputação a defender ou construir.
2. **Quanto tempo passou?** Memória de décadas é reconstrução, não gravação.
3. **A pessoa já contou isso antes?** Versão repetida em público vira roteiro fixo.
4. **Onde ela aparece bem demais na história?** Marcar.

Isso não invalida a fonte — só a calibra. Anote na abertura e siga.

## O PROMPT (colar a partir daqui)

```
Você vai analisar material em que {NOME} fala sobre Raul Seixas, para alimentar
um clone conversacional do Raul. {NOME} não é o Raul: nada aqui vira fala dele.

Antes de extrair, escreva a seção "Vieses" respondendo: que interesse esta
pessoa tem na história; quanto tempo passou; se é versão já contada muitas vezes;
onde ela aparece favorecida demais.

Depois extraia, marcando cada achado com [OBSERVADO], [INTERPRETADO] ou [CITADO]:

## Achado N `[CAMADA]`
**O que é:** uma frase.
**Como aparece:** o trecho, com citação literal da testemunha entre aspas.
**Vale para o clone?** Sim/não, e para qual arquivo. Se não vale, diga por quê.

Depois, as seções fixas:

## Fatos verificáveis
Datas, lugares, nomes, ordem dos acontecimentos. Só o que dá para cruzar.

## Comportamento observado
O que ele FAZIA, segundo quem viu. A camada mais útil de um testemunho.

## Fala atribuída
Toda citação do Raul feita pela testemunha, marcada como atribuída. Não é verbatim.

## Cruzamento com o que o Raul diz
Onde o testemunho confirma, amplia ou contradiz o que ele mesmo disse nas fontes
01-04. **Quando houver conflito entre a versão dele e a de terceiro, a dele
prevalece para o clone** — o clone é ele, não o consenso sobre ele. Registrar as
duas.

## O que só um terceiro pode dar
O que a testemunha vê e ele nunca diria de si — hábitos, contradições que ele não
percebe, efeito dele sobre os outros. É o valor exclusivo desta fonte.

## Lacunas
O que continua sem cobertura.
```

---

## Nota sobre Paulo Coelho especificamente

Testemunha de máximo valor e máximo viés ao mesmo tempo. Foi parceiro, coautor da
Sociedade Alternativa e participante dos episódios — presenciou o que ninguém mais
presenciou. E é parte interessada: tem obra própria construída em cima desse
período, versão pública repetida por décadas, e a relação terminou com dinheiro e
ressentimento envolvidos (ver fonte 04, o bloco de direito autoral).

Ler com as duas coisas na cabeça, sem descartar nem engolir.
