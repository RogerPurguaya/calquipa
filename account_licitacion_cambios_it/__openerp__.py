# -*- encoding: utf-8 -*-
{
	'name': 'Account Licitacion Cambios',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['purchase_requisition','mrp_simple_version','account','account_voucher','account_tables_it','account_type_doc_it','currency_sunat_change_it','partner_name_it','account_contable_book_it','repaccount_move_line_it'],
	'version': '1.0',
	'description':"""
	Personalizacion de Varios
	""",
	'auto_install': False,
	'demo': [],
	'data':	['account_asset_alter_view.xml'],
	'installable': True
}
