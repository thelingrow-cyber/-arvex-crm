-- ============================================================
-- PROJETOS v1 — acompanhamento das frentes dentro do CRM
-- Admin-only (RLS). Substitui docs/gestao/BACKLOG.md como fonte viva.
-- Aplicar com ROLLBACK antes do commit real (protocolo pós-incidente).
-- ============================================================

-- ── FRENTES ──────────────────────────────────────────────────
create table if not exists projetos_frentes (
  key        text primary key,
  nome       text not null,
  cor        text not null default '#5B6CFF',
  subtitulo  text,
  meta       text,                              -- alvo do trimestre; null = ainda não definido
  ordem      int  not null default 0,
  ativo      boolean not null default true,
  criado_em  timestamptz not null default now()
);

-- ── TAREFAS ──────────────────────────────────────────────────
create table if not exists projetos_tarefas (
  id             uuid primary key default gen_random_uuid(),
  frente         text not null references projetos_frentes(key) on delete cascade,
  codigo         text not null unique,          -- LG-01, VZ-12…
  titulo         text not null,
  trilha         text,                          -- agrupador dentro da frente
  trilha_nota    text,                          -- subtítulo da trilha (só na 1ª tarefa dela)
  ordem          int  not null default 0,       -- ordem de execução dentro da frente
  executor       text not null default 'eu'
                 check (executor in ('eu','vitor','equipe','ambos')),
  responsavel    text,                          -- nome quando executor='equipe'
  tamanho        text not null default 'M' check (tamanho in ('P','M','G','XG')),
  maquina        text check (maquina is null or maquina in ('M1','M2','M3','M4','M5')),
  bloqueado_por  text,                          -- codigo de outra tarefa
  prazo          date,
  status         text not null default 'aberto'
                 check (status in ('aberto','fazendo','feito','congelado')),
  nota           text,
  alerta         boolean not null default false,-- pinta a nota de vermelho
  criado_em      timestamptz not null default now(),
  atualizado_em  timestamptz not null default now(),
  concluido_em   timestamptz
);

create index if not exists idx_proj_tarefas_frente on projetos_tarefas(frente, ordem);
create index if not exists idx_proj_tarefas_status on projetos_tarefas(status);
create index if not exists idx_proj_tarefas_prazo  on projetos_tarefas(prazo) where prazo is not null;

-- ── carimbo de atualização + conclusão ───────────────────────
create or replace function projetos_touch() returns trigger
language plpgsql as $$
begin
  new.atualizado_em := now();
  if new.status = 'feito' and coalesce(old.status,'') <> 'feito' then
    new.concluido_em := now();
  elsif new.status <> 'feito' then
    new.concluido_em := null;
  end if;
  return new;
end $$;

drop trigger if exists trg_projetos_touch on projetos_tarefas;
create trigger trg_projetos_touch before update on projetos_tarefas
  for each row execute function projetos_touch();

-- ── RLS: só admin ────────────────────────────────────────────
alter table projetos_frentes enable row level security;
alter table projetos_tarefas enable row level security;

drop policy if exists projetos_frentes_admin on projetos_frentes;
create policy projetos_frentes_admin on projetos_frentes for all to authenticated
  using      (exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin'))
  with check (exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin'));

drop policy if exists projetos_tarefas_admin on projetos_tarefas;
create policy projetos_tarefas_admin on projetos_tarefas for all to authenticated
  using      (exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin'))
  with check (exists (select 1 from profiles p where p.id = auth.uid() and p.role = 'admin'));

-- ── SEED: frentes ────────────────────────────────────────────
insert into projetos_frentes (key, nome, cor, subtitulo, ordem) values
  ('LG','Lingrow',      '#3E7CB1','pré-lançamento na loja',      1),
  ('VZ','Viziom',       '#8B5CF6','onda 1 comercial começando',  2),
  ('CD','Cindy',        '#3FB950','paga o mês',                  3),
  ('MP','Marca pessoal','#C8A96E','constrói o próximo jogo',     4),
  ('OF','Oferta ARVEX', '#F85149','travada em OF-01',            5),
  ('PS','Pessoal',      '#8A98AD','não compete com o trabalho',  6)
on conflict (key) do update
  set nome=excluded.nome, cor=excluded.cor, subtitulo=excluded.subtitulo, ordem=excluded.ordem;

-- ── SEED: tarefas ────────────────────────────────────────────
insert into projetos_tarefas
  (frente, codigo, titulo, trilha, trilha_nota, ordem, executor, tamanho, maquina, bloqueado_por, nota, alerta)
values
-- LINGROW
('LG','LG-09','Aplicar migration 008 no SQL Editor do Supabase','Lançamento na loja','caminho crítico, nesta ordem',1,'vitor','P','M4',null,null,false),
('LG','LG-12','Decidir: completar 600 frases ou ajustar a promessa','Lançamento na loja',null,2,'vitor','P',null,null,'Decide o que a ficha da loja promete — vem antes de LG-14',false),
('LG','LG-10','Contrato de apps pagos Apple (PJ + DSA/UE + banco + W-8BEN)','Lançamento na loja',null,3,'vitor','M',null,null,'MAIOR ESPERA EXTERNA — sem ele o app não cobra. Comece por aqui',true),
('LG','LG-11','Terminar RevenueCat e entregar a chave appl_… + segredo do webhook','Lançamento na loja',null,4,'vitor','M',null,'LG-10',null,false),
('LG','LG-13','QA manual do fluxo no Expo Go','Lançamento na loja',null,5,'vitor','M',null,'LG-09',null,false),
('LG','LG-14','Aprovar ficha da loja e screenshots','Lançamento na loja',null,6,'vitor','P',null,'LG-12',null,false),
('LG','LG-15','Montar landing de waitlist','Demanda','encher antes de publicar',7,'eu','M','M2',null,'Possível duplicata de LG-04 — no pré-lançamento a waitlist É a página de captura',true),
('LG','LG-04','Página de captura e venda','Demanda',null,8,'eu','M','M2',null,'Confirmar se é a mesma coisa que LG-15 ou a página pós-lançamento',false),
('LG','LG-16','Gravar 4 vídeos do build-in-public','Demanda',null,9,'vitor','M','M1',null,null,false),
('LG','LG-17','Entrar em 15-20 comunidades ajudando','Demanda',null,10,'vitor','M','M3',null,'Canal mais barato e mais lento — comece cedo',false),
('LG','LG-01','Linha editorial — formatos de conteúdo','Demanda',null,11,'eu','M','M1',null,'Destrava LG-02',false),
('LG','LG-02','Criar roteiros','Demanda',null,12,'eu','M','M1','LG-01',null,false),
('LG','LG-03','Postar','Demanda',null,13,'vitor','P','M1',null,'Recorrente',false),
('LG','LG-07','Abordar 10 influencers','Demanda',null,14,'vitor','M','M3','LG-15',null,false),
('LG','LG-08','Definir a métrica que a semana move','Demanda',null,15,'vitor','P',null,null,'Waitlist? download? assinante? Sem alvo não há leitura',false),
('LG','LG-05','Atualizar o PostHog para revisar onde clicam','Produto',null,16,'eu','M','M4',null,'Confirmar se "postgate" é PostHog',false),
('LG','LG-06','Fazer melhorias no produto','Produto',null,17,'ambos','G','M4',null,'Escopo indefinido — precisa virar lista',true),
-- VIZIOM
('VZ','VZ-12','Preencher e assinar o contrato do closer','Comercial','onda 1 em andamento',1,'vitor','P','M3',null,'Antes de treinar alguém',false),
('VZ','VZ-11','Disparar as 15 mensagens da onda 1 — 8 longas, 7 curtas, manual','Comercial',null,2,'vitor','P','M3',null,'Manual de propósito: é teste A/B de formato, não volume',false),
('VZ','VZ-08','Coletar lista de leads p/ continuar o processo comercial','Comercial',null,3,'ambos','M','M3',null,'A onda 1 já consome lista — isto é reabastecer',false),
('VZ','VZ-05','Treinamento com vendedor','Comercial',null,4,'vitor','M','M3','VZ-12',null,false),
('VZ','VZ-10','Ajustar o system prompt em cima das falhas','Agente de IA','aprende com a onda 1',5,'eu','P','M3',null,'Me mande as falhas observadas — sem elas isto é chute',false),
('VZ','VZ-06','Estressar a plataforma (teste próprio)','Produto','responde se o produto se sustenta',6,'vitor','G',null,null,'Você já está vendendo na onda 1 — este teste virou urgente, não opcional',true),
('VZ','VZ-04','Criar o CRM da operação','Produto',null,7,'eu','G','M3',null,'D-1: reusar o arvex-crm (zero build) ou construir novo (semanas)?',true),
('VZ','VZ-09','Rotacionar a API Key do Evolution','Produto',null,8,'eu','P',null,null,'Vazou no chat em 14/07 — essa infra sustenta o atendimento da Cindy',true),
('VZ','VZ-07','Iniciar migração do produto para estrutura própria','Produto',null,9,'eu','XG','M4',null,'D-2: refazer um SaaS = MESES. Gate: só com cliente pagando',true),
('VZ','VZ-02','Definir posicionamento e linhas de conteúdo','Marca','só depois do posicionamento',10,'ambos','M','M5',null,'Destrava VZ-01 e VZ-03',false),
('VZ','VZ-01','Criar calendário editorial','Marca',null,11,'eu','M','M1','VZ-02',null,false),
('VZ','VZ-03','Criar carrosséis e roteiros de Reels','Marca',null,12,'eu','M','M1','VZ-02',null,false),
-- CINDY
('CD','CD-01','Fazer as calls','Caixa','vem antes de qualquer build',1,'vitor','P','M3',null,'Recorrente',false),
('CD','CD-07','Resolver os 5 leads quentes parados 17-19 dias','Caixa',null,2,'vitor','P','M3',null,'Dinheiro parado — sua janela de fechamento é de 1 dia',true),
('CD','CD-08','Limpar os 21 leads mortos do bolsão contato','Caixa',null,3,'eu','P','M3',null,null,false),
('CD','CD-09','Fechar os 3 gates (mídia · prompt da Carol · agente_pausado)','CRM','gates primeiro, builds depois',4,'ambos','M','M3',null,null,false),
('CD','CD-02','Agente de IA de atendimento','CRM',null,5,'eu','G','M3','CD-09','1ª da fila · Fase 3 já especificada',false),
('CD','CD-04','Módulo financeiro','CRM',null,6,'eu','G','M3',null,'2ª da fila · Proposta C aprovada',false),
('CD','CD-03','Sistema de IA do closer','CRM',null,7,'eu','G','M3',null,'3ª da fila · o mais sofisticado, o menos urgente',false),
('CD','CD-05','Escrever copy criativo do lançamento','Lançamento',null,8,'eu','M','M2',null,'Precisa da data do lançamento',false),
('CD','CD-06','Criar página do lançamento','Lançamento',null,9,'eu','M','M2','CD-05',null,false),
-- MARCA PESSOAL
('MP','MP-04','Refinar posicionamento','Base','destrava a produção',1,'vitor','M','M5',null,'O brand book já existe — é revisão, não criação',false),
('MP','MP-05','Criar o Projeto do carrossel no Claude','Base',null,2,'vitor','P','M1',null,'15 min · prompt e tool prontos, parados esperando só isso',false),
('MP','MP-01','Criar calendário de conteúdo','Produção',null,3,'eu','M','M1','MP-04',null,false),
('MP','MP-02','Escrever roteiros','Produção',null,4,'eu','M','M1','MP-01',null,false),
('MP','MP-03','Gravar vídeos','Produção',null,5,'vitor','M','M1',null,'Recorrente · o único gargalo que não terceiriza',false),
-- OFERTA
('OF','OF-01','Refinar a oferta definitiva','Definir','trava tudo abaixo',1,'ambos','M','M5',null,'PRIMEIRO DOMINÓ — destrava OF-02 a OF-05',false),
('OF','OF-09','Decidir de onde vem o próximo lead da oferta','Definir',null,2,'vitor','P','M3',null,'Hoje o pipeline próprio tem 1 nome',false),
('OF','OF-02','Criar o primeiro funil: webinário','Construir',null,3,'ambos','G','M2','OF-01',null,false),
('OF','OF-05','Escrever copy do criativo','Construir',null,4,'eu','M','M2','OF-01',null,false),
('OF','OF-03','Gravar ou criar criativo','Construir',null,5,'vitor','M','M1','OF-01',null,false),
('OF','OF-04','Criar página','Construir',null,6,'eu','M','M2','OF-01',null,false),
('OF','OF-06','Primeiros posts do perfil ARVEX (carrossel + vídeos com IA)','Distribuir',null,7,'eu','M','M1',null,null,false),
('OF','OF-07','Sequência de stories 2x/semana com CTA "me chama para implementar"','Distribuir',null,8,'ambos','P','M1',null,'Recorrente',false),
('OF','OF-08','Letícia Wendy: última chamada ou enterrar','Pipeline',null,9,'vitor','P','M3',null,'Call foi 30/06 — 34 dias; sua janela histórica máxima é 13',true),
-- PESSOAL
('PS','PS-01','Criar anúncio da mesa e dos 2 monitores','Vender',null,1,'ambos','P',null,null,null,false),
('PS','PS-02','Colocar o iPhone X na OLX','Vender',null,2,'ambos','P',null,null,null,false),
('PS','PS-03','Criar plano EUA e pesquisar passagens','Viagem',null,3,'ambos','M',null,null,'Quanto mais perto, mais caro — tem prazo implícito',false),
('PS','PS-04','Rio: pesquisar locais e falar com pessoas para ficar 1 mês','Viagem',null,4,'ambos','M',null,null,null,false)
on conflict (codigo) do nothing;
