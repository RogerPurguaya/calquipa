# -*- coding: utf-8 -*-
{
    'name': "Reporte",

    'description': """
        Reporte Mexicano para Dolares
    """,

    'author': "ITGRUPO-CALQUIPA",
    'website': "http://www.itgrupo.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['calquipa_report_costo_it'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'reporte_it.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'auto_install': False,
    'installable': True,
    'application': True
}
