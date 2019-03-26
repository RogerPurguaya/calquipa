# -*- encoding: utf-8 -*-
import base64
from openerp import models, fields, api

class hr_table_adelanto(models.Model):
	_name = 'hr.table.adelanto'
	_rec_name = 'name'

	name            = fields.Char('Nombre')
	code            = fields.Char(u'Código')
	tipo_trabajador = fields.Many2one('tipo.trabajador','Tipo de Trabajador')
	account_id      = fields.Many2one('account.account','Cuenta')