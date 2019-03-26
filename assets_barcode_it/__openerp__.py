# -*- encoding: utf-8 -*-
{
	'name': 'Print Asset EAN13 barcode IT',
	'category': 'stock',
	'author': 'ITGrupo',
	'depends': ['product_barcode_generator', 'account_asset_alter_it', 'point_of_sale', 'product_barcode_generator'],
	'version': '1.0',
	'description':"""
		Módulo que genera formato para impresión de etiquetas de producto.
	""",
	'auto_install': False,
	'demo': [],
	'data':	['account_asset.xml'],
	'installable': True
}