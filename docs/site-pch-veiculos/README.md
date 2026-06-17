# PCH Veículos — Site

Site de revenda de **carros clássicos**. Estático (HTML/CSS/JS), sem instalação,
sem build. Abre direto no navegador e sobe em qualquer hospedagem.

---

## 🚗 Como adicionar / editar um carro

1. Abra o arquivo **`carros.js`** num editor de texto (Bloco de Notas serve).
2. Copie um bloco `{ ... }` inteiro (com a vírgula no fim) e cole logo abaixo.
3. Troque as informações:

```js
{
  marca: 'Ford',
  modelo: 'Maverick',
  versao: 'GT V8',
  ano: '1975',
  km: 90000,
  preco: 180000,      // só números, sem ponto
  uf: 'SP',           // estado (2 letras) — nunca cidade
  blindado: false,
  destaque: true,     // true = aparece na página inicial
  condicao: 'original', // 'original' ou 'restaurado' (opcional → vira selo dourado)
  cor: 'Preto',       // opcional
  cambio: 'Manual',   // opcional
  historia: 'Conte aqui a história do carro...',
  fotos: ['fotos/maverick-frente.jpg', 'fotos/maverick-lateral.jpg'],
},
```

4. **Fotos:** coloque os arquivos na pasta **`fotos/`** e escreva o nome em
   `fotos`. A **primeira foto é a capa**. Pode colocar várias.
   - Sem fotos ainda? Deixe `fotos: []` → o site mostra "Foto em breve".
5. Salve. Pronto — o carro aparece no site.

> 💡 As 6 fotos que vêm no site agora são **modelos de demonstração** (clássicos
> famosos). Troque pelas fotos dos seus carros.

### Dicas de foto (valorizam a venda)
- 6 a 8 fotos por carro: frente 3/4, lateral, traseira, motor, interior, painel/hodômetro.
- Fundo escuro/limpo, boa luz. Evite fotos tortas, escuras ou com fundo bagunçado.

---

## 📱 Configurar o contato (WhatsApp)

Por padrão os botões levam para `contata.me/pchveiculos`. Se quiser usar um número
de WhatsApp direto (com mensagem pronta sobre o carro), abra **`assets/app.js`**,
no topo, e preencha:

```js
const WHATSAPP_NUM = '5511999999999'; // DDI+DDD+número, só dígitos
```

---

## 🌐 Como publicar (colocar no ar)

Qualquer uma destas opções (todas gratuitas):

- **Netlify** (`netlify.com`): arraste a pasta inteira em "Add new site → Deploy
  manually". Sai no ar em segundos com um link `seunome.netlify.app`.
- **Vercel** (`vercel.com`): importar a pasta. Mesmo resultado.
- **GitHub Pages**: subir a pasta num repositório e ativar Pages.

Depois é só apontar um domínio próprio (ex.: `pchveiculos.com.br`) se quiser.

---

## 📂 Arquivos

| Arquivo | O que é |
|---------|---------|
| `index.html` | Página inicial |
| `estoque.html` | Lista de carros com filtros |
| `veiculo.html` | Página de detalhe de um carro |
| `sobre.html` | Quem somos / missão / valores |
| `carros.js` | **Onde você edita os carros** |
| `assets/style.css` | Visual do site |
| `assets/app.js` | Funcionamento do site |
| `fotos/` | Fotos dos carros |

---

## 🔮 Próxima fase (opcional)

Hoje os carros são editados no arquivo `carros.js`. Numa **Fase 2**, dá pra
adicionar um **painel de administração com login** onde você sobe foto e cadastra
o carro por um formulário (sem mexer em arquivo). É só pedir.
