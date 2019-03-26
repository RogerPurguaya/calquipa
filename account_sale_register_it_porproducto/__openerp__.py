# -*- encoding: utf-8 -*-
{
	'name': 'Account Sale Register IT x producto',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account_move_sunat_it', 'account_contable_book_it'],
	'version': '1.0',
	'description':"""
	Registro de Ventas
	""",
	'auto_install': False,
	'demo': [],
	'data':	['wizard/account_sale_register_report_wizard_view.xml'],
	'installable': True
}
