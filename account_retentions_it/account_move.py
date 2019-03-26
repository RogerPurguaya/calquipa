# -*- coding: utf-8 -*-

from openerp import models, fields, api , exceptions , _

class account_move(models.Model):
	_inherit = 'account.move'
	
	com_ret_amount =fields.Float('Monto', digits=(12,2))