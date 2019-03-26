# -*- encoding: utf-8 -*-
{
	'name'    : 'IMPORTACION DE SALDOS INICIALES IT',
	'category': 'stock',
	'author'  : 'ITGrupo',
	'depends' : ['stock_picking_motive','delivery'],
	'version' : '1.0',

	'description':"""
	- Importa saldos iniciales.
	""",

	'auto_install': False,
	'demo'        : [],
	'data'        :	['stock_view.xml'],
	'installable' : True
}
