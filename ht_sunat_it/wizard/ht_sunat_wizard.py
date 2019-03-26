# -*- encoding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs

class ht_sunat_txt_wizard(osv.TransientModel):
	_name='ht.sunat.txt.wizard'

	form_pdt = fields.Char('Formulario PDT',size=40,required=False)
	ejercicio = fields.Many2one('account.fiscalyear',string='Ejercicio',required=True)
	tipo = fields.Selection( (('pantalla','Pantalla'),('txt','Txt')), 'Mostrar', required=True)



	@api.multi
	def do_rebuild(self):
		self.env.cr.execute(""" 

			DROP VIEW IF EXISTS ht_sunat;
			create or replace view ht_sunat as (



select row_number() OVER() as id,* from (
select aa.code_sunat as cuenta, 
sum( coalesce(totaldebe,0) )  as debe_si, 
sum( coalesce(totalhaber,0) )  as haber_si, 
sum( coalesce(debe,0) )  as debe, 
sum( coalesce(haber,0) )  as haber,
0 as debe_trans,
0 as haber_trans
  from get_reporte_hoja_registro(false,periodo_num('12/""" + str(self.ejercicio.name) +"""'),periodo_num('12/""" + str(self.ejercicio.name) +"""')) X
inner join account_account aa on aa.code = X.cuenta
where aa.code_sunat is not null
group by aa.code_sunat
order by aa.code_sunat ) X


		)""")


		if self.tipo == 'pantalla':
			return {
				'name':'B. Comprobación',
			    "type": "ir.actions.act_window",
			    "res_model": "ht.sunat",
			    'view_mode': 'tree',
                'view_type': 'form',
			}

		if self.tipo == 'txt':

			self.env.cr.execute("""
				


select * from (
select aa.code_sunat as cuenta, 
sum( coalesce(totaldebe,0) )  as debe_si, 
sum( coalesce(totalhaber,0) )  as haber_si, 
sum( coalesce(debe,0) )  as debe, 
sum( coalesce(haber,0) )  as haber,
0 as debe_trans,
0 as haber_trans
  from get_reporte_hoja_registro(false,periodo_num('12/""" + str(self.ejercicio.name) +"""'),periodo_num('12/""" + str(self.ejercicio.name) +"""')) X
inner join account_account aa on aa.code = X.cuenta
where aa.code_sunat is not null
group by aa.code_sunat
order by aa.code_sunat ) X
""")

			tra = self.env.cr.fetchall()
			
			
			import sys
			sys.setdefaultencoding('iso-8859-1')
			mod_obj = self.env['ir.model.data']
			act_obj = self.env['ir.actions.act_window']
			rpta = ""
			for i in tra:
				rpta += i[0] + '|'+ "%0.2f" %i[1]+ '|'+ "%0.2f" %i[2]+ '|'+ "%0.2f" %i[3]+ '|'+ "%0.2f" %i[4]+ '|'+ "%0.2f" %i[5]+ '|'+ "%0.2f" %i[6] + "\n"

			xui = self.env['res.company'].search([])[0].partner_id.type_number
			vals = {
				'output_name': str(self.form_pdt) + str(xui) + str(self.ejercicio.name) + '.txt',
				'output_file': base64.encodestring(" " if rpta=="" else rpta),		
			}
			sfs_id = self.env['export.file.save'].create(vals)
			result = {}
			view_ref = mod_obj.get_object_reference('account_contable_book_it', 'export_file_save_action')
			view_id = view_ref and view_ref[1] or False
			result = act_obj.read( [view_id] )
			print sfs_id
			return {
			    "type": "ir.actions.act_window",
			    "res_model": "export.file.save",
			    "views": [[False, "form"]],
			    "res_id": sfs_id.id,
			    "target": "new",
			}
		


	@api.multi
	def do_rebuilds(self):
		self.env.cr.execute(""" 

			DROP VIEW IF EXISTS ht_sunat;
			create or replace view ht_sunat as (



select row_number() OVER() as id,* from (
select aa.code_sunat as cuenta, 
sum( coalesce(totaldebe,0) )  as debe_si, 
sum( coalesce(totalhaber,0) )  as haber_si, 
sum( coalesce(debe,0) )  as debe, 
sum( coalesce(haber,0) )  as haber,
0 as debe_trans,
0 as haber_trans
  from get_reporte_hoja_registro(false,periodo_num('12/""" + str(self.ejercicio.name) +"""'),periodo_num('12/""" + str(self.ejercicio.name) +"""')) X
inner join account_account aa on aa.code = X.cuenta
where aa.code_sunat is not null
group by aa.code_sunat
order by aa.code_sunat ) X


		)""")


		if self.tipo == 'pantalla':
			return {
				'name':'B. Comprobación',
			    "type": "ir.actions.act_window",
			    "res_model": "ht.sunat",
			    'view_mode': 'tree',
                'view_type': 'form',
			}

		if self.tipo == 'txt':

			self.env.cr.execute("""
				


select * from (
select aa.code_sunat as cuenta, 
sum( coalesce(totaldebe,0) )  as debe_si, 
sum( coalesce(totalhaber,0) )  as haber_si, 
sum( coalesce(debe,0) )  as debe, 
sum( coalesce(haber,0) )  as haber,
0 as debe_trans,
0 as haber_trans
  from get_reporte_hoja_registro(false,periodo_num('12/""" + str(self.ejercicio.name) +"""'),periodo_num('12/""" + str(self.ejercicio.name) +"""')) X
inner join account_account aa on aa.code = X.cuenta
where aa.code_sunat is not null
group by aa.code_sunat
order by aa.code_sunat ) X
""")

			tra = self.env.cr.fetchall()
			
			
			import sys
			sys.setdefaultencoding('iso-8859-1')
			mod_obj = self.env['ir.model.data']
			act_obj = self.env['ir.actions.act_window']
			rpta = ""
			for i in tra:
				rpta += i[0] + '|'+ "%0.2f" %i[1]+ '|'+ "%0.2f" %i[2]+ '|'+ "%0.2f" %i[3]+ '|'+ "%0.2f" %i[4]+ '|'+ "%0.2f" %i[5]+ '|'+ "%0.2f" %i[6] + "\n"

			xui = self.env['res.company'].search([])[0].partner_id.type_number
			vals = {
				'output_name': str(self.form_pdt) + str(xui) + str(self.ejercicio.name) + '.txt',
				'output_file': base64.encodestring(" " if rpta=="" else rpta),		
			}
			sfs_id = self.env['export.file.save'].create(vals)
			result = {}
			view_ref = mod_obj.get_object_reference('account_contable_book_it', 'export_file_save_action')
			view_id = view_ref and view_ref[1] or False
			result = act_obj.read( [view_id] )
			print sfs_id
			return {
			    "type": "ir.actions.act_window",
			    "res_model": "export.file.save",
			    "views": [[False, "form"]],
			    "res_id": sfs_id.id,
			    "target": "new",
			}
		