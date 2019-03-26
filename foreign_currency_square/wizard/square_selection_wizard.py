# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv

class square_selection_wizard(osv.TransientModel):
	_name='square.selection.wizard'
	
	
	period_ini = fields.Many2one('account.period', 'Periodo Inicio')
	period_fin = fields.Many2one('account.period', 'Periodo Fin')
	
	
	def get_number(self, char_value):
		print char_value
		res = 0
		if char_value[0:19] == 'Periodo de apertura':
			res = int(char_value[20:] + '00')
		else:
			res = int(char_value[3:7] + char_value[0:2])
		print 'res', res
		return res
	
	def print_report(self, cr, uid, ids, context=None):
		line_obj = self.pool.get('vst.square.foreign.currency')
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		
		if context == None:
			context = {}
		data = self.read(cr, uid, ids, [], context=context)[0]
		#print 'Fecha Fin', data['date_end']
		#context.update({'fiscalyear_id': data['period_ini'][0], 'period_id': data['period_id'][0], 'type': data['type']})
		
		filtro = []
		
		period_ini_id = data['period_ini'][0]
		period_fin_id = data['period_fin'][0]
		
		period_ini = self.get_number(self.pool.get('account.period').browse(cr, uid, period_ini_id, context=context).name)
		period_fin = self.get_number(self.pool.get('account.period').browse(cr, uid, period_fin_id, context=context).name)
		
		print 'period_ini', period_ini
		print 'period_fin', period_fin
		filtro.append(('periodo_orden', '>=', period_ini))
		filtro.append(('periodo_orden', '<=', period_fin))
		
		result = mod_obj.get_object_reference(cr, uid, 'account_sheet_work', 'action_account_sheet_work_simple')
		id = result and result[1] or False
		print id
		return {
			'domain' : filtro,
			'type': 'ir.actions.act_window',
			'res_model': 'vst.square.foreign.currency',
			'view_mode': 'tree',
			'view_type': 'form',
			'res_id': id,
			'views': [(False, 'tree')],
		}
		# raise osv.except_osv('Alerta', view_ref[1])		
		
	