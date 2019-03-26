# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields

class stock_location(osv.osv):
	_inherit='stock.location'

	_columns={
		'check_ajuste_inventario':fields.boolean(u'Ajuste de Inventario'),
	}