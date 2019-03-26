# -*- encoding: utf-8 -*-
{
	'name': 'Visualizar Kardex IT',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['kardex','kardex_saldos'],
	'version': '1.0',
	'description':"""
		Crea grupo para visualizar el kardex
	""",
	'auto_install': False,
	'demo': [],
	'data':	['security/purchase_national_security.xml',
			'kardex_view.xml'],
	'installable': True
}
