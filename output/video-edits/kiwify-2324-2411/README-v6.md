# Kiwify — revisão V6, tratamento de imagem

V6 mantém integralmente a montagem da V5: duração, cortes, inserts, legendas,
flashes, trilha e mixagem. A única mudança editorial é o tratamento de imagem.

## Tratamento aplicado nos planos do podcast

- redução leve de ruído e macroblocos antes da ampliação (`hqdn3d`);
- upscale 504×896 ou 450×800 para 1080×1920 com spline36;
- redução discreta do excesso de verde nos médios e realces;
- contraste moderado sem esmagar a camisa preta;
- nitidez adaptativa leve (`CAS 0.22`), evitando halos e pele artificial;
- render novamente a partir da fonte, H.264 High, CRF14, preset slow/tune film.

A cena pública da Guday recebe apenas redução de ruído e nitidez leves. Os motions
permanecem sem tratamento destrutivo. O arquivo não passa por reconstrução facial ou
super-resolução generativa, que poderia inventar textura e variar entre quadros.

## Limite da fonte

O arquivo completo do YouTube é 1920×1080/H.264, mas tem vídeo de aproximadamente
1,91 Mbps. O recorte de rosto usa somente parte desses pixels. O tratamento melhora
limpeza, cor, contraste e preservação na nova exportação, mas não recupera detalhe de
câmera ausente. Um master original continua sendo a única melhoria estrutural.

## Reprodução e validação

```powershell
node output/video-edits/kiwify-2324-2411/build-v5.cjs --v6 --render
node output/video-edits/kiwify-2324-2411/check-v3.cjs --v6
```

Arquivos auxiliares: `captions-v6.ass/.srt`, `filter-v6.ffmpeg`,
`render-args-v6.json`, `edit-manifest-v6.json`, `validation-v6.json` e `qa-v6.jpg`.
V1–V5 e a fonte permanecem preservadas.
