# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv


class stock_move(models.Model):
	_inherit = 'stock.move'

	type_product = fields.Selection([('consu', 'Consumible'),('service','Servicio'),('product','Almacenable')], 'Tipo Producto', readonly=True, related="product_id.type")

class stock_picking_type(models.Model):
	_inherit = 'stock.picking.type'

	default_picking_type = fields.Boolean('Predeterminado',copy=False)

class purchase_requisition_line(models.Model):
	_inherit = 'purchase.requisition.line'


	type_product = fields.Selection([('consu', 'Consumible'),('service','Servicio'),('product','Almacenable')], 'Tipo Producto', readonly=True, related="product_id.type")

	descripcion = fields.Text('Descripción')

class purchase_requisition(models.Model):
	_inherit = 'purchase.requisition'

	
	def _prepare_purchase_order_line(self, cr, uid, requisition, requisition_line, purchase_id, supplier, context=None):
		t = super(purchase_requisition,self)._prepare_purchase_order_line(cr, uid, requisition, requisition_line, purchase_id, supplier, context)
		if requisition_line.descripcion and requisition_line.descripcion!= '':
			t['name'] = requisition_line.descripcion
		else:
			if requisition_line.product_id.id:
				t['name'] = requisition_line.product_id.name
		return t

	def _get_picking_in(self, cr, uid, context=None):
		obj_data = self.pool.get('ir.model.data')
		type_obj = self.pool.get('stock.picking.type')
		user_obj = self.pool.get('res.users')
		company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
		types = type_obj.search(cr, uid, [('code', '=', 'incoming'),('default_picking_type','=',True), ('warehouse_id.company_id', '=', company_id)], context=context)
		if not types:
			types = type_obj.search(cr, uid, [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)], context=context)
		if not types:
			types = type_obj.search(cr, uid, [('code', '=', 'incoming'), ('warehouse_id', '=', False)], context=context)
			if not types:
				raise osv.except_osv(_('Error!'), _("Make sure you have at least an incoming picking type defined"))
		return types[0]


class purchase_order_line(models.Model):
	_inherit = 'purchase.order.line'


	type_product = fields.Selection([('consu', 'Consumible'),('service','Servicio'),('product','Almacenable')], 'Tipo Producto', readonly=True, related="product_id.type")

	code_product_proveedor = fields.Char('Código Proveedor')

	def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,partner_id, date_order=False, fiscal_position_id=False, date_planned=False,	name=False, price_unit=False, state='draft', context=None):

		t = super(purchase_order_line,self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,partner_id, date_order, fiscal_position_id, date_planned,	name, price_unit, state, context)

		if product_id:

			code = ''
			product = self.pool.get('product.product').browse(cr,uid,product_id,context=context)

			if partner_id:
				for partner in product.seller_ids:
					if partner_id == partner.name.id:
						code = partner.product_code

			t['value']['code_product_proveedor'] = code
			t['value']['name'] = product.name

		return t

class purchase_order(models.Model):
	_inherit = 'purchase.order'

	"""
	def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
		t = super(purchase_order,self).onchange_partner_id(cr, uid, ids, partner_id, context)
		rpt = []
		purchase_obj = self.browse(cr,uid,ids,context=context)
		if len(purchase_obj)>0:
			purchase_obj= purchase_obj[0]
			for lineas in purchase_obj.order_line:
				code = ''
				if lineas.product_id.id:
					if partner_id:
						for partner in lineas.product_id.seller_ids:
							if partner_id == partner.name.id:
								code = partner.product_code

				rpt.append( (1,lineas.id,{'code_product_proveedor':code, 'name': lineas.name }) )

			t['value']['order_line'] = rpt

		return t
	"""

	@api.one
	def write(self,vals):
		t= super(purchase_order,self).write(vals)

		for lineas in self.order_line:
			code = ''
			if lineas.product_id.id:
				if self.partner_id.id:
					for partner in lineas.product_id.seller_ids:
						if self.partner_id.id == partner.name.id:
							code = partner.product_code
			lineas.code_product_proveedor = code
		return t


	@api.model
	def create(self,vals):
		t = super(purchase_order,self).create(vals)
		print "prder", t.order_line
		for lineas in t.order_line:
			code = ''
			if lineas.product_id.id:
				if t.partner_id.id:
					for partner in lineas.product_id.seller_ids:
						if t.partner_id.id == partner.name.id:
							code = partner.product_code

			lineas.code_product_proveedor = code

		return t
