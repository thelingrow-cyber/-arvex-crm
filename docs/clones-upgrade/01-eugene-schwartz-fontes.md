# Upgrade de Clone #1 — Eugene Schwartz

> Data: 2026-07-26 · Objetivo: elevar o clone de **consultivo** (destilado de resumos web) para **fonte primária**, no padrão Tay/Hormozi.
> Motivo da prioridade: o Schwartz sustentou sozinho o veredito do roundtable de 2026-07-25 sendo o clone menos verificado da mesa. Copy vira dinheiro direto.

## Situação atual

`.claude/clones/eugene-schwartz/sources/index.md` declara honestamente:

> Breakthrough Advertising (1966) — **PDF a ser fornecido pelo Vitor. Pendente de ingestão.**
> Os exemplos de headline são tratados como **ilustrativos**, não como transcrição literal verificada.

Os **frameworks** (5 níveis de consciência, 5 estágios de sofisticação, desejo de massa e suas 3 dimensões, mecanismo, gradualização, verbalização, redefinição) são fiéis ao método documentado. O que falta é a **voz literal** e os **exemplos verificados**.

## O universo é pequeno — só 3 fontes primárias existem

Segundo o arquivo de Michael Senoff (hardtofindseminars.com), que é quem detém e comercializa o acervo:

> "The genius of Gene Schwartz has only been documented in three surviving publications: **Breakthrough Advertising**, the **Rodale Workshop (video)** and this **transcript** [Phillips Publishing]."

Isso é ótima notícia: o alvo é finito. Não é "pesquisar Schwartz para sempre" — são três aquisições.

---

## Fonte 1 — *Breakthrough Advertising* (1966) 📕 PRIORIDADE MÁXIMA

O corpo canônico. Todos os frameworks do clone saem daqui; o que falta é a linguagem literal e os exemplos.

| Via | Onde | Observação |
|---|---|---|
| Edição oficial atual | `breakthroughadvertisingbook.com` (ed. Brian Kurtz, 2017) | Edição autorizada, cara historicamente |
| Amazon | ISBN `9780998503509` (Kurtz, 2017) · `9780887232985` (Edelston) | |
| Usado | AbeBooks — 27 resultados listados | Edições antigas costumam ser caras (livro é cult) |

**O que fazer com ele:** extrair texto e ingerir em blocos.
```
/mingw64/bin/pdftotext -enc UTF-8 -layout "breakthrough-advertising.pdf" "out.txt"
```
(o leitor de PDF padrão falha neste ambiente — falta `pdftoppm`; o método acima já está registrado no `sources/index.md` do clone)

**Destino:** `docs/clone-eugene-schwartz-pesquisa/`

---

## Fonte 2 — Seminário Phillips Publishing (8/out/1993, 90 min) 🎙️ MELHOR CUSTO-BENEFÍCIO

Palestra de 90 minutos para a Phillips Publishing, com copywriters A-list na plateia. É o Schwartz **ensinando o método na própria voz** — o que o livro não dá, porque o livro é tratado, não fala.

| Via | Preço | O que vem |
|---|---|---|
| `scientificadvertising.com/books/schwartztpp/` | **~US$ 19,97** | Transcrição da palestra ⭐ **começar por aqui** |
| `hardtofindseminars.com/Eugene_Schwartz_Speech.htm` | US$ 597 | 3 MP3s (90 min completos) + transcrição de 31 páginas + bônus |
| Podcast "Hardtofindseminars.com Copywriting University" | possivelmente grátis | Episódio "Eugene Schwartz Copywriting Seminar - Part One" aparece no player.fm e Apple Podcasts — **verificar se as 3 partes estão livres** |
| Fóruns | grátis | Warrior Forum tem thread sobre a palestra; PDFCoffee e Scribd listam versões |

**Ordem recomendada:** checar o podcast primeiro (se as 3 partes estiverem livres, o áudio sai de graça) → se não, comprar a transcrição de US$ 19,97 → o pacote de US$ 597 só se o acervo bônus interessar por si.

**Se conseguir o áudio:** o pipeline já existe nesta máquina. WhisperFlow (faster-whisper local, grátis) transcreve sem custo. Áudio → transcrição → re-destilação.

**Temas cobertos na palestra** (da página de vendas, útil para saber o que esperar):
conexão com a audiência · metodologia de trabalho intenso · descobrir em vez de criar · extrair apelos do produto · desejos ocultos do leitor · técnica de "entrevistar o produto" · geração subconsciente de ideias · previsão de eficácia da copy · estratégia de headline · construção de claim e prova · canalização da demanda de mercado · princípios de layout · rejuvenescimento de copy · estabelecimento de credibilidade.

---

## Fonte 3 — Rodale Workshop (vídeo) 📹 LOCALIZAR

A terceira fonte sobrevivente. Ainda não localizei disponibilidade pública — pesquisa pendente.

**Pesquisa a fazer:** "Rodale Schwartz workshop video", acervo do Senoff, arquivos da Rodale Press, Boardroom/Bottom Line (Marty Edelston publicou o livro).

---

## Outros livros do Schwartz (contexto, não fonte de copy)

Ele escreveu **10 livros**. Os relevantes:

| Livro | Ano | Serve para |
|---|---|---|
| *The Brilliance Breakthrough* | 1994 | Como escrever com clareza — método de escrita, complementa BA |
| *How to Double Your Power to Learn* | 1965 | Aprendizado; contexto do método de trabalho dele |
| *Confessions of a Poor Collector* | — | Biografia/arte; contexto de personalidade, baixa prioridade |

Os três são **contexto**, não fonte primária de copy. Não bloqueiam o upgrade.

---

## Sequência de execução

1. **Vitor:** verificar se o podcast do Senoff libera as 3 partes de graça.
2. **Vitor:** se não, comprar a transcrição (~US$ 19,97) — é o melhor retorno por dólar do projeto inteiro de clones.
3. **Vitor:** conseguir o PDF de *Breakthrough Advertising* e colocar em `docs/clone-eugene-schwartz-pesquisa/`.
4. **Orion:** ingerir (pdftotext em blocos / transcrição), re-destilar os 4 clone-files com citação literal verificada, atualizar `sources/index.md` removendo a nota de pendência.
5. **Orion:** reescrever o prompt de ativação com a voz literal.
6. **Validação:** re-rodar a mesa do roundtable de 2026-07-25 só com o Schwartz atualizado e comparar o parecer. Se a recomendação mudar, o upgrade valeu; se não mudar, o clone consultivo já era bom o suficiente — e isso também é informação.

## Fontes desta pesquisa

- https://www.scientificadvertising.com/books/schwartztpp/
- https://www.hardtofindseminars.com/Eugene_Schwartz_Speech.htm
- https://www.hardtofindseminars.com/ES.html
- https://www.warriorforum.com/copywriting/732264-heres-must-have-eugene-schwartz-lecture-philips-publishing.html
- https://www.goodreads.com/author/show/285754.Eugene_M_Schwartz
- https://breakthroughadvertisingbook.com/
- https://www.youtube.com/watch?v=OOhgr6sbstU (comentário sobre o método, não fonte primária)
