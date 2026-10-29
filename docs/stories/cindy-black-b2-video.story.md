# Cindy — criativo B2 com voz e takes existentes

Status: Ready for Review

## Objetivo
Entregar o criativo de aproximadamente 45 segundos solicitado em 21/10/2026: copy aprovada em
`docs/lancamento-black-recorde/roteiro-b2-curto.md`, narrada pela voz Cindy Batista
já criada no ElevenLabs, com takes locais usados nos vídeos anteriores da Cindy.

## Critérios de aceitação
- [x] Confirmar voz existente na conta sem recriar clone.
- [x] Gerar e salvar narração e alinhamento do B2.
- [x] Montar vídeo vertical com os takes existentes e legendas sincronizadas.
- [x] Conferir data 27/10/2026, 20h, evento ao vivo e gratuito e CTA grupo VIP.
- [x] Validar composição, imagens e arquivo final com áudio.
- [x] Atualizar handoff; manter publicação fora desta entrega.

## Decisões
- Copy de 123 palavras aprovada; usuário autorizou gerar voz clonada, montagem e edição. Nome Workshop Operação Black Recorde e promessa antes do CTA.
- Narração aprovada gerada em `b2-aprovado-45s.mp3`: 41,006 s, speed 0,92 no ElevenLabs. Edição usa atempo 0,94, preservando pitch, e respiro final para 45 s.
- Modelo eleven_multilingual_v2; stability 0,50; similarity 0,75; style 0.
- B2 original de 37,059 s preservado como alternativa; não usado na entrega final.
- Exportação direta FFmpeg/ASS devido ao baixo espaço inicial, preservando takes, textos e tempos do projeto HyperFrames.
- Limpeza de cache npm autorizada pelo usuário: 1,53 GB liberados; brutos preservados.
- Takes são imagens de apoio, sem sincronização labial artificial.
- Sistema visual do roteiro: Inter, navy e dourado; legenda por frase sem palavras pulando.

## File list
- `docs/stories/cindy-black-b2-video.story.md`
- `docs/lancamento-black-recorde/roteiro-b2-curto.md` (copy de 45 s aprovada e narrada)
- `docs/lancamento-black-recorde/voz/b2-cindy-v1.mp3` (local, ignorado)
- `docs/lancamento-black-recorde/voz/b2-cindy-v1-alignment.json` (local, ignorado)
- `docs/lancamento-black-recorde/voz/b2-cindy-v1-texto.txt` (local, ignorado)
- `videos/cindy-black-b2/` (composição e mídia)
- `videos/cindy-black-b2/build.py`
- `videos/cindy-black-b2/BRIEF.md`
- `videos/cindy-black-b2/design.md`
- `videos/cindy-black-b2/STORYBOARD.md`
- `docs/lancamento-black-recorde/voz/b2-aprovado-45s.mp3` e alinhamento/texto (locais, ignorados)
- `videos/cindy-black-b2/export_low_disk.py`
- `videos/cindy-black-b2/delivery.ass` e `delivery-concat.txt`
- `videos/cindy-black-b2/cindy-black-recorde-45s.mp4`
- `videos/cindy-black-b2/check-final.json`, `delivery-validation.json`, `delivery-contact.jpg` e frames de conferência
- `videos/cindy-black-b2/index.html`, `hyperframes.json`, `meta.json`, `timing.json`, `CREDITOS.md` e `assets/`
- `docs/sessions/CURRENT.md`

## Validação
- API confirmou clone existente e gerou a copy aprovada.
- HyperFrames check: runtime, layout e contraste aprovados; zero erros e oito avisos estruturais de organização.
- FFprobe: MP4 de 44,967 s, 1080×1920 a 30 fps, vídeo H.264 e áudio AAC, 34,6 MB.
- Decodificação integral do MP4 por FFmpeg concluída sem erros.
- Sete frames extraídos do MP4 final e inspecionados: takes, legendas, promessa, evento e CTA legíveis.
- `npm test`: handoff íntegro. `npm run lint` e `npm run typecheck`: scripts ausentes no package.json da raiz.
- Entrega local para revisão do usuário; nenhuma publicação realizada.

## Revisão de voz — 21/10/2026
- Usuário rejeitou a naturalidade da narração da primeira exportação.
- [x] Gerar duas amostras curtas cruas com o clone existente, speed 1 e estabilidade 0,50 / 0,35.
- [x] Usuário escolheu C e autorizou montagem final, ciente da naturalidade limitada.
- [x] Substituir narração e ajustar edição após escolha da voz.
- Arquivos: `docs/lancamento-black-recorde/voz/testes-naturalidade/A-normal-estabilidade-50.mp3`, `B-normal-estabilidade-35.mp3` e respectivos JSONs de parâmetros.

### Novo material de referência
- A/B rejeitadas pelo usuário; upload de áudio existente autorizado explicitamente.
- Amostra original conferida por hash: já estava na conta; sem reenvio duplicado.
- [x] Preparar referência alternativa com 65,3 s de gravação real de boas-vindas, sem filtros ou mudança de tempo.
- [x] Enviar ao ElevenLabs e criar clone de teste separado, preservando o anterior.
- [x] Gerar e validar arquivo da amostra C; sem afirmação de qualidade auditiva.
- Arquivos adicionais em `docs/lancamento-black-recorde/voz/testes-naturalidade/`: `referencia-cindy-boas-vindas-real.mp3` e JSON de proveniência, `clone-referencia-boas-vindas.json`, `C-clone-referencia-nova-normal.mp3`, parâmetros JSON e `C-validation.json`.

### Refino após melhora de semelhança
- Usuário confirmou melhora significativa em C; ainda falta naturalidade nas frases.
- Mantido clone novo. Testes D (v2, estabilidade 0,25, estilo 0,10) e E (v3, estabilidade 0,50), sem desaceleração.
- Arquivos: `voz/testes-naturalidade/D-conversa-v2.mp3`, `E-conversa-v3.mp3`, JSONs de parâmetros e validação, sob `docs/lancamento-black-recorde/`.
- Pendente: escolha de interpretação e geração completa.

## Entrega final C autorizada
- Usuário escolheu C e pediu render imediato, sem novos testes.
- [x] Narração completa com parâmetros C, velocidade original.
- [x] Legendas/cartelas sincronizadas e takes existentes reaproveitados.
- [x] Conferir e entregar MP4 final C: 45 s, 1080×1920, H.264/AAC; decodificação completa sem erros e frames inspecionados.
- Arquivos: `docs/lancamento-black-recorde/voz/b2-final-C.mp3`, `b2-final-C-alignment.json`, `b2-final-C-request.json`; `videos/cindy-black-b2/export_final_c.py`, `timing-C.json`, `delivery-C.ass`, `assets/voice-C.wav`, `assets/mix-C.wav`, `cindy-black-recorde-FINAL-C.mp4`.

Validação final: `videos/cindy-black-b2/validation-final-C.json`, `final-C-contact.jpg` e três frames `final-C-frame-*.jpg`.
