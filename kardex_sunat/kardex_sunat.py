# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields

class category_product_sunat(osv.osv):
	_name="category.product.sunat"

	_columns={
		'name':fields.char('Nombre de categoria'),
		'code':fields.char(u'Código de categoria')
	}

class category_uom_sunat(osv.osv):
	_name="category.uom.sunat"

	_columns={
		'name':fields.char('Nombre de categoria'),
		'code':fields.char(u'Código de categoria')
	}