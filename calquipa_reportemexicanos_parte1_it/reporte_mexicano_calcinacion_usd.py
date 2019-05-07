# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv

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

class rm_report_calcinacion(models.Model):
	_inherit= 'rm.report.calcinacion'

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

		workbook = Workbook(direccion +'Reporte_Calcinación_USD.xlsx')
		worksheet = workbook.add_worksheet("Calcinación")
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
		# colum = {
		# 	1: "TIPO COSTO",
		# 	2: "Enero",
		# 	3: "Febrero",
		# 	4: "Marzo",
		# 	5: "Abril",
		# 	6: "Mayo",
		# 	7: "Junio",
		# 	8: "Julio",
		# 	9: "Agosto",
		# 	10: "Septiembre",
		# 	11: "Octubre",
		# 	12: "Noviembre",
		# 	13: "Diciembre",
		# 	14: "Acumulado",
		# 	15: "%  ACUM",
		# 	16: "Promedio",
		# 	17: "%  PROM"
		# }
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

		# for k,v in colum.items():
		# 	worksheet.write(14,k-1, u'{0}'.format(v), boldbord)
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


		elements = self.env['rm.report.calcinacion.line'].search([('rm_report_calcinacion_id','=',self.id)]).sorted(key=lambda r: dig_5(r.tipo.order)+dig_5(r.grupo.order))
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
				worksheet.write(x,1, ((sub_tot[0])), numberdos)
				worksheet.write(x,2, ((sub_tot[1])), numberdos)
				worksheet.write(x,3, ((sub_tot[2])), numberdos)
				worksheet.write(x,4, ((sub_tot[3])), numberdos)
				worksheet.write(x,5, ((sub_tot[4])), numberdos)
				worksheet.write(x,6, ((sub_tot[5])), numberdos)
				worksheet.write(x,7, ((sub_tot[6])), numberdos)
				worksheet.write(x,8, ((sub_tot[7])), numberdos)
				worksheet.write(x,9, ((sub_tot[8])), numberdos)
				worksheet.write(x,10, ((sub_tot[9])), numberdos)
				worksheet.write(x,11, ((sub_tot[10])), numberdos)
				worksheet.write(x,12, ((sub_tot[11])), numberdos)
				worksheet.write(x,13, ((sub_tot[12])), numberdos)
				worksheet.write(x,14, ((sub_tot[13])), numberdos)
				worksheet.write(x,15, ((sub_tot[14])), numberdos)
				worksheet.write(x,16, ((sub_tot[15])), numberdos)

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
				worksheet.write(x,1, ((tot_tot[0])), numberdos)
				worksheet.write(x,2, ((tot_tot[1])), numberdos)
				worksheet.write(x,3, ((tot_tot[2])), numberdos)
				worksheet.write(x,4, ((tot_tot[3])), numberdos)
				worksheet.write(x,5, ((tot_tot[4])), numberdos)
				worksheet.write(x,6, ((tot_tot[5])), numberdos)
				worksheet.write(x,7, ((tot_tot[6])), numberdos)
				worksheet.write(x,8, ((tot_tot[7])), numberdos)
				worksheet.write(x,9, ((tot_tot[8])), numberdos)
				worksheet.write(x,10, ((tot_tot[9])), numberdos)
				worksheet.write(x,11, ((tot_tot[10])), numberdos)
				worksheet.write(x,12, ((tot_tot[11])), numberdos)
				worksheet.write(x,13, ((tot_tot[12])), numberdos)
				worksheet.write(x,14, ((tot_tot[13])), numberdos)
				worksheet.write(x,15, ((tot_tot[14])), numberdos)
				worksheet.write(x,16, ((tot_tot[15])), numberdos)
				sub_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
				tot_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

				x += 1
				worksheet.write(x,0, u'{0}'.format(i.tipo.titulo), bold)
				x += 1
				worksheet.write(x,0, u'{0}'.format(i.grupo.titulo), bold)
				x += 1
				worksheet.write(x,0, u'{0}'.format(i.concepto), normal)
				worksheet.write(x,1, ((i.enero)/exchange[1]), numberdoscon)
				worksheet.write(x,2, ((i.febrero)/exchange[2]), numberdoscon)
				worksheet.write(x,3, ((i.marzo)/exchange[3]), numberdoscon)
				worksheet.write(x,4, ((i.abril)/exchange[4]), numberdoscon)
				worksheet.write(x,5, ((i.mayo)/exchange[5]), numberdoscon)
				worksheet.write(x,6, ((i.junio)/exchange[6]), numberdoscon)
				worksheet.write(x,7, ((i.julio)/exchange[7]), numberdoscon)
				worksheet.write(x,8, ((i.agosto)/exchange[8]), numberdoscon)
				worksheet.write(x,9, ((i.septiembre)/exchange[9]), numberdoscon)
				worksheet.write(x,10, ((i.octubre)/exchange[10]), numberdoscon)
				worksheet.write(x,11, ((i.noviembre)/exchange[11]), numberdoscon)
				worksheet.write(x,12, ((i.diciembre)/exchange[12]), numberdoscon)
				worksheet.write(x,13, ((i.acumulado)), numberdoscon)
				worksheet.write(x,14, ((i.acumulado_pciento)), numberdoscon)
				worksheet.write(x,15, ((i.promedio)), numberdoscon)
				worksheet.write(x,16, ((i.promedio_pciento)), numberdoscon)
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
				sub_tot[12] += i.acumulado
				sub_tot[13] += i.acumulado_pciento
				sub_tot[14] += i.promedio
				sub_tot[15] += i.promedio_pciento
				x += 1
				n_grupo = i.grupo
				n_tipo = i.tipo
			elif n_grupo != i.grupo:
				worksheet.write(x,0, u'SUB TOTAL', boldtotal)
				worksheet.write(x,1, ((sub_tot[0])), numberdos)
				worksheet.write(x,2, ((sub_tot[1])), numberdos)
				worksheet.write(x,3, ((sub_tot[2])), numberdos)
				worksheet.write(x,4, ((sub_tot[3])), numberdos)
				worksheet.write(x,5, ((sub_tot[4])), numberdos)
				worksheet.write(x,6, ((sub_tot[5])), numberdos)
				worksheet.write(x,7, ((sub_tot[6])), numberdos)
				worksheet.write(x,8, ((sub_tot[7])), numberdos)
				worksheet.write(x,9, ((sub_tot[8])), numberdos)
				worksheet.write(x,10, ((sub_tot[9])), numberdos)
				worksheet.write(x,11, ((sub_tot[10])), numberdos)
				worksheet.write(x,12, ((sub_tot[11])), numberdos)
				worksheet.write(x,13, ((sub_tot[12])), numberdos)
				worksheet.write(x,14, ((sub_tot[13])), numberdos)
				worksheet.write(x,15, ((sub_tot[14])), numberdos)
				worksheet.write(x,16, ((sub_tot[15])), numberdos)
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
				worksheet.write(x,1, ((i.enero)/exchange[1]), numberdoscon)
				worksheet.write(x,2, ((i.febrero)/exchange[2]), numberdoscon)
				worksheet.write(x,3, ((i.marzo)/exchange[3]), numberdoscon)
				worksheet.write(x,4, ((i.abril)/exchange[4]), numberdoscon)
				worksheet.write(x,5, ((i.mayo)/exchange[5]), numberdoscon)
				worksheet.write(x,6, ((i.junio)/exchange[6]), numberdoscon)
				worksheet.write(x,7, ((i.julio)/exchange[7]), numberdoscon)
				worksheet.write(x,8, ((i.agosto)/exchange[8]), numberdoscon)
				worksheet.write(x,9, ((i.septiembre)/exchange[9]), numberdoscon)
				worksheet.write(x,10, ((i.octubre)/exchange[10]), numberdoscon)
				worksheet.write(x,11, ((i.noviembre)/exchange[11]), numberdoscon)
				worksheet.write(x,12, ((i.diciembre)/exchange[12]), numberdoscon)
				worksheet.write(x,13, ((i.acumulado)), numberdoscon)
				worksheet.write(x,14, ((i.acumulado_pciento)), numberdoscon)
				worksheet.write(x,15, ((i.promedio)), numberdoscon)
				worksheet.write(x,16, ((i.promedio_pciento)), numberdoscon)
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
				sub_tot[12] += i.acumulado
				sub_tot[13] += i.acumulado_pciento
				sub_tot[14] += i.promedio
				sub_tot[15] += i.promedio_pciento
				x += 1
				n_grupo = i.grupo
			else:
				
				worksheet.write(x,0, u'{0}'.format(i.concepto), normal)
				worksheet.write(x,1, ((i.enero)/exchange[1]), numberdoscon)
				worksheet.write(x,2, ((i.febrero)/exchange[2]), numberdoscon)
				worksheet.write(x,3, ((i.marzo)/exchange[3]), numberdoscon)
				worksheet.write(x,4, ((i.abril)/exchange[4]), numberdoscon)
				worksheet.write(x,5, ((i.mayo)/exchange[5]), numberdoscon)
				worksheet.write(x,6, ((i.junio)/exchange[6]), numberdoscon)
				worksheet.write(x,7, ((i.julio)/exchange[7]), numberdoscon)
				worksheet.write(x,8, ((i.agosto)/exchange[8]), numberdoscon)
				worksheet.write(x,9, ((i.septiembre)/exchange[9]), numberdoscon)
				worksheet.write(x,10, ((i.octubre)/exchange[10]), numberdoscon)
				worksheet.write(x,11, ((i.noviembre)/exchange[11]), numberdoscon)
				worksheet.write(x,12, ((i.diciembre)/exchange[12]), numberdoscon)
				worksheet.write(x,13, ((i.acumulado)), numberdoscon)
				worksheet.write(x,14, ((i.acumulado_pciento)), numberdoscon)
				worksheet.write(x,15, ((i.promedio)), numberdoscon)
				worksheet.write(x,16, ((i.promedio_pciento)), numberdoscon)
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
				sub_tot[12] += i.acumulado
				sub_tot[13] += i.acumulado_pciento
				sub_tot[14] += i.promedio
				sub_tot[15] += i.promedio_pciento
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
		worksheet.write(x,1, ((sub_tot[0])), numberdos)
		worksheet.write(x,2, ((sub_tot[1])), numberdos)
		worksheet.write(x,3, ((sub_tot[2])), numberdos)
		worksheet.write(x,4, ((sub_tot[3])), numberdos)
		worksheet.write(x,5, ((sub_tot[4])), numberdos)
		worksheet.write(x,6, ((sub_tot[5])), numberdos)
		worksheet.write(x,7, ((sub_tot[6])), numberdos)
		worksheet.write(x,8, ((sub_tot[7])), numberdos)
		worksheet.write(x,9, ((sub_tot[8])), numberdos)
		worksheet.write(x,10, ((sub_tot[9])), numberdos)
		worksheet.write(x,11, ((sub_tot[10])), numberdos)
		worksheet.write(x,12, ((sub_tot[11])), numberdos)
		worksheet.write(x,13, ((sub_tot[12])), numberdos)
		worksheet.write(x,14, ((sub_tot[13])), numberdos)
		worksheet.write(x,15, ((sub_tot[14])), numberdos)
		worksheet.write(x,16, ((sub_tot[15])), numberdos)
		x += 1

		worksheet.write(x,0, u"TOTAL " + n_tipo.titulo.upper(), boldtotal)
		worksheet.write(x,1, ((tot_tot[0])), numberdos)
		worksheet.write(x,2, ((tot_tot[1])), numberdos)
		worksheet.write(x,3, ((tot_tot[2])), numberdos)
		worksheet.write(x,4, ((tot_tot[3])), numberdos)
		worksheet.write(x,5, ((tot_tot[4])), numberdos)
		worksheet.write(x,6, ((tot_tot[5])), numberdos)
		worksheet.write(x,7, ((tot_tot[6])), numberdos)
		worksheet.write(x,8, ((tot_tot[7])), numberdos)
		worksheet.write(x,9, ((tot_tot[8])), numberdos)
		worksheet.write(x,10, ((tot_tot[9])), numberdos)
		worksheet.write(x,11, ((tot_tot[10])), numberdos)
		worksheet.write(x,12, ((tot_tot[11])), numberdos)
		worksheet.write(x,13, ((tot_tot[12])), numberdos)
		worksheet.write(x,14, ((tot_tot[13])), numberdos)
		worksheet.write(x,15, ((tot_tot[14])), numberdos)
		worksheet.write(x,16, ((tot_tot[15])), numberdos)
		x += 1

		worksheet.write(x,0, u"COSTO TOTAL DEL PROCESO", boldtotal)
		worksheet.write(x,1, ((tot_tot_tot[0])), numberdos)
		worksheet.write(x,2, ((tot_tot_tot[1])), numberdos)
		worksheet.write(x,3, ((tot_tot_tot[2])), numberdos)
		worksheet.write(x,4, ((tot_tot_tot[3])), numberdos)
		worksheet.write(x,5, ((tot_tot_tot[4])), numberdos)
		worksheet.write(x,6, ((tot_tot_tot[5])), numberdos)
		worksheet.write(x,7, ((tot_tot_tot[6])), numberdos)
		worksheet.write(x,8, ((tot_tot_tot[7])), numberdos)
		worksheet.write(x,9, ((tot_tot_tot[8])), numberdos)
		worksheet.write(x,10, ((tot_tot_tot[9])), numberdos)
		worksheet.write(x,11, ((tot_tot_tot[10])), numberdos)
		worksheet.write(x,12, ((tot_tot_tot[11])), numberdos)
		worksheet.write(x,13, ((tot_tot_tot[12])), numberdos)
		worksheet.write(x,14, ((tot_tot_tot[13])), numberdos)
		worksheet.write(x,15, ((tot_tot_tot[14])), numberdos)
		worksheet.write(x,16, ((tot_tot_tot[15])), numberdos)
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
				explosivo = self.env['rm.report.calcinacion.line'].search( [('rm_report_calcinacion_id','=',self.id),('pie_pagina','=','explosivo')] )
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


				laboratorio = self.env['rm.report.calcinacion.line'].search( [('rm_report_calcinacion_id','=',self.id),('pie_pagina','=','laboratorio')] )
				laboratorio_val = 0
				if len(laboratorio) >0:
					laboratorio = laboratorio[0]
					if k == 0:
						laboratorio_val = laboratorio.enero/exchange[1]
					elif k== 1:
						laboratorio_val = laboratorio.febrero/exchange[2]
					elif k== 2:
						laboratorio_val = laboratorio.marzo/exchange[3]
					elif k== 3:
						laboratorio_val = laboratorio.abril/exchange[4]
					elif k== 4:
						laboratorio_val = laboratorio.mayo/exchange[5]
					elif k== 5:
						laboratorio_val = laboratorio.junio/exchange[6]
					elif k== 6:
						laboratorio_val = laboratorio.julio/exchange[7]
					elif k== 7:
						laboratorio_val = laboratorio.agosto/exchange[8]
					elif k== 8:
						laboratorio_val = laboratorio.septiembre/exchange[9]
					elif k== 9:
						laboratorio_val = laboratorio.octubre/exchange[10]
					elif k== 10:
						laboratorio_val = laboratorio.noviembre/exchange[11]
					elif k== 11:
						laboratorio_val = laboratorio.diciembre/exchange[12]


				depreciacion = self.env['rm.report.calcinacion.line'].search( [('rm_report_calcinacion_id','=',self.id),('pie_pagina','=','depreciacion')] )
				depreciacion_val = 0
				for dep in depreciacion:
					if k == 0:
						depreciacion_val += dep.enero/exchange[1]
					elif k== 1:
						depreciacion_val += dep.febrero/exchange[2]
					elif k== 2:
						depreciacion_val += dep.marzo/exchange[3]
					elif k== 3:
						depreciacion_val += dep.abril/exchange[4]
					elif k== 4:
						depreciacion_val += dep.mayo/exchange[5]
					elif k== 5:
						depreciacion_val += dep.junio/exchange[6]
					elif k== 6:
						depreciacion_val += dep.julio/exchange[7]
					elif k== 7:
						depreciacion_val += dep.agosto/exchange[8]
					elif k== 8:
						depreciacion_val += dep.septiembre/exchange[9]
					elif k== 9:
						depreciacion_val += dep.octubre/exchange[10]
					elif k== 10:
						depreciacion_val += dep.noviembre/exchange[11]
					elif k== 11:
						depreciacion_val += dep.diciembre/exchange[12]

				valores[1][k] = tot_tot_tot[k] / valores[0][k]
				valores[2][k] = (tot_tot_tot[k] - explosivo_val )/valores[0][k]
				valores[3][k] = explosivo_val / valores[0][k]
				valores[4][k] = laboratorio_val / valores[0][k]
				valores[5][k] = (tot_tot_tot[k] - (depreciacion_val))/valores[0][k]

		worksheet.write(x,0, u'CONCEPTO', boldbord)
		worksheet.write(x,1, u'Enero', boldbord)
		worksheet.write(x,2, u'Febrero', boldbord)
		worksheet.write(x,3, u'Marzo', boldbord)
		worksheet.write(x,4, u'Abril', boldbord)
		worksheet.write(x,5, u'Mayo', boldbord)
		worksheet.write(x,6, u'Junio', boldbord)
		worksheet.write(x,7, u'Julio', boldbord)
		worksheet.write(x,8, u'Agosto', boldbord)
		worksheet.write(x,9, u'Septiembre', boldbord)
		worksheet.write(x,10, u'Octubre', boldbord)
		worksheet.write(x,11, u'Noviembre', boldbord)
		worksheet.write(x,12, u'Diciembre', boldbord)
		x += 1

		for i in range(0,6):
			worksheet.write(x,0, u'{0}'.format(nombres[i]), normal)
			worksheet.write(x,1, ((valores[i][0])), numberdoscon)
			worksheet.write(x,2, ((valores[i][1])), numberdoscon)
			worksheet.write(x,3, ((valores[i][2])), numberdoscon)
			worksheet.write(x,4, ((valores[i][3])), numberdoscon)
			worksheet.write(x,5, ((valores[i][4])), numberdoscon)
			worksheet.write(x,6, ((valores[i][5])), numberdoscon)
			worksheet.write(x,7, ((valores[i][6])), numberdoscon)
			worksheet.write(x,8, ((valores[i][7])), numberdoscon)
			worksheet.write(x,9, ((valores[i][8])), numberdoscon)
			worksheet.write(x,10, ((valores[i][9])), numberdoscon)
			worksheet.write(x,11, ((valores[i][10])), numberdoscon)
			worksheet.write(x,12, ((valores[i][11])), numberdoscon)
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

		nombres = ["TRASPASO PROCESO ANTERIOR","PRODUCCION COSTO POR TONELADA","INVENTARIO INICIAL","COMPRAS","DISPONIBLE","ENVIO TR","TRASPASO A MICRONIZADO","TRASPASO A AGREGADOS","VENTAS","AJUSTE DE INVENTARIO","OTRAS SALIDAS","INVENTARIO FINAL"]
		
		data = self.get_pie_pagina()[0]

		for i in range(12):
			worksheet.write(x,0, nombres[i], normal)
			worksheet.write(x,1, ((data[i][0])), numberdoscon)
			worksheet.write(x,2, ((data[i][1]))/tcvp, numberdoscon)
			worksheet.write(x,3, ((data[i][2]))/tcvp, numberdoscon)
			worksheet.write(x,4, ((data[i][3]))/tcvp, numberdoscon)
			worksheet.write(x,5, ((data[i][4]))/tcvp, numberdoscon)
			worksheet.write(x,6, ((data[i][5]))/tcvp, numberdoscon)
			x += 1
		workbook.close()
		
		f = open(direccion + 'Reporte_Calcinación_USD.xlsx', 'rb')
		
		vals = {
			'output_name': 'Reporte_Calcinación_USD.xlsx',
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


	# metodos para obtener datos de kardex, 
	#quedan pendiente para futuras mejoras
	# (no nos borres no te hacemos nada :) )
	#
	@api.multi
	def get_inv_ini(self,location,product,conf,initial_period=None):
		ton,imp,prom = 0,0,0
		if initial_period:
			code_ant = ['01',str(self.fiscal.name)]
		else:
			code_ant = self.period_actual.code.split('/')
		mes = int(code_ant[0])
		anio = int(code_ant[1])
		if mes == 1:
			mes = 12
			anio -= 1
		else:
			mes -= 1
		code_ant = ("%2d"%mes).replace(' ','0') + '/' + str(anio)
		periodo_anterior = self.env['account.period'].search( [('code','=',code_ant)])
		if mes == 12:
			fechaini = str(self.period_actual.date_start).replace('-','')
			fechafin = str(self.period_actual.date_stop).replace('-','')
			self.env.cr.execute(""" 
				SELECT
				round(saldof,2),
				round(saldov,2),
				CASE WHEN saldof != 0 
				THEN round(saldov/saldof,4) ELSE 0 END as cal
				 from get_kardex_v("""+fechaini+""","""+fechafin+""",
				'{"""+str(product) + """}',
				'{"""+str(conf.location_virtual_produccion.id) + """,
				""" + str(location) + """}') 
				where 
				(ubicacion_origen = """+str(conf.location_virtual_saldoinicial.id)+ """ and ubicacion_destino = """ + str(location) + """)
				or (ubicacion_origen = """+str(location) + """ and ubicacion_destino = """ + str(conf.location_virtual_saldoinicial.id) + """) 
				""")
			for i in self.env.cr.fetchall():
				ton = i[0]
				imp = i[1]
		else:
			if len(periodo_anterior )>0:
				fechaini = str(periodo_anterior.date_start).replace('-','')
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = str(periodo_anterior.date_stop).replace('-','')
				self.env.cr.execute("""
				SELECT
				round(saldof,2),
				round(saldov,2),
				CASE WHEN saldof != 0 
				THEN round(saldov/saldof,4) ELSE 0 END as cal
				 from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",
				'{""" + str(product) + """}',
				'{""" + str(conf.location_virtual_produccion.id) + """,
				""" + str(location) + """}') 
				where ubicacion_destino = """ + str(location) + """
				 or ubicacion_origen = """ + str(location) + """ 
				 """)
				for i in self.env.cr.fetchall():
					ton = i[0]
					imp = i[1]

		ton = ton if ton else 0
		imp = imp if imp else 0
		return ton,imp

	# new code
	@api.multi
	def get_ingre_trans(self,location,product,conf,dateini,datefin):
		location,product = str(location),str(product)
		ton,imp,prom = 0,0,0
		fechaini = str(dateini).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(datefin).replace('-','')
		# las tansferencias recibidas
		self.env.cr.execute("""
		SELECT  
		CASE WHEN SUM(ingreso) > 0 THEN round(SUM(ingreso),2) ELSE 0 END as ingreso,
		CASE WHEN SUM(credit) > 0 THEN round(SUM(credit),2) ELSE 0 END as credit,
		CASE WHEN SUM(ingreso) != 0 
		THEN round(SUM(credit)/SUM(ingreso),4) ELSE 0 END as cal
		 from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",
		 '{"""+str(product)+"""}',
		 '{"""+str(location)+"""}') 
		 where  
		operation_type = '06'
		and ubicacion_destino = """+location+"""
		and fecha >= '"""+ str(dateini) +"""' 
		and fecha <= '"""+ str(datefin) +"""'
		""")
		r = self.env.cr.fetchall()
		for i in r:
			ton = i[0]
			imp = i[1]
		ton = ton if ton else 0
		imp = imp if imp else 0
		return ton,imp

	# new code
	@api.multi
	def get_costo_ventas(self,location,product,conf,dateini,datefin):
		location,product = str(location),str(product)
		ton,imp,prom = 0,0,0
		fechaini = str(dateini).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(datefin).replace('-','')
		locations = self.env['stock.location'].search([('usage','=','customer')]).ids
		locations = ','.join(map(str,[location]+locations))
		self.env.cr.execute(""" 
		SELECT 
		round(SUM(ingreso),2),
		round(SUM(valor),2),
		CASE WHEN SUM(ingreso) != 0 
		THEN round(SUM(valor)/SUM(ingreso),2) ELSE 0 END as cal
		from (SELECT 
		(salida-ingreso) as ingreso,
		(credit-debit) as valor,
		ubicacion_origen,
		ubicacion_destino
		from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",
		'{"""+str(product)+"""}',
		'{"""+locations+"""}') 
		where ((ubicacion_destino = """+str(location)+""") 
		or (ubicacion_origen = """+str(location)+"""))
		and fecha >= '"""+str(dateini)+"""'  
		and fecha <= '"""+str(datefin)+"""')T
		where 
		ubicacion_origen in ("""+locations+""") 
		and ubicacion_destino in ("""+locations+""")
			""")
		for i in self.env.cr.fetchall():
			ton = i[0]
			imp = i[1]
		ton = ton if ton else 0
		imp = imp if imp else 0
		return ton,imp

	@api.multi
	def get_otros(self,location,product,conf,dateini,datefin):
		location,product = str(location),str(product)
		ton,imp,prom = 0,0,0
		fechaini = str(dateini).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(datefin).replace('-','')
		self.env.cr.execute(""" 
		SELECT 
		CASE WHEN sum(salida)>0 
		THEN round(sum(salida),2) ELSE 0 END as ingreso,
		CASE WHEN sum(credit)>0 
		THEN round(sum(credit),2) ELSE 0 END as credit,
		CASE WHEN SUM(salida) != 0 and SUM(credit) != 0
		THEN round(SUM(credit)/SUM(salida),2) ELSE 0 END as cal
		from get_kardex_v
		("""+str(fecha_inianio)+""","""+str(fechafin)+""",'{"""+product+"""}',
		'{"""+location+""","""+str(conf.location_perdidas_mermas.id)+"""}') 
		where (ubicacion_destino = """+location+"""
		or ubicacion_origen = """+location+""")
		and fecha >= '"""+str(dateini)+"""'  
		and fecha <= '"""+str(datefin)+"""'
		and operation_type = '16'
		""")
		for i in self.env.cr.fetchall():
			ton = i[0]
			imp = i[1]
		ton = ton if ton else 0
		imp = imp if imp else 0
		return ton,imp


	# new code
	@api.multi
	def get_transf_reali(self,location,product,conf,dateini,datefin):
		location,product = str(location),str(product)
		ton,imp,prom = 0,0,0
		fechaini = str(dateini).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(datefin).replace('-','')
		self.env.cr.execute(""" 
			SELECT 
			round(SUM(salida),2),
			round(SUM(credit),2),
			CASE WHEN SUM(salida) != 0
			THEN round(SUM(credit)/SUM(salida),2) ELSE 0 END as cal
			from get_kardex_v("""+str(fecha_inianio)+""","""+str(fechafin)+""",
			'{"""+product+"""}','{"""+location+"""}')
			where operation_type = '06'
			and fecha >= '"""+str(dateini)+"""'   
			and fecha <= '"""+str(datefin)+"""'
		""")
		for i in self.env.cr.fetchall():
			ton = i[0]
			imp = i[1]
		ton = ton if ton else 0
		imp = imp if imp else 0
		return ton,imp

	@api.multi
	def get_prom(self,ton,imp):
		res = 0
		try:
			res = imp/ton
		except ZeroDivisionError as e:
			print('Error: ',e)
		return res

	@api.multi
	def get_name_location(self,name):
		name = name.split('/')
		if len(name) == 2 or len(name) == 3:
			return name[1]
		elif len(name)==1:
			return name[0]
		else:
			return ''

	@api.one
	def get_pie_pagina(self):
		cp_obj = self.env['costos.produccion'].search( [('periodo','=',self.period_actual.id)] )
		rpt = []
		if len(cp_obj) >0:
			cp_obj = cp_obj[0]		
			#### la primera linea
			rpt.append([ cp_obj.piedra_tt_ton, cp_obj.piedra_tt_cp , cp_obj.piedra_tt_imp , 0,0,0])
			rpt.append([ cp_obj.calci_pro_ton, cp_obj.calci_pro_cp , cp_obj.calci_pro_imp , 0,0,0])
			rpt.append([ cp_obj.calci_ini_ton, cp_obj.calci_ini_cp , cp_obj.calci_ini_imp , 0,0,0])
			rpt.append([0,0,0,0,0,0])
			rpt.append([ cp_obj.calci_dis_ton, cp_obj.calci_dis_cp , cp_obj.calci_dis_imp , 0,0,0])
			rpt.append([0,0,0,0,0,0])
			rpt.append([ cp_obj.calci_tt_ton, cp_obj.calci_tt_cp , cp_obj.calci_tt_imp , 0,0,0])
			rpt.append([0,0,0,0,0,0])
			rpt.append([ cp_obj.calci_ven_ton, cp_obj.calci_ven_cp , cp_obj.calci_ven_imp , 0,0,0])
			rpt.append([0,0,0,0,0,0])
			rpt.append([0,0,0,0,0,0])
			rpt.append([ cp_obj.calci_final_ton, cp_obj.calci_final_cp , cp_obj.calci_final_imp , 0,0,0])
			
		else:
			for i in range(0,12):
				rpt.append([0,0,0,0,0,0])


		period_list = []
		nro_act = 1
		period_act =  ("%2d"%nro_act).replace(' ','0') +  '/' + self.period_actual.code.split('/')[1]
		nro_act = 2
		mkmk = self.env['account.period'].search( [('code','=',period_act)] )
		if len(mkmk)>0:
			period_list.append(mkmk[0])

		while period_act != self.period_actual.code:
			period_act =  ("%2d"%nro_act).replace(' ','0') +  '/' + self.period_actual.code.split('/')[1]
			nro_act += 1
			mkmk = self.env['account.period'].search( [('code','=',period_act)] )
			if len(mkmk)>0:
				period_list.append(mkmk[0])

		for i in period_list:
			cp_obj = self.env['costos.produccion'].search( [('periodo','=',i.id)] )
			if len(cp_obj) >0:
				cp_obj = cp_obj[0]		
				#### Aqui toda actualizar valores no modificarlos y  ahi sacar el promedio del medio con eso se termina ejemplo
				rpt[0][3] += cp_obj.piedra_tt_ton
				rpt[0][5] += cp_obj.piedra_tt_imp
				rpt[0][4] = 0 if rpt[0][3] == 0 else (rpt[0][5] / rpt[0][3] )

				rpt[1][3] += cp_obj.calci_pro_ton
				rpt[1][5] += cp_obj.calci_pro_imp
				rpt[1][4] = 0 if rpt[1][3] == 0 else (rpt[1][5] / rpt[1][3] )


				if i.code.split('/')[0] == '01':
					rpt[2][3] += cp_obj.calci_ini_ton
					rpt[2][5] += cp_obj.calci_ini_imp
					rpt[2][4] = 0 if rpt[2][3] == 0 else (rpt[2][5] / rpt[2][3] )

				rpt[4][3] = rpt[1][3]+ rpt[2][3]+ rpt[3][3]
				rpt[4][5] = rpt[1][5]+ rpt[2][5]+ rpt[3][5]
				rpt[4][4] = 0 if rpt[4][3] == 0 else (rpt[4][5] / rpt[4][3] )

				rpt[6][3] += cp_obj.calci_tt_ton
				rpt[6][5] += cp_obj.calci_tt_imp
				rpt[6][4] = 0 if rpt[6][3] == 0 else (rpt[6][5] / rpt[6][3] )


				rpt[8][3] += cp_obj.calci_ven_ton
				rpt[8][5] += cp_obj.calci_ven_imp
				rpt[8][4] = 0 if rpt[8][3] == 0 else (rpt[8][5] / rpt[8][3] )


				parametros = self.env['main.parameter'].search([])[0]
				tmp = []



				self.env.cr.execute(""" 
				   select sum(salida-ingreso),sum(debit-credit) from get_kardex_v("""+str(self.period_actual.date_start)[:4]+'0101'+""","""+str(self.period_actual.date_stop).replace('-','')+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
				   '{""" + str(parametros.location_existencias_calcinacion.id) + """}') 
				   where ((ubicacion_origen in (select id from stock_location where check_ajuste_inventario = true) and ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
				   or (ubicacion_destino in (select id from stock_location where check_ajuste_inventario = true) and ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """))
				   and fecha >= '"""+ str(self.period_actual.date_start) +"""' and fecha <= '"""+ str(self.period_actual.date_stop)+"""'
				""")
				tonex = 0
				preciox = 0


				for w in self.env.cr.fetchall():
					if w[0]:
						tonex += w[0]
						preciox += w[1]
				
				if tonex == None:
					tonex = 0
				if preciox == None:
					preciox = 0



				rpt[9][0] = tonex
				rpt[9][2] = preciox
				rpt[9][1] = 0 if rpt[9][0] == 0 else (rpt[9][2] / rpt[9][0] )



				self.env.cr.execute(""" 
				   select sum(salida-ingreso),sum(debit-credit) from get_kardex_v("""+str(self.period_actual.date_start)[:4]+'0101'+""","""+str(self.period_actual.date_stop).replace('-','')+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
				   '{""" + str(parametros.location_existencias_calcinacion.id) + """}') 
				   where ((ubicacion_origen in (select id from stock_location where check_ajuste_inventario = true) and ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
				   or (ubicacion_destino in (select id from stock_location where check_ajuste_inventario = true) and ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """))
				""")
				tonex = 0
				preciox = 0


				for w in self.env.cr.fetchall():
					if w[0]:
						tonex += w[0]
						preciox += w[1]
				
				if tonex == None:
					tonex = 0
				if preciox == None:
					preciox = 0



				rpt[9][3] = tonex
				rpt[9][5] = preciox
				rpt[9][4] = 0 if rpt[9][3] == 0 else (rpt[9][5] / rpt[9][3] )





				self.env.cr.execute(""" 
				   select sum(salida) as ingreso,sum(round(credit,2)) as debit from get_kardex_v("""+str(self.period_actual.date_start)[:4]+'0101'+""","""+str(self.period_actual.date_stop).replace('-','')+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
				   '{""" + str(parametros.location_existencias_calcinacion.id) + """,""" + str(parametros.location_perdidas_mermas.id) + """}') 
				   where ((ubicacion_origen = """ + str(parametros.location_perdidas_mermas.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
				   or (ubicacion_destino = """ + str(parametros.location_perdidas_mermas.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """))
				   and fecha >= '"""+ str(self.period_actual.date_start) +"""' and fecha <= '"""+ str(self.period_actual.date_stop)+"""'
				""")
				tonex = 0
				preciox = 0


				for w in self.env.cr.fetchall():
					if w[0]:
						tonex += w[0]
						preciox += w[1]
				
				if tonex == None:
					tonex = 0
				if preciox == None:
					preciox = 0


				#producto no conforme
				self.env.cr.execute(""" 
				   select sum(salida) as ingreso,sum(round(credit,2)) as debit from get_kardex_v("""+str(self.period_actual.date_start)[:4]+'0101'+""","""+str(self.period_actual.date_stop).replace('-','')+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
				   '{""" + str(parametros.location_existencias_calcinacion.id) + """,""" + str(parametros.location_perdidas_mermas.id) + """}')  as T
				   inner join stock_move sm on sm.id = T.stock_moveid
				   inner join stock_picking sp on sp.id = sm.picking_id
				   where ((ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
				   or (ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """))
				   and fecha >= '"""+ str(self.period_actual.date_start) +"""' and fecha <= '"""+ str(self.period_actual.date_stop)+"""'
				   and sp.motivo_guia = '16'
				""")


				for w in self.env.cr.fetchall():
					if w[0]:
						tonex += w[0]
						preciox += w[1]
				
				if tonex == None:
					tonex = 0
				if preciox == None:
					preciox = 0
				#fin de prod. no conforme



				rpt[10][0] = tonex
				rpt[10][2] = preciox
				rpt[10][1] = 0 if rpt[10][0] == 0 else (rpt[10][2] / rpt[10][0] )



				self.env.cr.execute(""" 
				   select sum(salida) as ingreso,sum(round(credit,2)) as debit from get_kardex_v("""+str(self.period_actual.date_start)[:4]+'0101'+""","""+str(self.period_actual.date_stop).replace('-','')+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
				   '{""" + str(parametros.location_existencias_calcinacion.id) + """,""" + str(parametros.location_perdidas_mermas.id) + """}') 
				   where (ubicacion_origen = """ + str(parametros.location_perdidas_mermas.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
				   or (ubicacion_destino = """ + str(parametros.location_perdidas_mermas.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """)
				""")
				tonex = 0
				preciox = 0


				for w in self.env.cr.fetchall():
					if w[0]:
						tonex += w[0]
						preciox += w[1]
				
				if tonex == None:
					tonex = 0
				if preciox == None:
					preciox = 0

				#prod. no conforme


				self.env.cr.execute(""" 
				   select sum(salida) as ingreso,sum(round(credit,2)) as debit from get_kardex_v("""+str(self.period_actual.date_start)[:4]+'0101'+""","""+str(self.period_actual.date_stop).replace('-','')+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
				   '{""" + str(parametros.location_existencias_calcinacion.id) + """,""" + str(parametros.location_perdidas_mermas.id) + """}') as T
				   inner join stock_move sm on sm.id = T.stock_moveid
				   inner join stock_picking sp on sp.id = sm.picking_id
				   where ((ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
				   or (ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """) )
				   and sp.motivo_guia = '16'

				""")


				for w in self.env.cr.fetchall():
					if w[0]:
						tonex += w[0]
						preciox += w[1]
				
				if tonex == None:
					tonex = 0
				if preciox == None:
					preciox = 0



				rpt[10][3] = tonex
				rpt[10][5] = preciox
				rpt[10][4] = 0 if rpt[10][3] == 0 else (rpt[10][5] / rpt[10][3] )

				
				rpt[11][0] = rpt[4][0] - rpt[5][0] -rpt[6][0] -rpt[7][0] -rpt[8][0] +rpt[9][0] -rpt[10][0]   #rpt[11][0] - rpt[10][0]
				rpt[11][2] = rpt[4][2] - rpt[5][2] -rpt[6][2] -rpt[7][2] -rpt[8][2] +rpt[9][2] -rpt[10][2]   #rpt[11][2] - rpt[10][2]
				rpt[11][1] = 0 if rpt[11][0] == 0 else (rpt[11][2] / rpt[11][0] )



				rpt[11][3] = rpt[4][3] - rpt[5][3] -rpt[6][3] -rpt[7][3] -rpt[8][3] +rpt[9][3] -rpt[10][3] 
				rpt[11][5] = rpt[4][5] - rpt[5][5] -rpt[6][5] -rpt[7][5] -rpt[8][5] +rpt[9][5] -rpt[10][5]
				rpt[11][4] = 0 if rpt[11][3] == 0 else (rpt[11][5] / rpt[11][3] )

		return rpt


	# esta funcion no funciona aun, queda pendiente:		
	@api.one
	def get_data(self):
		cp_obj = self.env['costos.produccion'].search( [('periodo','=',self.period_actual.id)] )
		rpt = []
		if len(cp_obj) >0:
			cp_obj = cp_obj[0]		
			#### la primera linea
			rpt.append([ cp_obj.piedra_tt_ton, cp_obj.piedra_tt_cp , cp_obj.piedra_tt_imp , 0,0,0])
			rpt.append([ cp_obj.calci_pro_ton, cp_obj.calci_pro_cp , cp_obj.calci_pro_imp , 0,0,0])
			rpt.append([ cp_obj.calci_ini_ton, cp_obj.calci_ini_cp , cp_obj.calci_ini_imp , 0,0,0]) # inv inicial
			rpt.append([0,0,0,0,0,0]) # ingresos
			rpt.append([ cp_obj.calci_dis_ton, cp_obj.calci_dis_cp , cp_obj.calci_dis_imp , 0,0,0])
			rpt.append([0,0,0,0,0,0]) # otros 
			rpt.append([ cp_obj.calci_tt_ton, cp_obj.calci_tt_cp , cp_obj.calci_tt_imp , 0,0,0])
			rpt.append([0,0,0,0,0,0])
			rpt.append([ cp_obj.calci_ven_ton, cp_obj.calci_ven_cp , cp_obj.calci_ven_imp , 0,0,0])
			rpt.append([0,0,0,0,0,0])
			rpt.append([0,0,0,0,0,0])
			rpt.append([ cp_obj.calci_final_ton, cp_obj.calci_final_cp , cp_obj.calci_final_imp , 0,0,0])
			
		else:
			for i in range(0,12):
				rpt.append([0,0,0,0,0,0])


		period_list = []
		nro_act = 1
		period_act =  ("%2d"%nro_act).replace(' ','0') +  '/' + self.period_actual.code.split('/')[1]
		nro_act = 2
		mkmk = self.env['account.period'].search( [('code','=',period_act)] )
		if len(mkmk)>0:
			period_list.append(mkmk[0])

		while period_act != self.period_actual.code:
			period_act =  ("%2d"%nro_act).replace(' ','0') +  '/' + self.period_actual.code.split('/')[1]
			nro_act += 1
			mkmk = self.env['account.period'].search( [('code','=',period_act)] )
			if len(mkmk)>0:
				period_list.append(mkmk[0])

		for i in period_list:
			cp_obj = self.env['costos.produccion'].search( [('periodo','=',i.id)] )
			if len(cp_obj) >0:
				cp_obj = cp_obj[0]		
				#### Aqui toda actualizar valores no modificarlos y  ahi sacar el promedio del medio con eso se termina ejemplo
				rpt[0][3] += cp_obj.piedra_tt_ton
				rpt[0][5] += cp_obj.piedra_tt_imp
				rpt[0][4] = 0 if rpt[0][3] == 0 else (rpt[0][5] / rpt[0][3] )

				rpt[1][3] += cp_obj.calci_pro_ton
				rpt[1][5] += cp_obj.calci_pro_imp
				rpt[1][4] = 0 if rpt[1][3] == 0 else (rpt[1][5] / rpt[1][3] )


				if i.code.split('/')[0] == '01':
					rpt[2][3] += cp_obj.calci_ini_ton
					rpt[2][5] += cp_obj.calci_ini_imp
					rpt[2][4] = 0 if rpt[2][3] == 0 else (rpt[2][5] / rpt[2][3] )

				rpt[4][3] = rpt[1][3]+ rpt[2][3]+ rpt[3][3]
				rpt[4][5] = rpt[1][5]+ rpt[2][5]+ rpt[3][5]
				rpt[4][4] = 0 if rpt[4][3] == 0 else (rpt[4][5] / rpt[4][3] )

				rpt[6][3] += cp_obj.calci_tt_ton
				rpt[6][5] += cp_obj.calci_tt_imp
				rpt[6][4] = 0 if rpt[6][3] == 0 else (rpt[6][5] / rpt[6][3] )


				rpt[8][3] += cp_obj.calci_ven_ton
				rpt[8][5] += cp_obj.calci_ven_imp
				rpt[8][4] = 0 if rpt[8][3] == 0 else (rpt[8][5] / rpt[8][3] )

				parametros = self.env['main.parameter'].search([])[0]
				tmp = []
		return rpt


