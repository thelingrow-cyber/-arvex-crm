# ARCHITECTURE — PCH Vintage

> Fase 4 do squad · Autor: **@architect (Aria)** · 2026-06-16
> Entrada: `squad/design-spec.md`, `PLANO.md` · Saída para: Fase 5 (Implementação).

---

## 1. Princípio Arquitetural

**Tecnologia chata onde dá, evolutiva onde importa.** Fase 1 é um site estático
vanilla (zero build, zero dependência, abre em `file://`, sobe em qualquer host).
O único ponto "inteligente" é o **contrato de dados** — desenhado para migrar
para Supabase na Fase 2 sem reescrever o front.

**Por quê vanilla:** o dono edita conteúdo, não código; o site é leve e rápido
(crucial p/ tráfego mobile do Instagram); custo zero; máxima portabilidade.

---

## 2. Estrutura de Arquivos

```
site-pch-veiculos/
├── index.html          # Home
├── estoque.html        # Vitrine + filtros
├── veiculo.html        # Detalhe (?id=N)
├── sobre.html          # Quem somos / missão / valores
├── carros.js           # CATÁLOGO (fonte de dados — o dono edita)
├── assets/
│   ├── style.css       # design system (tokens) + componentes + responsivo
│   └── app.js          # render, filtros, galeria, reveal, helpers
├── fotos/              # imagens dos carros (6 clássicos demo já presentes)
├── favicon.svg
├── PLANO.md · ESCALONAMENTO.md · README.md
└── squad/              # entregáveis do squad (research, copy, design, arch, qa)
```

**Decisão:** CSS e JS **compartilhados** entre as 4 páginas (um `style.css`, um
`app.js`). Header/footer replicados como HTML em cada página (sem build/includes)
— simples e suficiente para 4 páginas.

---

## 3. Contrato de Dados (a peça que garante evolução)

`carros.js` expõe um array global `CARROS`. **Cada objeto é o contrato** — o
mesmo shape será uma linha na tabela `carros` do Supabase na Fase 2.

```js
{
  id,            // estável (gerado: ver §4). chave do detalhe ?id=
  marca, modelo, versao,
  ano,           // string '1968' | '1968/1969'
  km,            // number
  preco,         // number (centavos? NÃO — reais inteiros, formatado no render)
  uf,            // string 2 letras (regra: nunca cidade)
  blindado,      // boolean → selo
  destaque,      // boolean → home
  // evolução prevista (opcionais, já suportar no render se presentes):
  cor, cambio, motor, condicao,  // 'original' | 'restaurado'
  historia,      // string
  fotos          // string[]  (1ª = capa; [] = placeholder "Foto em breve")
}
```

**Camada de acesso a dados (abstração):** o `app.js` nunca lê `CARROS`
diretamente nas views. Usa funções:
```js
getCarros()        // hoje: return CARROS;  amanhã: await fetch Supabase
getCarroById(id)
```
> Isolar o acesso num único ponto é o que permite trocar a fonte (arquivo →
> Supabase) na Fase 2 mexendo em **uma função**, não em 4 páginas.

### ID estável
Como o dono não vai gerar IDs manualmente, derivamos um **slug determinístico**:
`slugify(marca-modelo-ano)` + índice de desempate. Ex.: `ford-mustang-fastback-1968`.
O detalhe abre por `veiculo.html?id=ford-mustang-fastback-1968`. Na Fase 2 o slug
vira coluna única (ou usa o uuid do banco, com redirect do slug).

---

## 4. Render & Roteamento

- **Estoque/Home:** `app.js` lê `getCarros()`, aplica filtros/ordenação, gera os
  cards via template string e injeta no grid. Cards `destaque:true` na home.
- **Detalhe:** `veiculo.html` lê `?id=` → `getCarroById(id)` → preenche galeria,
  specs, história, CTA com mensagem pré-preenchida. Se id inválido → estado
  "carro não encontrado" + link pro estoque.
- **Filtros (estoque):** estado em memória + refletido na URL (`?marca=&uf=&q=`)
  para permitir compartilhar/voltar. Sem framework — `URLSearchParams`.
- **CTA WhatsApp:** monta `https://contata.me/pchveiculos` (e, se o dono der um
  número, `https://wa.me/<num>?text=` com a mensagem pré-preenchida da copy C6).

---

## 5. Performance (NFR — mobile é prioridade)

| Técnica | Aplicação |
|---------|-----------|
| `loading="lazy"` + `decoding="async"` | todas as imagens de carro |
| `width/height` nas imgs | evita layout shift (CLS) |
| `aspect-ratio` nos cards | reserva espaço da foto |
| Imagens otimizadas | redimensionar/comprimir (≤ ~250KB; as demo já estão) |
| CSS/JS inline-críticos pequenos | sem libs externas; fontes via `font-display:swap` |
| IntersectionObserver | reveal sem custo de scroll-jank |
| `<link rel="preload">` na foto do hero | LCP rápido |

**Meta:** Lighthouse ≥ 90 (Performance/SEO/Best Practices/A11y) — validado na F6.

---

## 6. SEO & Compartilhamento (base p/ seo-specialist na F6)

- Meta `title`/`description` por página (copy C8); Open Graph + Twitter Card com
  foto destaque (link bonito no Instagram/WhatsApp).
- HTML semântico (`<header><main><section><article><footer>`), `alt` descritivo
  nas fotos (`Marca Modelo Ano`), `<h1>` único por página.
- `favicon.svg`; futuramente `sitemap.xml` + JSON-LD `Vehicle`/`Car` (Fase 3).

## 7. Acessibilidade

- Contraste AA (texto claro sobre escuro — validar rosa sobre preto em textos
  pequenos; usar `--neon-soft` se necessário).
- Navegação por teclado (menu, filtros, lightbox com `Esc`), `:focus-visible`.
- `prefers-reduced-motion` (já no motion spec). `aria-label` nos ícones/botões.

## 8. Caminho de Evolução → Fase 2 (Supabase)

```
Hoje:   view → getCarros()/getCarroById() → CARROS (carros.js)
Fase 2: view → getCarros()/getCarroById() → fetch(Supabase REST)  [só muda aqui]
        + admin.html (Auth) → upload foto (Storage) → insert/update tabela
```
- Tabela `carros` = o contrato do §3. Bucket `fotos` no Storage; `fotos[]` passa
  a guardar URLs públicas. Auth simples (email/senha) só para o admin.
- **Zero retrabalho de UI:** o front consome a mesma abstração.

## 9. Riscos Técnicos & Mitigação

| Risco | Mitigação |
|-------|-----------|
| `fetch` de JSON falha em `file://` | usar `carros.js` como `<script>` (global), não JSON |
| Dono quebrar a sintaxe do `carros.js` | comentários guiando + try/catch no app.js com aviso amigável |
| Fotos pesadas | orientação no README + lazy-load |
| Links de foto externos quebram | preferir fotos locais em `fotos/` (demo já é local) |

## 10. Gate G4 — Veredito
✅ **APROVADO.** Arquitetura simples, performática e evolutiva. Contrato de dados
isola a fonte, permitindo Supabase na Fase 2 sem reescrita. Riscos do `file://`
endereçados.

**Handoff → Fase 5 (@dev + frontend-developer):** implementar `index.html`,
`estoque.html`, `veiculo.html`, `sobre.html`, `assets/style.css`, `assets/app.js`
(com `getCarros()/getCarroById()`), `favicon.svg` e `README.md`, seguindo o
design-spec e este contrato.

— Aria, arquitetando o futuro 🏗️
