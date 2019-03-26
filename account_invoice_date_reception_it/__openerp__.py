# -*- encoding: utf-8 -*-
{
	'name': 'Account Invoice Recepcion Fecha IT',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account_tables_it', 'account_type_doc_it'],
	'version': '1.0',
	'description':"""
	Nuevo requisito de fecha para Recepcion en facturas.
	""",
	'auto_install': False,
	'demo': [],
	'data':['account_invoice_view.xml'],
	'installable': True
}