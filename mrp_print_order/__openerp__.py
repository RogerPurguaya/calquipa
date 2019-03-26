# -*- encoding: utf-8 -*-
{
	'name': 'Production Order Report IT',
	'category': 'manufacture',
	'author': 'ITGrupo',
	'depends': ['stock', 'stock_comprobar_disponibilidad_it'],
	'version': '1.0',
	'description':"""
		Módulo que modifica reporte de Producción para mostrar información de todas las pestañas que contiene.
	""",
	'auto_install': False,
	'demo': [],
	'data':	['order_report.xml'],
	'installable': True
}