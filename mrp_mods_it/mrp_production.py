# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp

from openerp import models, fields, api
from openerp.osv import osv
from openerp.tools.translate import _

import pprint

class mrp_production(models.Model):
	_inherit='mrp.production'
	
	nro_viajes = fields.Integer('Nro. de Viajes')
