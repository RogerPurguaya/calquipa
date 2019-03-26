# -*- encoding: utf-8 -*-
{
	'name': 'facturas que no se encuentran en el kardex',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['kardex'],
	'version': '1.0',
	'description':"""Lista facuras de almacenables que no tienen relacion en el kardex """,
	'auto_install': False,
	'demo': [],
	'data':[#'kardex_invoice_notin_view.xml',
		   	'wizard/get_kardex_invoice_notin_view.xml'
		   	],
	'installable': True
}
