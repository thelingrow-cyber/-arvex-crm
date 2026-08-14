-- =====================================================================
-- leads: dono também para quem entra pelo agente + policy de edição (Fase 2)
-- Continuação de docs/crm/leads-owner-e-auditoria.sql (2026-07-29)
-- Autor: Orion (aiox-master) · 2026-08-14 · tarefa CD-11
--
-- O QUE ACONTECEU: o trigger trg_leads_set_owner de 2026-07-29 usa auth.uid(),
-- que é NULL quando o insert vem do agente SDR (service_role). Aquele arquivo
-- registrou isso como "aceitável". Não era: em 16 dias acumularam-se 102 leads
-- VIVOS sem dono nenhum — todos com origem 'whatsapp-agente-sdr' ou 'Respondi'.
-- Ninguém era responsável por 65% do funil ativo.
--
-- A FASE 2 daquele arquivo ficou comentada esperando "a maioria dos leads ativos
-- ter dono". A condição foi cumprida hoje: 156 vivos, 156 com dono.
--
-- ESTE ARQUIVO É IDEMPOTENTE. Rollback completo no fim.
-- =====================================================================

begin;

-- ---------------------------------------------------------------------
-- 1. o trigger passa a ter plano B: se não há usuário logado (insert de
--    serviço), o lead nasce com o SDR de plantão. Sem hardcode de pessoa:
--    lê quem tem role 'sdr' em profiles. Se não houver SDR cadastrado,
--    volta ao comportamento antigo (NULL) em vez de falhar o insert.
-- ---------------------------------------------------------------------
create or replace function public.leads_set_owner()
returns trigger
language plpgsql
security definer            -- precisa ler profiles mesmo vindo do agente
set search_path = public
as $$
begin
  if new.owner_id is null then
    new.owner_id := auth.uid();
  end if;

  if new.owner_id is null then
    select p.id into new.owner_id
      from public.profiles p
     where p.role = 'sdr'
     order by p.name
     limit 1;
  end if;

  return new;
end;
$$;

comment on function public.leads_set_owner() is
  'Todo lead nasce com dono: quem inseriu (auth.uid()) ou, se veio de serviço (agente SDR), o SDR de plantão. Ver docs/crm/leads-owner-v2-sdr-fallback.sql';

-- trigger já existe desde 2026-07-29; recriado aqui só para garantir o vínculo
drop trigger if exists trg_leads_set_owner on public.leads;
create trigger trg_leads_set_owner
  before insert on public.leads
  for each row execute function public.leads_set_owner();

-- ---------------------------------------------------------------------
-- 2. FASE 2 — a policy que estava comentada esperando esta condição.
--    `owner_id is null` continua aberto de propósito: os leads antigos
--    (perdidos/fechados) sem dono seguem editáveis, ninguém fica travado.
-- ---------------------------------------------------------------------
drop policy if exists leads_update on public.leads;
create policy leads_update on public.leads
  for update to authenticated
  using       (owner_id = auth.uid() or owner_id is null or is_admin())
  with check  (owner_id = auth.uid() or owner_id is null or is_admin());

commit;

-- =====================================================================
-- ESTADO EM 2026-08-14, DEPOIS DESTE ARQUIVO
-- =====================================================================
-- 395 leads · 156 vivos, todos com dono (Thalita 144, Vitor 11, Gabriel 1)
-- Distribuição feita hoje: topo de funil (contato/qualificado/followup) para a
-- SDR; o que já é de closer (quente/call) para o Vitor.
-- 'Victor P' (Pacheco) seguiu sem atribuição — 21 leads, todos já
-- perdidos/fechados. É histórico, não operação.
--
-- AINDA ABERTO: `leads_select` é USING (true) — qualquer conta autenticada LÊ
-- a base inteira. Não foi mexido aqui de propósito: fechar leitura muda o que
-- cada tela mostra e precisa de decisão do Vitor, não de migration.
-- =====================================================================

-- =====================================================================
-- ROLLBACK
-- =====================================================================
-- begin;
--   drop policy if exists leads_update on public.leads;
--   create policy leads_update on public.leads for update using (true);
--   -- e restaurar a versão anterior de leads_set_owner() (só auth.uid())
-- commit;
