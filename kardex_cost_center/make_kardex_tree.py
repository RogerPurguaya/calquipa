# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp
from openerp import models, fields
class make_kardex_tree(models.Model):
	_inherit = "make.kardex.tree"
	cost_account=fields.Char('Cuenta costo',size=50)


	def make_values_line(self,cr,uid,ids,linea,context=None):
		vals = super(make_kardex_tree,self).make_values_line(cr,uid,ids,linea,context)
		vals['cost_account']=linea['cost_account']
		print linea['cost_account']

		return vals