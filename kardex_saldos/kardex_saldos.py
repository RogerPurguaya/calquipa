# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields

class kardex_saldos(osv.osv):
	_name='kardex.saldos'
	_auto = False
	_columns={
		'almacen': fields.char('Almacen', size=200),
		'default_code':fields.char('Codigo',size=20),
		'producto': fields.char('Producto', size=200),
		'category_id':fields.char('Categoria',size=50),
		'unidad':fields.char('Unidad',size=20),
		'ingreso':fields.float('Ingreso', digits=(12,2)),
		'salida':fields.float('Salida', digits=(12,2)),
		'saldof': fields.float('Saldo Fisico', digits=(12,2)),
		'debit':fields.float('Debit', digits=(12,2)),
		'credit':fields.float('Credit', digits=(12,2)),
		'saldov': fields.float('Saldo Valorado', digits=(12,2)),
	}
kardex_saldos()
