# -*- encoding: utf-8 -*-
{
	'name': 'Fix stock name on duplicate IT',
	'category': 'stock',
	'author': 'ITGrupo',
	'depends': ['stock', 'stock_comprobar_disponibilidad_it', 'mrp_consumed_produced'],
	'version': '1.0',
	'description':"""
		Módulo que modifica el nombre del picking según la serie establecida en el el tipo de picking seleccionado al transferir un albarán duplicado.
	""",
	'auto_install': False,
	'demo': [],
	'data':	['stock_picking.xml'],
	'installable': True
}