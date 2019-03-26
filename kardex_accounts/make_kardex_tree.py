# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp
from openerp import models, fields
class make_kardex_tree(models.Model):
	_inherit = "make.kardex.tree"
	account_invoice=fields.Char('Cuenta factura',size=150)
	product_account=fields.Char('Cuenta producto',size=150)
