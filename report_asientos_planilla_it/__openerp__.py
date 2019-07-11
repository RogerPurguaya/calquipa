# -*- encoding: utf-8 -*-
{
	'name': 'Reporte de Asientos Contables-Planilla',
	'category': 'account',
	'author': 'ITGrupo-Calquipa',
	'depends': ['account_parameter_it','account','hr_nomina_it','account_contable_book_it'],
	'version': '1.0',
	'description':"""
		Módulo para exportar el reporte de Asientos contables por planilla
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'wizard/account_move_report.xml',
		],
	'installable': True
}
