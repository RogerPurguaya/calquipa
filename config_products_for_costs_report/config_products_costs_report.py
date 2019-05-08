# -*- coding: utf-8 -*-

from openerp import models, fields, api

class config_products_costs_report(models.Model):
	_name = 'config.products.costs.report'

	product_id = fields.Many2one('product.product', string='Producto')


	@api.multi
	def name_get(self):
		result = []
		for record in self:
			name = 'Prod.: '+str(record.product_id.name)
			result.append((record.id, name))
		return result