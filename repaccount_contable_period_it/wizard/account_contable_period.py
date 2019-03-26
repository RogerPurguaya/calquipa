# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_contable_period(models.Model):

	_name='account.contable.period'
	_auto = False

	@api.multi
	def compute_saldo(self):
		y_comp = None
		y_tipe = None
		y_cuenta = None
		SaldoN = 0
		for x in self.sorted(key=lambda r: r.id_order):
			if y_comp != x.comprobante or y_tipe != x.type_document or y_cuenta != x.cuenta:
				y_comp = x.comprobante
				y_tipe = x.type_document
				y_cuenta = x.cuenta
				SaldoN= 0 
			SaldoN += x.debe
			SaldoN -= x.haber
			x.saldo = SaldoN

	@api.multi
	def saldo_total_get(self):
		y_comp = None
		y_tipe = None
		y_cuenta = None
		SaldoN = 0
		ids_obj = []
		for x in self.sorted(key=lambda r: r.id_order):
			if y_comp != x.comprobante or y_tipe != x.type_document or y_cuenta != x.cuenta:
				y_comp = x.comprobante
				y_tipe = x.type_document
				y_cuenta = x.cuenta
				for ids_ids in ids_obj:
					ids_ids.saldo_total=abs(SaldoN)
				ids_obj=[]
				SaldoN= 0
			SaldoN += x.debe
			SaldoN -= x.haber
			ids_obj.append(x)
		for ids_ids in ids_obj:
			ids_ids.saldo_total=abs(SaldoN)
		


	_order = "id_order"
	
	tipofiltro = fields.Char(string='TipoFiltro', size=30)
	periodo = fields.Char(string='Periodo',size=30)
	libro = fields.Char(string='Libro',size=30)
	voucher = fields.Char('Voucher',size=30)
	fecha = fields.Date('Fecha')
	type_document = fields.Char('Tipo de Documento',size=50)
	fecha_maturity = fields.Date('Fecha Vencimiento')
	ruc = fields.Char('RUC',size=20)
	partner = fields.Char(string='Partner',size=100)
	comprobante = fields.Char(string='Comprobante',size=100)
	cuenta = fields.Char(string='Cuenta',size=100)
	debe = fields.Float('Debe',digits=(12,2))
	haber = fields.Float('Haber',digits=(12,2))
	moneda = fields.Char('Divisa',size=32)
	importe = fields.Float('Importe Divisa',digits=(12,2))
	caja = fields.Char('Caja',size=100)
	comcaja = fields.Char('Com. Caja',size=100)
	fecha_ini_c = fields.Date('Fecha ini')
	fecha_fin_c = fields.Date('Fecha ini')
	partner_id = fields.Integer('id partner')
	account_id = fields.Integer('id account')
	periodo = fields.Char('periodo',size=30)
	refconcile = fields.Char('Reconciliación')	
	saldo = fields.Float('Saldo', compute='compute_saldo', digits=(12,2))
	tipocambio = fields.Float('Tipo Cambio', digits=(12,3))
	id_order = fields.Integer("Linea ID")
	reconcile_id = fields.Integer('verify')
	saldo_total = fields.Integer('Salto Acumulado Total', compute='saldo_total_get' , digits=(12,2))

	def init(self,cr):
		cr.execute("""
			DROP VIEW IF EXISTS account_contable_period;
			create or replace view account_contable_period as (

SELECT tabla.id as id_order,
tabla.lineaid as id,
	tabla.moveid,
	tabla.lineaid,
	tabla.tipofiltro,
	tabla.tipofiltrob,
	tabla.posicion,
	tabla.tipo,
	tabla.periodo,
	tabla.cuenta,
	tabla.partner,
	tabla.fecha,
	tabla.fecha_maturity,
	tabla.libro,
	tabla.voucher,
	tabla.ruc,
	tabla.comprobante,
	tabla.type_document,
	tabla.debe,
	tabla.haber,
		CASE
			WHEN tabla.posicion = 2 THEN tabla.caja
			ELSE ''::character varying
		END AS caja,
		CASE
			WHEN tabla.posicion = 2 THEN tabla.comcaja
			ELSE ''::character varying
		END AS comcaja,
	tabla.fecha_ini_c,
	tabla.fecha_fin_c,
	tabla.account_id,
	tabla.partner_id,
	tabla.moneda,
	tabla.importe,
	tabla.refconcile ,
	CASE WHEN tabla.moneda != 'PEN' or tabla.moneda is Null THEN tabla.tipocambio ELSE Null::numeric END as tipocambio,
	tabla.reconcile_id
   FROM ( SELECT row_number() OVER () AS id,
			m.lineaid,
			m.moveid,
			m.tipofiltro,
			m.tipofiltrob,
			m.posicion,
			m.tipo,
			m.periodo,
			m.cuenta,
			m.partner,
			m.fecha,
			m.fecha_maturity,
			m.libro,
			m.voucher,
			m.ruc,
			m.comprobante,
			m.type_document,
			m.debe,
			m.haber,
			m.caja,
			m.comcaja,
			m.fecha_ini_c,
			m.fecha_fin_c,
			m.account_id,
			m.partner_id,
			m.moneda,
			m.importe,
			m.refconcile,
			m.tipocambio,
			m.reconcile_id
		   FROM ( SELECT DISTINCT t.lineaid,
					t.moveid,
					t.tipofiltro,
					t.tipofiltrob,
					t.posicion,
					t.tipo,
					t.periodo,
					t.cuenta,
					t.partner,
					t.fecha,
					t.fecha_maturity,
					t.libro,
					t.voucher,
					t.ruc,
					t.comprobante,
					t.type_document,
					t.debe,
					t.haber,
					t.caja,
					t.comcaja,
					t.fecha_ini_c,
					t.fecha_fin_c,
					t.account_id,
					t.partner_id,
					t.moneda,
					t.importe,
					t.refconcile,
					t.tipocambio,
					t.reconcile_id
				   FROM ( SELECT account_move_line.id AS lineaid,
							am.id AS moveid,
							account_account.type AS tipofiltro,
							aa.type AS tipofiltrob,
								CASE
									WHEN account_account.type::text = 'payable'::text AND account_move_line.debit = 0::numeric THEN 1
									WHEN account_account.type::text = 'receivable'::text AND account_move_line.credit = 0::numeric THEN 1
									ELSE 2
								END AS posicion,
							aj.type AS tipo,
							ap.name AS periodo,
							account_account.code AS cuenta,
							res_partner.name AS partner,
							account_move_line.date AS fecha,
							account_move_line.date_maturity AS fecha_maturity,
							aj.code AS libro,
							account_move.name AS voucher,
							res_partner.type_number AS ruc,
							account_move_line.nro_comprobante AS comprobante,
							account_move_line.debit AS debe,
							account_move_line.credit AS haber,
							aj.code AS caja,
							am.name AS comcaja,
							ap.date_start AS fecha_ini_c,
							ap.date_stop AS fecha_fin_c,
							account_account.id AS account_id,
							res_partner.id AS partner_id,
							res_currency.name AS moneda,
							account_move_line.amount_currency AS importe,
							amr.name as refconcile,
							it_type_document.code as type_document,
							account_move_line.currency_rate_it  as tipocambio,
							coalesce(account_move_line.reconcile_id,-1) as reconcile_id
						   FROM account_move_line
							 LEFT JOIN account_account ON account_account.id = account_move_line.account_id
							 LEFT JOIN account_move ON account_move_line.move_id = account_move.id
							 LEFT JOIN res_partner ON account_move_line.partner_id = res_partner.id
							 LEFT JOIN account_period ON account_period.id = account_move.period_id
							 LEFT JOIN account_journal ON account_journal.id = account_move_line.journal_id
							 LEFT JOIN account_journal aj ON account_move_line.journal_id = aj.id
							 LEFT JOIN account_move am ON account_move_line.move_id = am.id
							 LEFT JOIN account_period ap ON am.period_id = ap.id
							 LEFT JOIN account_account aa ON aa.id = account_move_line.account_id
							 LEFT JOIN res_currency ON account_move_line.currency_id = res_currency.id
							 LEFT JOIN it_type_document ON it_type_document.id = account_move_line.type_document_id
							 LEFT JOIN account_move_reconcile amr on amr.id = (SELECT 
							CASE WHEN account_move_line.reconcile_id is not Null THEN account_move_line.reconcile_id
							WHEN account_move_line.reconcile_partial_id is not Null THEN account_move_line.reconcile_partial_id
							ELSE Null END AS refconcil FROM account_move_line amlcon where amlcon.id = account_move_line.id)
						  WHERE account_move.state::text = 'posted' AND   account_account.type in ('payable', 'receivable')
						) t
				  ORDER BY t.partner,t.cuenta, t.comprobante,t.type_document, t.fecha, t.posicion) m) tabla





						)""")

