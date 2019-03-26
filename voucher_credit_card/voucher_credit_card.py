# -*- coding: utf-8 -*-

from openerp import models, fields, api

class voucher_credit_card(models.Model):
	_name = 'voucher.credit.card'

	name = fields.Char('Codigo',size=6)
	entity = fields.Many2one('res.partner','Entidad')
	card = fields.Char('Tarjeta',size=50)
	means_payment_id = fields.Many2one('it.means.payment','Medio Pago')

	_rec_name= 'card'