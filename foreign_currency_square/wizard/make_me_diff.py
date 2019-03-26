# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv

class make_me_diff(osv.TransientModel):
	_name = "make.me.diff"

	
	account_id = fields.Many2one('account.account','Seleccionar cuenta Para Gastos')
	account_analytic_id = fields.Many2one('account.analytic.account','Seleccionar cuenta analítica Para Gastos')
	

	def view_init(self, cr, uid, fields_list, context=None):
		if context is None:
			context = {}
		record_id = context and context.get('active_id', False)
		return False

	def make_calculate_differences(self, cr, uid, ids, context=None):
		line_obj = self.pool.get('vst.square.foreign.currency')
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		analytic_obj = self.pool.get('account.analytic.account')

		data = self.read(cr, uid, ids, [], context=context)[0]
		analytic_data_id = data['account_analytic_id'][0]
		account_id = data['account_id'][0]



		analytic_id = analytic_obj.browse(cr,uid,analytic_data_id,context=context)

		if context is None:
			context = {}
		# for install_act in picking_obj.browse(cr, uid, context.get(('active_ids'), []), context=context):
			# if install_act.state == 'draft':
			# 	raise osv.except_osv('Alerta', 'No es posible procesar notas en borrador')
		#data = self.read(cr, uid, ids, [], context=context)[0]
		#print 'Fecha Fin', data['date_end']
		#context.update({'journal_id': data['journal_id'][0]}) 
		ids2=line_obj.make_calculate_differences(cr, uid, context.get(('active_ids'), []),analytic_id.id,account_id, context)
		if ids2==[]:
			raise osv.except_osv('Alerta','No se calculo la diferencias, verifique que los elementos seleccionados')
		
		result={}
		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'foreign_currency_square','vst_square_foreign_currency_action')
		# raise osv.except_osv('Alerta', view_ref[1])		
		view_id = view_ref and view_ref[1] or False
		result = act_obj.read(cr, uid, [view_id], context=context)[0]
		return result
		