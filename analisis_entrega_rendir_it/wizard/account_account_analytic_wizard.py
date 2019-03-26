# -*- encoding: utf-8 -*-
from openerp.osv import osv
from openerp import models, fields, api


class analisis_entrega_rendir_wizard(osv.TransientModel):
	_name='analisis.entrega.rendir.wizard'
	
	partner_id =fields.Many2one('res.partner','Empleado',required=True)
	rendicion_id =fields.Many2one('deliveries.to.pay','Rendición',required=True)

	@api.multi
	def do_rebuild(self):
		aaar_obj = self.env['analisis.entrega.rendir.rep']		
		lstidsaaar = aaar_obj.search([('partner_id','=',self.partner_id.id),('rendicion_id','=',self.rendicion_id.id)])		
		#if (len(lstidsaaar) == 0):
		#	raise osv.except_osv('Alerta','No contiene datos.')
		
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		domain_tmp= [('partner_id','=',self.partner_id.id),('rendicion_id','=',self.rendicion_id.id)]

		
		result = mod_obj.get_object_reference('analisis_entrega_rendir_it', 'view_analisis_entrega_rendir_rep2')
		id = result and result[1] or False
		print id
		
		return {
			'domain' : domain_tmp,
			'type': 'ir.actions.act_window',
			'res_model': 'analisis.entrega.rendir.rep',
			'view_mode': 'tree',
			'view_type': 'form',
			'res_id': id,
			'views': [(False, 'tree')],
		}
