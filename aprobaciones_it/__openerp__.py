# -*- encoding: utf-8 -*-
{
	'name': 'Aprobaciones IT',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account','purchase_requisition','account_voucher','deliveries_to_pay_it','small_cash_another_it','desembolso_personal_it','anticipo_proveedor_it','account_budget'],
	'version': '1.0',
	'description':"""
		Permisos para Aprobar en los modulos contables y de gestion
	""",
	'auto_install': False,
	'demo': [],
	'data':	['security/purchase_national_security.xml',
			'account_journal_view.xml'],
	'installable': True
}
