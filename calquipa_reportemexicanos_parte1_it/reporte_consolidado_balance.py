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


class consolidado_rm_balance_mexicano_line(models.Model):
	_name = 'consolidado.rm.balance.mexicano.line'

	orden = fields.Integer('Orden',required=True)

	concepto = fields.Char('Concepto')
	tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=True)
	grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos Fijos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Grupo',readonly=True )
	formula = fields.Char('Formula')
	resaltado = fields.Boolean('Resaltado')
	bordes = fields.Boolean('Bordes')
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


	padre = fields.Many2one('consolidado.rm.balance.mexicano','Cabezera')

	_order = 'orden'




class consolidado_rm_balance_mexicano(models.Model):
	_name= 'consolidado.rm.balance.mexicano'

	fiscal_id = fields.Many2one('account.fiscalyear','Año Fiscal',required=True)	
	period_id = fields.Many2one('account.period','Periodo',required=True)
	lineas = fields.One2many('consolidado.rm.balance.mexicano.line','padre','Lineas')

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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'1',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)

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
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.rm.balance.mexicano.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Disponible',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'1',
			'formula' :'TOTAL_DISPONIBLE',
			'resaltado' :True,
			'bordes' :True,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'1',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)

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
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.rm.balance.mexicano.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Exigible',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'2',
			'formula' :'TOTAL_EXIGIBLE',
			'resaltado' :True,
			'bordes' :True,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'2',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
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
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.rm.balance.mexicano.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Realizable',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'3',
			'formula' :'TOTAL_REALIZABLE',
			'resaltado' :True,
			'bordes' :True,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'3',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Circulante',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'3',
			'formula' :'TOTAL_CIRCULANTE',
			'resaltado' :True,
			'bordes' :True,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'FIJO',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)

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
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Activo Fijo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'4',
			'formula' :'TOTAL_ACTIVO_FIJO',
			'resaltado' :True,
			'bordes' :True,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)


		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'4',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)

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
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Fijo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'4',
			'formula' :'TOTAL_FIJO',
			'resaltado' :True,
			'bordes' :True,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'DIFERIDO',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'6',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'6',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)

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
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['consolidado.rm.balance.mexicano.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Suma del Activo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'6',
			'formula' :'SUMA_DEL_ACTIVO',
			'resaltado' :True,
			'bordes' :True,
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
			'padre': self.id,
		}
		suma_activo_obj = self.env['consolidado.rm.balance.mexicano.line'].create(vals)


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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
		
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'8',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
			
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
				'padre': self.id,
			}
			self.env['consolidado.rm.balance.mexicano.line'].create(vals)


			orden_tmp +=1


	
		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Circulante',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'8',
			'formula' :'TOTAL_PASIVO_CIRCULANTE',
			'resaltado' :True,
			'bordes' :True,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
		
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
		
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : 'FIJO',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'9',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'9',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
			
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
				'padre': self.id,
			}
			self.env['consolidado.rm.balance.mexicano.line'].create(vals)

			orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Fijo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'9',
			'formula' :'TOTAL_PASIVO_FIJO',
			'resaltado' :True,
			'bordes' :True,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'9',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Suma del Pasivo',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'9',
			'formula' :'SUMA_PASIVO_CAPITAL',
			'resaltado' :True,
			'bordes' :True,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
			
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : 'CAPITAL CONTABLE',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'10',
			'formula' :False,
			'resaltado' :True,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'10',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
			
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
				'padre': self.id,
			}
			self.env['consolidado.rm.balance.mexicano.line'].create(vals)

			orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'UTILIDAD O (PERDIDA) DEL EJERCICIO',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'10',
			'formula' : "UTILIDAD",
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Total Capital Contable',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'10',
			'formula' :'TOTAL_CAPITAL_CONTABLE',
			'resaltado' :True,
			'bordes' :True,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		vals = {
			'orden': orden_tmp,
			'concepto' : ' ',
			'tipo_cuenta' :'5',
			'grupo_cuenta' :'10',
			'formula' :False,
			'resaltado' :False,
			'bordes' :False,
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
			'padre': self.id,
		}
		self.env['consolidado.rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'concepto' : 'Suma del Pasivo y Capital',
			'tipo_cuenta' :'3',
			'grupo_cuenta' :'10',
			'formula' :'SUMA_PASIVO_CAPITAL_TOTAL',
			'resaltado' :True,
			'bordes' :True,
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
			'padre': self.id,
		}
		suma_pasivo_obj = self.env['consolidado.rm.balance.mexicano.line'].create(vals)
			
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
			t = self.env['rm.balance.mexicano'].search( [('periodo_ini','=',i.id)] )
			if len(t)>0:
				t = t[0]
				for line in self.lineas:
					for j in self.env['rm.balance.mexicano.line'].search([('padre','=',t.id),('uno_concepto','=',line.concepto),('uno_tipo_cuenta','=',line.tipo_cuenta),('uno_grupo_cuenta','=',line.grupo_cuenta)]):
						if i.code.split('/')[0] == '01':
							line.enero = j.uno_monto_mes
						elif i.code.split('/')[0] == '02':
							line.febrero = j.uno_monto_mes
						elif i.code.split('/')[0] == '03':
							line.marzo = j.uno_monto_mes
						elif i.code.split('/')[0] == '04':
							line.abril = j.uno_monto_mes
						elif i.code.split('/')[0] == '05':
							line.mayo = j.uno_monto_mes
						elif i.code.split('/')[0] == '06':
							line.junio = j.uno_monto_mes
						elif i.code.split('/')[0] == '07':
							line.julio = j.uno_monto_mes
						elif i.code.split('/')[0] == '08':
							line.agosto = j.uno_monto_mes
						elif i.code.split('/')[0] == '09':
							line.septiembre = j.uno_monto_mes
						elif i.code.split('/')[0] == '10':
							line.octubre = j.uno_monto_mes
						elif i.code.split('/')[0] == '11':
							line.noviembre = j.uno_monto_mes
						elif i.code.split('/')[0] == '12':
							line.diciembre = j.uno_monto_mes

					for j in self.env['rm.balance.mexicano.line'].search([('padre','=',t.id),('dos_concepto','=',line.concepto),('dos_tipo_cuenta','=',line.tipo_cuenta),('dos_grupo_cuenta','=',line.grupo_cuenta)]):
						if i.code.split('/')[0] == '01':
							line.enero = j.dos_monto_mes
						elif i.code.split('/')[0] == '02':
							line.febrero = j.dos_monto_mes
						elif i.code.split('/')[0] == '03':
							line.marzo = j.dos_monto_mes
						elif i.code.split('/')[0] == '04':
							line.abril = j.dos_monto_mes
						elif i.code.split('/')[0] == '05':
							line.mayo = j.dos_monto_mes
						elif i.code.split('/')[0] == '06':
							line.junio = j.dos_monto_mes
						elif i.code.split('/')[0] == '07':
							line.julio = j.dos_monto_mes
						elif i.code.split('/')[0] == '08':
							line.agosto = j.dos_monto_mes
						elif i.code.split('/')[0] == '09':
							line.septiembre = j.dos_monto_mes
						elif i.code.split('/')[0] == '10':
							line.octubre = j.dos_monto_mes
						elif i.code.split('/')[0] == '11':
							line.noviembre = j.dos_monto_mes
						elif i.code.split('/')[0] == '12':
							line.diciembre = j.dos_monto_mes


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
		worksheet = workbook.add_worksheet(u"Consolidado Balance")
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
		worksheet.write(3,4, 'Balance General Consolidado', bold)
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


		for i in self.env['consolidado.rm.balance.mexicano.line'].search([('padre','=',self.id)]).sorted(lambda r : r.orden):

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

						numberdostmp = workbook.add_format({'bold': True,'num_format':'#,##0.00'})
						numberdostmp.set_text_wrap()
						numberdostmp.set_font_size(9)
					if i.bordes:
						boldbordtmp.set_border(style=2)
						numberdostmp.set_border(style=2)

						boldbordtmpRight.set_border(style=2)


					if True:
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