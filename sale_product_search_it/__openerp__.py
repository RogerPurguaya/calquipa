# -*- encoding: utf-8 -*-
{
	'name': 'Ventas busqueda x codigo',
	'category': 'sale',
	'author': 'ITGrupo',
	'depends': ['sale'],
	'version': '1.0',
	'description':"""
		En formulario Presupuesto/Pedido de venta:
	    Añadir una columna "Código", que permita ingresar un texto y al presionar TAB busque por el código de producto (referencia interna) y lo seleccione en la linea del pedido a ingresar (como se haría al buscar por nombre de producto).
	""",
	'auto_install': False,
	'demo': [],
	'data':['sale_order_view.xml'],
	'installable': True
}
