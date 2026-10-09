# task: fechar-player (estudo completo de um player)

**Agente:** analista-referencias · **Saída:** `docs/conteudo/banco-roteiros/players/<pasta>/` com `reels.json`, `resumo.json`, `classificacao.json` e `ESTUDO.md`
**Método validado em 08/10/2026** em 4 players (Elias, Luana, Tay, Matheus). Exemplo de referência: `players/tay-dantas/ESTUDO.md`.
**Substitui** o método antigo (3 a 5 vídeos + grade lida no navegador): com poucos vídeos e só os vencedores, tudo parece causa.

## Passos

1. **Coletar** (Apify + Groq; retoma sozinho se o Groq limitar, alternando dois modelos):
   ```
   python tools\roteiros\estudo_player.py <usuario_instagram> <pasta> [--limite 50] [--picos 3]
   ```
   Gera os 50 mais recentes (sem fixados), transcritos, e o `resumo.json`: medianas, por mês, testes reprovados,
   repostagens prováveis e os **picos de fora da janela já transcritos** (os fixados costumam ser os maiores da conta).

2. **Ler todas as transcrições**, ordenadas por views. Não pular os fracos: são eles que separam causa de estilo.

3. **Classificar cada vídeo** em `classificacao.json`:
   ```json
   {"usuario": "...", "repostagens": ["shortCode da cópia", ...], "picos": ["shortCode", ...],
    "videos": {"shortCode": ["formato", "tipo de gancho", "fecho"]}}
   ```
   - **Formato é o conceito**, não o tema ("Tendência → negócio", não "vídeo sobre a roça").
   - Conferir as repostagens: o resumo pega só as de abertura idêntica.

4. **Folhas de contato** dos maiores (obrigatório quando tela, inserção ou título fazem parte da mensagem):
   ```
   python tools\roteiros\estudo_folhas.py <pasta> [--top 6]
   ```
   Abrir cada folha e anotar: proporção rosto × tela, quando entra a inserção, título fixo, primeiro quadro.

5. **Escrever o `ESTUDO.md`** pelo modelo `players/_MODELO-ESTUDO.md`. As seções de análise vêm antes dos anexos.

6. **Gerar os anexos** (mediana por formato, os vídeos com abertura literal, roteiros completos + picos):
   ```
   python tools\roteiros\estudo_anexos.py <pasta> [--roteiros 10]
   ```
   Pode rodar de novo à vontade: só reescreve do marcador ANEXOS para baixo.

7. **Atualizar a síntese** `players/SINTESE-FORMATOS.md`: regra nova que o player confirma, ou regra que ele derruba
   (registrar o caso). Aberturas novas entram em `docs/conteudo/ESTUDO-GANCHOS.md`.

## Armadilhas já pagas

- **Abaixo de 500 views em perfil grande = trial reel reprovado**, não post normal (Elias: 16 de 50). Calcular a mediana
  também sem eles. Conferir no próprio Instagram antes de concluir qualquer coisa a partir deles.
- **Vídeo com menos de 3 dias** ainda está rodando: não entra na conclusão.
- **Só a janela de 50 perde os picos.** O vídeo de 1,66 milhão do Elias mudou duas conclusões.
- **Repostagem dias depois morre (1–2% da primeira), com ~2 meses volta.** Confirmado em 3 players.
- **Comparar dentro do perfil**, nunca número absoluto entre players (tamanho de conta e época pesam).
- **O público do player não é o ICP do Vitor.** Matheus fala com dev: dele vale o jeito de gravar, não o assunto.
- **Transcrição não é citação:** o Whisper troca palavras ("a vez você é a risco" = "avesso a risco").
- **Disco:** o C: já encheu no meio de um estudo. As ferramentas apagam os vídeos baixados; conferir espaço antes.

## Como o roteirista usa o estudo

Antes de escrever "no estilo de X": ler o esqueleto, a linguagem e 3 roteiros do Anexo C do player.
Do player vem **só o mecanismo**; expressões-assinatura dele não entram na boca do Vitor (`voz.md` decide).
