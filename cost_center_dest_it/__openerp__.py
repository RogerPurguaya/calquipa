# -*- encoding: utf-8 -*-
{
	'name': 'Auto Destination Location in Stock Picking IT',
	'category': 'stock',
	'author': 'ITGrupo',
	'depends': ['stock', 'analytic'],
	'version': '1.0',
	'description':"""
		Módulo que agrega campo al centro de costo para que sea copiado de manera predeterminada cuando se selecciona en el stock picking.
	""",
	'auto_install': False,
	'demo': [],
	'data':	['account_analytic_account.xml'],
	'installable': True
}