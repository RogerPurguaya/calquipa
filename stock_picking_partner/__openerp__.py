# -*- encoding: utf-8 -*-
{
	'name': 'Stock Picking Partner',
	'category': 'warehouse',
	'author': 'ITGrupo',
	'depends': ['stock_picking_motive', 'partner_name_it', 'account_moorage_analytic_it', 'calquipa_personalizacion_it','stock_account'],
	'version': '1.0',
	'description':"""
		Coloca los campos "Entregado a" y "Solicitado por" al albaran.
		Coloca el centro de costo en la cuenta analitica
	""",
	'auto_install': False,
	'demo': [],
	'data':['stock_picking_view.xml', 'account_analytic_account_view.xml'],
	'installable': True
}
