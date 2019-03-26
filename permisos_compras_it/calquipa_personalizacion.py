# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv


class product_pricelist(models.Model):
	_inherit= 'product.pricelist'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Tarifa") 

		return super(product_pricelist,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Tarifa") 

		return super(product_pricelist,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Tarifa") 

		return super(product_pricelist,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Tarifa") 

		return super(product_pricelist,self).unlink()		





class product_pricelist_version(models.Model):
	_inherit= 'product.pricelist.version'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Tarifa Versión") 

		return super(product_pricelist_version,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Tarifa Versión") 

		return super(product_pricelist_version,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Tarifa Versión") 

		return super(product_pricelist_version,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Tarifa Versión") 

		return super(product_pricelist_version,self).unlink()		






class product_price_type(models.Model):
	_inherit= 'product.price.type'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Tipo Precio") 

		return super(product_price_type,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Tipo Precio") 

		return super(product_price_type,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Tipo Precio") 

		return super(product_price_type,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Tipo Precio") 

		return super(product_price_type,self).unlink()		



class product_template(models.Model):
	_inherit= 'product.template'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Productos") 

		return super(product_template,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Productos") 

		return super(product_template,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Productos") 

		return super(product_template,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Productos") 

		return super(product_template,self).unlink()		




class product_category(models.Model):
	_inherit= 'product.category'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Categoria de Productos") 

		return super(product_category,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Categoria de Productos") 

		return super(product_category,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Categoria de Productos") 

		return super(product_category,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Categoria de Productos") 

		return super(product_category,self).unlink()		



class product_uom_categ(models.Model):
	_inherit= 'product.uom.categ'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Categoria de las Unidades") 

		return super(product_uom_categ,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Categoria de las Unidades") 

		return super(product_uom_categ,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Categoria de las Unidades") 

		return super(product_uom_categ,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Categoria de las Unidades") 

		return super(product_uom_categ,self).unlink()		

	


class product_uom(models.Model):
	_inherit= 'product.uom'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Unidades") 

		return super(product_uom,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Unidades") 

		return super(product_uom,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Unidades") 

		return super(product_uom,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Unidades") 

		return super(product_uom,self).unlink()		






class res_partner_category(models.Model):
	_inherit= 'res.partner.category'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Etiquetas de Empresa") 

		return super(res_partner_category,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Etiquetas de Empresa") 

		return super(res_partner_category,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Etiquetas de Empresa") 

		return super(res_partner_category,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Etiquetas de Empresa") 

		return super(res_partner_category,self).unlink()		






class stock_picking(models.Model):
	_inherit= 'stock.picking'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Envios Entrantes") 

		return super(stock_picking,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Envios Entrantes") 

		return super(stock_picking,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Envios Entrantes") 

		return super(stock_picking,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Envios Entrantes") 

		return super(stock_picking,self).unlink()		




class stock_move(models.Model):
	_inherit= 'stock.move'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Productos a Recibir") 

		return super(stock_move,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Productos a Recibir") 

		return super(stock_move,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Productos a Recibir") 

		return super(stock_move,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Productos a Recibir") 

		return super(stock_move,self).unlink()		



class account_invoice(models.Model):
	_inherit='account.invoice'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Facturas") 

		return super(account_invoice,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Facturas") 

		return super(account_invoice,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Facturas") 

		return super(account_invoice,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Facturas") 

		return super(account_invoice,self).unlink()		



class mail_compose_message(models.Model):
	_inherit='mail.compose.message'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Correos") 

		return super(mail_compose_message,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Correos") 

		return super(mail_compose_message,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Correos") 

		return super(mail_compose_message,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Correos") 

		return super(mail_compose_message,self).unlink()		


		
class purchase_order(models.Model):
	_inherit= 'purchase.order'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Pedidos de Compra o Solicitudes de Presupuesto") 

		return super(purchase_order,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Pedidos de Compra o Solicitudes de Presupuesto") 

		return super(purchase_order,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Pedidos de Compra o Solicitudes de Presupuesto") 

		return super(purchase_order,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Grupo Compras')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Grupo Compras' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Pedidos de Compra o Solicitudes de Presupuesto") 

		return super(purchase_order,self).unlink()		


