# -*- coding: utf-8 -*-

from openerp import models, fields, api ,  _


class account_perception(models.Model):
	_inherit='account.perception'




	@api.one
	def get_tc_auto(self):
		rc = self.env['res.currency'].search([('name','=','USD')])[0]
		lineas = self.env['res.currency.rate'].search([('currency_id','=',rc.id),('name','=',self.fecha)])
		tmp = 0
		for i in lineas:
			tmp = i.type_sale

		self.tc_auto = tmp

	tc_auto = fields.Float('T.C.',digits=(12,3),compute="get_tc_auto")

