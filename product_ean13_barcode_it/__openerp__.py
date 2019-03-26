# -*- encoding: utf-8 -*-
{
	'name': 'Print EAN13 barcode IT',
	'category': 'stock',
	'author': 'ITGrupo',
	'depends': ['product', 'point_of_sale', 'product_barcode_generator'],
	'version': '1.0',
	'description':"""
		Módulo que genera formato para impresión de etiquetas de producto.
	""",
	'auto_install': False,
	'demo': [],
	'data':	['product_report.xml',
			'point_of_sale.xml'],
	'installable': True
}