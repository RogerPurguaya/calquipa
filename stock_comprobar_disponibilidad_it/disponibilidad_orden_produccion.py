# -*- coding: utf-8 -*-

from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs

import datetime

class mrp_production(models.Model):
	_inherit = 'mrp.production'

	@api.one
	def disponibilidad_orden_produccion(self):
		po = self.env['stock.picking'].search([('origin','=',self.name),('move_lines.location_id.id','=',self.move_lines.location_id.id)])
		print po
		for i in po:
			print i.get_disponibilidad()