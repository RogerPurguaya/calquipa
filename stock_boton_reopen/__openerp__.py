# -*- encoding: utf-8 -*-
{
	'name': 'Ocultar Campos en Albaranes IT',
	'category': 'stock',
	'author': 'ITGrupo',
	'depends': ['stock_cancel','kardex'],
	'version': '1.0',
	'description':"""
	Vuelve visible solo para algunos usuarios: \n
	- boton reopen \n
	- campo precio unitario \n
	- campo factura \n
	""",
	'auto_install': False,
	'demo': [],
	'data':	['stock_picking_view.xml','security/almacen_reopen.xml'],
	'installable': True
}
