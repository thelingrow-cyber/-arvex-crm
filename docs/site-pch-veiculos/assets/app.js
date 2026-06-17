/* =========================================================================
   PCH VINTAGE — app.js
   Render de cards, filtros, detalhe, galeria, reveal e CTA.
   Sem dependências. Funciona em file://.
   ========================================================================= */

/* ---------- Config ---------- */
const CONTATO_URL = 'https://contata.me/pchveiculos';
const INSTAGRAM_URL = 'https://www.instagram.com/pchveiculos/';
// Se o dono passar um número de WhatsApp, preencha aqui (só dígitos, com DDI).
// Ex.: '5511999999999'. Deixe vazio para usar o contata.me.
const WHATSAPP_NUM = '';

/* ---------- Camada de acesso a dados (abstração p/ Supabase na Fase 2) ---------- */
function _withIds(lista){
  const seen = {};
  return lista.map((c, i) => {
    let base = slugify(`${c.marca}-${c.modelo}-${c.ano}`);
    if (seen[base] != null){ seen[base]++; base = `${base}-${seen[base]}`; }
    else seen[base] = 0;
    return { ...c, id: c.id || base, _i: i };
  });
}
function getCarros(){
  try{
    if (typeof CARROS === 'undefined' || !Array.isArray(CARROS)) throw new Error('CARROS ausente');
    return _withIds(CARROS);
  }catch(e){
    console.error('Erro ao ler carros.js:', e);
    return [];
  }
}
function getCarroById(id){ return getCarros().find(c => c.id === id) || null; }

/* ---------- Helpers ---------- */
function slugify(s){
  return String(s).toLowerCase()
    .normalize('NFD').replace(/[̀-ͯ]/g,'')
    .replace(/[^a-z0-9]+/g,'-').replace(/(^-|-$)/g,'');
}
function fmtPreco(n){
  if (n == null || isNaN(n)) return 'Consulte';
  return 'R$ ' + Number(n).toLocaleString('pt-BR');
}
function fmtKm(n){ return (n==null||isNaN(n)) ? '—' : Number(n).toLocaleString('pt-BR') + ' km'; }
function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m])); }

function contatoCarro(c){
  const txt = encodeURIComponent(`Olá! Tenho interesse no ${c.marca} ${c.modelo} ${c.ano} que vi no site da PCH. Pode me passar mais detalhes?`);
  if (WHATSAPP_NUM) return `https://wa.me/${WHATSAPP_NUM}?text=${txt}`;
  return CONTATO_URL;
}

function badgesHTML(c){
  let b = '';
  if (c.destaque) b += '<span class="badge badge-neon">Destaque</span>';
  if (c.blindado) b += '<span class="badge badge-neon">Blindado</span>';
  if (c.condicao === 'original') b += '<span class="badge badge-gold">Original</span>';
  if (c.condicao === 'restaurado') b += '<span class="badge badge-gold">Restaurado</span>';
  return b;
}
function mediaHTML(c){
  const foto = c.fotos && c.fotos[0];
  if (foto) return `<img src="${esc(foto)}" alt="${esc(c.marca+' '+c.modelo+' '+c.ano)}" loading="lazy" decoding="async">`;
  return `<div class="photo-soon"><b>Foto em breve</b><small>${esc(c.marca+' '+c.modelo)}</small></div>`;
}

/* ---------- Card ---------- */
function cardHTML(c){
  return `
  <article class="card reveal">
    <a class="card-link" href="veiculo.html?id=${encodeURIComponent(c.id)}">
      <div class="card-media">
        ${mediaHTML(c)}
        <div class="card-badges">${badgesHTML(c)}</div>
      </div>
      <div class="card-body">
        <div class="card-title">${esc(c.marca)} ${esc(c.modelo)}</div>
        <div class="card-version">${esc(c.versao||'')}</div>
        <div class="card-meta tnum">
          <span>${esc(c.ano)}</span><span class="dot">·</span>
          <span>${fmtKm(c.km)}</span><span class="dot">·</span>
          <span>${esc(c.uf)}</span>
        </div>
        <div class="card-price tnum">${fmtPreco(c.preco)}</div>
        <div class="card-foot"><span class="btn btn-ghost">Ver detalhes</span></div>
      </div>
    </a>
  </article>`;
}

/* ---------- Render: destaques (home) ---------- */
function renderDestaques(sel, limit){
  const el = document.querySelector(sel); if(!el) return;
  let lista = getCarros().filter(c => c.destaque);
  if (lista.length === 0) lista = getCarros();
  if (limit) lista = lista.slice(0, limit);
  el.innerHTML = lista.map(cardHTML).join('');
  observeReveal();
}

/* ---------- Render: estoque com filtros ---------- */
function initEstoque(){
  const grid = document.querySelector('#grid-estoque'); if(!grid) return;
  const fMarca = document.querySelector('#f-marca');
  const fUf = document.querySelector('#f-uf');
  const fPreco = document.querySelector('#f-preco');
  const fBusca = document.querySelector('#f-busca');
  const fOrder = document.querySelector('#f-order');
  const count = document.querySelector('#f-count');
  const all = getCarros();

  // popular selects
  const marcas = [...new Set(all.map(c=>c.marca))].sort();
  const ufs = [...new Set(all.map(c=>c.uf))].sort();
  fMarca.innerHTML = '<option value="">Todas</option>' + marcas.map(m=>`<option>${esc(m)}</option>`).join('');
  fUf.innerHTML = '<option value="">Todos</option>' + ufs.map(u=>`<option>${esc(u)}</option>`).join('');

  // estado inicial via URL
  const p = new URLSearchParams(location.search);
  if (p.get('marca')) fMarca.value = p.get('marca');
  if (p.get('uf')) fUf.value = p.get('uf');
  if (p.get('q')) fBusca.value = p.get('q');

  function apply(){
    let lista = all.slice();
    const m = fMarca.value, u = fUf.value, q = (fBusca.value||'').toLowerCase().trim();
    const pr = fPreco.value;
    if (m) lista = lista.filter(c=>c.marca===m);
    if (u) lista = lista.filter(c=>c.uf===u);
    if (q) lista = lista.filter(c=>(`${c.marca} ${c.modelo} ${c.versao||''}`).toLowerCase().includes(q));
    if (pr){
      const [min,max] = pr.split('-').map(Number);
      lista = lista.filter(c=> c.preco>=min && (max?c.preco<=max:true));
    }
    switch(fOrder.value){
      case 'preco-asc': lista.sort((a,b)=>a.preco-b.preco); break;
      case 'preco-desc': lista.sort((a,b)=>b.preco-a.preco); break;
      case 'ano': lista.sort((a,b)=>String(b.ano).localeCompare(String(a.ano))); break;
      case 'km': lista.sort((a,b)=>a.km-b.km); break;
    }
    if (lista.length){
      grid.innerHTML = lista.map(cardHTML).join('');
    }else{
      grid.innerHTML = `<div class="empty"><b>Nenhum clássico encontrado</b>Limpe os filtros ou fale com a gente — novidades chegam toda semana.</div>`;
    }
    count.textContent = `${lista.length} ${lista.length===1?'clássico':'clássicos'}`;
    // refletir na URL
    const np = new URLSearchParams();
    if (m) np.set('marca',m); if (u) np.set('uf',u); if (q) np.set('q',q);
    history.replaceState(null,'', location.pathname + (np.toString()?'?'+np:''));
    observeReveal();
  }
  [fMarca,fUf,fPreco,fOrder].forEach(e=>e.addEventListener('change',apply));
  fBusca.addEventListener('input',apply);
  apply();
}

/* ---------- Render: detalhe ---------- */
function initDetalhe(){
  const root = document.querySelector('#detalhe'); if(!root) return;
  const id = new URLSearchParams(location.search).get('id');
  const c = id && getCarroById(id);
  if(!c){
    root.innerHTML = `<div class="empty container"><b>Carro não encontrado</b><a class="link" href="estoque.html" style="color:var(--neon)">← Voltar para a coleção</a></div>`;
    return;
  }
  document.title = `${c.marca} ${c.modelo} ${c.ano} — PCH Veículos`;
  const fotos = (c.fotos && c.fotos.length) ? c.fotos : [];
  const mainImg = fotos.length
    ? `<img id="g-main" src="${esc(fotos[0])}" alt="${esc(c.marca+' '+c.modelo)}">`
    : `<div class="photo-soon"><b>Foto em breve</b><small>${esc(c.marca+' '+c.modelo)}</small></div>`;
  const thumbs = fotos.length>1
    ? `<div class="gallery-thumbs">${fotos.map((f,i)=>`<img src="${esc(f)}" data-i="${i}" class="${i===0?'active':''}" alt="foto ${i+1}">`).join('')}</div>` : '';

  const specs = [
    ['Ano', c.ano], ['Quilometragem', fmtKm(c.km)],
    ['Motor / Versão', c.versao||c.motor||'—'], ['Câmbio', c.cambio||'—'],
    ['Cor', c.cor||'—'], ['Estado', c.uf]
  ];

  root.innerHTML = `
  <div class="container">
    <div class="breadcrumb"><a href="estoque.html">← A coleção</a></div>
    <div class="detail">
      <div>
        <div class="gallery-main">${mainImg}</div>
        ${thumbs}
      </div>
      <div>
        <div class="card-badges" style="position:static;margin-bottom:10px">${badgesHTML(c)}</div>
        <h1 class="detail-title">${esc(c.marca)} ${esc(c.modelo)}</h1>
        <div class="detail-version">${esc(c.versao||'')} · ${esc(c.ano)}</div>
        <div class="detail-price tnum">${fmtPreco(c.preco)}</div>
        <div class="specs">${specs.map(s=>`<div class="spec"><div class="k">${s[0]}</div><div class="v">${esc(s[1])}</div></div>`).join('')}</div>
        <a class="btn btn-primary" href="${contatoCarro(c)}" target="_blank" rel="noopener">Tenho interesse neste ${esc(c.modelo)}</a>
        <a class="btn btn-ghost" href="estoque.html">Ver mais clássicos</a>
        <p class="trust">Atendimento humano e direto. Tire suas dúvidas, peça mais fotos e agende para ver pessoalmente.</p>
      </div>
    </div>
    ${c.historia?`<div class="history reveal"><h2 class="h2">A história deste ${esc(c.modelo)}</h2><p>${esc(c.historia)}</p></div>`:''}
    <div class="section">
      <div class="section-head"><h2 class="h2">Outros clássicos</h2><a class="link" href="estoque.html">Ver todos →</a></div>
      <div class="grid" id="relacionados"></div>
    </div>
  </div>`;

  // relacionados (mesma marca, senão quaisquer)
  let rel = getCarros().filter(x=>x.id!==c.id && x.marca===c.marca);
  if (rel.length<3) rel = rel.concat(getCarros().filter(x=>x.id!==c.id && x.marca!==c.marca));
  document.querySelector('#relacionados').innerHTML = rel.slice(0,3).map(cardHTML).join('');

  // galeria
  if (fotos.length>1){
    const main = document.querySelector('#g-main');
    root.querySelectorAll('.gallery-thumbs img').forEach(t=>{
      t.addEventListener('click',()=>{
        main.src = t.src;
        root.querySelectorAll('.gallery-thumbs img').forEach(x=>x.classList.remove('active'));
        t.classList.add('active');
      });
    });
  }
  if (fotos.length){
    const main = document.querySelector('#g-main');
    main && main.addEventListener('click',()=>openLightbox(main.src));
  }
  observeReveal();
}

/* ---------- Lightbox ---------- */
function openLightbox(src){
  let lb = document.querySelector('#lightbox');
  if(!lb){
    lb = document.createElement('div'); lb.id='lightbox'; lb.className='lightbox';
    lb.innerHTML = `<button class="lightbox-close" aria-label="Fechar">×</button><img alt="Foto ampliada">`;
    document.body.appendChild(lb);
    lb.addEventListener('click',e=>{ if(e.target===lb||e.target.classList.contains('lightbox-close')) lb.classList.remove('open'); });
    document.addEventListener('keydown',e=>{ if(e.key==='Escape') lb.classList.remove('open'); });
  }
  lb.querySelector('img').src = src; lb.classList.add('open');
}

/* ---------- Scroll reveal ---------- */
let _io;
function observeReveal(){
  const els = document.querySelectorAll('.reveal:not(.in)');
  if(!('IntersectionObserver' in window)){ els.forEach(e=>e.classList.add('in')); return; }
  if(!_io){
    _io = new IntersectionObserver((entries)=>{
      entries.forEach((en,i)=>{ if(en.isIntersecting){ en.target.style.transitionDelay=(i%6*60)+'ms'; en.target.classList.add('in'); _io.unobserve(en.target);} });
    },{threshold:.15});
  }
  els.forEach(e=>_io.observe(e));
}

/* ---------- Header scroll + menu mobile + FAB ---------- */
function initChrome(){
  const header = document.querySelector('.header');
  const fab = document.querySelector('.fab');
  const onScroll = ()=>{
    if (header) header.classList.toggle('scrolled', window.scrollY>40);
    if (fab) fab.classList.toggle('show', window.scrollY>500);
  };
  window.addEventListener('scroll', onScroll); onScroll();

  const burger = document.querySelector('.burger');
  const links = document.querySelector('.nav-links');
  if (burger && links){
    burger.addEventListener('click',()=>links.classList.toggle('open'));
    links.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>links.classList.remove('open')));
  }
  // contato dinâmico
  document.querySelectorAll('[data-contato]').forEach(a=>a.href = (WHATSAPP_NUM?`https://wa.me/${WHATSAPP_NUM}`:CONTATO_URL));
  document.querySelectorAll('[data-instagram]').forEach(a=>a.href = INSTAGRAM_URL);
}

/* ---------- Boot ---------- */
document.addEventListener('DOMContentLoaded',()=>{
  initChrome();
  renderDestaques('#grid-destaques', 6);
  initEstoque();
  initDetalhe();
  observeReveal();
});
