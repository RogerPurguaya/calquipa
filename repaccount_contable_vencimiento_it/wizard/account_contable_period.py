# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_contable_vencimiento_fila(models.Model):

	_name='account.contable.vencimiento.fila'

	_order = "vencimiento, empresa, fecha_vencimiento, nro_comprobante"
	
	vencimiento = fields.Char(string='Vencimiento',size=200)
	periodo = fields.Char(string='Periodo',size=200)
	libro = fields.Char(string='Libro',size=200)
	voucher = fields.Char(string='Voucher',size=200)
	cuenta = fields.Char(string='Cuenta',size=200)
	fecha_emision = fields.Char(string='Fecha Emision',size=200)
	fecha_vencimiento = fields.Char(string='Fecha Vencimiento',size=200)
	nro_comprobante = fields.Char(string='Nro. Comprobante',size=200)
	empresa = fields.Char(string='Empresa',size=200)
	saldo = fields.Float('Saldo', digits=(12,2))
	user_guardado = fields.Float('user Guardado')

class account_contable_vencimiento_columna(models.Model):

	_name='account.contable.vencimiento.columna'

	_order = "empresa, nro_comprobante"
	
	fecha_emision = fields.Char(string='Fecha Emision',size=200)
	nro_comprobante = fields.Char(string='Nro. Comprobante',size=200)
	empresa = fields.Char(string='Empresa',size=200)
	cuenta = fields.Char(string='Cuenta',size=200)
	vencidos = fields.Float('Vencidas', digits=(12,2))
	menos16 = fields.Float('De 0 a 15', digits=(12,2))
	de16a30 = fields.Float('De 16 a 30', digits=(12,2))
	de31a45 = fields.Float('De 31 a 45', digits=(12,2))
	de46a60 = fields.Float('De 46 a 60', digits=(12,2))
	de61a90 = fields.Float('De 61 a 90', digits=(12,2))
	de91a180 = fields.Float('De 91 a 180', digits=(12,2))
	mas180 = fields.Float('Mas de 180', digits=(12,2))
	user_guardado = fields.Float('user Guardado')

class account_contable_vencimiento_columna_agrupada(models.Model):

	_name='account.contable.vencimiento.columna.agrupada'
	_order = "empresa"
	
	@api.one
	def total_general(self):
		self.totalgeneral = self.de16a30 + self.de31a45 + self.de46a60 + self.de61a90 + self.de91a180 + self.mas180

	empresa = fields.Char(string='Empresa',size=200)
	vencidos = fields.Float('Vencidas', digits=(12,2))
	menos16 = fields.Float('De 0 a 15', digits=(12,2))
	de16a30 = fields.Float('De 16 a 30', digits=(12,2))	
	de31a45 = fields.Float('De 31 a 45', digits=(12,2))	
	de46a60 = fields.Float('De 46 a 60', digits=(12,2))	
	de61a90 = fields.Float('De 61 a 90', digits=(12,2))	
	de91a180 = fields.Float('De 91 a 180', digits=(12,2))	
	mas180 = fields.Float('Mas de 180', digits=(12,2))
	totalgeneral = fields.Float('Total General',compute="total_general", digits=(12,2))
	user_guardado = fields.Float('user Guardado')
