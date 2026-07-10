-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║   CRM ARVEX — Marca parcelas de cartão como quitadas (vendas junho/2026)   ║
-- ╠═══════════════════════════════════════════════════════════════════════════╣
-- ║ Data:  2026-07-10                                                          ║
-- ║ Motivo: no pagamento via cartão, a operadora garante/repassa o valor       ║
-- ║   total pra ARVEX — a dívida parcelada é do cliente com a operadora, não   ║
-- ║   com a ARVEX. Logo, toda parcela de cartão já está quitada do ponto de    ║
-- ║   vista financeiro da ARVEX, independente da data de vencimento futura.    ║
-- ║ Escopo: só as 5 vendas em cartão do import de junho/2026 (Cindy).          ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

begin;

update parcelas p
set    status = 'pago', pago_em = p.vencimento
from   vendas v
where  p.venda_id = v.id
  and  p.metodo = 'cartao'
  and  p.status in ('pendente', 'atrasado')
  and  v.expert = 'Cindy Batista'
  and  v.cliente in ('Kamila Torquato','Roberta','Aline','Willian','Tamires');

commit;

-- validação
select v.cliente, v.condicao_negociada as condicao,
       count(p.id) as parcelas,
       count(p.id) filter (where p.status = 'pago') as pagas,
       count(p.id) filter (where p.status = 'pendente') as pendentes
from   vendas v
join   parcelas p on p.venda_id = v.id
where  v.cliente in ('Kamila Torquato','Roberta','Aline','Willian','Tamires')
group  by v.cliente, v.condicao_negociada
order  by v.cliente;
