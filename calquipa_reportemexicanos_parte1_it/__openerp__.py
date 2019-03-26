# -*- encoding: utf-8 -*-
{
	'name': 'Reporte Mexicano Primera Parte IT',
	'category': 'account',
	'author': 'ITGrupo',
	'depends': ['account_parameter_it','calquipa_report_costo_it','web'],
	'version': '1.0',
	'description':"""
	Contendra los Reportes Mexicanos Siguientes:
		-Reporte Extraccion
		-Reporte Trituracion
		-Reporte Calcinacion
		-Reporte Micronizado
		-Reporte Pet
		-Administracion1
		-Ventas
		-
	""",
	'auto_install': False,
	'demo': [],
	'js':['static/src/js/mywidget.js'], 
	'data':	['reporte_mexicano_extraccion_view.xml','reporte_mexicano_trituracion_view.xml','reporte_mexicano_calcinacion_view.xml','reporte_mexicano_micronizado_view.xml','reporte_mexicano_administracion_view.xml','reporte_mexicano_ventas_view.xml','reporte_mexicano_capacitacion_view.xml','reporte_mexicano_promocion_view.xml','reporte_mexicano_intercompanias_view.xml','reporte_mexicano_gastos_view.xml','reporte_mexicano_costos_view.xml','reporte_mexicano_pet_view.xml','reporte_mexicano_petcal_view.xml','reporte_mexicano_nuevesiete_view.xml','reporte_balance_mexicano_view.xml','reporte_resultado_mexicano_view.xml','security/hr_security.xml','security/ir.model.access.csv','report_mexicano_estado_situacion_view.xml','report_detalle_activofijo_view.xml','report_patrimonio_view.xml','report_proyecto_view.xml','report_estado_resultado_view.xml','reporte_parametros_view.xml','reporte_consolidado_balance_view.xml','reporte_consolidado_resultado_view.xml','reporte_pre_flujo_efectivo_view.xml','reporte_flujo_efectivo_view.xml','reporte_consolidado_flujo_efectivo_view.xml'],
	'installable': True
}
