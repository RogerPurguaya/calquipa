# -*- encoding: utf-8 -*-
import base64
from openerp.osv import osv
from openerp import models, fields, api
from datetime import date,timedelta


class hr_employee(models.Model):
	_inherit = 'hr.employee'


	afiliacion        = fields.Many2one('hr.table.membership','Afiliación AFP')
	type_document_id  = fields.Many2one('it.type.document.partner','Tipo de Documento')
	cusspp            = fields.Char('CUSSPP')
	c_mixta           = fields.Boolean('Comisión Mixta')
	fecha_cese        = fields.Date('Fecha cese')
	basica            = fields.Float('Básico', digits=(12,2))
	direccion_text	  = fields.Char(u'Dirección')
	dist_c            = fields.Many2one('hr.distribucion.gastos','Dist. C.C.')
	banco_cts         = fields.Char('Banco CTS', size=50)
	banco_rem         = fields.Char('Banco Rem', size=50)
	cta_cts           = fields.Char('Nro. de Cta. CTS', size=50)
	cta_rem           = fields.Char('Nro. de Cta. Rem', size=50)
	tipo_trabajador   = fields.Many2one('tipo.trabajador','Tipo de Trabajador')
	codigo_trabajador = fields.Char('Código de Trabajador')
	condicion         = fields.Char('Condición')
	situacion         = fields.Char('Situación')
	no_domiciliado    = fields.Boolean('No domiciliado')
	use_eps           = fields.Boolean('Aport. EPS')
	essalud_vida	  = fields.Boolean('EsSalud Vida')
	fondo_jub		  = fields.Boolean(u'Fondo Jubilación')

	cuenta_adelanto = fields.Many2one('account.account','Cuenta de adelanto')
	situacion       = fields.Char('Situación', readonly=1, compute="get_situacion")
	is_practicant   = fields.Boolean('Practicante', default=False)

	@api.model
	def create(self, vals):
		t = super(hr_employee,self).create(vals)
		if 'identification_id' in vals:
			if len(self.env['hr.employee'].search([('identification_id','=',t.identification_id)])) > 1:
				raise osv.except_osv("Alerta!", u"Ya existe un empleado con el dni "+t.identification_id+" .")
		return t

	@api.one
	def write(self, vals):
		t = super(hr_employee,self).write(vals)
		self.refresh()
		if 'identification_id' in vals:
			if len(self.env['hr.employee'].search([('identification_id','=',self.identification_id)])) > 1:
				raise osv.except_osv("Alerta!", u"Ya existe un empleado con el dni "+self.identification_id+" .")
		return t

	@api.one
	def get_situacion(self):
		if self.fecha_cese:		
			if self.fecha_cese >= str(date.today())[:10]:
				self.situacion = "Activo"
			else:
				self.situacion = "Baja"

		else:
			self.situacion = "Activo"

class tipo_trabajador(models.Model):
	_name     = 'tipo.trabajador'
	_rec_name = 'name'

	name = fields.Char('nombre')