# -*- encoding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs
import pprint

class account_retention_wizard(osv.TransientModel):
	_name='account.retention.wizard'
	period_ini = fields.Many2one('account.period','Periodo Inicial',required=True)
	type_show =  fields.Selection([('pantalla','Pantalla'),('csv','Txt')], 'Mostrar en', required=True)
	
	
	@api.multi
	def do_rebuild(self):
		period_ini = self.period_ini
		
		filtro = [('periodo','=',period_ini.name)]

		self.env.cr.execute("""
		DROP VIEW IF EXISTS account_retention;
			CREATE OR REPLACE view account_retention as (
				SELECT * 
				FROM get_retentions(periodo_num('""" + period_ini.code + """')) 
		)""")

		
		if self.type_show == 'pantalla':
			mod_obj = self.env['ir.model.data']
			act_obj = self.env['ir.actions.act_window']

			result = mod_obj.get_object_reference('account_retentions_it', 'action_account_retention')
			
			id = result and result[1] or False
			print id
			return {
				'domain' : filtro,
				'type': 'ir.actions.act_window',
				'res_model': 'account.retention',
				'view_mode': 'tree',
				'view_type': 'form',
				'res_id': id,
				'views': [(False, 'tree')],
			}
		if self.type_show == 'csv':
			import sys
			sys.setdefaultencoding('iso-8859-1')
			mod_obj = self.env['ir.model.data']
			act_obj = self.env['ir.actions.act_window']
			Str_csv = self.env['account.retention'].search(filtro).mapped(lambda r: self.csv_convert(r,'|'))
			rpta = ""
			#rpta = self.cabezera_csv('|') + "\n"
			for i in Str_csv:
				rpta += i.encode('iso-8859-1','ignore') + "\r\n"

			code = '0601'
			periodo = period_ini.code
			periodo = periodo.split('/')
			name = periodo[1]+periodo[0]
			user = self.env['res.users'].browse(self.env.uid)

			if user.company_id.id == False:
				raise osv.except_osv('Alerta','El usuario actual no tiene una compañia asignada. Contacte a su administrador.')
			if user.company_id.partner_id.id == False:
				raise osv.except_osv('Alerta','La compañia del usuario no tiene una empresa asignada. Contacte a su administrador.')
			if user.company_id.partner_id.type_number == False:
				raise osv.except_osv('Alerta','La compañia del usuario no tiene un numero de documento. Contacte a su administrador.')

			ruc = user.company_id.partner_id.type_number

			file_name = code + ruc + name + '.TXT'	
				
				
			vals = {
				'output_name': file_name,
				'output_file': base64.encodestring(rpta),		
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
	def csv_verif_integer(self,data):
		if data:
			return str(data)
		else:
			return ''

	@api.multi
	def csv_verif(self,data):
		if data:
			return data
		else:
			return ''
	@api.multi
	def csv_convert(self,data,separador):
		tmp = self.csv_verif(data.ruc_proveedor)
		tmp += separador+ self.csv_verif(data.razon_social)
		tmp += separador+ self.csv_verif(data.apellido_paterno)
		tmp += separador+ self.csv_verif(data.apellido_materno)
		tmp += separador+ self.csv_verif(data.nombres)
		tmp += separador+ self.csv_verif(data.serie)
		tmp += separador+ self.csv_verif(data.numero)
		tmp += separador+ self.csv_verif(data.fecha_emision)
		tmp += separador+ self.csv_verif_integer(data.monto_retention)
		tmp += separador+ self.csv_verif(data.tipo_doc)
		tmp += separador+ self.csv_verif(data.serie_doc)
		tmp += separador+ self.csv_verif(data.numero_doc)
		tmp += separador+ self.csv_verif(data.fecha_doc)
		tmp += separador+ self.csv_verif_integer(data.total_doc)
		tmp += separador
		return unicode(tmp)
		
	@api.multi
	def cabezera_csv(self,separador):
		tmp = separador + self.csv_verif("Periodo")
		tmp += separador+ self.csv_verif("Libro")
		tmp += separador+ self.csv_verif("Voucher")
		tmp += separador+ self.csv_verif("Fecha Emision")
		tmp += separador+ self.csv_verif("Fecha Vencimiento")
		tmp += separador+ self.csv_verif("T.D.")
		tmp += separador+ self.csv_verif("Serie")
		tmp += separador+ self.csv_verif("Numero")
		tmp += separador+ self.csv_verif("Tipo de Documento")
		tmp += separador+ self.csv_verif("Num. Documento")
		tmp += separador+ self.csv_verif("Partner")
		tmp += separador+ self.csv_verif("ValorExp")
		tmp += separador+ self.csv_verif("BaseImp")
		tmp += separador+ self.csv_verif("Inafecto")
		tmp += separador+ self.csv_verif("Exonerado")
		tmp += separador+ self.csv_verif("Isc")
		tmp += separador+ self.csv_verif("Igv")
		tmp += separador+ self.csv_verif("Otros")
		tmp += separador+ self.csv_verif("Total")
		tmp += separador+ self.csv_verif("Divisa")
		tmp += separador+ self.csv_verif("Tipo de Cambio")
		tmp += separador+ self.csv_verif("T.D.M")
		tmp += separador+ self.csv_verif("Serie D.")
		tmp += separador+ self.csv_verif("Numero D.")
		tmp += separador
		return unicode(tmp)
		