# -*- encoding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import osv
from openerp import models, fields, api

class account_voucher(osv.osv):
	_inherit='account.voucher'
	
	monto_retention = fields.Float('Monto Retencion', digits=(12,2))
	
	def action_move_line_create(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		move_pool = self.pool.get('account.move')
		move_line_pool = self.pool.get('account.move.line')
		
		parametro_id = self.pool.get('main.parameter').search(cr, uid, [])
		parametro = self.pool.get('main.parameter').browse(cr, uid, parametro_id[0],context)
		for voucher in self.browse(cr, uid, ids, context=context):
			if voucher.amount != 0.00:
				if voucher.journal_id.is_retention:
					#Validaciones
					if parametro.partner_sunat.id == False:
						raise osv.except_osv('Acción Inválida!', 'Debe configurar un cliente para retenciones Sunat')
					if parametro.retention_document_type.id == False:
						raise osv.except_osv('Acción Inválida!', 'Debe configurar un tipo de documento para retenciones Sunat')
					if parametro.tax_code_id.id == False:
						raise osv.except_osv('Acción Inválida!', 'Debe configurar un impuesto para retenciones Sunat')
					
					super(account_voucher,self).action_move_line_create(cr, uid, [voucher.id], context)
					#voucher_tmp = self.browse(cr,uid,ids[0],context)
					
					cuentas = [
						voucher.journal_id.default_debit_account_id.id 
					]

					vals = {
						'dec_reg_type_document_id': parametro.retention_document_type.id,
						'dec_reg_nro_comprobante': voucher.reference,
						'com_ret_amount': voucher.monto_retention,
					}
					self.pool.get('account.move').write(cr, uid, [voucher.move_id.id], vals, context)
				
					#Agregamos la referencia de la rendicion a las lineas de asiento contable
					for move_line in voucher.move_id.line_id:
						if move_line.account_id.id in cuentas:
							vals = {
								'nro_comprobante': voucher.reference,
								'partner_id': parametro.partner_sunat.id,
								'tax_code_id': parametro.tax_code_id.id,
							}
							self.pool.get('account.move.line').write(cr, uid, [move_line.id], vals, context)
					return True
				else:
					super(account_voucher,self).action_move_line_create(cr, uid, ids, context)
					return True
			else:
				raise osv.except_osv('Acción Inválida!', 'El monto a pagar no puede ser 0.00.')
		return True