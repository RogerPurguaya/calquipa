# -*- encoding: utf-8 -*-
{
	'name': 'Reporte de Costo de Venta Calquipa',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account_parameter_it','kardex_campos_it',
	'config_products_for_costs_report','calquipa_reportemexicanos_parte1_it'],
	'version': '1.0',
	'description':"""
	Reporte de Costo de Venta para Calquipa
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'wizard/reporte_costo_venta_wizard_view.xml',#'reporte_facturas_pagos_view.xml'
	],
	'installable': True
}
