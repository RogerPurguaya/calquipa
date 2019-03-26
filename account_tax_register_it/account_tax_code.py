# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_tax_code(models.Model):
	_inherit='account.tax.code'

	record_shop = fields.Selection((('1','Base Imponible destinadas a operaciones de Gravadas y/o de exportación.'),
									('2','Base Imponible destinadas a operaciones gravadas y/o de exportación y a operaciones no gravadas. '),
									('3','Base Imponible destinadas a operaciones no gravadas.'),
									('4','Compras No Gravadas.'),
									('5','Impuesto Selectivo al Consumo.'),
									('6','Otros.'),
									('7','Impuesto para Base Imponible destinadas a operaciones de Gravadas y/o de exportación.'),
									('8','Impuesto para Base Imponible destinadas a operaciones gravadas y/o de exportación y a operaciones no gravadas.'),
									('9','Impuesto para Base Imponible destinadas a operaciones no gravadas.')
									),'Registro de Compra')
	record_sale = fields.Selection((('1','Valor de Exportacion.'),
									('2','Base Imponible Ventas.'),
									('3','Ventas Inafectas.'),
									('4','Ventas Exoneradas.'),
									('5','Impuesto Selectivo al Consumo.'),
									('6','Otros.'),
									('7','Impuesto para Base Imponible Ventas.')
									),'Registro de Venta')
	record_fees = fields.Selection((('1','Renta de Cuarta.'),
									('2','Retencion.')
									),'Libro de Honorarios')