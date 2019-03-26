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


class consolidado_mes_rm_pre_flujo_efectivo_line(models.Model):
	_name = 'consolidado.mes.rm.pre.flujo.efectivo.line'

	orden = fields.Integer('Orden',required=True)


	concepto = fields.Char('Concepto')
	tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=True)
	grupo_cuenta = fields.Selection([('1','Utilidad Neta'),(u'2',u'Capital de Trabajo'),(u'3','Actividades de Inversión'),('4','Actividades de Capital'),('5','Otros')],'Grupo',required=True)
	formula = fields.Char('Formula')
	resaltado = fields.Boolean('Resaltado')
	bordes = fields.Boolean('Bordes')
	monto = fields.Float('Monto',digits=(12,2))
	tipo_valor = fields.Char('Tipo Valor')
	code_flujo_efec= fields.Char('Codigo Flujo Efectivo')
	

	padre = fields.Many2one('consolidado.mes.rm.pre.flujo.efectivo','Cabezera')

	_order = 'orden'


class consolidado_mes_rm_pre_flujo_efectivo(models.Model):
	_name= 'consolidado.mes.rm.pre.flujo.efectivo'

	fiscal_id = fields.Many2one('account.fiscalyear','Año Fiscal',required=True)	
	period_id = fields.Many2one('account.period','Periodo',required=True)
	lineas = fields.One2many('consolidado.mes.rm.pre.flujo.efectivo.line','padre','Lineas')

	_rec_name = 'period_id'


	@api.one
	def traer_datos(self):
		t_i = self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search([])
		if len(t_i) >0 :
			pass
		else:
			raise osv.except_osv('Alerta!', "No hay plantilla configurada")

		for i in self.lineas:
			i.unlink()

		orden_tmp = 0
		#### AQUI COMIENZA EL JUEGO DONDE ESTAN LAS POSICIONES
		#tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=True)
		#grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos Fijos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Grupo',readonly=True )
		
		tt_tmp = self.env['consolidado.rm.pre.flujo.efectivo'].search( [('period_id','=',self.period_id.id)] ) 
		valor = 0			
		if len(tt_tmp)>0:
			for mm in self.env['consolidado.rm.pre.flujo.efectivo.line'].search( [('padre','=',tt_tmp[0].id),('concepto','=','UTILIDAD O (PERDIDA) DEL EJERCICIO'),('tipo_cuenta','=','3'),('grupo_cuenta','=','10'),('formula','=','UTILIDAD')]):
				valor += mm.entrada - mm.salida	
		vals = {
			'orden': orden_tmp,
			'concepto' : 'Utilidad Neta',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'1',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'monto':valor,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'1',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"1")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto_origen,
				'code_flujo_efec':i.code_flujo_efec,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'1',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto' :0,
				'tipo_valor':'origen',
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Generación Neta de Efectivo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'1',
			'formula' :'TOTAL_1',
			'resaltado' :True,
			'bordes' :True,
			'monto' :0,
			'padre': self.id,
		}
		T1 = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'1',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		#### SUMO LA 1


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Capital de Trabajo',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'2',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'monto':0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'2',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"2")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto_origen,
				'code_flujo_efec':i.code_flujo_efec,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'2',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto' :0,
				'tipo_valor':'origen',
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Flujo de Operación',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'2',
			'formula' :'TOTAL_2',
			'resaltado' :True,
			'bordes' :True,
			'monto' :0,
			'padre': self.id,
		}
		T2 = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'2',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		### SUMO LA 2


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Actividades de Inversión',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'3',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'monto':0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'3',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"3")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto_origen ,
				'code_flujo_efec':i.code_flujo_efec,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'3',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto' :0,
				'tipo_valor':'origen',
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Flujo Despues de Inversiones',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'3',
			'formula' :'TOTAL_3',
			'resaltado' :True,
			'bordes' :True,
			'monto' :0,
			'padre': self.id,
		}
		T3 = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'3',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		### SUMO LA 3


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Actividades de Capital',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'monto':0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"4")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto_origen ,
				'code_flujo_efec':i.code_flujo_efec,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'4',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto' :0,
				'tipo_valor':'origen',
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Flujo de Capital',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'4',
			'formula' :'TOTAL_4',
			'resaltado' :True,
			'bordes' :True,
			'monto' :0,
			'padre': self.id,
		}
		T4 = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		# SUMO LA 4


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Otros',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'5',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'monto':0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'5',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"5")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto_origen ,
				'code_flujo_efec':i.code_flujo_efec,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'5',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'monto' :0,
				'tipo_valor':'origen',
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)



		vals = {
			'orden': orden_tmp,
			'concepto' : 'Otros...',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'5',
			'formula' :'TOTAL_5',
			'resaltado' :True,
			'bordes' :True,
			'monto' :0,
			'padre': self.id,
		}
		T5 = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'5',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		# SUMO LA 5

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'5',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Flujo Neto',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'5',
			'formula' :'TOTAL_6',
			'resaltado' :True,
			'bordes' :True,
			'monto' :0,
			'padre': self.id,
		}
		T6 = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'5',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Saldo al inicio del periodo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'5',
			'formula' :'TOTAL_7',
			'resaltado' :True,
			'bordes' :True,
			'monto' :0,
			'padre': self.id,
		}
		T7 = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'5',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'monto' :0,
			'padre': self.id,
		}
		self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Saldo al final del periodo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'5',
			'formula' :'TOTAL_8',
			'resaltado' :True,
			'bordes' :True,
			'monto' :0,
			'padre': self.id,
		}
		T8 = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		self.refresh()

		for i in self.lineas:
			if i.tipo_cuenta == '1':
				tt_tmp = self.env['consolidado.rm.pre.flujo.efectivo'].search( [('period_id','=',self.period_id.id)] ) 
				if len(tt_tmp)>0:
					for mm in self.env['consolidado.rm.pre.flujo.efectivo.line'].search( [('padre','=',tt_tmp[0].id),('code_flujo_efec','=',i.code_flujo_efec)]):
						i.monto += mm.entrada - mm.salida

				

		self.refresh()

		for i in self.lineas:
			if (i.tipo_cuenta == '1' and i.grupo_cuenta == '1') or (i.concepto == 'Utilidad Neta' and  i.tipo_cuenta == '5' and i.grupo_cuenta == '1') :
				T1.monto += i.monto
			
		T2.monto = T1.monto
		for i in self.lineas:
			if i.tipo_cuenta == '1' and i.grupo_cuenta == '2':
				T2.monto += i.monto

		T3.monto = T2.monto
		for i in self.lineas:
			if i.tipo_cuenta == '1' and i.grupo_cuenta == '3':
				T3.monto += i.monto

		T4.monto = T3.monto
		for i in self.lineas:
			if i.tipo_cuenta == '1' and i.grupo_cuenta == '4':
				T4.monto += i.monto

		T5.monto = T4.monto
		for i in self.lineas:
			if i.tipo_cuenta == '1' and i.grupo_cuenta == '5':
				T5.monto += i.monto

		T6.monto = T5.monto

		### saldo_inicial_periodo = fields.Many2one('rm.balance.config.mexicano.line','Saldo Inicial Periodo')

		param = self.env['reporte.parametros'].search( [] )[0]
		valor = 0
		if param.saldo_inicial_periodo.id:
			tt_tmp = self.env['consolidado.rm.pre.flujo.efectivo'].search( [('period_id','=',self.period_id.id)] ) 
			if len(tt_tmp)>0:
				for mm in self.env['consolidado.rm.pre.flujo.efectivo.line'].search( [('padre','=',tt_tmp[0].id),('concepto','=',param.saldo_inicial_periodo.concepto),('tipo_cuenta','=',param.saldo_inicial_periodo.tipo_cuenta),('grupo_cuenta','=',param.saldo_inicial_periodo.grupo_cuenta)]):
					valor += mm.mes_ant

		T7.monto = valor
		T8.monto = T6.monto + T7.monto

		#for i in self.lineas:
		#	if i.tipo_cuenta == '1' and i.monto == 0:
		#		i.unlink()

		"""
		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"5")] ).sorted(lambda r: r.orden):
			if i.concepto_origen == i.concepto_aplicacion:
				t = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].search( [('padre','=',self.id),('grupo_cuenta','=',"5"),('tipo_cuenta','=',"1"),('concepto','=',i.concepto_origen)] )
				m1 = t[0]
				m2 = t[1]
				if m1.monto == 0 and m2.monto== 0:
					m2.unlink()
				elif m2.monto==0:
					m2.unlink()
				else:
					m1.unlink()

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"4")] ).sorted(lambda r: r.orden):
			if i.concepto_origen == i.concepto_aplicacion:
				t = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].search( [('padre','=',self.id),('grupo_cuenta','=',"4"),('tipo_cuenta','=',"1"),('concepto','=',i.concepto_origen)] )
				m1 = t[0]
				m2 = t[1]
				if m1.monto == 0 and m2.monto== 0:
					m2.unlink()
				elif m2.monto==0:
					m2.unlink()
				else:
					m1.unlink()

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"3")] ).sorted(lambda r: r.orden):
			if i.concepto_origen == i.concepto_aplicacion:
				t = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].search( [('padre','=',self.id),('grupo_cuenta','=',"3"),('tipo_cuenta','=',"1"),('concepto','=',i.concepto_origen)] )
				m1 = t[0]
				m2 = t[1]
				if m1.monto == 0 and m2.monto== 0:
					m2.unlink()
				elif m2.monto==0:
					m2.unlink()
				else:
					m1.unlink()

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"2")] ).sorted(lambda r: r.orden):
			if i.concepto_origen == i.concepto_aplicacion:
				t = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].search( [('padre','=',self.id),('grupo_cuenta','=',"2"),('tipo_cuenta','=',"1"),('concepto','=',i.concepto_origen)] )
				m1 = t[0]
				m2 = t[1]
				if m1.monto == 0 and m2.monto== 0:
					m2.unlink()
				elif m2.monto==0:
					m2.unlink()
				else:
					m1.unlink()

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"1")] ).sorted(lambda r: r.orden):
			if i.concepto_origen == i.concepto_aplicacion:
				t = self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].search( [('padre','=',self.id),('grupo_cuenta','=',"1"),('tipo_cuenta','=',"1"),('concepto','=',i.concepto_origen)] )
				m1 = t[0]
				m2 = t[1]
				if m1.monto == 0 and m2.monto== 0:
					m2.unlink()
				elif m2.monto==0:
					m2.unlink()
				else:
					m1.unlink() """


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

		workbook = Workbook(direccion +'Reporte_pre_flujo_efectivo.xlsx')
		worksheet = workbook.add_worksheet(u"Flujo Efectivo")
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
		worksheet.write(1,4, u'CALQUIPA S.A.C', bold)
		worksheet.write(3,4, 'Flujo Efectivo', bold)
		worksheet.write(4,4, u'Expresado en Nuevo Soles', bold)
		
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

		
		titlees = workbook.add_format({'bold': True})
		titlees.set_align('center')
		titlees.set_align('vcenter')
		#worksheet.merge_range(6,1,8,1,u'Cuenta', boldbord)

		#worksheet.write(7,2, 'S/.' , boldbord)
		worksheet.write(7,2, 'Monto' , titlees)

		x = 8

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


		for i in self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].search([('padre','=',self.id)]).sorted(lambda r : r.orden):

			if i.concepto == '' or i.concepto == False:
				pass
			else:
				if i.tipo_cuenta == '5':

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
					#worksheet.write(x,0, dic_grup[i.grupo_cuenta] if i.grupo_cuenta else '',boldbordtmp)
					worksheet.write(x,1, i.concepto if i.concepto else '',boldbordtmp)

					if i.concepto == 'Utilidad Neta' and  i.tipo_cuenta == '5' and i.grupo_cuenta == '1':
						worksheet.write(x,2, i.monto ,numberdostmp)	
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


					#worksheet.write(x,0, dic_grup[i.grupo_cuenta] if i.grupo_cuenta else '',boldbordtmp)
					worksheet.write(x,1, i.concepto if i.concepto else '',boldbordtmp)

					worksheet.write(x,2, i.monto ,numberdostmp)
			x += 1

		t = 14.86
		worksheet.set_column('A:A', t)
		worksheet.set_column('B:B', 50)
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
		
		f = open(direccion + 'Reporte_pre_flujo_efectivo.xlsx', 'rb')
		
		vals = {
			'output_name': 'Flujo Efectivo.xlsx',
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