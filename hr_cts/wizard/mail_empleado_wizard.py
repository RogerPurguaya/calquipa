# -*- encoding: utf-8 -*-
import base64
from openerp     import models, fields, api
from openerp.osv import osv

import datetime

class mail_empleado_wizard(models.TransientModel):
	_name = 'mail.empleado.wizard'

	forma       = fields.Selection([('1','Todos'),('2','Uno')],'Imprimir',required=True,default='1')
	employee_id = fields.Many2one('hr.employee','Empleado')
	digital_sgn = fields.Binary('Firma', filename="may")

	in_charge = fields.Many2one('hr.employee', "Encargado", required=1)
	date      = fields.Date("Fecha", required=1)

	reporte = fields.Boolean('Reporte')
	boleta  = fields.Boolean('Boleta')

	@api.model
	def default_get(self, fields):
		res = super(mail_empleado_wizard,self).default_get(fields)		
		res['in_charge'] = self.env['hr.employee'].search([])[0].id
		res['date'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
		return res

	@api.multi
	def do_rebuild(self):
		hr  = self.env['hr.cts'].search([('id','=',self.env.context['active_id'])])[0]
		hrl = self.env['hr.cts.line'].search([('cts','=',self.env.context['active_id']),('employee_id','=',self.employee_id.id)])
		checks = {
			'reporte': self.reporte,
			'boleta' : self.boleta,
		}
		add_data = {
			'in_charge': self.in_charge.id,
			'date'    : self.date,
		}
		if self.forma == '1':
			return hr.make_email(hr.cts_lines2.ids, self.digital_sgn, checks, add_data)			
		if self.forma == '2':
			if len(hrl) == 0:
				raise osv.except_osv("Alerta!", u"No existe el empleado en el tareo.")
			else:
				return hr.make_email(hrl.id, self.digital_sgn, checks, add_data)
		return True