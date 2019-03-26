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



class rm_er_mexicano_line(models.Model):
	_name = 'rm.er.mexicano.line'



	@api.one
	def get_t_monto(self):
		self.t_monto = self.monto + self.reclasif

	@api.one
	def get_t_monto_ifrs(self):
		self.t_monto_ifrs = self.t_monto + self.reclasif_ifrs


	@api.one
	def get_ajuste(self):
		self.ajuste = self.t_monto_ifrs - self.monto_usd

	@api.one
	def get_tc_usd(self):
		if self.monto_usd == 0:
			self.tc_usd = 0
		else:
			self.tc_usd = self.t_monto_ifrs / self.monto_usd

	@api.one
	def get_ajuste_usd(self):
		self.ajuste_usd = self.monto_mxn - self.monto_usd

	@api.one
	def get_tc_mxn(self):
		if self.monto_usd == 0:
			self.tc_mxn = 0
		else:
			self.tc_mxn = self.monto_mxn / self.monto_usd


	@api.one
	def get_monto_usd(self):
		if self.tipo_cuenta == '3' and self.resaltado and self.bordes:

			val = 0
			print "calculando: ", self.concepto
			try:
				exec("val = " + self.formula.replace('L[','self.calculo_prog_mesD_Ori(').replace(']',')[0]'))
			except:
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ self.formula )
			print "valor: ",val, -1 if self.check_change_value else 1
			self.monto_usd = val * (-1 if self.check_change_value else 1)


		elif not self.tipo_cambio:
			self.monto_usd = 0

		else:
			periodo_padre = self.padre.periodo_id.id
			tipo_obj = self.env['tipo.cambio.mexicano'].search([('periodo_id','=',periodo_padre)])
			if len(tipo_obj)>0:
				tipo_obj = tipo_obj[0]
				tmp_m = 1
				if self.tipo_cambio == '1':
					tmp_m = tipo_obj.t_cambio_compra
				if self.tipo_cambio == '2':
					tmp_m = tipo_obj.t_cambio_venta
				if self.tipo_cambio == '3':
					tmp_m = tipo_obj.promedio_compra
				if self.tipo_cambio == '4':
					tmp_m = tipo_obj.promedio_venta

				self.monto_usd = self.t_monto_ifrs /  ( tmp_m )


				if self.tipo_cambio == '5':
					linea_aa = self.env['rm.resultado.config.mexicano.line'].search([('concepto','=',self.concepto)])
					if len(linea_aa)>0:
						linea_aa = linea_aa[0]
						padre = self.padre.periodo_id.id
						activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
						if len(activofijo) >0:
							resumen_activo_fijo = self.env['resumen.activo.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
							if len(resumen_activo_fijo)>0:
								self.monto_usd = resumen_activo_fijo[0].monto_usd  
							else:
								self.monto_usd = 0
						else:
							self.monto_usd = 0
					else:
						self.monto_usd = 0

				if self.tipo_cambio == '6':
					
					linea_aa = self.env['rm.resultado.config.mexicano.line'].search([('concepto','=',self.concepto)])
					if len(linea_aa)>0:
						linea_aa = linea_aa[0]
						padre = self.padre.periodo_id.id
						activofijo = self.env['reporte.patrimonio'].search([('name','=',padre)])
						if len(activofijo) >0:
							resumen_activo_fijo = self.env['resumen.patrimonio.line'].search([('patrimonio_id','=',activofijo[0].id),('partida','=',linea_aa.orden)])
							if len(resumen_activo_fijo)>0:
								self.monto_usd = resumen_activo_fijo[0].dlls  
							else:
								self.monto_usd = 0
						else:
							self.monto_usd = 0
					else:
						self.monto_usd = 0

				if self.tipo_cambio == '7':
					linea_aa = self.env['rm.resultado.config.mexicano.line'].search([('concepto','=',self.concepto)])
					if len(linea_aa)>0:
						linea_aa = linea_aa[0]
						padre = self.padre.periodo_id.id
						activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
						if len(activofijo) >0:
							resumen_activo_fijo = self.env['resumen.depre.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
							if len(resumen_activo_fijo)>0:
								self.monto_usd = resumen_activo_fijo[0].monto_usd  
							else:
								self.monto_usd = 0
						else:
							self.monto_usd = 0
					else:
						self.monto_usd = 0
			else:
				self.monto_usd = 0


	@api.one
	def get_monto_mxn(self):
		if self.tipo_cuenta == '3'  and self.resaltado and self.bordes:


			val = 0
			try:
				exec("val = " + self.formula.replace('L[','self.calculo_prog_mesM_Ori(').replace(']',')[0]'))
			except:
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ self.formula )

			self.monto_mxn = val * (-1 if self.check_change_value else 1)

		elif not self.tipo_cambio:
			self.monto_mxn = 0

		else:
			periodo_padre = self.padre.periodo_id.id
			tipo_obj = self.env['tipo.cambio.mexicano'].search([('periodo_id','=',periodo_padre)])
			if len(tipo_obj)>0:
				tipo_obj = tipo_obj[0]
				tmp_m = 1
				if self.tipo_cambio == '1':
					tmp_m = tipo_obj.t_cambio_mexicano
				if self.tipo_cambio == '2':
					tmp_m = tipo_obj.t_cambio_mexicano
				if self.tipo_cambio == '3':
					tmp_m = tipo_obj.t_cambio_mexicano
				if self.tipo_cambio == '4':
					tmp_m = tipo_obj.t_cambio_mexicano

				self.monto_mxn = self.monto_usd * ( tmp_m )


				if self.tipo_cambio == '5':
					linea_aa = self.env['rm.resultado.config.mexicano.line'].search([('concepto','=',self.concepto)])
					if len(linea_aa)>0:
						linea_aa = linea_aa[0]
						padre = self.padre.periodo_id.id
						activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
						if len(activofijo) >0:
							resumen_activo_fijo = self.env['resumen.activo.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
							if len(resumen_activo_fijo)>0:
								self.monto_mxn = resumen_activo_fijo[0].pesos  
							else:
								self.monto_mxn = 0
						else:
							self.monto_mxn = 0
					else:
						self.monto_mxn = 0

				if self.tipo_cambio == '6':
					
					linea_aa = self.env['rm.resultado.config.mexicano.line'].search([('concepto','=',self.concepto)])
					if len(linea_aa)>0:
						linea_aa = linea_aa[0]
						padre = self.padre.periodo_id.id
						activofijo = self.env['reporte.patrimonio'].search([('name','=',padre)])
						if len(activofijo) >0:
							resumen_activo_fijo = self.env['resumen.patrimonio.line'].search([('patrimonio_id','=',activofijo[0].id),('partida','=',linea_aa.orden)])
							if len(resumen_activo_fijo)>0:
								self.monto_mxn = resumen_activo_fijo[0].valor_mxn  
							else:
								self.monto_mxn = 0
						else:
							self.monto_mxn = 0
					else:
						self.monto_mxn = 0

				if self.tipo_cambio == '7':
					linea_aa = self.env['rm.resultado.config.mexicano.line'].search([('concepto','=',self.concepto)])
					if len(linea_aa)>0:
						linea_aa = linea_aa[0]
						padre = self.padre.periodo_id.id
						activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
						if len(activofijo) >0:
							resumen_activo_fijo = self.env['resumen.depre.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
							if len(resumen_activo_fijo)>0:
								self.monto_mxn = resumen_activo_fijo[0].pesos  
							else:
								self.monto_mxn = 0
						else:
							self.monto_mxn = 0
					else:
						self.monto_mxn = 0
			else:
				self.monto_mxn = 0


	orden = fields.Float('Orden',required=True)
	concepto = fields.Char('Concepto')
	tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta')
	tipo_cambio = fields.Selection([('1','Tipo Compra Cierre'),('2','Tipo Venta Cierre'),('3','Tipo Promedio Compras'),('4','Tipo Promedio Ventas'),('5','Activo Fijo-Cédula'),('6','Patrimonio-Cédula'),('7','Depreciacion-Cédula')],'Tipo de Cambio',required=False, default="1")	
	formula = fields.Char('Formula')
	total = fields.Char('Linea de Total')
	resaltado = fields.Boolean('Resaltado')
	bordes = fields.Boolean('Bordes')

	monto = fields.Float('Saldo',digits=(12,2))
	reclasif = fields.Float('Reclasif. +/-',digits=(12,2))
	ref = fields.Integer('Ref')
	t_monto = fields.Float('Monto Soles',compute="get_t_monto",digits=(12,2))
	reclasif_ifrs = fields.Float('Reclasifc. IFRS',digits=(12,2))
	t_monto_ifrs = fields.Float('Monto Soles IFRS',compute="get_t_monto_ifrs",digits=(12,2))
	ajuste = fields.Float('Ajuste +/-',compute="get_ajuste",digits=(12,2))
	tc_usd = fields.Float('T.C. SOL vs USD',compute="get_tc_usd", digits=(12,3))
	monto_usd = fields.Float('Monto USD',digits=(12,2))
	ajuste_usd = fields.Float('Ajuste +/-',compute="get_ajuste_usd",digits=(12,2))
	tc_mxn = fields.Float('T.C. USD vs MXN',compute="get_tc_mxn",digits=(12,3))
	monto_mxn = fields.Float('Monto MXN',digits=(12,2))

	check_change_value = fields.Boolean('Cambiar Valor')
	padre = fields.Many2one('rm.er.mexicano','Cabezera')


	@api.one
	def calculo_prog_mes(self,orden):
		calculo = 0
		for i in self.env['rm.er.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			calculo += i.monto
		return calculo



	@api.one
	def calculo_prog_mesM(self,orden):
		calculo = 0
		for i in self.env['rm.er.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			calculo += i.monto_mxn
		return calculo



	@api.one
	def calculo_prog_mesD(self,orden):
		calculo = 0
		for i in self.env['rm.er.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			calculo += i.monto_usd
		if orden == 7.1:
			t = open('E:/OdooFiles/aqui.txt','w')
			t.write(str(calculo) + ',' + str(self.env['rm.er.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)])) + ', ' + str(self.env['rm.er.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)])[0].monto_usd)  )
			t.write(',')
			padre = self.padre
			for i in padre.lineas:
				if i.orden == 7.1:
					t.write(str(calculo)+ '\n' )
			t.close()
		return calculo


	@api.one
	def calculo_prog_mesM_Ori(self,orden):
		calculo = 0
		for i in self.env['rm.er.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			
			calculo += i.monto_mxn * (-1 if i.check_change_value else 1)
		return calculo

	@api.one
	def calculo_prog_mesD_Ori(self,orden):
		calculo = 0
		for i in self.env['rm.er.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			print "linea: ",i.concepto, i.monto_usd,-1 if i.check_change_value else 1
			calculo += i.monto_usd * (-1 if i.check_change_value else 1)
		return calculo


class rm_er_mexicano(models.Model):
	_name= 'rm.er.mexicano'


	@api.one
	def get_t_cambio_compra(self):
		j = self.env['tipo.cambio.mexicano'].search([('periodo_id','=',self.periodo_id.id)])
		if len(j)==0:
			self.t_cambio_compra= 0
		else:
			self.t_cambio_compra = j[0].t_cambio_compra

	@api.one
	def get_t_cambio_venta(self):
		j = self.env['tipo.cambio.mexicano'].search([('periodo_id','=',self.periodo_id.id)])
		if len(j)==0:
			self.t_cambio_venta= 0
		else:
			self.t_cambio_venta = j[0].t_cambio_venta

	@api.one
	def get_t_cambio_mexicano(self):
		j = self.env['tipo.cambio.mexicano'].search([('periodo_id','=',self.periodo_id.id)])
		if len(j)==0:
			self.t_cambio_mexicano= 0
		else:
			self.t_cambio_mexicano = j[0].t_cambio_mexicano


	periodo_id = fields.Many2one('account.period','Periodo Actual',required=True)

	t_cambio_compra = fields.Float('T. Cambio Compra',compute="get_t_cambio_compra",digits=(12,3))
	t_cambio_venta = fields.Float('T. Cambio Venta',compute="get_t_cambio_venta",digits=(12,3))
	t_cambio_mexicano = fields.Float('T. Cambio Mexicano',compute="get_t_cambio_mexicano",digits=(12,3))

	periodo_id = fields.Many2one('account.period','Periodo',required=True)
	
	lineas = fields.One2many('rm.er.mexicano.line','padre','Lineas')

	_rec_name = 'periodo_id'


	@api.one
	def eliminar_ceros(self):
		for i in self.lineas:
			if i.monto == 0:
				i.unlink()

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
				'monto' :i.monto_mes,
				'tipo_cambio':i.tipo_cambio,
				'check_change_value': i.check_change_value,
				'padre': self.id,
			}
			self.env['rm.er.mexicano.line'].create(vals)

	@api.one
	def actualizar(self):
		for i in self.lineas.sorted(lambda r : r.orden):
			i.get_monto_usd()
			i.refresh()
			i.get_monto_mxn()
			i.refresh()

	@api.one
	def calculate(self):

		for i in self.lineas:
			if i.tipo_cuenta == '1' or i.tipo_cuenta == '2':
				i.monto= 0

		for i in self.lineas:
			t_t = self.env['rm.resultado.mexicano.line'].search([('concepto','=',i.concepto),('padre.periodo_fin','=',self.periodo_id.id),('tipo_cuenta','=',i.tipo_cuenta)])
			if len(t_t)>0:
				t_t = t_t[0]
				i.monto = t_t.monto_mes

		for i in self.lineas:
			i.refresh()

	

		#for i in self.env['rm.er.mexicano.line'].search([('tipo_cuenta','=','3'),('padre','=',self.id)]).sorted(lambda r: r.orden):
		#	val = 0
		#	try:
		#		print "val = " + i.formula.replace('L[','i.calculo_prog_mes(').replace(']',')[0]') 
		#		exec("val = " + i.formula.replace('L[','i.calculo_prog_mes(').replace(']',')[0]'))
		#	except:
		#		raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.formula )

		#	print val
		#	i.monto = val

	""" ----------------------------- REPORTE EXCEL ----------------------------- """

	@api.multi
	def export_excel(self):
		import io
		from xlsxwriter.workbook import Workbook
		from xlsxwriter.utility import xl_rowcol_to_cell

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
		worksheet = workbook.add_worksheet(u"Reporte de Resultado")
		worksheet3 = workbook.add_worksheet(u"Resultado Acumulado")
		worksheet_2 = workbook.add_worksheet(u"Detalle de Estado de Resultado")
		bold = workbook.add_format({'bold': True})
		boldtop = workbook.add_format({'bold': True,'top':1})
		boldbot = workbook.add_format({'bold': True,'bottom':1})

		boldcenter = workbook.add_format({'bold': True})
		boldcenter.set_align('center')
		boldcenter.set_align('vcenter')

		boldcentertop = workbook.add_format({'bold': True,'top':1})
		boldcentertop.set_align('center')
		boldcentertop.set_align('vcenter')

		boldcenterbot = workbook.add_format({'bold': True,'bottom':1})
		boldcenterbot.set_align('center')
		boldcenterbot.set_align('vcenter')
				

		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(9)
		boldbord.set_bg_color('#DCE6F1')


		boldbords = workbook.add_format({'bold': True})
		boldbords.set_border(style=2)
		boldbords.set_align('center')
		boldbords.set_align('vcenter')
		boldbords.set_text_wrap()
		boldbords.set_font_size(9)
		boldbords.set_bg_color('#DCE6F1')

		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'#,##0.00'})
		numbertress = workbook.add_format({'num_format':'0.000'})
		numberdoss = workbook.add_format({'num_format':'#,##0.00'})
		numbertrestop = workbook.add_format({'num_format':'0.000'})
		numbertrestop.set_top(1)
		numberdostop = workbook.add_format({'num_format':'#,##0.00'})
		numberdostop.set_top(1)
		bord = workbook.add_format()

		bords = workbook.add_format()
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


		dic_anio = {
			'01': 'Enero',
			'02': 'Febrero',
			'03': 'Marzo',
			'04': 'Abril',
			'05': 'Mayo',
			'06': 'Junio',
			'07': 'Julio',
			'08': 'Agosto',
			'09': 'Septiembre',
			'10': 'Octubre',
			'11': 'Noviembre',
			'12': 'Diciembre',
		}

		worksheet.insert_image('A2', 'calidra.jpg')
		worksheet.write(1,4, u'CALQUIPA {0}'.format(self.periodo_id.code.split('/')[1]), bold)
		worksheet.write(3,4, 'Estado de Resultados', bold)
		worksheet.write(4,4, u'{0}'.format(self.periodo_id.code.split('/')[1]), bold)
		

		worksheet3.insert_image('A2', 'calidra.jpg')
		worksheet3.write(1,4, u'CALQUIPA {0}'.format(self.periodo_id.code.split('/')[1]), bold)
		worksheet3.write(3,4, 'Estado de Resultados', bold)
		worksheet3.write(4,4, u'{0}'.format(self.periodo_id.code.split('/')[1]), bold)
		

		titlees = workbook.add_format({'bold': True})
		titlees.set_align('center')
		titlees.set_align('vcenter')
		
		#worksheet.merge_range(6,0,7,0,u'Nombre', boldbord)

		########worksheet.merge_range(6,1,6,2, u'Mes', titlees)
		#worksheet.write(7,1, u'Saldo', boldbord)
		#worksheet.write(7,2, u'%', boldbord)
		#worksheet.merge_range(6,3,6,6, u'Acumulado', boldbord)
		########worksheet.merge_range(6,3,6,4, u'Año Actual', titlees)
		#worksheet.write(7,4, u'%', boldbord)
		########worksheet.merge_range(6,5,6,6, u'Año Anterior', titlees)
		#worksheet.write(7,6, u'%', boldbord)
		#worksheet.merge_range(6,7,7,7, u'Variacion', boldbord)

		#worksheet.write(6,1, dic_anio[self.periodo_id.code.split('/')[0]].upper(), titlees)
		#worksheet.write(7,1, 'SOLES', titlees)
		#worksheet.write(6,2, 'RECLASIF', titlees)
		#worksheet.write(7,2, '+/-', titlees)
		#worksheet.write(6,3, '', titlees)
		#worksheet.write(7,3, 'Ref', titlees)
		#worksheet.write(6,4, dic_anio[self.periodo_id.code.split('/')[0]].upper(), titlees)
		#worksheet.write(7,4, 'SOLES', titlees)
		#worksheet.write(6,5, 'RECLASIF', titlees)
		#worksheet.write(7,5, 'IFRS', titlees)		
		worksheet.write(6,1, dic_anio[self.periodo_id.code.split('/')[0]].upper(), titlees)
		worksheet.write(7,1, 'SOLES IFRS', titlees)
		#worksheet.write(6,7, 'AJUSTE', titlees)
		#worksheet.write(7,7, '+/-', titlees)
		worksheet.write(6,2, 'T.C.', titlees)
		worksheet.write(7,2, 'SOL VS USD', titlees)
		worksheet.write(6,3, dic_anio[self.periodo_id.code.split('/')[0]].upper(), titlees)
		worksheet.write(7,3, 'USD', titlees)
		#worksheet.write(6,10, 'AJUSTE', titlees)
		#worksheet.write(7,10, '+/-', titlees)
		worksheet.write(6,4, 'T.C.', titlees)
		worksheet.write(7,4, 'USD VS MXN', titlees)
		worksheet.write(6,5, dic_anio[self.periodo_id.code.split('/')[0]].upper(), titlees)
		worksheet.write(7,5, 'MXN', titlees)
		
				





		worksheet3.write(6,1, dic_anio[self.periodo_id.code.split('/')[0]].upper(), titlees)
		worksheet3.write(7,1, 'SOLES IFRS', titlees)
		#worksheet.write(6,7, 'AJUSTE', titlees)
		#worksheet.write(7,7, '+/-', titlees)
		worksheet3.write(6,2, 'T.C.', titlees)
		worksheet3.write(7,2, 'SOL VS USD', titlees)
		worksheet3.write(6,3, dic_anio[self.periodo_id.code.split('/')[0]].upper(), titlees)
		worksheet3.write(7,3, 'USD', titlees)
		#worksheet.write(6,10, 'AJUSTE', titlees)
		#worksheet.write(7,10, '+/-', titlees)
		worksheet3.write(6,4, 'T.C.', titlees)
		worksheet3.write(7,4, 'USD VS MXN', titlees)
		worksheet3.write(6,5, dic_anio[self.periodo_id.code.split('/')[0]].upper(), titlees)
		worksheet3.write(7,5, 'MXN', titlees)
		
		x = 8

		totalfinal = [0,0,0,0,0]

		for i in self.env['rm.er.mexicano.line'].search([('padre','=',self.id)]).sorted(lambda r : r.orden):
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
			else:			
				boldbordtmp = workbook.add_format({'bold': False})
				boldbordtmp.set_font_size(9)
				boldbordtmpRight = workbook.add_format({'bold': False})
				boldbordtmpRight.set_font_size(9)
				boldbordtmpRight.set_align('right')
				boldbordtmpRight.set_align('vright')
				numberdostmp = workbook.add_format({'num_format':'#,##0.00'})
				numbertrestmp = workbook.add_format({'num_format':'0.000'})
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

					numberdostmp = workbook.add_format({'bold': True,'num_format':'#,##0.00'})
					numberdostmp.set_text_wrap()
					numberdostmp.set_font_size(9)

					numbertrestmp = workbook.add_format({'bold': True,'num_format':'0.000'})
					numbertrestmp.set_text_wrap()
					numbertrestmp.set_font_size(9)

				if i.bordes:
					boldbordtmp.set_border(style=2)
					numberdostmp.set_border(style=2)
					numbertrestmp.set_border(style=2)

					boldbordtmpRight.set_border(style=2)



				worksheet.write(x,0, i.concepto if i.concepto else '',boldbordtmp)
				#worksheet.write(x,1, i.monto ,numberdostmp)
				#worksheet.write(x,2, i.reclasif ,numberdostmp)
				#worksheet.write(x,3, str(i.ref) if i.ref != 0 else '' ,boldbordtmp)
				#worksheet.write(x,4, i.t_monto ,numberdostmp)
				#worksheet.write(x,5, i.reclasif_ifrs ,numberdostmp)
				worksheet.write(x,1, i.t_monto_ifrs ,numberdostmp)
				#worksheet.write(x,7, i.ajuste ,numberdostmp)
				worksheet.write(x,2, i.tc_usd ,numbertrestmp)
				worksheet.write(x,3, i.monto_usd ,numberdostmp)
				#worksheet.write(x,10, i.ajuste_usd ,numberdostmp)
				worksheet.write(x,4, i.tc_mxn ,numbertrestmp)
				worksheet.write(x,5, i.monto_mxn ,numberdostmp)

				tmpty= [i.t_monto_ifrs,i.monto_usd,i.monto_mxn]
				for ittt in self.env['rm.er.mexicano.line'].search([('padre.periodo_id.date_stop','<',self.periodo_id.date_start),('orden','=',i.orden)]):
					tmpty[0] += ittt.t_monto_ifrs
					tmpty[1] += ittt.monto_usd
					tmpty[2] += ittt.monto_mxn

				worksheet3.write(x,0, i.concepto if i.concepto else '',boldbordtmp)
				#worksheet.write(x,1, i.monto ,numberdostmp)
				#worksheet.write(x,2, i.reclasif ,numberdostmp)
				#worksheet.write(x,3, str(i.ref) if i.ref != 0 else '' ,boldbordtmp)
				#worksheet.write(x,4, i.t_monto ,numberdostmp)
				#worksheet.write(x,5, i.reclasif_ifrs ,numberdostmp)
				worksheet3.write(x,1, tmpty[0] ,numberdostmp)
				#worksheet.write(x,7, i.ajuste ,numberdostmp)
				worksheet3.write(x,2, tmpty[0]/tmpty[1] if tmpty[1] != 0 else 0  ,numbertrestmp)
				worksheet3.write(x,3, tmpty[1] ,numberdostmp)
				#worksheet.write(x,10, i.ajuste_usd ,numberdostmp)
				worksheet3.write(x,4, tmpty[2]/tmpty[1] if tmpty[1] != 0 else 0 ,numbertrestmp)
				worksheet3.write(x,5, tmpty[2] ,numberdostmp)

				totalfinal[0]=tmpty[0]
				totalfinal[1]=tmpty[1]
				totalfinal[2]=tmpty[2]

			x += 1


		x += 1


		boldbordtmp = workbook.add_format({'bold': False})
		boldbordtmp.set_font_size(9)
		boldbordtmpRight = workbook.add_format({'bold': False})
		boldbordtmpRight.set_font_size(9)
		boldbordtmpRight.set_align('right')
		boldbordtmpRight.set_align('vright')
		numberdostmp = workbook.add_format({'num_format':'#,##0.00'})
		numbertrestmp = workbook.add_format({'num_format':'0.000'})
		numberdostmp.set_font_size(9)
		if True:
			boldbordtmp = workbook.add_format({'bold': True})
			boldbordtmp.set_text_wrap()
			boldbordtmp.set_font_size(9)

			boldbordtmpRight = workbook.add_format({'bold': True})
			boldbordtmpRight.set_text_wrap()
			boldbordtmpRight.set_align('right')
			boldbordtmpRight.set_align('vright')
			boldbordtmpRight.set_font_size(9)

			numberdostmp = workbook.add_format({'bold': True,'num_format':'#,##0.00'})
			numberdostmp.set_text_wrap()
			numberdostmp.set_font_size(9)

			numbertrestmp = workbook.add_format({'bold': True,'num_format':'0.000'})
			numbertrestmp.set_text_wrap()
			numbertrestmp.set_font_size(9)

		if True:
			boldbordtmp.set_border(style=2)
			numberdostmp.set_border(style=2)
			numbertrestmp.set_border(style=2)

			boldbordtmpRight.set_border(style=2)


		
		obj_llegardolar = 0
		obj_llegarmxn= 0
		obj_llegarsoles = 0

		obj_totalizador = self.env['rm.es.simple.mexicano.line'].search([('padre_pasivo.periodo_id','=',self.periodo_id.id),('concepto','=','UTILIDAD O (PERDIDA) DEL EJERCICIO')])
		if len(obj_totalizador)>0:
			obj_llegardolar = obj_totalizador[0].monto_usd
			obj_llegarmxn= obj_totalizador[0].monto_mxn
			obj_llegarsoles = obj_totalizador[0].t_monto_ifrs

		worksheet3.write(x,0, 'DIFERENCIA DE CONVERSION',boldbordtmp)
		#worksheet.write(x,1, i.monto ,numberdostmp)
		#worksheet.write(x,2, i.reclasif ,numberdostmp)
		#worksheet.write(x,3, str(i.ref) if i.ref != 0 else '' ,boldbordtmp)
		#worksheet.write(x,4, i.t_monto ,numberdostmp)
		#worksheet.write(x,5, i.reclasif_ifrs ,numberdostmp)
		worksheet3.write(x,1, 0 ,numberdostmp)
		#worksheet.write(x,7, i.ajuste ,numberdostmp)
		#worksheet.write(x,2, '' ,numbertrestmp)
		worksheet3.write(x,3, obj_llegardolar - totalfinal[1] ,numberdostmp)
		#worksheet.write(x,10, i.ajuste_usd ,numberdostmp)
		#worksheet.write(x,4, i.tc_mxn ,numbertrestmp)
		worksheet3.write(x,5, obj_llegarmxn - totalfinal[2] ,numberdostmp)


		x += 2



		worksheet3.write(x,0, 'RESULTADO DEL PERIODO',boldbordtmp)
		#worksheet.write(x,1, i.monto ,numberdostmp)
		#worksheet.write(x,2, i.reclasif ,numberdostmp)
		#worksheet.write(x,3, str(i.ref) if i.ref != 0 else '' ,boldbordtmp)
		#worksheet.write(x,4, i.t_monto ,numberdostmp)
		#worksheet.write(x,5, i.reclasif_ifrs ,numberdostmp)
		worksheet3.write(x,1, obj_llegarsoles ,numberdostmp)
		#worksheet.write(x,7, i.ajuste ,numberdostmp)
		worksheet3.write(x,2, obj_llegarsoles/obj_llegardolar if obj_llegardolar != 0 else 0  ,numbertrestmp)
		worksheet3.write(x,3, obj_llegardolar  ,numberdostmp)
		#worksheet.write(x,10, i.ajuste_usd ,numberdostmp)
		worksheet3.write(x,4, obj_llegarmxn/obj_llegardolar if obj_llegardolar != 0 else 0 ,numbertrestmp)
		worksheet3.write(x,5, obj_llegarmxn  ,numberdostmp)



		t = 15.86
		worksheet.set_column('A:A', 55)
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



		#worksheet.insert_image('A2', 'calidra.jpg')
		worksheet_2.merge_range(0,0,0,12, u'CALQUIPA S.A.C', boldcenter)
		worksheet_2.merge_range(2,0,2,12, u'ESTADOS DE RESULTADOS (SOLES(S)) '+ str(self.periodo_id.code.split('/')[1]) , boldbords)
	
		worksheet_2.write(5,0, u'CONCEPTO', boldcenter)
		worksheet_2.write(5,1, u'ENERO', boldcenter)
		worksheet_2.write(5,2, u'FEBRERO', boldcenter)
		worksheet_2.write(5,3, u'MARZO', boldcenter)
		worksheet_2.write(5,4, u'ABRIL', boldcenter)
		worksheet_2.write(5,5, u'MAYO', boldcenter)
		worksheet_2.write(5,6, u'JUNIO', boldcenter)
		worksheet_2.write(5,7, u'JULIO', boldcenter)
		worksheet_2.write(5,8, u'AGOSTO', boldcenter)
		worksheet_2.write(5,9, u'SEPTIEMBRE', boldcenter)
		worksheet_2.write(5,10, u'OCTUBRE', boldcenter)
		worksheet_2.write(5,11, u'NOVIEMBRE', boldcenter)
		worksheet_2.write(5,12, u'DICIEMBRE', boldcenter)

		worksheet_2.write(6,0, u'INGRESOS:', boldcenter)

		x = 7
		x_inicio = 7
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.er.mexicano'].search([('periodo_id','=',m.id)])
				if len(tt)>0:
					tt=tt[0]
					period_list.append( (m,tt) )

		for i in self.env['rm.resultado.config.mexicano.line'].search([('tipo_cuenta','=','1')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.er.mexicano.line'].search([('concepto','=',i.concepto),('tipo_cuenta','=','1'),('padre','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].t_monto_ifrs ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)
				camino+=1
			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		total_ingreso_sol_pos = x
		worksheet_2.write(x,0,'TOTAL DE INGRESOS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1		

		x+=2

		worksheet_2.write(6,0, u'EGRESOS:', boldcenter)

		for i in self.env['rm.resultado.config.mexicano.line'].search([('tipo_cuenta','=','2')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.er.mexicano.line'].search([('concepto','=',i.concepto),('tipo_cuenta','=','2'),('padre','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].t_monto_ifrs ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)
				camino+=1
			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		total_egreso_sol_pos = x
		worksheet_2.write(x,0,'TOTAL DE EGRESOS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1
		

		x+=2

		camino_final =1
		worksheet_2.write(x,0,'UTILIDAD (PERDIDA) EN SOLES',bords)
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(total_ingreso_sol_pos,camino_final) +'+' +xl_rowcol_to_cell(total_egreso_sol_pos,camino_final) + ')', numberdostop)
				camino_final += 1
		x+=2

		camino_final =1
		worksheet_2.write(x,0,'T.C. COMPRA (S VS USD)',bords)
		for j in period_list:
			if j[1]:
				worksheet_2.write(x,camino_final, j[1].t_cambio_compra , numbertress)
				camino_final += 1

		x+=2

		camino_final =1
		worksheet_2.write(x,0,'T.C. VENTA (S VS USD)',bords)
		for j in period_list:
			if j[1]:
				worksheet_2.write(x,camino_final, j[1].t_cambio_venta , numbertress)
				camino_final += 1


		#AQUI SE TERMINO LA PRIMERA PARTE


		x += 2
		worksheet_2.merge_range(x,0,x,12, u'ESTADOS DE RESULTADOS (DOLARES(USD)) '+ str(self.periodo_id.code.split('/')[1]) , boldbords)
		x += 2


		worksheet_2.write(x,0, u'CONCEPTO', boldcenter)
		worksheet_2.write(x,1, u'ENERO', boldcenter)
		worksheet_2.write(x,2, u'FEBRERO', boldcenter)
		worksheet_2.write(x,3, u'MARZO', boldcenter)
		worksheet_2.write(x,4, u'ABRIL', boldcenter)
		worksheet_2.write(x,5, u'MAYO', boldcenter)
		worksheet_2.write(x,6, u'JUNIO', boldcenter)
		worksheet_2.write(x,7, u'JULIO', boldcenter)
		worksheet_2.write(x,8, u'AGOSTO', boldcenter)
		worksheet_2.write(x,9, u'SEPTIEMBRE', boldcenter)
		worksheet_2.write(x,10, u'OCTUBRE', boldcenter)
		worksheet_2.write(x,11, u'NOVIEMBRE', boldcenter)
		worksheet_2.write(x,12, u'DICIEMBRE', boldcenter)

		x = x+1
		worksheet_2.write(x,0, u'INGRESOS:', boldcenter)

		x = x+1
		x_inicio = x
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.er.mexicano'].search([('periodo_id','=',m.id)])
				if len(tt)>0:
					tt = tt[0]
					period_list.append( (m,tt) )

		for i in self.env['rm.resultado.config.mexicano.line'].search([('tipo_cuenta','=','1')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.er.mexicano.line'].search([('concepto','=',i.concepto),('tipo_cuenta','=','1'),('padre','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].monto_usd ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)
				camino+=1
			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		total_ingreso_usd_pos = x
		worksheet_2.write(x,0,'TOTAL DE INGRESOS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1		

		x+=2

		worksheet_2.write(6,0, u'EGRESOS:', boldcenter)

		for i in self.env['rm.resultado.config.mexicano.line'].search([('tipo_cuenta','=','2')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.er.mexicano.line'].search([('concepto','=',i.concepto),('tipo_cuenta','=','2'),('padre','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].monto_usd ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)
				camino+=1
			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		total_egreso_usd_pos = x
		worksheet_2.write(x,0,'TOTAL DE EGRESOS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1
		

		x+=2

		camino_final =1
		worksheet_2.write(x,0,'UTILIDAD (PERDIDA) EN USD',bords)
		pos_utilidad_dolares = x
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(total_ingreso_usd_pos,camino_final) +'+' +xl_rowcol_to_cell(total_egreso_usd_pos,camino_final) + ')', numberdostop)
				camino_final += 1
		x+=2

		camino_final =1
		worksheet_2.write(x,0,'T.C. COMPRA (USD VS MXN)',bords)
		pos_mxn_valor = x
		for j in period_list:
			if j[1]:
				worksheet_2.write(x,camino_final, j[1].t_cambio_mexicano , numbertress)
				camino_final += 1



		##### asdnhiasonhfioasjfasjfioas



		x += 2
		worksheet_2.merge_range(x,0,x,12, u'ESTADOS DE RESULTADOS (PESOS(MXN)) '+ str(self.periodo_id.code.split('/')[1]) , boldbords)
		x += 2


		worksheet_2.write(x,0, u'CONCEPTO', boldcenter)
		worksheet_2.write(x,1, u'ENERO', boldcenter)
		worksheet_2.write(x,2, u'FEBRERO', boldcenter)
		worksheet_2.write(x,3, u'MARZO', boldcenter)
		worksheet_2.write(x,4, u'ABRIL', boldcenter)
		worksheet_2.write(x,5, u'MAYO', boldcenter)
		worksheet_2.write(x,6, u'JUNIO', boldcenter)
		worksheet_2.write(x,7, u'JULIO', boldcenter)
		worksheet_2.write(x,8, u'AGOSTO', boldcenter)
		worksheet_2.write(x,9, u'SEPTIEMBRE', boldcenter)
		worksheet_2.write(x,10, u'OCTUBRE', boldcenter)
		worksheet_2.write(x,11, u'NOVIEMBRE', boldcenter)
		worksheet_2.write(x,12, u'DICIEMBRE', boldcenter)

		x = x+1
		worksheet_2.write(x,0, u'INGRESOS:', boldcenter)

		x = x+1
		x_inicio = x
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.er.mexicano'].search([('periodo_id','=',m.id)])
				if len(tt)>0:
					tt = tt[0]
					period_list.append( (m,tt) )

		for i in self.env['rm.resultado.config.mexicano.line'].search([('tipo_cuenta','=','1')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.er.mexicano.line'].search([('concepto','=',i.concepto),('tipo_cuenta','=','1'),('padre','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].monto_mxn ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)
				camino+=1
			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		total_ingreso_mxn_pos = x
		worksheet_2.write(x,0,'TOTAL DE INGRESOS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1		

		x+=2

		worksheet_2.write(6,0, u'EGRESOS:', boldcenter)

		for i in self.env['rm.resultado.config.mexicano.line'].search([('tipo_cuenta','=','2')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.er.mexicano.line'].search([('concepto','=',i.concepto),('tipo_cuenta','=','2'),('padre','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].monto_mxn ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)
				camino+=1
			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		total_egreso_mxn_pos = x
		worksheet_2.write(x,0,'TOTAL DE EGRESOS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1
		

		x+=2

		camino_final =1
		worksheet_2.write(x,0,'UTILIDAD (PERDIDA) SIN DEPREC.',bords)
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(total_ingreso_mxn_pos,camino_final) +'+' +xl_rowcol_to_cell(total_egreso_mxn_pos,camino_final) + ')', numberdostop)
				camino_final += 1
		x+=1

		camino_final =1

		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(x-1,camino_final) +'/' +xl_rowcol_to_cell(pos_utilidad_dolares,camino_final) + ')', numberdostop)
				camino_final += 1

		x+=1
		camino_final =1
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(x-1,camino_final) +'-' +xl_rowcol_to_cell(pos_mxn_valor,camino_final) + ')', numberdostop)
				camino_final += 1


		# oaspdjaspdjaspodmpakm 2


		#AQUI SE TERMINO LA Tercera PARTE


		t = 15.86
		worksheet_2.set_column('A:A', 55)
		worksheet_2.set_column('B:B', t)
		worksheet_2.set_column('C:C', t)
		worksheet_2.set_column('D:D', t)
		worksheet_2.set_column('E:E', t)
		worksheet_2.set_column('F:F', t)
		worksheet_2.set_column('G:G', t)
		worksheet_2.set_column('H:H', t)
		worksheet_2.set_column('I:I', t)
		worksheet_2.set_column('J:J', t)
		worksheet_2.set_column('K:K', t)
		worksheet_2.set_column('L:L', t)
		worksheet_2.set_column('M:M', t)
		worksheet_2.set_column('N:N', t)
		worksheet_2.set_column('O:O', t)
		worksheet_2.set_column('P:P', t)
		worksheet_2.set_column('Q:Q', t)




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