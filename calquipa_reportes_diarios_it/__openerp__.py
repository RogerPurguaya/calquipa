# -*- coding: utf-8 -*-
{
    'name': "Reportes Diarios Mexicanos",

    'description': """
        - Genera reportes diarios para:\n
            - Extracción
            - Trituración
            - Gran. Piedra
            - Anivi Coke
            - Control Antracita
            - Maervz
            - Pulv. CaO
            - Salidas CaO Diaria
            - Salidas CaO Acum
            - Invent
            - Calcu Combusti
    """,

    'author': "ITGrupo",
    'category': 'account',
    'version': '0.1',
    'auto_install': False,
    'installable': True,
    'depends': ['account','sale','product'],
    'data': ['security/reportes_diarios_security.xml',
             'security/ir.model.access.csv',
             'reportes_diarios_menu.xml',    
             'wizard/reporte_wizard_view.xml',
             'principal_view.xml',
             'extraccion_reporte_view.xml',
             'trituracion_reporte_view.xml',
             'anivi_coke_reporte_view.xml',
             'control_antracita_reporte_view.xml',
             'maerz_reporte_view.xml',
             'pulv_cao_reporte_view.xml',
             'salida_cao_reporte_view.xml',],
}