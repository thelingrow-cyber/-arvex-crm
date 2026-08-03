# Pesquisa para Clone Raul Seixas — Base de Conteúdo

> Material-fonte do clone conversacional do Raul Seixas (`.claude/clones/raul-seixas/`).
> Aqui ficam as **transcrições originais** e o **prompt de extração**.
> Os destilados por fonte ficam em `.claude/clones/raul-seixas/sources/`.

**Uso:** pessoal — trocar ideia. Não é clone de decisão de negócio.

## Configuração de análise

- Prompt: [PROMPT-EXTRACAO.md](PROMPT-EXTRACAO.md) (**v2 Raul**) — uma rodada por transcrição.
  A fonte 01 foi processada com a v1; reprocessar se sobrar tempo (a v2 pega
  palavras recusadas, ações não-verbais e o par pergunta→resposta)
- Regra crítica: **não inventar** — Raul é pessoa real (1945–1989). Só o que está
  na transcrição. Citação literal entre aspas; trecho duvidoso marcado `[incerto]`
- Só a fala do Raul vira insight; entrevistador entra como contexto
- Contradições são preservadas, não resolvidas

## Índice

| # | Conteúdo | Tipo | Transcrição | Destilado |
|---|----------|------|-------------|-----------|
| 01 | Mudança Rio → SP, origem baiana, rock e classe, Sociedade Alternativa, Lennon, virada de fase | Entrevista de TV (2 tomadas) | pendente | [entrevista-tv-mudanca-sao-paulo.md](../../.claude/clones/raul-seixas/sources/entrevista-tv-mudanca-sao-paulo.md) |
| 02 | Reciclagem, o diário da infância, o irmão Plínio, cinema, Plunct Plact Zuum, parceria com a mulher, show do metrô | Entrevista de TV (com "Marília") | pendente | [entrevista-tv-reciclagem-livro-thor.md](../../.claude/clones/raul-seixas/sources/entrevista-tv-reciclagem-livro-thor.md) |

| 03 | Disco *Mata Virgem*, virada bucólica, método de arranjo, tese de *Judas*, influências tropicalistas, teatro e livro infantil | MPB Especial (ASR muito degradado) | pendente | [entrevista-mpb-especial-mata-virgem.md](../../.claude/clones/raul-seixas/sources/entrevista-mpb-especial-mata-virgem.md) |

> **Fases no corpus.** 01 e 02 são do mesmo período (~1983-84) e da mesma
> campanha — mesmo disco, mesmo livro —, então muita repetição entre elas é
> release, não núcleo duro. A 03 é anterior (~6 LPs antes) e corrigiu o vício:
> já dá para separar traço permanente de fala de campanha.
>
| 04 | Diálogo com Paulo Coelho: pecado do não-envolvimento, seguidores deixados na mão, alcoolismo, morte, dinheiro, parceria travada | Conversa gravada (ASR muito degradado; extração por nível de confiança A/B/C) | pendente | [dialogo-paulo-coelho.md](../../.claude/clones/raul-seixas/sources/dialogo-paulo-coelho.md) |

> 🔑 **A fonte 04 é a base do jeito de falar.** O ASR destruiu as palavras mas
> preservou o ritmo — ver a seção *Padrão de fala* nela, que é o que faz o clone
> soar como ele. Vale re-transcrever com áudio melhor: o segundo "pecado capital"
> se perdeu no ASR e é provavelmente o material mais valioso do corpus.

> **Traços confirmados em fases diferentes** (podem ir para o clone com confiança):
> timidez · recolher-se antes de criar · recusar a palavra oferecida e trocar por
> outra (3/3 fontes) · não acompanhar as próprias vendas · Gonzaga + Elvis como as
> duas sementes · já estar no próximo projeto enquanto divulga o atual.

## Escopo do clone

Existência, liberdade individual, criação e o preço de não pertencer.
Fora disso, ele desconversa.

## Próximos passos

- [x] Processar a 1ª entrevista com o prompt v1
- [ ] Salvar a transcrição crua da fonte 01 em `transcricoes/` (rastreabilidade das citações)
- [ ] Coletar fontes 2-4 — priorizar as lacunas apontadas no "Cruzamento" da fonte 01:
      composição, Sociedade Alternativa como ideia, morte/fé, os pais
- [ ] Destilar os 4 arquivos do clone
- [ ] Criar `.claude/commands/AIOX/clone/raul-seixas.md`
