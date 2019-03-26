# -*- coding: utf-8 -*-

from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs

class stock_picking(models.Model):
	_inherit = 'stock.picking'

	@api.one
	def compute_show_reopen(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Permite Utilizar Reopen en Albaranes')])

		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Boton Reopen' creado.")

		if self.state == 'done' or self.state == 'cancel':
			if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
				self.show_reopen = False
			else:
				self.show_reopen = True
	show_reopen = fields.Boolean('Reopen', compute="compute_show_reopen")

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Permite Eliminar Albaran')])

		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Eliminar Albaran' creado.")

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No Tienes los permisos para eliminar un albarán")
		else:
			return super(stock_picking,self).unlink()

class stock_move(models.Model):
	_inherit = 'stock.move'

	@api.one
	def compute_show_price_unit(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Muestra Precio Unitario de los Productos del Albaran')])

		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Mostrar Precio Unitario' creado.")

		if self.state == 'done' or self.state == 'cancel':
			if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
				self.show_price_unit = False
			else:
				self.show_price_unit = True
	show_price_unit = fields.Boolean('priceunit', compute="compute_show_price_unit")

	@api.one
	def compute_show_invoice(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Muestra Factura de los Productos del Albaran')])

		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Mostrar Factura' creado.")

		if self.state == 'done' or self.state == 'cancel':
			if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
				self.show_invoice = False
			else:
				self.show_invoice = True
	show_invoice = fields.Boolean('invoice', compute="compute_show_invoice")
