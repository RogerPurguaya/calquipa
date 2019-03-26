# -*- encoding: utf-8 -*-

from openerp import models, fields, api



class sale_order_line(models.Model):

	_inherit='sale.order.line'

	product_code = fields.Char('Codigo',size=20)


	@api.onchange('product_code')
	def search_code(self):
		res={}
		#raise osv.except_osv('a',product_code.rjust(6,'0'))
		if self.product_code:
			lst=self.env['product.product'].search( [('default_code','=',self.product_code.rjust(6,'0'))])
			if len(lst) >0:
				self.product_id = lst[0].id
			
