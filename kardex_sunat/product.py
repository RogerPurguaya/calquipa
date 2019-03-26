# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields

class product_category(osv.osv):
	_inherit='product.category'

	_columns={
		'cod_sunat':fields.many2one('category.product.sunat',u'SUNAT Código tipo de existencia'),
	}

class product_uom(osv.osv):
	_inherit='product.uom'

	_columns={
		'cod_sunat':fields.many2one('category.uom.sunat',u'SUNAT Código'),
	}

class stock_location(osv.osv):
	_inherit='stock.location'

	_columns={
		'cod_sunat':fields.char(u'SUNAT Código'),
	}