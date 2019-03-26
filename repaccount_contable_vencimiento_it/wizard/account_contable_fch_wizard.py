# -*- encoding: utf-8 -*-

from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs
import pprint

class account_contable_vencimiento_wizard(osv.TransientModel):
	_name='account.contable.vencimiento.wizard'

	date = fields.Date('Fecha')
	type_account = fields.Selection((('cc1','Cuentas Por Pagar'),
									('cc2','Cuentas Por Cobrar')
									),'Tipo')
	cuenta_id = fields.Many2one('account.account','Cuenta')
	partner_id =fields.Many2one('res.partner','Empresa')
	forma_reporte = fields.Selection((('fila','Por Filas'),
									('col','Por Columnas'),
									('cola','Por Columnas Agrupado por Empresa')
									),'Forma de Reporte')
	mostrar_en = fields.Selection((('pantalla','Pantalla'),
									('excel','Excel')
									),'Mostrar en')


	@api.onchange('type_account')
	def _onchange_type_account(self):
		if self.type_account:
			if str(self.type_account) == "cc1":
				return {'domain':{'cuenta_id':[('type','=','payable')]}}
			elif str(self.type_account) == "cc2":
				return {'domain':{'cuenta_id':[('type','=','receivable')]}}
		else:
			return {'domain':{'cuenta_id':[('type','in',('payable','receivable'))]}}

	@api.multi
	def do_rebuild(self):

		move_obj = self.env['account.contable.period']
		filtro = []

		tipef = self.type_account
		#filtro.append( ('fecha_maturity','!=',False) )

		if self.partner_id:
			filtro.append( ('partner_id','=',self.partner_id.id) )
		if self.cuenta_id:
			filtro.append( ('account_id','=',self.cuenta_id.id) )
		if str(tipef) == 'cc1':
			filtro.append( ('tipofiltro','=','payable') )
		if str(tipef) == 'cc2':
			filtro.append( ('tipofiltro','=','receivable') )


		lstidsmove= move_obj.search(filtro)

		if (len(lstidsmove) == 0):
			raise osv.except_osv('Alerta','No contiene datos.')
		

		if self.forma_reporte == 'fila':
			self.env.cr.execute("DELETE FROM account_contable_vencimiento_fila where user_guardado =" + str(self.env.uid))
			for elemento in lstidsmove:

				#if elemento.fecha_maturity !=False and elemento.saldo_total!= 0 and self.date< elemento.fecha_maturity:
				if elemento.fecha_maturity !=False and elemento.saldo!= 0 :

					self.env.cr.execute("select '"+ str(elemento.fecha_maturity) + "'::date - '"+ str(self.date)+ "'::date")
					num_t = self.env.cr.fetchall()
					num_a= num_t[0][0]
					venci = None
					venci = 'Vencida' if num_a < 0 else venci
					venci = "DE 0 a 15 " if num_a >=0 and num_a<=15 else venci
					venci = "DE 16 a 30" if num_a >=16 and num_a<=30 else venci
					venci = "DE 31 a 45" if num_a >=31 and num_a<=45 else venci
					venci = "DE 46 a 60" if num_a >=46 and num_a<=60 else venci
					venci = "DE 61 a 90" if num_a >=61 and num_a<=90 else venci
					venci = "DE 91 a 180" if num_a >=91 and num_a<=180 else venci
					venci = "MAS de 180" if num_a >180 else venci
					
					data = {
						'vencimiento':venci,
						'periodo': elemento.periodo,
						'libro':elemento.libro,
						'cuenta':elemento.cuenta,
						'voucher':elemento.voucher,
						'fecha_emision':elemento.fecha,
						'fecha_vencimiento':elemento.fecha_maturity,
						'nro_comprobante':elemento.comprobante,
						'empresa':elemento.partner,
						'saldo':elemento.saldo,
						'user_guardado': self.env.uid,
					}
					self.env['account.contable.vencimiento.fila'].create(data)


			if self.mostrar_en == 'pantalla':

				return {
					'domain': [('user_guardado','=',self.env.uid)],
					'name': 'Análisis de Vencimiento',
					'type': 'ir.actions.act_window',
					'res_model': 'account.contable.vencimiento.fila',
					'view_mode': 'tree,graph',
					'view_type': 'form',
					'views': [(False, 'tree'),(False, 'graph')],
				}
			else:

				import io
				from xlsxwriter.workbook import Workbook
				output = io.BytesIO()
				########### PRIMERA HOJA DE LA DATA EN TABLA
				#workbook = Workbook(output, {'in_memory': True})
				direccion = self.env['main.parameter'].search([])[0].dir_create_file
				workbook = Workbook( direccion + 'tempo_cuentacorrientefila.xlsx')
				worksheet = workbook.add_worksheet("Analisis Vencimiento")
				bold = workbook.add_format({'bold': True})
				normal = workbook.add_format()
				boldbord = workbook.add_format({'bold': True})
				boldbord.set_border(style=2)
				boldbord.set_align('center')
				boldbord.set_align('vcenter')
				boldbord.set_text_wrap()
				boldbord.set_font_size(9)
				boldbord.set_bg_color('#DCE6F1')


				title = workbook.add_format({'bold': True})
				title.set_align('center')
				title.set_align('vcenter')
				title.set_text_wrap()
				title.set_font_size(18)
				numbertres = workbook.add_format({'num_format':'0.000'})
				numberdos = workbook.add_format({'num_format':'0.00'})
				bord = workbook.add_format()
				bord.set_border(style=1)
				numberdos.set_border(style=1)
				numbertres.set_border(style=1)			
				x= 5				
				tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
				tam_letra = 1.2
				import sys
				reload(sys)
				sys.setdefaultencoding('iso-8859-1')


				worksheet.merge_range(0,0,0,15,u"Análisis de Vencimiento",title)

				worksheet.write(1,0, "Fecha:", bold)
				
				worksheet.write(1,1, self.date, normal)
								
				#worksheet.write(1,1, total.date.strftime('%Y-%m-%d %H:%M'),bord)
				
				worksheet.write(4,0, "Vencimiento",boldbord)
				
				worksheet.write(4,1, "Periodo",boldbord)
				worksheet.write(4,2, "Libro",boldbord)
				worksheet.write(4,3, "Cuenta",boldbord)				
				worksheet.write(4,4, u"Voucher",boldbord)

				worksheet.write(4,5, u"Fecha Emisión",boldbord)
				worksheet.write(4,6, "Fecha Vencimiento",boldbord)

				worksheet.write(4,7, "Nro. Comprobante",boldbord)
				worksheet.write(4,8, u"Empresa",boldbord)
				worksheet.write(4,9, "Saldo",boldbord)

				for line in self.env['account.contable.vencimiento.fila'].search([('user_guardado','=',self.env.uid)]):
					worksheet.write(x,0,line.vencimiento if line.vencimiento else '' ,bord )
					worksheet.write(x,1,line.periodo if line.periodo  else '',bord )
					worksheet.write(x,2,line.libro if line.libro  else '',bord)
					worksheet.write(x,3,line.cuenta if line.cuenta  else '',bord)
					worksheet.write(x,4,line.voucher if line.voucher else '',bord)
					worksheet.write(x,5,line.fecha_emision if line.fecha_emision else '',bord)
					worksheet.write(x,6,line.fecha_vencimiento if line.fecha_vencimiento else '',bord)
					worksheet.write(x,7,line.nro_comprobante if line.nro_comprobante else '',bord)
					worksheet.write(x,8,line.empresa if line.empresa  else '',bord)
					worksheet.write(x,9,line.saldo ,numberdos)

					x = x +1

				tam_col = [16,7,10,13,16,16,16,20,14]
				worksheet.set_row(0, 30)

				worksheet.set_column('A:A', tam_col[0])
				worksheet.set_column('B:B', tam_col[1])
				worksheet.set_column('C:C', tam_col[2])
				worksheet.set_column('D:D', tam_col[3])
				worksheet.set_column('E:E', tam_col[4])
				worksheet.set_column('F:F', tam_col[5])
				worksheet.set_column('G:G', tam_col[6])
				worksheet.set_column('H:H', tam_col[7])
				worksheet.set_column('I:I', tam_col[8])
				workbook.close()
				
				f = open(direccion + 'tempo_cuentacorrientefila.xlsx', 'rb')
				
				
				sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
				vals = {
					'output_name': 'AnalisisVencimiento.xlsx',
					'output_file': base64.encodestring(''.join(f.readlines())),		
				}

				mod_obj = self.env['ir.model.data']
				act_obj = self.env['ir.actions.act_window']
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

		



		if self.forma_reporte == 'col':
			self.env.cr.execute("DELETE FROM account_contable_vencimiento_columna where user_guardado =" + str(self.env.uid))
			for elemento in lstidsmove:

				if elemento.fecha_maturity !=False and elemento.saldo!= 0 :

					self.env.cr.execute("select '"+ str(elemento.fecha_maturity) + "'::date - '"+ str(self.date)+ "'::date")
					num_t = self.env.cr.fetchall()
					num_a= num_t[0][0]
					vencivencida = elemento.saldo if num_a <0 else 0
					vencigama = elemento.saldo if num_a >=0 and num_a<=15 else 0
					vencia = elemento.saldo if num_a >=16 and num_a<=30 else 0
					vencib = elemento.saldo if num_a >=31 and num_a<=45 else 0
					vencic = elemento.saldo if num_a >=46 and num_a<=60 else 0
					vencid = elemento.saldo if num_a >=61 and num_a<=90 else 0
					vencie = elemento.saldo if num_a >=91 and num_a<=180 else 0
					vencif = elemento.saldo if num_a >180 else 0
					
					data = {
						'nro_comprobante':elemento.comprobante,
						'cuenta': elemento.cuenta,
						'fecha_emision':elemento.fecha,
						'empresa':elemento.partner,
						'vencidos': vencivencida,
						'menos16':vencigama,
						'de16a30':vencia,
						'de31a45':vencib,
						'de46a60':vencic,
						'de61a90':vencid,
						'de91a180':vencie,
						'mas180':vencif,
						'user_guardado': self.env.uid,

					}
					self.env['account.contable.vencimiento.columna'].create(data)


			if self.mostrar_en == 'pantalla':
				return {
					'domain': [('user_guardado','=',self.env.uid)],
					'name': 'Análisis de Vencimiento',
					'type': 'ir.actions.act_window',
					'res_model': 'account.contable.vencimiento.columna',
					'view_mode': 'tree,graph',
					'view_type': 'form',
					'views': [(False, 'tree'),(False, 'graph')],
				}


			else:

				import io
				from xlsxwriter.workbook import Workbook
				output = io.BytesIO()
				########### PRIMERA HOJA DE LA DATA EN TABLA
				#workbook = Workbook(output, {'in_memory': True})
				direccion = self.env['main.parameter'].search([])[0].dir_create_file
				workbook = Workbook( direccion + 'tempo_cuentacorrientecolumna.xlsx')
				worksheet = workbook.add_worksheet("Analisis Vencimiento")
				bold = workbook.add_format({'bold': True})
				normal = workbook.add_format()
				boldbord = workbook.add_format({'bold': True})
				boldbord.set_border(style=2)
				boldbord.set_align('center')
				boldbord.set_align('vcenter')
				boldbord.set_text_wrap()
				boldbord.set_font_size(9)
				boldbord.set_bg_color('#DCE6F1')


				title = workbook.add_format({'bold': True})
				title.set_align('center')
				title.set_align('vcenter')
				title.set_text_wrap()
				title.set_font_size(18)
				numbertres = workbook.add_format({'num_format':'0.000'})
				numberdos = workbook.add_format({'num_format':'0.00'})
				bord = workbook.add_format()
				bord.set_border(style=1)
				numberdos.set_border(style=1)
				numbertres.set_border(style=1)			
				x= 5				
				tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
				tam_letra = 1.2
				import sys
				reload(sys)
				sys.setdefaultencoding('iso-8859-1')


				worksheet.merge_range(0,0,0,15,u"Análisis de Vencimiento",title)

				worksheet.write(1,0, "Fecha:", bold)
				
				worksheet.write(1,1, self.date, normal)
								
				#worksheet.write(1,1, total.date.strftime('%Y-%m-%d %H:%M'),bord)
				

				worksheet.write(4,0, u"Fecha Emisión",boldbord)
				worksheet.write(4,1, "Nro. Comprobante",boldbord)
				worksheet.write(4,2, "Cuenta",boldbord)
				
				worksheet.write(4,3, "Empresa",boldbord)
				worksheet.write(4,4, "Vencidas",boldbord)
				worksheet.write(4,5, "De 0 a 15 ",boldbord)
				worksheet.write(4,6, "De 16 a 30",boldbord)
				worksheet.write(4,7, u"De 31 a 45",boldbord)

				worksheet.write(4,8, u"De 46 a 60",boldbord)
				worksheet.write(4,9, "De 61 a 90",boldbord)

				worksheet.write(4,10, "De 91 a 180",boldbord)
				worksheet.write(4,11, u"Mas de 180",boldbord)

				for line in self.env['account.contable.vencimiento.columna'].search([('user_guardado','=',self.env.uid)]):
					worksheet.write(x,0,line.fecha_emision if line.fecha_emision else '' ,bord )
					worksheet.write(x,1,line.nro_comprobante if line.nro_comprobante else '' ,bord )
					worksheet.write(x,2,line.cuenta if line.cuenta else '' ,bord )
					worksheet.write(x,3,line.empresa if line.empresa  else '',bord )
					worksheet.write(x,4,line.vencidos ,numberdos)
					worksheet.write(x,5,line.menos16 ,numberdos)
					worksheet.write(x,6,line.de16a30 ,numberdos)
					worksheet.write(x,7,line.de31a45 ,numberdos)
					worksheet.write(x,8,line.de46a60 ,numberdos)
					worksheet.write(x,9,line.de61a90 ,numberdos)
					worksheet.write(x,10,line.de91a180 ,numberdos)
					worksheet.write(x,11,line.mas180 ,numberdos)

					x = x +1

				tam_col = [12,16,9,10,10,10,10,10,10,10,10,10]
				worksheet.set_row(0, 30)

				worksheet.set_column('A:A', tam_col[0])
				worksheet.set_column('B:B', tam_col[1])
				worksheet.set_column('C:C', tam_col[2])
				worksheet.set_column('D:D', tam_col[3])
				worksheet.set_column('E:E', tam_col[4])
				worksheet.set_column('F:F', tam_col[5])
				worksheet.set_column('G:G', tam_col[6])
				worksheet.set_column('H:H', tam_col[7])
				worksheet.set_column('I:I', tam_col[8])
				worksheet.set_column('J:J', tam_col[9])
				worksheet.set_column('K:K', tam_col[10])
				workbook.close()
				
				f = open(direccion + 'tempo_cuentacorrientecolumna.xlsx', 'rb')
				
				
				sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
				vals = {
					'output_name': 'AnalisisVencimiento.xlsx',
					'output_file': base64.encodestring(''.join(f.readlines())),		
				}

				mod_obj = self.env['ir.model.data']
				act_obj = self.env['ir.actions.act_window']
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

		


		if self.forma_reporte == 'cola':
			self.env.cr.execute("DELETE FROM account_contable_vencimiento_columna where user_guardado =" + str(self.env.uid))
			for elemento in lstidsmove:

				if elemento.fecha_maturity !=False and elemento.saldo!= 0:

					self.env.cr.execute("select '"+ str(elemento.fecha_maturity) + "'::date - '"+ str(self.date)+ "'::date")
					num_t = self.env.cr.fetchall()
					num_a= num_t[0][0]

					vencivencida = elemento.saldo if num_a <0 else 0
					vencigama = elemento.saldo if num_a >=0 and num_a<=15 else 0
					vencia = elemento.saldo if num_a >=16 and num_a<=30 else 0
					vencib = elemento.saldo if num_a >=31 and num_a<=45 else 0
					vencic = elemento.saldo if num_a >=46 and num_a<=60 else 0
					vencid = elemento.saldo if num_a >=61 and num_a<=90 else 0
					vencie = elemento.saldo if num_a >=91 and num_a<=180 else 0
					vencif = elemento.saldo if num_a >180 else 0
					
					data = {
						'nro_comprobante':elemento.comprobante,
						'cuenta':elemento.cuenta,
						'empresa':elemento.partner,
						'vencidos': vencivencida,
						'menos16':vencigama,
						'de16a30':vencia,
						'de31a45':vencib,
						'de46a60':vencic,
						'de61a90':vencid,
						'de91a180':vencie,
						'mas180':vencif,
						'user_guardado': self.env.uid,

					}
					self.env['account.contable.vencimiento.columna'].create(data)


			self.env.cr.execute("DELETE FROM account_contable_vencimiento_columna_agrupada where user_guardado =" + str(self.env.uid))
			empresa_r = None
			vvencida = 0
			vgama= 0
			va = 0
			vb = 0
			vc = 0
			vd = 0
			ve = 0
			vf = 0

			for elemento in self.env['account.contable.vencimiento.columna'].search([('user_guardado','=',self.env.uid)]).sorted(key=lambda r: r.empresa):
					if empresa_r == None:
						empresa_r = elemento.empresa

					if empresa_r != elemento.empresa:
						data = {
							'empresa':empresa_r,
							'menos16':vgama,
							'vencidos': vvencida,
							'de16a30':va,
							'de31a45':vb,
							'de46a60':vc,
							'de61a90':vd,
							'de91a180':ve,
							'mas180':vf,
							'user_guardado': self.env.uid,

						}
						self.env['account.contable.vencimiento.columna.agrupada'].create(data)
						vvencida = elemento.vencidos
						vgama = elemento.menos16
						va = elemento.de16a30
						vb = elemento.de31a45
						vc = elemento.de46a60
						vd = elemento.de61a90
						ve = elemento.de91a180
						vf = elemento.mas180
						empresa_r = elemento.empresa
					else:
						vvencida += elemento.vencidos
						vgama += elemento.menos16
						va += elemento.de16a30
						vb += elemento.de31a45
						vc += elemento.de46a60
						vd += elemento.de61a90
						ve += elemento.de91a180
						vf += elemento.mas180

			if empresa_r != None:
				data = {
					'empresa':empresa_r,
					'vencidos': vvencida,
					'menos16':vgama,
					'de16a30':va,
					'de31a45':vb,
					'de46a60':vc,
					'de61a90':vd,
					'de91a180':ve,
					'mas180':vf,
					'user_guardado': self.env.uid,

				}
				self.env['account.contable.vencimiento.columna.agrupada'].create(data)

			if self.mostrar_en == 'pantalla':
				return {
					'domain': [('user_guardado','=',self.env.uid)],
					'name': 'Análisis de Vencimiento',
					'type': 'ir.actions.act_window',
					'res_model': 'account.contable.vencimiento.columna.agrupada',
					'view_mode': 'tree,graph',
					'view_type': 'form',
					'views': [(False, 'tree'),(False, 'graph')],
				}

			else:

				import io
				from xlsxwriter.workbook import Workbook
				output = io.BytesIO()
				########### PRIMERA HOJA DE LA DATA EN TABLA
				#workbook = Workbook(output, {'in_memory': True})
				direccion = self.env['main.parameter'].search([])[0].dir_create_file
				workbook = Workbook( direccion + 'tempo_cuentacorrientecolumnaagrupada.xlsx')
				worksheet = workbook.add_worksheet("Analisis Vencimiento")
				bold = workbook.add_format({'bold': True})
				normal = workbook.add_format()
				boldbord = workbook.add_format({'bold': True})
				boldbord.set_border(style=2)
				boldbord.set_align('center')
				boldbord.set_align('vcenter')
				boldbord.set_text_wrap()
				boldbord.set_font_size(9)
				boldbord.set_bg_color('#DCE6F1')


				title = workbook.add_format({'bold': True})
				title.set_align('center')
				title.set_align('vcenter')
				title.set_text_wrap()
				title.set_font_size(18)
				numbertres = workbook.add_format({'num_format':'0.000'})
				numberdos = workbook.add_format({'num_format':'0.00'})
				bord = workbook.add_format()
				bord.set_border(style=1)
				numberdos.set_border(style=1)
				numbertres.set_border(style=1)			
				x= 5				
				tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
				tam_letra = 1.2
				import sys
				reload(sys)
				sys.setdefaultencoding('iso-8859-1')


				worksheet.merge_range(0,0,0,15,u"Análisis de Vencimiento",title)

				worksheet.write(1,0, "Fecha:", bold)
				
				worksheet.write(1,1, self.date, normal)
								
				#worksheet.write(1,1, total.date.strftime('%Y-%m-%d %H:%M'),bord)
								
				worksheet.write(4,0, "Empresa",boldbord)
				worksheet.write(4,1, "Vencidas",boldbord)

				worksheet.write(4,2, "De 0 a 15 ",boldbord)
				worksheet.write(4,3, "De 16 a 30",boldbord)
				worksheet.write(4,4, u"De 31 a 45",boldbord)

				worksheet.write(4,5, u"De 46 a 60",boldbord)
				worksheet.write(4,6, "De 61 a 90",boldbord)

				worksheet.write(4,7, "De 91 a 180",boldbord)
				worksheet.write(4,8, u"Mas de 180",boldbord)
				worksheet.write(4,9, u"Total General",boldbord)

				for line in self.env['account.contable.vencimiento.columna.agrupada'].search([('user_guardado','=',self.env.uid)]):
					worksheet.write(x,0,line.empresa if line.empresa  else '',bord )
					worksheet.write(x,1,line.vencidos ,numberdos)
					worksheet.write(x,2,line.menos16 ,numberdos)
					worksheet.write(x,3,line.de16a30 ,numberdos)
					worksheet.write(x,4,line.de31a45 ,numberdos)
					worksheet.write(x,5,line.de46a60 ,numberdos)
					worksheet.write(x,6,line.de61a90 ,numberdos)
					worksheet.write(x,7,line.de91a180 ,numberdos)
					worksheet.write(x,8,line.mas180 ,numberdos)
					worksheet.write(x,9,line.totalgeneral ,numberdos)

					x = x +1

				tam_col = [16,10,10,10,10,10,10,10,10,10]
				worksheet.set_row(0, 30)

				worksheet.set_column('A:A', tam_col[0])
				worksheet.set_column('B:B', tam_col[1])
				worksheet.set_column('C:C', tam_col[2])
				worksheet.set_column('D:D', tam_col[3])
				worksheet.set_column('E:E', tam_col[4])
				worksheet.set_column('F:F', tam_col[5])
				worksheet.set_column('G:G', tam_col[6])
				worksheet.set_column('H:H', tam_col[7])
				worksheet.set_column('I:I', tam_col[8])
				worksheet.set_column('J:J', tam_col[9])
				workbook.close()
				
				f = open(direccion + 'tempo_cuentacorrientecolumnaagrupada.xlsx', 'rb')
				
				
				sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
				vals = {
					'output_name': 'AnalisisVencimiento.xlsx',
					'output_file': base64.encodestring(''.join(f.readlines())),		
				}

				mod_obj = self.env['ir.model.data']
				act_obj = self.env['ir.actions.act_window']
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
