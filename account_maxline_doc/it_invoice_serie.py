# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv

class it_invoice_serie(models.Model):
	_inherit = 'it.invoice.serie'
	
	maxlines = fields.Integer('Elementos en documento impreso')

"""
class account_journal(osv.osv):
	_name='account.journal'
	_inherit='account.journal'
	_columns={
		'maxlines':fields.integer('Elementos en documento impreso'),
	}
account_journal()
"""