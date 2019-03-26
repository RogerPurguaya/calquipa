# -*- encoding: utf-8 -*-
{
	'name': 'MRP Consumed Produced',
	'category': 'mrp',
	'author': 'ITGrupo',
	'depends': ['mrp_move_picking'],
	'version': '1.0',
	'description':"""
		Consume all the product to consume and all the products to produce no care about the product qty on wizard to produce
	""",
	'auto_install': False,
	'demo': [],
	'data':['wizard/mrp_product_produce_view.xml'],
	'installable': True
}