# -*- encoding: utf-8 -*-
{
	'name': 'Account Retentions IT',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account_parameter_it', 'account_move_sunat_it', 'daot_sunat_it', 'account_contable_book_it'],
	'version': '1.0',
	'description':"""
		Modulo de Retenciones para ODOO
	""",
	'auto_install': False,
	'demo': [],
	'data':	['voucher_payment_receipt_view.xml','main_parameter_view.xml','account_journal_view.xml', 'account_move_view.xml', 'account_retention_view.xml', 'wizard/account_retention_wizard_view.xml'],
	'installable': True
}
