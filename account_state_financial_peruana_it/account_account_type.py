# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_account_type(models.Model):
	_inherit = 'account.account.type'
	
	tipo_cambio_usar = fields.Selection([('cc','Compra Cierre'),('vc','Venta Cierre'),('pcc','Promedio Cierre Compra'),('pcv','Promedio Cierre Venta'),('ca','Cedula Activos'),('cp','Cedula Patrimonio')],'Tipo de Cambio a Usar', size=100)
