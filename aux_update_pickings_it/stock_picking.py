# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import models, fields, api

class stock_picking(models.Model):
	_inherit = 'stock.picking'

	@api.one
	def update_picking(self):
		picking_ids = self.env['stock.picking'].search([('name','like','Borrador'),('state','=','done')], order='date asc')
		for picking in picking_ids:
			picking.do_transfer()
		picking_ids = self.env['stock.picking'].search([('state','=','done')])
		for picking in picking_ids:
			picking.internal_name = picking.name