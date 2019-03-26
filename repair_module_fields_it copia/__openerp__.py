# -*- encoding: utf-8 -*-
{
	'name': 'Repair Module Fields IT',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account','account_analytic_plans','account_type_doc_it','daot_sunat_it'],
	'version': '1.0',
	'description':"""
Ocultando campos que ya carecen de necesidad:
	Es operacion externa
	es asiento unico
	distribucion analytica
	""",
	'auto_install': False,
	'demo': [],
	'data':	['account_journal_view.xml'],
	'installable': True
}
