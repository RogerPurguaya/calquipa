# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import models, fields, api

class account_analytic_account(models.Model):
	_inherit = 'account.analytic.account'

	dest_location = fields.Many2one('stock.location', "Ubicación Destino")

class stock_move(models.Model):
	_inherit = 'stock.move'

	@api.onchange('analitic_id')
	def onchange_cost_center(self):
		if self.analitic_id.dest_location:
			self.location_dest_id = self.analitic_id.dest_location.id
