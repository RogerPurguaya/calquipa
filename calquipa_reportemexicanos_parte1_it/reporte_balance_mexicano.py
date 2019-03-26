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


class account_balance_type_mex(models.Model):
	_name = 'account.balance.type.mex'

	name = fields.Char('Concepto')
	tipo_cuenta = fields.Selection([('1','Grupo'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',required=True)
	grupo = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos Fijos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Grupo',required=True)

class account_account(models.Model):
	_inherit = 'account.account'

	balance_type_mex_id = fields.Many2one('rm.balance.config.mexicano.line','Balance Mexicano Grupo')

class rm_balance_config_mexicano_line(models.Model):
	_name = 'rm.balance.config.mexicano.line'

	orden = fields.Integer('Orden',required=True)

	concepto = fields.Char('Concepto')
	tipo_cuenta = fields.Selection([('1','Grupo'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',required=True, default="1")
	tipo_cambio = fields.Selection([('1','Tipo Compra Cierre'),('2','Tipo Venta Cierre'),('3','Tipo Promedio Compras'),('4','Tipo Promedio Ventas'),('5','Activo Fijo-Cédula'),('6','Patrimonio-Cédula'),('7','Depreciacion-Cédula')],'Tipo de Cambio',required=True, default="1")	
	grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos Fijos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Grupo',required=True)
	formula = fields.Char('Formula', help="Las siguientes son reservadas:  'UTILIDAD', 'SUMA_PASIVO_CAPITAL', 'SUMA_DEL_ACTIVO', 'TOTAL_FIJO', 'TOTAL_CIRCULANTE', 'DEUDA_INTRINSECA_ARRENDAMIENTO', 'TOTAL_CAPITAL_CONTABLE', 'TOTAL_PASIVO_FIJO', 'TOTAL_PASIVO_CIRCULANTE', 'VALOR_ACTUAL_ARRENDAMIENTO', 'TOTAL_DIFERIDO', 'TOTAL_5', 'TOTAL_ACTIVO_FIJO', 'TOTAL_EXIGIBLE', 'TOTAL_REALIZABLE', 'TOTAL_DISPONIBLE', 'L', 'R' ")
	resaltado = fields.Boolean('Resaltado')
	bordes = fields.Boolean('Bordes')
	monto_mes = fields.Float('Saldo',digits=(12,2))
	monto_mes_anterior = fields.Float('Saldo Anterior',digits=(12,2))
	is_monetario = fields.Selection([('monetario','Monetario'),('nomonetario','No Monetario')],'Tipo de Partida')

	code_flujo_efec= fields.Char('Codigo Flujo Efectivo')	
	
	#uno_concepto = fields.Many2one('account.balance.type.mex','Concepto')
	#uno_tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=True)
	#uno_grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos FIjos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Tipo Cuenta',readonly=True)
	#uno_formula = fields.Char('Formula')
	#uno_resaltado = fields.Boolean('Resaltado')
	#uno_bordes = fields.Boolean('Bordes')
	#uno_monto_mes = fields.Float('Saldo',digits=(12,2))
	#uno_monto_mes_anterior = fields.Float('Saldo Anterior',digits=(12,2))


	#dos_concepto = fields.Many2one('account.balance.type.mex','Concepto')
	#dos_tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=True)
	#dos_grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos FIjos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Tipo Cuenta',readonly=True)
	#dos_formula = fields.Char('Formula')
	#dos_resaltado = fields.Boolean('Resaltado')
	#dos_bordes = fields.Boolean('Bordes')
	#dos_monto_mes = fields.Float('Saldo',digits=(12,2))
	#dos_monto_mes_anterior = fields.Float('Saldo Anterior',digits=(12,2))

	padre = fields.Many2one('rm.balance.config.mexicano','Cabezera')

	_rec_name = 'concepto'

class rm_balance_mexicano_line(models.Model):
	_name = 'rm.balance.mexicano.line'

	orden = fields.Integer('Orden',required=True)

	uno_concepto = fields.Char('Concepto')
	uno_tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=True)
	uno_grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos Fijos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Grupo',readonly=True )
	uno_formula = fields.Char('Formula')
	uno_resaltado = fields.Boolean('Resaltado')
	uno_bordes = fields.Boolean('Bordes')
	uno_monto_mes = fields.Float('Saldo',digits=(12,2))
	uno_monto_mes_anterior = fields.Float('Saldo Anterior',digits=(12,2))


	dos_concepto = fields.Char('Concepto')
	dos_tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=True)
	dos_grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos Fijos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Grupo',readonly=True)
	dos_formula = fields.Char('Formula')
	dos_resaltado = fields.Boolean('Resaltado')
	dos_bordes = fields.Boolean('Bordes')
	dos_monto_mes = fields.Float('Saldo',digits=(12,2))
	dos_monto_mes_anterior = fields.Float('Saldo Anterior',digits=(12,2))

	padre = fields.Many2one('rm.balance.mexicano','Cabezera')

	_order = 'orden'



	@api.one
	def _sum_total_utilidad_(self,mes):
		calculo = 0
		for i in self.env['rm.balance.mexicano.line'].search([('padre','=',self.padre.id),('uno_grupo_cuenta','in',('1','2','3','4','5','6') ),('uno_tipo_cuenta','=','1')]):
			if mes == 1:
				calculo += i.uno_monto_mes
			else:
				calculo += i.uno_monto_mes_anterior
		for i in self.env['rm.balance.mexicano.line'].search([('padre','=',self.padre.id),('dos_grupo_cuenta','in',('1','2','3','4','5','6') ),('dos_tipo_cuenta','=','1')]):
			if mes == 1:
				calculo += i.dos_monto_mes
			else:
				calculo += i.dos_monto_mes_anterior


		
		for i in self.env['rm.balance.mexicano.line'].search([('padre','=',self.padre.id),('uno_grupo_cuenta','in',('8','9','10') ),('uno_tipo_cuenta','=','1')]):
			if mes == 1:
				calculo -= i.uno_monto_mes
			else:
				calculo -= i.uno_monto_mes_anterior
		for i in self.env['rm.balance.mexicano.line'].search([('padre','=',self.padre.id),('dos_grupo_cuenta','in',('8','9','10') ),('dos_tipo_cuenta','=','1')]):
			if mes == 1:
				calculo -= i.dos_monto_mes
			else:
				calculo -= i.dos_monto_mes_anterior



		return calculo


	@api.one
	def _sum_total_(self,grupo,mes):
		calculo = 0

		if grupo == '10':
			for i in self.env['rm.balance.mexicano.line'].search([('padre','=',self.padre.id),('uno_grupo_cuenta','=',grupo),('uno_tipo_cuenta','in',('1','3') )]):
				if i.uno_tipo_cuenta == '1':
					if mes == 1:
						calculo += i.uno_monto_mes
					else:
						calculo += i.uno_monto_mes_anterior
				else:
					if i.uno_concepto=='UTILIDAD O (PERDIDA) DEL EJERCICIO':
						if mes == 1:
							calculo += i.uno_monto_mes
						else:
							calculo += i.uno_monto_mes_anterior	

			for i in self.env['rm.balance.mexicano.line'].search([('padre','=',self.padre.id),('dos_grupo_cuenta','=',grupo),('dos_tipo_cuenta','in',('1','3') )]):
				if i.dos_tipo_cuenta == '1':
					if mes == 1:
						calculo += i.dos_monto_mes
					else:
						calculo += i.dos_monto_mes_anterior
				else:
					if i.dos_concepto=='UTILIDAD O (PERDIDA) DEL EJERCICIO':
						if mes == 1:
							calculo += i.dos_monto_mes
						else:
							calculo += i.dos_monto_mes_anterior

		else:

			for i in self.env['rm.balance.mexicano.line'].search([('padre','=',self.padre.id),('uno_grupo_cuenta','=',grupo),('uno_tipo_cuenta','=','1')]):
				if mes == 1:
					calculo += i.uno_monto_mes
				else:
					calculo += i.uno_monto_mes_anterior

			for i in self.env['rm.balance.mexicano.line'].search([('padre','=',self.padre.id),('dos_grupo_cuenta','=',grupo),('dos_tipo_cuenta','=','1')]):
				if mes == 1:
					calculo += i.dos_monto_mes
				else:
					calculo += i.dos_monto_mes_anterior

		return calculo

	@api.one
	def _cal_orden_(self,grupo,mes,orden):
		calculo = 0

		for i in self.env['rm.balance.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
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


	@api.one
	def calculo_prog_mes_uno(self,orden):
		calculo = 0
		for i in self.env['rm.balance.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			calculo += i.uno_monto_mes
		return calculo


	@api.one
	def calculo_prog_anterior_uno(self,orden):
		calculo = 0
		for i in self.env['rm.balance.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			calculo += i.uno_monto_mes_anterior
		return calculo

	@api.one
	def calculo_prog_mes_dos(self,orden):
		calculo = 0
		for i in self.env['rm.balance.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			calculo += i.dos_monto_mes
		return calculo

	@api.one
	def calculo_prog_anterior_dos(self,orden):
		calculo = 0
		for i in self.env['rm.balance.mexicano.line'].search([('orden','=',orden),('padre','=',self.padre.id)]):
			calculo += i.dos_monto_mes_anterior
		return calculo


class rm_balance_config_mexicano(models.Model):
	_name = 'rm.balance.config.mexicano'

	lineas = fields.One2many('rm.balance.config.mexicano.line','padre','Lineas')
	name = fields.Char('Nombre',default='Balance Configuración')

	_rec_name = 'name'


class rm_balance_mexicano(models.Model):
	_name= 'rm.balance.mexicano'

	periodo_ini = fields.Many2one('account.period','Periodo Actual',required=True)	
	periodo_ini_ant = fields.Many2one('account.period','Periodo Anterior',required=True)

	tipo_cambio = fields.Float('Tipo Cambio',digits=(12,3))
	lineas = fields.One2many('rm.balance.mexicano.line','padre','Lineas')

	_rec_name = 'periodo_ini'


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
		#uno_tipo_cuenta = fields.Selection([('1','Ingreso'),('2','Costo o Gasto'),('3','Calculado'),('4','Ingresado'),('5','Texto Fijo')],'Tipo Cuenta',readonly=True)
		#uno_grupo_cuenta = fields.Selection([('1','Disponible'),('2','Exigible'),('3','Realizable'),('4','Activo Fijo'),('5','Otros Activos Fijos'),('6','Activo Diferido'),('7','Activos Arrendamiento Financiero'),('8','Pasivo Circulante'),('9','Pasivo Fijo'),('10','Capital Contable'),('11','Deuda Intrinseca por Arredamiento')],'Grupo',readonly=True )
	
		vals = {
			'orden': orden_tmp,
			'uno_concepto' : 'CIRCULANTE',
			'uno_tipo_cuenta' :'5',
			'uno_grupo_cuenta' :'1',
			'uno_formula' :False,
			'uno_resaltado' :True,
			'uno_bordes' :False,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : ' ',
			'uno_tipo_cuenta' :'5',
			'uno_grupo_cuenta' :'1',
			'uno_formula' :False,
			'uno_resaltado' :False,
			'uno_bordes' :False,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"1")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'uno_concepto' : i.concepto,
				'uno_tipo_cuenta' :'1',
				'uno_grupo_cuenta' :'1',
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes' :0,
				'uno_monto_mes_anterior' :0,
				'dos_concepto' :False,
				'dos_tipo_cuenta' :False,
				'dos_grupo_cuenta' :False,
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes':0,
				'dos_monto_mes_anterior' :0,
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['rm.balance.mexicano.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'uno_concepto' : 'Total Disponible',
			'uno_tipo_cuenta' :'3',
			'uno_grupo_cuenta' :'1',
			'uno_formula' :'TOTAL_DISPONIBLE',
			'uno_resaltado' :True,
			'uno_bordes' :True,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : ' ',
			'uno_tipo_cuenta' :'5',
			'uno_grupo_cuenta' :'1',
			'uno_formula' :False,
			'uno_resaltado' :False,
			'uno_bordes' :False,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)

		### FINALIZO DISPONIBLE

		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"2")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'uno_concepto' : i.concepto,
				'uno_tipo_cuenta' :'1',
				'uno_grupo_cuenta' :'2',
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes' :0,
				'uno_monto_mes_anterior' :0,
				'dos_concepto' :False,
				'dos_tipo_cuenta' :False,
				'dos_grupo_cuenta' :False,
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes':0,
				'dos_monto_mes_anterior' :0,
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['rm.balance.mexicano.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'uno_concepto' : 'Total Exigible',
			'uno_tipo_cuenta' :'3',
			'uno_grupo_cuenta' :'2',
			'uno_formula' :'TOTAL_EXIGIBLE',
			'uno_resaltado' :True,
			'uno_bordes' :True,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : ' ',
			'uno_tipo_cuenta' :'5',
			'uno_grupo_cuenta' :'2',
			'uno_formula' :False,
			'uno_resaltado' :False,
			'uno_bordes' :False,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)
		#### TERMINO EXIGIBLE

		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"3")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'uno_concepto' : i.concepto,
				'uno_tipo_cuenta' :'1',
				'uno_grupo_cuenta' :'3',
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes' :0,
				'uno_monto_mes_anterior' :0,
				'dos_concepto' :False,
				'dos_tipo_cuenta' :False,
				'dos_grupo_cuenta' :False,
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes':0,
				'dos_monto_mes_anterior' :0,
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['rm.balance.mexicano.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'uno_concepto' : 'Total Realizable',
			'uno_tipo_cuenta' :'3',
			'uno_grupo_cuenta' :'3',
			'uno_formula' :'TOTAL_REALIZABLE',
			'uno_resaltado' :True,
			'uno_bordes' :True,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : ' ',
			'uno_tipo_cuenta' :'5',
			'uno_grupo_cuenta' :'3',
			'uno_formula' :False,
			'uno_resaltado' :False,
			'uno_bordes' :False,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : 'Total Circulante',
			'uno_tipo_cuenta' :'3',
			'uno_grupo_cuenta' :'3',
			'uno_formula' :'TOTAL_CIRCULANTE',
			'uno_resaltado' :True,
			'uno_bordes' :True,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1
		#### TERMINO REALIZABLE Y CIRCULANTE

		### AQUI COMIENZA FIJO

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : ' ',
			'uno_tipo_cuenta' :'5',
			'uno_grupo_cuenta' :'4',
			'uno_formula' :False,
			'uno_resaltado' :False,
			'uno_bordes' :False,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : 'FIJO',
			'uno_tipo_cuenta' :'5',
			'uno_grupo_cuenta' :'4',
			'uno_formula' :False,
			'uno_resaltado' :True,
			'uno_bordes' :False,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : ' ',
			'uno_tipo_cuenta' :'5',
			'uno_grupo_cuenta' :'4',
			'uno_formula' :False,
			'uno_resaltado' :False,
			'uno_bordes' :False,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"4")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'uno_concepto' : i.concepto,
				'uno_tipo_cuenta' :'1',
				'uno_grupo_cuenta' :'4',
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes' :0,
				'uno_monto_mes_anterior' :0,
				'dos_concepto' :False,
				'dos_tipo_cuenta' :False,
				'dos_grupo_cuenta' :False,
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes':0,
				'dos_monto_mes_anterior' :0,
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : 'Total Activo Fijo',
			'uno_tipo_cuenta' :'3',
			'uno_grupo_cuenta' :'4',
			'uno_formula' :'TOTAL_ACTIVO_FIJO',
			'uno_resaltado' :True,
			'uno_bordes' :True,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)


		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : ' ',
			'uno_tipo_cuenta' :'5',
			'uno_grupo_cuenta' :'4',
			'uno_formula' :False,
			'uno_resaltado' :False,
			'uno_bordes' :False,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"5")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'uno_concepto' : i.concepto,
				'uno_tipo_cuenta' :'1',
				'uno_grupo_cuenta' :'4',
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes' :0,
				'uno_monto_mes_anterior' :0,
				'dos_concepto' :False,
				'dos_tipo_cuenta' :False,
				'dos_grupo_cuenta' :False,
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes':0,
				'dos_monto_mes_anterior' :0,
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : 'Total Fijo',
			'uno_tipo_cuenta' :'3',
			'uno_grupo_cuenta' :'4',
			'uno_formula' :'TOTAL_FIJO',
			'uno_resaltado' :True,
			'uno_bordes' :True,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1 

		### AQUI COMIENZA Diferido

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : ' ',
			'uno_tipo_cuenta' :'5',
			'uno_grupo_cuenta' :'6',
			'uno_formula' :False,
			'uno_resaltado' :False,
			'uno_bordes' :False,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : 'DIFERIDO',
			'uno_tipo_cuenta' :'5',
			'uno_grupo_cuenta' :'6',
			'uno_formula' :False,
			'uno_resaltado' :True,
			'uno_bordes' :False,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1

		vals = {
			'orden': orden_tmp,
			'uno_concepto' : ' ',
			'uno_tipo_cuenta' :'5',
			'uno_grupo_cuenta' :'6',
			'uno_formula' :False,
			'uno_resaltado' :False,
			'uno_bordes' :False,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		self.env['rm.balance.mexicano.line'].create(vals)

		orden_tmp +=1
		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"6")] ).sorted(lambda r: r.orden):
			vals = {
				'orden': orden_tmp,
				'uno_concepto' : i.concepto,
				'uno_tipo_cuenta' :'1',
				'uno_grupo_cuenta' :'6',
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes' :0,
				'uno_monto_mes_anterior' :0,
				'dos_concepto' :False,
				'dos_tipo_cuenta' :False,
				'dos_grupo_cuenta' :False,
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes':0,
				'dos_monto_mes_anterior' :0,
				'padre': self.id,
			}
			orden_tmp +=1
			self.env['rm.balance.mexicano.line'].create(vals)


		vals = {
			'orden': orden_tmp,
			'uno_concepto' : 'Suma del Activo',
			'uno_tipo_cuenta' :'3',
			'uno_grupo_cuenta' :'6',
			'uno_formula' :'SUMA_DEL_ACTIVO',
			'uno_resaltado' :True,
			'uno_bordes' :True,
			'uno_monto_mes' :0,
			'uno_monto_mes_anterior' :0,
			'dos_concepto' :False,
			'dos_tipo_cuenta' :False,
			'dos_grupo_cuenta' :False,
			'dos_formula' :False,
			'dos_resaltado' :False,
			'dos_bordes' :False,
			'dos_monto_mes':0,
			'dos_monto_mes_anterior' :0,
			'padre': self.id,
		}
		suma_activo_obj = self.env['rm.balance.mexicano.line'].create(vals)


		orden_tmp +=1

		#### AQUI TERMINA EL JUEGO DEL LADO IZQUIERDA




		orden_tmp = 0

		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = 'CIRCULANTE'
			t_obj_tmp[0].dos_tipo_cuenta ='5'
			t_obj_tmp[0].dos_grupo_cuenta = '8'
			t_obj_tmp[0].dos_formula = False
			t_obj_tmp[0].dos_resaltado = True
			t_obj_tmp[0].dos_bordes = False
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : 'CIRCULANTE',
				'dos_tipo_cuenta' :'5',
				'dos_grupo_cuenta' :'8',
				'dos_formula' :False,
				'dos_resaltado' :True,
				'dos_bordes' :False,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = ' '
			t_obj_tmp[0].dos_tipo_cuenta ='5'
			t_obj_tmp[0].dos_grupo_cuenta = '8'
			t_obj_tmp[0].dos_formula = False
			t_obj_tmp[0].dos_resaltado = False
			t_obj_tmp[0].dos_bordes = False
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : ' ',
				'dos_tipo_cuenta' :'5',
				'dos_grupo_cuenta' :'8',
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"8")] ).sorted(lambda r: r.orden):
			t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
			if len(t_obj_tmp) >0:
				t_obj_tmp[0].dos_concepto = i.concepto
				t_obj_tmp[0].dos_tipo_cuenta ='1'
				t_obj_tmp[0].dos_grupo_cuenta = '8'
				t_obj_tmp[0].dos_formula = False
				t_obj_tmp[0].dos_resaltado = False
				t_obj_tmp[0].dos_bordes = False
				t_obj_tmp[0].dos_monto_mes =0
				t_obj_tmp[0].dos_monto_mes_anterior =0
			else:
				vals = {
					'orden': orden_tmp,
					'dos_concepto' : i.concepto,
					'dos_tipo_cuenta' :'1',
					'dos_grupo_cuenta' :'8',
					'dos_formula' :False,
					'dos_resaltado' :False,
					'dos_bordes' :False,
					'dos_monto_mes' :0,
					'dos_monto_mes_anterior' :0,
					'uno_concepto' :False,
					'uno_tipo_cuenta' :False,
					'uno_grupo_cuenta' :False,
					'uno_formula' :False,
					'uno_resaltado' :False,
					'uno_bordes' :False,
					'uno_monto_mes':0,
					'uno_monto_mes_anterior' :0,
					'padre': self.id,
				}
				self.env['rm.balance.mexicano.line'].create(vals)


			orden_tmp +=1


		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = 'Total Circulante'
			t_obj_tmp[0].dos_tipo_cuenta ='3'
			t_obj_tmp[0].dos_grupo_cuenta = '8'
			t_obj_tmp[0].dos_formula = 'TOTAL_PASIVO_CIRCULANTE'
			t_obj_tmp[0].dos_resaltado = True
			t_obj_tmp[0].dos_bordes = True
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : 'Total Circulante',
				'dos_tipo_cuenta' :'3',
				'dos_grupo_cuenta' :'8',
				'dos_formula' :'TOTAL_PASIVO_CIRCULANTE',
				'dos_resaltado' :True,
				'dos_bordes' :True,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1

		### segundo derecho

		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = ' '
			t_obj_tmp[0].dos_tipo_cuenta ='5'
			t_obj_tmp[0].dos_grupo_cuenta = '9'
			t_obj_tmp[0].dos_formula = False
			t_obj_tmp[0].dos_resaltado = False
			t_obj_tmp[0].dos_bordes = False
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : ' ',
				'dos_tipo_cuenta' :'5',
				'dos_grupo_cuenta' :'9',
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = 'FIJO'
			t_obj_tmp[0].dos_tipo_cuenta ='5'
			t_obj_tmp[0].dos_grupo_cuenta = '9'
			t_obj_tmp[0].dos_formula = False
			t_obj_tmp[0].dos_resaltado = True
			t_obj_tmp[0].dos_bordes = False
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : 'FIJO',
				'dos_tipo_cuenta' :'5',
				'dos_grupo_cuenta' :'9',
				'dos_formula' :False,
				'dos_resaltado' :True,
				'dos_bordes' :False,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = ' '
			t_obj_tmp[0].dos_tipo_cuenta ='5'
			t_obj_tmp[0].dos_grupo_cuenta = '9'
			t_obj_tmp[0].dos_formula = False
			t_obj_tmp[0].dos_resaltado = False
			t_obj_tmp[0].dos_bordes = False
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : ' ',
				'dos_tipo_cuenta' :'5',
				'dos_grupo_cuenta' :'9',
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"9")] ).sorted(lambda r: r.orden):
			t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
			if len(t_obj_tmp) >0:
				t_obj_tmp[0].dos_concepto = i.concepto
				t_obj_tmp[0].dos_tipo_cuenta ='1'
				t_obj_tmp[0].dos_grupo_cuenta = '9'
				t_obj_tmp[0].dos_formula = False
				t_obj_tmp[0].dos_resaltado = False
				t_obj_tmp[0].dos_bordes = False
				t_obj_tmp[0].dos_monto_mes =0
				t_obj_tmp[0].dos_monto_mes_anterior =0
			else:
				vals = {
					'orden': orden_tmp,
					'dos_concepto' : i.concepto,
					'dos_tipo_cuenta' :'1',
					'dos_grupo_cuenta' :'9',
					'dos_formula' :False,
					'dos_resaltado' :False,
					'dos_bordes' :False,
					'dos_monto_mes' :0,
					'dos_monto_mes_anterior' :0,
					'uno_concepto' :False,
					'uno_tipo_cuenta' :False,
					'uno_grupo_cuenta' :False,
					'uno_formula' :False,
					'uno_resaltado' :False,
					'uno_bordes' :False,
					'uno_monto_mes':0,
					'uno_monto_mes_anterior' :0,
					'padre': self.id,
				}
				self.env['rm.balance.mexicano.line'].create(vals)

			orden_tmp +=1


		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = 'Total Fijo'
			t_obj_tmp[0].dos_tipo_cuenta ='3'
			t_obj_tmp[0].dos_grupo_cuenta = '9'
			t_obj_tmp[0].dos_formula = 'TOTAL_PASIVO_FIJO'
			t_obj_tmp[0].dos_resaltado = True
			t_obj_tmp[0].dos_bordes = True
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : 'Total Fijo',
				'dos_tipo_cuenta' :'3',
				'dos_grupo_cuenta' :'9',
				'dos_formula' :'TOTAL_PASIVO_FIJO',
				'dos_resaltado' :True,
				'dos_bordes' :True,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1

		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = ' '
			t_obj_tmp[0].dos_tipo_cuenta ='5'
			t_obj_tmp[0].dos_grupo_cuenta = '9'
			t_obj_tmp[0].dos_formula = False
			t_obj_tmp[0].dos_resaltado = False
			t_obj_tmp[0].dos_bordes = False
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : ' ',
				'dos_tipo_cuenta' :'5',
				'dos_grupo_cuenta' :'9',
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1

		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = 'Suma del Pasivo'
			t_obj_tmp[0].dos_tipo_cuenta ='3'
			t_obj_tmp[0].dos_grupo_cuenta = '9'
			t_obj_tmp[0].dos_formula = 'SUMA_PASIVO_CAPITAL'
			t_obj_tmp[0].dos_resaltado = True
			t_obj_tmp[0].dos_bordes = True
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : 'Suma del Pasivo',
				'dos_tipo_cuenta' :'3',
				'dos_grupo_cuenta' :'9',
				'dos_formula' :'SUMA_PASIVO_CAPITAL',
				'dos_resaltado' :True,
				'dos_bordes' :True,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1
		##### AKI LA TERCERAE Y ULTIMA

		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = ' '
			t_obj_tmp[0].dos_tipo_cuenta ='5'
			t_obj_tmp[0].dos_grupo_cuenta = '10'
			t_obj_tmp[0].dos_formula = False
			t_obj_tmp[0].dos_resaltado = False
			t_obj_tmp[0].dos_bordes = False
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : ' ',
				'dos_tipo_cuenta' :'5',
				'dos_grupo_cuenta' :'10',
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = 'CAPITAL CONTABLE'
			t_obj_tmp[0].dos_tipo_cuenta ='5'
			t_obj_tmp[0].dos_grupo_cuenta = '10'
			t_obj_tmp[0].dos_formula = False
			t_obj_tmp[0].dos_resaltado = True
			t_obj_tmp[0].dos_bordes = False
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : 'CAPITAL CONTABLE',
				'dos_tipo_cuenta' :'5',
				'dos_grupo_cuenta' :'10',
				'dos_formula' :False,
				'dos_resaltado' :True,
				'dos_bordes' :False,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = ' '
			t_obj_tmp[0].dos_tipo_cuenta ='5'
			t_obj_tmp[0].dos_grupo_cuenta = '10'
			t_obj_tmp[0].dos_formula = False
			t_obj_tmp[0].dos_resaltado = False
			t_obj_tmp[0].dos_bordes = False
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : ' ',
				'dos_tipo_cuenta' :'5',
				'dos_grupo_cuenta' :'10',
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		for i in self.env['rm.balance.config.mexicano.line'].search( [('grupo_cuenta','=',"10")] ).sorted(lambda r: r.orden):
			t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
			if len(t_obj_tmp) >0:
				t_obj_tmp[0].dos_concepto = i.concepto
				t_obj_tmp[0].dos_tipo_cuenta ='1'
				t_obj_tmp[0].dos_grupo_cuenta = '10'
				t_obj_tmp[0].dos_formula = False
				t_obj_tmp[0].dos_resaltado = False
				t_obj_tmp[0].dos_bordes = False
				t_obj_tmp[0].dos_monto_mes =0
				t_obj_tmp[0].dos_monto_mes_anterior =0
			else:
				vals = {
					'orden': orden_tmp,
					'dos_concepto' : i.concepto,
					'dos_tipo_cuenta' :'1',
					'dos_grupo_cuenta' :'10',
					'dos_formula' :False,
					'dos_resaltado' :False,
					'dos_bordes' :False,
					'dos_monto_mes' :0,
					'dos_monto_mes_anterior' :0,
					'uno_concepto' :False,
					'uno_tipo_cuenta' :False,
					'uno_grupo_cuenta' :False,
					'uno_formula' :False,
					'uno_resaltado' :False,
					'uno_bordes' :False,
					'uno_monto_mes':0,
					'uno_monto_mes_anterior' :0,
					'padre': self.id,
				}
				self.env['rm.balance.mexicano.line'].create(vals)

			orden_tmp +=1

		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = 'UTILIDAD O (PERDIDA) DEL EJERCICIO'
			t_obj_tmp[0].dos_tipo_cuenta ='3'
			t_obj_tmp[0].dos_grupo_cuenta = '10'
			t_obj_tmp[0].dos_formula = "UTILIDAD"
			t_obj_tmp[0].dos_resaltado = False
			t_obj_tmp[0].dos_bordes = False
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : 'UTILIDAD O (PERDIDA) DEL EJERCICIO',
				'dos_tipo_cuenta' :'3',
				'dos_grupo_cuenta' :'10',
				'dos_formula' : "UTILIDAD",
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
		orden_tmp +=1

		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = 'Total Capital Contable'
			t_obj_tmp[0].dos_tipo_cuenta ='3'
			t_obj_tmp[0].dos_grupo_cuenta = '10'
			t_obj_tmp[0].dos_formula = 'TOTAL_CAPITAL_CONTABLE'
			t_obj_tmp[0].dos_resaltado = True
			t_obj_tmp[0].dos_bordes = True
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : 'Total Capital Contable',
				'dos_tipo_cuenta' :'3',
				'dos_grupo_cuenta' :'10',
				'dos_formula' :'TOTAL_CAPITAL_CONTABLE',
				'dos_resaltado' :True,
				'dos_bordes' :True,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])
		if len(t_obj_tmp) >0:
			t_obj_tmp[0].dos_concepto = ' '
			t_obj_tmp[0].dos_tipo_cuenta ='5'
			t_obj_tmp[0].dos_grupo_cuenta = '10'
			t_obj_tmp[0].dos_formula = False
			t_obj_tmp[0].dos_resaltado = False
			t_obj_tmp[0].dos_bordes = False
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : ' ',
				'dos_tipo_cuenta' :'5',
				'dos_grupo_cuenta' :'10',
				'dos_formula' :False,
				'dos_resaltado' :False,
				'dos_bordes' :False,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1


		t_obj_tmp = self.env['rm.balance.mexicano.line'].search([('orden','=',orden_tmp),('padre','=',self.id)])

		suma_pasivo_obj = None
		if len(t_obj_tmp) >0:
			suma_pasivo_obj = t_obj_tmp[0]

			t_obj_tmp[0].dos_concepto = 'Suma del Pasivo y Capital'
			t_obj_tmp[0].dos_tipo_cuenta ='3'
			t_obj_tmp[0].dos_grupo_cuenta = '10'
			t_obj_tmp[0].dos_formula = 'SUMA_PASIVO_CAPITAL_TOTAL'
			t_obj_tmp[0].dos_resaltado = True
			t_obj_tmp[0].dos_bordes = True
			t_obj_tmp[0].dos_monto_mes =0
			t_obj_tmp[0].dos_monto_mes_anterior =0
		else:
			vals = {
				'orden': orden_tmp,
				'dos_concepto' : 'Suma del Pasivo y Capital',
				'dos_tipo_cuenta' :'3',
				'dos_grupo_cuenta' :'10',
				'dos_formula' :'SUMA_PASIVO_CAPITAL_TOTAL',
				'dos_resaltado' :True,
				'dos_bordes' :True,
				'dos_monto_mes' :0,
				'dos_monto_mes_anterior' :0,
				'uno_concepto' :False,
				'uno_tipo_cuenta' :False,
				'uno_grupo_cuenta' :False,
				'uno_formula' :False,
				'uno_resaltado' :False,
				'uno_bordes' :False,
				'uno_monto_mes':0,
				'uno_monto_mes_anterior' :0,
				'padre': self.id,
			}
			suma_pasivo_obj = self.env['rm.balance.mexicano.line'].create(vals)
			
		orden_tmp +=1

		if suma_activo_obj.orden > suma_pasivo_obj.orden:
			suma_activo_obj.dos_concepto = 'Suma del Pasivo y Capital'
			suma_activo_obj.dos_tipo_cuenta ='3'
			suma_activo_obj.dos_grupo_cuenta = '10'
			suma_activo_obj.dos_formula = 'SUMA_PASIVO_CAPITAL_TOTAL'
			suma_activo_obj.dos_resaltado = True
			suma_activo_obj.dos_bordes = True
			suma_activo_obj.dos_monto_mes =0
			suma_activo_obj.dos_monto_mes_anterior =0

			suma_pasivo_obj.dos_concepto = False
			suma_pasivo_obj.dos_tipo_cuenta = False
			suma_pasivo_obj.dos_grupo_cuenta = False
			suma_pasivo_obj.dos_formula = False
			suma_pasivo_obj.dos_resaltado = False
			suma_pasivo_obj.dos_bordes = False
			suma_pasivo_obj.dos_monto_mes =0
			suma_pasivo_obj.dos_monto_mes_anterior =0
		else:

			suma_pasivo_obj.uno_concepto = 'Suma del Activo'
			suma_pasivo_obj.uno_tipo_cuenta ='3'
			suma_pasivo_obj.uno_grupo_cuenta = '6'
			suma_pasivo_obj.uno_formula = 'SUMA_DEL_ACTIVO'
			suma_pasivo_obj.uno_resaltado = True
			suma_pasivo_obj.uno_bordes = True
			suma_pasivo_obj.uno_monto_mes =0
			suma_pasivo_obj.uno_monto_mes_anterior =0

			suma_activo_obj.uno_concepto = False
			suma_activo_obj.uno_tipo_cuenta = False
			suma_activo_obj.uno_grupo_cuenta = False
			suma_activo_obj.uno_formula = False
			suma_activo_obj.uno_resaltado = False
			suma_activo_obj.uno_bordes = False
			suma_activo_obj.uno_monto_mes =0
			suma_activo_obj.uno_monto_mes_anterior =0

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
				i.uno_monto_mes= 0
				i.uno_monto_mes_anterior =0

			if i.dos_tipo_cuenta == '1' or i.dos_tipo_cuenta == '2':
				i.dos_monto_mes= 0
				i.dos_monto_mes_anterior =0

		param_report = self.env['reporte.parametros'].search([])[0]
		cuentas_list = []
		if param_report.tributos.id:
			for m in self.env['account.account'].search( [('balance_type_mex_id','=',param_report.tributos.id)]):

				cuentas_list.append(m)
				self.env.cr.execute(""" 
					select (debe-haber) from get_hoja_trabajo_detalle_registro_analisis_ht(false,(substring('""" + self.periodo_ini.code + """'::varchar,4,4)||'00')::integer,periodo_num('""" + self.periodo_ini.code +"""'))
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
update rm_balance_mexicano_line
set uno_monto_mes= T1.monto
from ( select artm.id, artm.concepto, CASE WHEN artm.grupo_cuenta = '1' or artm.grupo_cuenta = '2' or artm.grupo_cuenta = '3' or artm.grupo_cuenta = '4' or artm.grupo_cuenta = '5' or artm.grupo_cuenta = '6' or artm.grupo_cuenta = '7'
THEN sum(debit-credit) ELSE sum(credit-debit) END as monto from
account_account aa
inner join account_move_line aml on aml.account_id = aa.id
inner join account_move am on am.id = aml.move_id
inner join account_period ap on ap.id = am.period_id
inner join rm_balance_config_mexicano_line artm on artm.id = aa.balance_type_mex_id
where (artm.tipo_cuenta = '1'  ) and periodo_num(ap.code) <= periodo_num('""" + self.periodo_ini.code + """')
and periodo_num(ap.code)>= (substring('""" + self.periodo_ini.code + """'::varchar,4,4)||'00')::integer
and am.state != 'draft'
group by artm.id, artm.concepto
) T1
where rm_balance_mexicano_line.uno_concepto = T1.concepto
and rm_balance_mexicano_line.padre = """ + str(self.id) + """
			""")
		

		self.env.cr.execute("""
update rm_balance_mexicano_line
set uno_monto_mes_anterior= T1.monto
from ( select artm.id, artm.concepto, CASE WHEN artm.grupo_cuenta = '1' or artm.grupo_cuenta = '2' or artm.grupo_cuenta = '3' or artm.grupo_cuenta = '4' or artm.grupo_cuenta = '5' or artm.grupo_cuenta = '6' or artm.grupo_cuenta = '7'
THEN sum(debit-credit) ELSE sum(credit-debit) END as monto from
account_account aa
inner join account_move_line aml on aml.account_id = aa.id
inner join account_move am on am.id = aml.move_id
inner join account_period ap on ap.id = am.period_id
inner join rm_balance_config_mexicano_line artm on artm.id = aa.balance_type_mex_id
where (artm.tipo_cuenta = '1'  ) and periodo_num(ap.code) <= periodo_num('""" + self.periodo_ini_ant.code + """')
and periodo_num(ap.code)>= (substring('""" + self.periodo_ini_ant.code + """'::varchar,4,4)||'00')::integer
group by artm.id, artm.concepto
) T1
where rm_balance_mexicano_line.uno_concepto = T1.concepto
and rm_balance_mexicano_line.padre = """ + str(self.id) + """
			""")
		

		self.env.cr.execute("""
update rm_balance_mexicano_line
set dos_monto_mes= T1.monto
from ( select artm.id, artm.concepto, CASE WHEN artm.grupo_cuenta = '1' or artm.grupo_cuenta = '2' or artm.grupo_cuenta = '3' or artm.grupo_cuenta = '4' or artm.grupo_cuenta = '5' or artm.grupo_cuenta = '6' or artm.grupo_cuenta = '7'
THEN sum(debit-credit) ELSE sum(credit-debit) END as monto from
account_account aa
inner join account_move_line aml on aml.account_id = aa.id
inner join account_move am on am.id = aml.move_id
inner join account_period ap on ap.id = am.period_id
inner join rm_balance_config_mexicano_line artm on artm.id = aa.balance_type_mex_id
where (artm.tipo_cuenta = '1'  ) and periodo_num(ap.code) <= periodo_num('""" + self.periodo_ini.code + """')
and periodo_num(ap.code)>= (substring('""" + self.periodo_ini.code + """'::varchar,4,4)||'00')::integer
group by artm.id, artm.concepto
) T1
where rm_balance_mexicano_line.dos_concepto = T1.concepto
and rm_balance_mexicano_line.padre = """ + str(self.id) + """
			""")
		

		self.env.cr.execute("""
update rm_balance_mexicano_line
set dos_monto_mes_anterior= T1.monto
from ( select artm.id, artm.concepto, CASE WHEN artm.grupo_cuenta = '1' or artm.grupo_cuenta = '2' or artm.grupo_cuenta = '3' or artm.grupo_cuenta = '4' or artm.grupo_cuenta = '5' or artm.grupo_cuenta = '6' or artm.grupo_cuenta = '7'
THEN sum(debit-credit) ELSE sum(credit-debit) END as monto from
account_account aa
inner join account_move_line aml on aml.account_id = aa.id
inner join account_move am on am.id = aml.move_id
inner join account_period ap on ap.id = am.period_id
inner join rm_balance_config_mexicano_line artm on artm.id = aa.balance_type_mex_id
where (artm.tipo_cuenta = '1'  ) and periodo_num(ap.code) <= periodo_num('""" + self.periodo_ini_ant.code + """')
and periodo_num(ap.code)>= (substring('""" + self.periodo_ini_ant.code + """'::varchar,4,4)||'00')::integer
and am.state != 'draft'
group by artm.id, artm.concepto
) T1
where rm_balance_mexicano_line.dos_concepto = T1.concepto
and rm_balance_mexicano_line.padre = """ + str(self.id) + """
			""")

		for i in self.lineas:
			i.refresh()		

		for ii in cuentas_list:
			ii.balance_type_mex_id = param_report.tributos.id 


	@api.one
	def calculate(self):
		

		for i in self.lineas:
			i.refresh()		

		directorio_mes_actual = [
			[2,'UTILIDAD',"i._sum_total_utilidad_(1]"],
			[2,'SUMA_PASIVO_CAPITAL_TOTAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO + TOTAL_CAPITAL_CONTABLE"],
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
		]

		directorio_mes_anterior = [
			[2,'UTILIDAD',"i._sum_total_utilidad_(2]"],
			[2,'SUMA_PASIVO_CAPITAL_TOTAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO + TOTAL_CAPITAL_CONTABLE"],
			[2,'SUMA_PASIVO_CAPITAL',"TOTAL_PASIVO_CIRCULANTE + TOTAL_PASIVO_FIJO"],
			[2,'SUMA_DEL_ACTIVO',"TOTAL_CIRCULANTE + TOTAL_FIJO + TOTAL_DIFERIDO"],
			[2,'TOTAL_FIJO',"TOTAL_5 + TOTAL_ACTIVO_FIJO"],
			[2,'TOTAL_CIRCULANTE',"TOTAL_EXIGIBLE + TOTAL_REALIZABLE + TOTAL_DISPONIBLE"],
			[1,'DEUDA_INTRINSECA_ARRENDAMIENTO',"i._sum_total_('11',2]"],
			[1,'TOTAL_CAPITAL_CONTABLE',"i._sum_total_('10',2]"],
			[1,'TOTAL_PASIVO_FIJO',"i._sum_total_('9',2]"],
			[1,'TOTAL_PASIVO_CIRCULANTE',"i._sum_total_('8',2]"],
			[1,'VALOR_ACTUAL_ARRENDAMIENTO',"i._sum_total_('7',2]"],
			[1,'TOTAL_DIFERIDO',"i._sum_total_('6',2]"],
			[1,'TOTAL_5',"i._sum_total_('5',2]"],
			[1,'TOTAL_ACTIVO_FIJO',"i._sum_total_('4',2]"],
			[1,'TOTAL_EXIGIBLE',"i._sum_total_('2',2]"],
			[1,'TOTAL_REALIZABLE',"i._sum_total_('3',2]"],
			[1,'TOTAL_DISPONIBLE',"i._sum_total_('1',2]"],
			[1,'L[',"i._cal_orden_('1','2',"],
			[1,'R[',"i._cal_orden_('2','2',"],
		]
		
		for i in self.env['rm.balance.mexicano.line'].search([('uno_tipo_cuenta','=','3'),('padre','=',self.id)]):
			val = 0
			try:
				tmp_formula = i.uno_formula					
				for dir_m_ac in directorio_mes_actual:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2])

				#print "formula 1",tmp_formula
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!', "val = " + i.formula.replace('L[','i.calculo_prog_mes_uno(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.uno_formula )

			#print val
			i.uno_monto_mes = val

			val = 0
			try:
				tmp_formula = i.uno_formula					
				for dir_m_ac in directorio_mes_anterior:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2])

				#print "formula 2",tmp_formula
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!',"val = " + i.formula.replace('L[','i.calculo_prog_anterior_uno(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.uno_formula )

			i.uno_monto_mes_anterior = val



		for i in self.env['rm.balance.mexicano.line'].search([('dos_tipo_cuenta','=','3'),('padre','=',self.id)]):
			val = 0
			try:
				tmp_formula = i.dos_formula					
				for dir_m_ac in directorio_mes_actual:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2])

				#print "formula 3",tmp_formula
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!', "val = " + i.formula.replace('L[','i.calculo_prog_mes_dos(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.dos_formula )

			#print val
			i.dos_monto_mes = val

			val = 0
			try:
				tmp_formula = i.dos_formula					
				for dir_m_ac in directorio_mes_anterior:
					tmp_formula = tmp_formula.replace(dir_m_ac[1],dir_m_ac[2])

				#print "formula 4",tmp_formula
				exec("val = " + tmp_formula.replace(']',')[0]'))
			except:
				#raise osv.except_osv('Alerta!', "val = " + i.formula.replace('L[','i.calculo_prog_anterior_dos(').replace(']',')[0]') )
				raise osv.except_osv('Alerta!', u"No tiene un formato correcto: "+ i.dos_formula )

			i.dos_monto_mes_anterior = val




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
			'output_name': 'Reportes Mexicanos Balance.pdf',
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
		c.drawString( 404 + adicional, pos_inicial, "CALQUIPA S.A.C")
		c.setFont("Arimo-Bold", 11)
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,30,pagina)

		c.setFont("Arimo-Regular", 10)
		c.drawString( 404 + adicional, pos_inicial, "Balance General Consolidado")
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)
		c.drawString( 404 + adicional, pos_inicial, "Expresado en Nuevo Soles" )
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,55,pagina)



		#c.setStrokeColor(black)
		#c.setFillColor("#CCCCFF")
		#c.rect(105+adicional, pos_inicial, 300 , 30, stroke=1, fill=1)
		#c.rect(510+adicional, pos_inicial, 300 , 30, stroke=1, fill=1)

		#c.line(105 + adicional, pos_inicial, 105 + adicional , pos_inicial + 30)
		#c.line(205 + adicional, pos_inicial, 205 + adicional , pos_inicial + 30)
		#c.line(255 + adicional, pos_inicial, 255 + adicional , pos_inicial + 30)
		#c.line(305 + adicional, pos_inicial, 305 + adicional , pos_inicial + 30)
		#c.line(355 + adicional, pos_inicial, 355 + adicional , pos_inicial + 30)
		#c.line(405 + adicional, pos_inicial, 405 + adicional , pos_inicial + 30)
		#c.line(510 + adicional, pos_inicial, 510 + adicional , pos_inicial + 30)
		#c.line(610 + adicional, pos_inicial, 610 + adicional , pos_inicial + 30)
		#c.line(660 + adicional, pos_inicial, 660 + adicional , pos_inicial + 30)
		#c.line(710 + adicional, pos_inicial, 710 + adicional , pos_inicial + 30)
		#c.line(760 + adicional, pos_inicial, 760 + adicional , pos_inicial + 30)
		#c.line(810 + adicional, pos_inicial, 810 + adicional , pos_inicial + 30)


		c.setFillColor(black)
		c.setFont("Arimo-BoldItalic", 9)
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

		#c.drawCentredString(105 + 50 + adicional,pos_inicial + 15, u"Cuenta")
		c.drawCentredString(205 + 25 + adicional,pos_inicial + 22, dic_anio[self.periodo_ini.code.split('/')[0]])

		c.setFont("Arimo-BoldItalic", 7)
		#c.drawCentredString(205 + 25 + adicional,pos_inicial + 12, 'S/.')
		c.drawCentredString(205 + 25 + adicional,pos_inicial + 3, self.periodo_ini.code.split('/')[1])
		c.setFont("Arimo-BoldItalic", 9)
		c.drawCentredString(255 + 25 + adicional,pos_inicial + 22, dic_anio[self.periodo_ini.code.split('/')[0]])
		c.setFont("Arimo-BoldItalic", 7)
		#c.drawCentredString(255 + 25 + adicional,pos_inicial + 12, 'USD')
		c.drawCentredString(255 + 25 + adicional,pos_inicial + 3, self.periodo_ini.code.split('/')[1])

		c.setFont("Arimo-BoldItalic", 9)
		c.drawCentredString(305 + 25 + adicional,pos_inicial + 22, dic_anio[self.periodo_ini_ant.code.split('/')[0]])
		c.setFont("Arimo-BoldItalic", 7)
		#c.drawCentredString(305 + 25 + adicional,pos_inicial + 12, 'S/.')
		c.drawCentredString(305 + 25 + adicional,pos_inicial + 3, self.periodo_ini_ant.code.split('/')[1])
		c.setFont("Arimo-BoldItalic", 9)
		c.drawCentredString(355 + 25 + adicional,pos_inicial + 22, dic_anio[self.periodo_ini_ant.code.split('/')[0]])
		c.setFont("Arimo-BoldItalic", 7)
		#c.drawCentredString(355 + 25 + adicional,pos_inicial + 12, 'USD')
		c.drawCentredString(355 + 25 + adicional,pos_inicial + 3, self.periodo_ini_ant.code.split('/')[1])

		c.setFont("Arimo-BoldItalic", 9)
		#c.drawCentredString(510 + 50 + adicional,pos_inicial + 15, u"Cuenta")

		c.setFont("Arimo-BoldItalic", 9)
		c.drawCentredString(610 + 25 + adicional,pos_inicial + 22, dic_anio[self.periodo_ini.code.split('/')[0]])
		c.setFont("Arimo-BoldItalic", 7)
		#c.drawCentredString(610 + 25 + adicional,pos_inicial + 12, 'S/.')
		c.drawCentredString(610 + 25 + adicional,pos_inicial + 3, self.periodo_ini.code.split('/')[1])

		c.setFont("Arimo-BoldItalic", 9)
		c.drawCentredString(660 + 25 + adicional,pos_inicial + 22, dic_anio[self.periodo_ini.code.split('/')[0]])
		c.setFont("Arimo-BoldItalic", 7)
		#c.drawCentredString(660 + 25 + adicional,pos_inicial + 12, 'USD')
		c.drawCentredString(660 + 25 + adicional,pos_inicial + 3, self.periodo_ini.code.split('/')[1])

		c.setFont("Arimo-BoldItalic", 9)
		c.drawCentredString(710 + 25 + adicional,pos_inicial + 22, dic_anio[self.periodo_ini_ant.code.split('/')[0]])
		c.setFont("Arimo-BoldItalic", 7)
		#c.drawCentredString(710 + 25 + adicional,pos_inicial + 12, 'S/.')
		c.drawCentredString(710 + 25 + adicional,pos_inicial + 3, self.periodo_ini_ant.code.split('/')[1])
		c.setFont("Arimo-BoldItalic", 9)
		c.drawCentredString(760 + 25 + adicional,pos_inicial + 22, dic_anio[self.periodo_ini_ant.code.split('/')[0]])
		c.setFont("Arimo-BoldItalic", 7)
		#c.drawCentredString(760 + 25 + adicional,pos_inicial + 12, 'USD')
		c.drawCentredString(760 + 25 + adicional,pos_inicial + 3, self.periodo_ini_ant.code.split('/')[1])

		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,15,pagina)



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
		for i in self.env['rm.balance.mexicano.line'].search([('padre','=',self.id)]).sorted(lambda r : r.orden):

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)
			if i.uno_resaltado:
				c.setFont("Arimo-Bold", 6)
			else:
				c.setFont("Arimo-Regular", 6)
		
			if i.uno_concepto == '' or i.uno_concepto == False:
				pass
			else:
				if i.uno_tipo_cuenta == '5':
					#c.drawString( adicional + 2 , pos_inicial, self.particionar_text( dic_grup[i.uno_grupo_cuenta] ) if i.uno_grupo_cuenta else '' )		
					#c.drawString( adicional + 105 + 2 , pos_inicial, self.particionar_text(i.uno_concepto) if i.uno_concepto else '' )		
					c.drawString( adicional +  22 , pos_inicial, self.particionar_text(i.uno_concepto) if i.uno_concepto else '' )		
				else:
					#c.drawString( adicional + 2 , pos_inicial, self.particionar_text(dic_grup[i.uno_grupo_cuenta]) if i.uno_grupo_cuenta else '' )		
					c.drawString( adicional +20 + 2 , pos_inicial, self.particionar_text(i.uno_concepto) if i.uno_concepto else '' )		
					c.drawRightString( adicional + 205 + 50 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.uno_monto_mes)) )
					c.drawRightString( adicional + 205 + 100 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % ( (i.uno_monto_mes/ self.tipo_cambio) if self.tipo_cambio != 0 else 0 ) )) )
					c.drawRightString( adicional + 205 + 150 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.uno_monto_mes_anterior)) )
					c.drawRightString( adicional + 205 + 200 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % ( (i.uno_monto_mes_anterior/ self.tipo_cambio) if self.tipo_cambio != 0 else 0 ) )) )

			if i.dos_resaltado:
				c.setFont("Arimo-Bold", 6)
			else:
				c.setFont("Arimo-Regular", 6)


			if i.dos_concepto == '' or i.dos_concepto == False:
				pass
			else:
				if i.dos_tipo_cuenta == '5':
					#c.drawString( adicional + 405+ 2 , pos_inicial, self.particionar_text(dic_grup[i.uno_grupo_cuenta]) if i.uno_grupo_cuenta else '' )		
					#c.drawString( adicional + 405+105 + 2 , pos_inicial, self.particionar_text(i.dos_concepto) if i.dos_concepto else '' )		
					c.drawString( adicional + 405+ 22 , pos_inicial, self.particionar_text(i.dos_concepto) if i.dos_concepto else '' )		
				else:
					#c.drawString( adicional + 405+2 , pos_inicial, self.particionar_text(dic_grup[i.uno_grupo_cuenta]) if i.uno_grupo_cuenta else '' )		
					c.drawString( adicional + 405+20 + 2 , pos_inicial, self.particionar_text(i.dos_concepto) if i.dos_concepto else '' )		
					c.drawRightString( adicional + 405+105 + 100 + 50 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.dos_monto_mes)) )
					c.drawRightString( adicional + 405+105 + 100 + 100 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % ( (i.dos_monto_mes/ self.tipo_cambio) if self.tipo_cambio != 0 else 0 ) )) )
					c.drawRightString( adicional + 405+105 + 100 + 150 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.dos_monto_mes_anterior)) )
					c.drawRightString( adicional + 405+105 + 100 + 200 - 2 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % ( (i.dos_monto_mes_anterior/ self.tipo_cambio) if self.tipo_cambio != 0 else 0 ) )) )

			if i.uno_bordes:
				c.line( adicional + 205, pos_inicial-2, adicional + 125 + 280 ,pos_inicial-2)
				c.line( adicional + 205, pos_inicial-5, adicional + 125 + 280 ,pos_inicial-5)
				c.line( adicional + 205, pos_inicial+9, adicional + 125 + 280 ,pos_inicial+9)

			if i.dos_bordes:
				c.line( adicional + 205 + 280+ 125, pos_inicial-2, adicional + 125 + 280+ 125+ 280 ,pos_inicial-2)
				c.line( adicional + 205 + 280+ 125, pos_inicial-5, adicional + 125 + 280+ 125+ 280 ,pos_inicial-5)
				c.line( adicional + 205 + 280+ 125, pos_inicial+9, adicional + 125 + 280+ 125+ 280 ,pos_inicial+9)		
		c.save()

	@api.multi
	def particionar_text(self,c):
		tet = ""
		for i in range(len(c)):
			tet += c[i]
			lines = simpleSplit(tet,'Arimo-Regular',9,220)
			if len(lines)>1:
				return tet[:-1]
		return tet

	@api.multi
	def verify_linea(self,c,wReal,hReal,posactual,valor,pagina):
		if posactual <40:
			c.showPage()
			self.cabezera(c,wReal,hReal)

			#c.setFont("Arimo-Bold", 10)
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

		workbook = Workbook(direccion +'Reporte_balance_mexicano.xlsx')
		worksheet = workbook.add_worksheet(u"Balance")
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

		worksheet.write(6,2, dic_anio[self.periodo_ini.code.split('/')[0]] , titlees)
		worksheet.write(8,2, 'S/.' , boldbord)
		worksheet.write(7,2, self.periodo_ini.code.split('/')[1] , titlees)

		worksheet.write(6,3, dic_anio[self.periodo_ini.code.split('/')[0]] , titlees)
		worksheet.write(8,3, 'USD' , boldbord)
		worksheet.write(7,3, self.periodo_ini.code.split('/')[1] , titlees)


		worksheet.write(6,4, dic_anio[self.periodo_ini_ant.code.split('/')[0]] , titlees)
		worksheet.write(8,4, 'S/.' , boldbord)
		worksheet.write(7,4, self.periodo_ini_ant.code.split('/')[1] , titlees)

		worksheet.write(6,5, dic_anio[self.periodo_ini_ant.code.split('/')[0]] , titlees)
		worksheet.write(8,5, 'USD' , boldbord)
		worksheet.write(7,5, self.periodo_ini_ant.code.split('/')[1] , titlees)


		#worksheet.merge_range(6,7,8,7,u'Cuenta', boldbord)

		worksheet.write(6,8, dic_anio[self.periodo_ini.code.split('/')[0]] , titlees)
		worksheet.write(8,8, 'S/.' , boldbord)
		worksheet.write(7,8, self.periodo_ini.code.split('/')[1] , titlees)

		worksheet.write(6,9, dic_anio[self.periodo_ini.code.split('/')[0]] , titlees)
		worksheet.write(8,9, 'USD' , boldbord)
		worksheet.write(7,9, self.periodo_ini.code.split('/')[1] , titlees)


		worksheet.write(6,10, dic_anio[self.periodo_ini_ant.code.split('/')[0]] , titlees)
		worksheet.write(8,10, 'S/.' , boldbord)
		worksheet.write(7,10, self.periodo_ini_ant.code.split('/')[1] , titlees)

		worksheet.write(6,11, dic_anio[self.periodo_ini_ant.code.split('/')[0]] , titlees)
		worksheet.write(8,11, 'USD' , boldbord)
		worksheet.write(7,11, self.periodo_ini_ant.code.split('/')[1] , titlees)
				
		x = 9


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

		xi = 9
		xf = 9

		for i in self.env['rm.balance.mexicano.line'].search([('padre','=',self.id)]).sorted(lambda r : r.orden):

			if i.uno_concepto == '' or i.uno_concepto == False:
				xi += 1
			else:
				if i.uno_tipo_cuenta == '5':

					boldbordtmp = workbook.add_format({'bold': False})
					boldbordtmp.set_font_size(9)
					if i.uno_resaltado:
						boldbordtmp = workbook.add_format({'bold': True})
						boldbordtmp.set_text_wrap()
						boldbordtmp.set_font_size(9)
					if i.uno_bordes:
						boldbordtmp.set_border(style=2)
					#worksheet.write(x,0, dic_grup[i.uno_grupo_cuenta] if i.uno_grupo_cuenta else '',boldbordtmp)
					worksheet.write(xi,1, i.uno_concepto if i.uno_concepto else '',boldbordtmp)
					xi += 1
				else:			
					boldbordtmp = workbook.add_format({'bold': False})
					boldbordtmp.set_font_size(9)
					boldbordtmpRight = workbook.add_format({'bold': False})
					boldbordtmpRight.set_font_size(9)
					boldbordtmpRight.set_align('right')
					boldbordtmpRight.set_align('vright')
					numberdostmp = workbook.add_format({'num_format':'#,##0.00'})
					numberdostmp.set_font_size(9)
					if i.uno_resaltado:
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
					if i.uno_bordes:
						boldbordtmp.set_border(style=2)
						numberdostmp.set_border(style=2)

						boldbordtmpRight.set_border(style=2)


					if True:
						#worksheet.write(x,0, dic_grup[i.uno_grupo_cuenta] if i.uno_grupo_cuenta else '',boldbordtmp)
						worksheet.write(xi,1, i.uno_concepto if i.uno_concepto else '',boldbordtmp)

						worksheet.write(xi,2, i.uno_monto_mes ,numberdostmp)
						worksheet.write(xi,3, ( i.uno_monto_mes / self.tipo_cambio) if self.tipo_cambio != 0 else 0 ,numberdostmp)
						worksheet.write(xi,4, i.uno_monto_mes_anterior ,numberdostmp)
						worksheet.write(xi,5, (i.uno_monto_mes_anterior / self.tipo_cambio) if self.tipo_cambio != 0 else 0 ,numberdostmp)
						xi += 1

			if i.dos_concepto == '' or i.dos_concepto == False:
				xf += 1
			else:
				if i.dos_tipo_cuenta == '5':

					boldbordtmp = workbook.add_format({'bold': False})
					boldbordtmp.set_font_size(9)
					if i.dos_resaltado:
						boldbordtmp = workbook.add_format({'bold': True})
						boldbordtmp.set_text_wrap()
						boldbordtmp.set_font_size(9)
					if i.dos_bordes:
						boldbordtmp.set_border(style=2)
					#worksheet.write(x,6, dic_grup[i.uno_grupo_cuenta] if i.uno_grupo_cuenta else '',boldbordtmp)
					worksheet.write(xf,7, i.dos_concepto if i.dos_concepto else '',boldbordtmp)
					xf += 1
				else:			
					boldbordtmp = workbook.add_format({'bold': False})
					boldbordtmp.set_font_size(9)
					boldbordtmpRight = workbook.add_format({'bold': False})
					boldbordtmpRight.set_font_size(9)
					boldbordtmpRight.set_align('right')
					boldbordtmpRight.set_align('vright')
					numberdostmp = workbook.add_format({'num_format':'#,##0.00'})
					numberdostmp.set_font_size(9)
					if i.dos_resaltado:
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
					if i.dos_bordes:
						boldbordtmp.set_border(style=2)
						numberdostmp.set_border(style=2)

						boldbordtmpRight.set_border(style=2)


					if True:
						#worksheet.write(x,6, dic_grup[i.uno_grupo_cuenta] if i.uno_grupo_cuenta else '',boldbordtmp)
						worksheet.write(xf,7, i.dos_concepto if i.dos_concepto else '',boldbordtmp)

						worksheet.write(xf,8, i.dos_monto_mes ,numberdostmp)
						worksheet.write(xf,9, (i.dos_monto_mes / self.tipo_cambio) if self.tipo_cambio != 0 else 0 ,numberdostmp)
						worksheet.write(xf,10, i.dos_monto_mes_anterior ,numberdostmp)
						worksheet.write(xf,11, (i.dos_monto_mes_anterior / self.tipo_cambio) if self.tipo_cambio != 0 else 0,numberdostmp)
						xf += 1
			x += 1

		t = 14.86
		worksheet.set_column('A:A', t)
		worksheet.set_column('B:B', 50)
		worksheet.set_column('C:C', t)
		worksheet.set_column('D:D', t)
		worksheet.set_column('E:E', t)
		worksheet.set_column('F:F', t)
		worksheet.set_column('G:G', t)
		worksheet.set_column('H:H', 50)
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