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


class consolidado_rm_pre_flujo_efectivo_line_config(models.Model):
	_name = 'consolidado.rm.pre.flujo.efectivo.line.config'

	orden = fields.Integer('Orden',required=True)
	concepto_origen = fields.Char('Concepto Origen')
	concepto_aplicacion = fields.Char('Concepto Aplicación')
	grupo_cuenta = fields.Selection([('1','Utilidad Neta'),(u'2',u'Capital de Trabajo'),(u'3','Actividades de Inversión'),('4','Actividades de Capital'),('5','Otros')],'Grupo',required=True)
	code_flujo_efec= fields.Char('Codigo Flujo Efectivo')
	
	_rec_name = 'code_flujo_efec'



def dig_5(n):
	return ("%5d" % n).replace(' ','0')


class consolidado_rm_pre_flujo_efectivo_line(models.Model):
	_name = 'consolidado.rm.pre.flujo.efectivo.line'

	orden = fields.Integer('Orden',required=True)

	@api.one
	def get_variacion(self):
		self.variacion = self.mes - self.mes_ant

	@api.one
	def get_entrada(self):
		if self.grupo_cuenta in ('1','2','3','4','5','6','7'):
			if self.variacion >0:
				self.entrada = 0
			else:
				self.entrada = self.variacion * -1
		else:
			if self.variacion >0:
				self.entrada = self.variacion
			else:
				self.entrada = 0


	@api.one
	def get_salida(self):
		if self.grupo_cuenta in ('1','2','3','4','5','6','7'):
			if self.variacion >0:
				self.salida = self.variacion
			else:
				self.salida = 0
		else:
			if self.variacion >0:
				self.salida = 0 
			else:
				self.salida = self.variacion * -1


	concepto = fields.Char('Concepto')
	tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=True)
	grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos Fijos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Grupo',readonly=True )
	formula = fields.Char('Formula')
	resaltado = fields.Boolean('Resaltado')
	bordes = fields.Boolean('Bordes')
	mes = fields.Float('Mes',digits=(12,2))
	mes_ant = fields.Float('Mes Anterior',digits=(12,2))

	code_flujo_efec= fields.Char('Codigo Flujo Efectivo')
	
	variacion = fields.Float('Variación',compute="get_variacion")
	entrada= fields.Float('Origen',compute="get_entrada")
	salida = fields.Float(u'Aplicación',compute="get_salida")
	padre = fields.Many2one('consolidado.rm.pre.flujo.efectivo','Cabezera')

	_order = 'orden'


class consolidado_rm_pre_flujo_efectivo(models.Model):
	_name= 'consolidado.rm.pre.flujo.efectivo'

	fiscal_id = fields.Many2one('account.fiscalyear','Año Fiscal',required=True)	
	period_id = fields.Many2one('account.period','Periodo Actual',required=True)	
	period_ant_id = fields.Many2one('account.period','Periodo Anterior',required=True)
	lineas = fields.One2many('consolidado.rm.pre.flujo.efectivo.line','padre','Lineas')

	_rec_name = 'period_id'


	@api.one
	def traer_datos(self):
		t_i = self.env['rm.balance.config.mexicano.line'].search([])
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
			'concepto' : 'CIRCULANTE',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'1',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'1',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"1")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'code_flujo_efec':i.code_flujo_efec,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'1',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Disponible',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'1',
			'formula' :'TOTAL_DISPONIBLE',
			'resaltado' :True,
			'bordes' :True,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'1',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

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
				'code_flujo_efec':i.code_flujo_efec,
			'mes' :0,
			'mes_ant' :0,
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Exigible',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'2',
			'formula' :'TOTAL_EXIGIBLE',
			'resaltado' :True,
			'bordes' :True,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'2',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
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
				'code_flujo_efec':i.code_flujo_efec,
			'mes' :0,
			'mes_ant' :0,
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Realizable',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'3',
			'formula' :'TOTAL_REALIZABLE',
			'resaltado' :True,
			'bordes' :True,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'3',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Circulante',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'3',
			'formula' :'TOTAL_CIRCULANTE',
			'resaltado' :True,
			'bordes' :True,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
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
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'FIJO',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

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
				'code_flujo_efec':i.code_flujo_efec,
			'mes' :0,
			'mes_ant' :0,
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Activo Fijo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'4',
			'formula' :'TOTAL_ACTIVO_FIJO',
			'resaltado' :True,
			'bordes' :True,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)


		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"5")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'4',
				'formula' :False,
				'resaltado' :False,
				'bordes' :False,
				'code_flujo_efec':i.code_flujo_efec,
			'mes' :0,
			'mes_ant' :0,
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Fijo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'4',
			'formula' :'TOTAL_FIJO',
			'resaltado' :True,
			'bordes' :True,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
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
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'DIFERIDO',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'6',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'6',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

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
				'code_flujo_efec':i.code_flujo_efec,
			'mes' :0,
			'mes_ant' :0,
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Suma del Activo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'6',
			'formula' :'SUMA_DEL_ACTIVO',
			'resaltado' :True,
			'bordes' :True,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		suma_activo_obj = self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)


		orden_tmp +=1

		#### AQUI TERMINA EL JUEGO DEL LADO IZQUIERDA



		vals = {
			'orden': orden_tmp,
			'concepto' : 'CIRCULANTE',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'8',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
		
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'8',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
			
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
				'code_flujo_efec':i.code_flujo_efec,
			'mes' :0,
			'mes_ant' :0,
				'padre': self.id,
			}
			self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)


			orden_tmp +=1


	
		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Circulante',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'8',
			'formula' :'TOTAL_PASIVO_CIRCULANTE',
			'resaltado' :True,
			'bordes' :True,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
		
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
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
		
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : 'FIJO',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'9',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
			
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'9',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
			
		orden_tmp +=1


		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"9")] ).sorted(lambda r: r.orden):
		
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'9',
				'formula' :False,
				'resaltado' :False,
				'code_flujo_efec':i.code_flujo_efec,
				'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
				'padre': self.id,
			}
			self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

			orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Fijo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'9',
			'formula' :'TOTAL_PASIVO_FIJO',
			'resaltado' :True,
			'bordes' :True,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
			
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'9',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
			
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Suma del Pasivo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'9',
			'formula' :'SUMA_PASIVO_CAPITAL',
			'resaltado' :True,
			'bordes' :True,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
			
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
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
			
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : 'CAPITAL CONTABLE',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'10',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
			
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'10',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
			
		orden_tmp +=1


		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"10")] ).sorted(lambda r: r.orden):
		
			vals = {
				'orden': orden_tmp,
				'concepto' : i.concepto,
				'tipo_cuenta' :'1',
				'grupo_cuenta' :'10',
				'formula' :False,
				'resaltado' :False,
				'code_flujo_efec':i.code_flujo_efec,
				'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
				'padre': self.id,
			}
			self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)

			orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'UTILIDAD O (PERDIDA) DEL EJERCICIO', 
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'10',
			'formula' : "UTILIDAD",
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Capital Contable',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'10',
			'formula' :'TOTAL_CAPITAL_CONTABLE',
			'resaltado' :True,
			'bordes' :True,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
			
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'10',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
			
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Suma del Pasivo y Capital',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'10',
			'formula' :'SUMA_PASIVO_CAPITAL_TOTAL',
			'resaltado' :True,
			'bordes' :True,
			'mes' :0,
			'mes_ant' :0,
			'padre': self.id,
		}
		suma_pasivo_obj = self.env['consolidado.rm.pre.flujo.efectivo.line'].create(vals)
			
		orden_tmp +=1

		self.refresh()

		period_mes = self.period_id
		period_mes_ant = self.period_ant_id


		if period_mes:
			t = self.env['rm.balance.mexicano'].search( [('periodo_ini','=',period_mes.id)] )
			if len(t)>0:
				t = t[0]
				for line in self.lineas:
					for j in self.env['rm.balance.mexicano.line'].search([('padre','=',t.id),('uno_concepto','=',line.concepto),('uno_tipo_cuenta','=',line.tipo_cuenta),('uno_grupo_cuenta','=',line.grupo_cuenta)]):
						line.mes = j.uno_monto_mes
						
					for j in self.env['rm.balance.mexicano.line'].search([('padre','=',t.id),('dos_concepto','=',line.concepto),('dos_tipo_cuenta','=',line.tipo_cuenta),('dos_grupo_cuenta','=',line.grupo_cuenta)]):
						line.mes = j.dos_monto_mes
						

		if period_mes_ant:
			t = self.env['rm.balance.mexicano'].search( [('periodo_ini','=',period_mes_ant.id)] )
			if len(t)>0:
				t = t[0]
				for line in self.lineas:
					for j in self.env['rm.balance.mexicano.line'].search([('padre','=',t.id),('uno_concepto','=',line.concepto),('uno_tipo_cuenta','=',line.tipo_cuenta),('uno_grupo_cuenta','=',line.grupo_cuenta)]):
						line.mes_ant = j.uno_monto_mes
						
					for j in self.env['rm.balance.mexicano.line'].search([('padre','=',t.id),('dos_concepto','=',line.concepto),('dos_tipo_cuenta','=',line.tipo_cuenta),('dos_grupo_cuenta','=',line.grupo_cuenta)]):
						line.mes_ant = j.dos_monto_mes
						

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
		worksheet = workbook.add_worksheet(u"Hoja Trabajo Flujo Efectivo")
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


		#worksheet.insert_image('A2', 'calidra.jpg')
		worksheet.write(1,2, u'Hoja Trabajo Flujo Efectivo', bold)
		worksheet.write(3,2, 'Periodo:', bold)
		worksheet.write(3,3, self.period_id.code, bold)
		
		dic_anio = {
			'00': 'Apertura',		
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
		worksheet.write(7,2, 'Mes Actual' , titlees)
		worksheet.write(7,3, 'Mes Anterior' , titlees)
		worksheet.write(7,4, u'Variación' , titlees)
		worksheet.write(7,5, 'Origen' , titlees)
		worksheet.write(7,6, u'Aplicación' , titlees)

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

		total1 = 0
		total2 = 0

		for i in self.env['consolidado.rm.pre.flujo.efectivo.line'].search([('padre','=',self.id)]).sorted(lambda r : r.orden):

			if i.concepto == '' or i.concepto == False:
				pass
			else:
				if i.tipo_cuenta == '5':

					boldbordtmp = workbook.add_format({'bold': False})
					boldbordtmp.set_font_size(9)
					if i.resaltado:
						boldbordtmp = workbook.add_format({'bold': True})
						boldbordtmp.set_text_wrap()
						boldbordtmp.set_font_size(9)
					if i.bordes:
						boldbordtmp.set_border(style=2)
					#worksheet.write(x,0, dic_grup[i.grupo_cuenta] if i.grupo_cuenta else '',boldbordtmp)
					worksheet.write(x,1, i.concepto if i.concepto else '',boldbordtmp)
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

					worksheet.write(x,2, i.mes ,numberdostmp)
					worksheet.write(x,3, i.mes_ant ,numberdostmp)

					if i.resaltado or i.bordes:
						pass
					else:
						worksheet.write(x,4, i.variacion ,numberdostmp)
						worksheet.write(x,5, i.entrada ,numberdostmp)
						worksheet.write(x,6, i.salida ,numberdostmp)
						total1 += i.entrada
						total2 += i.salida

			x += 1


		boldbordtmp = workbook.add_format({'bold': False})
		boldbordtmp.set_font_size(9)
		boldbordtmpRight = workbook.add_format({'bold': False})
		boldbordtmpRight.set_font_size(9)
		boldbordtmpRight.set_align('right')
		boldbordtmpRight.set_align('vright')
		numberdostmp = workbook.add_format({'num_format':'#,##0.00'})
		numberdostmp.set_font_size(9)
		
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
		boldbordtmp.set_border(style=2)
		numberdostmp.set_border(style=2)

		boldbordtmpRight.set_border(style=2)

		worksheet.write(x,1, 'TOTALES',boldbordtmp)

		worksheet.write(x,5, total1 ,numberdostmp)
		worksheet.write(x,6, total2 ,numberdostmp)
						
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
			'output_name': 'Consolidado Mexicanos Balance.xlsx',
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