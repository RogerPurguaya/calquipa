# -*- encoding: utf-8 -*-
{
	'name': 'Generar Facturas IT',
	'category': 'sale',
	'author': 'ITGrupo',
	'depends': ['purchase','account','obras_curso_expediente_importacion_it','calquipa_personalizacion_it'],
	'version': '1.0',
	'description':"""
	Generación de facturas personalizada 
	""",
	'auto_install': False,
	'demo': [],
	'data':	['facturas_button_view.xml','wizard/datos_factura_view.xml'],
	'installable': True
}
