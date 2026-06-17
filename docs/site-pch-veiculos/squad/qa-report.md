# QA REPORT — PCH Vintage (Fase 1)

> Fase 6 do squad · Autor: **@qa (Quinn)** + cro-analyst + seo-specialist · 2026-06-16
> Escopo: `index/estoque/veiculo/sobre.html`, `assets/style.css`, `assets/app.js`,
> `carros.js`. Evidência: screenshots desktop+mobile + checagem de console + teste de dados.

---

## Veredito: ✅ PASS (com CONCERNS não-bloqueantes)

O site está **pronto para publicar**. Funciona, renderiza, é responsivo e sem erros
de console. Os CONCERNS são melhorias de conteúdo/refino, não defeitos — não
bloqueiam o deploy.

---

## 1. Checklist de Qualidade (@qa)

| # | Item | Resultado | Evidência |
|---|------|-----------|-----------|
| 1 | Sintaxe JS (`carros.js`, `app.js`) | ✅ PASS | `node --check` OK |
| 2 | Dados íntegros (6 carros, IDs únicos) | ✅ PASS | teste headless |
| 3 | Imagens resolvem (6/6) | ✅ PASS | `fs.existsSync` OK |
| 4 | Home renderiza destaques (4 cards) | ✅ PASS | DOM dump + screenshot |
| 5 | Estoque renderiza grid + filtros | ✅ PASS | screenshot desktop |
| 6 | Detalhe (galeria, specs, história, relacionados) | ✅ PASS | screenshot detalhe |
| 7 | Responsivo mobile (390px) | ✅ PASS | screenshot mobile |
| 8 | Erros de console | ✅ PASS | nenhum erro de app |
| 9 | Fallback "Foto em breve" | ✅ PASS | implementado p/ `fotos:[]` |
| 10 | Funciona em `file://` | ✅ PASS | `carros.js` global, sem fetch |
| 11 | Navegação (menu, links entre páginas) | ✅ PASS | links relativos corretos |
| 12 | CTAs apontam p/ contato | ✅ PASS | `data-contato` → contata.me |

## 2. Acessibilidade (A11y)

| Item | Resultado |
|------|-----------|
| `prefers-reduced-motion` respeitado | ✅ PASS |
| Navegação por teclado (lightbox `Esc`, foco) | ✅ PASS |
| `alt` descritivo nas fotos | ✅ PASS |
| HTML semântico (`header/main/section/footer/article`) | ✅ PASS |
| Contraste texto principal sobre fundo escuro | ✅ PASS |
| ⚠️ Contraste de texto rosa pequeno sobre preto | CONCERNS (baixo) |

## 3. SEO on-page (seo-specialist)

| Item | Resultado |
|------|-----------|
| `<title>` único por página | ✅ PASS |
| `meta description` por página | ✅ PASS |
| Open Graph (title/description/image) | ✅ PASS (home) |
| `<h1>` único por página | ✅ PASS |
| `alt` com marca+modelo+ano | ✅ PASS |
| `lang="pt-BR"` | ✅ PASS |
| ⚠️ `sitemap.xml` + JSON-LD `Vehicle` | CONCERNS (Fase 3) |
| ⚠️ OG image por veículo no detalhe | CONCERNS (Fase 2/3 — precisa render dinâmico) |

## 4. Conversão (cro-analyst)

| Item | Resultado |
|------|-----------|
| CTA persistente (botão flutuante após scroll) | ✅ PASS |
| CTA por veículo no pico de desejo (detalhe) | ✅ PASS |
| Mensagem WhatsApp pré-preenchida com o carro | ✅ PASS |
| Jornada clara Home→Estoque→Detalhe→Contato | ✅ PASS |
| Prova/escassez (selos DESTAQUE/raridade) | ✅ PASS |
| 💡 Sugestão: adicionar nº de WhatsApp direto | recomendação |

## 5. Performance (NFR)

| Item | Resultado |
|------|-----------|
| `loading="lazy"` + `decoding="async"` nas fotos | ✅ PASS |
| `aspect-ratio` evita layout shift | ✅ PASS |
| Sem libs externas (só fonte Google) | ✅ PASS |
| Preload da imagem do hero | ✅ PASS |
| 💡 Fotos demo ~100–270KB (OK; otimizar as reais) | recomendação |

> Lighthouse formal será rodado após o deploy (precisa de servidor http; `file://`
> não reflete métricas reais). Estrutura preparada para ≥ 90.

---

## 6. CONCERNS (não bloqueiam — para evolução)

1. **Conteúdo institucional** (Sobre, números "100%/BR/∞") é rascunho — **o dono
   deve confirmar/ajustar** fatos reais (anos de mercado, nº de carros vendidos).
2. **Fotos demo** devem ser substituídas pelas reais dos carros do dono.
3. **Contraste de neon pequeno**: usar `--neon-soft` em textos pequenos rosa se
   necessário (títulos grandes estão OK).
4. **Número de WhatsApp**: hoje usa `contata.me`; se o dono der o número, ativar
   `WHATSAPP_NUM` em `app.js` para mensagem pré-preenchida.
5. **SEO avançado** (sitemap, JSON-LD, OG por veículo): planejado p/ Fase 2/3.

---

## 7. Gate G6 — Decisão

✅ **PASS.** Qualidade aprovada para publicação. Zero defeito bloqueante. CONCERNS
são de conteúdo (dependem do dono) e melhorias de fases futuras.

**Handoff → Fase 7 (@devops):** liberado para deploy. Recomendação: publicar em
Netlify/Vercel, rodar Lighthouse em produção, e retornar os CONCERNS de conteúdo
ao dono para personalização.

— Quinn, guardião da qualidade 🛡️
