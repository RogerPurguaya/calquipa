# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv
import openerp.addons.decimal_precision as dp



class centro_costo(models.Model):
	_name = 'centro.costo'

	columna = fields.Char('Columna', help="Indica su tipo de Centro de Costo al que pertenece: '1': Extracción, '2': Trituración, '3':Calcinacion, '4':Micronizado, '5': Administración, '6':Ventas, '7':Capacitación, '8':Promoción, '9':Gastos Corporativos",size=2, required=True)
	descripcion = fields.Char('Descripción', size=100, required=True)

	user_ids_new = fields.Many2many('res.users','centro_costo_users_new_rel','centro_costo_id','user_id', string='Restringuir a los Usuarios',required=True)
	_rec_name = 'descripcion'
	_order = 'columna'

"""
class res_users(models.Model):
	_inherit = 'res.users'
"""

class it_account_mexicana(models.Model):
	_name = 'it.account.mexicana'

	code = fields.Char(required=True, string="Código",size=50)
	nomenclatura = fields.Char(required=True, string="Nomenclatura",size=200)
	_order = 'code'
	_rec_name='code'



class account_account(models.Model):
	_inherit='account.account'

	code_mexicana = fields.Many2one('it.account.mexicana',required=False, string="Código Mexico",size=30)
	nomenclatura_mexicana = fields.Char(required=False, related="code_mexicana.nomenclatura", string="Nomenclatura Mexico",size=100)



class product_template(models.Model):
	_inherit= 'product.template'

	is_controlate= fields.Boolean('Producto Controlado')

	extraccion_acc = fields.Many2one('account.account','Cuenta para Extracción')
	trituracion_acc = fields.Many2one('account.account','Cuenta para Trituración')
	calcinacion_acc = fields.Many2one('account.account','Cuenta para Calcinación')
	micronizado_acc = fields.Many2one('account.account','Cuenta para Micronizado')


	administracion_acc = fields.Many2one('account.account','Cuenta para Administración')
	ventas_acc = fields.Many2one('account.account','Cuenta para Ventas')
	capacitacion_acc = fields.Many2one('account.account','Cuenta para Capacitación')
	promocion_acc = fields.Many2one('account.account','Cuenta para Promoción')
	gastos_acc = fields.Many2one('account.account','Cuenta para Gastos Corporativos')


class sector_economic(models.Model):
	_name='sector.economic'

	name= fields.Char('Sector Económico',size=100)


class res_partner(models.Model):
	_inherit= 'res.partner'

	is_controlate= fields.Boolean('Proveedor de Producto Controlado')
	sector_economic_id = fields.Many2one('sector.economic','Sector Económico')


class account_invoice(models.Model):
	_inherit='account.invoice'
	
	residual = fields.Float(string='Balance', digits=dp.get_precision('Account'),compute='_compute_residual', store=False, help="Remaining amount due.")

	is_heredado= fields.Boolean('Es heredado', copy=False)


	type_doc = fields.Selection( [('preventivo','Preventivo'), ('correctivo','Correctivo')], string='Tipo' )



	user_id_centro_costo= fields.Many2one('res.users','User Invisible')

	_defaults={
		'user_id_centro_costo': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id,
	}

	centro_costo_id = fields.Many2one('centro.costo','Centro de Costo')
	

	@api.onchange('centro_costo_id')
	def onchange_centro_costo(self):
		if self.centro_costo_id:
			if self.centro_costo_id.columna == '1':
				for i in self.invoice_line:
					if i.product_id.id:
						if i.product_id.type != 'product':
							bandera = False
							if i.product_id.extraccion_acc.id:
								i.account_id = i.product_id.extraccion_acc.id
								bandera = True
							if not bandera:
								if i.product_id.property_account_expense.id:
									i.account_id = i.product_id.property_account_expense.id
								elif i.product_id.categ_id.id:
									if i.product_id.categ_id.property_account_expense_categ.id:
										i.account_id = i.product_id.categ_id.property_account_expense_categ.id
			elif self.centro_costo_id.columna == '2':
				for i in self.invoice_line:
					if i.product_id.id:
						if i.product_id.type != 'product':
							bandera = False
							if i.product_id.trituracion_acc.id:
								i.account_id = i.product_id.trituracion_acc.id
								bandera = True
							if not bandera:
								if i.product_id.property_account_expense.id:
									i.account_id = i.product_id.property_account_expense.id
								elif i.product_id.categ_id.id:
									if i.product_id.categ_id.property_account_expense_categ.id:
										i.account_id = i.product_id.categ_id.property_account_expense_categ.id
			elif self.centro_costo_id.columna == '3':
				for i in self.invoice_line:
					if i.product_id.id:
						if i.product_id.type != 'product':
							bandera = False
							if i.product_id.calcinacion_acc.id:
								i.account_id = i.product_id.calcinacion_acc.id
								bandera = True
							if not bandera:
								if i.product_id.property_account_expense.id:
									i.account_id = i.product_id.property_account_expense.id
								elif i.product_id.categ_id.id:
									if i.product_id.categ_id.property_account_expense_categ.id:
										i.account_id = i.product_id.categ_id.property_account_expense_categ.id
			elif self.centro_costo_id.columna == '4':
				for i in self.invoice_line:
					if i.product_id.id:
						if i.product_id.type != 'product':
							bandera = False
							if i.product_id.micronizado_acc.id:
								i.account_id = i.product_id.micronizado_acc.id
								bandera = True
							if not bandera:
								if i.product_id.property_account_expense.id:
									i.account_id = i.product_id.property_account_expense.id
								elif i.product_id.categ_id.id:
									if i.product_id.categ_id.property_account_expense_categ.id:
										i.account_id = i.product_id.categ_id.property_account_expense_categ.id
			elif self.centro_costo_id.columna == '5':
				for i in self.invoice_line:
					if i.product_id.id:
						if i.product_id.type != 'product':
							bandera = False
							if i.product_id.administracion_acc.id:
								i.account_id = i.product_id.administracion_acc.id
								bandera = True
							if not bandera:
								if i.product_id.property_account_expense.id:
									i.account_id = i.product_id.property_account_expense.id
								elif i.product_id.categ_id.id:
									if i.product_id.categ_id.property_account_expense_categ.id:
										i.account_id = i.product_id.categ_id.property_account_expense_categ.id
			elif self.centro_costo_id.columna == '6':
				for i in self.invoice_line:
					if i.product_id.id:
						if i.product_id.type != 'product':
							bandera = False
							if i.product_id.ventas_acc.id:
								i.account_id = i.product_id.ventas_acc.id
								bandera = True
							if not bandera:
								if i.product_id.property_account_expense.id:
									i.account_id = i.product_id.property_account_expense.id
								elif i.product_id.categ_id.id:
									if i.product_id.categ_id.property_account_expense_categ.id:
										i.account_id = i.product_id.categ_id.property_account_expense_categ.id
			elif self.centro_costo_id.columna == '7':
				for i in self.invoice_line:
					if i.product_id.id:
						if i.product_id.type != 'product':
							bandera = False
							if i.product_id.capacitacion_acc.id:
								i.account_id = i.product_id.capacitacion_acc.id
								bandera = True
							if not bandera:
								if i.product_id.property_account_expense.id:
									i.account_id = i.product_id.property_account_expense.id
								elif i.product_id.categ_id.id:
									if i.product_id.categ_id.property_account_expense_categ.id:
										i.account_id = i.product_id.categ_id.property_account_expense_categ.id
			elif self.centro_costo_id.columna == '8':
				for i in self.invoice_line:
					if i.product_id.id:
						if i.product_id.type != 'product':
							bandera = False
							if i.product_id.promocion_acc.id:
								i.account_id = i.product_id.promocion_acc.id
								bandera = True
							if not bandera:
								if i.product_id.property_account_expense.id:
									i.account_id = i.product_id.property_account_expense.id
								elif i.product_id.categ_id.id:
									if i.product_id.categ_id.property_account_expense_categ.id:
										i.account_id = i.product_id.categ_id.property_account_expense_categ.id
			elif self.centro_costo_id.columna == '9':
				for i in self.invoice_line:
					if i.product_id.id:
						if i.product_id.type != 'product':
							bandera = False
							if i.product_id.gastos_acc.id:
								i.account_id = i.product_id.gastos_acc.id
								bandera = True
							if not bandera:
								if i.product_id.property_account_expense.id:
									i.account_id = i.product_id.property_account_expense.id
								elif i.product_id.categ_id.id:
									if i.product_id.categ_id.property_account_expense_categ.id:
										i.account_id = i.product_id.categ_id.property_account_expense_categ.id



		else:
			for i in self.invoice_line:
				if i.product_id.id:
					if i.product_id.type != 'product':
						if i.product_id.property_account_expense.id:
							i.account_id = i.product_id.property_account_expense.id	
						elif i.product_id.categ_id.id:
							if i.product_id.categ_id.property_account_expense_categ.id:
								i.account_id = i.product_id.categ_id.property_account_expense_categ.id				





class account_invoice_line(models.Model):
	_inherit='account.invoice.line'

	@api.multi
	def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False,	company_id=None):
		t = super(account_invoice_line,self).product_id_change(product, uom_id, qty, name, type, partner_id, fposition_id, price_unit, currency_id,	company_id)

		if product:
			producto = self.env['product.product'].search([('id','=',product)])

			if producto.type!='product':
				bandera = False
				if 'centro_costo_context' in self.env.context:
					print "ESTE ES: ---_>",self.env.context['centro_costo_context']
					if self.env.context['centro_costo_context']:
						c_c_c = self.env['centro.costo'].search([('id','=',self.env.context['centro_costo_context'])])[0]
						if c_c_c.columna == '1':
							if producto.extraccion_acc.id:
								t['value']['account_id'] = producto.extraccion_acc.id
								bandera = True
						if c_c_c.columna == '2':
							if producto.trituracion_acc.id:
								t['value']['account_id'] = producto.trituracion_acc.id
								bandera = True
						if c_c_c.columna == '3':
							print "soy 3 :3"
							if producto.calcinacion_acc.id:
								t['value']['account_id'] = producto.calcinacion_acc.id
								bandera = True
						if c_c_c.columna == '4':
							if producto.micronizado_acc.id:
								t['value']['account_id'] = producto.micronizado_acc.id
								bandera = True
						if c_c_c.columna == '5':
							if producto.administracion_acc.id:
								t['value']['account_id'] = producto.administracion_acc.id
								bandera = True
						if c_c_c.columna == '6':
							if producto.ventas_acc.id:
								t['value']['account_id'] = producto.ventas_acc.id
								bandera = True
						if c_c_c.columna == '7':
							if producto.capacitacion_acc.id:
								t['value']['account_id'] = producto.capacitacion_acc.id
								bandera = True
						if c_c_c.columna == '8':
							if producto.promocion_acc.id:
								t['value']['account_id'] = producto.promocion_acc.id
								bandera = True
						if c_c_c.columna == '9':
							if producto.gastos_acc.id:
								t['value']['account_id'] = producto.gastos_acc.id
								bandera = True

				if not bandera:
					if producto.property_account_expense.id:
						t['value']['account_id'] = producto.property_account_expense.id
					elif producto.categ_id.id:
						if producto.categ_id.property_account_expense_categ.id:
							t['value']['account_id'] = producto.categ_id.property_account_expense_categ.id
		print t

		return t


class purchase_order(models.Model):
	_inherit= 'purchase.order'

	is_heredado= fields.Boolean('Es heredado', copy=False)

	centro_costo_id = fields.Many2one('centro.costo','Centro de Costo',required=False )
	
	type_doc = fields.Selection( [('preventivo','Preventivo'), ('correctivo','Correctivo')], string='Tipo' )


	user_id_centro_costo= fields.Many2one('res.users','User Invisible')
	user_id = fields.Many2one('res.users','User Invisible')

	
	_defaults={
		'user_id_centro_costo': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id,
		'user_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id,
	}

	@api.one
	def get_centro_costo_txt(self):
		if self.centro_costo_id:
			self.texto_centro_costo = self.centro_costo_id.descripcion
		else:
			self.texto_centro_costo = False

	texto_centro_costo = fields.Char('Centro Costo', compute='get_centro_costo_txt')



	def action_picking_create(self, cr, uid, ids, context=None):
		for order in self.browse(cr, uid, ids):
			t = super(purchase_order,self).action_picking_create(cr,uid,ids,context)
			picking_vals = {
				'picking_type_id': order.picking_type_id.id,
				'partner_id': order.partner_id.id,
				'date': order.date_order,
				'origin': order.name + ' / ' + (order.origin if order.origin else '')
			}
			self.pool.get('stock.picking').write(cr,uid,[t],picking_vals)
			return t

	@api.multi
	def action_invoice_create(self):
		t = super(purchase_order,self).action_invoice_create()
		invoice_obj = self.env['account.invoice'].search([('id','=',t)])[0]
		invoice_obj.is_heredado = True
		if self.type_doc:
			invoice_obj.type_doc = self.type_doc

		if self.centro_costo_id:
			invoice_obj.centro_costo_id = self.centro_costo_id.id

			for i in invoice_obj.invoice_line:
				if i.product_id.id:
					if i.product_id.type!='product':
						bandera = False
						if self.centro_costo_id.columna == '1':
							if i.product_id.extraccion_acc.id:
								i.account_id = i.product_id.extraccion_acc.id
								bandera = True

						elif self.centro_costo_id.columna == '2':
							if i.product_id.trituracion_acc.id:
								i.account_id = i.product_id.trituracion_acc.id
								bandera = True

						elif self.centro_costo_id.columna == '3':
							if i.product_id.calcinacion_acc.id:
								i.account_id = i.product_id.calcinacion_acc.id
								bandera = True

						elif self.centro_costo_id.columna == '4':
							if i.product_id.micronizado_acc.id:
								i.account_id = i.product_id.micronizado_acc.id
								bandera = True

						elif self.centro_costo_id.columna == '5':
							if i.product_id.administracion_acc.id:
								i.account_id = i.product_id.administracion_acc.id
								bandera = True
							
						elif self.centro_costo_id.columna == '6':
							if i.product_id.ventas_acc.id:
								i.account_id = i.product_id.ventas_acc.id
								bandera = True
							
						elif self.centro_costo_id.columna == '7':
							if i.product_id.capacitacion_acc.id:
								i.account_id = i.product_id.capacitacion_acc.id
								bandera = True
							
						elif self.centro_costo_id.columna == '8':
							if i.product_id.promocion_acc.id:
								i.account_id = i.product_id.promocion_acc.id
								bandera = True
							
						elif self.centro_costo_id.columna == '9':
							if i.product_id.gastos_acc.id:
								i.account_id = i.product_id.gastos_acc.id
								bandera = True
		return t




class purchase_requisition(models.Model):
	_inherit = 'purchase.requisition'


	type_doc = fields.Selection( [('preventivo','Preventivo'), ('correctivo','Correctivo')], string='Tipo' )
	user_id_centro_costo= fields.Many2one('res.users','User Invisible')
	

	name_sec = fields.Char(string="Nombre",size=200)

	urgente = fields.Boolean(string='Urgente')

	_defaults={
		'exclusive':'exclusive',
		'user_id_centro_costo': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id,
		'name': 'Borrador',
		'name_sec': 'Borrador',
	}

	centro_costo_id = fields.Many2one('centro.costo','Centro de Costo',required=False )

	@api.one
	def write(self,vals):
		if 'centro_costo_id' in vals:
			for i in self.purchase_ids:
				if i.state =='draft':
					i.centro_costo_id = vals['centro_costo_id']
		return super(purchase_requisition,self).write(vals)

	@api.model
	def create(self,vals):
		tex = self.env['ir.sequence'].get('purchase.order.requisition')
		vals['name']= tex
		vals['name_sec']= tex
		return super(purchase_requisition,self).create(vals)


	
	@api.one
	def get_centro_costo_txt(self):
		if self.centro_costo_id:
			self.texto_centro_costo = self.centro_costo_id.descripcion
		else:
			self.texto_centro_costo = False

	texto_centro_costo = fields.Char('Centro Costo', compute='get_centro_costo_txt')



	def _prepare_purchase_order(self, cr, uid, requisition, supplier, context=None):
		t = super(purchase_requisition,self)._prepare_purchase_order(cr, uid, requisition, supplier, context)
		if requisition.type_doc:
			t['type_doc']=requisition.type_doc

		t['centro_costo_id']= requisition.centro_costo_id.id
		
		t['is_heredado'] = True
		t['user_id']= requisition.user_id.id
		return t


