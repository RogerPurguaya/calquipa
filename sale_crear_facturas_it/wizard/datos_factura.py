# -*- coding: utf-8 -*-

from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs

import datetime

class datos_factura_lines_wizard(models.TransientModel):
	_name= 'datos.factura.lines.wizard'

	producto = fields.Many2one('product.product','Producto', readonly=True)
	cantidad = fields.Float('Cantidad por Facturar')	
	cantidad_facturar = fields.Float('Cantidad a Facturar', required=True, readonly=False)

	purchase_order_line_id = fields.Many2one('purchase.order.line','purchase line')

class datos_factura_wizard(models.TransientModel):
	_name='datos.factura.wizard'

	producto_lines = fields.Many2many('datos.factura.lines.wizard','datos_factura_wizard_datos_lines_rel','datos_factura_wizard_id','datos_factura_lines_wizard_id','Detalles')

	@api.one
	def do_rebuild(self):
		po = self.env.context['purchase_order_id']
		po_obj = self.env['purchase.order'].search([('id','=',po)])[0]
		d = self.producto_lines

		vals = {
			"partner_id": po_obj.partner_id.id,
			"origin": po_obj.name,
			"date_invoice": datetime.datetime.today(),
			"account_id": po_obj.partner_id.property_account_payable.id,
			"obra_curso_id": po_obj.obra_curso_id.id,
			"expediente_importacion_id": po_obj.expediente_importacion_id.id,
			"type_doc": po_obj.type_doc,
			"centro_costo_id": po_obj.centro_costo_id.id,
		}
		invo = self.env['account.invoice'].create(vals)
		invo_lines = []
		for i in self.producto_lines:

			if i.cantidad_facturar > i.cantidad:
				 raise osv.except_osv('Alerta!', "La cantidad colocada es mayor a la cantidad que se debe facturar\n producto {0}.".format(i.producto.name))
			if i.cantidad_facturar < 0:
				raise osv.except_osv('Alerta!', "La cantidad colocada es incorrecta\n producto {0}.".format(i.producto.name))

			vals_line = {
				"product_id": i.producto.id,
				"name": i.purchase_order_line_id.name,
				"quantity": i.cantidad_facturar,
				"uos_id": i.purchase_order_line_id.product_uom.id,
				"price_unit": i.purchase_order_line_id.price_unit,
				"invoice_line_tax_id": i.purchase_order_line_id.taxes_id.ids,
				"purchase_order_line_id": i.purchase_order_line_id.id,
			}
			print i.purchase_order_line_id.taxes_id.ids
			li = self.env['account.invoice.line'].create(vals_line)
			li.invoice_line_tax_id = i.purchase_order_line_id.taxes_id.ids
			invo_lines.append(li.id)

		invo.invoice_line = invo_lines

		tmp = po_obj.invoice_ids.ids
		tmp.append(invo.id)
		po_obj.invoice_ids = tmp

		if invo.centro_costo_id:
			for i in invo.invoice_line:
				if i.product_id.id:
					if i.product_id.type!='product':
						bandera = False
						if invo.centro_costo_id.columna == '1':
							if i.product_id.extraccion_acc.id:
								i.account_id = i.product_id.extraccion_acc.id
								bandera = True

						elif invo.centro_costo_id.columna == '2':
							if i.product_id.trituracion_acc.id:
								i.account_id = i.product_id.trituracion_acc.id
								bandera = True

						elif invo.centro_costo_id.columna == '3':
							if i.product_id.calcinacion_acc.id:
								i.account_id = i.product_id.calcinacion_acc.id
								bandera = True

						elif invo.centro_costo_id.columna == '4':
							if i.product_id.micronizado_acc.id:
								i.account_id = i.product_id.micronizado_acc.id
								bandera = True

						elif invo.centro_costo_id.columna == '5':
							if i.product_id.administracion_acc.id:
								i.account_id = i.product_id.administracion_acc.id
								bandera = True
							
						elif invo.centro_costo_id.columna == '6':
							if i.product_id.ventas_acc.id:
								i.account_id = i.product_id.ventas_acc.id
								bandera = True
							
						elif invo.centro_costo_id.columna == '7':
							if i.product_id.capacitacion_acc.id:
								i.account_id = i.product_id.capacitacion_acc.id
								bandera = True
							
						elif invo.centro_costo_id.columna == '8':
							if i.product_id.promocion_acc.id:
								i.account_id = i.product_id.promocion_acc.id
								bandera = True
							
						elif invo.centro_costo_id.columna == '9':
							if i.product_id.gastos_acc.id:
								i.account_id = i.product_id.gastos_acc.id
								bandera = True
			