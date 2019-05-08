# -*- encoding: utf-8 -*-
{
	'name': 'Rporte de facturas y pagos',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account','account_voucher','account_tables_it','account_type_doc_it','currency_sunat_change_it','partner_name_it','account_contable_book_it'],
	'version': '1.0',
	'description':"""
	Reporte de facturas y pagos basado en el libro mayor analitico

	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'wizard/reporte_facturas_pagos_wizard_view.xml',
	],
	'installable': True
}
