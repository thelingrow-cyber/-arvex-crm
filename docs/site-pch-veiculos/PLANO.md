# PLANO DO SITE — PCH Veículos

> Plano completo de produção do site da revenda **PCH Veículos**.
> Status: **aguardando aprovação** · Versão 1.0 · 2026-06-16

---

## 1. Visão & Objetivo

Construir o **site institucional + vitrine de estoque** da PCH Veículos —
revenda de **carros clássicos / vintage** — com ambição de ser **referência
mundial no nicho**: um site completo (não uma única página) com identidade
**dark + rosa neon**, onde a revenda exibe os clássicos à venda com foto,
história e dados, e converte o visitante em conversa no WhatsApp/contato.

> A **história de cada carro** é peça central da venda de clássico (procedência,
> originalidade, restauração) — não é só ficha técnica.

**Princípio estratégico do cliente:** mostrar **estado (UF)**, nunca cidade —
para que o cliente precise falar com a revenda para fechar (não dá pra "filtrar
o carro sem a gente").

**Meta de conversão:** todo caminho leva ao contato (`contata.me/pchveiculos`).

---

## 2. Briefing Consolidado (fonte da verdade)

**Origem:** áudio do dono (transcrito) + 2 referências + Instagram/contato.

| Item | Definição |
|------|-----------|
| Nome | PCH Veículos |
| Nicho | Revenda de **carros clássicos / vintage** (colecionáveis) |
| Visual | Fundo preto + letreiro/acento **rosa neon** |
| Instagram | `@pchveiculos` |
| Contato/CTA | `contata.me/pchveiculos` |
| Card do carro | foto, modelo, marca, ano, km, valor, **estado (UF)**, história |
| Regra de negócio | mostrar UF, **não** cidade (força contato) |
| Seções institucionais | Quem Somos, Missão, Valores |
| Prioridade nº 1 (palavras dele) | "conseguir subir foto dos carros" |
| Referências | `paitomotors.com.br`, `armazemdovovo.com.br/vendidos` |

**Leitura das referências:**
- *Païto Motors*: estrutura clássica de vitrine premium (carrossel de destaques,
  grid de cards com marca/modelo/ano/km/preço, busca por marca, selo
  "BLINDADO", WhatsApp flutuante). **Mas é claro/minimalista** — nós invertemos
  para dark/neon.
- *Armazém do Vovô*: vitrine com paginação e busca textual; reforça o padrão de
  grid + filtro.

---

## 3. Arquitetura de Informação (mapa do site)

```
PCH Veículos
│
├── Home (index.html)
│     • Hero com letreiro neon + headline + CTA
│     • Faixa de destaques (3–4 carros marcados "destaque")
│     • Atalho "Ver estoque completo"
│     • Bloco institucional curto + prova (Instagram)
│     • Faixa de contato/CTA
│
├── Estoque (estoque.html)
│     • Vitrine completa (grid)
│     • Filtros: marca, estado (UF), faixa de preço, busca por texto
│     • Ordenar por: preço, ano, km
│
├── Detalhe do Veículo (veiculo.html?id=…)
│     • Galeria de fotos
│     • Specs: marca, modelo, versão, ano, km, preço, UF, selos
│     • História do carro (texto)
│     • CTA forte "Tenho interesse" → contato com msg pré-preenchida
│     • Carros relacionados
│
├── Sobre (sobre.html)
│     • Quem Somos, Missão, Valores
│     • Diferenciais / por que comprar na PCH
│
└── Contato (contato.html  — ou seção fixa)
      • Botões: WhatsApp/contata.me, Instagram
      • Horário, atendimento, localização (apenas estado/região)
```

Componentes globais reaproveitados em todas as páginas: **header** (logo neon +
menu), **footer** (contato + redes), **botão flutuante de contato**, **card de
carro**, **design tokens** (cores/tipografia).

---

## 4. Stack Técnica

### Recomendada (Fase 1): Multi-página estático vanilla
- **HTML + CSS + JavaScript puro**, sem build, sem framework.
- Dados dos carros num único arquivo **`carros.js`** (já criado) — o dono edita
  esse arquivo para adicionar/remover carros.
- Cada página lê o mesmo `carros.js`. O detalhe usa `?id=` na URL.
- **Por quê:** entrega rápida, custo zero, abre direto no navegador, sobe em
  qualquer hospedagem grátis, e o dono consegue editar sem conhecimento técnico.

### Evolução (Fase 2): Backend + Painel admin
- **Supabase** (Postgres + Storage + Auth) para o dono **subir foto pelo painel**
  — exatamente o que ele pediu como prioridade.
- Página `admin.html` protegida por login: formulário com upload de imagem,
  campos do carro, publicar/despublicar. Site passa a ler do Supabase.

### Alternativa (se quiser robustez desde já): Astro
- Gera site estático com ótimo SEO e componentização. Custo: exige Node/build e
  deploy (Vercel/Netlify). **Recomendo deixar para depois** — não é necessário
  para o MVP e adiciona fricção.

> **Decisão pedida:** seguir Fase 1 vanilla agora e Fase 2 Supabase depois? (rec.)

---

## 5. Design System (dark / neon)

| Token | Valor proposto | Uso |
|-------|----------------|-----|
| `--bg` | `#0a0a0c` | fundo principal (preto) |
| `--bg-2` | `#121217` | seções alternadas / cards |
| `--neon` | `#ff1f8f` | rosa neon (acento, letreiro, CTA) |
| `--neon-soft` | `#ff66b3` | hover / brilho |
| `--text` | `#f5f5f7` | texto principal |
| `--muted` | `#9a9aa5` | texto secundário |
| `--line` | `rgba(255,255,255,.08)` | bordas |

- **Tipografia:** display forte e condensada para headlines (peso 800–900) +
  sans neutra para corpo. Números com `tabular-nums` (preço/km/ano).
- **Efeitos:** letreiro com **glow neon** (text-shadow/box-shadow), cards com
  glassmorphism sutil e borda neon no hover, **scroll reveal**, micro-animações.
  Sem exagero — fiel à vibe "showroom noturno".
- **Selos:** `DESTAQUE`, `BLINDADO` (pílulas neon).
- **Responsivo mobile-first** (a maioria virá do link na bio do Instagram).

---

## 6. Funcionalidades por página

**Home**
- [ ] Hero com letreiro neon + CTA primário
- [ ] Faixa de destaques (carros com `destaque: true`)
- [ ] Bloco institucional curto + CTA Instagram
- [ ] Faixa de contato

**Estoque**
- [ ] Grid de todos os carros (render via JS a partir de `carros.js`)
- [ ] Filtro por marca
- [ ] Filtro por estado (UF)
- [ ] Filtro por faixa de preço
- [ ] Busca por texto (marca/modelo)
- [ ] Ordenação (preço ↑↓, ano, km)
- [ ] Estado vazio elegante ("nenhum carro encontrado")

**Detalhe do veículo**
- [ ] Galeria (capa + miniaturas) com fallback "Foto em breve"
- [ ] Specs completas + selos
- [ ] História do carro
- [ ] CTA "Tenho interesse" → contato com mensagem pré-preenchida (modelo+ano)
- [ ] Carros relacionados (mesma marca/faixa)

**Sobre**
- [ ] Quem Somos, Missão, Valores
- [ ] Diferenciais

**Global**
- [ ] Header + menu responsivo
- [ ] Footer (contato, Instagram, UF de atuação)
- [ ] Botão flutuante de contato
- [ ] Favicon + meta tags (título, descrição, Open Graph p/ link bonito no Insta)

---

## 7. Modelo de Dados do Carro

Já implementado em `carros.js`:

```js
{
  marca, modelo, versao,
  ano,        // '2022/2023'
  km,         // 38000
  preco,      // 149900
  uf,         // 'SP'  (estado, nunca cidade)
  blindado,   // true/false → selo
  destaque,   // true/false → aparece na home
  historia,   // texto
  fotos: []   // caminhos; 1ª é a capa; vazio = "Foto em breve"
}
```

Na Fase 2 esse mesmo modelo vira uma **tabela no Supabase** + bucket de Storage
para as fotos — migração direta, sem retrabalho de modelagem.

---

## 8. Fases de Entrega

### FASE 1 — Site estático completo (MVP) · **agora**
Site multi-página funcional, dark/neon, com vitrine, filtros, detalhe,
institucional e contato. Carros gerenciados via `carros.js`. Pronto pra subir.
**Esforço:** ~1–2h. **Entrega:** site no ar.

### FASE 2 — Painel admin + backend (Supabase) · *quando quiser autonomia total*
O dono sobe foto e cadastra carro por um painel com login. Site passa a ler do
banco. **Esforço:** ~3–5h. **Pré-requisito:** criar projeto Supabase (grátis).

### FASE 3 — Polimento & crescimento · *opcional*
SEO técnico, domínio próprio, Google Analytics/Pixel, sitemap, página de
financiamento/avaliação de usado, compartilhamento do carro no WhatsApp,
integração com o Instagram. **Esforço:** sob demanda.

---

## 9. Squad AIOX por fase

| Fase | Agentes | Papel |
|------|---------|-------|
| Plano | `@aiox-master` (Orion) | orquestração (este doc) |
| Design | `@ux-design-expert` (Uma) + WebDesign `web-designer` | layout, design system dark/neon |
| Copy | WebDesign `copywriter` | headlines, institucional, CTAs |
| Build F1 | `@dev` (Dex) | implementação das páginas estáticas |
| Build F2 | `@data-engineer` (Dara) + `@dev` | schema Supabase, storage, painel admin |
| Qualidade | `@qa` (Quinn) | revisão responsividade, links, performance |
| Deploy | `@devops` (Gage) | publicação (push/host) — autoridade exclusiva |

> Em modo "1 hora", a Fase 1 pode ser executada direto por `@dev`/Orion com a
> referência visual já definida, acionando os especialistas em pontos de revisão.

---

## 10. Cronograma / Esforço

| Entrega | Esforço | Quando |
|---------|---------|--------|
| Plano (este doc) | ✔ feito | hoje |
| `carros.js` (dados) | ✔ feito | hoje |
| Fase 1 — site estático completo | ~1–2h | hoje |
| Fase 1 — publicação | ~15min | hoje |
| Fase 2 — painel Supabase | ~3–5h | quando o dono pedir |
| Fase 3 — extras/SEO | sob demanda | futuro |

---

## 11. Decisões em Aberto (preciso de você)

1. **Stack:** confirmar Fase 1 vanilla agora + Fase 2 Supabase depois? (rec. sim)
2. **Páginas separadas vs single-page:** site multi-página (rec., melhor p/ SEO e
   organização) ou tudo numa página só com âncoras (mais rápido)?
3. **Fotos:** o amigo já tem as fotos dos carros? (Hoje o site já vem populado
   com **6 clássicos reais de demonstração** — Mustang 68, Jaguar E-Type 64,
   Porsche 356 51, Bel Air 57, VW SP2 73, Opala 77 — de acervo livre/Wikimedia,
   só para ele visualizar; troca depois pelos arquivos dele na pasta `fotos/`.)
4. **Logo:** existe logo da PCH? Se não, gero um letreiro neon tipográfico.
5. **Contato:** uso só o `contata.me/pchveiculos`, ou ele tem número direto de
   WhatsApp para CTA com mensagem pré-preenchida?
6. **Conteúdo institucional:** ele manda os textos de Quem Somos/Missão/Valores
   ou eu escrevo um rascunho profissional para ele aprovar?
7. **Domínio:** vai ser domínio próprio (ex.: `pchveiculos.com.br`) ou subdomínio
   grátis (`pchveiculos.netlify.app`) no começo?

---

## 12. Publicação / Deploy

- **Fase 1:** arrastar a pasta para **Netlify** ou **Vercel** (grátis) → site no
  ar em minutos com URL temporária; depois apontar domínio próprio.
- Alternativa: **GitHub Pages** (grátis, bom se quiser versionar).
- **Fase 2 (Supabase):** segue o mesmo deploy do front; backend é gerenciado.

---

## Estrutura de arquivos prevista (Fase 1)

```
site-pch-veiculos/
├── index.html        # Home
├── estoque.html      # Vitrine + filtros
├── veiculo.html      # Detalhe (?id=)
├── sobre.html        # Quem somos / missão / valores
├── contato.html      # Contato (ou seção)
├── carros.js         # ✔ CATÁLOGO (o dono edita aqui)
├── assets/
│   ├── style.css     # design system + componentes
│   └── app.js        # render de cards, filtros, galeria
├── fotos/            # fotos dos carros
├── PLANO.md          # este documento
└── README.md         # como adicionar carro + publicar
```
