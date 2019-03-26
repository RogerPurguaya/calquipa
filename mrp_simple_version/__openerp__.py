# -*- coding: utf-8 -*-
{
    'name': 'MRP Simple version',
    'version': '1.0',
    'category': 'Manufacturing',
    'description': """
		This module reduces the option from mrp_production in order to make it simple to manage
    """,
    'author': 'ITGrupo',
    'website': '',
    'depends': ['base', 'sale_mrp', 'product'],
    'data': [
       'mrp_view.xml',
       'product_view.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}