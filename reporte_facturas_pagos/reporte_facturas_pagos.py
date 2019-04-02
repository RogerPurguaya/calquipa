# -*- coding: utf-8 -*-

from openerp import models, fields, api


class reporte_facturas_pagos(models.Model):
	_name = 'reporte.facturas.pagos'
	_auto = False
	
	periodo= fields.Char('Periodo', size=50)
	libro= fields.Char('Libro', size=50)
	voucher= fields.Char('Voucher', size=50)
	cuenta= fields.Char('Cuenta', size=200)
	debe = fields.Float('Debe', digits=(12,2))
	haber = fields.Float('Haber', digits=(12,2))
	divisa= fields.Char('Divisa', size=50)
	tipocambio  = fields.Float('Tipo Cambio', digits=(12,3))
	importedivisa  = fields.Float('Importe Divisa', digits=(12,2))
	conciliacion= fields.Char('Conciliación', size=50)
	fechaemision = fields.Date('Fecha Emisión')
	fechavencimiento = fields.Date('Fecha Vencimiento')
	tipodocumento= fields.Char('Tipo de Documento', size=50)
	numero= fields.Char('Número', size=50)
	ruc= fields.Char('RUC', size=50)
	partner= fields.Char('Partner', size=50)
	glosa = fields.Char('Glosa', size=50)
	ordenamiento = fields.Integer('Ordenamiento')
	cuentaname = fields.Char('Cuenta Name', size=200)
	state = fields.Char('Estado',size=50)