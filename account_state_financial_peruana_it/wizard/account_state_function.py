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

class account_state_function_peruano_wizard(osv.TransientModel):
	_name='account.state.function.peruano.wizard'

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
			DROP VIEW IF EXISTS account_state_function_peruana;
			create or replace view account_state_function_peruana as(
					select row_number() OVER () AS id,* from ( select *,0 as saldoc from get_estado_funcion_peruano(""" + flag+ """ ,periodo_num('""" + self.periodo_ini.name+"""') ,periodo_num('""" +self.periodo_fin.name +"""' )) ) AS T
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

			workbook = Workbook(direccion +'Reporte_state_function.xlsx')
			worksheet = workbook.add_worksheet(u"Estado Función")
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

			numbertresbold = workbook.add_format({'num_format':'0.000','bold': True})
			numberdosbold = workbook.add_format({'num_format':'#,##0.00','bold': True})
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

			worksheet.write(1,2, self.env["res.company"].search([])[0].name.upper(), bold)
			worksheet.write(2,2, u"ESTADO DE RESULTADO POR FUNCION", bold)
			worksheet.write(3,2, u"AL "+ str(self.periodo_fin.date_stop), bold)
			worksheet.write(4,2, u"(Expresado en Nuevos Soles)", bold)
		

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


			#### nuevo ini
			x=6

			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo) ,orden,sum(coalesce(monto_usd,0)), min(tc) from account_state_function_peruana
				where grupo = 'F1'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosF1 =  self.env.cr.fetchall()

			worksheet.write(x,1, "INGRESOS OPERACIONALES", bold)

			#worksheet.write(x,2, self.fiscalyear_id.name, bold)

			x+=1					

			sumgrupo1 = None
			sumgrupo1N = None
			for i in listobjetosF1:

				worksheet.write(x,1, i[0], normal)
				worksheet.write(x,2, i[3], numberdos)
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)
				x += 1

			x+=1

			if len(listobjetosF1)>0:
				worksheet.write(x,1, "TOTAL INGRESOS BRUTOS", bold)

				self.env.cr.execute(""" select sum(saldo), sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_function_peruana where grupo = 'F1' """)
				totalB1 = self.env.cr.fetchall()[0]
				sumgrupo1 = totalB1[0]
				sumgrupo1N = totalB1[2]

				worksheet.write(x,2, totalB1[0], numberdosbold)
				worksheet.write(x,4, totalB1[2], numberdosbold)
				x += 1

			else:
				sumgrupo1 = 0
				sumgrupo1N = 0
				
				worksheet.write(x,1, "TOTAL INGRESOS BRUTOS", bold)

				worksheet.write(x,2, 0, numberdosbold)
				worksheet.write(x,4, 0, numberdosbold)
				x += 1

			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo),orden,sum(coalesce(monto_usd,0)), min(tc)  from account_state_function_peruana
				where grupo = 'F2'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosF2 =  self.env.cr.fetchall()

			x+=1

			sumgrupo2 = None
			sumgrupo2N = None
			for i in listobjetosF2:

				worksheet.write(x,1, i[0], bold)

				worksheet.write(x,2, i[3], numberdos)
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)
				x += 1

			x+=1

			if len(listobjetosF2)>0:

				self.env.cr.execute(""" select sum(saldo),sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_function_peruana where grupo = 'F2' """)
				totalB1 = self.env.cr.fetchall()[0]
				sumgrupo2 = totalB1[0]
				sumgrupo2N = totalB1[2]


				worksheet.write(x,1, "TOTAL COSTOS OPERACIONALES", bold)

				worksheet.write(x,2, totalB1[0], numberdosbold)
				worksheet.write(x,4, totalB1[2], numberdosbold)
				x += 1

			else:
				sumgrupo2 = 0
				sumgrupo2N = 0


				worksheet.write(x,1, "TOTAL COSTOS OPERACIONALES", bold)

				worksheet.write(x,2, 0, numberdosbold)
				worksheet.write(x,4, 0, numberdosbold)
				x += 1

			x+=1

			worksheet.write(x,1, "UTILIDAD BRUTA", bold)

			worksheet.write(x,2, sumgrupo1 + sumgrupo2, numberdosbold)
			worksheet.write(x,4, sumgrupo1N + sumgrupo2N, numberdosbold)
			x += 1

			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo),orden,sum(coalesce(monto_usd,0)), min(tc)  from account_state_function_peruana
				where grupo = 'F3'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosF3 =  self.env.cr.fetchall()

			for i in listobjetosF3:

				worksheet.write(x,1, i[0], bold)

				worksheet.write(x,2, i[3], numberdos)
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)
				x += 1

			totalF3 = sumgrupo1 + sumgrupo2
			totalF3N = sumgrupo1N + sumgrupo2N
			if len(listobjetosF3)>0:
				self.env.cr.execute(""" select sum(saldo),sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_function_peruana where grupo = 'F3' """)
				totalB1 = self.env.cr.fetchall()[0]
				totalF3 += totalB1[0]
				totalF3N += totalB1[2]

			x+=1


			worksheet.write(x,1, "UTILIDAD OPERATIVA", bold)

			worksheet.write(x,2, totalF3, numberdosbold)
			worksheet.write(x,4, totalF3N, numberdosbold)
			x += 1


			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo),orden,sum(coalesce(monto_usd,0)), min(tc)  from account_state_function_peruana
				where grupo = 'F4'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosF4 =  self.env.cr.fetchall()

			for i in listobjetosF4:

				worksheet.write(x,1, i[0], bold)

				worksheet.write(x,2, i[3], numberdos)
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)
				x += 1


			totalF4 = totalF3
			totalF4N = totalF3N
			if len(listobjetosF4)>0:
				self.env.cr.execute(""" select sum(saldo),sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_function_peruana where grupo = 'F4' """)
				totalB1 = self.env.cr.fetchall()[0]
				totalF4 += totalB1[0]
				totalF4N += totalB1[2]

			x+=1
			worksheet.write(x,1, "RESULTADO ANTES DE PARTICIPACIONES E IMPUESTOS", bold)

			worksheet.write(x,2, totalF4, numberdosbold)
			worksheet.write(x,4, totalF4N, numberdosbold)
			x += 1


			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo),orden,sum(coalesce(monto_usd,0)), min(tc)  from account_state_function_peruana
				where grupo = 'F5'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosF5 =  self.env.cr.fetchall()

			for i in listobjetosF5:
				worksheet.write(x,1, i[0], bold)

				worksheet.write(x,2, i[3], numberdos)
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)
				x += 1


			totalF5 = totalF4
			totalF5N = totalF4N
			if len(listobjetosF5)>0:
				self.env.cr.execute(""" select sum(saldo),sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_function_peruana where grupo = 'F5' """)
				totalB1 = self.env.cr.fetchall()[0]
				totalF5 += totalB1[0]
				totalF5N += totalB1[2]



			x+=1
			worksheet.write(x,1, "UTILIDAD(PERDIDA) NETA ACT DISCONTINUAS", bold)

			worksheet.write(x,2, totalF5, numberdosbold)
			worksheet.write(x,4, totalF5N, numberdosbold)
			x += 1


			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo),orden,sum(coalesce(monto_usd,0)), min(tc)  from account_state_function_peruana
				where grupo = 'F6'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosF6 =  self.env.cr.fetchall()

			for i in listobjetosF6:
				worksheet.write(x,1, i[0], bold)

				worksheet.write(x,2, i[3], numberdos)
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)
				x += 1

			totalF6 = totalF5
			totalF6N = totalF5N
			if len(listobjetosF6)>0:
				self.env.cr.execute(""" select sum(saldo),sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_function_peruana where grupo = 'F6' """)
				totalB1 = self.env.cr.fetchall()[0]
				totalF6 += totalB1[0]
				totalF6N += totalB1[2]



			x+=1
			

			self.env.cr.execute(""" 
			DROP VIEW IF EXISTS account_balance_general_peruana;
			create or replace view account_balance_general_peruana as(
					select row_number() OVER () AS id,* from ( select * from get_balance_general_peruana(""" + flag+ """ ,periodo_num('""" + self.periodo_ini.name+"""') ,periodo_num('""" +self.periodo_fin.name +"""' )) ) AS T
			)
			""")	


			self.env.cr.execute(""" select coalesce(sum(saldo),0) ,sum(coalesce(monto_usd,0)) from account_balance_general_peruana
	where grupo = 'B1' or grupo = 'B2' """)
			tmp_consultaB1B2 = self.env.cr.fetchall()
			totalA12 = tmp_consultaB1B2[0]
			self.env.cr.execute(""" select coalesce(sum(saldo),0) ,sum(coalesce(monto_usd,0)) from account_balance_general_peruana
	where grupo = 'B3' or grupo = 'B4' or grupo = 'B5' """)
			tmp_consultaB345 = self.env.cr.fetchall()
			totalA345 = tmp_consultaB345[0]

			worksheet.write(x,1, "RESULTADO CONVERSION", bold)

			worksheet.write(x,2, totalF6 - (totalA12[0]- totalA345[0]) , numberdosbold)
			worksheet.write(x,4, totalF6N - (totalA12[1]- totalA345[1]) , numberdosbold)
			x += 1

			x += 1
			worksheet.write(x,1, "UTILIDAD(PERDIDA) NETA DEL EJERCICIO", bold)

			worksheet.write(x,2, totalA12[0]- totalA345[0], numberdosbold)
			worksheet.write(x,4, totalA12[1]- totalA345[1], numberdosbold)
			x += 1


			worksheet.set_column('B:B',57)
			worksheet.set_column('C:C',24)
			#### FIN

			workbook.close()
			
			f = open(direccion + 'Reporte_state_function.xlsx', 'rb')
			
			vals = {
				'output_name': 'EstadoFuncion.xlsx',
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


