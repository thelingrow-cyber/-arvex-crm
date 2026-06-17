/* =========================================================================
   PCH VEÍCULOS — CATÁLOGO DE CARROS CLÁSSICOS
   -------------------------------------------------------------------------
   Este é o ÚNICO arquivo que você precisa editar para adicionar, remover
   ou alterar carros no site. Não precisa mexer nas páginas .html.

   COMO ADICIONAR UM CARRO:
   1. Copie um bloco { ... } inteiro (incluindo a vírgula no final).
   2. Cole logo abaixo, dentro dos colchetes [ ].
   3. Troque as informações.
   4. Coloque as fotos do carro na pasta  fotos/  e escreva o nome do
      arquivo em "fotos" (ex.: 'fotos/meu-carro-frente.jpg').
      Pode colocar várias fotos — a primeira é a capa.
   5. Salve. Pronto, o carro aparece no site.

   DICA: se deixar "fotos" vazio [], o site mostra um cartão neon de
   "Foto em breve" no lugar — útil enquanto você não tirou as fotos.

   >>> AS FOTOS ATUAIS SÃO APENAS MODELOS (carros clássicos de demonstração)
   >>> para você visualizar o site. Troque pelas fotos dos SEUS carros.

   CAMPOS:
   - marca, modelo, versao .... texto
   - ano ...................... ex.: '1968'  ou  '1968/1969'
   - km ...................... número (sem ponto). ex.: 78000
   - preco ................... número (sem ponto). ex.: 320000
   - uf ..................... estado em 2 letras. ex.: 'SP'  (nunca cidade)
   - blindado ............... true ou false  (mostra selo BLINDADO)
   - destaque .............. true ou false  (aparece em destaque na home)
   - historia .............. texto livre contando a história do carro
   - fotos ................. lista de caminhos de imagem
   ========================================================================= */

const CARROS = [
  {
    marca: 'Ford',
    modelo: 'Mustang Fastback',
    versao: '4.7 V8 Coupé',
    ano: '1968',
    km: 86000,
    preco: 520000,
    uf: 'SP',
    blindado: false,
    destaque: true,
    historia:
      'O fastback mais cobiçado da história do automóvel. Esta unidade 1968 vermelho-vinho passou por restauração completa, motor V8 retificado e originalidade preservada nos mínimos detalhes. Documentação em dia. Uma lenda viva para o colecionador exigente.',
    fotos: ['fotos/mustang-fastback-1968.jpg'],
  },
  {
    marca: 'Jaguar',
    modelo: 'E-Type Série 1',
    versao: '3.8 Coupé',
    ano: '1964',
    km: 64000,
    preco: 980000,
    uf: 'RJ',
    blindado: false,
    destaque: true,
    historia:
      'Chamado por Enzo Ferrari de "o carro mais bonito já feito". A Série 1 é o ápice do design britânico dos anos 60. Pintura azul gelo impecável, rodas de raios e interior em couro original. Peça de museu, pronta para desfilar.',
    fotos: ['fotos/jaguar-etype-1964.jpg'],
  },
  {
    marca: 'Porsche',
    modelo: '356',
    versao: '1.5 Coupé',
    ano: '1951',
    km: 42000,
    preco: 1250000,
    uf: 'SP',
    blindado: false,
    destaque: true,
    historia:
      'O primeiro Porsche da história. Raríssima unidade dos primeiros anos de produção, na icônica cor salmão. Procedência rastreável e restauração de concurso. Para o investidor e o entusiasta que querem o começo de tudo.',
    fotos: ['fotos/porsche-356-1951.jpg'],
  },
  {
    marca: 'Chevrolet',
    modelo: 'Bel Air',
    versao: '4.6 V8',
    ano: '1957',
    km: 99000,
    preco: 410000,
    uf: 'MG',
    blindado: false,
    destaque: false,
    historia:
      'O símbolo máximo dos anos dourados americanos. Rabos de peixe, cromados generosos e pneus faixa branca. Esta unidade cor cobre está completa e funcional, pronta para casamentos, eventos e coleção.',
    fotos: ['fotos/chevrolet-bel-air-1957.jpg'],
  },
  {
    marca: 'Volkswagen',
    modelo: 'SP2',
    versao: '1.7 Coupé',
    ano: '1973',
    km: 71000,
    preco: 195000,
    uf: 'PR',
    blindado: false,
    destaque: true,
    historia:
      'O esportivo brasileiro mais elegante já produzido. Linhas baixas, desenho atemporal e raridade absoluta — pouquíssimos restaram em estado original. Azul claro com faixas, motor 1.7 revisado. Orgulho nacional sobre rodas.',
    fotos: ['fotos/vw-sp2-1973.jpg'],
  },
  {
    marca: 'Chevrolet',
    modelo: 'Opala',
    versao: 'SS Coupé 4.1',
    ano: '1977',
    km: 112000,
    preco: 135000,
    uf: 'RS',
    blindado: false,
    destaque: false,
    historia:
      'O muscle car brasileiro por excelência. Esta Opala coupé vermelha respira a estrada — motor 6 cilindros encorpado, presença imponente e aquele ronco inconfundível. Conservada e pronta para rodar.',
    fotos: ['fotos/chevrolet-opala-1977.jpg'],
  },
];
