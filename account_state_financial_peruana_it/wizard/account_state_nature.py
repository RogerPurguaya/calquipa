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




class account_state_nature_peruano_wizard(osv.TransientModel):
	_name='account.state.nature.peruano.wizard'

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
			DROP VIEW IF EXISTS account_state_nature_peruano;
			create or replace view account_state_nature_peruano as(
					select row_number() OVER () AS id,* from ( select *,0 as saldoc from get_estado_nature_peruano(""" + flag+ """ ,periodo_num('""" + self.periodo_ini.name+"""') ,periodo_num('""" +self.periodo_fin.name +"""' )) ) AS T
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
			worksheet = workbook.add_worksheet(u"Estado Naturaleza Peruano")
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
			worksheet.write(2,2, u"ESTADO DE RESULTADO POR NATURALEZA", bold)
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


			### aki newnew
			x=6

			#worksheet.write(x,2, self.fiscalyear_id.name, bold)
			
			x+=1	


			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo),orden,sum(coalesce(monto_usd,0)), min(tc) from account_state_nature_peruano
				where grupo = 'N1'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosN1 =  self.env.cr.fetchall()

			sumgrupo1 = None
			sumgrupo1N = None
			
			for i in listobjetosN1:

				worksheet.write(x,1, i[0], normal)
				worksheet.write(x,2, i[3], numberdos)	
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)		
				x+=1
				

			if len(listobjetosN1)>0:
				
				self.env.cr.execute(""" select sum(saldo),sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano where grupo = 'N1' """)
				totalB1 = self.env.cr.fetchall()[0]
				sumgrupo1 = totalB1[0]
				sumgrupo1N = totalB1[2]
				
			else:
				sumgrupo1 = 0
				sumgrupo1N = 0
				
			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo),orden,sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano
				where grupo = 'N2'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosN2 =  self.env.cr.fetchall()

			sumgrupo2 = None
			sumgrupo2N = None

			for i in listobjetosN2:
				
				worksheet.write(x,1, i[0], normal)
				worksheet.write(x,2, i[3], numberdos)			
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)
				x+=1

			x+=1
				
			if len(listobjetosN2)>0:

				self.env.cr.execute(""" select sum(saldo),sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano where grupo = 'N2' """)
				totalB1 = self.env.cr.fetchall()[0]
				sumgrupo2 = totalB1[0]
				sumgrupo2N = totalB1[2]


				worksheet.write(x,1, "MARGEN COMERCIAL", bold)
				worksheet.write(x,2, sumgrupo1 - sumgrupo2, numberdosbold)	
				worksheet.write(x,4, sumgrupo1N - sumgrupo2N, numberdosbold)			
				x+=1

			else:
				sumgrupo2 = 0
				sumgrupo2N = 0
				

				worksheet.write(x,1, "MARGEN COMERCIAL", bold)
				worksheet.write(x,2, sumgrupo1 , numberdosbold)			
				worksheet.write(x,4, sumgrupo1N , numberdosbold)			
				x+=1
				

			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo),orden,sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano
				where grupo = 'N3'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosN3 =  self.env.cr.fetchall()

			for i in listobjetosN3:

				worksheet.write(x,1, i[0], normal)
				worksheet.write(x,2, i[3], numberdos)			
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)		
				x+=1
								
			totalN3 = 0
			totalN3N = 0
			if len(listobjetosN3)>0:
				self.env.cr.execute(""" select sum(saldo),sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano where grupo = 'N3' """)
				totalB1 = self.env.cr.fetchall()[0]
				totalN3 = totalB1[0]
				totalN3N = totalB1[2]



			x+=1
			worksheet.write(x,1, "TOTAL PRODUCCIÓN", bold)
			worksheet.write(x,2, totalN3 , numberdosbold)			
			worksheet.write(x,4, totalN3N , numberdosbold)			
			x+=1
			

			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo),orden,sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano
				where grupo = 'N4'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosN4 =  self.env.cr.fetchall()

			for i in listobjetosN4:

				worksheet.write(x,1, i[0], normal)
				worksheet.write(x,2, i[3], numberdos)			
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)			
				x+=1
			
			totalN4 = 0
			totalN4N = 0
			if len(listobjetosN4)>0:
				self.env.cr.execute(""" select sum(saldo),sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano where grupo = 'N4' """)
				totalB1 = self.env.cr.fetchall()[0]
				totalN4 = totalB1[0]
				totalN4N = totalB1[2]

			sumgrupo4 = sumgrupo1 + sumgrupo2 + totalN3 + totalN4
			sumgrupo4N = sumgrupo1N + sumgrupo2N + totalN3N + totalN4N


			x+=1
			worksheet.write(x,1, "VALOR AGREGADO", bold)
			worksheet.write(x,2, sumgrupo4  , numberdosbold)			
			worksheet.write(x,4, sumgrupo4N  , numberdosbold)			
			x+=1


			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo),orden,sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano
				where grupo = 'N5'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosN5 =  self.env.cr.fetchall()

			for i in listobjetosN5:
			
				worksheet.write(x,1, i[0], normal)
				worksheet.write(x,2, i[3], numberdos)			
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)			
				x+=1
			

			totalN5 = sumgrupo4 
			totalN5N = sumgrupo4N

			if len(listobjetosN5)>0:
				self.env.cr.execute(""" select sum(saldo),sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano where grupo = 'N5' """)
				totalB1 = self.env.cr.fetchall()[0]
				totalN5 += totalB1[0]
				totalN5N += totalB1[2]

			x+=1
			
			worksheet.write(x,1, "EXCEDENTE (O INSUFICIENCIA) BRUTO DE EXPL.", bold)
			worksheet.write(x,2, totalN5 , numberdosbold)			
			worksheet.write(x,4, totalN5N , numberdosbold)			
			x+=1



			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo),orden,sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano
				where grupo = 'N6'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosN6 =  self.env.cr.fetchall()

			for i in listobjetosN6:
				worksheet.write(x,1, i[0], normal)
				worksheet.write(x,2, i[3], numberdos)			
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)			
				x+=1

			totalN6 = totalN5
			totalN6N = totalN5N
			if len(listobjetosN6)>0:
				self.env.cr.execute(""" select sum(saldo),sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano where grupo = 'N6' """)
				totalB1 = self.env.cr.fetchall()[0]
				totalN6 += totalB1[0]
				totalN6N += totalB1[2]


			x+=1

			worksheet.write(x,1, "RESULTADO ANTES DE PARTC. E IMPUESTOS", bold)
			worksheet.write(x,2, totalN6 , numberdosbold)			
			worksheet.write(x,4, totalN6N , numberdosbold)			
			x+=1


			self.env.cr.execute(""" select name as code,'' as concept,grupo,sum(saldo),sum(saldo),orden,sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano
				where grupo = 'N7'
				group by name,grupo,orden
				order by orden,name   """)
			listobjetosN7 =  self.env.cr.fetchall()

			for i in listobjetosN7:
				worksheet.write(x,1, i[0], normal)
				worksheet.write(x,2, i[3], numberdos)			
				worksheet.write(x,3, i[7], numbertres)
				worksheet.write(x,4, i[6], numberdos)			
				x+=1

			totalN7 = totalN6
			totalN7N = totalN6N
			if len(listobjetosN7)>0:
				self.env.cr.execute(""" select sum(saldo),sum(saldo),sum(coalesce(monto_usd,0)), min(tc)  from account_state_nature_peruano where grupo = 'N7' """)
				totalB1 = self.env.cr.fetchall()[0]
				totalN7 += totalB1[0]
				totalN7N += totalB1[2]



			x+=1
			worksheet.write(x,1, "RESULTADO DEL EJERCICIO", bold)
			worksheet.write(x,2, totalN7 , numberdosbold)			
			worksheet.write(x,4, totalN7N , numberdosbold)			
			x+=1

			worksheet.set_column('B:B',57)
			worksheet.set_column('C:C',24)


			#### FIN

			workbook.close()
			
			f = open(direccion + 'Reporte_state_function.xlsx', 'rb')
			
			vals = {
				'output_name': 'EstadoNatural.xlsx',
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
