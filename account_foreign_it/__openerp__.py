# -*- encoding: utf-8 -*-
{
	'name': 'Account Foreign IT',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['delivery','base','account_tables_it', 'account_type_doc_it','finantial_convertion_it'],
	'version': '1.0',
	'description':"""
	Agregar a cuentas las de tipo extrangero
	""",
	'auto_install': False,
	'demo': [],
	'data':['account_invoice_view.xml'],
	'installable': True
}