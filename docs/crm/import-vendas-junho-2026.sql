-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║          CRM ARVEX — Import de vendas fechadas (junho/2026 · Cindy)        ║
-- ╠═══════════════════════════════════════════════════════════════════════════╣
-- ║ Data:  2026-07-01 (atualizado 2026-07-08 — + Tamires)                     ║
-- ║ Fonte: planilha enviada pelo Vitor (7 vendas de junho não lançadas)        ║
-- ║ Autor: @data-engineer (Dara)                                              ║
-- ║                                                                           ║
-- ║ O QUE FAZ (por venda):                                                    ║
-- ║   1. Cria um LEAD com status='fechado' → aparece na coluna Fechado da     ║
-- ║      Pipeline (expert=Cindy Batista, closer/resp=Vitor).                  ║
-- ║   2. Cria a VENDA no Financeiro (vendas) ligada ao lead (lead_id).        ║
-- ║   3. Gera as PARCELAS (parcelas) ligadas à venda (venda_id).              ║
-- ║                                                                           ║
-- ║ REGRAS DE PARCELA:                                                        ║
-- ║   • Vencimentos mensais a partir da data da venda (exceto Marília).       ║
-- ║   • Valor dividido igual; a ÚLTIMA parcela absorve os centavos p/ somar   ║
-- ║     exatamente o valor_total.                                             ║
-- ║   • status: vencimento <= hoje → 'pago' (pago_em = vencimento);           ║
-- ║             vencimento  > hoje → 'pendente'.                              ║
-- ║                                                                           ║
-- ║ SUPOSIÇÕES (revisar se necessário):                                       ║
-- ║   • "Vencida = paga": parcela de cartão já vencida assume-se liquidada    ║
-- ║     pela operadora; Pix vencido assume-se recebido. Ajuste manual no CRM  ║
-- ║     se alguma ainda estiver pendente.                                     ║
-- ║   • Roberta (12x R$516) e Aline (10x R$500): o valor informado por        ║
-- ║     parcela inclui JUROS do cartão. Como o Financeiro rastreia o valor    ║
-- ║     DA VENDA, as parcelas foram ajustadas p/ somar o valor_total          ║
-- ║     (R$4.997 e R$4.500). O nº de parcelas foi mantido.                    ║
-- ║   • responsavel_cobranca = "Vitor" em todas.                             ║
-- ║                                                                           ║
-- ║ SEGURANÇA:                                                                ║
-- ║   • Idempotente: pula a venda se já existir (mesmo cliente + valor).      ║
-- ║   • Roda dentro de transação (BEGIN/COMMIT) — tudo ou nada.               ║
-- ║   • A função helper é removida no fim (DROP).                             ║
-- ║                                                                           ║
-- ║ COMO APLICAR:                                                             ║
-- ║   1. Supabase Dashboard → SQL Editor → colar tudo → Run                   ║
-- ║   2. Esperado: a query final lista as 7 vendas com nº de parcelas e       ║
-- ║      quanto já consta como pago.                                          ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

begin;

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Função helper: cria lead fechado + venda + parcelas mensais
-- ─────────────────────────────────────────────────────────────────────────────
create or replace function _imp_venda_mensal(
  p_cliente        text,
  p_valor          numeric,
  p_produto        text,
  p_condicao       text,      -- 'avista' | 'parcelado' | 'entrada_saldo'
  p_metodo         text,      -- 'pix' | 'cartao' | 'boleto'
  p_total_parcelas int,
  p_data_venda     date,
  p_obs            text default null
) returns void language plpgsql as $$
declare
  v_lead        uuid;
  v_venda       uuid;
  v_hoje        date := current_date;
  v_i           int;
  v_venc        date;
  v_valor_base  numeric(10,2);
  v_valor_parc  numeric(10,2);
  v_acumulado   numeric(10,2) := 0;
  v_status      text;
  v_pago        date;
  v_prod_obs    text := p_produto || coalesce(' — ' || p_obs, '');
begin
  -- idempotência: não duplica venda já existente do mesmo cliente/valor
  if exists (select 1 from vendas where cliente = p_cliente and valor_total = p_valor) then
    raise notice 'Pulando %, venda ja existe', p_cliente;
    return;
  end if;

  -- 1) LEAD fechado → Pipeline (coluna Fechado)
  insert into leads (nome, expert, closer, resp, socio, ticket, status, origem, data_call, obs)
  values (p_cliente, 'Cindy Batista', 'Vitor', 'Vitor', 'Vitor', p_valor, 'fechado',
          'Mentoria Cindy', to_char(p_data_venda, 'DD/MM/YYYY'), v_prod_obs)
  returning id into v_lead;

  -- 2) VENDA → Financeiro
  insert into vendas (lead_id, cliente, valor_total, expert, condicao_negociada, responsavel_cobranca, observacao)
  values (v_lead, p_cliente, p_valor, 'Cindy Batista', p_condicao, 'Vitor',
          p_produto || ' · ' || p_total_parcelas || 'x ' || upper(p_metodo) || coalesce(' · ' || p_obs, ''))
  returning id into v_venda;

  -- 3) PARCELAS (mensais; última absorve centavos)
  v_valor_base := trunc(p_valor / p_total_parcelas, 2);
  for v_i in 1..p_total_parcelas loop
    v_venc := (p_data_venda + ((v_i - 1) || ' months')::interval)::date;
    if v_i < p_total_parcelas then
      v_valor_parc := v_valor_base;
      v_acumulado  := v_acumulado + v_valor_base;
    else
      v_valor_parc := p_valor - v_acumulado;   -- fecha o total exato
    end if;
    if v_venc <= v_hoje then
      v_status := 'pago';     v_pago := v_venc;
    else
      v_status := 'pendente'; v_pago := null;
    end if;
    insert into parcelas (venda_id, numero, total_parcelas, valor, vencimento, status, pago_em, metodo)
    values (v_venda, v_i, p_total_parcelas, v_valor_parc, v_venc, v_status, v_pago, p_metodo);
  end loop;
end;
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. As 6 vendas com parcelas mensais (ou à vista)
-- ─────────────────────────────────────────────────────────────────────────────
--                       cliente            valor    produto        condicao      metodo   nº   data_venda     obs
select _imp_venda_mensal('Kamila Torquato', 4500.00, 'Mentoria',    'parcelado',  'cartao', 10,  date '2026-06-03');

-- Roberta paga 12x R$516 no cartao (com juros); valor ajustado pra somar o total da venda (ver topo do arquivo)
select _imp_venda_mensal('Roberta',         4997.00, 'Mentoria',    'parcelado',  'cartao', 12,  date '2026-06-08');

-- Aline (Renovacao) paga 10x R$500 no cartao (com juros); valor ajustado pra somar o total da venda
select _imp_venda_mensal('Aline',           4500.00, 'Mentoria',    'parcelado',  'cartao', 10,  date '2026-06-16', 'Renovacao');

select _imp_venda_mensal('Alanna',          2500.00, 'Mentoria',    'avista',     'pix',    1,   date '2026-06-15', 'Renovacao');
select _imp_venda_mensal('Willian',         4500.00, 'Mentoria',    'parcelado',  'cartao', 12,  date '2026-06-29');

-- Tamires: PLACEHOLDER, valor/condicao/data a confirmar com Vitor
select _imp_venda_mensal('Tamires',         4500.00, 'Mentoria',    'parcelado',  'cartao', 10,  date '2026-06-20');

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Marília — Consultoria R$10.000, 2x Pix em datas coladas (não mensal)
--    R$5.000 em 18/06 + R$5.000 em 19/06 → entrada_saldo, ambas pagas
-- ─────────────────────────────────────────────────────────────────────────────
do $$
declare
  v_lead  uuid;
  v_venda uuid;
begin
  if exists (select 1 from vendas where cliente = 'Marília' and valor_total = 10000.00) then
    raise notice 'Pulando Marilia, venda ja existe';
    return;
  end if;

  insert into leads (nome, expert, closer, resp, socio, ticket, status, origem, data_call, obs)
  values ('Marília', 'Cindy Batista', 'Vitor', 'Vitor', 'Vitor', 10000.00, 'fechado',
          'Mentoria Cindy', '18/06/2026', 'Consultoria')
  returning id into v_lead;

  -- observacao: Consultoria, 2x Pix - R$5.000 em 18/06 + R$5.000 em 19/06
  insert into vendas (lead_id, cliente, valor_total, expert, condicao_negociada, responsavel_cobranca, observacao)
  values (v_lead, 'Marília', 10000.00, 'Cindy Batista', 'entrada_saldo', 'Vitor',
          'Consultoria 2x Pix')
  returning id into v_venda;

  insert into parcelas (venda_id, numero, total_parcelas, valor, vencimento, status, pago_em, metodo) values
    (v_venda, 1, 2, 5000.00, date '2026-06-18', 'pago', date '2026-06-18', 'pix'),
    (v_venda, 2, 2, 5000.00, date '2026-06-19', 'pago', date '2026-06-19', 'pix');
end;
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. Limpeza da função helper
-- ─────────────────────────────────────────────────────────────────────────────
drop function if exists _imp_venda_mensal(text, numeric, text, text, text, int, date, text);

commit;

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. VALIDAÇÃO — confira as vendas importadas (rode junto; é só SELECT)
-- ─────────────────────────────────────────────────────────────────────────────
select v.cliente,
       v.valor_total,
       v.condicao_negociada                                as condicao,
       count(p.id)                                         as parcelas,
       count(p.id) filter (where p.status = 'pago')        as pagas,
       count(p.id) filter (where p.status = 'pendente')    as pendentes,
       sum(p.valor)                                        as soma_parcelas,
       max(l.status)                                       as pipeline_status
from   vendas v
join   parcelas p on p.venda_id = v.id
left   join leads l on l.id = v.lead_id
where  v.cliente in ('Kamila Torquato','Roberta','Marília','Aline','Alanna','Willian','Tamires')
group  by v.cliente, v.valor_total, v.condicao_negociada
order  by v.cliente;

-- ─────────────────────────────────────────────────────────────────────────────
-- COMO REVERTER (rode SÓ se precisar desfazer o import):
--   begin;
--     delete from vendas
--      where cliente in ('Kamila Torquato','Roberta','Marília','Aline','Alanna','Willian','Tamires');
--     -- parcelas caem automaticamente (ON DELETE CASCADE)
--     delete from leads
--      where nome in ('Kamila Torquato','Roberta','Marília','Aline','Alanna','Willian','Tamires')
--        and status = 'fechado' and expert = 'Cindy Batista';
--   commit;
-- ─────────────────────────────────────────────────────────────────────────────
-- FIM — import-vendas-junho-2026.sql
