# -*- coding: utf-8 -*-

from openerp import models, fields, api

class analisis_entrega_rendir_rep(models.Model):

	_name='analisis.entrega.rendir.rep'
	_auto = False

	rendicion_id = fields.Integer(string='Rendicion ID')
	partner_id = fields.Integer(string='Partner ID')
	libro = fields.Char(string='Libro',size=30)
	periodo = fields.Char('Periodo')
	fecha = fields.Date(string='Fecha')
	cuenta = fields.Char(string='Cuenta',size=100)
	rendicion = fields.Char(string='Rendicion',size=100)
	code = fields.Char(string='Codigo',size=100)
	nro_comprobante = fields.Char('Nro. Comprobante')
	empresa = fields.Char('Empresa')
	ingresos = fields.Float(string='Ingresos',  digits=(12,2))
	gasto = fields.Float(string='Gastos', digits=(12,2))
	balance = fields.Float(string='Balance', digits=(12,2))
	importe_me = fields.Float(string='Importe M.E.', digits=(12,2))
	moneda = fields.Char(string='Moneda',size=100)
	tipo_c = fields.Float(string='T.C.',digits=(12,3))
	

	def init(self,cr):
		cr.execute("""
			create or replace view analisis_entrega_rendir_rep as (


select row_number() OVER() as id,* from
(

select
t1.rendicion_id,
t8.id as partner_id,
t3.code as libro,
t2.code as periodo,
t1.date as fecha,
t4.code as cuenta,
t1.rendicion_name as rendicion,
t7.code,
t6.nro_comprobante,
t8.name as empresa,
t1.debit as ingresos,
t1.credit as gasto,
t1.debit-t1.credit as balance,
amount_currency as importe_me,
t5.name as moneda,
currency_rate_it as tipo_c


from account_move_line t1 
left join account_period t2 on t2.id=t1.period_id
left join account_journal t3 on t3.id=t1.journal_id
left join account_account t4 on t4.id=t1.account_id
left join res_currency t5 on t5.id=t1.currency_id
left join (
select z1.move_id,z1.type_document_id,z1.nro_comprobante,z1.partner_id from account_move_line z1 
right join ( 
select move_id,min(id) as id from account_move_line 
where rendicion_id is not null
and account_id <> ( select deliver_account_mn from main_parameter)
and account_id <> ( select deliver_account_me from main_parameter)
and (journal_id=(select loan_journal_mn from main_parameter) or journal_id=(select loan_journal_me from main_parameter))  
group by move_id) lista on lista.id=z1.id) t6 on t6.move_id=t1.move_id
left join it_type_document t7 on t7.id=t6.type_document_id
left join res_partner t8 on t8.id=t6.partner_id
where rendicion_id is not null
and (account_id = ( select deliver_account_mn from main_parameter)
or account_id = ( select deliver_account_me from main_parameter) )
and (journal_id=(select loan_journal_mn from main_parameter) or journal_id=(select loan_journal_me from main_parameter))

---  este es el campo que permitira filtra en la lista 
order by balance desc,t1.date



) as T

						)""")