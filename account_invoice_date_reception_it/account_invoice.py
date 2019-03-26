# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
import datetime

class detalle_venta_invoice(models.Model):
	_name = 'detalle.venta.invoice'

	producto = fields.Many2one('product.product','Producto',required=True)
	monto_venta = fields.Float('Monto Venta',digits=(12,2))
	monto_flete = fields.Float('Monto Flete',digits=(12,2))
	invoice_id = fields.Many2one('account.invoice','Factura')

class account_invoice(models.Model):
	_inherit = 'account.invoice'

	date_reception = fields.Date('Fecha Recepción')	
	detalle_venta_ids = fields.One2many('detalle.venta.invoice','invoice_id','Detalle Ventas')

	@api.onchange('date_reception','payment_term')
	def onchange_date_reception(self):
		if self.date_reception:
			if self.payment_term.id:
				dia = datetime.datetime(year=int( self.date_reception.split('-')[0] ),month=int(self.date_reception.split('-')[1]),day=int(self.date_reception.split('-')[2]))
				if len(self.payment_term.line_ids)>0:
					dia = dia + datetime.timedelta(days=self.payment_term.line_ids[0].days)
				self.date_due = str(dia)[:10]
			else:
				self.date_due = self.date_reception


	@api.multi
	def onchange_payment_term_date_invoice(self, payment_term_id, date_invoice):
		return {}

	@api.multi
	def onchange_payment_term_date_invoice_reception(self, payment_term_id, date_reception):
		if not date_reception:
			date_reception = fields.Date.context_today(self)
		if not payment_term_id:
			# To make sure the invoice due date should contain due date which is
			# entered by user when there is no payment term defined
			return {'value': {'date_due': self.date_due or date_reception}}
		pterm = self.env['account.payment.term'].browse(payment_term_id)
		pterm_list = pterm.compute(value=1, date_ref=date_reception)[0]
		if pterm_list:
			return {'value': {'date_due': max(line[0] for line in pterm_list)}}
		else:
			raise except_orm(_('Insufficient Data!'),
				_('The payment term of supplier does not have a payment term line.'))

class sale_order(models.Model):
	_inherit = 'sale.order'

	p_padre = fields.Char('Pedido Padre')