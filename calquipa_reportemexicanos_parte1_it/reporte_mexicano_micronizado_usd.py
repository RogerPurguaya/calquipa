# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv
from functools import reduce
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import magenta, red , black, white, blue, gray, Color, HexColor, PCMYKColor, PCMYKColorSep
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, A4, legal
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table
from reportlab.lib.units import  cm,mm
from reportlab.lib.utils import simpleSplit
from cgi import escape
import decimal
import calendar

def dig_5(n):
	return ("%5d" % n).replace(' ','0')

class rm_report_micronizado_line(models.Model):
	_inherit = 'rm.report.micronizado.line'

	@api.one
	def get_acumulado_usd(self):
		periodos = self.env['account.period'].search([('fiscalyear_id','=',self.rm_report_micronizado_id.fiscal.id)])
		ex = self.env['tipo.cambio.mexicano'].search([('periodo_id','in',periodos.ids)])
		exchange = {
			1:ex.filtered(lambda x:x.periodo_id.name[:3] == '01/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '01/'))==1 else 1 ,
			2:ex.filtered(lambda x:x.periodo_id.name[:3] == '02/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '02/'))==1 else 1 ,
			3:ex.filtered(lambda x:x.periodo_id.name[:3] == '03/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '03/'))==1 else 1 ,
			4:ex.filtered(lambda x:x.periodo_id.name[:3] == '04/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '04/'))==1 else 1 ,
			5:ex.filtered(lambda x:x.periodo_id.name[:3] == '05/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '05/'))==1 else 1 ,
			6:ex.filtered(lambda x:x.periodo_id.name[:3] == '06/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '06/'))==1 else 1 ,
			7:ex.filtered(lambda x:x.periodo_id.name[:3] == '07/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '07/'))==1 else 1 ,
			8:ex.filtered(lambda x:x.periodo_id.name[:3] == '08/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '08/'))==1 else 1 ,
			9:ex.filtered(lambda x:x.periodo_id.name[:3] == '09/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '09/'))==1 else 1 ,
			10:ex.filtered(lambda x:x.periodo_id.name[:3] == '10/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '10/'))==1 else 1 ,
			11:ex.filtered(lambda x:x.periodo_id.name[:3] == '11/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '11/'))==1 else 1 ,
			12:ex.filtered(lambda x:x.periodo_id.name[:3] == '12/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '12/'))==1 else 1 ,
		}

		enero   = self.enero/exchange[1]
		febrero = self.febrero/exchange[2]
		marzo   = self.marzo/exchange[3]
		abril   = self.abril/exchange[4]
		mayo    = self.mayo/exchange[5]
		junio   = self.junio/exchange[6]
		julio   = self.julio/exchange[7]
		agosto  = self.agosto/exchange[8]
		septiembre = self.septiembre/exchange[9]
		octubre   = self.octubre/exchange[10]
		noviembre = self.noviembre/exchange[11]
		diciembre = self.diciembre/exchange[12]

		self.acumulado_usd = enero + febrero + marzo + abril + mayo + junio + julio + agosto + septiembre + octubre + noviembre + diciembre
	acumulado_usd = fields.Float('Acumulado USD', readonly=True, default=0, compute="get_acumulado_usd")

	@api.one
	def get_acumulado_pciento_usd(self):
		if self.acumulado_usd != 0:
			self.acumulado_pciento_usd = self.acumulado_usd / self.rm_report_micronizado_id.total_general_usd
		else:
			self.acumulado_pciento_usd = 0
	acumulado_pciento_usd = fields.Float('%  ACUM', readonly=True, compute="get_acumulado_pciento_usd")

	@api.one
	def get_promedio_usd(self):
		if self.acumulado_usd != 0:
			self.promedio_usd = self.acumulado_usd / 1
		else:
			self.promedio_usd = 0
	promedio_usd = fields.Float('Promedio', readonly=True, compute="get_promedio_usd")

	@api.one
	def get_promedio_pciento_usd(self):
		if self.acumulado_usd != 0:
			self.promedio_pciento_usd = self.promedio_usd / self.rm_report_micronizado_id.total_promedio_general_usd
		else:
			self.promedio_pciento_usd = 0
	promedio_pciento_usd = fields.Float('%  PROM', readonly=True, compute="get_promedio_pciento_usd")

class rm_report_micronizado(models.Model):
	_inherit= 'rm.report.micronizado'

	@api.one
	def get_total_general_usd(self):
		if len(self.conf_line_ids) > 0:
			self.total_general_usd = reduce(lambda x,y:x+y,self.conf_line_ids.mapped('acumulado_usd'))
		else:
			self.total_general_usd = 0
	total_general_usd = fields.Float('Total general USD', compute="get_total_general_usd")


	@api.one
	def get_total_promedio_general_usd(self):
		if len(self.conf_line_ids) > 0:
			self.total_promedio_general_usd = reduce(lambda x,y:x+y,self.conf_line_ids.mapped('promedio_usd'))
		else:
			self.total_promedio_general_usd = 0
	total_promedio_general_usd = fields.Float(compute="get_total_promedio_general_usd")


	""" ----------------------------- REPORTE EXCEL ----------------------------- """

	@api.multi
	def export_excel_usd(self):
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

		workbook = Workbook(direccion +'Reporte_Micronizado_USD.xlsx')
		worksheet = workbook.add_worksheet(u"Micronizado")
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
		numberdos.set_border(style=1)
		numbertres.set_border(style=1)	

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

		m = str(self.period_actual.code).split('/')
		m = int(m[0])
		doce = 12

		worksheet.insert_image('C2', 'calidra.jpg')
		worksheet.write(1,8, u'ANEXO DE OPERACIÓN {0}'.format(self.fiscal.name), bold)
		worksheet.write(2,8, 'Sitio:', bold)
		worksheet.write(2,12, self.sitio if self.sitio else '', normal)
		worksheet.write(3,8, 'Centro de Costo:', bold)
		worksheet.write(3,12, self.centro_de_costo if self.centro_de_costo else '', normal)
		worksheet.write(4,8, u'Propósito:', bold)
		worksheet.write(4,12, self.proposito if self.proposito else '', normal)
		worksheet.write(5,8, u'Fecha de Emisión del Reporte:', bold)
		worksheet.write(5,12, self.fecha_emision_reporte if self.fecha_emision_reporte else '', normal)
		worksheet.write(6,8, 'Usuario:', bold)
		worksheet.write(6,12, self.usuario.name if self.usuario.name else '', normal)
		worksheet.write(7,8, 'Moneda:', bold)
		worksheet.write(7,12,u'Dólares', normal)

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

		periodos = self.env['account.period'].search([('fiscalyear_id','=',self.fiscal.id)])
		ex = self.env['tipo.cambio.mexicano'].search([('periodo_id','in',periodos.ids)])

		exchange = {
			1:ex.filtered(lambda x:x.periodo_id.name[:3] == '01/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '01/'))==1 else 1 ,
			2:ex.filtered(lambda x:x.periodo_id.name[:3] == '02/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '02/'))==1 else 1 ,
			3:ex.filtered(lambda x:x.periodo_id.name[:3] == '03/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '03/'))==1 else 1 ,
			4:ex.filtered(lambda x:x.periodo_id.name[:3] == '04/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '04/'))==1 else 1 ,
			5:ex.filtered(lambda x:x.periodo_id.name[:3] == '05/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '05/'))==1 else 1 ,
			6:ex.filtered(lambda x:x.periodo_id.name[:3] == '06/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '06/'))==1 else 1 ,
			7:ex.filtered(lambda x:x.periodo_id.name[:3] == '07/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '07/'))==1 else 1 ,
			8:ex.filtered(lambda x:x.periodo_id.name[:3] == '08/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '08/'))==1 else 1 ,
			9:ex.filtered(lambda x:x.periodo_id.name[:3] == '09/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '09/'))==1 else 1 ,
			10:ex.filtered(lambda x:x.periodo_id.name[:3] == '10/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '10/'))==1 else 1 ,
			11:ex.filtered(lambda x:x.periodo_id.name[:3] == '11/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '11/'))==1 else 1 ,
			12:ex.filtered(lambda x:x.periodo_id.name[:3] == '12/')[0].t_cambio_venta if len(ex.filtered(lambda x:x.periodo_id.name[:3] == '12/'))==1 else 1 ,
		}

		worksheet.write(14,0, u'TIPO COSTO', boldbord)
		col = 1
		mon = 0
		while mon+1 <= doce:
			worksheet.write(13,col, exchange[mon+1] if exchange[mon+1] > 1 else '', numberdoscon)
			worksheet.write(14,col, u'{0}'.format(colum[mon+1]), boldbord)
			col += 1
			mon += 1
		worksheet.write(14,col, u'Acumulado', boldbord)
		col+=1
		worksheet.write(14,col, u'%  ACUM', boldbord)
		col+=1
		worksheet.write(14,col, u'Promedio', boldbord)
		col+=1
		worksheet.write(14,col, u'%  PROM', boldbord)
		col+=1
		
		elements = self.env['rm.report.micronizado.line'].search([('rm_report_micronizado_id','=',self.id)]).sorted(key=lambda r: dig_5(r.tipo.order)+dig_5(r.grupo.order))
		flag = True
		n_grupo = None
		n_tipo = None
		ultimo_elem = None

		sub_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tot_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tot_tot_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

		x= 15
		for i in elements:
			if n_tipo == None:
				n_tipo = i.tipo
				worksheet.write(x,0, u'{0}'.format(i.tipo.titulo), bold)
				x += 1
			if n_grupo == None:
				n_grupo = i.grupo
				worksheet.write(x,0, u'{0}'.format(i.grupo.titulo), bold)
				x += 1
			if n_tipo != i.tipo:
				worksheet.write(x,0, u'SUB TOTAL', boldtotal)
				col = 1
				mon = 0
				while mon+1 <= doce:
					worksheet.write(x,col, ((sub_tot[mon])), numberdos)
					col += 1
					mon += 1
				worksheet.write(x,col, ((sub_tot[-4])), numberdos)
				col += 1
				worksheet.write(x,col, ((sub_tot[-3])), numberdos)
				col += 1
				worksheet.write(x,col, ((sub_tot[-2])), numberdos)
				col += 1
				worksheet.write(x,col, ((sub_tot[-1])), numberdos)

				tot_tot[0] += sub_tot[0]
				tot_tot[1] += sub_tot[1]
				tot_tot[2] += sub_tot[2]
				tot_tot[3] += sub_tot[3]
				tot_tot[4] += sub_tot[4]
				tot_tot[5] += sub_tot[5]
				tot_tot[6] += sub_tot[6]
				tot_tot[7] += sub_tot[7]
				tot_tot[8] += sub_tot[8]
				tot_tot[9] += sub_tot[9]
				tot_tot[10] += sub_tot[10]
				tot_tot[11] += sub_tot[11]
				tot_tot[12] += sub_tot[12]
				tot_tot[13] += sub_tot[13]
				tot_tot[14] += sub_tot[14]
				tot_tot[15] += sub_tot[15]
				tot_tot_tot[0] += tot_tot[0]
				tot_tot_tot[1] += tot_tot[1]
				tot_tot_tot[2] += tot_tot[2]
				tot_tot_tot[3] += tot_tot[3]
				tot_tot_tot[4] += tot_tot[4]
				tot_tot_tot[5] += tot_tot[5]
				tot_tot_tot[6] += tot_tot[6]
				tot_tot_tot[7] += tot_tot[7]
				tot_tot_tot[8] += tot_tot[8]
				tot_tot_tot[9] += tot_tot[9]
				tot_tot_tot[10] += tot_tot[10]
				tot_tot_tot[11] += tot_tot[11]
				tot_tot_tot[12] += tot_tot[12]
				tot_tot_tot[13] += tot_tot[13]
				tot_tot_tot[14] += tot_tot[14]
				tot_tot_tot[15] += tot_tot[15]

				x += 1
				worksheet.write(x,0, u"TOTAL " + n_tipo.titulo.upper(), boldtotal)
				col = 1
				mon = 0
				while mon+1 <= doce:
					worksheet.write(x,col, ((tot_tot[mon])), numberdos)
					col += 1
					mon += 1
				worksheet.write(x,col, ((tot_tot[-4])), numberdos)
				col += 1
				worksheet.write(x,col, ((tot_tot[-3])), numberdos)
				col += 1
				worksheet.write(x,col, ((tot_tot[-2])), numberdos)
				col += 1
				worksheet.write(x,col, ((tot_tot[-1])), numberdos)
				col += 1

				sub_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
				tot_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

				x += 1
				worksheet.write(x,0, u'{0}'.format(i.tipo.titulo), bold)
				x += 1
				worksheet.write(x,0, u'{0}'.format(i.grupo.titulo), bold)
				x += 1
				worksheet.write(x,0, u'{0}'.format(i.concepto), normal)
				mon_m = {
					0: i.enero / exchange[1],
					1: i.febrero / exchange[2],
					2: i.marzo / exchange[3],
					3: i.abril / exchange[4],
					4: i.mayo / exchange[5],
					5: i.junio / exchange[6],
					6: i.julio / exchange[7],
					7: i.agosto / exchange[8],
					8: i.septiembre / exchange[9],
					9: i.octubre / exchange[10],
					10: i.noviembre / exchange[11],
					11: i.diciembre / exchange[12],
				}
				col = 1
				mon = 0
				while mon+1 <= doce:
					worksheet.write(x,col, ((mon_m[mon])), numberdoscon)
					col += 1
					mon += 1
				worksheet.write(x,col, ((i.acumulado_usd)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.acumulado_pciento_usd)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.promedio_usd)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.promedio_pciento_usd)), numberdoscon)

				sub_tot[0] += i.enero / exchange[1]
				sub_tot[1] += i.febrero / exchange[2]
				sub_tot[2] += i.marzo / exchange[3]
				sub_tot[3] += i.abril / exchange[4]
				sub_tot[4] += i.mayo / exchange[5]
				sub_tot[5] += i.junio / exchange[6]
				sub_tot[6] += i.julio / exchange[7]
				sub_tot[7] += i.agosto / exchange[8]
				sub_tot[8] += i.septiembre / exchange[9]
				sub_tot[9] += i.octubre / exchange[10]
				sub_tot[10] += i.noviembre / exchange[11]
				sub_tot[11] += i.diciembre / exchange[12]
				sub_tot[12] += i.acumulado_usd
				sub_tot[13] += i.acumulado_pciento_usd
				sub_tot[14] += i.promedio_usd
				sub_tot[15] += i.promedio_pciento_usd
				x += 1
				n_grupo = i.grupo
				n_tipo = i.tipo
			elif n_grupo != i.grupo:
				worksheet.write(x,0, u'SUB TOTAL', boldtotal)
				col = 1
				mon = 0
				while mon+1 <= doce:
					worksheet.write(x,col, ((sub_tot[mon])), numberdos)
					col += 1
					mon += 1
				worksheet.write(x,col, ((sub_tot[-4])), numberdos)
				col += 1
				worksheet.write(x,col, ((sub_tot[-3])), numberdos)
				col += 1
				worksheet.write(x,col, ((sub_tot[-2])), numberdos)
				col += 1
				worksheet.write(x,col, ((sub_tot[-1])), numberdos)
				
				tot_tot[0] += sub_tot[0]
				tot_tot[1] += sub_tot[1]
				tot_tot[2] += sub_tot[2]
				tot_tot[3] += sub_tot[3]
				tot_tot[4] += sub_tot[4]
				tot_tot[5] += sub_tot[5]
				tot_tot[6] += sub_tot[6]
				tot_tot[7] += sub_tot[7]
				tot_tot[8] += sub_tot[8]
				tot_tot[9] += sub_tot[9]
				tot_tot[10] += sub_tot[10]
				tot_tot[11] += sub_tot[11]
				tot_tot[12] += sub_tot[12]
				tot_tot[13] += sub_tot[13]
				tot_tot[14] += sub_tot[14]
				tot_tot[15] += sub_tot[15]
				sub_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
				x += 1
				worksheet.write(x,0, u'{0}'.format(i.grupo.titulo), bold)
				x += 1
				
				worksheet.write(x,0, u'{0}'.format(i.concepto), normal)
				mon_m = {
					0: i.enero / exchange[1],
					1: i.febrero / exchange[2],
					2: i.marzo / exchange[3],
					3: i.abril / exchange[4],
					4: i.mayo / exchange[5],
					5: i.junio / exchange[6],
					6: i.julio / exchange[7],
					7: i.agosto / exchange[8],
					8: i.septiembre / exchange[9],
					9: i.octubre / exchange[10],
					10: i.noviembre / exchange[11],
					11: i.diciembre / exchange[12],
				}
				col = 1
				mon = 0
				while mon+1 <= doce:
					worksheet.write(x,col, ((mon_m[mon])), numberdoscon)
					col += 1
					mon += 1
				worksheet.write(x,col, ((i.acumulado_usd)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.acumulado_pciento_usd)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.promedio_usd)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.promedio_pciento_usd)), numberdoscon)
				
				sub_tot[0] += i.enero / exchange[1]
				sub_tot[1] += i.febrero / exchange[2]
				sub_tot[2] += i.marzo / exchange[3]
				sub_tot[3] += i.abril / exchange[4]
				sub_tot[4] += i.mayo / exchange[5]
				sub_tot[5] += i.junio / exchange[6]
				sub_tot[6] += i.julio / exchange[7]
				sub_tot[7] += i.agosto / exchange[8]
				sub_tot[8] += i.septiembre / exchange[9]
				sub_tot[9] += i.octubre / exchange[10]
				sub_tot[10] += i.noviembre / exchange[11]
				sub_tot[11] += i.diciembre / exchange[12]
				sub_tot[12] += i.acumulado_usd
				sub_tot[13] += i.acumulado_pciento_usd
				sub_tot[14] += i.promedio_usd
				sub_tot[15] += i.promedio_pciento_usd
				x += 1
				n_grupo = i.grupo
			else:
				
				worksheet.write(x,0, u'{0}'.format(i.concepto), normal)
				mon_m = {
					0: i.enero / exchange[1],
					1: i.febrero / exchange[2],
					2: i.marzo / exchange[3],
					3: i.abril / exchange[4],
					4: i.mayo / exchange[5],
					5: i.junio / exchange[6],
					6: i.julio / exchange[7],
					7: i.agosto / exchange[8],
					8: i.septiembre / exchange[9],
					9: i.octubre / exchange[10],
					10: i.noviembre / exchange[11],
					11: i.diciembre / exchange[12],
				}
				col = 1
				mon = 0
				while mon+1 <= doce:
					worksheet.write(x,col, ((mon_m[mon])), numberdoscon)
					col += 1
					mon += 1
				worksheet.write(x,col, ((i.acumulado_usd)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.acumulado_pciento_usd)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.promedio_usd)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.promedio_pciento_usd)), numberdoscon)
				
				sub_tot[0] += i.enero / exchange[1]
				sub_tot[1] += i.febrero / exchange[2]
				sub_tot[2] += i.marzo / exchange[3]
				sub_tot[3] += i.abril / exchange[4]
				sub_tot[4] += i.mayo / exchange[5]
				sub_tot[5] += i.junio / exchange[6]
				sub_tot[6] += i.julio / exchange[7]
				sub_tot[7] += i.agosto / exchange[8]
				sub_tot[8] += i.septiembre / exchange[9]
				sub_tot[9] += i.octubre / exchange[10]
				sub_tot[10] += i.noviembre / exchange[11]
				sub_tot[11] += i.diciembre / exchange[12]
				sub_tot[12] += i.acumulado_usd
				sub_tot[13] += i.acumulado_pciento_usd
				sub_tot[14] += i.promedio_usd
				sub_tot[15] += i.promedio_pciento_usd
				x += 1

			ultimo_elem = i
			
		tot_tot[0] += sub_tot[0]
		tot_tot[1] += sub_tot[1]
		tot_tot[2] += sub_tot[2]
		tot_tot[3] += sub_tot[3]
		tot_tot[4] += sub_tot[4]
		tot_tot[5] += sub_tot[5]
		tot_tot[6] += sub_tot[6]
		tot_tot[7] += sub_tot[7]
		tot_tot[8] += sub_tot[8]
		tot_tot[9] += sub_tot[9]
		tot_tot[10] += sub_tot[10]
		tot_tot[11] += sub_tot[11]
		tot_tot[12] += sub_tot[12]
		tot_tot[13] += sub_tot[13]
		tot_tot[14] += sub_tot[14]
		tot_tot[15] += sub_tot[15]

		tot_tot_tot[0] += tot_tot[0]
		tot_tot_tot[1] += tot_tot[1]
		tot_tot_tot[2] += tot_tot[2]
		tot_tot_tot[3] += tot_tot[3]
		tot_tot_tot[4] += tot_tot[4]
		tot_tot_tot[5] += tot_tot[5]
		tot_tot_tot[6] += tot_tot[6]
		tot_tot_tot[7] += tot_tot[7]
		tot_tot_tot[8] += tot_tot[8]
		tot_tot_tot[9] += tot_tot[9]
		tot_tot_tot[10] += tot_tot[10]
		tot_tot_tot[11] += tot_tot[11]
		tot_tot_tot[12] += tot_tot[12]
		tot_tot_tot[13] += tot_tot[13]
		tot_tot_tot[14] += tot_tot[14]
		tot_tot_tot[15] += tot_tot[15]

		worksheet.write(x,0, u'SUB TOTAL', boldtotal)
		col = 1
		mon = 0
		while mon+1 <= doce:
			worksheet.write(x,col, ((sub_tot[mon])), numberdos)
			col += 1
			mon += 1
		worksheet.write(x,col, ((sub_tot[-4])), numberdos)
		col += 1
		worksheet.write(x,col, ((sub_tot[-3])), numberdos)
		col += 1
		worksheet.write(x,col, ((sub_tot[-2])), numberdos)
		col += 1
		worksheet.write(x,col, ((sub_tot[-1])), numberdos)
		x += 1

		worksheet.write(x,0, u"TOTAL " + n_tipo.titulo.upper(), boldtotal)
		col = 1
		mon = 0
		while mon+1 <= doce:
			worksheet.write(x,col, ((tot_tot[mon])), numberdos)
			col += 1
			mon += 1
		worksheet.write(x,col, ((tot_tot[-4])), numberdos)
		col += 1
		worksheet.write(x,col, ((tot_tot[-3])), numberdos)
		col += 1
		worksheet.write(x,col, ((tot_tot[-2])), numberdos)
		col += 1
		worksheet.write(x,col, ((tot_tot[-1])), numberdos)
		col += 1
		x += 1

		worksheet.write(x,0, u"COSTO TOTAL DEL PROCESO", boldtotal)
		col = 1
		mon = 0
		while mon+1 <= doce:
			worksheet.write(x,col, ((tot_tot_tot[mon])), numberdos)
			col += 1
			mon += 1
		worksheet.write(x,col, ((tot_tot_tot[-4])), numberdos)
		col += 1
		worksheet.write(x,col, ((tot_tot_tot[-3])), numberdos)
		col += 1
		worksheet.write(x,col, ((tot_tot_tot[-2])), numberdos)
		col += 1
		worksheet.write(x,col, ((tot_tot_tot[-1])), numberdos)
		col += 1
		x += 1

		t = 11.86
		worksheet.set_column('A:A', 49)
		worksheet.set_column('B:B', t)
		worksheet.set_column('C:C', t)
		worksheet.set_column('D:D', t)
		worksheet.set_column('E:E', t)
		worksheet.set_column('F:F', t)
		worksheet.set_column('G:G', t)
		worksheet.set_column('H:H', t)
		worksheet.set_column('I:I', t)
		worksheet.set_column('J:J', t)
		worksheet.set_column('K:K', t)
		worksheet.set_column('L:L', t)
		worksheet.set_column('M:M', t)
		worksheet.set_column('N:N', t)
		worksheet.set_column('O:O', t)
		worksheet.set_column('P:P', t)
		worksheet.set_column('Q:Q', t)


		x += 2
		worksheet.write(x,0, u'Otros datos Informativos'.format(i.tipo.titulo), bold)
		x += 1

		nombres = ["TONELADAS PRODUCIDAS","COSTO PROCESO POR TONELADA", "COSTO POR TONELADA SIN EXPLOSIVOS", "COSTO DE EXPLOSIVOS", "COSTO LABORATORIO POR TON.", "COSTO POR TON. SIN DEPRECIACIÓN"]
		valores = [[0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0]]
		valores = self.get_valores()[0]
		for k in range(12):
			if valores[0][k] == 0:
				valores[1][k] = 0
				valores[2][k] = 0
				valores[3][k] = 0
				valores[4][k] = 0
				valores[5][k] = 0
			else:
				explosivo = self.env['rm.report.micronizado.line'].search( [('rm_report_micronizado_id','=',self.id),('pie_pagina','=','explosivo')] )
				explosivo_val = 0
				if len(explosivo) >0:
					explosivo = explosivo[0]
					if k == 0:
						explosivo_val = explosivo.enero / exchange[1]
					elif k== 1:
						explosivo_val = explosivo.febrero / exchange[2]
					elif k== 2:
						explosivo_val = explosivo.marzo / exchange[3]
					elif k== 3:
						explosivo_val = explosivo.abril / exchange[4]
					elif k== 4:
						explosivo_val = explosivo.mayo / exchange[5]
					elif k== 5:
						explosivo_val = explosivo.junio / exchange[6]
					elif k== 6:
						explosivo_val = explosivo.julio / exchange[7]
					elif k== 7:
						explosivo_val = explosivo.agosto / exchange[8]
					elif k== 8:
						explosivo_val = explosivo.septiembre / exchange[9]
					elif k== 9:
						explosivo_val = explosivo.octubre / exchange[10]
					elif k== 10:
						explosivo_val = explosivo.noviembre / exchange[11]
					elif k== 11:
						explosivo_val = explosivo.diciembre / exchange[12]


				laboratorio = self.env['rm.report.micronizado.line'].search( [('rm_report_micronizado_id','=',self.id),('pie_pagina','=','laboratorio')] )
				laboratorio_val = 0
				if len(laboratorio) >0:
					laboratorio = laboratorio[0]
					if k == 0:
						laboratorio_val = laboratorio.enero / exchange[1]
					elif k== 1:
						laboratorio_val = laboratorio.febrero / exchange[2]
					elif k== 2:
						laboratorio_val = laboratorio.marzo / exchange[3]
					elif k== 3:
						laboratorio_val = laboratorio.abril / exchange[4]
					elif k== 4:
						laboratorio_val = laboratorio.mayo / exchange[5]
					elif k== 5:
						laboratorio_val = laboratorio.junio / exchange[6]
					elif k== 6:
						laboratorio_val = laboratorio.julio / exchange[7]
					elif k== 7:
						laboratorio_val = laboratorio.agosto / exchange[8]
					elif k== 8:
						laboratorio_val = laboratorio.septiembre / exchange[9]
					elif k== 9:
						laboratorio_val = laboratorio.octubre / exchange[10]
					elif k== 10:
						laboratorio_val = laboratorio.noviembre / exchange[11]
					elif k== 11:
						laboratorio_val = laboratorio.diciembre / exchange[12]


				depreciacion = self.env['rm.report.micronizado.line'].search( [('rm_report_micronizado_id','=',self.id),('pie_pagina','=','depreciacion')] )
				depreciacion_val = 0
				for dep in depreciacion:
					if k == 0:
						depreciacion_val += dep.enero / exchange[1]
					elif k== 1:
						depreciacion_val += dep.febrero / exchange[2]
					elif k== 2:
						depreciacion_val += dep.marzo / exchange[3]
					elif k== 3:
						depreciacion_val += dep.abril / exchange[4]
					elif k== 4:
						depreciacion_val += dep.mayo / exchange[5]
					elif k== 5:
						depreciacion_val += dep.junio / exchange[6]
					elif k== 6:
						depreciacion_val += dep.julio / exchange[7]
					elif k== 7:
						depreciacion_val += dep.agosto / exchange[8]
					elif k== 8:
						depreciacion_val += dep.septiembre / exchange[9]
					elif k== 9:
						depreciacion_val += dep.octubre / exchange[10]
					elif k== 10:
						depreciacion_val += dep.noviembre / exchange[11]
					elif k== 11:
						depreciacion_val += dep.diciembre / exchange[12]

				valores[1][k] = tot_tot_tot[k] / valores[0][k]
				valores[2][k] = (tot_tot_tot[k] - explosivo_val )/valores[0][k]
				valores[3][k] = explosivo_val / valores[0][k]
				valores[4][k] = laboratorio_val / valores[0][k]
				valores[5][k] = (tot_tot_tot[k] - (depreciacion_val))/valores[0][k]

		
		worksheet.write(x,0, u'CONCEPTO', boldbord)
		col = 1
		mon = 0
		while mon+1 <= doce:
			worksheet.write(x,col, u'{0}'.format(colum[mon+1]), boldbord)
			col += 1
			mon += 1

		x += 1


		for i in range(0,6):
			worksheet.write(x,0, u'{0}'.format(nombres[i]), normal)
			col = 1
			mon = 0
			while mon+1 <= doce:
				worksheet.write(x,col, ((valores[i][mon])), numberdoscon)
				col += 1
				mon += 1
			x += 1

		x += 2
		worksheet.write(x,0, u'Pie de Página', bold)
		x += 1
		worksheet.merge_range(x,0,x+1,0, u'CONCEPTO', merge_format)
		worksheet.merge_range(x,1,x,3, u'MES ACTUAL', merge_format)
		worksheet.merge_range(x,4,x,6, u'ACUMULADO', merge_format)
		worksheet.write(x,7, u'TCVP', boldbord)
		x += 1
		worksheet.write(x,1, u'TONS', boldbord)
		worksheet.write(x,2, u'PROMEDIO', boldbord)
		worksheet.write(x,3, u'IMPORTE', boldbord)
		worksheet.write(x,4, u'TONS', boldbord)
		worksheet.write(x,5, u'PROMEDIO', boldbord)
		worksheet.write(x,6, u'IMPORTE', boldbord)
		tcvp =  self.env['tipo.cambio.mexicano'].search([('periodo_id','=',self.period_actual.id)])
		if len(tcvp) != 1:
			raise exceptions.Warning('No se ha encontrado el tipo de cambio promedio para el periodo: '
				+str(self.period_actual.name)+ '\n o el T.C. para dicho periodo esta duplicado')
		tcvp = tcvp[0].promedio_venta if tcvp[0].promedio_venta > 0 else 1
		worksheet.write(x,7,tcvp , numberdoscon)
		x += 1

		nombres = ["TRASPASO PROCESO ANTERIOR","PRODUCCION COSTO POR TONELADA","INVENTARIO INICIAL","COMPRAS","DISPONIBLE","ENVIO TR","TRASPASO A TRITURACION","TRASPASO A AGREGADOS","VENTAS","AJUSTE DE INVENTARIO","OTRAS SALIDAS","INVENTARIO FINAL"]
		
		data_final_pagina = self.get_pie_pagina()[0]

		for i in range(12):
			worksheet.write(x,0, nombres[i], normal)
			worksheet.write(x,1, (data_final_pagina[i][0]), numberdoscon)
			worksheet.write(x,2, ((data_final_pagina[i][1]))/tcvp, numberdoscon)
			worksheet.write(x,3, ((data_final_pagina[i][2]))/tcvp, numberdoscon)
			worksheet.write(x,4, ((data_final_pagina[i][3])), numberdoscon)
			worksheet.write(x,5, ((data_final_pagina[i][4]))/tcvp, numberdoscon)
			worksheet.write(x,6, ((data_final_pagina[i][5]))/tcvp, numberdoscon)
			x += 1

		workbook.close()
		
		f = open(direccion + 'Reporte_Micronizado_USD.xlsx', 'rb')
		
		vals = {
			'output_name': 'Reporte_Micronizado_USD.xlsx',
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

	""" ----------------------------- REPORTE EXCEL ----------------------------- """