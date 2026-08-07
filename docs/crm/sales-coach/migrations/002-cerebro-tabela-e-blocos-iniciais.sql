-- ============================================================================
-- Sales Coach — cérebro do agente (sales_knowledge)
-- O que o coach precisa SABER antes de julgar uma call: quem é o comprador,
-- o que a ARVEX vende, qual é o método e quais objeções são reais.
-- Sem isso, o coach analisa a call como um consultor genérico de vendas.
--
-- Aplicar: node -e "..." com SUPABASE_DB_URL, ou colar no SQL Editor.
-- ============================================================================

create table if not exists sales_knowledge (
  id          uuid primary key default gen_random_uuid(),
  tipo        text not null check (tipo in ('icp','metodo','oferta','objecao','caso','produto')),
  titulo      text not null,
  conteudo    text not null,
  fonte       text,                       -- de onde veio (call, live, livro, doc)
  tags        text[] default '{}',
  peso        int  default 3 check (peso between 1 and 5),  -- ordena quando há muito material
  ativo       boolean default true,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

create index if not exists sales_knowledge_ativo_idx on sales_knowledge (ativo, tipo, peso desc);

alter table sales_knowledge enable row level security;

-- leitura: qualquer usuário autenticado do CRM. escrita: só admin.
drop policy if exists sales_knowledge_select on sales_knowledge;
create policy sales_knowledge_select on sales_knowledge
  for select to authenticated using (true);

drop policy if exists sales_knowledge_admin on sales_knowledge;
create policy sales_knowledge_admin on sales_knowledge
  for all to authenticated
  using (exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin'))
  with check (exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin'));

-- ── conteúdo inicial ────────────────────────────────────────────────────────
-- Destilado de calls reais (ver docs/crm/sales-coach/conhecimento/). Nada aqui é suposição:
-- cada bloco tem fonte rastreável.

insert into sales_knowledge (tipo, titulo, conteudo, fonte, tags, peso) values

('icp', 'Quem é o dono de ótica (perfil real, extraído de calls)',
$$Dono de ótica de cidade média (interior/entorno metropolitano), 6+ anos de loja, 1 a 3 unidades,
faturamento de R$16k a R$45k por loja/mês. Decide SEMPRE em dupla (cônjuge ou sócio) — não existe
decisor solitário. Tem carteira de clientes de anos que nunca foi trabalhada.

DOR DECLARADA: "quero vender mais". DOR REAL: falta de critério para decidir. Ele não é parado —
roda tráfego, faz campanha, liga cliente a cliente — ele se move sem bússola e sabe disso.
Frases-sintoma: "a gente não sabe se tá fazendo certo", "fica sem saber o que fazer na hora de gravar".

MARCAS RECORRENTES:
1. Já foi queimado por agência/gestor de tráfego. Objeção latente: "vai, faz aí, me paga; se der certo,
   deu certo". Ele pesquisa o fornecedor ANTES da call.
2. Compra curso e não assiste ("o dia a dia corrido"). Não vender treinamento — vender acompanhamento.
3. Refém da guerra de preço e sabe disso (armação a 49 na compra da lente, "público chorão").
   Não precisa ser convencido de que é ruim; precisa da SAÍDA.
4. A base de clientes é caixa esquecido — nunca fez reativação.
5. O WhatsApp vaza venda: não responde fora do horário, tudo chega pedindo preço, sem automação.
6. O cônjuge é o rosto do conteúdo e está sobrecarregado ("tem que gravar vídeo, tem bastante funções").
7. Vocabulário dele: guerra de preço, público chorão, multifocal/visão simples, marca própria vs grife,
   feira de São Paulo, exame de vista como chamariz, passante, curadoria de peças.$$,
 'docs/crm/sales-coach/conhecimento/icp-dono-de-otica.md (3 calls: Djarla 04/08, Anderson 03/08, Tatiane 09/07)',
 array['icp','otica','comprador'], 5),

('oferta', 'O que a ARVEX/Cindy vende (para julgar se o closer apresentou certo)',
$$PROGRAMA DE ACOMPANHAMENTO — 4 meses. Faixa praticada nas calls: R$4.997 à vista ou 12× R$516
(há registro de apresentação a R$12.500 / 12× R$250 em outro perfil de lead).

ENTREGAS:
- Reunião inicial com a Sabrina (principal vendedora/gerente das óticas da Cindy): diagnóstico da loja,
  tipo de cliente, ticket médio.
- 1ª campanha = reativação da base via grupo VIP no WhatsApp (disparo por API, ~3 centavos/disparo,
  2-3 dias de antecipação com gatilhos, depois oferta exclusiva). É o gerador de caixa inicial.
- Encontro semanal em grupo com a Cindy + encontro individual de plano/meta.
- Treinamento Estrategista (8 módulos) — posicionado como MANUAL, não como o produto.
- Acompanhamento individual da Sabrina no WhatsApp (script comercial/WhatsApp e presencial).
- Encontro mensal com o gestor de tráfego da Cindy; gestor por 1 mês como bônus em casos selecionados.
- Rede de 9 fornecedores + curadoria de peças + caminho para marca própria.
- Banco de campanhas validadas (arte, legenda, calendário), checklist de missões, call SOS (48h),
  Restart Óptico como bônus, grupo de donos de ótica.
- Cláusula de exclusividade na cidade enquanto o contrato durar.

POSICIONAMENTO CENTRAL: não vendemos tráfego avulso — "só o tráfego não resolve". O objetivo é
transformar o dono em ESTRATEGISTA (se não mudar o repertório dele, o resultado não se sustenta).
Pilares: (1) posicionamento no Instagram gerando desejo por armação, (2) tráfego alinhado ao
posicionamento, (3) campanhas sobre a base.$$,
 'Extraído das calls de venda reais (Gabriel 04/08 e Vitor 09/07)',
 array['oferta','arvex','cindy'], 5),

('metodo', 'A conta da base — o reframe que está sendo desperdiçado',
$$O argumento mais forte da oferta é a reativação da base, e nas calls analisadas ele aparece só como
CONCEITO ("tem um dinheiro parado na mesa"), nunca como CONTA FEITA na frente do lead.

O que fazer ao vivo, antes de falar preço:
"Vocês têm X anos de loja. Quantos clientes vocês têm no cadastro? [esperar o número]
Se só 2% voltarem numa campanha, com o ticket médio de vocês, isso é R$ N numa única semana —
mais do que o programa inteiro custa. Esse dinheiro já é de vocês, só não foi buscado ainda."

Isso converte o preço de CUSTO em ANTECIPAÇÃO DE CAIXA QUE JÁ EXISTE, e ataca de frente a objeção
de orçamento apertado, que aparece em praticamente toda call.

REGRA DERIVADA: não apresentar a oferta sem ter três números do lead na tela — faturamento médio,
ticket médio e tamanho da base. Sem esses três, a apresentação vira folheto.$$,
 'docs/crm/sales-coach/conhecimento/casos/caso-04-djarla-oticas-adrian.md',
 array['metodo','fechamento','reframe'], 5),

('objecao', 'Objeções reais x cortinas no nicho óptico',
$$GENUÍNAS (o lead mantém a mesma narrativa do início ao fim da call):
- Caixa comprometido por evento recente: reforma da loja, dívida com fornecedor, abertura de nova
  unidade. Ex.: "teve uma reforma recente e a gente gastou um valor alto"; "estou investindo numa nova loja".
- Compromisso ativo com concorrente: "faz dois meses que entrei em outra mentoria e tenho um ano ainda".

CORTINAS (mudam de forma ao longo da call): "vou analisar", "vou ver o orçamento" quando o valor
ainda não foi construído. SINTOMA-CHAVE: o lead pergunta o preço ANTES da apresentação — preço
perguntado cedo = valor ainda não estabelecido.

OBJEÇÃO SILENCIOSA (está em todas, ninguém verbaliza): "como eu sei que funciona pra MIM, na MINHA
cidade?". Prova social do MESMO porte e região vale mais do que o caso do aluno-estrela.

ANTIPADRÃO DETECTADO NO TIME: responder ao "vou pensar" pedindo um SINAL SIMBÓLICO (R$100) para
"segurar a condição/reservar vaga". Aconteceu em 2 calls, com 2 closers diferentes, e nas duas o
lead saiu sem decidir. Pedir R$100 num programa de R$4.997 sinaliza que o valor não foi construído,
e substitui o "sim" grande por um "sim" pequeno. Alternativa: fazer a conta da base e fechar no
valor cheio, OU marcar a call de decisão COM o segundo decisor presente e data no calendário.$$,
 'docs/crm/sales-coach/conhecimento/ (calls Djarla 04/08 e Tatiane 09/07)',
 array['objecao','fechamento'], 4)

on conflict do nothing;
