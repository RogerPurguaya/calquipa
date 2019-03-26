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


class account_result_type_mex(models.Model):
	_name = 'account.result.type.mex'

	name = fields.Char('Concepto')
	tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',required=True)


class account_account(models.Model):
	_inherit = 'account.account'

	result_type_mex_id = fields.Many2one('rm.resultado.config.mexicano.line','Resultado Mexicano Grupo')
	


class rm_resultado_config_mexicano_line(models.Model):
	_name = 'rm.resultado.config.mexicano.line'

	orden = fields.Float('Orden',required=True)
	concepto = fields.Char('Concepto')
	tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta')
	tipo_cambio = fields.Selection([('1','Tipo Compra Cierre'),('2','Tipo Venta Cierre'),('3','Tipo Promedio Compras'),('4','Tipo Promedio Ventas'),('5','Cédula')],'Tipo de Cambio',required=True, default="1")	
	
	#tipo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos FIjos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Tipo Cuenta',required=True)
	formula = fields.Char('Formula')
	total = fields.Char('Linea de Total')
	resaltado = fields.Boolean('Resaltado')
	bordes = fields.Boolean('Bordes')

	monto_mes = fields.Float('Saldo',digits=(12,2))
	porcentaje_mes = fields.Float('Saldo Porcentaje',digits=(12,2))

	monto_actual = fields.Float('Año Actual',digits=(12,2))
	porcentaje_actual = fields.Float('Saldo Porcentaje Año Actual',digits=(12,2))

	monto_anterior = fields.Float('Año Anterior',digits=(12,2))
	porcentaje_anterior = fields.Float('Saldo Porcentaje Año Anterior',digits=(12,2))

	check_change_value= fields.Boolean('Cambiar Signo')

	padre = fields.Many2one('rm.resultado.config.mexicano','Cabezera')

	_rec_name = 'concepto'


class rm_resultado_mexicano_line(models.Model):
	_name = 'rm.resultado.mexicano.line'

	orden = fields.Float('Orden',required=True)
	concepto = fields.Char('Concepto')
	tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta')
	#tipo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos FIjos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Tipo Cuenta',required=True)
	formula = fields.Char('Formula')
	total = fields.Char('Linea de Total')
	resaltado = fields.Boolean('Resaltado')
	bordes = fields.Boolean('Bordes')

	monto_mes = fields.Float('Monto',digits=(12,2))
	porcentaje_mes = fields.Float('Saldo Porcentaje',digits=(12,2))

	monto_actual = fields.Float('Año Actual',digits=(12,2))
	porcentaje_actual = fields.Float('Saldo Porcentaje Año Actual',digits=(12,2))

	monto_anterior = fields.Float('Año Anterior',digits=(12,2))
	porcentaje_anterior = fields.Float('Saldo Porcentaje Año Anterior',digits=(12,2))

	check_change_value= fields.Boolean('Cambiar Signo')
	padre = fields.Many2one('rm.resultado.mexicano','Cabezera')


	@api.one
	def calculo_prog_mes(self,orden):
		calculo = 0
		for i in self.env['rm.resultado.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			calculo += i.monto_mes
			print '1',i.concepto,calculo, i.monto_mes
		print '2',calculo
		return calculo

	@api.one
	def calculo_prog_actual(self,orden):
		calculo = 0
		for i in self.env['rm.resultado.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			calculo += i.monto_actual
		return calculo

	@api.one
	def calculo_prog_anterior(self,orden):
		calculo = 0
		for i in self.env['rm.resultado.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			calculo += i.monto_anterior
		return calculo



class rm_resultado_config_mexicano(models.Model):
	_name= 'rm.resultado.config.mexicano'

	name = fields.Char('Nombre',default='Plantilla Resultado')
	lineas = fields.One2many('rm.resultado.config.mexicano.line','padre','Lineas')

	_rec_name = 'name'


class rm_resultado_mexicano(models.Model):
	_name= 'rm.resultado.mexicano'

	periodo_ini = fields.Many2one('account.period','Periodo Inicial',required=True)
	periodo_fin = fields.Many2one('account.period','Periodo',required=True)
	
	periodo_ini_ant = fields.Many2one('account.period','Periodo Anterior Inicial',required=True)
	periodo_fin_ant = fields.Many2one('account.period','Periodo Anterior Final',required=True)

	tipo_cambio = fields.Float('Tipo Cambio',digits=(12,3))
	lineas = fields.One2many('rm.resultado.mexicano.line','padre','Lineas')

	_rec_name = 'periodo_fin'

	@api.onchange('periodo_fin')
	def onchange_periodo_fin(self):
		self.periodo_ini = self.periodo_fin.id
		self.periodo_ini_ant = self.periodo_fin.id
		self.periodo_fin_ant = self.periodo_fin.id

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
				'monto_mes' :i.monto_mes,
				'porcentaje_mes' :i.porcentaje_mes,
				'monto_actual' :i.monto_actual,
				'porcentaje_actual' :i.porcentaje_actual,
				'monto_anterior' :i.monto_anterior,
				'porcentaje_anterior' :i.porcentaje_anterior,
				'check_change_value' : i.check_change_value,
				'padre': self.id,
			}
			self.env['rm.resultado.mexicano.line'].create(vals)


	@api.one
	def calculate(self):

		for i in self.lineas:
			if i.tipo_cuenta == '1' or i.tipo_cuenta == '2':
				i.monto_mes= 0
				i.porcentaje_mes= 0
				i.monto_actual = 0
				i.porcentaje_actual = 0
				i.monto_anterior= 0
				i.porcentaje_anterior = 0

		self.env.cr.execute("""

			update rm_resultado_mexicano_line
set monto_mes= T1.monto
from ( 
select rrcml.id, rrcml.concepto , sum(M.debe - M.haber) as monto
from get_hoja_trabajo_detalle(false,periodo_num_i('""" + self.periodo_fin.code + """'),periodo_num_i('""" + self.periodo_fin.code + """')) as M
inner join account_account aa ON aa.code = cuentaactual
left join account_account_type aat on aat.id = aa.user_type
left join rm_resultado_config_mexicano_line rrcml on rrcml.id = aa.result_type_mex_id
where rrcml.tipo_cuenta = '1' or rrcml.tipo_cuenta = '2'
group by rrcml.id, rrcml.concepto
) T1
where rm_resultado_mexicano_line.concepto = T1.concepto
and rm_resultado_mexicano_line.padre = """ + str(self.id) + """
			""")

		self.env.cr.execute("""
			update rm_resultado_mexicano_line
set monto_actual= T1.monto
from ( 
select rrcml.id, rrcml.concepto , sum(M.debe - M.haber) as monto
from get_hoja_trabajo_detalle(false,periodo_num_i('""" + self.periodo_ini.code + """'),periodo_num_i('""" + self.periodo_fin.code + """')) as M
inner join account_account aa ON aa.code = cuentaactual
left join account_account_type aat on aat.id = aa.user_type
left join rm_resultado_config_mexicano_line rrcml on rrcml.id = aa.result_type_mex_id
where rrcml.tipo_cuenta = '1' or rrcml.tipo_cuenta = '2'
group by rrcml.id, rrcml.concepto
) T1
where rm_resultado_mexicano_line.concepto = T1.concepto
and rm_resultado_mexicano_line.padre = """ + str(self.id) + """


			""")



		self.env.cr.execute("""

			update rm_resultado_mexicano_line
set monto_anterior= T1.monto
from ( 
select rrcml.id, rrcml.concepto , sum(M.debe - M.haber) as monto
from get_hoja_trabajo_detalle(false,periodo_num_i('""" + self.periodo_ini_ant.code + """'),periodo_num_i('""" + self.periodo_fin_ant.code + """')) as M
inner join account_account aa ON aa.code = cuentaactual
left join account_account_type aat on aat.id = aa.user_type
left join rm_resultado_config_mexicano_line rrcml on rrcml.id = aa.result_type_mex_id
where rrcml.tipo_cuenta = '1' or rrcml.tipo_cuenta = '2'
group by rrcml.id, rrcml.concepto
) T1
where rm_resultado_mexicano_line.concepto = T1.concepto
and rm_resultado_mexicano_line.padre = """ + str(self.id) + """

			""")
		for i in self.lineas:
			i.refresh()

		for i in self.env['rm.resultado.mexicano.line'].search([('tipo_cuenta','=','3'),('padre','=',self.id)]):
			val = 0
			try:
				print "val = " + i.formula.replace('L[','i.calculo_prog_mes(').replace(']',')[0]') 
				exec("val = " + i.formula.replace('L[','i.calculo_prog_mes(').replace(']',')[0]'))
			except:
				pass

			print val
			i.monto_mes = val

			val = 0
			try:
				exec("val = " + i.formula.replace('L[','i.calculo_prog_actual(').replace(']',')[0]'))
			except:
				pass

			i.monto_actual = val

			val = 0
			try:
				exec("val = " + i.formula.replace('L[','i.calculo_prog_anterior(').replace(']',')[0]'))
			except:
				pass

			i.monto_anterior = val



		for i in self.env['rm.resultado.mexicano.line'].search([('tipo_cuenta','!=','5'),('padre','=',self.id)]):
			val = 0
			try:
				exec("val = " + i.total.replace('L[','i.calculo_prog_mes(').replace(']',')[0]'))
			except:
				pass
			if val== 0:
				i.porcentaje_mes = 0
			else:
				i.porcentaje_mes = (i.monto_mes/val) *100.0

			val = 0
			try:
				exec("val = " + i.total.replace('L[','i.calculo_prog_actual(').replace(']',')[0]'))
			except:
				pass
			if val== 0:
				i.porcentaje_actual = 0
			else:
				i.porcentaje_actual = (i.monto_actual/val) *100.0

			val = 0
			try:
				exec("val = " + i.total.replace('L[','i.calculo_prog_anterior(').replace(']',')[0]'))
			except:
				pass
			if val== 0:
				i.porcentaje_anterior = 0
			else:
				i.porcentaje_anterior = (i.monto_anterior/val) *100.0
		
		for i in self.lineas:
			if i.check_change_value == True:
				i.monto_anterior= -i.monto_anterior
				i.monto_actual = -i.monto_actual
				i.monto_mes = -i.monto_mes
				i.porcentaje_anterior  = -i.porcentaje_anterior
				i.porcentaje_actual = -i.porcentaje_actual
				i.porcentaje_mes = -i.porcentaje_mes


	""" ----------------------------- REPORTE PDF ----------------------------- """

	@api.multi
	def export_pdf(self):
		self.reporteador()
		
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		import os
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		vals = {
			'output_name': 'Reportes Mexicanos Resultado.pdf',
			'output_file': open(direccion + "a.pdf", "rb").read().encode("base64"),	
		}
		sfs_id = self.env['export.file.save'].create(vals)
		return {
			"type": "ir.actions.act_window",
			"res_model": "export.file.save",
			"views": [[False, "form"]],
			"res_id": sfs_id.id,
			"target": "new",
		}

	@api.multi
	def cabezera(self,c,wReal,hReal):
		pagina = 1
		adicional = 10
		pos_inicial = hReal-30

		c.drawImage( 'calquipa.jpg' , 70 ,pos_inicial-60,width=214, height=131)
		c.setFont("Arimo-Bold", 20)
		c.setFillColor(black)
		c.drawString( 404 + adicional, pos_inicial, "CALQUIPA " + self.periodo_ini.code.split('/')[1])
		c.setFont("Arimo-Bold", 11)
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,30,pagina)
		c.drawString( 404 + adicional, pos_inicial, "Estado de Resultados")
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)
		c.drawString( 404 + adicional, pos_inicial, self.periodo_ini.code.split('/')[1] )
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,55,pagina)



		#c.setStrokeColor(black)
		#c.setFillColor("#CCCCFF")
		#c.rect(0+adicional, pos_inicial, 810 , 30, stroke=1, fill=1)

		#c.line(200 + adicional, pos_inicial, 200 + adicional , pos_inicial + 30)
		#c.line(315 + adicional, pos_inicial, 315 + adicional , pos_inicial + 15)
		#c.line(365 + adicional, pos_inicial, 365 + adicional , pos_inicial + 30)
		#c.line(480 + adicional, pos_inicial, 480 + adicional , pos_inicial + 15)
		#c.line(530 + adicional, pos_inicial, 530 + adicional , pos_inicial + 15)
		#c.line(645 + adicional, pos_inicial, 645 + adicional , pos_inicial + 15)
		#c.line(695 + adicional, pos_inicial, 695 + adicional , pos_inicial + 30)
		#c.line(200 + adicional, pos_inicial+15, 810 - 115 + adicional , pos_inicial + 15)

		c.setFillColor(black)
		c.setFont("Arimo-BoldItalic", 9)
		#c.drawCentredString(100 + adicional,pos_inicial + 15, u"Nombre")
		c.drawCentredString(400+200 + 82 + adicional,pos_inicial + 15, u"Monto")
		#c.drawCentredString(200 + 57 + adicional,pos_inicial + 5, u"Saldo")
		#c.drawCentredString(200 + 140 + adicional,pos_inicial + 5, u"%")
		#c.drawCentredString(200 + 165 + 165 + adicional,pos_inicial + 20, u"Acumulado")
		####c.drawCentredString(200 + 165 + 100 + adicional,pos_inicial + 15, u"Año Actual")
		#c.drawCentredString(200 + 165 + 140 + adicional,pos_inicial + 5, u"%")
		####c.drawCentredString(200 + 165 + 165 + 100 + adicional,pos_inicial + 15, u"Año Anterior")
		#c.drawCentredString(200 + 165 + 165 + 140 +adicional,pos_inicial + 5, u"%")
		#c.drawCentredString(200 + 165 + 165 + 165 + 57 +adicional,pos_inicial + 15, u"variación")

		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,15,pagina)
		#c.drawCentredString((wReal/2)+20,hReal, self.env["res.company"].search([])[0].name.upper())
		#c.drawCentredString((wReal/2)+20,hReal-96, "LIQUIDACION DE BENEFICIOS SOCIALES")



	@api.multi
	def reporteador(self):

		import sys

		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		width , height = A4  # 595 , 842

		#print legal
		wReal = height- 30
		hReal = width - 40

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		c = canvas.Canvas( direccion + "a.pdf", pagesize=(height, width))


		pdfmetrics.registerFont(TTFont('Arimo-Bold', 'Arimo-Bold.ttf'))
		pdfmetrics.registerFont(TTFont('Arimo-BoldItalic', 'Arimo-BoldItalic.ttf'))
		pdfmetrics.registerFont(TTFont('Arimo-Italic', 'Arimo-Italic.ttf'))
		pdfmetrics.registerFont(TTFont('Arimo-Regular', 'Arimo-Regular.ttf'))



		inicio = 0
		pos_inicial = hReal-132

		pagina = 1
		textPos = 0

		adicional = 10

		
		self.cabezera(c,wReal,hReal)			
		


		for i in self.env['rm.resultado.mexicano.line'].search([('padre','=',self.id)]).sorted(lambda r : r.orden):

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)
			if i.resaltado:
				c.setFont("Arimo-Bold", 8)
			else:
				c.setFont("Arimo-Regular", 8)

			if i.tipo_cuenta == '5':
				c.drawString( adicional + 52 , pos_inicial, i.concepto if i.concepto else '' )				
			else:			
				c.drawString( adicional + 52 , pos_inicial, i.concepto if i.concepto else '' )
				c.drawRightString( adicional + 400+ 200 + 115 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.monto_mes)) )
				#c.drawRightString( adicional + 200 + 115 + 50 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porcentaje_mes)) +" %" )

				#c.drawRightString( adicional + 200 + 280 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.monto_actual)) )
				#c.drawRightString( adicional + 200 + 280 + 50 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porcentaje_actual)) +" %" )

				#c.drawRightString( adicional + 200 + 445 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.monto_anterior)) )
				#c.drawRightString( adicional + 200 + 445 + 50 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porcentaje_anterior)) +" %" )

				#c.drawRightString( adicional + 200 + 495 + 115 -  2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (i.monto_actual - i.monto_anterior) )) )
				

			tamanios_x = [80,120, 80, 90, 50,60,60,25]

			if i.bordes:
				c.line( adicional + 400+200, pos_inicial-2, adicional + 715 ,pos_inicial-2)
				c.line( adicional + 400+200, pos_inicial-5, adicional + 715 ,pos_inicial-5)
				c.line( adicional + 400+200, pos_inicial+9, adicional + 715 ,pos_inicial+9)
		
		c.save()

	@api.multi
	def particionar_text(self,c):
		tet = ""
		for i in range(len(c)):
			tet += c[i]
			lines = simpleSplit(tet,'Arimo-Regular',9,160)
			if len(lines)>1:
				return tet[:-1]
		return tet

	@api.multi
	def verify_linea(self,c,wReal,hReal,posactual,valor,pagina):
		if posactual <40:
			c.showPage()
			self.cabezera(c,wReal,hReal)

			c.setFont("Arimo-Bold", 10)
			#c.drawCentredString(300,25,'Pag. ' + str(pagina+1))
			return pagina+1,hReal-132
		else:
			return pagina,posactual-valor

	""" ----------------------------- REPORTE PDF ----------------------------- """

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
		worksheet = workbook.add_worksheet(u"Resultado")
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


		worksheet.insert_image('A1', 'calidra.jpg')
		worksheet.write(1,1, u'CALQUIPA {0}'.format(self.periodo_ini.code.split('/')[1]), bold)
		worksheet.write(3,1, 'Estado de Resultados', bold)
		worksheet.write(4,1, u'{0}'.format(self.periodo_ini.code.split('/')[1]), bold)
		
		titlees = workbook.add_format({'bold': True})
		titlees.set_align('center')
		titlees.set_align('vcenter')
		
		#worksheet.merge_range(6,0,7,0,u'Nombre', boldbord)

		#worksheet.merge_range(6,1,6,2, u'Monto', titlees)
		worksheet.write(6,1, u'Monto', boldbord)
		#worksheet.write(7,2, u'%', boldbord)
		#worksheet.merge_range(6,3,6,6, u'Acumulado', boldbord)
		#####worksheet.merge_range(6,3,6,4, u'Año Actual', titlees)
		#worksheet.write(7,4, u'%', boldbord)
		#####worksheet.merge_range(6,5,6,6, u'Año Anterior', titlees)
		#worksheet.write(7,6, u'%', boldbord)
		#worksheet.merge_range(6,7,7,7, u'Variacion', boldbord)
				
		x = 8

		for i in self.env['rm.resultado.mexicano.line'].search([('padre','=',self.id)]).sorted(lambda r : r.orden):
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

				x += 1
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
					worksheet.write(x,1, i.monto_mes ,numberdostmp)
					#worksheet.write(x,2, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porcentaje_mes)) +" %",boldbordtmpRight)
					#worksheet.write(x,3, i.monto_actual,numberdostmp)
					#worksheet.write(x,4, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porcentaje_actual)) +" %",boldbordtmpRight)
					#worksheet.write(x,5, i.monto_anterior ,numberdostmp)
					#worksheet.write(x,6, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.porcentaje_anterior)) +" %",boldbordtmpRight)
					#worksheet.write(x,7, i.monto_actual-i.monto_anterior ,numberdostmp)

					x += 1

		t = 14.86
		worksheet.set_column('A:A', 120)
		worksheet.set_column('B:B', 20)
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

		workbook.close()
		
		f = open(direccion + 'Reporte_resultado_mexicano.xlsx', 'rb')
		
		vals = {
			'output_name': 'Reportes Mexicanos Resultado.xlsx',
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