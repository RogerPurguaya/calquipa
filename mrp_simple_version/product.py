# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp

from openerp import models, fields, api
from openerp.osv import osv
from openerp.tools.translate import _

class product_product(models.Model):
	_inherit='product.product'
	
	es_produccion = fields.Boolean('Es produccion', related='product_tmpl_id.es_produccion')
	
	
class product_product(models.Model):
	_inherit='product.template'
	
	es_produccion = fields.Boolean('Es produccion', default=False)
	
class product_uom(models.Model):
	_inherit='product.uom'
	
	es_produccion = fields.Boolean('Es produccion', default=False)