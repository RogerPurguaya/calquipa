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


def dig_5(n):
	return ("%5d" % n).replace(' ','0')


class consolidado_rm_resultado_mexicano_line(models.Model):
	_name = 'consolidado.rm.resultado.mexicano.line'

	orden = fields.Float('Orden',required=True)
	concepto = fields.Char('Concepto')
	tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta')
	#tipo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos FIjos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Tipo Cuenta',required=True)
	formula = fields.Char('Formula')
	total = fields.Char('Linea de Total')
	resaltado = fields.Boolean('Resaltado')
	bordes = fields.Boolean('Bordes')

	#monto_mes = fields.Float('Saldo',digits=(12,2))
	enero = fields.Float('Enero',digits=(12,2))
	febrero = fields.Float('Febrero',digits=(12,2))
	marzo = fields.Float('Marzo',digits=(12,2))
	abril = fields.Float('Abril',digits=(12,2))
	mayo = fields.Float('Mayo',digits=(12,2))
	junio = fields.Float('Junio',digits=(12,2))
	julio = fields.Float('Julio',digits=(12,2))
	agosto = fields.Float('Agosto',digits=(12,2))
	septiembre = fields.Float('Septiembre',digits=(12,2))
	octubre = fields.Float('Octubre',digits=(12,2))
	noviembre = fields.Float('Noviembre',digits=(12,2))
	diciembre = fields.Float('Diciembre',digits=(12,2))

	porc_enero = fields.Float('Porcentaje Enero',digits=(12,2))
	porc_febrero = fields.Float('Porcentaje Febrero',digits=(12,2))
	porc_marzo = fields.Float('Porcentaje Marzo',digits=(12,2))
	porc_abril = fields.Float('Porcentaje Abril',digits=(12,2))
	porc_mayo = fields.Float('Porcentaje Mayo',digits=(12,2))
	porc_junio = fields.Float('Porcentaje Junio',digits=(12,2))
	porc_julio = fields.Float('Porcentaje Julio',digits=(12,2))
	porc_agosto = fields.Float('Porcentaje Agosto',digits=(12,2))
	porc_septiembre = fields.Float('Porcentaje Septiembre',digits=(12,2))
	porc_octubre = fields.Float('Porcentaje Octubre',digits=(12,2))
	porc_noviembre = fields.Float('Porcentaje Noviembre',digits=(12,2))
	porc_diciembre = fields.Float('Porcentaje Diciembre',digits=(12,2))

	@api.one
	def get_acum_anio(self):
		self.acum_anio = self.enero + self.febrero + self.marzo + self.abril + self.mayo + self.junio + self.julio + self.agosto + self.septiembre + self.octubre + self.noviembre + self.diciembre


	@api.one
	def get_acum_porc(self):
		tmp = ((self.enero*100.0) / self.porc_enero)  if self.porc_enero != 0 else 0 
		tmp += ((self.febrero*100.0) / self.porc_febrero)  if self.porc_febrero != 0 else 0
		tmp += ((self.marzo*100.0) / self.porc_marzo)  if self.porc_marzo != 0 else 0
		tmp += ((self.abril*100.0) / self.porc_abril)  if self.porc_abril != 0 else 0
		tmp += ((self.mayo*100.0) / self.porc_mayo)  if self.porc_mayo != 0 else 0
		tmp += ((self.junio*100.0) / self.porc_junio)  if self.porc_junio != 0 else 0
		tmp += ((self.julio*100.0) / self.porc_julio)  if self.porc_julio != 0 else 0
		tmp += ((self.agosto*100.0) / self.porc_agosto)  if self.porc_agosto != 0 else 0
		tmp += ((self.septiembre*100.0) / self.porc_septiembre)  if self.porc_septiembre != 0 else 0
		tmp += ((self.octubre*100.0) / self.porc_octubre)  if self.porc_octubre != 0 else 0
		tmp += ((self.noviembre*100.0) / self.porc_noviembre)  if self.porc_noviembre != 0 else 0
		tmp += ((self.diciembre*100.0) / self.porc_diciembre)  if self.porc_diciembre != 0 else 0

		self.acum_porc = ( (self.acum_anio * 100.0) / tmp ) if tmp != 0 else 0


	acum_anio = fields.Float('Acumulado Soles',compute="get_acum_anio",digits=(12,2))
	acum_porc = fields.Float('Porcentaje Acumulado',compute="get_acum_porc",digits=(12,2))
	##porcentaje_mes


	padre = fields.Many2one('consolidado.rm.resultado.mexicano','Cabezera')




class consolidado_rm_resultado_mexicano(models.Model):
	_name= 'consolidado.rm.resultado.mexicano'

	fiscal_id = fields.Many2one('account.fiscalyear','Año Fiscal',required=True)
	periodo_ini = fields.Many2one('account.period','Periodo',required=True)
	tipo_cambio = fields.Float('Tipo Cambio',digits=(12,3))

	tipo_cambio1 = fields.Float('Tipo Cambio',digits=(12,3))
	tipo_cambio2 = fields.Float('Tipo Cambio',digits=(12,3))
	tipo_cambio3 = fields.Float('Tipo Cambio',digits=(12,3))
	tipo_cambio4 = fields.Float('Tipo Cambio',digits=(12,3))
	tipo_cambio5 = fields.Float('Tipo Cambio',digits=(12,3))
	tipo_cambio6 = fields.Float('Tipo Cambio',digits=(12,3))
	tipo_cambio7 = fields.Float('Tipo Cambio',digits=(12,3))
	tipo_cambio8 = fields.Float('Tipo Cambio',digits=(12,3))
	tipo_cambio9 = fields.Float('Tipo Cambio',digits=(12,3))
	tipo_cambio10 = fields.Float('Tipo Cambio',digits=(12,3))
	tipo_cambio11 = fields.Float('Tipo Cambio',digits=(12,3))
	tipo_cambio12 = fields.Float('Tipo Cambio',digits=(12,3))

	lineas = fields.One2many('consolidado.rm.resultado.mexicano.line','padre','Lineas')

	_rec_name = 'periodo_ini'


	@api.one
	def traer_datos(self):
		t_i = self.env['rm.resultado.config.mexicano.line'].search([])
		if len(t_i) >0 :
			pass
		else:
			raise osv.except_osv('Alerta!', "No hay plantilla configurada")

		for i in self.lineas:
			i.unlink()

		for i in t_i:
			vals = {
				'orden': i.orden, 
				'concepto' : i.concepto,
				'tipo_cuenta' :i.tipo_cuenta,
				'formula' :i.formula,
				'total' :i.total,
				'resaltado' :i.resaltado,
				'bordes' :i.bordes,
				'enero' :0,
				'febrero' :0,
				'marzo' :0,
				'abril' :0,
				'mayo' :0,
				'junio' :0,
				'julio' :0,
				'agosto' :0,
				'septiembre' :0,
				'octubre' :0,
				'noviembre' :0,
				'diciembre' :0,
				'porc_enero' :0,
				'porc_febrero' :0,
				'porc_marzo' :0,
				'porc_abril' :0,
				'porc_mayo' :0,
				'porc_junio' :0,
				'porc_julio' :0,
				'porc_agosto' :0,
				'porc_septiembre' :0,
				'porc_octubre' :0,
				'porc_noviembre' :0,
				'porc_diciembre' :0,
				'padre': self.id,
			}
			self.env['consolidado.rm.resultado.mexicano.line'].create(vals)


		self.refresh()



		period_list = []
		nro_act = 1
		period_act =  ("%2d"%nro_act).replace(' ','0') +  '/' + self.fiscal_id.name
		nro_act = 2
		mkmk = self.env['account.period'].search( [('code','=',period_act)] )
		if len(mkmk)>0:
			period_list.append(mkmk[0])

		while period_act != self.periodo_ini.code :
			period_act =  ("%2d"%nro_act).replace(' ','0') +  '/' + self.fiscal_id.name
			nro_act += 1
			mkmk = self.env['account.period'].search( [('code','=',period_act)] )
			if len(mkmk)>0:
				period_list.append(mkmk[0])

		for i in period_list:
			t = self.env['rm.resultado.mexicano'].search( [('periodo_fin','=',i.id)] )
			if len(t)>0:
				t = t[0]
				for line in self.lineas:
					for j in self.env['rm.resultado.mexicano.line'].search([('orden','=',line.orden),('padre','=',t.id),('concepto','=',line.concepto),('tipo_cuenta','=',line.tipo_cuenta)]):
						if i.code.split('/')[0] == '01':
							line.enero = j.monto_mes
							line.porc_enero = j.porcentaje_mes
							self.tipo_cambio1 = j.padre.tipo_cambio
						elif i.code.split('/')[0] == '02':
							line.febrero = j.monto_mes
							line.porc_febrero = j.porcentaje_mes
							self.tipo_cambio2 = j.padre.tipo_cambio
						elif i.code.split('/')[0] == '03':
							line.marzo = j.monto_mes
							line.porc_marzo = j.porcentaje_mes
							self.tipo_cambio3 = j.padre.tipo_cambio
						elif i.code.split('/')[0] == '04':
							line.abril = j.monto_mes
							line.porc_abril = j.porcentaje_mes
							self.tipo_cambio4 = j.padre.tipo_cambio
						elif i.code.split('/')[0] == '05':
							line.mayo = j.monto_mes
							line.porc_mayo = j.porcentaje_mes
							self.tipo_cambio5 = j.padre.tipo_cambio
						elif i.code.split('/')[0] == '06':
							line.junio = j.monto_mes
							line.porc_junio = j.porcentaje_mes
							self.tipo_cambio6 = j.padre.tipo_cambio
						elif i.code.split('/')[0] == '07':
							line.julio = j.monto_mes
							line.porc_julio = j.porcentaje_mes
							self.tipo_cambio7 = j.padre.tipo_cambio
						elif i.code.split('/')[0] == '08':
							line.agosto = j.monto_mes
							line.porc_agosto = j.porcentaje_mes
							self.tipo_cambio8 = j.padre.tipo_cambio
						elif i.code.split('/')[0] == '09':
							line.septiembre = j.monto_mes
							line.porc_septiembre = j.porcentaje_mes
							self.tipo_cambio9 = j.padre.tipo_cambio
						elif i.code.split('/')[0] == '10':
							line.octubre = j.monto_mes
							line.porc_octubre = j.porcentaje_mes
							self.tipo_cambio10 = j.padre.tipo_cambio
						elif i.code.split('/')[0] == '11':
							line.noviembre = j.monto_mes
							line.porc_noviembre = j.porcentaje_mes
							self.tipo_cambio11 = j.padre.tipo_cambio
						elif i.code.split('/')[0] == '12':
							line.diciembre = j.monto_mes
							line.porc_diciembre = j.porcentaje_mes
							self.tipo_cambio12 = j.padre.tipo_cambio


	""" ----------------------------- REPORTE EXCEL ----------------------------- """

	@api.multi
	def export_excel(self):
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

		workbook = Workbook(direccion +'Reporte_resultado_mexicano.xlsx')
		worksheet = workbook.add_worksheet(u"Consolidado Resultado")
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


		worksheet.insert_image('A2', 'calidra.jpg')
		worksheet.write(1,4, u'CALQUIPA {0}'.format(self.periodo_ini.code.split('/')[1]), bold)
		worksheet.write(3,4, 'Estado de Resultados', bold)
		worksheet.write(4,4, u'{0}'.format(self.periodo_ini.code.split('/')[1]), bold)
		
		titlees = workbook.add_format({'bold': True})
		titlees.set_align('center')
		titlees.set_align('vcenter')
		
		#worksheet.merge_range(6,0,7,0,u'Nombre', boldbord)

		worksheet.merge_range(6,1,6,3, u'T.C: ' + ("%0.3f"%self.tipo_cambio1), titlees)
		worksheet.merge_range(7,1,7,3, u'Enero', titlees)
		worksheet.write(8,1, u'Soles', titlees)
		worksheet.write(8,2, u'USD', titlees)
		worksheet.write(8,3, u'%', titlees)

		worksheet.merge_range(6,4,6,6, u'T.C: ' + ("%0.3f"%self.tipo_cambio2), titlees)
		worksheet.merge_range(7,4,7,6, u'Febrero', titlees)
		worksheet.write(8,4, u'Soles', titlees)
		worksheet.write(8,5, u'USD', titlees)
		worksheet.write(8,6, u'%', titlees)

		worksheet.merge_range(6,7,6,9, u'T.C: ' + ("%0.3f"%self.tipo_cambio3), titlees)
		worksheet.merge_range(7,7,7,9, u'Marzo', titlees)
		worksheet.write(8,7, u'Soles', titlees)
		worksheet.write(8,8, u'USD', titlees)
		worksheet.write(8,9, u'%', titlees)

		worksheet.merge_range(6,10,6,12, u'T.C: ' + ("%0.3f"%self.tipo_cambio4), titlees)
		worksheet.merge_range(7,10,7,12, u'Abril', titlees)
		worksheet.write(8,10, u'Soles', titlees)
		worksheet.write(8,11, u'USD', titlees)
		worksheet.write(8,12, u'%', titlees)

		worksheet.merge_range(6,13,6,15, u'T.C: ' + ("%0.3f"%self.tipo_cambio5), titlees)
		worksheet.merge_range(7,13,7,15, u'Mayo', titlees)
		worksheet.write(8,13, u'Soles', titlees)
		worksheet.write(8,14, u'USD', titlees)
		worksheet.write(8,15, u'%', titlees)

		worksheet.merge_range(6,16,6,18, u'T.C: ' + ("%0.3f"%self.tipo_cambio6), titlees)
		worksheet.merge_range(7,16,7,18, u'Junio', titlees)
		worksheet.write(8,16, u'Soles', titlees)
		worksheet.write(8,17, u'USD', titlees)
		worksheet.write(8,18, u'%', titlees)

		worksheet.merge_range(6,19,6,21, u'T.C: ' + ("%0.3f"%self.tipo_cambio7), titlees)
		worksheet.merge_range(7,19,7,21, u'Julio', titlees)
		worksheet.write(8,19, u'Soles', titlees)
		worksheet.write(8,20, u'USD', titlees)
		worksheet.write(8,21, u'%', titlees)

		worksheet.merge_range(6,22,6,24, u'T.C: ' + ("%0.3f"%self.tipo_cambio8), titlees)
		worksheet.merge_range(7,22,7,24, u'Agosto', titlees)
		worksheet.write(8,22, u'Soles', titlees)
		worksheet.write(8,23, u'USD', titlees)
		worksheet.write(8,24, u'%', titlees)

		worksheet.merge_range(6,25,6,27, u'T.C: ' + ("%0.3f"%self.tipo_cambio9), titlees)
		worksheet.merge_range(7,25,7,27, u'Septiembre', titlees)
		worksheet.write(8,25, u'Soles', titlees)
		worksheet.write(8,26, u'USD', titlees)
		worksheet.write(8,27, u'%', titlees)

		worksheet.merge_range(6,28,6,30, u'T.C: ' + ("%0.3f"%self.tipo_cambio10), titlees)
		worksheet.merge_range(7,28,7,30, u'Octubre', titlees)
		worksheet.write(8,28, u'Soles', titlees)
		worksheet.write(8,29, u'USD', titlees)
		worksheet.write(8,30, u'%', titlees)

		worksheet.merge_range(6,31,6,33, u'T.C: ' + ("%0.3f"%self.tipo_cambio11), titlees)
		worksheet.merge_range(7,31,7,33, u'Noviembre', titlees)
		worksheet.write(8,31, u'Soles', titlees)
		worksheet.write(8,32, u'USD', titlees)
		worksheet.write(8,33, u'%', titlees)

		worksheet.merge_range(6,34,6,36, u'T.C: ' + ("%0.3f"%self.tipo_cambio12), titlees)
		worksheet.merge_range(7,34,7,36, u'Diciembre', titlees)
		worksheet.write(8,34, u'Soles', titlees)
		worksheet.write(8,35, u'USD', titlees)
		worksheet.write(8,36, u'%', titlees)
				
		worksheet.merge_range(6,37,6,39, u'T.C: ' + ("%0.3f"%self.tipo_cambio), titlees)
		worksheet.merge_range(7,37,7,39, u'Acumulado', titlees)
		worksheet.write(8,37, u'Soles', titlees)
		worksheet.write(8,38, u'USD', titlees)
		worksheet.write(8,39, u'%', titlees)
				
		x = 9

		for i in self.env['consolidado.rm.resultado.mexicano.line'].search([('padre','=',self.id)]).sorted(lambda r : r.orden):
			if i.tipo_cuenta == '5':

				boldbordtmp = workbook.add_format({'bold': False})
				boldbordtmp.set_font_size(9)
				if i.resaltado:
					boldbordtmp = workbook.add_format({'bold': True})
					boldbordtmp.set_text_wrap()
					boldbordtmp.set_font_size(9)
				if i.bordes:
					boldbordtmp.set_border(style=2)
				worksheet.write(x,0, i.concepto if i.concepto else '',boldbordtmp)
				x+=1
			else:			
				boldbordtmp = workbook.add_format({'bold': False})
				boldbordtmp.set_font_size(9)
				boldbordtmpRight = workbook.add_format({'bold': False})
				boldbordtmpRight.set_font_size(9)
				boldbordtmpRight.set_align('right')
				boldbordtmpRight.set_align('vright')
				numberdostmp = workbook.add_format({'num_format':'#,##0.00'})
				numberdostmp.set_font_size(9)
				if i.resaltado:
					boldbordtmp = workbook.add_format({'bold': True})
					boldbordtmp.set_text_wrap()
					boldbordtmp.set_font_size(9)

					boldbordtmpRight = workbook.add_format({'bold': True})
					boldbordtmpRight.set_text_wrap()
					boldbordtmpRight.set_align('right')
					boldbordtmpRight.set_align('vright')
					boldbordtmpRight.set_font_size(9)

					numberdostmp = workbook.add_format({'bold': True})
					numberdostmp.set_text_wrap()
					numberdostmp.set_font_size(9)
				if i.bordes:
					boldbordtmp.set_border(style=2)
					numberdostmp.set_border(style=2)

					boldbordtmpRight.set_border(style=2)

				if True:
					worksheet.write(x,0, i.concepto if i.concepto else '',boldbordtmp)
					worksheet.write(x,1, i.enero ,numberdostmp)
					worksheet.write(x,2, i.enero / self.tipo_cambio1 if self.tipo_cambio1 != 0 else 0 ,numberdostmp)
					worksheet.write(x,3, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porc_enero)) +" %",boldbordtmpRight)
					
					worksheet.write(x,4, i.febrero ,numberdostmp)
					worksheet.write(x,5, i.febrero / self.tipo_cambio2  if self.tipo_cambio2 != 0 else 0  ,numberdostmp)
					worksheet.write(x,6, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porc_febrero)) +" %",boldbordtmpRight)
					
					worksheet.write(x,7, i.marzo ,numberdostmp)
					worksheet.write(x,8, i.marzo / self.tipo_cambio3  if self.tipo_cambio3 != 0 else 0  ,numberdostmp)
					worksheet.write(x,9, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porc_marzo)) +" %",boldbordtmpRight)
					
					worksheet.write(x,10, i.abril ,numberdostmp)
					worksheet.write(x,11, i.abril / self.tipo_cambio4  if self.tipo_cambio4 != 0 else 0  ,numberdostmp)
					worksheet.write(x,12, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porc_abril)) +" %",boldbordtmpRight)
					
					worksheet.write(x,13, i.mayo ,numberdostmp)
					worksheet.write(x,14, i.mayo / self.tipo_cambio5 if self.tipo_cambio5 != 0 else 0  ,numberdostmp)
					worksheet.write(x,15, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porc_mayo)) +" %",boldbordtmpRight)
					
					worksheet.write(x,16, i.junio ,numberdostmp)
					worksheet.write(x,17, i.junio / self.tipo_cambio6 if self.tipo_cambio6 != 0 else 0  ,numberdostmp)
					worksheet.write(x,18, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porc_junio)) +" %",boldbordtmpRight)
					
					worksheet.write(x,19, i.julio ,numberdostmp)
					worksheet.write(x,20, i.julio / self.tipo_cambio7 if self.tipo_cambio7 != 0 else 0  ,numberdostmp)
					worksheet.write(x,21, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porc_julio)) +" %",boldbordtmpRight)
					
					worksheet.write(x,22, i.agosto ,numberdostmp)
					worksheet.write(x,23, i.agosto / self.tipo_cambio8 if self.tipo_cambio8 != 0 else 0  ,numberdostmp)
					worksheet.write(x,24, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porc_agosto)) +" %",boldbordtmpRight)
					
					worksheet.write(x,25, i.septiembre ,numberdostmp)
					worksheet.write(x,26, i.septiembre / self.tipo_cambio9 if self.tipo_cambio9 != 0 else 0  ,numberdostmp)
					worksheet.write(x,27, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porc_septiembre)) +" %",boldbordtmpRight)
					
					worksheet.write(x,28, i.octubre ,numberdostmp)
					worksheet.write(x,29, i.octubre / self.tipo_cambio10 if self.tipo_cambio10 != 0 else 0  ,numberdostmp)
					worksheet.write(x,30, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porc_octubre)) +" %",boldbordtmpRight)
					
					worksheet.write(x,31, i.noviembre ,numberdostmp)
					worksheet.write(x,32, i.noviembre / self.tipo_cambio11  if self.tipo_cambio11 != 0 else 0 ,numberdostmp)
					worksheet.write(x,33, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porc_noviembre)) +" %",boldbordtmpRight)
					
					worksheet.write(x,34, i.diciembre ,numberdostmp)
					worksheet.write(x,35, i.diciembre / self.tipo_cambio12  if self.tipo_cambio12 != 0 else 0  ,numberdostmp)
					worksheet.write(x,36, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porc_diciembre)) +" %",boldbordtmpRight)
					
					worksheet.write(x,37, i.acum_anio ,numberdostmp)
					worksheet.write(x,38, i.acum_anio / self.tipo_cambio if self.tipo_cambio != 0 else 0  ,numberdostmp)
					worksheet.write(x,39, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.acum_porc)) +" %",boldbordtmpRight)


					x += 1

		t = 14.86
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
		worksheet.set_column('R:R', t)
		worksheet.set_column('S:S', t)
		worksheet.set_column('T:T', t)
		worksheet.set_column('U:U', t)
		worksheet.set_column('V:V', t)
		worksheet.set_column('W:W', t)
		worksheet.set_column('X:X', t)
		worksheet.set_column('Y:Y', t)
		worksheet.set_column('Z:Z', t)
		worksheet.set_column('AA:AA', t)
		worksheet.set_column('AB:AB', t)
		worksheet.set_column('AC:AC', t)
		worksheet.set_column('AD:AD', t)
		worksheet.set_column('AE:AE', t)
		worksheet.set_column('AF:AF', t)
		worksheet.set_column('AG:AG', t)
		worksheet.set_column('AH:AH', t)
		worksheet.set_column('AI:AI', t)
		worksheet.set_column('AJ:AJ', t)
		worksheet.set_column('AK:AK', t)
		worksheet.set_column('AL:AL', t)
		worksheet.set_column('AM:AM', t)
		worksheet.set_column('AN:AN', t)

		workbook.close()
		
		f = open(direccion + 'Reporte_resultado_mexicano.xlsx', 'rb')
		
		vals = {
			'output_name': 'Consolidado Mexicanos Resultado.xlsx',
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