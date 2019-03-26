# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import models, fields, api

class stock_picking(models.Model):
	_inherit = 'stock.picking'
	
	@api.onchange('picking_type_id')
	def onchange_picking_type_id(self):
		if self.picking_type_id.id:
			for i in self.move_lines:
				i.location_id = self.picking_type_id.default_location_src_id.id
				i.location_dest_id= self.picking_type_id.default_location_dest_id