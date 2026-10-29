# Fontes e método — Fábio Hansen

**Data de referência: 28/10/2026, America/Sao_Paulo.** Os dados descrevem essa coleta. [Estudo](ESTUDO.md) · [Inventário com links de cada Reel](ANEXOS.md).

## Fontes primárias consultadas

- [Reel enviado pelo usuário](https://www.instagram.com/reel/DdbwbqdKmil/): autoria, vídeo, legenda e metadados públicos; ficha individual no banco de referências.
- [Perfil @fabiohansen](https://www.instagram.com/fabiohansen/): bio, número de seguidores e link de consultoria, coletados pelo Apify. Resumo em `perfil.json`.
- Os 16 Reels listados em `ANEXOS.md`: métricas públicas, fala transcrita automaticamente e material visual. Consolidados em `reels.json`.
- [Página PERCEP](https://percep.hansendigital.com.br/): HTML e lógica de interface consultados sem preencher ou enviar formulário. Arquivo de trabalho local `tools/roteiros/work/estudo/fabiohansen/percep.html`. O estudo não publica endpoints de captura ou dados de leads.
- Para a aplicação à marca: `docs/ecossistema/brand-book-marca-pessoal.md`, versão vigente; as informações de audiência antigas desse documento não foram tratadas como contagem atual.

Pesquisa web trouxe homônimos acadêmicos. Nenhuma informação deles foi usada para descrever este criador.

## Coleta e análise

Comandos executados na raiz do repositório:

```powershell
python tools/roteiros/colher.py https://www.instagram.com/reel/DdbwbqdKmil/ --lang pt
python tools/roteiros/estudo_player.py fabiohansen fabio-hansen --limite 50 --picos 3 --lang pt
python tools/roteiros/estudo_folhas.py fabio-hansen --top 6
python docs/conteudo/banco-roteiros/players/fabio-hansen/coletar_folhas_controle.py
python docs/conteudo/banco-roteiros/players/fabio-hansen/auditar_dados.py
python docs/conteudo/banco-roteiros/players/fabio-hansen/gerar_anexos.py
```

O coletor retornou 16 vídeos apesar da tentativa de janela maior. Nova chamada ao scraper genérico para ampliar a base foi recusada por cobrança, HTTP 402. A coleta de perfil separada funcionou. Nenhum pico histórico independente fora dessa janela foi obtido. Não assumir que os 16 sejam os únicos posts do perfil.

Todos os textos dos 16 vídeos foram lidos; cada publicação recebeu formato, tipo de entrada e fecho. Identificadas duas famílias de versões semelhantes. Seis maiores e três controles tiveram folhas de contato inspecionadas. Quadros amostrados não equivalem a uma análise integral de áudio, música ou ritmo de todos os cortes.

## Cálculo e unidades

- Mediana bruta: 16 publicações, 1.905 views.
- Base com pelo menos três dias de calendário: 13 publicações, 2.675 views. Três posts do dia foram separados; o limiar não garante estabilização do alcance.
- Sensibilidade às versões: retirando a segunda publicação do mesmo dia sobre primeira impressão, ficam 12 e mediana 2.846,5. Não é substituto de uma amostra maior.
- Concentração: soma das views dos três maiores dividida pela soma das views dos 16 = 91,8176%.
- Duração: metadados arredondados do coletor; mediana bruta 57 s. Tempos do roteiro são aproximados, provenientes de ASR.
- Cada Reel é uma publicação; versões semelhantes não são ideias independentes. Views não equivalem a pessoas únicas, vendas ou seguidores adquiridos.

`auditar_dados.py` gera `resumo-auditado.json` e `classificacao.json`. O `resumo.json` original é artefato automático preservado, **não é a base interpretativa do dossiê**: sua convenção de classificar contagens baixas como testes não pode ser inferida destes dados. O gerador de anexos desta pasta usa o resumo auditado, evita essa inferência e não reproduz roteiros integrais.

## O que não foi possível verificar

Retenção, alcance único, origem do tráfego, seguidores por publicação, compartilhamentos, salvamentos, gastos, eventual condição de trial, vendas, conversão do quiz, atendimento efetivo, preço e histórico completo. Idades dos posts diferentes impedem comparar as contagens como se fossem resultados no mesmo prazo.

O dossiê distingue observação, interpretação e hipótese de teste. Não atribui causalidade ao gancho, edição ou formato a partir de um único pico.
