# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv


class res_partner(models.Model):
	_inherit = 'res.partner'

	account_receivable_me = fields.Many2one('account.account', 'Cuenta a Cobrar M.E.')
	account_payable_me = fields.Many2one('account.account', 'Cuenta a Pagar M.E.')

class account_invoice(models.Model):
	_inherit = 'account.invoice'

	@api.onchange('currency_id')
	def onchange_currency_me(self):
		t = self.env['main.parameter'].search([])[0].currency_id
		if self.currency_id == t:
			if self.type == 'out_invoice' or self.type == 'out_refund':
				if self.partner_id.account_receivable_me:
					self.account_id = self.partner_id.account_receivable_me.id
				else:
					raise osv.except_osv('Alerta!', "No existe una cuenta para moneda extranjera.")
			if self.type == 'in_invoice' or self.type == 'in_refund':
				if self.partner_id.account_payable_me:
					self.account_id = self.partner_id.account_payable_me.id
				else:
					raise osv.except_osv('Alerta!', "No existe una cuenta para moneda extranjera.")