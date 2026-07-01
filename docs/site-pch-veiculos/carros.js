/* =========================================================================
   PCH VEÍCULOS — CATÁLOGO DE CARROS
   -------------------------------------------------------------------------
   Este é o ÚNICO arquivo que você precisa editar para adicionar, remover
   ou alterar carros no site. Não precisa mexer nas páginas .html.

   COMO ADICIONAR UM CARRO:
   1. Copie um bloco { ... } inteiro (incluindo a vírgula no final).
   2. Cole logo abaixo, dentro dos colchetes [ ].
   3. Troque as informações.
   4. Coloque as fotos do carro na pasta  fotos/  e escreva o nome do
      arquivo em "fotos" (ex.: 'fotos/meu-carro-frente.jpg').
      Pode colocar várias fotos — a primeira é a CAPA.
   5. Salve. Pronto, o carro aparece no site.

   DICA: se deixar "fotos" vazio [], o site mostra um cartão neon de
   "Foto em breve" no lugar — útil enquanto você não tirou as fotos.

   CAMPOS:
   - marca, modelo, versao .... texto
   - ano ...................... ex.: '2008'  ou  '2008/2009'
   - km ...................... número (sem ponto). ex.: 33000
   - preco ................... número (sem ponto). ex.: 320000
                               deixe  null  para mostrar "Consulte"
   - uf ..................... estado em 2 letras. ex.: 'SC'  (nunca cidade)
   - cor ................... texto. ex.: 'Preto'
   - cambio ............... texto. ex.: 'Automático'
   - condicao ............ 'original' ou 'restaurado'  (mostra selo)
   - blindado ............ true ou false  (mostra selo BLINDADO)
   - destaque ........... true ou false  (aparece em destaque na home)
   - historia .......... texto livre contando a história do carro
   - fotos ............. lista de caminhos de imagem (a 1ª é a capa)
   ========================================================================= */

const CARROS = [
  {
    marca: 'Renault',
    modelo: 'Mégane Cabriolet',
    versao: '2.0 16V',
    ano: '2008',
    km: 33000,
    preco: null,
    uf: 'SC',
    cor: 'Preto',
    cambio: 'Automático',
    condicao: 'original',
    blindado: false,
    destaque: true,
    historia:
      'Existem carros raros — e existem carros que carregam uma história. Este Mégane Cabriolet saiu zero-quilômetro de uma concessionária de São Paulo e foi transportado de cegonha até Balneário Camboriú, onde passou toda a sua trajetória com um único dono, usado apenas em ocasiões especiais. Chega aos dias de hoje com somente 33.000 km. Pouquíssimas unidades deste conversível vieram ao Brasil — a combinação de exclusividade, baixa quilometragem e procedência faz dele uma oportunidade difícil de encontrar. Capota rígida elétrica retrátil. Um automóvel para quem entende que alguns carros vão além da mobilidade: transformam cada trajeto em uma experiência.',
    fotos: [
      'fotos/renault-megane-cc-2008-01-lateral.jpg',
      'fotos/renault-megane-cc-2008-02-frente-34.jpg',
      'fotos/renault-megane-cc-2008-03-frente.jpg',
      'fotos/renault-megane-cc-2008-04-traseira.jpg',
      'fotos/renault-megane-cc-2008-05-traseira-detalhe.jpg',
      'fotos/renault-megane-cc-2008-06-painel.jpg',
      'fotos/renault-megane-cc-2008-07-bancos-frente.jpg',
      'fotos/renault-megane-cc-2008-08-bancos-traseira.jpg',
      'fotos/renault-megane-cc-2008-09-motor.jpg',
    ],
  },
  {
    marca: 'Chevrolet',
    modelo: 'Kadett GSI',
    versao: '2.0',
    ano: '1995', // ⚠️ PLACEHOLDER — confirmar o ano real com o Vitor
    km: null,    // ⚠️ a confirmar (mostra "—" até preencher)
    preco: null, // mostra "Consulte" até informar valor
    uf: 'SC',
    cor: 'Branco',
    cambio: 'Manual',
    condicao: 'original',
    blindado: false,
    destaque: true,
    historia:
      'Há carros que definem uma geração — e o Kadett GSI é um deles. Símbolo máximo do esportivo nacional dos anos 90, foi o hot hatch que colocou adrenalina ao alcance de quem sonhava com desempenho de verdade: motor 2.0, câmbio manual, rodas de liga leve, aerofólio e os inconfundíveis grafismos GSI nas laterais. Esta unidade, na cobiçada cor branca, se manteve fiel à sua essência original — do volante com a gravata Chevrolet aos bancos com o tecido esportivo de fábrica. Um automóvel que dispensa apresentações para quem viveu a época e desperta desejo imediato em quem coleciona ícones. Mais do que um clássico: um pedaço da história automotiva brasileira pronto para rodar.',
    fotos: [
      'fotos/chevrolet-kadett-gsi-01-frente-34.jpg',
      'fotos/chevrolet-kadett-gsi-02-traseira-34.jpg',
      'fotos/chevrolet-kadett-gsi-03-traseira.jpg',
      'fotos/chevrolet-kadett-gsi-04-lateral.jpg',
      'fotos/chevrolet-kadett-gsi-05-painel.jpg',
      'fotos/chevrolet-kadett-gsi-06-cambio.jpg',
    ],
  },
];
