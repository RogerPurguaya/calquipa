# -*- encoding: utf-8 -*-
{
	'name': 'Calquipa Personalizacion IT',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account','product','purchase','purchase_requisition','base','purchase_analytic_plans','product_analytic_account_it','purchase_analytic_plans','sale_stock','stock_account','account_means_payment_it'],
	'version': '1.0',
	'description':"""
	Crear las cuentas mexico, ( Codigo mexico y nomenclatura mexico)
	Crear Centros de costo en licitaciones, presupuesto y pedido de compra. Y su configuracion correspondiente en los usuarios.
	Agrupaciones de los centros de costo.
	Grupo para modificar, crear, eliminar los centros de costo.
	Crear Aprobaciones de los formularios de Compras.

	""",
	'auto_install': False,
	'demo': [],
	'data':	['security/purchase_national_security.xml','calquipa_personalizacion_view.xml','security/centro_costo_security_security.xml'],
	'installable': True
}
