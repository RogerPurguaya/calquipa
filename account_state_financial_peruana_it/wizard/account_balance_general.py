# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv



from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import magenta, red , black , blue, gray, Color, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table
from reportlab.lib.units import  cm,mm
from reportlab.lib.utils import simpleSplit
from cgi import escape
import base64


class account_balance_general_peruano_wizard(osv.TransientModel):
	_name='account.balance.general.peruano.wizard'

	periodo_ini = fields.Many2one('account.period','Periodo Inicio', required="1")
	periodo_fin = fields.Many2one('account.period','Periodo Fin', required="1")



	@api.onchange('periodo_ini')
	def _change_periodo_ini(self):
		if self.periodo_ini:
			self.periodo_fin= self.periodo_ini

	@api.multi
	def do_rebuild(self):

		flag = 'false'

		self.env.cr.execute(""" 
			DROP VIEW IF EXISTS account_balance_general_peruana;
			create or replace view account_balance_general_peruana as(
					select row_number() OVER () AS id,* from ( select * from get_balance_general_peruana(""" + flag+ """ ,periodo_num('""" + self.periodo_ini.name+"""') ,periodo_num('""" +self.periodo_fin.name +"""' )) ) AS T
			)
			""")		


		if True:

			import io
			from xlsxwriter.workbook import Workbook

			import sys
			reload(sys)
			sys.setdefaultencoding('iso-8859-1')

			output = io.BytesIO()
			########### PRIMERA HOJA DE LA DATA EN TABLA
			#workbook = Workbook(output, {'in_memory': True})

			direccion = self.env['main.parameter'].search([])[0].dir_create_file
			if not direccion:
				raise osv.except_osv('Alerta!', u"No fue configurado el directorio para los archivos en Configuracion.")

			workbook = Workbook(direccion +'Reporte_Balance_general.xlsx')
			worksheet = workbook.add_worksheet(u"Balance General")
			bold = workbook.add_format({'bold': True})
			normal = workbook.add_format()
			boldbord = workbook.add_format({'bold': True})
			boldbord.set_border(style=2)
			boldbord.set_align('center')
			boldbord.set_align('vcenter')
			boldbord.set_text_wrap()
			boldbord.set_font_size(9)
			boldbord.set_bg_color('#DCE6F1')
			numbertres = workbook.add_format({'num_format':'0.000'})
			numberdos = workbook.add_format({'num_format':'#,##0.00'})
			bord = workbook.add_format()
			bord.set_border(style=1)


			numbertresbold = workbook.add_format({'num_format':'0.000','bold':True})
			numberdosbold = workbook.add_format({'num_format':'#,##0.00','bold':True})
			numberdosbold.set_border(style=1)
			numbertresbold.set_border(style=1)	

			numberdoscon = workbook.add_format({'num_format':'#,##0.00'})

			boldtotal = workbook.add_format({'bold': True})
			boldtotal.set_align('right')
			boldtotal.set_align('vright')

			merge_format = workbook.add_format({
												'bold': 1,
												'border': 1,
												'align': 'center',
												'valign': 'vcenter',
												})	
			merge_format.set_bg_color('#DCE6F1')
			merge_format.set_text_wrap()
			merge_format.set_font_size(9)


			worksheet.write(1,1, self.env["res.company"].search([])[0].name.upper(), bold)
			worksheet.write(2,1, u"ESTADO DE SITUACIÓN FINANCIERA", bold)
			worksheet.write(3,1, u"AL "+ str(self.periodo_fin.date_stop), bold)
			worksheet.write(4,1, u"(Expresado en Nuevos Soles)", bold)
		

			colum = {
				1: "Enero",
				2: "Febrero",
				3: "Marzo",
				4: "Abril",
				5: "Mayo",
				6: "Junio",
				7: "Julio",
				8: "Agosto",
				9: "Septiembre",
				10: "Octubre",
				11: "Noviembre",
				12: "Diciembre",
			}


			###  B1
			self.env.cr.execute(""" select name as code,'' as concept,sum(saldo),sum(coalesce(monto_usd,0)), min(tc) from account_balance_general_peruana
				where grupo = 'B1'
				group by name ,grupo,orden
				order by orden,name """)
			listobjetosB1 =  self.env.cr.fetchall()

			
			worksheet.write(6,1, 'ACTIVO' , bold)
			#worksheet.write(6,2, self.fiscalyear_id.name , bold)

			worksheet.write(7,1, 'ACTIVO CORRIENTE' , bold)

			x=9
			for i in listobjetosB1:

				worksheet.write(x,1, i[0], normal)
				worksheet.write(x,2, i[2], numberdos)
				worksheet.write(x,3, i[4], numbertres)
				worksheet.write(x,4, i[3], numberdos)
				x += 1

			x += 1

			if len(listobjetosB1)>0:
				worksheet.write(x,1, 'TOTAL ACTIVO CORRIENTE' , bold)

				self.env.cr.execute(""" select sum(saldo),sum(coalesce(monto_usd,0)), min(tc) from account_balance_general_peruana where grupo = 'B1' """)
				totalB1 = self.env.cr.fetchall()[0]
				
				worksheet.write(x,2, totalB1[0], numberdosbold)
				worksheet.write(x,4, totalB1[1], numberdosbold)
				x+=1

			else:
				worksheet.write(x,1, 'TOTAL ACTIVO CORRIENTE' , bold)

				worksheet.write(x,2, 0, numberdosbold)
				worksheet.write(x,4, 0, numberdosbold)
				x+=1


			# segunda parte B2
			x += 1

			self.env.cr.execute(""" select name as code,'' as concept, sum(saldo) ,sum(coalesce(monto_usd,0)), min(tc)  from account_balance_general_peruana
				where grupo = 'B2'
				group by name,grupo,orden
				order by orden,name """)
			listobjetosB1 =  self.env.cr.fetchall()

			worksheet.write(x,1, 'ACTIVO NO CORRIENTE' , bold)

			for i in listobjetosB1:
				worksheet.write(x,1, i[0], normal)
				worksheet.write(x,2, i[2], numberdos)
				worksheet.write(x,3, i[4], numbertres)
				worksheet.write(x,4, i[3], numberdos)
				x += 1

			data_inicial2 = 0

			if len(listobjetosB1)>0:
				worksheet.write(x,1, 'TOTAL ACTIVO NO CORRIENTE' , bold)

				self.env.cr.execute(""" select sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_balance_general_peruana where grupo = 'B2' """)
				totalB1 = self.env.cr.fetchall()[0]

				worksheet.write(x,2, totalB1[0], numberdosbold)	
				worksheet.write(x,4, totalB1[1], numberdosbold)
				data_inicial2 = totalB1[0]
				x+=1

			else:

				worksheet.write(x,1, 'TOTAL ACTIVO NO CORRIENTE' , bold)
				
				worksheet.write(x,2, 0, numberdosbold)		
				worksheet.write(x,4, 0, numberdosbold)	
				x+=1

			pos_inicial2 = x+1

			###  B3 AQUI ES EL LADO DERECHO

			x=6
			x += 1


			self.env.cr.execute(""" select name as code,'' as concept, sum(saldo) ,sum(coalesce(monto_usd,0)), min(tc)  from account_balance_general_peruana
	where grupo = 'B3'
	group by name,grupo,orden
	order by orden,name """)
			listobjetosB1 =  self.env.cr.fetchall()

			worksheet.write(x,5, 'PASIVO Y PATRIMONIO' , bold)
			#worksheet.write(x,6, self.fiscalyear_id.name + '(' + self.periodo_ini.code[:2] +' - ' + self.periodo_fin.code[:2] + ')' , bold)
			
			x+=2


			worksheet.write(x,5, 'PASIVO CORRIENTE' , bold)
			x+=1

			for i in listobjetosB1:

				worksheet.write(x,5, i[0], normal)
				worksheet.write(x,6, i[2], numberdos)
				worksheet.write(x,7, i[4], numbertres)
				worksheet.write(x,8, i[3], numberdos)
				x+=1


			if len(listobjetosB1)>0:
				worksheet.write(x,5, 'TOTAL PASIVO CORRIENTE' , bold)
								
				self.env.cr.execute(""" select  sum(saldo) ,sum(coalesce(monto_usd,0)), min(tc)  from account_balance_general_peruana where grupo = 'B3' """)
				totalB1 = self.env.cr.fetchall()[0]
				worksheet.write(x,6, totalB1[0], numberdosbold)
				worksheet.write(x,8, totalB1[1], numberdosbold)
				x+=1

			else:

				worksheet.write(x,5, 'TOTAL PASIVO CORRIENTE' , bold)
								
				worksheet.write(x,6, 0, numberdosbold)
				worksheet.write(x,8 ,0, numberdosbold)
				x+=1

			x+= 1

			
			###  B4
			self.env.cr.execute(""" select name as code,'' as concept, sum(saldo) ,sum(coalesce(monto_usd,0)), min(tc)  from account_balance_general_peruana
	where grupo = 'B4'
	group by name,grupo,orden
	order by orden,name """)
			listobjetosB1 =  self.env.cr.fetchall()
			
			worksheet.write(x,5, 'PASIVO NO CORRIENTE' , bold)
			x+=1

			for i in listobjetosB1:
				worksheet.write(x,5, i[0], normal)
				worksheet.write(x,6, i[2], numberdos)
				worksheet.write(x,7, i[4], numbertres)
				worksheet.write(x,8, i[3], numberdos)
				x+=1

		
			if len(listobjetosB1)>0:
				worksheet.write(x,5, 'TOTAL PASIVO NO CORRIENTE' , bold)
			
				self.env.cr.execute(""" select sum(saldo) ,sum(coalesce(monto_usd,0)), min(tc)  from account_balance_general_peruana where grupo = 'B4' """)
				totalB1 = self.env.cr.fetchall()[0]

				worksheet.write(x,6, totalB1[0], numberdosbold)
				worksheet.write(x,8, totalB1[1], numberdosbold)
				x+=1

			else:
				
				worksheet.write(x,5, 'TOTAL PASIVO NO CORRIENTE' , bold)
				worksheet.write(x,6, 0, numberdosbold)
				worksheet.write(x,8, 0, numberdosbold)
				x+=1


			x+= 1




			###  B5
			self.env.cr.execute(""" select name as code,'' as concept,sum(saldo) ,sum(coalesce(monto_usd,0)), min(tc)  from account_balance_general_peruana
	where grupo = 'B5'
	group by name,grupo,orden
	order by orden,name """)
			listobjetosB1 =  self.env.cr.fetchall()

			worksheet.write(x,5, 'PATRIMONIO' , bold)
			
			for i in listobjetosB1:
				worksheet.write(x,5, i[0] , bold)
				worksheet.write(x,6, i[2], numberdos)
				worksheet.write(x,7, i[4], numbertres)
				worksheet.write(x,8, i[3], numberdos)
				x+=1


			if len(listobjetosB1)>0:
				worksheet.write(x,5, 'TOTAL PATRIMONIO' , bold)
				
				self.env.cr.execute(""" select  sum(saldo) ,sum(coalesce(monto_usd,0)), min(tc)  from account_balance_general_peruana where grupo = 'B5' """)
				totalB1 = self.env.cr.fetchall()[0]
				
				worksheet.write(x,6, totalB1[0], numberdosbold)
				worksheet.write(x,8, totalB1[1], numberdosbold)
				x+=1

			else:

				worksheet.write(x,5, 'TOTAL PATRIMONIO' , bold)
								
				worksheet.write(x,6, 0, numberdosbold)
				worksheet.write(x,8, 0, numberdosbold)
				x+=1

			x+= 1


			worksheet.write(x,5, 'RESULTADO DEL PERIODO' , bold)

			self.env.cr.execute(""" select coalesce(sum(saldo),0) ,sum(coalesce(monto_usd,0)), min(tc)  from account_balance_general_peruana
	where grupo = 'B1' or grupo = 'B2' """)
			tmp_consultaB1B2 = self.env.cr.fetchall()
			totalA12 = tmp_consultaB1B2[0]
			self.env.cr.execute(""" select coalesce(sum(saldo),0) ,sum(coalesce(monto_usd,0)), min(tc)  from account_balance_general_peruana
	where grupo = 'B3' or grupo = 'B4' or grupo = 'B5' """)
			tmp_consultaB345 = self.env.cr.fetchall()
			totalA345 = tmp_consultaB345[0]

			worksheet.write(x,6, totalA12[0]- totalA345[0], numberdos)
			worksheet.write(x,8, totalA12[1]- totalA345[1], numberdos)
		
			x+=2
			#### AQUI VAN LOS FINALES FINALES
			if x > pos_inicial2:
				pass
			else:
				x = pos_inicial2

			worksheet.write(x,5, 'TOTAL PASIVO Y PATRIMONIO' , bold)
			
			worksheet.write(x,1, 'TOTAL ACTIVO' , bold)


			self.env.cr.execute(""" select coalesce(sum(saldo),0) ,sum(coalesce(monto_usd,0)), min(tc)  from account_balance_general_peruana
	where grupo = 'B1' or grupo = 'B2' """)
			tmp_totalA12 = self.env.cr.fetchall()
			
			totalA12 = tmp_totalA12[0]

			worksheet.write(x,2, totalA12[0] , numberdosbold)
			worksheet.write(x,4, totalA12[1] , numberdosbold)


			worksheet.write(x,6, totalA12[0] , numberdosbold)
			worksheet.write(x,8, totalA12[1] , numberdosbold)

			worksheet.set_column('B:B',57)
			worksheet.set_column('C:C',24)
			worksheet.set_column('F:F',57)
			worksheet.set_column('G:G',24)

			workbook.close()
			
			f = open(direccion + 'Reporte_Balance_general.xlsx', 'rb')
			
			vals = {
				'output_name': 'BalanceGeneral.xlsx',
				'output_file': base64.encodestring(''.join(f.readlines())),		
			}

			sfs_id = self.env['export.file.save'].create(vals)
			return {
				"type": "ir.actions.act_window",
				"res_model": "export.file.save",
				"views": [[False, "form"]],
				"res_id": sfs_id.id,
				"target": "new",
			}


