# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv


class res_currency_mex(models.Model):
	_name = 'res.currency.mex'

	fecha  = fields.Date('Fecha',required=True)
	tipo_cambio = fields.Float('Tipo de Cambio',digits=(12,3),required=True)

	