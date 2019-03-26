# -*- encoding: utf-8 -*-
{
	'name': 'Ajuste por Diferencia de Cambio M.E',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account', 'finantial_convertion_it'],
	'version': '1.0',
	'description':""" Crea ajustes por diferencia de cambio en M.E. """,
	'auto_install': False,
	'demo': [],
	'data':['square_foreign_currency_view.xml', 'wizard/make_me_diff_view.xml', 'wizard/square_selection_wizard_view.xml'],
	'installable': True
}
