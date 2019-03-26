# -*- encoding: utf-8 -*-
import base64
from openerp     import models, fields, api
from openerp.osv import osv

class boleta_cts_wizard(models.TransientModel):
	_name = 'boleta.cts.wizard'

	forma       = fields.Selection([('1','Todos'),('2','Uno')],'Imprimir',required=True,default='1')
	employee_id = fields.Many2one('hr.employee','Empleado')
	digital_sgn = fields.Binary('Firma', filename="may")

	@api.multi
	def do_rebuild(self):
		hr  = self.env['hr.cts'].search([('id','=',self.env.context['active_id'])])[0]
		hrl = self.env['hr.cts.line'].search([('cts','=',self.env.context['active_id']),('employee_id','=',self.employee_id.id)])
		if self.forma == '1':
			return hr.get_pdf(hr.cts_lines2.ids, self.digital_sgn)			
		if self.forma == '2':
			if len(hrl) == 0:
				raise osv.except_osv("Alerta!", u"No existe el empleado en el tareo.")
			else:
				return hr.get_pdf(hrl.id, self.digital_sgn)
		return True