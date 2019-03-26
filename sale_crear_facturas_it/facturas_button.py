# -*- coding: utf-8 -*-

from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs

class account_invoice_line(models.Model):
	_inherit='account.invoice.line'

	purchase_order_line_id = fields.Many2one('purchase.order.line','Pedido de Compra')

class purchase_order_line(models.Model):
	_inherit='purchase.order.line'

	@api.one
	def get_cantidad_facturar(self):
		ob = self.env['account.invoice.line'].search([('purchase_order_line_id','=',self.id)])
		acum = 0
		for i in ob:
			acum += i.quantity
		self.cantidad_facturar = self.product_qty - acum
	cantidad_facturar = fields.Float('Cantidad por Facturar', compute="get_cantidad_facturar")

class purchase_order(models.Model):
	_inherit = 'purchase.order'

	@api.one
	def action_invoice_create(self):
		t = super(purchase_order,self).action_invoice_create()
		print t, "FAC"
		for i in self.invoice_ids:
			i.unlink()
		print t, "FAC"
		return t

	@api.multi
	def create_invoice(self):		
		if len(self.aprobations) == 0:
			raise osv.except_osv('Alerta!', "Se requiere Aprobación.")
		else:
			fg = True 
			for i in self.order_line:
				if i.cantidad_facturar != 0:
					fg = False
			if fg:
				raise osv.except_osv('Alerta!', "La cantidad por facturar de los productos están agotados, Ya no se puede generar mas facturas.")
			nuevo = self.env['datos.factura.wizard'].create({})
			arr = []
			for i in self.order_line:
				if i.cantidad_facturar != 0:
					valores = {
						"producto": i.product_id.id,
						"cantidad": i.cantidad_facturar,
						"cantidad_facturar": 0,
						"purchase_order_line_id": i.id,
					}
					detalle = self.env['datos.factura.lines.wizard'].create(valores)
					arr.append(detalle.id)
			nuevo.producto_lines= arr

			return {
				"context": {"purchase_order_id": self.id},
				"type": "ir.actions.act_window",
				"res_model": "datos.factura.wizard",
				"res_id": nuevo.id,
				"view_type": "form",
				"view_mode": "form",
				"target": "new",
			}

