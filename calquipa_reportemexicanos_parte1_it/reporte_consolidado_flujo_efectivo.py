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


class consolidado_rm_anual_flujo_efectivo_line(models.Model):
	_name = 'consolidado.rm.anual.flujo.efectivo.line'

	orden = fields.Integer('Orden',required=True)


	concepto = fields.Char('Concepto')
	tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=True)
	grupo_cuenta = fields.Selection([('1','Utilidad Neta'),(u'2',u'Capital de Trabajo'),(u'3','Actividades de Inversión'),('4','Actividades de Capital'),('5','Otros')],'Grupo',required=True)
	formula = fields.Char('Formula')
	resaltado = fields.Boolean('Resaltado')
	bordes = fields.Boolean('Bordes')
	tipo_valor = fields.Char('Tipo Valor')
	code_flujo_efec= fields.Char('Codigo Flujo Efectivo')
	
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


	padre = fields.Many2one('consolidado.rm.anual.flujo.efectivo','Cabezera')

	_order = 'orden'




class consolidado_rm_anual_flujo_efectivo(models.Model):
	_name= 'consolidado.rm.anual.flujo.efectivo'

	fiscal_id = fields.Many2one('account.fiscalyear','Año Fiscal',required=True)	
	period_id = fields.Many2one('account.period','Periodo',required=True)
	lineas = fields.One2many('consolidado.rm.anual.flujo.efectivo.line','padre','Lineas')

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
	
		vals = {
			'orden': orden_tmp,
			'concepto' : 'Utilidad Neta',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'1',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'monto':0,
			'padre': self.id,
		}
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
			self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)
			"""

			if i.concepto_origen != i.concepto_aplicacion:

				vals = {
					'orden': orden_tmp,
					'concepto' : i.concepto_aplicacion,
					'code_flujo_efec':i.code_flujo_efec,
					'tipo_cuenta' :'1',
					'grupo_cuenta' :'1',
					'formula' :False,
					'resaltado' :False,
					'bordes' :False,
					'monto' :0,
					'tipo_valor':'aplicacion',
					'padre': self.id,
				}
				orden_tmp +=1
				self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)"""


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
		T1 = self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)
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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
			self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)
			"""

			if i.concepto_origen != i.concepto_aplicacion:
				vals = {
					'orden': orden_tmp,
					'concepto' : i.concepto_aplicacion,
					'code_flujo_efec':i.code_flujo_efec,
					'tipo_cuenta' :'1',
					'grupo_cuenta' :'2',
					'formula' :False,
					'resaltado' :False,
					'bordes' :False,
					'monto' :0,
					'tipo_valor':'aplicacion',
					'padre': self.id,
				}
				orden_tmp +=1
				self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)"""


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
		T2 = self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)
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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"3")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto_origen,
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
			self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

			"""
			if i.concepto_origen != i.concepto_aplicacion:
				vals = {
					'orden': orden_tmp,
					'concepto' : i.concepto_aplicacion,
					'code_flujo_efec':i.code_flujo_efec,
					'tipo_cuenta' :'1',
					'grupo_cuenta' :'3',
					'formula' :False,
					'resaltado' :False,
					'bordes' :False,
					'monto' :0,
					'tipo_valor':'aplicacion',
					'padre': self.id,
				}
				orden_tmp +=1
				self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)"""


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
		T3 = self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)
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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"4")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto_origen,
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
			self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)
			"""

			if i.concepto_origen != i.concepto_aplicacion:
				vals = {
					'orden': orden_tmp,
					'concepto' : i.concepto_aplicacion,
					'code_flujo_efec':i.code_flujo_efec,
					'tipo_cuenta' :'1',
					'grupo_cuenta' :'4',
					'formula' :False,
					'resaltado' :False,
					'bordes' :False,
					'monto' :0,
					'tipo_valor':'aplicacion',
					'padre': self.id,
				}
				orden_tmp +=1
				self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)"""


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
		T4 = self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)
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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line.config'].search( [('grupo_cuenta','=',"5")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto_origen,
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
			self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)
			"""
			if i.concepto_origen != i.concepto_aplicacion:
				vals = {
					'orden': orden_tmp,
					'concepto' : i.concepto_aplicacion,
					'code_flujo_efec':i.code_flujo_efec,
					'tipo_cuenta' :'1',
					'grupo_cuenta' :'5',
					'formula' :False,
					'resaltado' :False,
					'bordes' :False,
					'monto' :0,
					'tipo_valor':'aplicacion',
					'padre': self.id,
				}
				orden_tmp +=1
				self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)"""


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
		T5 = self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)
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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		T6 = self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)
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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		T7 = self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)
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
		self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)

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
		T8 = self.env['consolidado.rm.anual.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		self.refresh()



		period_list = []
		nro_act = 1
		period_act =  ("%2d"%nro_act).replace(' ','0') +  '/' + self.fiscal_id.name
		nro_act = 2
		mkmk = self.env['account.period'].search( [('code','=',period_act)] )
		if len(mkmk)>0:
			period_list.append(mkmk[0])

		while period_act != self.period_id.code :
			period_act =  ("%2d"%nro_act).replace(' ','0') +  '/' + self.fiscal_id.name
			nro_act += 1
			mkmk = self.env['account.period'].search( [('code','=',period_act)] )
			if len(mkmk)>0:
				period_list.append(mkmk[0])

		for i in period_list:
			t = self.env['consolidado.mes.rm.pre.flujo.efectivo'].search( [('period_id','=',i.id)] )
			if len(t)>0:
				t = t[0]
				for line in self.lineas:
					if line.code_flujo_efec and line.code_flujo_efec != '':
						for j in self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].search([('padre','=',t.id),('code_flujo_efec','=',line.code_flujo_efec),('tipo_cuenta','=',line.tipo_cuenta),('grupo_cuenta','=',line.grupo_cuenta)]):
							if i.code.split('/')[0] == '01':
								line.enero = j.monto
							elif i.code.split('/')[0] == '02':
								line.febrero = j.monto
							elif i.code.split('/')[0] == '03':
								line.marzo = j.monto
							elif i.code.split('/')[0] == '04':
								line.abril = j.monto
							elif i.code.split('/')[0] == '05':
								line.mayo = j.monto
							elif i.code.split('/')[0] == '06':
								line.junio = j.monto
							elif i.code.split('/')[0] == '07':
								line.julio = j.monto
							elif i.code.split('/')[0] == '08':
								line.agosto = j.monto
							elif i.code.split('/')[0] == '09':
								line.septiembre = j.monto
							elif i.code.split('/')[0] == '10':
								line.octubre = j.monto
							elif i.code.split('/')[0] == '11':
								line.noviembre = j.monto
							elif i.code.split('/')[0] == '12':
								line.diciembre = j.monto
					else:
						for j in self.env['consolidado.mes.rm.pre.flujo.efectivo.line'].search([('padre','=',t.id),('concepto','=',line.concepto),('tipo_cuenta','=',line.tipo_cuenta),('grupo_cuenta','=',line.grupo_cuenta)]):
							if i.code.split('/')[0] == '01':
								line.enero = j.monto
							elif i.code.split('/')[0] == '02':
								line.febrero = j.monto
							elif i.code.split('/')[0] == '03':
								line.marzo = j.monto
							elif i.code.split('/')[0] == '04':
								line.abril = j.monto
							elif i.code.split('/')[0] == '05':
								line.mayo = j.monto
							elif i.code.split('/')[0] == '06':
								line.junio = j.monto
							elif i.code.split('/')[0] == '07':
								line.julio = j.monto
							elif i.code.split('/')[0] == '08':
								line.agosto = j.monto
							elif i.code.split('/')[0] == '09':
								line.septiembre = j.monto
							elif i.code.split('/')[0] == '10':
								line.octubre = j.monto
							elif i.code.split('/')[0] == '11':
								line.noviembre = j.monto
							elif i.code.split('/')[0] == '12':
								line.diciembre = j.monto


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

		workbook = Workbook(direccion +'Reporte_balance_mexicano.xlsx')
		worksheet = workbook.add_worksheet(u"Consolidado Flujo Efectivo")
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
		worksheet.write(3,4, 'Consolidado Flujo Efectivo', bold)
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
		worksheet.write(7,2, 'Enero' , titlees)
		worksheet.write(7,3, 'Febrero' , titlees)
		worksheet.write(7,4, 'Marzo' , titlees)
		worksheet.write(7,5, 'Abril' , titlees)
		worksheet.write(7,6, 'Mayo' , titlees)
		worksheet.write(7,7, 'Junio' , titlees)
		worksheet.write(7,8, 'Julio' , titlees)
		worksheet.write(7,9, 'Agosto' , titlees)
		worksheet.write(7,10, 'Septiembre' , titlees)
		worksheet.write(7,11, 'Octubre' , titlees)
		worksheet.write(7,12, 'Noviembre' , titlees)
		worksheet.write(7,13, 'Diciembre' , titlees)

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


		for i in self.env['consolidado.rm.anual.flujo.efectivo.line'].search([('padre','=',self.id)]).sorted(lambda r : r.orden):

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
						
						worksheet.write(x,2, i.enero ,numberdostmp)
						worksheet.write(x,3, i.febrero ,numberdostmp)
						worksheet.write(x,4, i.marzo ,numberdostmp)
						worksheet.write(x,5, i.abril ,numberdostmp)
						worksheet.write(x,6, i.mayo ,numberdostmp)
						worksheet.write(x,7, i.junio ,numberdostmp)
						worksheet.write(x,8, i.julio ,numberdostmp)
						worksheet.write(x,9, i.agosto ,numberdostmp)
						worksheet.write(x,10, i.septiembre ,numberdostmp)
						worksheet.write(x,11, i.octubre ,numberdostmp)
						worksheet.write(x,12, i.noviembre ,numberdostmp)
						worksheet.write(x,13, i.diciembre ,numberdostmp)

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

					worksheet.write(x,2, i.enero ,numberdostmp)
					worksheet.write(x,3, i.febrero ,numberdostmp)
					worksheet.write(x,4, i.marzo ,numberdostmp)
					worksheet.write(x,5, i.abril ,numberdostmp)
					worksheet.write(x,6, i.mayo ,numberdostmp)
					worksheet.write(x,7, i.junio ,numberdostmp)
					worksheet.write(x,8, i.julio ,numberdostmp)
					worksheet.write(x,9, i.agosto ,numberdostmp)
					worksheet.write(x,10, i.septiembre ,numberdostmp)
					worksheet.write(x,11, i.octubre ,numberdostmp)
					worksheet.write(x,12, i.noviembre ,numberdostmp)
					worksheet.write(x,13, i.diciembre ,numberdostmp)


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
		
		f = open(direccion + 'Reporte_balance_mexicano.xlsx', 'rb')
		
		vals = {
			'output_name': 'Consolidado Flujo Efectivo.xlsx',
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