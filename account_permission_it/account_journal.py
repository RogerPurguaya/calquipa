# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp import models, fields, api  , exceptions , _

class res_partner_bank(models.Model):
	_inherit = 'res.partner.bank'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Banco") 

		return super(res_partner_bank,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Banco") 

		return super(res_partner_bank,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Banco") 

		return super(res_partner_bank,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Banco") 

		return super(res_partner_bank,self).unlink()		





class product_template(models.Model):
	_inherit = 'product.template'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Productos") 

		return super(product_template,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Productos") 

		return super(product_template,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Productos") 

		return super(product_template,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Productos") 

		return super(product_template,self).unlink()		


class account_account_template(models.Model):
	_inherit = 'account.account.template'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Plantilla Cuenta") 

		return super(account_account_template,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Plantilla Cuenta") 

		return super(account_account_template,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Plantilla Cuenta") 

		return super(account_account_template,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Plantilla Cuenta") 

		return super(account_account_template,self).unlink()		


class account_chart_template(models.Model):
	_inherit = 'account.chart.template'



	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Plantilla Cuenta Chart") 

		return super(account_chart_template,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Plantilla Cuenta Chart") 

		return super(account_chart_template,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Plantilla Cuenta Chart") 

		return super(account_chart_template,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Plantilla Cuenta Chart") 

		return super(account_chart_template,self).unlink()		

class account_tax_template(models.Model):
	_inherit = 'account.tax.template'



	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Plantilla Impuesto") 

		return super(account_tax_template,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Plantilla Impuesto") 

		return super(account_tax_template,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Plantilla Impuesto") 

		return super(account_tax_template,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Plantilla Impuesto") 

		return super(account_tax_template,self).unlink()		

class account_tax_code_template(models.Model):
	_inherit = 'account.tax.code.template'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Plantilla Impuesto Code") 

		return super(account_tax_code_template,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Plantilla Impuesto Code") 

		return super(account_tax_code_template,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Plantilla Impuesto Code") 

		return super(account_tax_code_template,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Plantilla Impuesto Code") 

		return super(account_tax_code_template,self).unlink()		


class account_fiscal_position_template(models.Model):
	_inherit = 'account.fiscal.position.template'



	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Plantilla Posicion Fiscal") 

		return super(account_fiscal_position_template,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Plantilla Posicion Fiscal") 

		return super(account_fiscal_position_template,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Plantilla Posicion Fiscal") 

		return super(account_fiscal_position_template,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Plantilla Posicion Fiscal") 

		return super(account_fiscal_position_template,self).unlink()		

class account_account_type(models.Model):
	_inherit = 'account.account.type'



	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Tipo De Cuenta") 

		return super(account_account_type,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Tipo De Cuenta") 

		return super(account_account_type,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Tipo De Cuenta") 

		return super(account_account_type,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Tipo De Cuenta") 

		return super(account_account_type,self).unlink()		

class account_tax(models.Model):
	_inherit = 'account.tax'



	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Impuesto") 

		return super(account_tax,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Impuesto") 

		return super(account_tax,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Impuesto") 

		return super(account_tax,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Impuesto") 

		return super(account_tax,self).unlink()		

class account_tax_code(models.Model):
	_inherit = 'account.tax.code'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Codigo Impuesto") 

		return super(account_tax_code,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Codigo Impuesto") 

		return super(account_tax_code,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Codigo Impuesto") 

		return super(account_tax_code,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Codigo Impuesto") 

		return super(account_tax_code,self).unlink()		


class account_fiscal_position(models.Model):
	_inherit = 'account.fiscal.position'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Posicion Fiscal") 

		return super(account_fiscal_position,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Posicion Fiscal") 

		return super(account_fiscal_position,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Posicion Fiscal") 

		return super(account_fiscal_position,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Posicion Fiscal") 

		return super(account_fiscal_position,self).unlink()		


class account_financial_report(models.Model):
	_inherit = 'account.financial.report'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Reporte Finanzas") 

		return super(account_financial_report,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Reporte Finanzas") 

		return super(account_financial_report,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Reporte Finanzas") 

		return super(account_financial_report,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Reporte Finanzas") 

		return super(account_financial_report,self).unlink()		


class account_analytic_journal(models.Model):
	_inherit = 'account.analytic.journal'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Diario Analítico") 

		return super(account_analytic_journal,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Diario Analítico") 

		return super(account_analytic_journal,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Diario Analítico") 

		return super(account_analytic_journal,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Diario Analítico") 

		return super(account_analytic_journal,self).unlink()		



class account_analytic_default(models.Model):
	_inherit = 'account.analytic.default'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear C. Analítica Defecto") 

		return super(account_analytic_default,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar C. Analítica Defecto") 

		return super(account_analytic_default,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar C. Analítica Defecto") 

		return super(account_analytic_default,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar C. Analítica Defecto") 

		return super(account_analytic_default,self).unlink()		


class account_analytic_plan(models.Model):
	_inherit = 'account.analytic.plan'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Plan Analítico") 

		return super(account_analytic_plan,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Plan Analítico") 

		return super(account_analytic_plan,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Plan Analítico") 

		return super(account_analytic_plan,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Plan Analítico") 

		return super(account_analytic_plan,self).unlink()		


class account_analytic_plan_instance(models.Model):
	_inherit = 'account.analytic.plan.instance'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Distribución Analitica") 

		return super(account_analytic_plan_instance,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Distribución Analitica") 

		return super(account_analytic_plan_instance,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Distribución Analitica") 

		return super(account_analytic_plan_instance,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Distribución Analitica") 

		return super(account_analytic_plan_instance,self).unlink()		


class account_budget_post(models.Model):
	_inherit = 'account.budget.post'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Budgets Post") 

		return super(account_budget_post,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Budgets Post") 

		return super(account_budget_post,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Budgets Post") 

		return super(account_budget_post,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Budgets Post") 

		return super(account_budget_post,self).unlink()		

class account_payment_term(models.Model):
	_inherit = 'account.payment.term'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Terminos Pago") 

		return super(account_payment_term,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Terminos Pago") 

		return super(account_payment_term,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Terminos Pago") 

		return super(account_payment_term,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Terminos Pago") 

		return super(account_payment_term,self).unlink()		


class main_parameter(models.Model):
	_inherit = 'main.parameter'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Parametros Principales") 

		return super(main_parameter,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Parametros Principales") 

		return super(main_parameter,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Parametros Principales") 

		return super(main_parameter,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Parametros Principales") 

		return super(main_parameter,self).unlink()		


class exchange_diff_config(models.Model):
	_inherit = 'exchange.diff.config'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Metodo Cobro") 

		return super(exchange_diff_config,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Metodo Cobro") 

		return super(exchange_diff_config,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Metodo Cobro") 

		return super(exchange_diff_config,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Metodo Cobro") 

		return super(exchange_diff_config,self).unlink()		


class voucher_credit_card(models.Model):
	_inherit = 'voucher.credit.card'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Tarjeta Credito") 

		return super(voucher_credit_card,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Tarjeta Credito") 

		return super(voucher_credit_card,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Tarjeta Credito") 

		return super(voucher_credit_card,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Tarjeta Credito") 

		return super(voucher_credit_card,self).unlink()		


class res_currency(models.Model):
	_inherit = 'res.currency'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Monedas") 

		return super(res_currency,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Monedas") 

		return super(res_currency,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Monedas") 

		return super(res_currency,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Monedas") 

		return super(res_currency,self).unlink()		


class res_currency_rate(models.Model):
	_inherit = 'res.currency.rate'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Tipo Cambio") 

		return super(res_currency_rate,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Tipo Cambio") 

		return super(res_currency_rate,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Tipo Cambio") 

		return super(res_currency_rate,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Tipo Cambio") 

		return super(res_currency_rate,self).unlink()		


class account_statement_operation_template(models.Model):
	_inherit = 'account.statement.operation.template'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Plantilla Operaciones") 

		return super(account_statement_operation_template,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Plantilla Operaciones") 

		return super(account_statement_operation_template,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Plantilla Operaciones") 

		return super(account_statement_operation_template,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Plantilla Operaciones") 

		return super(account_statement_operation_template,self).unlink()		




class account_config_efective(models.Model):
	_inherit = 'account.config.efective'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Flujo Efectivo") 

		return super(account_config_efective,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Flujo Efectivo") 

		return super(account_config_efective,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Flujo Efectivo") 

		return super(account_config_efective,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Flujo Efectivo") 

		return super(account_config_efective,self).unlink()		




class account_fiscalyear(models.Model):
	_inherit = 'account.fiscalyear'


	#@api.multi
	#def create_period(self, interval=1):
	#	all_groups=self.env['res.groups']
	#	all_users =self.env['res.users']
		
	#	g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
	#	if not g1_ids: 
	#		raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

	#	if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
	#		raise osv.except_osv('Alerta!', "No tiene los permisos para crear Año Fiscal") 

	#	return super(account_fiscalyear,self).create_period(interval)

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Año Fiscal") 

		return super(account_fiscalyear,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Año Fiscal") 

		return super(account_fiscalyear,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Año Fiscal") 

		return super(account_fiscalyear,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Año Fiscal") 

		return super(account_fiscalyear,self).unlink()		


class account_journal(models.Model):
	_inherit = 'account.journal'


	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Diarios") 

		return super(account_journal,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Diarios") 

		return super(account_journal,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Diarios") 

		return super(account_journal,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Diarios") 

		return super(account_journal,self).unlink()		




class account_account(models.Model):
	_inherit = 'account.account'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Cuentas Contables") 

		return super(account_account,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Cuentas Contables") 

		return super(account_account,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Cuentas Contables") 

		return super(account_account,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Cuentas Contables") 

		return super(account_account,self).unlink()		




class account_analytic_account(models.Model):
	_inherit = 'account.analytic.account'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Cuentas Analíticas") 

		return super(account_analytic_account,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Cuentas Analíticas") 

		return super(account_analytic_account,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Cuentas Analíticas") 

		return super(account_analytic_account,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Cuentas Analíticas") 

		return super(account_analytic_account,self).unlink()		



class account_period(models.Model):
	_inherit = 'account.period'

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para crear Periodos") 

		return super(account_period,self).create(vals)

	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para copiar Periodos") 

		return super(account_period,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para editar Periodos") 

		return super(account_period,self).write(vals)

	@api.one
	def unlink(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para eliminar Periodos") 

		return super(account_period,self).unlink()		

	@api.one
	def action_draft(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para re-abrir Periodos") 

		return super(account_period,self).action_draft()		

class account_period_close(models.TransientModel):
	_inherit= 'account.period.close'


	@api.one
	def data_save(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Editar Cuenta,Analítica y Diario')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos para Cerrar Periodos") 

		return super(account_period_close,self).data_save()		
