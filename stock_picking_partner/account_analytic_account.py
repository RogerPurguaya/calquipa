# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_analytic_account(models.Model):
	_inherit = 'account.analytic.account'

	cost_center_id = fields.Many2one('centro.costo',string ="Centro Costo",index = True)