# -*- encoding: utf-8 -*-
{
	'name': 'Obras Curso - Expediente Importacion IT',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account','product','account_analytic_bookmajor_it','account_analytic_bookmajor_mexico_it','account_contable_book_it','purchase','purchase_requisition','base','purchase_analytic_plans','product_analytic_account_it','account_analytic_plans','purchase_analytic_plans','calquipa_personalizacion_it'],
	'version': '1.0',
	'description':"""
	Obras Curso y Expedientes Importacion 
	presentes en licitaciones, solicitudes de presupuesto, pedido de compra, facturas de proveedor
	y en las lineas del asiento
	""",
	'auto_install': False,
	'demo': [],
	'data':	['obras_curso_view.xml'],
	'installable': True
}
