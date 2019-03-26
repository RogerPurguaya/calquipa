# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp import models, fields, api  , exceptions , _


class purchase_order(models.Model):
	_inherit = 'purchase.order'

	@api.one
	def action_cancel(self):
		t =  super(purchase_order,self).action_cancel()

		for i in self.aprobations:
			i.with_context({'supereliminate':'1'}).unlink()
		return t

	@api.multi
	def correo_informativo(self):
		for o in self:
			if len(o.aprobations) > 0:
				values = {}
				values['subject'] = "Solicitud de Presupuesto Aprobado - "+ o.name
				values['email_to'] = "mleon@calidra.com.mx"
				txt = """<h2>*** Solicitud de Presupuesto Aprobado - """+ o.name +""" ***</h2>
				<p>Proveedor: """+ o.partner_id.name + """</p>
				<p>Total: """+ ("%0.2f"%o.amount_total)+ """</p>
				<h2>Aprobaciones:</h2>
				<p>-------------------------------------------------</p>
				"""
				for yy in o.aprobations:
					txt += "<p>Usuario: "+ (yy.usuario.name if yy.usuario.name else '') +", Fecha: "+ (str(yy.fecha) if yy.fecha else '') +", Glosa: "+ (yy.glosa if yy.glosa else 'Sin Glosa') +"</p>"
				values['body_html'] = txt
				values['res_id'] = False
				mail_mail_obj = self.env['mail.mail']
				msg_id = mail_mail_obj.create(values)
				if msg_id:
					msg_id.send()
					print "Correo enviado", values


	@api.multi
	def wkf_confirm_order(self):
		for o in self:
			if len(o.aprobations)== 0:
				raise osv.except_osv('Alerta!', "La Orden de Compra no tiene Aprobaciones")

			usuario_total = []
			for mm in self.env['res.users'].search([]):


				all_groups=self.env['res.groups']
				all_users =self.env['res.users']
				
				g1_ids = all_groups.search([('name','=',u'Permite dar Aprobaciones')])

				if g1_ids in mm.groups_id:
					usuario_total.append(mm)

			for xx in usuario_total:
				flag = False
				for yy in o.aprobations:
					if xx.id == yy.usuario.id:
						flag = True

				if flag == False:
					values = {}
					values['subject'] = "Solicitud de Presupuesto Aprobado - "+ o.name
					values['email_to'] = xx.partner_id.email
					txt = """<h2>*** Solicitud de Presupuesto Aprobado - """+ o.name +""" ***</h2>
					<p>Proveedor: """+ o.partner_id.name + """</p>
					<p>Total: """+ ("%0.2f"%o.amount_total)+ """</p>
					<h2>Aprobaciones:</h2>
					<p>-------------------------------------------------</p>
					"""
					for yy in o.aprobations:
						txt += "<p>Usuario: "+yy.usuario.name+", Fecha: "+ str(yy.fecha) +", Glosa: "+ (yy.glosa if yy.glosa else 'Sin Glosa') +"</p>"
					values['body_html'] = txt
					values['res_id'] = False
					mail_mail_obj = self.env['mail.mail']
					msg_id = mail_mail_obj.create(values)
					if msg_id:
						msg_id.send()
						print "Correo enviado", values
			
		return super(purchase_order,self).wkf_confirm_order()

	@api.one
	def aprobations_calculate(self):
		texto = 'purchase_order,' + str(self.id)
		vrp = []
		for i in self.env['aprobacion.users'].search([('ids_conexion','=',texto)]):
			vrp.append(i.id)
		self.aprobations = vrp

	aprobations = fields.Many2many('aprobacion.users',string='Aprobaciones',compute='aprobations_calculate',readonly="1")


	@api.one
	def get_aprobacion_flag(self):
		if len(self.aprobations)>0:
			self.flag_aprobations = True
		else:
			self.flag_aprobations = False

	flag_aprobations = fields.Boolean('Aprobado', compute="get_aprobacion_flag", store=False)


	@api.multi
	def agregar_aprobation(self):
		compose_form = self.env.ref('aprobaciones_it.it_aprobacion_users_wizard_form', False)
		return {
			'name': 'Aprobación',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'aprobacion.users',
			'views': [(compose_form.id, 'form')],
			'view_id': compose_form.id,
			'target': 'new',
			'context': {'default_ids_conexion':'purchase_order,'+str(self.id), },
		}


class aprobacion_users(models.Model):
	_name = 'aprobacion.users'

	fecha = fields.Date('Fecha')
	usuario = fields.Many2one('res.users','Usuario')
	cargo = fields.Char('Cargo')
	nombre = fields.Char('Nombre')
	glosa = fields.Char('Glosa',size=200)
	ids_conexion = fields.Char('ids_conexion',size=200)


	@api.multi
	def do_rebuild(self):
		from  datetime import date
		self.fecha= date.today()
		self.usuario= self.env.uid
		self.cargo= ''
		self.nombre= ''
		return True


	@api.multi
	def do_eliminar(self):
		self.unlink()
		return True

	@api.model
	def create(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Permite dar Aprobaciones')])
				
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos de Aprobación") 

		t = super(aprobacion_users,self).create(vals)
		prueba = t.ids_conexion.split(',')
		if prueba[0] == 'purchase_order':
			self.env['purchase.order'].search([('id','=',int(prueba[1]))])[0].correo_informativo()
		return t


	@api.one
	def copy(self,default=None):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Permite dar Aprobaciones')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos de Aprobación") 

		if self.usuario.id and self.env.uid != self.usuario.id:
			raise osv.except_osv('Alerta!', "Esta aprobación fue realizado por otro usuario") 
		return super(aprobacion_users,self).copy(default)		


	@api.one
	def write(self,vals):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Permite dar Aprobaciones')])
		
		
		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

		if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
			raise osv.except_osv('Alerta!', "No tiene los permisos de Aprobación") 

		if self.usuario.id and self.env.uid != self.usuario.id:
			raise osv.except_osv('Alerta!', "Esta aprobación fue realizado por otro usuario") 

		return super(aprobacion_users,self).write(vals)

	@api.one
	def unlink(self):
		if 'supereliminate' in self.env.context:
			pass
		else:

			all_groups=self.env['res.groups']
			all_users =self.env['res.users']
			
			g1_ids = all_groups.search([('name','=',u'Permite dar Aprobaciones')])
			
			
			if not g1_ids: 
				raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.") 

			if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
				raise osv.except_osv('Alerta!', "No tiene los permisos de Aprobación") 

			if self.usuario.id and self.env.uid != self.usuario.id:
				raise osv.except_osv('Alerta!', "Esta aprobación fue realizado por otro usuario")

		return super(aprobacion_users,self).unlink()




class account_voucher(models.Model):
	_inherit= 'account.voucher'
	
	@api.one
	def aprobations_calculate(self):
		texto = 'account_voucher,' + str(self.id)
		vrp = []
		for i in self.env['aprobacion.users'].search([('ids_conexion','=',texto)]):
			vrp.append(i.id)
		self.aprobations = vrp

	aprobations = fields.Many2many('aprobacion.users',string='Aprobaciones',compute='aprobations_calculate',readonly="1")

	@api.multi
	def agregar_aprobation(self):
		compose_form = self.env.ref('aprobaciones_it.it_aprobacion_users_wizard_form', False)
		return {
			'name': 'Aprobación',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'aprobacion.users',
			'views': [(compose_form.id, 'form')],
			'view_id': compose_form.id,
			'target': 'new',
			'context': {'default_ids_conexion':'account_voucher,'+str(self.id), },
		}


class deliveries_to_pay(models.Model):
	_inherit='deliveries.to.pay'


	@api.one
	def aprobations_calculate(self):
		texto = 'deliveries_to_pay,' + str(self.id)
		vrp = []
		for i in self.env['aprobacion.users'].search([('ids_conexion','=',texto)]):
			vrp.append(i.id)
		self.aprobations = vrp

	aprobations = fields.Many2many('aprobacion.users',string='Aprobaciones',compute='aprobations_calculate',readonly="1")

	@api.multi
	def agregar_aprobation(self):
		compose_form = self.env.ref('aprobaciones_it.it_aprobacion_users_wizard_form', False)
		return {
			'name': 'Aprobación',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'aprobacion.users',
			'views': [(compose_form.id, 'form')],
			'view_id': compose_form.id,
			'target': 'new',
			'context': {'default_ids_conexion':'deliveries_to_pay,'+str(self.id), },
		}


class small_cash_another(models.Model):
	_inherit = 'small.cash.another'


	@api.one
	def aprobations_calculate(self):
		texto = 'small_cash,' + str(self.id)
		vrp = []
		for i in self.env['aprobacion.users'].search([('ids_conexion','=',texto)]):
			vrp.append(i.id)
		self.aprobations = vrp

	aprobations = fields.Many2many('aprobacion.users',string='Aprobaciones',compute='aprobations_calculate',readonly="1")

	@api.multi
	def agregar_aprobation(self):
		compose_form = self.env.ref('aprobaciones_it.it_aprobacion_users_wizard_form', False)
		return {
			'name': 'Aprobación',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'aprobacion.users',
			'views': [(compose_form.id, 'form')],
			'view_id': compose_form.id,
			'target': 'new',
			'context': {'default_ids_conexion':'small_cash,'+str(self.id), },
		}



class desembolso_personal(models.Model):
	_inherit = 'desembolso.personal'


	@api.one
	def aprobations_calculate(self):
		texto = 'desembolso_personal,' + str(self.id)
		vrp = []
		for i in self.env['aprobacion.users'].search([('ids_conexion','=',texto)]):
			vrp.append(i.id)
		self.aprobations = vrp

	aprobations = fields.Many2many('aprobacion.users',string='Aprobaciones',compute='aprobations_calculate',readonly="1")

	@api.multi
	def agregar_aprobation(self):
		compose_form = self.env.ref('aprobaciones_it.it_aprobacion_users_wizard_form', False)
		return {
			'name': 'Aprobación',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'aprobacion.users',
			'views': [(compose_form.id, 'form')],
			'view_id': compose_form.id,
			'target': 'new',
			'context': {'default_ids_conexion':'desembolso_personal,'+str(self.id), },
		}


class anticipo_proveedor(models.Model):
	_inherit = 'anticipo.proveedor'


	@api.one
	def aprobations_calculate(self):
		texto = 'anticipo_proveedor,' + str(self.id)
		vrp = []
		for i in self.env['aprobacion.users'].search([('ids_conexion','=',texto)]):
			vrp.append(i.id)
		self.aprobations = vrp

	aprobations = fields.Many2many('aprobacion.users',string='Aprobaciones',compute='aprobations_calculate',readonly="1")

	@api.multi
	def agregar_aprobation(self):
		compose_form = self.env.ref('aprobaciones_it.it_aprobacion_users_wizard_form', False)
		return {
			'name': 'Aprobación',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'aprobacion.users',
			'views': [(compose_form.id, 'form')],
			'view_id': compose_form.id,
			'target': 'new',
			'context': {'default_ids_conexion':'anticipo_proveedor,'+str(self.id), },
		}


class crossovered_budget(models.Model):
	_inherit = 'crossovered.budget'

	
	@api.one
	def aprobations_calculate(self):
		texto = 'crossovered_budget,' + str(self.id)
		vrp = []
		for i in self.env['aprobacion.users'].search([('ids_conexion','=',texto)]):
			vrp.append(i.id)
		self.aprobations = vrp

	aprobations = fields.Many2many('aprobacion.users',string='Aprobaciones',compute='aprobations_calculate',readonly="1")

	@api.multi
	def agregar_aprobation(self):
		compose_form = self.env.ref('aprobaciones_it.it_aprobacion_users_wizard_form', False)
		return {
			'name': 'Aprobación',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'aprobacion.users',
			'views': [(compose_form.id, 'form')],
			'view_id': compose_form.id,
			'target': 'new',
			'context': {'default_ids_conexion':'crossovered_budget,'+str(self.id), },
		}
