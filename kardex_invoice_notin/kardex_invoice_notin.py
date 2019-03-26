# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields

class kardex_invoice_notin(osv.osv):
	_name='kardex.invoice.notin'
	_auto = False
	_columns={
		'origin': fields.char('Origen', size=200),
		'numdoc':fields.char('Número de factura',size=20),
		'partner': fields.char('Proveedor/Cliente', size=200),
		'fecha':fields.char('Fecha de factura',size=50),
	}
	
kardex_invoice_notin()
