# -*- encoding: utf-8 -*-
{
	'name': 'Comprabación de Disponibilidad IT',
	'category': 'stock',
	'author': 'ITGrupo',
	'depends': ['stock_picking_partner','stock','kardex_saldos','product'],
	'version': '1.0',
	'description':"""
	Comprobacion de disponibilidad personalizada 
	""",
	'auto_install': False,
	'demo': [],
	'data':	['comprobar_disponibilidad_view.xml','disponibilidad_orden_produccion_view.xml','security/almacen_forzar_security.xml'],
	'installable': True
}
