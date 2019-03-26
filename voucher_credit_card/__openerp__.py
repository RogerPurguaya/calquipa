# -*- encoding: utf-8 -*-
{
	'name': 'Voucher Credit Card IT',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account', 'account_tables_it', 'account_voucher','account_means_payment_it','deliveries_to_pay_it'],
	'version': '1.0',
	'description':"""
	Pago con Tarjetas de Credito
	""",
	'auto_install': False,
	'demo': [],
	'data':	['account_journal_view.xml','voucher_credit_card_view.xml','account_voucher_view.xml'],
	'installable': True
}
