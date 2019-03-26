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



class tipo_cambio_mexicano(models.Model):
	_name = 'tipo.cambio.mexicano'

	periodo_id = fields.Many2one('account.period','Periodo')
	t_cambio_compra = fields.Float('T. Cambio Compra',digits=(12,3))
	t_cambio_venta = fields.Float('T. Cambio Venta',digits=(12,3))
	t_cambio_mexicano = fields.Float('T. Cambio Mexicano',digits=(12,3))

	promedio_compra = fields.Float('Prom. Compra',digits=(12,3),readonly="1")
	promedio_venta = fields.Float('Prom. Venta',digits=(12,3),readonly="1")
	promedio_mexicano = fields.Float('Prom. Mexicano',digits=(12,3),readonly="1")

	@api.multi
	def actualizar_cambios(selfs):
		for self in selfs:
			moneda_dolar = self.env['res.currency'].search([('name','=','USD')])[0]
			total_compra = 0
			total_venta = 0
			total_nro = 0
			for i in self.env['res.currency.rate'].search([('currency_id','=',moneda_dolar.id),('name','>=',self.periodo_id.date_start),('name','<=',self.periodo_id.date_stop)]):
				total_compra += i.type_purchase
				total_venta += i.type_sale
				total_nro += 1
			self.promedio_venta = total_venta / total_nro if total_nro != 0 else 0
			self.promedio_compra = total_compra / total_nro if total_nro != 0 else 0

			total_nro = 0
			total_mex = 0
			for i in self.env['res.currency.mex'].search([('fecha','>=',self.periodo_id.date_start),('fecha','<=',self.periodo_id.date_stop)]):
				total_mex  += i.tipo_cambio
				total_nro += 1

			self.promedio_mexicano = total_mex / total_nro if total_nro != 0 else 0


	_rec_name = 'periodo_id'

def dig_5(n):
	return ("%5d" % n).replace(' ','0')

class rm_es_simple_mexicano_line(models.Model):
	_name = 'rm.es.simple.mexicano.line'

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
	def get_monto_usd(self):
		if self.tipo_cuenta == '3':# and self.formula != 'UTILIDAD':

			directorio = [
				[2,'UTILIDAD',"i._sum_total_utilidad_W(XX]"],
				[2,'AJUSTE_CONVERSION',"i._sum_ajuste_conversion_W(XX]"],				
				[2,'SUMA_PASIVO_CAPITAL_TOTAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO + TOTAL_CAPITAL_CONTABLE"],
				[2,'SUMA_PASIVO_CAPITAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO"],
				[2,'SUMA_DEL_ACTIVO',"TOTAL_CIRCULANTE + TOTAL_FIJO + TOTAL_DIFERIDO"],
				[2,'TOTAL_FIJO',"TOTAL_5 + TOTAL_ACTIVO_FIJO"],
				[2,'TOTAL_CIRCULANTE',"TOTAL_EXIGIBLE + TOTAL_REALIZABLE + TOTAL_DISPONIBLE"],
				[1,'DEUDA_INTRINSECA_ARRENDAMIENTO',"i._sum_total_W('11',XX]"],
				[1,'TOTAL_CAPITAL_CONTABLE',"i._sum_total_W('10',XX]"],
				[1,'TOTAL_PASIVO_FIJO',"i._sum_total_W('9',XX]"],
				[1,'TOTAL_PASIVO_CIRCULANTE',"i._sum_total_W('8',XX]"],
				[1,'VALOR_ACTUAL_ARRENDAMIENTO',"i._sum_total_W('7',XX]"],
				[1,'TOTAL_DIFERIDO',"i._sum_total_W('6',XX]"],
				[1,'TOTAL_5',"i._sum_total_W('5',XX]"],
				[1,'TOTAL_ACTIVO_FIJO',"i._sum_total_W('4',XX]"],
				[1,'TOTAL_EXIGIBLE',"i._sum_total_W('2',XX]"],
				[1,'TOTAL_REALIZABLE',"i._sum_total_W('3',XX]"],
				[1,'TOTAL_DISPONIBLE',"i._sum_total_W('1',XX]"],
				[1,'L[',"i._cal_orden_W('1',XX,"],
				[1,'R[',"i._cal_orden_W('2',XX,"],
			]

			i = self.env['rm.es.simple.mexicano.line'].search([('tipo_cuenta','=','3'),('padre_activo','=',self.padre_activo.id),('padre_pasivo','=',self.padre_pasivo.id),('formula','=',self.formula)])[0]
			val = 0
			try:
				tmp_formula = i.formula					
				for dir_m_ac in directorio:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2].replace('XX','1'))
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!', "val = " + i.formula.replace('L[','i.calculo_prog_mes_uno(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.formula )

			self.monto_usd = val

		elif not self.tipo_cambio:
			self.monto_usd = 0

		else:
			periodo_padre = self.padre_pasivo.periodo_id.id if self.padre_pasivo.id else self.padre_activo.periodo_id.id
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
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.concepto)])[0]
					padre = self.padre_activo.periodo_id.id if self.padre_activo.id else self.padre_pasivo.periodo_id.id
					activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.activo.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.monto_usd = resumen_activo_fijo[0].monto_usd * (-1 if self.t_monto_ifrs * resumen_activo_fijo[0].monto_usd < 0 else 1 ) 
						else:
							self.monto_usd = 0
					else:
						self.monto_usd = 0

				if self.tipo_cambio == '6':
					
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.concepto)])[0]
					padre = self.padre_activo.periodo_id.id if self.padre_activo.id else self.padre_pasivo.periodo_id.id
					activofijo = self.env['reporte.patrimonio'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.patrimonio.line'].search([('patrimonio_id','=',activofijo[0].id),('partida','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.monto_usd = resumen_activo_fijo[0].dlls  * (-1 if self.t_monto_ifrs *resumen_activo_fijo[0].dlls < 0 else 1 )
						else:
							self.monto_usd = 0
					else:
						self.monto_usd = 0
					
				if self.tipo_cambio == '7':
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.concepto)])[0]
					padre = self.padre_activo.periodo_id.id if self.padre_activo.id else self.padre_pasivo.periodo_id.id
					activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.depre.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.monto_usd = resumen_activo_fijo[0].monto_usd * (-1 if self.t_monto_ifrs * resumen_activo_fijo[0].monto_usd < 0 else 1 )  
						else:
							self.monto_usd = 0
					else:
						self.monto_usd = 0
			else:
				self.monto_usd = 0


	@api.one
	def get_monto_mxn(self):
		if self.tipo_cuenta == '3':# and self.formula != 'UTILIDAD':
			directorio = [
				[2,'UTILIDAD',"i._sum_total_utilidad_W(XX]"],
				[2,'AJUSTE_CONVERSION',"i._sum_ajuste_conversion_W(XX]"],	
				[2,'SUMA_PASIVO_CAPITAL_TOTAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO + TOTAL_CAPITAL_CONTABLE"],
				[2,'SUMA_PASIVO_CAPITAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO"],
				[2,'SUMA_DEL_ACTIVO',"TOTAL_CIRCULANTE + TOTAL_FIJO + TOTAL_DIFERIDO"],
				[2,'TOTAL_FIJO',"TOTAL_5 + TOTAL_ACTIVO_FIJO"],
				[2,'TOTAL_CIRCULANTE',"TOTAL_EXIGIBLE + TOTAL_REALIZABLE + TOTAL_DISPONIBLE"],
				[1,'DEUDA_INTRINSECA_ARRENDAMIENTO',"i._sum_total_W('11',XX]"],
				[1,'TOTAL_CAPITAL_CONTABLE',"i._sum_total_W('10',XX]"],
				[1,'TOTAL_PASIVO_FIJO',"i._sum_total_W('9',XX]"],
				[1,'TOTAL_PASIVO_CIRCULANTE',"i._sum_total_W('8',XX]"],
				[1,'VALOR_ACTUAL_ARRENDAMIENTO',"i._sum_total_W('7',XX]"],
				[1,'TOTAL_DIFERIDO',"i._sum_total_W('6',XX]"],
				[1,'TOTAL_5',"i._sum_total_W('5',XX]"],
				[1,'TOTAL_ACTIVO_FIJO',"i._sum_total_W('4',XX]"],
				[1,'TOTAL_EXIGIBLE',"i._sum_total_W('2',XX]"],
				[1,'TOTAL_REALIZABLE',"i._sum_total_W('3',XX]"],
				[1,'TOTAL_DISPONIBLE',"i._sum_total_W('1',XX]"],
				[1,'L[',"i._cal_orden_W('1',XX,"],
				[1,'R[',"i._cal_orden_W('2',XX,"],
			]

			i = self.env['rm.es.simple.mexicano.line'].search([('tipo_cuenta','=','3'),('padre_activo','=',self.padre_activo.id),('padre_pasivo','=',self.padre_pasivo.id),('formula','=',self.formula)])[0]
			val = 0
			try:
				tmp_formula = i.formula					
				for dir_m_ac in directorio:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2].replace('XX','2'))
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!', "val = " + i.formula.replace('L[','i.calculo_prog_mes_uno(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.formula )

			self.monto_mxn = val
		elif not self.tipo_cambio:
			self.monto_mxn = 0
		else:
			periodo_padre = self.padre_pasivo.periodo_id.id if self.padre_pasivo.id else self.padre_activo.periodo_id.id
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
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.concepto)])[0]
					padre = self.padre_activo.periodo_id.id if self.padre_activo.id else self.padre_pasivo.periodo_id.id
					activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.activo.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.monto_mxn = resumen_activo_fijo[0].pesos  * (-1 if self.t_monto_ifrs *resumen_activo_fijo[0].pesos < 0 else 1 )
						else:
							self.monto_mxn = 0
					else:
						self.monto_mxn = 0

				if self.tipo_cambio == '6':
					
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.concepto)])[0]
					padre = self.padre_activo.periodo_id.id if self.padre_activo.id else self.padre_pasivo.periodo_id.id
					activofijo = self.env['reporte.patrimonio'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.patrimonio.line'].search([('patrimonio_id','=',activofijo[0].id),('partida','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.monto_mxn = resumen_activo_fijo[0].valor_mxn  * (-1 if self.t_monto_ifrs * resumen_activo_fijo[0].valor_mxn < 0 else 1 )
						else:
							self.monto_mxn = 0
					else:
						self.monto_mxn = 0

				if self.tipo_cambio == '7':
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.concepto)])[0]
					padre = self.padre_activo.periodo_id.id if self.padre_activo.id else self.padre_pasivo.periodo_id.id
					activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.depre.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.monto_mxn = resumen_activo_fijo[0].pesos * (-1 if self.t_monto_ifrs * resumen_activo_fijo[0].pesos < 0 else 1 ) 
						else:
							self.monto_mxn = 0
					else:
						self.monto_mxn = 0
			else:
				self.monto_mxn = 0

	@api.one
	def get_ajuste_usd(self):
		self.ajuste_usd = self.monto_mxn - self.monto_usd

	@api.one
	def get_tc_mxn(self):
		if self.monto_usd == 0:
			self.tc_mxn = 0
		else:
			self.tc_mxn = self.monto_mxn / self.monto_usd


	orden = fields.Integer('Orden',required=True)
	concepto = fields.Char('Concepto')
	tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=True)
	tipo_cambio = fields.Selection([('1','Tipo Compra Cierre'),('2','Tipo Venta Cierre'),('3','Tipo Promedio Compras'),('4','Tipo Promedio Ventas'),('5','Activo Fijo-Cédula'),('6','Patrimonio-Cédula'),('7','Depreciacion-Cédula')],'Tipo de Cambio',required=False, default="1")	
	grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos Fijos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Grupo',readonly=True )
	formula = fields.Char('Formula')
	resaltado = fields.Boolean('Resaltado')
	bordes = fields.Boolean('Bordes')
	monto = fields.Float('Monto Soles',digits=(12,2))
	reclasif = fields.Float('Reclasif. +/-',digits=(12,2))
	ref = fields.Integer('Ref')
	t_monto = fields.Float('Monto Soles',compute="get_t_monto",digits=(12,2))
	reclasif_ifrs = fields.Float('Reclasifc. IFRS',digits=(12,2))
	t_monto_ifrs = fields.Float('Monto Soles IFRS',compute="get_t_monto_ifrs",digits=(12,2))
	ajuste = fields.Float('Ajuste +/-',compute="get_ajuste",digits=(12,2))
	tc_usd = fields.Float('T.C. SOL vs USD',compute="get_tc_usd", digits=(12,3))
	monto_usd = fields.Float('Monto USD',compute="get_monto_usd",digits=(12,2))
	ajuste_usd = fields.Float('Ajuste +/-',compute="get_ajuste_usd",digits=(12,2))
	tc_mxn = fields.Float('T.C. USD vs MXN',compute="get_tc_mxn",digits=(12,3))
	monto_mxn = fields.Float('Monto MXN',compute="get_monto_mxn",digits=(12,2))

	padre_pasivo = fields.Many2one('rm.es.mexicano','Cabezera')
	padre_activo = fields.Many2one('rm.es.mexicano','Cabezera')

	_order = 'orden'




	@api.one
	def _sum_total_utilidad_(self,mes):
		calculo = 0
		for i in self.env['rm.es.simple.mexicano.line'].search([('grupo_cuenta','in',('1','2','3','4','5','6') ),('tipo_cuenta','=','1'),'|',('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) ),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
			if mes == 1:
				calculo += i.monto
			elif mes == 2:
				calculo += i.reclasif
			else:
				calculo += i.reclasif_ifrs

		for i in self.env['rm.es.simple.mexicano.line'].search([('grupo_cuenta','in',('8','9','10') ),('tipo_cuenta','=','1'),'|',('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) ),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
			if mes == 1:
				calculo -= i.monto
			elif mes == 2:
				calculo -= i.reclasif
			else:
				calculo -= i.reclasif_ifrs


		return calculo



	@api.one
	def _sum_ajuste_conversion_(self,mes):
		calculo = 0
		return calculo


	@api.one
	def _sum_total_utilidad_W(self,mes):
		calculo = 0
		for i in self.env['rm.es.simple.mexicano.line'].search([('grupo_cuenta','in',('1','2','3','4','5','6') ),('tipo_cuenta','=','1'),'|',('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) ),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
			if mes == 1:
				calculo += i.monto_usd
			else:
				calculo += i.monto_mxn

		for i in self.env['rm.es.simple.mexicano.line'].search([('grupo_cuenta','in',('8','9','10') ),('tipo_cuenta','=','1'),'|',('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) ),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
			if mes == 1:
				calculo -= i.monto_usd
			else:
				calculo -= i.monto_mxn


		return calculo


	@api.one
	def _sum_ajuste_conversion_W(self,mes):
		calculo = 0
		for i in self.env['rm.es.simple.mexicano.line'].search([('grupo_cuenta','in',('1','2','3','4','5','6') ),('tipo_cuenta','in',('1','3')),'|',('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) ),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
			if i.tipo_cuenta == '1' or ( i.tipo_cuenta == '3' and i.formula == 'UTILIDAD' ):
				if mes == 1:
					calculo += i.monto_usd
				else:
					calculo += i.monto_mxn

		for i in self.env['rm.es.simple.mexicano.line'].search([('grupo_cuenta','in',('8','9','10') ),('tipo_cuenta','in',('1','3')),'|',('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) ),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
			if i.tipo_cuenta == '1' or ( i.tipo_cuenta == '3' and i.formula == 'UTILIDAD' ):
				if mes == 1:
					calculo -= i.monto_usd
				else:
					calculo -= i.monto_mxn

		return calculo


	@api.one
	def _sum_total_(self,grupo,mes):
		calculo = 0
		if grupo == '10':
			for i in self.env['rm.es.simple.mexicano.line'].search([('tipo_cuenta','in',('1','3') ),('grupo_cuenta','=',grupo),'|',('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) ),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
				if i.tipo_cuenta == '1':
					if mes == 1:
						calculo += i.monto
					elif mes == 2:
						calculo += i.reclasif
					else:
						calculo += i.reclasif_ifrs
				else:
					if i.concepto == 'UTILIDAD O (PERDIDA) DEL EJERCICIO' or i.concepto == 'AJUSTE POR CONVERSION':
						if mes == 1:
							calculo += i.monto
						elif mes == 2:
							calculo += i.reclasif
						else:
							calculo += i.reclasif_ifrs
		else:
			for i in self.env['rm.es.simple.mexicano.line'].search([('tipo_cuenta','in',('1','3') ),('grupo_cuenta','=',grupo),'|',('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) ),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
				if i.tipo_cuenta == '1':
					if mes == 1:
						calculo += i.monto
					elif mes == 2:
						calculo += i.reclasif
					else:
						calculo += i.reclasif_ifrs
					
		return calculo


	@api.one
	def _sum_total_W(self,grupo,mes):
		calculo = 0
		if grupo == '10':
			for i in self.env['rm.es.simple.mexicano.line'].search([('tipo_cuenta','in',('1','3') ),('grupo_cuenta','=',grupo),'|',('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) ),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
				if i.tipo_cuenta == '1':
					if mes == 1:
						calculo += i.monto_usd
					else:
						calculo += i.monto_mxn
				else:
					if i.concepto == 'UTILIDAD O (PERDIDA) DEL EJERCICIO' or i.concepto == 'AJUSTE POR CONVERSION':
						if mes == 1:
							calculo += i.monto_usd
						else:
							calculo += i.monto_mxn
		else:
			for i in self.env['rm.es.simple.mexicano.line'].search([('tipo_cuenta','in',('1','3') ),('grupo_cuenta','=',grupo),'|',('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) ),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
				if i.tipo_cuenta == '1':
					if mes == 1:
						calculo += i.monto_usd
					else:
						calculo += i.monto_mxn
					
		return calculo

	"""
	@api.one
	def _sum_total_(self,grupo,mes):
		calculo = 0
		for i in self.env['rm.es.simple.mexicano.line'].search([('tipo_cuenta','=','1'),('grupo_cuenta','=',grupo),'|',('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) ),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
			if mes == 1:
				calculo += i.monto
			elif mes == 2:
				calculo += i.reclasif
			else:
				calculo += i.reclasif_ifrs

		return calculo
	"""
	@api.one
	def _cal_orden_(self,grupo,mes,orden):
		calculo = 0
		if grupo == '1':
			for i in self.env['rm.es.simple.mexicano.line'].search([('orden','=',orden),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
				if mes == 1:
					calculo += i.monto
				elif mes == 2:
					calculo += i.reclasif
				else:
					calculo += i.reclasif_ifrs
		else:
			for i in self.env['rm.es.simple.mexicano.line'].search([('orden','=',orden),('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
				if mes == 1:
					calculo += i.monto
				elif mes == 2:
					calculo += i.reclasif
				else:
					calculo += i.reclasif_ifrs

		return calculo


	@api.one
	def _cal_orden_W(self,grupo,mes,orden):
		calculo = 0
		if grupo == '1':
			for i in self.env['rm.es.simple.mexicano.line'].search([('orden','=',orden),('padre_activo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
				if mes == 1:
					calculo += i.monto_usd
				else:
					calculo += i.monto_mxn
		else:
			for i in self.env['rm.es.simple.mexicano.line'].search([('orden','=',orden),('padre_pasivo','=',( self.padre_pasivo.id if self.padre_pasivo.id else self.padre_activo.id) )]):
				if mes == 1:
					calculo += i.monto_usd
				else:
					calculo += i.monto_mxn

		return calculo



class rm_es_mexicano_line(models.Model):
	_name = 'rm.es.mexicano.line'


	@api.one
	def get_uno_t_monto(self):
		self.uno_t_monto = self.uno_monto + self.uno_reclasif

	@api.one
	def get_uno_t_monto_ifrs(self):
		self.uno_t_monto_ifrs = self.uno_t_monto + self.uno_reclasif_ifrs


	@api.one
	def get_uno_ajuste(self):
		self.uno_ajuste = self.uno_t_monto_ifrs - self.uno_monto_usd

	@api.one
	def get_uno_tc_usd(self):
		if self.uno_monto_usd == 0:
			self.uno_tc_usd = 0
		else:
			self.uno_tc_usd = self.uno_t_monto_ifrs / self.uno_monto_usd

	@api.one
	def get_uno_ajuste_usd(self):
		self.uno_ajuste_usd = self.uno_monto_mxn - self.uno_monto_usd

	@api.one
	def get_uno_tc_mxn(self):
		if self.uno_monto_usd == 0:
			self.uno_tc_mxn = 0
		else:
			self.uno_tc_mxn = self.uno_monto_mxn / self.uno_monto_usd



	@api.one
	def get_uno_monto_usd(self):
		if self.uno_tipo_cuenta == '3':# and self.uno_formula != 'UTILIDAD':

			directorio = [
				[2,'UTILIDAD',"i._sum_total_utilidad_W(XX]"],
				[2,'AJUSTE_CONVERSION',"i._sum_ajuste_conversion_W(XX]"],	
				[2,'SUMA_PASIVO_CAPITAL_TOTAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO + TOTAL_CAPITAL_CONTABLE"],
				[2,'SUMA_PASIVO_CAPITAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO"],
				[2,'SUMA_DEL_ACTIVO',"TOTAL_CIRCULANTE + TOTAL_FIJO + TOTAL_DIFERIDO"],
				[2,'TOTAL_FIJO',"TOTAL_5 + TOTAL_ACTIVO_FIJO"],
				[2,'TOTAL_CIRCULANTE',"TOTAL_EXIGIBLE + TOTAL_REALIZABLE + TOTAL_DISPONIBLE"],
				[1,'DEUDA_INTRINSECA_ARRENDAMIENTO',"i._sum_total_W('11',XX]"],
				[1,'TOTAL_CAPITAL_CONTABLE',"i._sum_total_W('10',XX]"],
				[1,'TOTAL_PASIVO_FIJO',"i._sum_total_W('9',XX]"],
				[1,'TOTAL_PASIVO_CIRCULANTE',"i._sum_total_W('8',XX]"],
				[1,'VALOR_ACTUAL_ARRENDAMIENTO',"i._sum_total_W('7',XX]"],
				[1,'TOTAL_DIFERIDO',"i._sum_total_W('6',XX]"],
				[1,'TOTAL_5',"i._sum_total_W('5',XX]"],
				[1,'TOTAL_ACTIVO_FIJO',"i._sum_total_W('4',XX]"],
				[1,'TOTAL_EXIGIBLE',"i._sum_total_W('2',XX]"],
				[1,'TOTAL_REALIZABLE',"i._sum_total_W('3',XX]"],
				[1,'TOTAL_DISPONIBLE',"i._sum_total_W('1',XX]"],
				[1,'L[',"i._cal_orden_W('1',XX,"],
				[1,'R[',"i._cal_orden_W('2',XX,"],
			]

			i = self.env['rm.es.simple.mexicano.line'].search([('tipo_cuenta','=','3'),'|',('padre_activo','=',self.padre.id),('padre_pasivo','=',self.padre.id),('formula','=',self.uno_formula)])[0]
			val = 0
			try:
				tmp_formula = i.formula					
				for dir_m_ac in directorio:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2].replace('XX','1'))
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!', "val = " + i.formula.replace('L[','i.calculo_prog_mes_uno(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.formula )

			self.uno_monto_usd = val
		elif not self.uno_tipo_cambio:
			self.uno_monto_usd = 0
		else:
			periodo_padre = self.padre.periodo_id.id
			tipo_obj = self.env['tipo.cambio.mexicano'].search([('periodo_id','=',periodo_padre)])
			if len(tipo_obj)>0:
				tipo_obj = tipo_obj[0]
				tmp_m = 1
				if self.uno_tipo_cambio == '1':
					tmp_m = tipo_obj.t_cambio_compra
				if self.uno_tipo_cambio == '2':
					tmp_m = tipo_obj.t_cambio_venta
				if self.uno_tipo_cambio == '3':
					tmp_m = tipo_obj.promedio_compra
				if self.uno_tipo_cambio == '4':
					tmp_m = tipo_obj.promedio_venta

				self.uno_monto_usd = self.uno_t_monto_ifrs /  ( tmp_m )


				if self.uno_tipo_cambio == '5':
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.uno_concepto)])[0]
					padre = self.padre.periodo_id.id
					activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.activo.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.uno_monto_usd = resumen_activo_fijo[0].monto_usd   * (-1 if self.uno_t_monto_ifrs * resumen_activo_fijo[0].monto_usd < 0 else 1 )
						else:
							self.uno_monto_usd = 0
					else:
						self.uno_monto_usd = 0

				if self.uno_tipo_cambio == '6':
					
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.uno_concepto)])[0]
					padre = self.padre.periodo_id.id
					activofijo = self.env['reporte.patrimonio'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.patrimonio.line'].search([('patrimonio_id','=',activofijo[0].id),('partida','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.uno_monto_usd = resumen_activo_fijo[0].dlls  * (-1 if self.uno_t_monto_ifrs * resumen_activo_fijo[0].dlls < 0 else 1 )
						else:
							self.uno_monto_usd = 0
					else:
						self.uno_monto_usd = 0


				if self.uno_tipo_cambio == '7':
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.uno_concepto)])[0]
					padre = self.padre.periodo_id.id
					activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.depre.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.uno_monto_usd = resumen_activo_fijo[0].monto_usd  * (-1 if self.uno_t_monto_ifrs * resumen_activo_fijo[0].monto_usd < 0 else 1 )
						else:
							self.uno_monto_usd = 0
					else:
						self.uno_monto_usd = 0
			else:
				self.uno_monto_usd = 0

				
	@api.one
	def get_uno_monto_mxn(self):
		if self.uno_tipo_cuenta == '3':# and self.uno_formula != 'UTILIDAD':

			directorio = [
				[2,'UTILIDAD',"i._sum_total_utilidad_W(XX]"],
				[2,'AJUSTE_CONVERSION',"i._sum_ajuste_conversion_W(XX]"],	
				[2,'SUMA_PASIVO_CAPITAL_TOTAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO + TOTAL_CAPITAL_CONTABLE"],
				[2,'SUMA_PASIVO_CAPITAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO"],
				[2,'SUMA_DEL_ACTIVO',"TOTAL_CIRCULANTE + TOTAL_FIJO + TOTAL_DIFERIDO"],
				[2,'TOTAL_FIJO',"TOTAL_5 + TOTAL_ACTIVO_FIJO"],
				[2,'TOTAL_CIRCULANTE',"TOTAL_EXIGIBLE + TOTAL_REALIZABLE + TOTAL_DISPONIBLE"],
				[1,'DEUDA_INTRINSECA_ARRENDAMIENTO',"i._sum_total_W('11',XX]"],
				[1,'TOTAL_CAPITAL_CONTABLE',"i._sum_total_W('10',XX]"],
				[1,'TOTAL_PASIVO_FIJO',"i._sum_total_W('9',XX]"],
				[1,'TOTAL_PASIVO_CIRCULANTE',"i._sum_total_W('8',XX]"],
				[1,'VALOR_ACTUAL_ARRENDAMIENTO',"i._sum_total_W('7',XX]"],
				[1,'TOTAL_DIFERIDO',"i._sum_total_W('6',XX]"],
				[1,'TOTAL_5',"i._sum_total_W('5',XX]"],
				[1,'TOTAL_ACTIVO_FIJO',"i._sum_total_W('4',XX]"],
				[1,'TOTAL_EXIGIBLE',"i._sum_total_W('2',XX]"],
				[1,'TOTAL_REALIZABLE',"i._sum_total_W('3',XX]"],
				[1,'TOTAL_DISPONIBLE',"i._sum_total_W('1',XX]"],
				[1,'L[',"i._cal_orden_W('1',XX,"],
				[1,'R[',"i._cal_orden_W('2',XX,"],
			]

			i = self.env['rm.es.simple.mexicano.line'].search([('tipo_cuenta','=','3'),'|',('padre_activo','=',self.padre.id),('padre_pasivo','=',self.padre.id),('formula','=',self.uno_formula)])[0]
			val = 0
			try:
				tmp_formula = i.formula					
				for dir_m_ac in directorio:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2].replace('XX','2'))
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!', "val = " + i.formula.replace('L[','i.calculo_prog_mes_uno(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.formula )

			self.uno_monto_mxn = val
		elif not self.uno_tipo_cambio:
			self.uno_monto_mxn = 0
		else:
			periodo_padre = self.padre.periodo_id.id
			tipo_obj = self.env['tipo.cambio.mexicano'].search([('periodo_id','=',periodo_padre)])
			if len(tipo_obj)>0:
				tipo_obj = tipo_obj[0]
				tmp_m = 1
				if self.uno_tipo_cambio == '1':
					tmp_m = tipo_obj.t_cambio_mexicano
				if self.uno_tipo_cambio == '2':
					tmp_m = tipo_obj.t_cambio_mexicano
				if self.uno_tipo_cambio == '3':
					tmp_m = tipo_obj.t_cambio_mexicano
				if self.uno_tipo_cambio == '4':
					tmp_m = tipo_obj.t_cambio_mexicano

				self.uno_monto_mxn = self.uno_monto_usd * ( tmp_m )

				if self.uno_tipo_cambio == '5':
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.uno_concepto)])[0]
					padre = self.padre.periodo_id.id
					activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.activo.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.uno_monto_mxn = resumen_activo_fijo[0].pesos  * (-1 if self.uno_t_monto_ifrs * resumen_activo_fijo[0].pesos < 0 else 1 )
						else:
							self.uno_monto_mxn = 0
					else:
						self.uno_monto_mxn = 0

				if self.uno_tipo_cambio == '6':
					
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.uno_concepto)])[0]
					padre = self.padre.periodo_id.id 
					activofijo = self.env['reporte.patrimonio'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.patrimonio.line'].search([('patrimonio_id','=',activofijo[0].id),('partida','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.uno_monto_mxn = resumen_activo_fijo[0].valor_mxn  * (-1 if self.uno_t_monto_ifrs * resumen_activo_fijo[0].valor_mxn < 0 else 1 )
						else:
							self.uno_monto_mxn = 0
					else:
						self.uno_monto_mxn = 0

				if self.uno_tipo_cambio == '7':
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.uno_concepto)])[0]
					padre = self.padre.periodo_id.id
					activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.depre.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.uno_monto_mxn = resumen_activo_fijo[0].pesos  * (-1 if self.uno_t_monto_ifrs* resumen_activo_fijo[0].pesos < 0 else 1 )
						else:
							self.uno_monto_mxn = 0
					else:
						self.uno_monto_mxn = 0
			else:
				self.uno_monto_mxn = 0


	@api.one
	def get_dos_t_monto(self):
		self.dos_t_monto = self.dos_monto + self.dos_reclasif

	@api.one
	def get_dos_t_monto_ifrs(self):
		self.dos_t_monto_ifrs = self.dos_t_monto + self.dos_reclasif_ifrs


	@api.one
	def get_dos_ajuste(self):
		self.dos_ajuste = self.dos_t_monto_ifrs - self.dos_monto_usd

	@api.one
	def get_dos_tc_usd(self):
		if self.dos_monto_usd == 0:
			self.dos_tc_usd = 0
		else:
			self.dos_tc_usd = self.dos_t_monto_ifrs / self.dos_monto_usd

	@api.one
	def get_dos_ajuste_usd(self):
		self.dos_ajuste_usd = self.dos_monto_mxn - self.dos_monto_usd

	@api.one
	def get_dos_tc_mxn(self):
		if self.dos_monto_usd == 0:
			self.dos_tc_mxn = 0
		else:
			self.dos_tc_mxn = self.dos_monto_mxn / self.dos_monto_usd


	@api.one
	def get_dos_monto_usd(self):
		if self.dos_tipo_cuenta == '3':# and self.dos_formula != 'UTILIDAD':

			directorio = [
				[2,'UTILIDAD',"i._sum_total_utilidad_W(XX]"],
				[2,'AJUSTE_CONVERSION',"i._sum_ajuste_conversion_W(XX]"],	
				[2,'SUMA_PASIVO_CAPITAL_TOTAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO + TOTAL_CAPITAL_CONTABLE"],
				[2,'SUMA_PASIVO_CAPITAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO"],
				[2,'SUMA_DEL_ACTIVO',"TOTAL_CIRCULANTE + TOTAL_FIJO + TOTAL_DIFERIDO"],
				[2,'TOTAL_FIJO',"TOTAL_5 + TOTAL_ACTIVO_FIJO"],
				[2,'TOTAL_CIRCULANTE',"TOTAL_EXIGIBLE + TOTAL_REALIZABLE + TOTAL_DISPONIBLE"],
				[1,'DEUDA_INTRINSECA_ARRENDAMIENTO',"i._sum_total_W('11',XX]"],
				[1,'TOTAL_CAPITAL_CONTABLE',"i._sum_total_W('10',XX]"],
				[1,'TOTAL_PASIVO_FIJO',"i._sum_total_W('9',XX]"],
				[1,'TOTAL_PASIVO_CIRCULANTE',"i._sum_total_W('8',XX]"],
				[1,'VALOR_ACTUAL_ARRENDAMIENTO',"i._sum_total_W('7',XX]"],
				[1,'TOTAL_DIFERIDO',"i._sum_total_W('6',XX]"],
				[1,'TOTAL_5',"i._sum_total_W('5',XX]"],
				[1,'TOTAL_ACTIVO_FIJO',"i._sum_total_W('4',XX]"],
				[1,'TOTAL_EXIGIBLE',"i._sum_total_W('2',XX]"],
				[1,'TOTAL_REALIZABLE',"i._sum_total_W('3',XX]"],
				[1,'TOTAL_DISPONIBLE',"i._sum_total_W('1',XX]"],
				[1,'L[',"i._cal_orden_W('1',XX,"],
				[1,'R[',"i._cal_orden_W('2',XX,"],
			]

			i = self.env['rm.es.simple.mexicano.line'].search([('tipo_cuenta','=','3'),'|',('padre_activo','=',self.padre.id),('padre_pasivo','=',self.padre.id),('formula','=',self.dos_formula)])[0]
			val = 0
			try:
				tmp_formula = i.formula					
				for dir_m_ac in directorio:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2].replace('XX','1'))
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!', "val = " + i.formula.replace('L[','i.calculo_prog_mes_uno(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.formula )

			self.dos_monto_usd = val
		elif not self.dos_tipo_cambio:
			self.dos_monto_usd = 0
		else:
			periodo_padre = self.padre.periodo_id.id
			tipo_obj = self.env['tipo.cambio.mexicano'].search([('periodo_id','=',periodo_padre)])
			if len(tipo_obj)>0:
				tipo_obj = tipo_obj[0]
				tmp_m = 1
				if self.dos_tipo_cambio == '1':
					tmp_m = tipo_obj.t_cambio_compra
				if self.dos_tipo_cambio == '2':
					tmp_m = tipo_obj.t_cambio_venta
				if self.dos_tipo_cambio == '3':
					tmp_m = tipo_obj.promedio_compra
				if self.dos_tipo_cambio == '4':
					tmp_m = tipo_obj.promedio_venta

				self.dos_monto_usd = self.dos_t_monto_ifrs /  ( tmp_m )






				if self.dos_tipo_cambio == '5':
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.dos_concepto)])[0]
					padre = self.padre.periodo_id.id
					activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.activo.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.dos_monto_usd = resumen_activo_fijo[0].monto_usd  * (-1 if self.dos_t_monto_ifrs*resumen_activo_fijo[0].monto_usd < 0 else 1 )
						else:
							self.dos_monto_usd = 0
					else:
						self.dos_monto_usd = 0

				if self.dos_tipo_cambio == '6':
					
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.dos_concepto)])[0]
					padre = self.padre.periodo_id.id
					activofijo = self.env['reporte.patrimonio'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.patrimonio.line'].search([('patrimonio_id','=',activofijo[0].id),('partida','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.dos_monto_usd = resumen_activo_fijo[0].dlls  * (-1 if self.dos_t_monto_ifrs *resumen_activo_fijo[0].dlls < 0 else 1 )
						else:
							self.dos_monto_usd = 0
					else:
						self.dos_monto_usd = 0


				if self.dos_tipo_cambio == '7':
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.dos_concepto)])[0]
					padre = self.padre.periodo_id.id
					activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.depre.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.dos_monto_usd = resumen_activo_fijo[0].monto_usd  * (-1 if self.dos_t_monto_ifrs *resumen_activo_fijo[0].monto_usd < 0 else 1 )
						else:
							self.dos_monto_usd = 0
					else:
						self.dos_monto_usd = 0
			else:
				self.dos_monto_usd = 0

				
	@api.one
	def get_dos_monto_mxn(self):
		if self.dos_tipo_cuenta == '3':# and self.dos_formula != 'UTILIDAD':

			directorio = [
				[2,'UTILIDAD',"i._sum_total_utilidad_W(XX]"],
				[2,'AJUSTE_CONVERSION',"i._sum_ajuste_conversion_W(XX]"],	
				[2,'SUMA_PASIVO_CAPITAL_TOTAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO + TOTAL_CAPITAL_CONTABLE"],
				[2,'SUMA_PASIVO_CAPITAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO"],
				[2,'SUMA_DEL_ACTIVO',"TOTAL_CIRCULANTE + TOTAL_FIJO + TOTAL_DIFERIDO"],
				[2,'TOTAL_FIJO',"TOTAL_5 + TOTAL_ACTIVO_FIJO"],
				[2,'TOTAL_CIRCULANTE',"TOTAL_EXIGIBLE + TOTAL_REALIZABLE + TOTAL_DISPONIBLE"],
				[1,'DEUDA_INTRINSECA_ARRENDAMIENTO',"i._sum_total_W('11',XX]"],
				[1,'TOTAL_CAPITAL_CONTABLE',"i._sum_total_W('10',XX]"],
				[1,'TOTAL_PASIVO_FIJO',"i._sum_total_W('9',XX]"],
				[1,'TOTAL_PASIVO_CIRCULANTE',"i._sum_total_W('8',XX]"],
				[1,'VALOR_ACTUAL_ARRENDAMIENTO',"i._sum_total_W('7',XX]"],
				[1,'TOTAL_DIFERIDO',"i._sum_total_W('6',XX]"],
				[1,'TOTAL_5',"i._sum_total_W('5',XX]"],
				[1,'TOTAL_ACTIVO_FIJO',"i._sum_total_W('4',XX]"],
				[1,'TOTAL_EXIGIBLE',"i._sum_total_W('2',XX]"],
				[1,'TOTAL_REALIZABLE',"i._sum_total_W('3',XX]"],
				[1,'TOTAL_DISPONIBLE',"i._sum_total_W('1',XX]"],
				[1,'L[',"i._cal_orden_W('1',XX,"],
				[1,'R[',"i._cal_orden_W('2',XX,"],
			]

			i = self.env['rm.es.simple.mexicano.line'].search([('tipo_cuenta','=','3'),'|',('padre_activo','=',self.padre.id),('padre_pasivo','=',self.padre.id),('formula','=',self.dos_formula)])[0]
			val = 0
			try:
				tmp_formula = i.formula					
				for dir_m_ac in directorio:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2].replace('XX','2'))
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!', "val = " + i.formula.replace('L[','i.calculo_prog_mes_uno(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.formula )

			self.dos_monto_mxn = val
		elif not self.dos_tipo_cambio:
			self.dos_monto_mxn = 0
		else:
			periodo_padre = self.padre.periodo_id.id
			tipo_obj = self.env['tipo.cambio.mexicano'].search([('periodo_id','=',periodo_padre)])
			if len(tipo_obj)>0:
				tipo_obj = tipo_obj[0]
				tmp_m = 1
				if self.dos_tipo_cambio == '1':
					tmp_m = tipo_obj.t_cambio_mexicano
				if self.dos_tipo_cambio == '2':
					tmp_m = tipo_obj.t_cambio_mexicano
				if self.dos_tipo_cambio == '3':
					tmp_m = tipo_obj.t_cambio_mexicano
				if self.dos_tipo_cambio == '4':
					tmp_m = tipo_obj.t_cambio_mexicano

				self.dos_monto_mxn = self.dos_monto_usd * ( tmp_m )
				

				if self.dos_tipo_cambio == '5':
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.dos_concepto)])[0]
					padre = self.padre.periodo_id.id
					activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.activo.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.dos_monto_mxn = resumen_activo_fijo[0].pesos  * (-1 if self.dos_t_monto_ifrs * resumen_activo_fijo[0].pesos < 0 else 1 )
						else:
							self.dos_monto_mxn = 0
					else:
						self.dos_monto_mxn = 0

				if self.dos_tipo_cambio == '6':
					
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.dos_concepto)])[0]
					padre = self.padre.periodo_id.id 
					activofijo = self.env['reporte.patrimonio'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.patrimonio.line'].search([('patrimonio_id','=',activofijo[0].id),('partida','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.dos_monto_mxn = resumen_activo_fijo[0].valor_mxn  * (-1 if self.dos_t_monto_ifrs * resumen_activo_fijo[0].valor_mxn < 0 else 1 )
						else:
							self.dos_monto_mxn = 0
					else:
						self.dos_monto_mxn = 0

				if self.dos_tipo_cambio == '7':
					linea_aa = self.env['rm.balance.config.mexicano.line'].search([('concepto','=',self.dos_concepto)])[0]
					padre = self.padre.periodo_id.id
					activofijo = self.env['reporte.activofijo'].search([('name','=',padre)])
					if len(activofijo) >0:
						resumen_activo_fijo = self.env['resumen.depre.line'].search([('activofijo_id','=',activofijo[0].id),('grupo','=',linea_aa.orden)])
						if len(resumen_activo_fijo)>0:
							self.dos_monto_mxn = resumen_activo_fijo[0].pesos  * (-1 if self.dos_t_monto_ifrs * resumen_activo_fijo[0].pesos < 0 else 1 )
						else:
							self.dos_monto_mxn = 0
					else:
						self.dos_monto_mxn = 0

			else:
				self.dos_monto_mxn = 0

	orden = fields.Integer('Orden',required=True)

	uno_concepto = fields.Char('Concepto')
	uno_tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=False)
	uno_grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos Fijos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Grupo',readonly=True )
	uno_formula = fields.Char('Formula')
	uno_resaltado = fields.Boolean('Resaltado')
	uno_bordes = fields.Boolean('Bordes')
	uno_monto = fields.Float('Monto Soles',digits=(12,2))
	uno_reclasif = fields.Float('Reclasif. +/-',digits=(12,2))
	uno_tipo_cambio = fields.Selection([('1','Tipo Compra Cierre'),('2','Tipo Venta Cierre'),('3','Tipo Promedio Compras'),('4','Tipo Promedio Ventas'),('5','Activo Fijo-Cédula'),('6','Patrimonio-Cédula'),('7','Depreciacion-Cédula')],'Tipo de Cambio',required=False, default="1")	
	
	uno_ref = fields.Integer('Ref')
	uno_t_monto = fields.Float('Monto Soles',digits=(12,2))
	uno_reclasif_ifrs = fields.Float('Reclasifc. IFRS',digits=(12,2))
	uno_t_monto_ifrs = fields.Float('Monto Soles IFRS',digits=(12,2))
	uno_ajuste = fields.Float('Ajuste +/-',digits=(12,2))
	uno_tc_usd = fields.Float('T.C. SOL vs USD', digits=(12,3))
	uno_monto_usd = fields.Float('Monto USD',digits=(12,2))
	uno_ajuste_usd = fields.Float('Ajuste +/-',digits=(12,2))
	uno_tc_mxn = fields.Float('T.C. USD vs MXN',digits=(12,3))
	uno_monto_mxn = fields.Float('Monto MXN',digits=(12,2))

	dos_concepto = fields.Char('Concepto')
	dos_tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=False)
	dos_grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos Fijos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Grupo',readonly=True)
	dos_formula = fields.Char('Formula')
	dos_tipo_cambio = fields.Selection([('1','Tipo Compra Cierre'),('2','Tipo Venta Cierre'),('3','Tipo Promedio Compras'),('4','Tipo Promedio Ventas'),('5','Activo Fijo-Cédula'),('6','Patrimonio-Cédula'),('7','Depreciacion-Cédula')],'Tipo de Cambio',required=False, default="1")	
	dos_resaltado = fields.Boolean('Resaltado')
	dos_bordes = fields.Boolean('Bordes')
	dos_monto = fields.Float('Monto Soles',digits=(12,2))
	dos_reclasif = fields.Float('Reclasif. +/-',digits=(12,2))
	dos_ref = fields.Integer('Ref')
	dos_t_monto = fields.Float('Monto Soles',digits=(12,2))
	dos_reclasif_ifrs = fields.Float('Reclasifc. IFRS',digits=(12,2))
	dos_t_monto_ifrs = fields.Float('Monto Soles IFRS',digits=(12,2))
	dos_ajuste = fields.Float('Ajuste +/-',digits=(12,2))
	dos_tc_usd = fields.Float('T.C. SOL vs USD', digits=(12,3))
	dos_monto_usd = fields.Float('Monto USD',digits=(12,2))
	dos_ajuste_usd = fields.Float('Ajuste +/-',digits=(12,2))
	dos_tc_mxn = fields.Float('T.C. USD vs MXN',digits=(12,3))
	dos_monto_mxn = fields.Float('Monto MXN',digits=(12,2))

	padre = fields.Many2one('rm.es.mexicano','Cabezera')

	_order = 'orden'


	@api.one
	def _sum_total_utilidad_(self,mes):
		calculo = 0
		for i in self.env['rm.es.mexicano.line'].search([('padre','=',self.padre.id),('uno_grupo_cuenta','in',('1','2','3','4','5','6') ),('uno_tipo_cuenta','=','1')]):
			if mes == 1:
				calculo += i.uno_monto_mes
			else:
				calculo += i.uno_monto_mes_anterior
		for i in self.env['rm.es.mexicano.line'].search([('padre','=',self.padre.id),('dos_grupo_cuenta','in',('1','2','3','4','5','6') ),('dos_tipo_cuenta','=','1')]):
			if mes == 1:
				calculo += i.dos_monto_mes
			else:
				calculo += i.dos_monto_mes_anterior


		
		for i in self.env['rm.es.mexicano.line'].search([('padre','=',self.padre.id),('uno_grupo_cuenta','in',('8','9','10') ),('uno_tipo_cuenta','=','1')]):
			if mes == 1:
				calculo -= i.uno_monto_mes
			else:
				calculo -= i.uno_monto_mes_anterior
		for i in self.env['rm.es.mexicano.line'].search([('padre','=',self.padre.id),('dos_grupo_cuenta','in',('8','9','10') ),('dos_tipo_cuenta','=','1')]):
			if mes == 1:
				calculo -= i.dos_monto_mes
			else:
				calculo -= i.dos_monto_mes_anterior



		return calculo



	@api.one
	def _sum_ajuste_conversion_(self,mes):
		calculo = 0
		return calculo


	@api.one
	def _sum_total_(self,grupo,mes):
		calculo = 0

		if grupo == '10':
			for i in self.env['rm.es.mexicano.line'].search([('padre','=',self.padre.id),('uno_grupo_cuenta','=',grupo),('uno_tipo_cuenta','in',('1','3') )]):
				if i.uno_tipo_cuenta == '1':
					if mes == 1:
						calculo += i.uno_monto_mes
					else:
						calculo += i.uno_monto_mes_anterior
				else:
					if i.uno_concepto=='UTILIDAD O (PERDIDA) DEL EJERCICIO' or i.uno_concepto == 'AJUSTE POR CONVERSION':
						if mes == 1:
							calculo += i.uno_monto_mes
						else:
							calculo += i.uno_monto_mes_anterior	

			for i in self.env['rm.es.mexicano.line'].search([('padre','=',self.padre.id),('dos_grupo_cuenta','=',grupo),('dos_tipo_cuenta','in',('1','3') )]):
				if i.dos_tipo_cuenta == '1':
					if mes == 1:
						calculo += i.dos_monto_mes
					else:
						calculo += i.dos_monto_mes_anterior
				else:
					if i.dos_concepto=='UTILIDAD O (PERDIDA) DEL EJERCICIO' or i.dos_concepto == 'AJUSTE POR CONVERSION':
						if mes == 1:
							calculo += i.dos_monto_mes
						else:
							calculo += i.dos_monto_mes_anterior

		else:

			for i in self.env['rm.es.mexicano.line'].search([('padre','=',self.padre.id),('uno_grupo_cuenta','=',grupo),('uno_tipo_cuenta','=','1')]):
				if mes == 1:
					calculo += i.uno_monto_mes
				else:
					calculo += i.uno_monto_mes_anterior

			for i in self.env['rm.es.mexicano.line'].search([('padre','=',self.padre.id),('dos_grupo_cuenta','=',grupo),('dos_tipo_cuenta','=','1')]):
				if mes == 1:
					calculo += i.dos_monto_mes
				else:
					calculo += i.dos_monto_mes_anterior

		return calculo

	"""
	@api.one
	def _sum_total_(self,grupo,mes):
		calculo = 0
		for i in self.env['rm.es.mexicano.line'].search([('padre','=',self.padre.id),('uno_grupo_cuenta','=',grupo)]):
			if mes == 1:
				calculo += i.uno_monto_mes
			else:
				calculo += i.uno_monto_mes_anterior

		for i in self.env['rm.es.mexicano.line'].search([('padre','=',self.padre.id),('dos_grupo_cuenta','=',grupo)]):
			if mes == 1:
				calculo += i.dos_monto_mes
			else:
				calculo += i.dos_monto_mes_anterior

		return calculo
	"""
	@api.one
	def _cal_orden_(self,grupo,mes,orden):
		calculo = 0

		for i in self.env['rm.es.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			if grupo==1:
				if mes == 1:
					calculo += i.uno_monto_mes
				else:
					calculo += i.uno_monto_mes_anterior
			else:
				if mes == 1:
					calculo += i.dos_monto_mes
				else:
					calculo += i.dos_monto_mes_anterior

		return calculo


class rm_es_mexicano(models.Model):
	_name= 'rm.es.mexicano'

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

	lineas = fields.One2many('rm.es.mexicano.line','padre','Lineas')

	lineas_activo = fields.One2many('rm.es.simple.mexicano.line','padre_activo','Lineas')
	lineas_pasivo = fields.One2many('rm.es.simple.mexicano.line','padre_pasivo','Lineas')

	_rec_name = 'periodo_id'


	@api.one
	def write(self,vals):
		t = super(rm_es_mexicano,self).write(vals)
		self.refresh()

		t_i = self.env['rm.es.simple.mexicano.line'].search(['|',('padre_activo','=',self.id),('padre_pasivo','=',self.id)])

		for i in self.lineas:
			i.unlink()

		for i in t_i:
			tt = self.env['rm.es.mexicano.line'].search( [('orden','=',i.orden),('padre','=',self.id)] )
			if len(tt)> 0:
				if i.padre_activo.id:
					tt.uno_concepto = i.concepto
					tt.uno_tipo_cuenta = i.tipo_cuenta
					tt.uno_grupo_cuenta = i.grupo_cuenta
					tt.uno_formula = i.formula
					tt.uno_resaltado = i.resaltado
					tt.uno_bordes = i.bordes
					tt.uno_monto = i.monto
					tt.uno_reclasif = i.reclasif
					tt.uno_ref = i.ref
					tt.uno_reclasif_ifrs = i.reclasif_ifrs
					tt.uno_tipo_cambio = i.tipo_cambio

					tt.uno_t_monto = i.t_monto
					tt.uno_t_monto_ifrs = i.t_monto_ifrs
					tt.uno_ajuste = i.ajuste
					tt.uno_tc_usd = i.tc_usd
					tt.uno_monto_usd = i.monto_usd
					tt.uno_ajuste_usd = i.ajuste_usd
					tt.uno_tc_mxn = i.tc_mxn
					tt.uno_monto_mxn = i.monto_mxn

				else:




					tt.dos_concepto = i.concepto
					tt.dos_tipo_cuenta = i.tipo_cuenta
					tt.dos_grupo_cuenta = i.grupo_cuenta
					tt.dos_formula = i.formula
					tt.dos_resaltado = i.resaltado
					tt.dos_bordes = i.bordes
					tt.dos_monto = i.monto
					tt.dos_reclasif = i.reclasif
					tt.dos_ref = i.ref
					tt.dos_reclasif_ifrs = i.reclasif_ifrs
					tt.dos_tipo_cambio = i.tipo_cambio


					tt.dos_t_monto = i.t_monto
					tt.dos_t_monto_ifrs = i.t_monto_ifrs
					tt.dos_ajuste = i.ajuste
					tt.dos_tc_usd = i.tc_usd
					tt.dos_monto_usd = i.monto_usd
					tt.dos_ajuste_usd = i.ajuste_usd
					tt.dos_tc_mxn = i.tc_mxn
					tt.dos_monto_mxn = i.monto_mxn
			else:
				vals = {}
				if i.padre_activo.id:

					vals = {
						'orden': i.orden,
						'uno_concepto' : i.concepto,
						'uno_tipo_cuenta' :i.tipo_cuenta,
						'uno_grupo_cuenta' :i.grupo_cuenta,
						'uno_formula' :i.formula,
						'uno_resaltado' :i.resaltado,
						'uno_bordes' :i.bordes,
						'uno_monto' :i.monto,
						'uno_reclasif':i.reclasif,
						'uno_ref':i.ref,
						'uno_reclasif_ifrs':i.reclasif_ifrs,
						'uno_tipo_cambio': i.tipo_cambio,
					'uno_t_monto' : i.t_monto,
					'uno_t_monto_ifrs' : i.t_monto_ifrs,
					'uno_ajuste' : i.ajuste,
					'uno_tc_usd' : abs(i.tc_usd),
					'uno_monto_usd' : i.monto_usd,
					'uno_ajuste_usd' : i.ajuste_usd,
					'uno_tc_mxn' : abs(i.tc_mxn),
					'uno_monto_mxn' : i.monto_mxn,
						'dos_concepto' :'',
						'dos_tipo_cuenta' :'',
						'dos_grupo_cuenta' :'',
						'dos_formula' :'',
						'dos_resaltado' :False,
						'dos_bordes' :False,
						'dos_monto':0,
						'dos_reclasif':0,
						'dos_ref':0,
						'dos_reclasif_ifrs':0,
						'dos_tipo_cambio':False,
						'padre': self.id,
					}
				else:

					vals = {
						'orden': i.orden,
						'uno_concepto' : '',
						'uno_tipo_cuenta' :'',
						'uno_grupo_cuenta' :'',
						'uno_formula' :0,
						'uno_resaltado' :False,
						'uno_bordes' :False,
						'uno_monto' :0,
						'uno_reclasif':0,
						'uno_ref':0,
						'uno_reclasif_ifrs':0,
						'uno_tipo_cambio':0,
						'dos_concepto' :i.concepto,
						'dos_tipo_cuenta' :i.tipo_cuenta,
						'dos_grupo_cuenta' :i.grupo_cuenta,
						'dos_formula' :i.formula,
						'dos_resaltado' :i.resaltado,
						'dos_bordes' :i.bordes,
						'dos_monto':i.monto,
						'dos_reclasif':i.reclasif,
						'dos_ref':i.ref,
						'dos_reclasif_ifrs':i.reclasif_ifrs,
						'dos_tipo_cambio':i.tipo_cambio,						
						'dos_t_monto' : i.t_monto,
						'dos_t_monto_ifrs' : i.t_monto_ifrs,
						'dos_ajuste' : i.ajuste,
						'dos_tc_usd' : abs(i.tc_usd),
						'dos_monto_usd' : i.monto_usd,
						'dos_ajuste_usd' : i.ajuste_usd,
						'dos_tc_mxn' : abs(i.tc_mxn),
						'dos_monto_mxn' : i.monto_mxn,
						'padre': self.id,
					}
				self.env['rm.es.mexicano.line'].create(vals)




	@api.one
	def traer_datos(self):
		t_i = self.env['rm.balance.config.mexicano.line'].search([])
		if len(t_i) >0 :
			pass
		else:
			raise osv.except_osv('Alerta!', "No hay plantilla configurada")

		for i in self.lineas_activo:
			i.unlink()
		for i in self.lineas_pasivo:
			i.unlink()


		orden_tmp = 0
		#### AQUI COMIENZA EL JUEGO DONDE ESTAN LAS POSICIONES
		#uno_tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=True)
		#uno_grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos Fijos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Grupo',readonly=True )
	
		vals = {
			'orden': orden_tmp,
			'concepto' : 'CIRCULANTE',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'1',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'1',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)

		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"1")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'1',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto_mes' :0,
				'monto_mes_anterior' :0,
				'tipo_cambio':i.tipo_cambio,
				'padre_activo': self.id,
			}
			orden_tmp +=1
			self.env['rm.es.simple.mexicano.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Disponible',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'1',
			'formula' :'TOTAL_DISPONIBLE',
			'resaltado' :True,
			'bordes' :True,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'1',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'concepto' :False,
			'tipo_cuenta' :False,
			'grupo_cuenta' :False,
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes':0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)

		### FINALIZO DISPONIBLE

		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"2")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'2',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto_mes' :0,
				'monto_mes_anterior' :0,
				'tipo_cambio':i.tipo_cambio,
				'padre_activo': self.id,
			}
			orden_tmp +=1
			self.env['rm.es.simple.mexicano.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Exigible',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'2',
			'formula' :'TOTAL_EXIGIBLE',
			'resaltado' :True,
			'bordes' :True,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'2',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
		#### TERMINO EXIGIBLE

		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"3")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'3',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto_mes' :0,
				'monto_mes_anterior' :0,
				'tipo_cambio':i.tipo_cambio,
				'padre_activo': self.id,
			}
			orden_tmp +=1
			self.env['rm.es.simple.mexicano.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Realizable',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'3',
			'formula' :'TOTAL_REALIZABLE',
			'resaltado' :True,
			'bordes' :True,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'3',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Circulante',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'3',
			'formula' :'TOTAL_CIRCULANTE',
			'resaltado' :True,
			'bordes' :True,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
		orden_tmp +=1
		#### TERMINO REALIZABLE Y CIRCULANTE

		### AQUI COMIENZA FIJO

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'FIJO',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)

		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"4")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'4',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto_mes' :0,
				'monto_mes_anterior' :0,
				'tipo_cambio':i.tipo_cambio,
				'padre_activo': self.id,
			}
			orden_tmp +=1
			self.env['rm.es.simple.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Activo Fijo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'4',
			'formula' :'TOTAL_ACTIVO_FIJO',
			'resaltado' :True,
			'bordes' :True,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)


		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)

		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"5")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'5',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto_mes' :0,
				'monto_mes_anterior' :0,
				'tipo_cambio':i.tipo_cambio,
				'padre_activo': self.id,
			}
			orden_tmp +=1
			self.env['rm.es.simple.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Fijo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'5',
			'formula' :'TOTAL_FIJO',
			'resaltado' :True,
			'bordes' :True,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
		orden_tmp +=1 

		### AQUI COMIENZA Diferido

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'6',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'DIFERIDO',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'6',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'6',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)

		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"6")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'6',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto_mes' :0,
				'monto_mes_anterior' :0,
				'tipo_cambio':i.tipo_cambio,
				'padre_activo': self.id,
			}
			orden_tmp +=1
			self.env['rm.es.simple.mexicano.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Suma del Activo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'6',
			'formula' :'SUMA_DEL_ACTIVO',
			'resaltado' :True,
			'bordes' :True,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_activo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)


		orden_tmp +=1

		#### AQUI TERMINA EL JUEGO DEL LADO IZQUIERDA




		orden_tmp = 0

		vals = {
			'orden': orden_tmp,
			'concepto' : 'CIRCULANTE',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'8',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
			
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'8',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
			
		orden_tmp +=1


		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"8")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'8',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto_mes' :0,
				'monto_mes_anterior' :0,
				'tipo_cambio':i.tipo_cambio,
				'padre_pasivo': self.id,
			}
			self.env['rm.es.simple.mexicano.line'].create(vals)


			orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Circulante',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'8',
			'formula' :'TOTAL_PASIVO_CIRCULANTE',
			'resaltado' :True,
			'bordes' :True,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
			
		orden_tmp +=1

		### segundo derecho
		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'9',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
		
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : 'FIJO',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'9',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
			
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'9',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
			
		orden_tmp +=1


		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"9")] ).sorted(lambda r: r.orden):
		
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'9',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto_mes' :0,
				'monto_mes_anterior' :0,
				'tipo_cambio':i.tipo_cambio,
				'padre_pasivo': self.id,
			}
			self.env['rm.es.simple.mexicano.line'].create(vals)

			orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Fijo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'9',
			'formula' :'TOTAL_PASIVO_FIJO',
			'resaltado' :True,
			'bordes' :True,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
			
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'9',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
			
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Suma del Pasivo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'9',
			'formula' :'SUMA_PASIVO_CAPITAL',
			'resaltado' :True,
			'bordes' :True,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
			
		orden_tmp +=1
		##### AKI LA TERCERAE Y ULTIMA

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'10',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
		
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : 'CAPITAL CONTABLE',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'10',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
		
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'10',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
		
		orden_tmp +=1


		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"10")] ).sorted(lambda r: r.orden):
		
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'10',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto_mes' :0,
				'monto_mes_anterior' :0,
				'tipo_cambio':i.tipo_cambio,
				'padre_pasivo': self.id,
			}
			self.env['rm.es.simple.mexicano.line'].create(vals)

			orden_tmp +=1
		###########

		vals = {
			'orden': orden_tmp,
			'concepto' : 'UTILIDAD O (PERDIDA) DEL EJERCICIO',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'10',
			'formula' :'UTILIDAD',
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
			
		orden_tmp +=1


		###########

		#vals = {
		#	'orden': orden_tmp,
		#	'concepto' : 'AJUSTE POR CONVERSION',
		#	'tipo_cuenta' :'3',
		#	'grupo_cuenta' :'10',
		#	'formula' :'AJUSTE_CONVERSION',
		#	'resaltado' :False,
		#	'bordes' :False,
		#	'monto_mes' :0,
		#	'monto_mes_anterior' :0,
		#	'padre_pasivo': self.id,
		#}
		#self.env['rm.es.simple.mexicano.line'].create(vals)
			
		#orden_tmp +=1

		#############

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Capital Contable',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'10',
			'formula' :'TOTAL_CAPITAL_CONTABLE',
			'resaltado' :True,
			'bordes' :True,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
			
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'10',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
			
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Suma del Pasivo y Capital',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'10',
			'formula' :'SUMA_PASIVO_CAPITAL_TOTAL',
			'resaltado' :True,
			'bordes' :True,
			'monto_mes' :0,
			'monto_mes_anterior' :0,
			'padre_pasivo': self.id,
		}
		self.env['rm.es.simple.mexicano.line'].create(vals)
			
		orden_tmp +=1
		"""
			[2,'UTILIDAD',"SUMA_DEL_ACTIVO - ( SUMA_PASIVO_CAPITAL )"],
			[2,'SUMA_PASIVO_CAPITAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO"],
			[2,'SUMA_DEL_ACTIVO',"TOTAL_CIRCULANTE + TOTAL_FIJO + TOTAL_DIFERIDO"],
			[2,'TOTAL_FIJO',"TOTAL_5 + TOTAL_ACTIVO_FIJO"],
			[2,'TOTAL_CIRCULANTE',"TOTAL_EXIGIBLE + TOTAL_REALIZABLE + TOTAL_DISPONIBLE"],
			[1,'DEUDA_INTRINSECA_ARRENDAMIENTO',"i._sum_total_('11',1]"],
			[1,'TOTAL_CAPITAL_CONTABLE',"i._sum_total_('10',1]"],
			[1,'TOTAL_PASIVO_FIJO',"i._sum_total_('9',1]"],
			[1,'TOTAL_PASIVO_CIRCULANTE',"i._sum_total_('8',1]"],
			[1,'VALOR_ACTUAL_ARRENDAMIENTO',"i._sum_total_('7',1]"],
			[1,'TOTAL_DIFERIDO',"i._sum_total_('6',1]"],
			[1,'TOTAL_5',"i._sum_total_('5',1]"],
			[1,'TOTAL_ACTIVO_FIJO',"i._sum_total_('4',1]"],
			[1,'TOTAL_EXIGIBLE',"i._sum_total_('2',1]"],
			[1,'TOTAL_REALIZABLE',"i._sum_total_('3',1]"],
			[1,'TOTAL_DISPONIBLE',"i._sum_total_('1',1]"],
			[1,'L[',"i._cal_orden_('1','1',"],
			[1,'R[',"i._cal_orden_('2','1',"],
		"""
		#### AQUI TERMINA EL JUEGO








		for i in self.lineas:
			if i.uno_tipo_cuenta == '1' or i.uno_tipo_cuenta == '2':
				i.uno_monto= 0

			if i.dos_tipo_cuenta == '1' or i.dos_tipo_cuenta == '2':
				i.dos_monto= 0


		param_report = self.env['reporte.parametros'].search([])[0]
		cuentas_list = []
		if param_report.tributos.id:
			for m in self.env['account.account'].search( [('balance_type_mex_id','=',param_report.tributos.id)]):

				cuentas_list.append(m)
				self.env.cr.execute(""" 
					select (debe-haber) from get_hoja_trabajo_detalle_registro_analisis_ht(false,(substring('""" + self.periodo_id.code + """'::varchar,4,4)||'00')::integer,periodo_num('""" + self.periodo_id.code +"""'))
					where cuenta = '""" + m.code + """'
					""")
				tmp_in = 0
				for klg in self.env.cr.fetchall():
					tmp_in = klg[0]

				print m.code, tmp_in
				if tmp_in>=0:
					m.balance_type_mex_id = param_report.impuesto_recuperar.id
				else:
					m.balance_type_mex_id = param_report.impuesto_pagar.id


		self.env.cr.execute("""
update rm_es_simple_mexicano_line
set monto= T1.monto
from ( select artm.id, artm.concepto, CASE WHEN artm.grupo_cuenta = '1' or artm.grupo_cuenta = '2' or artm.grupo_cuenta = '3' or artm.grupo_cuenta = '4' or artm.grupo_cuenta = '5' or artm.grupo_cuenta = '6' or artm.grupo_cuenta = '7'
THEN sum(debit-credit) ELSE sum(credit-debit) END as monto from
account_account aa
inner join account_move_line aml on aml.account_id = aa.id
inner join account_move am on am.id = aml.move_id
inner join account_period ap on ap.id = am.period_id
inner join rm_balance_config_mexicano_line artm on artm.id = aa.balance_type_mex_id
where (artm.tipo_cuenta = '1'  ) and periodo_num(ap.code) <= periodo_num('""" + self.periodo_id.code + """')
and periodo_num(ap.code)>= (substring('""" + self.periodo_id.code + """'::varchar,4,4)||'00')::integer
and am.state != 'draft'
group by artm.id, artm.concepto
) T1
where rm_es_simple_mexicano_line.concepto = T1.concepto
and ( rm_es_simple_mexicano_line.padre_pasivo = """ + str(self.id) + """ or rm_es_simple_mexicano_line.padre_activo = """ + str(self.id) + """ )
			""")
					

		for ii in cuentas_list:
			ii.balance_type_mex_id = param_report.tributos.id 


		self.refresh()
		self.write({})


	@api.one
	def calculate(self):
		
		for i in self.lineas_activo:
			i.refresh()		
		for i in self.lineas_pasivo:
			i.refresh()		

		directorio = [
			[2,'UTILIDAD',"i._sum_total_utilidad_(XX]"],
			[2,'AJUSTE_CONVERSION',"i._sum_ajuste_conversion_(XX]"],			
			[2,'SUMA_PASIVO_CAPITAL_TOTAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO + TOTAL_CAPITAL_CONTABLE"],
			[2,'SUMA_PASIVO_CAPITAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO"],
			[2,'SUMA_DEL_ACTIVO',"TOTAL_CIRCULANTE + TOTAL_FIJO + TOTAL_DIFERIDO"],
			[2,'TOTAL_FIJO',"TOTAL_5 + TOTAL_ACTIVO_FIJO"],
			[2,'TOTAL_CIRCULANTE',"TOTAL_EXIGIBLE + TOTAL_REALIZABLE + TOTAL_DISPONIBLE"],
			[1,'DEUDA_INTRINSECA_ARRENDAMIENTO',"i._sum_total_('11',XX]"],
			[1,'TOTAL_CAPITAL_CONTABLE',"i._sum_total_('10',XX]"],
			[1,'TOTAL_PASIVO_FIJO',"i._sum_total_('9',XX]"],
			[1,'TOTAL_PASIVO_CIRCULANTE',"i._sum_total_('8',XX]"],
			[1,'VALOR_ACTUAL_ARRENDAMIENTO',"i._sum_total_('7',XX]"],
			[1,'TOTAL_DIFERIDO',"i._sum_total_('6',XX]"],
			[1,'TOTAL_5',"i._sum_total_('5',XX]"],
			[1,'TOTAL_ACTIVO_FIJO',"i._sum_total_('4',XX]"],
			[1,'TOTAL_EXIGIBLE',"i._sum_total_('2',XX]"],
			[1,'TOTAL_REALIZABLE',"i._sum_total_('3',XX]"],
			[1,'TOTAL_DISPONIBLE',"i._sum_total_('1',XX]"],
			[1,'L[',"i._cal_orden_('1',XX,"],
			[1,'R[',"i._cal_orden_('2',XX,"],
		]

		for i in self.env['rm.es.simple.mexicano.line'].search([('tipo_cuenta','=','3'),'|',('padre_activo','=',self.id),('padre_pasivo','=',self.id)]):
			val = 0
			try:
				tmp_formula = i.formula					
				for dir_m_ac in directorio:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2].replace('XX','1'))

				print "formula 1:",tmp_formula.replace(']',')[0]')
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!', "val = " + i.formula.replace('L[','i.calculo_prog_mes_uno(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.formula )

			print val
			i.monto = val



			val = 0
			try:
				tmp_formula = i.formula					
				for dir_m_ac in directorio:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2].replace('XX','2'))

				print "formula 2:",tmp_formula.replace(']',')[0]')
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!', "val = " + i.formula.replace('L[','i.calculo_prog_mes_uno(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.formula )

			print val
			i.reclasif = val




			val = 0
			try:
				tmp_formula = i.formula					
				for dir_m_ac in directorio:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2].replace('XX','3'))

				print "formula 3:",tmp_formula.replace(']',')[0]')
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!', "val = " + i.formula.replace('L[','i.calculo_prog_mes_uno(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.formula )

			print val
			i.reclasif_ifrs = val

		self.refresh()
		self.write({})

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

		workbook = Workbook(direccion +'Reporte_balance_mexicano.xlsx')
		worksheet = workbook.add_worksheet(u"Estado de Situación")
		worksheet_2 = workbook.add_worksheet(u"Partidas Monetarias")
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


		#worksheet.insert_image('A2', 'calidra.jpg')
		worksheet.merge_range(1,0,1,30, u'CALQUIPA S.A.C', boldcenter)
		worksheet.merge_range(2,0,2,30, u'INTEGRACIÓN DEL PARTIDAS MONETARIAS MON.REG. (SOLES(S)) '+ str(self.periodo_id.code.split('/')[1]) , boldcenter)
	
		worksheet.merge_range(4,0,4,1, u'CUENTAS ACTIVO', boldcenter)

		worksheet.write(4,0, u'ACTIVO', boldtop)
		worksheet.write(5,0, u'', boldbot)
		worksheet.write(4,1, u'', boldtop)
		worksheet.write(5,1, u'', boldbot)
		worksheet.write(4,2, u'', boldtop)
		worksheet.write(5,2, u'', boldbot)
		#worksheet.write(4,3, dic_anio[self.periodo_id.code.split('/')[0]].upper(), boldcentertop)
		#worksheet.write(5,3, 'SOLES', boldcenterbot)
		#worksheet.write(4,4, 'RECLASIF', boldcentertop)
		#worksheet.write(5,4, '+/-', boldcenterbot)
		#worksheet.write(4,5, '', boldcentertop)
		#worksheet.write(5,5, 'Ref', boldcenterbot)
		#worksheet.write(4,6, dic_anio[self.periodo_id.code.split('/')[0]].upper(), boldcentertop)
		#worksheet.write(5,6, 'SOLES', boldcenterbot)
		#worksheet.write(4,7, 'RECLASIF', boldcentertop)
		#worksheet.write(5,7, 'IFRS', boldcenterbot)		

		worksheet.write(4,3, dic_anio[self.periodo_id.code.split('/')[0]].upper(), boldcentertop)
		worksheet.write(5,3, 'SOLES IFRS', boldcenterbot)
		#worksheet.write(4,9, 'AJUSTE', boldcentertop)
		#worksheet.write(5,9, '+/-', boldcenterbot)
		worksheet.write(4,4, 'T.C.', boldcentertop)
		worksheet.write(5,4, 'SOL VS USD', boldcenterbot)
		worksheet.write(4,5, dic_anio[self.periodo_id.code.split('/')[0]].upper(), boldcentertop)
		worksheet.write(5,5, 'USD', boldcenterbot)
		#worksheet.write(4,12, 'AJUSTE', boldcentertop)
		#worksheet.write(5,12, '+/-', boldcenterbot)
		worksheet.write(4,6, 'T.C.', boldcentertop)
		worksheet.write(5,6, 'USD VS MXN', boldcenterbot)
		worksheet.write(4,7, dic_anio[self.periodo_id.code.split('/')[0]].upper(), boldcentertop)
		worksheet.write(5,7, 'MXN', boldcenterbot)
		

		worksheet.write(4,9, u'PASIVO', boldtop)
		worksheet.write(5,9, u'', boldbot)
		worksheet.write(4,10, u'', boldtop)
		worksheet.write(5,10, u'', boldbot)
		worksheet.write(4,11, u'', boldtop)
		worksheet.write(5,11, u'', boldbot)
		#worksheet.write(4,19, dic_anio[self.periodo_id.code.split('/')[0]].upper(), boldcentertop)
		#worksheet.write(5,19, 'SOLES', boldcenterbot)
		#worksheet.write(4,20, 'RECLASIF', boldcentertop)
		#worksheet.write(5,20, '+/-', boldcenterbot)
		#worksheet.write(4,21, '', boldcentertop)
		#worksheet.write(5,21, 'Ref', boldcenterbot)
		#worksheet.write(4,22, dic_anio[self.periodo_id.code.split('/')[0]].upper(), boldcentertop)
		#worksheet.write(5,22, 'SOLES', boldcenterbot)
		#worksheet.write(4,23, 'RECLASIF', boldcentertop)
		#worksheet.write(5,23, 'IFRS', boldcenterbot)		
		worksheet.write(4,12, dic_anio[self.periodo_id.code.split('/')[0]].upper(), boldcentertop)
		worksheet.write(5,12, 'SOLES IFRS', boldcenterbot)
		#worksheet.write(4,25, 'AJUSTE', boldcentertop)
		#worksheet.write(5,25, '+/-', boldcenterbot)
		worksheet.write(4,13, 'T.C.', boldcentertop)
		worksheet.write(5,13, 'SOL VS USD', boldcenterbot)
		worksheet.write(4,14, dic_anio[self.periodo_id.code.split('/')[0]].upper(), boldcentertop)
		worksheet.write(5,14, 'USD', boldcenterbot)
		#worksheet.write(4,28, 'AJUSTE', boldcentertop)
		#worksheet.write(5,28, '+/-', boldcenterbot)
		worksheet.write(4,15, 'T.C.', boldcentertop)
		worksheet.write(5,15, 'USD VS MXN', boldcenterbot)
		worksheet.write(4,16, dic_anio[self.periodo_id.code.split('/')[0]].upper(), boldcentertop)
		worksheet.write(5,16, 'MXN', boldcenterbot)
		

				
		x = 6


		dic_grup = {
			'1':'Disponible',
			'2':'Exigible',
			'3':'Realizable',
			'4':'Activo Fijo',
			'5':'Otros Activos Fijos',
			'6':'Activo Diferido',
			'7':'Activos Arrendamiento Financiero',
			'8':'Pasivo Circulante',
			'9':'Pasivo Fijo',
			'10':'Capital Contable',
			'11':'Deuda Intrinseca por Arredamiento'
		}


		for i in self.lineas.sorted(lambda r : r.orden):

			if i.uno_concepto == '' or i.uno_concepto == False:
				pass
			else:
				if i.uno_tipo_cuenta == '5':

					boldbordtmp = workbook.add_format({'bold': False})
					boldbordtmp.set_font_size(9)
					if i.uno_resaltado:
						boldbordtmp = workbook.add_format({'bold': True})
						#boldbordtmp.set_text_wrap()
						boldbordtmp.set_font_size(9)
					if i.uno_bordes:
						boldbordtmp.set_top(1)
						#boldbordtmp.set_border(style=2)
					worksheet.write(x,1, i.uno_concepto if i.uno_concepto else '',boldbordtmp)
				else:			
					boldbordtmp = workbook.add_format({'bold': False})
					boldbordtmp.set_font_size(9)
					boldbordtmpRight = workbook.add_format({'bold': False})
					boldbordtmpRight.set_font_size(9)
					boldbordtmpRight.set_align('right')
					boldbordtmpRight.set_align('vright')
					numberdostmp = workbook.add_format({'num_format':'#,##0.00'})
					numberdostmp.set_font_size(9)
					numbertrestmp = workbook.add_format({'num_format':'0.000'})
					numbertrestmp.set_font_size(9)
					if i.uno_resaltado:
						boldbordtmp = workbook.add_format({'bold': True})
						#boldbordtmp.set_text_wrap()
						boldbordtmp.set_font_size(9)

						boldbordtmpRight = workbook.add_format({'bold': True})
						boldbordtmpRight.set_text_wrap()
						boldbordtmpRight.set_align('right')
						boldbordtmpRight.set_align('vright')
						boldbordtmpRight.set_font_size(9)

						numberdostmp = workbook.add_format({'num_format':'#,##0.00','bold': True})
						numberdostmp.set_text_wrap()
						numberdostmp.set_font_size(9)

						numbertrestmp = workbook.add_format({'num_format':'0.000','bold': True})
						numbertrestmp.set_text_wrap()
						numbertrestmp.set_font_size(9)
					if i.uno_bordes:
						#boldbordtmp.set_border(style=2)
						#numberdostmp.set_border(style=2)
						numberdostmp.set_top(1)
						#numbertrestmp.set_border(style=2)
						numbertrestmp.set_top(1)

						#boldbordtmpRight.set_border(style=2)

					worksheet.write(x,2, i.uno_concepto if i.uno_concepto else '',boldbordtmp)

					#worksheet.write(x,3, i.uno_monto ,numberdostmp)
					#worksheet.write(x,4, i.uno_reclasif ,numberdostmp)
					#worksheet.write(x,5, str(i.uno_ref) if i.uno_ref >0 else '' ,boldbordtmp)
					#worksheet.write(x,6, i.uno_t_monto ,numberdostmp)
					#worksheet.write(x,7, i.uno_reclasif_ifrs ,numberdostmp)
					worksheet.write(x,3, i.uno_t_monto_ifrs ,numberdostmp)
					#worksheet.write(x,9, i.uno_ajuste ,numberdostmp)
					worksheet.write(x,4, i.uno_tc_usd ,numberdostmp)
					worksheet.write(x,5, i.uno_monto_usd ,numberdostmp)
					#worksheet.write(x,12, i.uno_ajuste_usd ,numberdostmp)
					worksheet.write(x,6, i.uno_tc_mxn ,numberdostmp)
					worksheet.write(x,7, i.uno_monto_mxn ,numberdostmp)

			if i.dos_concepto == '' or i.dos_concepto == False:
				pass
			else:
				if i.dos_tipo_cuenta == '5':

					boldbordtmp = workbook.add_format({'bold': False})
					boldbordtmp.set_font_size(9)
					if i.uno_resaltado:
						boldbordtmp = workbook.add_format({'bold': True})
						#boldbordtmp.set_text_wrap()
						boldbordtmp.set_font_size(9)
					if i.uno_bordes:
						boldbordtmp.set_top(1)
						#boldbordtmp.set_border(style=2)
					worksheet.write(x,17, i.dos_concepto if i.dos_concepto else '',boldbordtmp)
				else:			
					boldbordtmp = workbook.add_format({'bold': False})
					boldbordtmp.set_font_size(9)
					boldbordtmpRight = workbook.add_format({'bold': False})
					boldbordtmpRight.set_font_size(9)
					boldbordtmpRight.set_align('right')
					boldbordtmpRight.set_align('vright')
					numberdostmp = workbook.add_format({'num_format':'#,##0.00'})
					numberdostmp.set_font_size(9)
					numbertrestmp = workbook.add_format({'num_format':'0.000'})
					numbertrestmp.set_font_size(9)
					if i.dos_resaltado:
						boldbordtmp = workbook.add_format({'bold': True})
						#boldbordtmp.set_text_wrap()
						boldbordtmp.set_font_size(9)

						boldbordtmpRight = workbook.add_format({'bold': True})
						boldbordtmpRight.set_text_wrap()
						boldbordtmpRight.set_align('right')
						boldbordtmpRight.set_align('vright')
						boldbordtmpRight.set_font_size(9)

						numberdostmp = workbook.add_format({'num_format':'#,##0.00','bold': True})
						numberdostmp.set_text_wrap()
						numberdostmp.set_font_size(9)

						numbertrestmp = workbook.add_format({'num_format':'0.000','bold': True})
						numbertrestmp.set_text_wrap()
						numbertrestmp.set_font_size(9)
					if i.dos_bordes:
						#boldbordtmp.set_border(style=2)
						#numberdostmp.set_border(style=2)
						numberdostmp.set_top(1)
						#numbertrestmp.set_border(style=2)
						numbertrestmp.set_top(1)

						#boldbordtmpRight.set_border(style=2)

					worksheet.write(x,11, i.dos_concepto if i.dos_concepto else '',boldbordtmp)

					#worksheet.write(x,19, i.dos_monto ,numberdostmp)
					#worksheet.write(x,20, i.dos_reclasif ,numberdostmp)
					#worksheet.write(x,21, str(i.dos_ref) if i.dos_ref > 0 else '' ,boldbordtmp)
					#worksheet.write(x,22, i.dos_t_monto ,numberdostmp)
					#worksheet.write(x,23, i.dos_reclasif_ifrs ,numberdostmp)
					worksheet.write(x,12, i.dos_t_monto_ifrs ,numberdostmp)
					#worksheet.write(x,25, i.dos_ajuste ,numberdostmp)
					worksheet.write(x,13, i.dos_tc_usd ,numberdostmp)
					worksheet.write(x,14, i.dos_monto_usd ,numberdostmp)
					#worksheet.write(x,28, i.dos_ajuste_usd ,numberdostmp)
					worksheet.write(x,15, i.dos_tc_mxn ,numberdostmp)
					worksheet.write(x,16, i.dos_monto_mxn ,numberdostmp)

			x += 1

		t = 14.86
		worksheet.set_column('A:A', 7)
		worksheet.set_column('B:B', 4)
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
		worksheet.set_column('Q:Q', 7)
		worksheet.set_column('R:R', 4)
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




		#worksheet.insert_image('A2', 'calidra.jpg')
		worksheet_2.merge_range(0,0,0,12, u'CALQUIPA S.A.C', boldcenter)
		worksheet_2.merge_range(2,0,2,12, u'INTEGRACIÓN DEL PARTIDAS MONETARIAS MON.REG. (SOLES(S)) '+ str(self.periodo_id.code.split('/')[1]) , boldbords)
	
		worksheet_2.merge_range(4,0,4,1, u'CUENTAS ACTIVO', boldcenter)

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

		x = 6
		x_inicio = 6
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.es.mexicano'].search([('periodo_id','=',m.id)])
				if len(tt)>0:
					tt = tt[0]
				else:
					tt = False
				period_list.append( (m,tt) )

		for i in self.env['rm.balance.config.mexicano.line'].search([('grupo_cuenta','in',('3','7','6','5','1','2') ),('is_monetario','=','monetario')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.es.simple.mexicano.line'].search([('concepto','=',i.concepto),('grupo_cuenta','=',i.grupo_cuenta),('padre_activo','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].t_monto_ifrs ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)

				camino+=1

			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		total_activo_sol_pos = x
		worksheet_2.write(x,0,'TOTAL DE ACTIVOS MONETARIOS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1
		

		x+=2

		camino_final =1
		worksheet_2.write(x,0,'T.C. COMPRA (S VS USD)',bords)
		for j in period_list:
			if j[1]:
				worksheet_2.write(x,camino_final, j[1].t_cambio_compra , numbertress)
				camino_final += 1

		x = x+2
		worksheet_2.merge_range(x,0,x,1, u'CUENTAS PASIVO', boldcenter)
		x = x+1
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
		x_inicio = x
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.es.mexicano'].search([('periodo_id','=',m.id)])

				if len(tt)>0:
					tt = tt[0]
				else:
					tt = False

				period_list.append( (m,tt) )

		for i in self.env['rm.balance.config.mexicano.line'].search([('grupo_cuenta','in',('4','8','9','10','11','12') ),('is_monetario','=','monetario')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.es.simple.mexicano.line'].search([('concepto','=',i.concepto),('grupo_cuenta','=',i.grupo_cuenta),('padre_pasivo','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].t_monto_ifrs ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)

				camino+=1

			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		total_pasivo_sol_pos = x
		worksheet_2.write(x,0,'TOTAL DE PASIVOS MONETARIOS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
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
		worksheet_2.merge_range(x,0,x,12, u'INTEGRACIÓN DEL PARTIDAS MONETARIAS MON.FUN. (DOLARES(USD)) '+ str(self.periodo_id.code.split('/')[1]) , boldbords)
		x += 2
		worksheet_2.merge_range(x,0,x,1, u'CUENTAS ACTIVO', boldcenter)
		x+= 1
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
		x_inicio = x
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.es.mexicano'].search([('periodo_id','=',m.id)])

				if len(tt)>0:
					tt = tt[0]
				else:
					tt = False
				period_list.append( (m,tt) )

		for i in self.env['rm.balance.config.mexicano.line'].search([('grupo_cuenta','in',('3','7','6','5','1','2') ),('is_monetario','=','monetario')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.es.simple.mexicano.line'].search([('concepto','=',i.concepto),('grupo_cuenta','=',i.grupo_cuenta),('padre_activo','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].monto_usd ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)

				camino+=1

			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		total_activo_usd_pos = x
		worksheet_2.write(x,0,'TOTAL DE ACTIVOS MONETARIOS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1
	


		x = x+2
		worksheet_2.merge_range(x,0,x,1, u'CUENTAS PASIVO', boldcenter)
		x = x+1
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
		x_inicio = x
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.es.mexicano'].search([('periodo_id','=',m.id)])

				if len(tt)>0:
					tt = tt[0]
				else:
					tt = False
				period_list.append( (m,tt) )

		for i in self.env['rm.balance.config.mexicano.line'].search([('grupo_cuenta','in',('4','8','9','10','11','12') ),('is_monetario','=','monetario')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.es.simple.mexicano.line'].search([('concepto','=',i.concepto),('grupo_cuenta','=',i.grupo_cuenta),('padre_pasivo','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].monto_usd ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)

				camino+=1

			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		total_pasivo_usd_pos = x
		worksheet_2.write(x,0,'TOTAL DE PASIVO MONETARIOS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1
		

		x+=2
		camino_final =1
		worksheet_2.write(x,0,'T.C.  (USD VS MXN)',bords)
		for j in period_list:
			if j[1]:
				worksheet_2.write(x,camino_final, j[1].t_cambio_mexicano , numbertress)
				camino_final += 1
		#AQUI SE TERMINO LA Segunda PARTE



		x += 2
		worksheet_2.merge_range(x,0,x,12, u' AJ. EFECTO DE CONVERSION MONEDA FUNCIONAL (DOLARES (USD)) '+ str(self.periodo_id.code.split('/')[1]) , boldbords)
		x += 2
		worksheet_2.merge_range(x,0,x,1, u'CUENTAS ACTIVO', boldcenter)
		x+= 1
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
		x_inicio = x
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.es.mexicano'].search([('periodo_id','=',m.id)])

				if len(tt)>0:
					tt = tt[0]
				else:
					tt = False
				period_list.append( (m,tt) )

		for i in self.env['rm.balance.config.mexicano.line'].search([('grupo_cuenta','in',('3','7','6','5','1','2') ),('is_monetario','=','monetario')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.es.simple.mexicano.line'].search([('concepto','=',i.concepto),('grupo_cuenta','=',i.grupo_cuenta),('padre_activo','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].ajuste ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)

				camino+=1

			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		worksheet_2.write(x,0,'RECON RIF DE EFECTO DE CONVER CTAS ACTIVAS',bords)
		dif_activo_pos = x
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1
	


		x = x+2
		worksheet_2.merge_range(x,0,x,1, u'CUENTAS PASIVO', boldcenter)
		x = x+1
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
		x_inicio = x
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.es.mexicano'].search([('periodo_id','=',m.id)])

				if len(tt)>0:
					tt = tt[0]
				else:
					tt = False
				period_list.append( (m,tt) )

		for i in self.env['rm.balance.config.mexicano.line'].search([('grupo_cuenta','in',('4','8','9','10','11','12') ),('is_monetario','=','monetario')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.es.simple.mexicano.line'].search([('concepto','=',i.concepto),('grupo_cuenta','=',i.grupo_cuenta),('padre_pasivo','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].ajuste ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)

				camino+=1

			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		dif_pasivo_pos = x
		worksheet_2.write(x,0,'RECON RIF DE EFECTO DE CONVER CTAS PASIVAS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1

		

		x+=2

		worksheet_2.write(x,0,'RESUMEN DE EFACTOS NETOS ',bords)
		x+=2

		camino_final = 1
		worksheet_2.write(x,0,'RECON RIF DE EFECTO DE CONVER CTAS ACTIVAS ',bords)
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(total_activo_sol_pos,camino_final) +'-' +xl_rowcol_to_cell(total_activo_usd_pos,camino_final) + ')', numberdoss)
				camino_final +=1

		x+=1 
		camino_final = 1
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(dif_activo_pos,camino_final) +'-' +xl_rowcol_to_cell(x-1,camino_final) + ')', numberdoss)
				camino_final +=1

		x+=1

		camino_final = 1
		worksheet_2.write(x,0,'RECON RIF DE EFECTO DE CONVER CTAS PASIVAS',bords)
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(total_pasivo_sol_pos,camino_final) +'-' +xl_rowcol_to_cell(total_pasivo_usd_pos,camino_final) + ')', numberdoss)
				camino_final +=1

		x+=1 
		camino_final = 1
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(dif_pasivo_pos,camino_final) +'-' +xl_rowcol_to_cell(x-1,camino_final) + ')', numberdoss)
				camino_final +=1

		x+=1

		camino_final = 1
		worksheet_2.write(x,0,'UTILIDAD (PERDIDA) POR CONVER SOLES VS DLLS (RIF)',bords)
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(x-2,camino_final) +'-' +xl_rowcol_to_cell(x-4,camino_final) + ')', numberdoss)
				camino_final +=1

		#AQUI SE TERMINO LA Tercera PARTE



		x += 2
		worksheet_2.merge_range(x,0,x,12, u'INTEGRACIÓN DEL PARTIDAS MONETARIAS MON.REP. (PESOS(MXN)) '+ str(self.periodo_id.code.split('/')[1]) , boldbords)
		x += 2
		worksheet_2.merge_range(x,0,x,1, u'CUENTAS ACTIVO', boldcenter)
		x+= 1
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
		x_inicio = x
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.es.mexicano'].search([('periodo_id','=',m.id)])

				if len(tt)>0:
					tt = tt[0]
				else:
					tt = False
				period_list.append( (m,tt) )

		for i in self.env['rm.balance.config.mexicano.line'].search([('grupo_cuenta','in',('3','7','6','5','1','2') ),('is_monetario','=','monetario')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.es.simple.mexicano.line'].search([('concepto','=',i.concepto),('grupo_cuenta','=',i.grupo_cuenta),('padre_activo','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].monto_mxn ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)

				camino+=1

			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		total_activo_mxn_pos = x
		worksheet_2.write(x,0,'TOTAL DE ACTIVOS MONETARIOS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1
	


		x = x+2
		worksheet_2.merge_range(x,0,x,1, u'CUENTAS PASIVO', boldcenter)
		x = x+1
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
		x_inicio = x
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.es.mexicano'].search([('periodo_id','=',m.id)])

				if len(tt)>0:
					tt = tt[0]
				else:
					tt = False
				period_list.append( (m,tt) )

		for i in self.env['rm.balance.config.mexicano.line'].search([('grupo_cuenta','in',('4','8','9','10','11','12') ),('is_monetario','=','monetario')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.es.simple.mexicano.line'].search([('concepto','=',i.concepto),('grupo_cuenta','=',i.grupo_cuenta),('padre_pasivo','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].monto_mxn ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)

				camino+=1

			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		total_pasivo_mxn_pos = x
		worksheet_2.write(x,0,'TOTAL DE PASIVO MONETARIOS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1
		
		#AQUI SE TERMINO LA Cuarta PARTE

		x += 2
		worksheet_2.merge_range(x,0,x,12, u' AJ. EFECTO DE CONVERSION MONEDA FUNCIONAL (DOLARES (USD)) '+ str(self.periodo_id.code.split('/')[1]) , boldbords)
		x += 2
		worksheet_2.merge_range(x,0,x,1, u'CUENTAS ACTIVO', boldcenter)
		x+= 1
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
		x_inicio = x
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.es.mexicano'].search([('periodo_id','=',m.id)])

				if len(tt)>0:
					tt = tt[0]
				else:
					tt = False
				period_list.append( (m,tt) )

		for i in self.env['rm.balance.config.mexicano.line'].search([('grupo_cuenta','in',('3','7','6','5','1','2') ),('is_monetario','=','monetario')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.es.simple.mexicano.line'].search([('concepto','=',i.concepto),('grupo_cuenta','=',i.grupo_cuenta),('padre_activo','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].ajuste_usd ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)

				camino+=1

			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		worksheet_2.write(x,0,'RECON RIF DE EFECTO DE CONVER CTAS ACTIVAS',bords)
		dif_activo_mxn_pos = x
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1
	


		x = x+2
		worksheet_2.merge_range(x,0,x,1, u'CUENTAS PASIVO', boldcenter)
		x = x+1
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
		x_inicio = x
		period_inicio = ['01','02','03','04','05','06','07','08','09','10','11','12']
		period_list = []
		for i in period_inicio:
			if i <= self.periodo_id.code.split('/')[0]:
				m = self.env['account.period'].search([('code','=', i + '/' + self.periodo_id.code.split('/')[1] )])[0]
				tt = self.env['rm.es.mexicano'].search([('periodo_id','=',m.id)])

				if len(tt)>0:
					tt = tt[0]
				else:
					tt = False
				period_list.append( (m,tt) )

		for i in self.env['rm.balance.config.mexicano.line'].search([('grupo_cuenta','in',('4','8','9','10','11','12') ),('is_monetario','=','monetario')]).sorted(lambda r: r.orden):
			worksheet_2.write(x,0, i.concepto , bords)
			camino = 1
			print "entro",i
			for j in period_list:
				print "jentro",j
				if j[1]:
					elem_d = self.env['rm.es.simple.mexicano.line'].search([('concepto','=',i.concepto),('grupo_cuenta','=',i.grupo_cuenta),('padre_pasivo','=',j[1].id)])
					if len(elem_d)>0:
						worksheet_2.write(x,camino, elem_d[0].ajuste_usd ,numberdoss)
					else:
						worksheet_2.write(x,camino, 0 ,numberdoss)

				camino+=1

			x+=1

		x+=1
		x_final = x-1
		camino_final = 1
		dif_pasivo_mxn_pos = x
		worksheet_2.write(x,0,'RECON RIF DE EFECTO DE CONVER CTAS PASIVAS',bords)
		for j in period_list:
			worksheet_2.write_formula(x,camino_final, '=sum(' + xl_rowcol_to_cell(x_inicio,camino_final) +':' +xl_rowcol_to_cell(x_final,camino_final) + ')', numberdostop)
			camino_final += 1

		

		x+=2

		worksheet_2.write(x,0,'RESUMEN DE EFACTOS NETOS ',bords)
		x+=2

		camino_final = 1
		worksheet_2.write(x,0,'RECON ORI DE EFECTO DE CONVER CTAS ACTIVAS ',bords)
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(total_activo_mxn_pos,camino_final) +'-' +xl_rowcol_to_cell(total_activo_usd_pos,camino_final) + ')', numberdoss)
				camino_final +=1

		x+=1 
		camino_final = 1
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(dif_activo_mxn_pos,camino_final) +'-' +xl_rowcol_to_cell(x-1,camino_final) + ')', numberdoss)
				camino_final +=1

		x+=1

		camino_final = 1
		worksheet_2.write(x,0,'RECON ORI DE EFECTO DE CONVER CTAS PASIVAS',bords)
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(total_pasivo_mxn_pos,camino_final) +'-' +xl_rowcol_to_cell(total_pasivo_usd_pos,camino_final) + ')', numberdoss)
				camino_final +=1

		x+=1 
		camino_final = 1
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(dif_pasivo_mxn_pos,camino_final) +'-' +xl_rowcol_to_cell(x-1,camino_final) + ')', numberdoss)
				camino_final +=1

		x+=1

		camino_final = 1
		worksheet_2.write(x,0,'UTILIDAD (PERDIDA) POR CONVER SOLES VS DLLS (RIF)',bords)
		for j in period_list:
			if j[1]:
				worksheet_2.write_formula(x,camino_final, '=(' + xl_rowcol_to_cell(x-2,camino_final) +'-' +xl_rowcol_to_cell(x-4,camino_final) + ')', numberdoss)
				camino_final +=1


		t = 14.86
		worksheet_2.set_column('A:A', 24)
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
		worksheet_2.set_column('R:R', t)
		
		workbook.close()
		
		
		f = open(direccion + 'Reporte_balance_mexicano.xlsx', 'rb')
		
		vals = {
			'output_name': 'Reportes Mexicanos Balance.xlsx',
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