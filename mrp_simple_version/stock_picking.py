# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp

from openerp import models, fields, api
from openerp.osv import osv
from openerp.tools.translate import _

import pprint

class stock_picking(models.Model):
	_inherit='stock.picking'
	
	production_id = fields.Many2one('mrp.production', 'Produccion')