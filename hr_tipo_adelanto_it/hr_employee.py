# -*- encoding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs

class hr_employee(models.Model):
	_inherit = 'hr.employee'
	
	adelanto_id  = fields.One2many('hr.tipo.adelanto','employee_id','tipo adelanto')
	emergency_id = fields.One2many('hr.emergency.phones','employee_id','llamada de emergencia')

class hr_tipo_adelanto(models.Model):
	_name = 'hr.tipo.adelanto'

	employee_id = fields.Many2one('hr.employee','padre')

	name        = fields.Char('Nombre')
	relative    = fields.Char('Parentesco')
	birth_date  = fields.Date('Fecha de Nacimiento')
	age         = fields.Integer('Edad')

class hr_emergency_phones(models.Model):
	_name = 'hr.emergency.phones'

	employee_id = fields.Many2one('hr.employee','padre')
	
	name        = fields.Char('Nombre')
	phone       = fields.Char(u'Teléfono')