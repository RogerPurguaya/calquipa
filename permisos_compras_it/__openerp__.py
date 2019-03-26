# -*- encoding: utf-8 -*-
{
	'name': 'Permisos Compras IT',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account','product','purchase','purchase_requisition','base','purchase_analytic_plans','product_analytic_account_it','mail'],
	'version': '1.0',
	'description':"""
	Permisos para el GRUPO Compras donde pueden hacer todo de compras, caso contrario solo pueden crear,eliminar,modificar licitaciones.
	""",
	'auto_install': False,
	'demo': [],
	'data':	['security/purchase_national_security.xml'],
	'installable': True
}
