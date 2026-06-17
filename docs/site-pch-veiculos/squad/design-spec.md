# DESIGN SPEC — PCH Vintage

> Fase 3 do squad · Contribuições: **Leo (creative-director)**,
> **web-designer**, **motion-designer**, **@ux-design-expert (Uma)** · 2026-06-16
> Entrada: `squad/research.md`, `squad/copy.md` · Saída para: Fase 4 (Arquitetura).

---

# PARTE A — DIREÇÃO CRIATIVA (Leo · creative-director)

## A1. Conceito: "Showroom Noturno"

O site é um **showroom à noite, iluminado por neon**. O visitante entra num
ambiente escuro e premium onde cada carro clássico está sob um foco de luz rosa —
como uma joia numa vitrine. Silencioso, sofisticado, cinematográfico. A escuridão
não é vazia: é palco. O carro é a estrela; o neon é o brilho; a história é a alma.

**Antítese de mercado:** os concorrentes são showrooms diurnos, brancos,
fluorescentes, genéricos. A PCH é o after-hours exclusivo — onde colecionadores
de verdade vão.

## A2. Princípios de Arte

1. **A foto manda.** Imagem grande, contrastada, protagonista. Texto nunca compete.
2. **Escuridão com profundidade.** Nada de preto chapado — gradientes radiais sutis
   nos cantos, vinheta leve, sensação de "luz vindo de algum lugar".
3. **Neon com propósito.** O rosa pontua (letreiro, CTA, hover, linhas), não inunda.
4. **Dourado = procedência.** Detalhe premium só nos selos de originalidade/raridade.
5. **Respiro.** Muito espaço negativo. Curadoria, não catálogo lotado.
6. **Cinema, não banner.** Transições suaves, brilho que pulsa devagar, elegância.

## A3. Moodboard (descritivo)

- Garagem/showroom escuro com um único carro sob luz neon rosa.
- Reflexos de neon no capô polido; chão escuro espelhado.
- Tipografia condensada gigante em néon (estilo letreiro de oficina vintage premium).
- Detalhes cromados brilhando no escuro; faróis redondos acesos.
- Paleta: preto carvão, rosa choque luminoso, toques de dourado champanhe.
- Referência de mood: trailer de filme + galeria de arte + garagem de colecionador.

## A4. Direção de Fotografia (para o dono fotografar os carros dele)

- Fundo escuro/neutro (garagem, parede lisa, noite) — o carro se funde ao tema.
- 3/4 frontal como capa; depois: lateral, traseira, motor, interior, detalhes
  (emblema, rodas, painel, hodômetro).
- Mínimo recomendado: **6–8 fotos por carro**. Luz lateral valoriza a lataria.
- Evitar: fundo bagunçado, sol estourado, foto torta de celular na rua.

> *(As 6 fotos demo atuais já seguem o espírito: clássicos com presença.)*

---

# PARTE B — DESIGN SYSTEM & LAYOUT (Vera · web-designer)

## B1. Design Tokens

```css
/* Cores (das brand guidelines) */
--bg:        #0a0a0c;   --bg-2:   #121217;   --bg-3: #1a1a22;
--neon:      #ff1f8f;   --neon-soft: #ff66b3;
--gold:      #e8c479;
--text:      #f5f5f7;   --muted:  #9a9aa5;
--line:      rgba(255,255,255,.08);
--ok:        #36d399;   --warn:   #ff5a5a;

/* Profundidade */
--glow-neon: 0 0 24px rgba(255,31,143,.55);
--shadow-card: 0 24px 60px rgba(0,0,0,.55);
--radius: 16px;   --radius-sm: 10px;

/* Tipografia */
--font-display: 'Anton','Archivo Black',sans-serif;  /* letreiro/headlines */
--font-body:    'Inter','Manrope',system-ui,sans-serif;

/* Ritmo (escala de espaçamento 4px) */
--s1:4px --s2:8px --s3:12px --s4:16px --s5:24px --s6:32px --s7:48px --s8:64px --s9:96px
```

- **Escala tipográfica:** H1 `clamp(2.5rem,7vw,5.5rem)` · H2 `clamp(1.8rem,4vw,3rem)`
  · H3 `1.4rem` · corpo `1rem/1.6` · label `.8rem` uppercase tracking.
- **Letreiro "PCH":** `--font-display`, uppercase, cor `--neon` + `text-shadow:
  var(--glow-neon)`.
- **Grid:** container máx `1200px`, gutter 24px. Cards: `repeat(auto-fill,
  minmax(300px,1fr))`.

## B2. Componentes

**Header (sticky, translúcido)**
- Logo "PCH" neon à esquerda · menu (Início · Estoque · Sobre · Contato) ·
  fundo `rgba(10,10,12,.7)` + `backdrop-filter: blur(12px)` + borda inferior `--line`.
- Mobile: logo + menu hambúrguer → drawer escuro full-height.

**Card de carro** (o componente mais importante)
```
┌───────────────────────────┐
│  [FOTO 16:10 — capa]       │  ← imagem domina; zoom suave no hover
│  ⟨selos no canto sup.⟩     │  ← DESTAQUE(rosa) / ORIGINAL(dourado)
├───────────────────────────┤
│  Ford Mustang Fastback     │  ← H3, peso 800
│  4.7 V8 Coupé              │  ← versão, --muted
│  1968 · 86.000 km · SP     │  ← meta line, tabular-nums
│  R$ 520.000                │  ← preço, --neon, destaque
│  [ Ver detalhes ]          │  ← botão outline neon
└───────────────────────────┘
```
- Fundo `--bg-2`, borda `--line` → no hover borda `--neon` + `--shadow-card` +
  leve `translateY(-4px)`.

**Filtros (estoque):** barra horizontal de selects estilizados (Marca · UF ·
Preço) + campo de busca + ordenação. Mobile: viram um botão "Filtrar" que abre
painel deslizante (bottom sheet).

**Galeria (detalhe):** foto grande (capa) + tira de miniaturas clicáveis abaixo;
clique abre lightbox escuro. Fallback "Foto em breve" = placeholder neon com o
nome do modelo quando `fotos` está vazio.

**Selos:** pílulas pequenas. `DESTAQUE`/`BLINDADO` fundo rosa translúcido + texto
rosa; `ORIGINAL`/`RESTAURADO` borda dourada + texto dourado.

**Botão flutuante de contato:** canto inferior direito, círculo/pílula neon com
glow pulsante suave, texto "Falar conosco" → `contata.me/pchveiculos`. Aparece
após sair do hero.

**Botões:** primário = preenchido rosa com glow; secundário = outline rosa;
terciário = texto com underline animado.

**Footer:** fundo `--bg-2`, logo neon, tagline "Clássicos com procedência",
@pchveiculos, "Atendemos todo o Brasil", link de contato, gradiente sutil no topo.

## B3. Layouts por página (wireframes anotados)

### HOME (`index.html`)
1. **Header** sticky.
2. **Hero** full-height: fundo escuro com gradiente radial rosa atrás do letreiro;
   H1 "Clássicos que contam histórias." + subheadline + 2 CTAs (`Ver coleção`
   primário, `Falar com a PCH` secundário). Scroll hint embaixo.
3. **Destaques**: título "Destaques da coleção" + grid de 3–4 cards (carros com
   `destaque:true`) + link "Ver estoque completo →".
4. **Quem Somos (resumo)**: 2 colunas — texto institucional + número/prova
   (anos de mercado / +X clássicos). Fundo `--bg-2`.
5. **Faixa CTA**: "Achou o seu clássico?" + botão WhatsApp.
6. **Footer**.

### ESTOQUE (`estoque.html`)
1. Header.
2. **Cabeçalho da página**: "A coleção" + apoio.
3. **Barra de filtros** (Marca · UF · Preço · Busca · Ordenar).
4. **Grid** de todos os carros (render via `carros.js`). Estado vazio elegante.
5. Footer.

### DETALHE (`veiculo.html?id=`)
1. Header + breadcrumb ("← A coleção").
2. **Galeria** (capa grande + miniaturas) à esquerda/topo.
3. **Painel de info** à direita/abaixo: título + selos · preço grande neon ·
   bloco de specs (Ano/Km/Motor/Câmbio/Cor/UF) · **CTA "Tenho interesse"** com
   glow · reforço de confiança.
4. **História do carro**: seção larga abaixo, título "A história deste [modelo]".
5. **Relacionados**: "Outros clássicos" — 3 cards.
6. Footer.

### SOBRE (`sobre.html`)
1. Header.
2. **Hero curto**: "Mais que uma revenda. Uma paixão."
3. **Texto institucional** + **Missão** + **Valores** (4 cards com ícone).
4. Faixa CTA + Footer.

## B4. Responsivo (mobile-first)

- **Base (mobile):** 1 coluna; menu drawer; filtros em bottom sheet; hero com
  H1 reduzido; galeria do detalhe vira carrossel swipe; botão flutuante visível.
- **≥ 720px:** grid 2 colunas; menu horizontal.
- **≥ 1024px:** grid 3 colunas; detalhe em 2 colunas (galeria | info).
- Toque mínimo 44px; contraste AA garantido (texto claro sobre fundo escuro).

## B5. Decisões justificadas pela jornada
- Foto dominante no card → no nicho, foto é o gatilho nº1 (pesquisa F1).
- Detalhe em 2 colunas (galeria + CTA fixo ao lado) → mantém o "Tenho interesse"
  sempre à vista no pico de desejo.
- UF visível, cidade ausente → regra de negócio (forçar contato).
- Dark + foco neon → diferenciação de mercado + foto valorizada.

---

# PARTE C — MOTION & MICRO-INTERAÇÕES (Mo · motion-designer)

## C1. Tokens de movimento
```css
--ease-out: cubic-bezier(.16,1,.3,1);   /* entradas */
--ease:     cubic-bezier(.4,0,.2,1);    /* micro-interações */
--t-micro:  .3s;   --t-enter: .6s;
```

## C2. Hero
- **Entrada (load):** letreiro `opacity 0→1` + `translateY(16px→0)` em `--t-enter`
  `--ease-out`, stagger 80ms (letreiro → subheadline → CTAs).
- **Glow do letreiro (loop):** `text-shadow` pulsa entre `0 0 18px` e `0 0 34px`
  rosa, `@keyframes` 3.5s ease-in-out infinite alternate (sutil, lento).
- **Scroll hint:** seta com bob vertical 1.5s infinite.

## C3. Scroll reveal (seções e cards)
- IntersectionObserver (`threshold .15`) adiciona `.in` → de
  `opacity:0; translateY(24px)` para visível em `--t-enter --ease-out`.
- **Cards em grid:** stagger de 60ms por card (delay incremental). Revela uma vez.

## C4. Card de carro (hover/tap)
- Container: `translateY(-4px)` + borda `--neon` + `--shadow-card`, `--t-micro --ease`.
- Foto interna: `scale(1.06)` com `overflow:hidden` no wrapper, `--t-micro`.
- Botão "Ver detalhes": fundo preenche da esquerda→direita no hover.
- Mobile: efeitos de hover viram estado `:active` (feedback ao toque).

## C5. Galeria / Lightbox (detalhe)
- Troca de foto principal: `crossfade` (opacity) 250ms; miniatura ativa ganha
  borda neon.
- Lightbox: fundo escurece (`backdrop` fade 200ms) + imagem `scale(.96→1)` 300ms.
- Swipe no mobile com transição de slide.

## C6. Botão flutuante de contato
- Surge após o hero: `opacity/scale(.8→1)` 300ms.
- **Pulse de atenção:** halo `box-shadow` expande e some, 2.4s infinite (discreto).
- Hover: `scale(1.05)` + glow intensifica.

## C7. Header on-scroll
- Ao rolar > 40px: header reduz padding e aumenta blur/opacidade do fundo,
  transição 250ms. Logo levemente menor.

## C8. Botões e microcopy
- Primário hover: `translateY(-2px)` + glow +20%, `--t-micro`.
- Links de texto: underline cresce de 0→100% (`transform: scaleX`).
- Selects de filtro: borda → neon no focus.

## C9. Performance & Acessibilidade
- Animar **apenas** `transform` e `opacity` (GPU). Nunca `width/height/top/left`.
- `will-change` só onde necessário; remover após animar.
- **Obrigatório:**
```css
@media (prefers-reduced-motion: reduce){
  *{animation:none!important;transition:none!important;scroll-behavior:auto!important}
  .reveal{opacity:1!important;transform:none!important}
}
```
- Tudo funciona sem JS/animação (conteúdo visível por padrão; `.reveal` só
  esconde quando JS confirma suporte).

---

## Gate G3 — Veredito (aprovação do Creative Director)
✅ **APROVADO por Leo.** Conceito "Showroom Noturno" coeso da arte ao movimento,
fiel ao briefing dark/neon, mobile-first, com acessibilidade. Design system e
specs prontos para implementação.

**Handoff → Fase 4 (@architect):** transformar este spec em arquitetura técnica
(estrutura de arquivos, render via `carros.js`, performance, evolução Supabase).
