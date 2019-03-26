# -*- encoding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs


class account_sheet_work_wizard(osv.TransientModel):
	_name='account.sheet.work.wizard'
	_inherit='account.sheet.work.wizard'
	
	period_ini = fields.Many2one('account.period','Periodo Inicial',required=True)
	period_end = fields.Many2one('account.period','Periodo Final',required=True)
	wizrd_level_sheet = fields.Selection((('1','Nivel 1'),
									('2','Nivel 2'),
									('3','Nivel 3'),
									('4','Nivel 4'),
									('5','Nivel 5'),
									('6','Nivel 6')
									),'Nivel',required=True)

	moneda = fields.Many2one('res.currency','Moneda', required=False)
	

	@api.onchange('period_ini')
	def _change_periodo_ini(self):
		if self.period_ini:
			self.period_end= self.period_ini


	@api.multi
	def do_rebuild(self):
		period_ini = self.period_ini
		period_end = self.period_end
		has_currency = self.moneda
		
		filtro = []
		
		currency = False
		if has_currency.id != False:
			user = self.env['res.users'].browse(self.env.uid)
			if user.company_id.id == False:
				raise osv.except_osv('Alerta!', "No existe una compañia configurada para el usuario actual.")
			if user.company_id.currency_id.id == False:
				raise osv.except_osv('Alerta!', "No existe una moneda configurada para la compañia del usuario actual.")
			
			if has_currency.id != user.company_id.currency_id.id:
				currency = True
			
	
		self.env.cr.execute("""
		DROP VIEW IF EXISTS account_sheet_work_simple CASCADE;
		CREATE OR REPLACE view account_sheet_work_simple as (
			select hoja.id,cuenta,aa.name as descripcion, debe,haber,saldodeudor,saldoacredor from get_hoja_trabajo_simple_six("""+ str(currency)+ """,periodo_num('""" + period_ini.code + """'),periodo_num('""" + period_end.code +"""'),'"""+str( int(self.wizrd_level_sheet) + 2 )+"""')as hoja
			left join account_account aa on aa.code= hoja.cuenta
			union all 
			select  
			1000001 as id,
			Null::varchar as cuenta,
			'Total' as descripcion,
			sum(debe) as debe,
			sum(haber) as haber,
			sum(saldodeudor) as saldodeudor,
			sum(saldoacredor) as saldoacredor
			from 
			get_hoja_trabajo_simple_six("""+ str(currency)+ """,periodo_num('""" + period_ini.code + """'),periodo_num('""" + period_end.code +"""'),'"""+str(int(self.wizrd_level_sheet) + 2)+"""')

			 
		)""")	
		
				
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']

		
		result = mod_obj.get_object_reference('account_sheet_work', 'action_account_sheet_work_simple')
		
		id = result and result[1] or False
		print id
		return {
			'domain' : filtro,
			'type': 'ir.actions.act_window',
			'res_model': 'account.sheet.work.simple',
			'view_mode': 'tree',
			'view_type': 'form',
			'res_id': id,
			'views': [(False, 'tree')],
		}
	