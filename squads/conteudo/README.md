# 🎬 CONTEÚDO Squad

> Criado em 2026-09-23. A máquina de conteúdo da marca pessoal: **pauta → roteiro → gravação → edição**.
> Regra do squad: **todo agente tem ferramenta executável**. Persona sem ferramenta não entra aqui.

## Os quatro agentes

| Agente | Papel | Ferramenta real |
|---|---|---|
| ☕ **pauteiro** (Caio) | fato do dia, filtrado e **conferido na fonte primária** | `tools/roteiros/noticias.py` + checagem na fonte |
| ✍️ **roteirista** (Téo) | roteiro gravável no formato do dia, na voz do Vitor | `ESTUDO-GANCHOS.md` + banco + portão de qualidade |
| 🔬 **analista-referencias** (Bia) | disseca player, mede grade, nomeia mecânica | `tools/roteiros/colher.py` + navegador |
| 🎞️ **editor-video** (Rui) | take bruto → Reels publicado | `tools/video-recut/camadas/camadas.py` |

## Como rodar o dia

```powershell
# 1. manhã — pauta
python tools\roteiros\noticias.py --horas 30 --salvar

# 2. roteiro: chamar o roteirista com formato + pauta escolhida
#    formatos: cafeia · obra · disrupcao · arquetipo · contraste · curiosidade

# 3. Vitor grava em lote (mesma roupa, mesmo enquadramento)

# 4. edição
python tools\video-recut\camadas\camadas.py <nome-do-video>
```

## A base que todos consultam

- **`docs/conteudo/banco-pautas/`** — 119 pautas geradas (`pautas.py`) + 15 ganchos já escritos
- **`voz.md`** — como o Vitor fala, extraído da transcrição literal dos takes dele + os 6 testes do roteiro
- **`cliente.md`** — para quem o roteiro fala, com nível de evidência (🟢 palavra real · 🟡 hipótese · 🔴 lacuna)
- `docs/conteudo/ESTUDO-GANCHOS.md` — 9 famílias que funcionam e 5 que afundam, com desempenho medido
- `docs/conteudo/DOSSIE-ROTEIROS.md` — cruzamento por player
- `docs/conteudo/banco-roteiros/` — ~65 fichas + players fechados (hormozi, daniel-dalen, matheus-gomes, gringos-ia, troncoso, seb-stritt)
- `docs/ecossistema/linha-editorial-e-calendario.md` — a grade fixa e a função de cada dia

## As regras que o squad inteiro obedece

1. **Identidade alcança; tática converte.** Peças de função diferente em dias diferentes.
2. **CTA troca alcance por comentário.** Peça de alcance não pede nada.
3. **Relato pessoal só com artefato na tela em até 15 segundos.**
4. **Número só como prova de terceiro**, com veículo e data, conferido na fonte primária.
5. **Material de terceiro não entra em vídeo publicado.** Arte original resolve.
6. **Roteiro é escrito para a boca** — sem tríade simétrica, sem paralelismo repetido, sem jargão.

## 🚫 Fontes proibidas

Não é preferência, é limite. **Material de mentoria de terceiros** (live, aula, transcrição de aluno de
outra marca) não entra como fonte de vocabulário, exemplo ou pauta — nem para pesquisa interna.
Fonte válida é a que é do Vitor: take dele, call dele, DM dele, pesquisa dele.

## ⚠️ Pendências que dependem do Vitor

`voz.md` e `cliente.md` foram fechados em 2026-09-23. O que ainda limita a qualidade:

| Pendência | Efeito enquanto falta |
|---|---|
| **Vocabulário real** — `cliente.md` tem **um** lead como fonte verificada | o roteiro escreve em cima de 1 caso + hipótese; export de DM e transcrição de call resolvem |
| **oferta vigente** — há 2 documentos de oferta no repositório | o agente não sabe para onde o conteúdo deve empurrar |
| **posicionamento vigente** — há 3 versões, algumas se contradizem | risco de escrever a partir de material superado |
| **beachhead** — `02-icp.md` fecha em Empresário, mas o acesso não veio | o roteiro pode mirar no perfil errado |

## Conflito conhecido

O squad `marketing` tem a agente **social-content-strategist (Nina)**, que também escreve roteiro de short-form,
e as fontes dela apontam para a categoria antiga da marca ("O Futuro Instalado"), superada pelo Brand Book v2.
Decisão a tomar: aposentar a Nina, ou reduzir o escopo dela a calendário e repurpose, deixando roteiro com o Téo.
