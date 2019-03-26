# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv


class vst_square_foreign_currency(models.Model):
	_name='vst.square.foreign.currency'
	_auto=False
	
	
	move_id = fields.Many2one('account.move','Move Id')
	asiento = fields.Char('Asiento', size=64)
	periodo = fields.Char('Periodo', size=64)
	libro = fields.Char('Libro', size=64)
	voucher = fields.Char('Voucher', size=64)
	periodo_orden = fields.Integer('Periodo orden', size=64)
	debit = fields.Float('Debe', digits=(12,2))
	credit = fields.Float('Haber', digits=(12,2))
	debit_me = fields.Float('Debe M.E', digits=(12,2))
	credit_me = fields.Float('Haber M.E', digits=(12,2))
	diff_mn = fields.Float('Diff M.N', digits=(12,2))
	diff_me = fields.Float('Diff M.E', digits=(12,2))
	
	
	def init(self,cr):
		cr.execute(""" 
			DROP VIEW IF EXISTS vst_square_foreign_currency;
			CREATE OR REPLACE VIEW vst_square_foreign_currency AS 
			SELECT 
				row_number() OVER () as id,
				am.id as move_id,
				am.name as asiento,
				ap.name as periodo,
				aj.code as libro,
				am.name as voucher,
				periodo_num(ap.name) as periodo_orden,
				sum(aml.debit) as debit,
				sum(aml.credit) as credit,
				sum(aml.debit_me) as debit_me,
				sum(aml.credit_me)as credit_me, 
				sum(aml.debit)-sum(aml.credit) as diff_mn, 
				SUM(aml.debit_me)-sum(aml.credit_me) as diff_me 
			FROM 
				account_move_line AS aml JOIN 
				account_move AS am ON aml.move_id = am.id JOIN
				account_period AS ap ON am.period_id = ap.id JOIN
				account_journal AS aj ON aj.id = am.journal_id

			GROUP BY am.id, ap.name,aj.code
			HAVING (SUM(debit)-sum(credit))!=0 or (SUM(debit_me)-sum(credit_me))!=0
			ORDER BY ap.name
;
		""")
	
	def make_calculate_differences(self, cr, uid, ids, analytic_id,account_id_t,context):
		#raise osv.except_osv('Alerta','Listo para implemetar el asiento de cambio')
		#Configuracion
		config_obj_id = self.pool.get('exchange.diff.config').search(cr, uid, [])
		if len(config_obj_id) == 0:
			raise osv.except_osv('Alerta','Debe configurar las diferencias de cambio en el menu Contabilidad/Miscelaneous')
		config_obj = self.pool.get('exchange.diff.config').browse(cr, uid, config_obj_id[0], context)
		if config_obj.earn_account_id.id == False:
			raise osv.except_osv('Alerta','Debe configurar una cuenta para las ganancias')
		if config_obj.lose_account_id.id == False:
			raise osv.except_osv('Alerta','Debe configurar una cuenta para las perdidas')


		for item in self.browse(cr, uid, ids, context):
			if item.diff_me != 0:
				#self.pool.get('account.move').write(cr, uid, [item.move_id.id], {'state': 'draft'}, context)

				vals = {
					'tax_amount': 0.0, 
					'name': 'CUADRE MONEDA EXTRANJERA',
					'ref': False,
					'nro_comprobante': False,
					'currency_id': False, 
					'debit': 0,
					'credit': 0, 
					'date_maturity': False, 
					'date': item.move_id.date,
					'amount_currency': 0, 
					'currency_rate_it': 1.00,
					'account_id': account_id_t,
					'partner_id': False,
					'debit_me': abs(item.diff_me) if item.diff_me < 0 else 0,
					'credit_me': abs(item.diff_me) if item.diff_me > 0 else 0, 
					'move_id': item.move_id.id,
					'analytic_account_id': analytic_id  if item.diff_me <0 else False,
					'square_flag': True,
				}

				debit_me_write =abs(item.diff_me) if item.diff_me < 0 else 0
				credit_me_write = abs(item.diff_me) if item.diff_me > 0 else 0

				print 'New Line', vals
				new_line = self.pool.get('account.move.line').create(cr, uid, vals, context)
				#self.pool.get('account.move').post(cr, uid, [item.move_id.id], context=None)
				self.pool.get('account.move.line').write(cr,uid,new_line,{'debit_me':debit_me_write,'credit_me':credit_me_write},context)
		return ids