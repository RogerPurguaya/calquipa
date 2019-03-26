# -*- encoding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs

import datetime
import decimal
from calendar import monthrange
from dateutil import relativedelta as rdelta

import sys
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import magenta, red , black , blue, gray, white, Color, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table
from reportlab.lib.units import  cm,mm
from reportlab.lib.utils import simpleSplit
from cgi import escape

def number_to_letter(number, mi_moneda=None):
	UNIDADES = (
		'',
		'UN ',
		'DOS ',
		'TRES ',
		'CUATRO ',
		'CINCO ',
		'SEIS ',
		'SIETE ',
		'OCHO ',
		'NUEVE ',
		'DIEZ ',
		'ONCE ',
		'DOCE ',
		'TRECE ',
		'CATORCE ',
		'QUINCE ',
		'DIECISEIS ',
		'DIECISIETE ',
		'DIECIOCHO ',
		'DIECINUEVE ',
		'VEINTE '
	)

	DECENAS = (
		'VENTI',
		'TREINTA ',
		'CUARENTA ',
		'CINCUENTA ',
		'SESENTA ',
		'SETENTA ',
		'OCHENTA ',
		'NOVENTA ',
		'CIEN '
	)

	CENTENAS = (
		'CIENTO ',
		'DOSCIENTOS ',
		'TRESCIENTOS ',
		'CUATROCIENTOS ',
		'QUINIENTOS ',
		'SEISCIENTOS ',
		'SETECIENTOS ',
		'OCHOCIENTOS ',
		'NOVECIENTOS '
	)

	MONEDAS = (
		{'country': u'Colombia', 'currency': 'COP', 'singular': u'PESO COLOMBIANO', 'plural': u'PESOS COLOMBIANOS', 'symbol': u'$'},
		{'country': u'Estados Unidos', 'currency': 'USD', 'singular': u'DÓLAR', 'plural': u'DOLARES', 'symbol': u'US$'},
		{'country': u'Europa', 'currency': 'EUR', 'singular': u'EURO', 'plural': u'EUROS', 'symbol': u'€'},
		{'country': u'México', 'currency': 'MXN', 'singular': u'PESO MEXICANO', 'plural': u'PESOS MEXICANOS', 'symbol': u'$'},
		{'country': u'Perú', 'currency': 'PEN', 'singular': u'SOL', 'plural': u'SOLES', 'symbol': u'S/.'},
		{'country': u'Reino Unido', 'currency': 'GBP', 'singular': u'LIBRA', 'plural': u'LIBRAS', 'symbol': u'£'}
	)
	# Para definir la moneda me estoy basando en los código que establece el ISO 4217
	# Decidí poner las variables en inglés, porque es más sencillo de ubicarlas sin importar el país
	# Si, ya sé que Europa no es un país, pero no se me ocurrió un nombre mejor para la clave.

	def __convert_group(n):
		"""Turn each group of numbers into letters"""
		output = ''

		if(n == '100'):
			output = "CIEN"
		elif(n[0] != '0'):
			output = CENTENAS[int(n[0]) - 1]

		k = int(n[1:])
		if(k <= 20):
			output += UNIDADES[k]
		else:
			if((k > 30) & (n[2] != '0')):
				output += '%sY %s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])
			else:
				output += '%s%s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])
		return output
	#raise osv.except_osv('Alerta', number)
	number=str(round(float(number),2))
	separate = number.split(".")
	number = int(separate[0])
	if mi_moneda != None:
		try:
			moneda = ""
			for moneda1 in MONEDAS:
				if moneda1['currency']==mi_moneda:
				# moneda = ifilter(lambda x: x['currency'] == mi_moneda, MONEDAS).next()
				# return "Tipo de moneda inválida"
					if number < 2:
						#raise osv.except_osv('Alerta', number)
						if float(number)==0:
							moneda = moneda1['plural']
						else:
							if int(separate[1]) > 0:
								moneda = moneda1['plural']
							else:
								moneda = moneda1['singular']
					else:
						moneda = moneda1['plural']
		except:
			return "Tipo de moneda inválida"
	else:
		moneda = ""

	if int(separate[1]) >= 0:
		moneda = "con " + str(separate[1]).ljust(2,'0') + "/" + "100 " + moneda

	"""Converts a number into string representation"""
	converted = ''
	
	if not (0 <= number < 999999999):
		raise osv.except_osv('Alerta', number)
		#return 'No es posible convertir el numero a letras'

	
	
	number_str = str(number).zfill(9)
	millones = number_str[:3]
	miles = number_str[3:6]
	cientos = number_str[6:]
	

	if(millones):
		if(millones == '001'):
			converted += 'UN MILLON '
		elif(int(millones) > 0):
			converted += '%sMILLONES ' % __convert_group(millones)

	if(miles):
		if(miles == '001'):
			converted += 'MIL '
		elif(int(miles) > 0):
			converted += '%sMIL ' % __convert_group(miles)

	if(cientos):
		if(cientos == '001'):
			converted += 'UN '
		elif(int(cientos) > 0):
			converted += '%s ' % __convert_group(cientos)
	if float(number_str)==0:
		converted += 'CERO '
	converted += moneda

	return converted.upper()

def date_to_month(m):
	meses = {
		1:	"Enero",
		2:	"Febrero",
		3:	"Marzo",
		4: "Abril",
		5: "Mayo",
		6: "Junio",
		7: "Julio",
		8: "Agosto",
		9: "Setiembre",
		10: "Octubre",
		11: "Noviembre",
		12: "Diciembre",
	}
	return meses[m]

class hr_liquidaciones(models.Model):
	_name = 'hr.liquidaciones'

	period_id = fields.Many2one('account.period','Periodo')
	check_bonus = fields.Boolean('Bonificación')

	familiar_assignation = fields.Float('Asignacion Familiar', compute="get_familiar_assignation")

	lines_cts = fields.One2many('hr.liquidaciones.lines.cts','liquidacion_id', u'Línea CTS')
	lines_grat = fields.One2many('hr.liquidaciones.lines.grat','liquidacion_id', u'Línea Gratificación')
	lines_vac = fields.One2many('hr.liquidaciones.lines.vac','liquidacion_id', u'Línea Vacaciones')

	_rec_name = 'period_id'

	@api.model
	def create(self, vals):
		hl = self.env['hr.liquidaciones'].search([('period_id','=',vals['period_id'])])
		t = super(hr_liquidaciones,self).create(vals)
		if len(hl) > 0:
			raise osv.except_osv('Alerta!', u"Ya existe una liquidación con el mismo periodo.")
		return t

	@api.one
	def get_familiar_assignation(self):
		if len(self.env['hr.parameters'].search([])) > 0:
			self.familiar_assignation = self.env['hr.parameters'].search([('num_tipo','=',10001)])[0].monto
		else:
			self.familiar_assignation = 85

	@api.one
	def calculate(self):
		
		for i in self.env["hr.employee"].search([]):		
			if i.fecha_cese <= self.period_id.date_stop and i.fecha_cese >= self.period_id.date_start:
				if len(self.env['hr.liquidaciones.lines.cts'].search([('liquidacion_id','=',self.id), ('employee_id','=',i.id)])) > 0:
					pass
				else:
					temp_faltas = 0

					obj = self.env["hr.tareo.line"].search([('employee_id','=',i.id)])
					for f in obj:
						temp_faltas += f.dias_suspension_perfecta

					basic_rem = i.basica
					if i.children_number:
						basic_rem += self.familiar_assignation
					if i.is_practicant:
						basic_rem /= 2
					data = {
						'employee_id': i.id,
						'start_date': i.fecha_ingreso,
						'cese_date': i.fecha_cese,
						'basic_remuneration': basic_rem,
						'absences': temp_faltas,
						'sixth_gratification': 0,
						'issue_date': datetime.datetime.today(),
						'liquidacion_id': self.id,
					}
					self.env['hr.liquidaciones.lines.cts'].create(data)

					data_grat = {
						'employee_id': i.id,
						'start_date': i.fecha_ingreso,
						'cese_date': i.fecha_cese,
						'basic_remuneration': basic_rem,
						'absences': temp_faltas,
						'issue_date': datetime.datetime.today(),
						'liquidacion_id': self.id,
					}
					self.env['hr.liquidaciones.lines.grat'].create(data_grat)

					data_vac = {
						'employee_id': i.id,
						'start_date': i.fecha_ingreso,
						'cese_date': i.fecha_cese,
						'basic_remuneration': basic_rem,
						'absences': temp_faltas,
						'fall_due_holidays': 0,
						'issue_date': datetime.datetime.today(),
						'liquidacion_id': self.id,
					}
					self.env['hr.liquidaciones.lines.vac'].create(data_vac)

		for i in self.env['hr.liquidaciones.lines.cts'].search([('liquidacion_id','=',self.id)]):
			if i.employee_id.fecha_cese >= self.period_id.date_start:
				obj = self.env['hr.employee'].search([('id','=',i.employee_id.id)])
				rem_base = obj[0].basica
				if obj.children_number:
					rem_base += self.familiar_assignation
				if obj.is_practicant:
					rem_base /= 2
				i.basic_remuneration = rem_base
				i.start_date = obj[0].fecha_ingreso
				i.employee_id.children_number = obj[0].children_number
			else:
				i.unlink()
		for i in self.env['hr.liquidaciones.lines.grat'].search([('liquidacion_id','=',self.id)]):
			if i.employee_id.fecha_cese >= self.period_id.date_start:
				obj = self.env['hr.employee'].search([('id','=',i.employee_id.id)])
				rem_base = obj[0].basica
				if obj.children_number:
					rem_base += self.familiar_assignation
				if obj.is_practicant:
					rem_base /= 2
				i.basic_remuneration = rem_base
				i.start_date = obj[0].fecha_ingreso
				i.employee_id.children_number = obj[0].children_number
			else:
				i.unlink()
		for i in self.env['hr.liquidaciones.lines.vac'].search([('liquidacion_id','=',self.id)]):
			if i.employee_id.fecha_cese >= self.period_id.date_start:
				obj = self.env['hr.employee'].search([('id','=',i.employee_id.id)])
				rem_base = obj[0].basica
				if obj.children_number:
					rem_base += self.familiar_assignation
				if obj.is_practicant:
					rem_base /= 2
				i.basic_remuneration = rem_base
				i.start_date = obj[0].fecha_ingreso
				i.employee_id.children_number = obj[0].children_number
			else:
				i.unlink()

	@api.multi
	def export(self):

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
		workbook = Workbook( direccion + u'Liquidaciones.xlsx')
		worksheet_cts = workbook.add_worksheet(u"Liquidación CTS")
		worksheet_grat = workbook.add_worksheet(u"Liquidación Gratificación")
		worksheet_vac = workbook.add_worksheet(u"Liquidación Vacación")
		bold = workbook.add_format({'bold': True})
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		bord = workbook.add_format()
		bord.set_border(style=1)
		numberdos.set_border(style=1)
		numbertres.set_border(style=1)	

		x= 6				
		worksheet_cts.write(0,0, u"Liquidación CTS:", bold)

		worksheet_cts.write(5,0, u"Nombre",boldbord)
		worksheet_cts.write(5,1, u"Fecha Ingreso",boldbord)
		worksheet_cts.write(5,2, u"Fecha Inicio Comp.",boldbord)
		worksheet_cts.write(5,3, u"Fecha Cese",boldbord)
		worksheet_cts.write(5,4, u"Faltas",boldbord)
		worksheet_cts.write(5,5, u"Remuneración Básica",boldbord)
		worksheet_cts.write(5,6, u"Promedio Sobret Noc.",boldbord)
		worksheet_cts.write(5,7, u"6ta Gratificación",boldbord)
		worksheet_cts.write(5,8, u"Remuneración Computable",boldbord)
		worksheet_cts.write(5,9, u"Meses Comp.",boldbord)
		worksheet_cts.write(5,10, u"Días Comp.",boldbord)
		worksheet_cts.write(5,11, u"Por los Meses",boldbord)
		worksheet_cts.write(5,12, u"Por los Días",boldbord)
		worksheet_cts.write(5,13, u"Total a Pagar",boldbord)
		for line in self.lines_cts:
			worksheet_cts.write(x,0, "{0} {1} {2}".format(line.employee_id.last_name_father, line.employee_id.last_name_mother, line.employee_id.first_name_complete) if line.employee_id else '' ,bord )
			worksheet_cts.write(x,1,line.start_date if line.start_date else '', bord)
			worksheet_cts.write(x,2,line.comp_date if line.comp_date else '', bord)
			worksheet_cts.write(x,3,line.cese_date if line.cese_date else '', bord)
			worksheet_cts.write(x,4,line.absences if line.absences else '0', bord)
			worksheet_cts.write(x,5,line.basic_remuneration if line.basic_remuneration else '0', numberdos)
			worksheet_cts.write(x,6,line.nocturnal_surcharge_mean if line.nocturnal_surcharge_mean else '0', numberdos)
			worksheet_cts.write(x,7,line.sixth_gratification if line.sixth_gratification else '0', numberdos)
			worksheet_cts.write(x,8,line.computable_remuneration if line.computable_remuneration else '0', numberdos)
			worksheet_cts.write(x,9,line.computable_months if line.computable_months else '0', numberdos)
			worksheet_cts.write(x,10,line.computable_days if line.computable_days else '0', numberdos)
			worksheet_cts.write(x,11,line.for_months if line.for_months else '0', numberdos)
			worksheet_cts.write(x,12,line.for_days if line.for_days else '0', numberdos)
			worksheet_cts.write(x,13,line.total_payment if line.total_payment else '0', numberdos)
			x = x + 1
		worksheet_cts.set_column('A:A', 31.43)
		worksheet_cts.set_column('B:N', 13)

		x=6
		worksheet_grat.write(0,0, u"Liquidación Gratificaciones:", bold)

		worksheet_grat.write(5,0, u"Nombre",boldbord)
		worksheet_grat.write(5,1, u"Fecha Ingreso",boldbord)
		worksheet_grat.write(5,2, u"Fecha Inicio Comp.",boldbord)
		worksheet_grat.write(5,3, u"Fecha Cese",boldbord)
		worksheet_grat.write(5,4, u"Faltas",boldbord)
		worksheet_grat.write(5,5, u"Remuneración Básica",boldbord)
		worksheet_grat.write(5,6, u"Promedio Sobret Noc.",boldbord)
		worksheet_grat.write(5,7, u"Remuneración Computable",boldbord)
		worksheet_grat.write(5,8, u"Meses Comp.",boldbord)
		worksheet_grat.write(5,9, u"Días Comp.",boldbord)
		worksheet_grat.write(5,10, u"Por los Meses",boldbord)
		worksheet_grat.write(5,11, u"Por los Días",boldbord)
		worksheet_grat.write(5,12, u"Total Meses",boldbord)
		worksheet_grat.write(5,13, u"Bonificación",boldbord)
		worksheet_grat.write(5,14, u"Total Grat. Bon.",boldbord)
		worksheet_grat.write(5,15, u"ONP",boldbord)
		worksheet_grat.write(5,16, u"AFP JUB",boldbord)
		worksheet_grat.write(5,17, u"AFP SI",boldbord)
		worksheet_grat.write(5,18, u"AFP COM",boldbord)
		worksheet_grat.write(5,19, u"Neto Total",boldbord)
		for line in self.lines_grat:
			worksheet_grat.write(x,0, "{0} {1} {2}".format(line.employee_id.last_name_father, line.employee_id.last_name_mother, line.employee_id.first_name_complete) if line.employee_id else '' ,bord )
			worksheet_grat.write(x,1,line.start_date if line.start_date else '', bord)
			worksheet_grat.write(x,2,line.comp_date if line.comp_date else '', bord)
			worksheet_grat.write(x,3,line.cese_date if line.cese_date else '', bord)
			worksheet_grat.write(x,4,line.absences if line.absences else '0', bord)
			worksheet_grat.write(x,5,line.basic_remuneration if line.basic_remuneration else '0', numberdos)
			worksheet_grat.write(x,6,line.nocturnal_surcharge_mean if line.nocturnal_surcharge_mean else '0', numberdos)
			worksheet_grat.write(x,7,line.computable_remuneration if line.computable_remuneration else '0' ,numberdos )
			worksheet_grat.write(x,8,line.computable_months if line.computable_months else '0' ,bord )
			worksheet_grat.write(x,9,line.computable_days if line.computable_days else '0' ,bord )
			worksheet_grat.write(x,10,line.for_months if line.for_months else '0' ,numberdos )
			worksheet_grat.write(x,11,line.for_days if line.for_days else '0' ,numberdos )
			worksheet_grat.write(x,12,line.total_months if line.total_months else '0' ,numberdos )
			worksheet_grat.write(x,13,line.bonus if line.bonus else '0' ,numberdos )
			worksheet_grat.write(x,14,line.total_gratification_bonus if line.total_gratification_bonus else '0' ,numberdos )
			worksheet_grat.write(x,15,line.ONP if line.ONP else '0' ,numberdos )
			worksheet_grat.write(x,16,line.AFP_JUB if line.AFP_JUB else '0' ,numberdos )
			worksheet_grat.write(x,17,line.AFP_SI if line.AFP_SI else '0' ,numberdos )
			worksheet_grat.write(x,18,line.AFP_COM if line.AFP_COM else '0' ,numberdos )
			worksheet_grat.write(x,19,line.total_net if line.total_net else '0' ,numberdos )
			x = x + 1
		worksheet_grat.set_column('A:A', 31.43)
		worksheet_grat.set_column('B:N', 13)

		x=6
		worksheet_vac.write(0,0, u"Liquidación Vacación:", bold)

		worksheet_vac.write(5,0, u"Nombre", boldbord)
		worksheet_vac.write(5,1, u"Fecha Ingreso", boldbord)
		worksheet_vac.write(5,2, u"Fecha Inicio Comp.", boldbord)
		worksheet_vac.write(5,3, u"Fecha Cese", boldbord)
		worksheet_vac.write(5,4, u"Faltas", boldbord)
		worksheet_vac.write(5,5, u"Remuneración Básica", boldbord)
		worksheet_vac.write(5,6, u"Promedio Sobret. Noc.", boldbord)
		worksheet_vac.write(5,7, u"Remuneración Computable", boldbord)
		worksheet_vac.write(5,8, u"Meses Comp.", boldbord)
		worksheet_vac.write(5,9, u"Días Comp.", boldbord)
		worksheet_vac.write(5,10, u"Por los Meses", boldbord)
		worksheet_vac.write(5,11, u"Por los Días", boldbord)
		worksheet_vac.write(5,12, u"Vacaciones", boldbord)
		worksheet_vac.write(5,13, u"Vacaciones no Gozadas", boldbord)
		worksheet_vac.write(5,14, u"Total Vacaciones", boldbord)
		worksheet_vac.write(5,15, u"ONP", boldbord)
		worksheet_vac.write(5,16, u"AFP JUB", boldbord)
		worksheet_vac.write(5,17, u"AFP SI", boldbord)
		worksheet_vac.write(5,18, u"AFP COM", boldbord)
		worksheet_vac.write(5,19, u"Neto Total", boldbord)
		for line in self.lines_vac:
			worksheet_vac.write(x,0,"{0} {1} {2}".format(line.employee_id.last_name_father, line.employee_id.last_name_mother, line.employee_id.first_name_complete) if line.employee_id else '' ,bord )
			worksheet_vac.write(x,1,line.start_date if line.start_date else '' ,bord )
			worksheet_vac.write(x,2,line.comp_date if line.comp_date else '' ,bord )
			worksheet_vac.write(x,3,line.cese_date if line.cese_date else '' ,bord )
			worksheet_vac.write(x,4,line.absences if line.absences else '0' ,bord )
			worksheet_vac.write(x,5,line.basic_remuneration if line.basic_remuneration else '0' ,numberdos )
			worksheet_vac.write(x,6,line.nocturnal_surcharge_mean if line.nocturnal_surcharge_mean else '0' ,numberdos )
			worksheet_vac.write(x,7,line.computable_remuneration if line.computable_remuneration else '0' ,numberdos )
			worksheet_vac.write(x,8,line.computable_months if line.computable_months else '0' ,bord )
			worksheet_vac.write(x,9,line.computable_days if line.computable_days else '0' ,bord )
			worksheet_vac.write(x,10,line.for_months if line.for_months else '0' ,numberdos )
			worksheet_vac.write(x,11,line.for_days if line.for_days else '0' ,numberdos )
			worksheet_vac.write(x,12,line.total_holidays_sinva if line.total_holidays_sinva else '0' ,numberdos )
			worksheet_vac.write(x,13,line.fall_due_holidays if line.fall_due_holidays else '0' ,numberdos )
			worksheet_vac.write(x,14,line.total_holidays if line.total_holidays else '0' ,numberdos )
			worksheet_vac.write(x,15,line.ONP if line.ONP else '' ,numberdos )
			worksheet_vac.write(x,16,line.AFP_JUB if line.AFP_JUB else '0' ,numberdos )
			worksheet_vac.write(x,17,line.AFP_SI if line.AFP_SI else '0' ,numberdos )
			worksheet_vac.write(x,18,line.AFP_COM if line.AFP_COM else '0' ,numberdos )
			worksheet_vac.write(x,19,line.total_net if line.total_net else '0' ,numberdos )
			x = x + 1
		worksheet_vac.set_column('A:A', 31.43)
		worksheet_vac.set_column('B:N', 13)

		workbook.close()
		
		f = open( direccion + u'Liquidaciones.xlsx', 'rb')
		
		
		vals = {
			'output_name': u'Liquidaciones.xlsx',
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
			'output_name': 'Liquidaciones Reporte.pdf',
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

		import os
		direccion = self.env['main.parameter'].search([])[0].dir_create_file

		c.setFont("Arimo-Bold", 8)
		c.setFillColor(black)
		endl = 12
		pos_inicial = hReal-10
		pagina = 1

		c.drawCentredString((wReal/2)+20,hReal-10, "ANEXO 1")
		c.line(285, hReal-12, 320 , hReal-12)
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*2,pagina)
		c.drawString( 30 , pos_inicial, u"Empresa: CALQUIPA SAC")
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
		c.drawString( 30 , pos_inicial, u"Dirección: URB. SAN JOSE D-11 - YANAHUARA")
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
		c.drawString( 30 , pos_inicial, u"RUC: 20455959943")
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*2,pagina)
		c.drawCentredString((wReal/2)+20,pos_inicial, u"LIQUIDACION DE BENEFICIOS SOCIALES")
		c.drawImage(direccion + 'calquipalright.png',20, hReal-20, width=120, height=50)
		c.drawImage(direccion + 'calquipalleft.png',430, hReal-35, width=140, height=70)

	@api.multi
	def reporteador(self):
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		width , height = A4  # 595 , 842
		wReal = width- 30
		hReal = height - 40

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		c = canvas.Canvas( direccion + "a.pdf", pagesize=A4)
		inicio = 0
		pos_inicial = hReal-100
		endl = 12
		font_size = 8

		pagina = 1
		textPos = 0

		pdfmetrics.registerFont(TTFont('Arimo-Bold', 'Arimo-Bold.ttf'))
		pdfmetrics.registerFont(TTFont('Arimo-BoldItalic', 'Arimo-BoldItalic.ttf'))
		pdfmetrics.registerFont(TTFont('Arimo-Italic', 'Arimo-Italic.ttf'))
		pdfmetrics.registerFont(TTFont('Arimo-Regular', 'Arimo-Regular.ttf'))

		for i in self.lines_cts:
			self.cabezera(c,wReal,hReal)
			hllg = self.env['hr.liquidaciones.lines.grat'].search([('employee_id','=',i.employee_id.id),('liquidacion_id','=',i.liquidacion_id.id)])[0]
			hllv = self.env['hr.liquidaciones.lines.vac'].search([('employee_id','=',i.employee_id.id),('liquidacion_id','=',i.liquidacion_id.id)])[0]

			total_sum = 0

			c.drawString( 30 , pos_inicial, u"DATOS GENERALES")
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
			c.setFont("Arimo-Regular", font_size)
			c.drawString( 30 , pos_inicial, u"Código")
			c.drawString( 320 , pos_inicial, u"Cargo de Puesto")
			c.setFont("Arimo-Bold", font_size)
			c.drawString( 140 , pos_inicial, u": {0}".format(i.employee_id.codigo_trabajador) if i.employee_id.codigo_trabajador else ':')
			c.drawString( 420 , pos_inicial, u": {0}".format(i.employee_id.job_id.name.capitalize()) if i.employee_id.job_id else ':')
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
			c.setFont("Arimo-Regular", font_size)
			c.drawString( 30 , pos_inicial, u"Apellidos y Nombres")
			c.drawString( 320 , pos_inicial, u"Fondo de Pensión")
			c.setFont("Arimo-Bold", font_size)
			c.drawString( 140 , pos_inicial, u": {0} {1} {2}".format(i.employee_id.last_name_father.upper(), i.employee_id.last_name_mother.upper(), i.employee_id.first_name_complete.upper()))
			c.drawString( 420 , pos_inicial, u": {0}".format(i.employee_id.afiliacion.name) if i.employee_id.afiliacion else ':')
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
			c.setFont("Arimo-Regular", font_size)
			c.drawString( 30 , pos_inicial, u"DNI")
			c.drawString( 320 , pos_inicial, u"CUSPP")
			c.setFont("Arimo-Bold", font_size)
			c.drawString( 140 , pos_inicial, u": {0}".format(i.employee_id.identification_id) if i.employee_id.identification_id else ':')
			c.drawString( 420 , pos_inicial, u": {0}".format(i.employee_id.cusspp) if i.employee_id.cusspp else ':')
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
			c.setFont("Arimo-Regular", font_size)
			c.drawString( 30 , pos_inicial, u"Motivo de Cese")
			c.drawString( 320 , pos_inicial, u"Fecha de Ingreso")
			c.setFont("Arimo-Bold", font_size)
			c.drawString( 140 , pos_inicial, u": {0}".format(i.cese_reason) if i.cese_reason else ':')
			c.drawString( 420 , pos_inicial, u": {0}".format(i.employee_id.fecha_ingreso) if i.employee_id.fecha_ingreso else ':')
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
			c.setFont("Arimo-Regular", font_size)
			c.drawString( 320 , pos_inicial, u"Fecha de Cese")
			c.setFont("Arimo-Bold", font_size)
			c.drawString( 420 , pos_inicial, u": {0}".format(i.employee_id.fecha_cese) if i.employee_id.fecha_cese else ':')

			if i.comp_date:
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*2,pagina)
				if pos_inicial < 90:
					c.showPage()
					inicio = 0
					pos_inicial = hReal-100
					pagina = 1
					textPos = 0	
					c.cabezera()			
				c.drawString( 30 , pos_inicial, u"A) Compensación por Tiempo de Servicio: Calculado de Acuerdo TUO D.I. 650 (D.S. 001-97-TR) y normas reglamentarias")
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.setFillColor(HexColor('#99ccff'), alpha=0.5)
				c.rect(30, pos_inicial-4, 260, endl, stroke=0, fill=1)
				c.setFillColor(black)
				c.drawString( 30 , pos_inicial, u"Periodos que se liquidan: {0} al {1}".format(i.comp_date, i.cese_date))
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.setFont("Arimo-Regular", font_size)
				c.drawString( 40 , pos_inicial, u"Dozavos")
				c.drawString( 140 , pos_inicial, u":")
				c.drawString( 175 , pos_inicial, u"S/.")
				c.drawRightString( 255 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.computable_remuneration )) if i.computable_remuneration else "%.2f" %0)
				c.drawString( 260 , pos_inicial, u"/")
				c.drawRightString( 280 , pos_inicial, u"12")
				c.drawString( 285 , pos_inicial, u"=")
				c.drawString( 300 , pos_inicial, u"S/.")
				c.drawRightString( 380 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (i.computable_remuneration / 12) )) if i.computable_remuneration else "%.2f" %0)
				c.drawString( 390 , pos_inicial, u"*")
				c.setFillColor(HexColor('#4da6ff'), alpha=0.5)
				c.rect(400, pos_inicial-4, 25, endl, stroke=0, fill=1)
				c.setFillColor(black)

				fmt = '%Y-%m-%d'
				f1 = datetime.datetime.strptime(i.comp_date, fmt)
				f2 = datetime.datetime.strptime(i.cese_date, fmt)
				d1 = f1
				d2 = f2 + datetime.timedelta(days=1)
				rd = rdelta.relativedelta(d2,d1)

				c.drawString( 400 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (rd.months+(rd.years*12)) )) if rd.months or rd.years else "%.2f" %0)
				c.drawString( 430 , pos_inicial, u"=")
				c.drawString( 480 , pos_inicial, u"S/.")
				tmpc =  float('{:.2f}'.format(decimal.Decimal ("%0.2f" % (i.computable_remuneration / 12* float((rd.months+(rd.years*12))) ) ))) 
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (tmpc) )) if i.computable_remuneration else "%.2f" %0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.drawString( 40 , pos_inicial, u"Treintavos")
				c.drawString( 140 , pos_inicial, u":")
				c.drawString( 175 , pos_inicial, u"S/.")
				c.drawRightString( 255 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.computable_remuneration )) if i.computable_remuneration else "%.2f" %0)
				c.drawString( 260 , pos_inicial, u"/")
				c.drawRightString( 280 , pos_inicial, u"360")
				c.drawString( 285 , pos_inicial, u"=")
				c.drawString( 300 , pos_inicial, u"S/.")
				c.drawRightString( 380 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (i.computable_remuneration / 360) )) if i.computable_remuneration else "%.2f" %0)
				c.drawString( 390 , pos_inicial, u"*")
				c.setFillColor(HexColor('#4da6ff'), alpha=0.5)
				c.rect(400, pos_inicial-4, 25, endl, stroke=0, fill=1)
				c.setFillColor(black)
				c.drawString( 400 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % rd.days )) if rd.days else "%.2f" %0)
				c.drawString( 430 , pos_inicial, u"=")
				c.drawString( 480 , pos_inicial, u"S/.")
				tmpc2 = float('{:.2f}'.format(decimal.Decimal ("%0.2f" % (i.computable_remuneration / 360* rd.days) ))) 
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (tmpc2) )) if i.computable_remuneration else "%.2f" %0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.drawString( 40 , pos_inicial, u"Inasistencias")
				c.drawString( 140 , pos_inicial, u":")
				c.drawString( 175 , pos_inicial, u"S/.")
				c.drawRightString( 255 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (i.computable_remuneration/360) )) if i.computable_remuneration else "%.2f" %0)
				c.drawString( 260 , pos_inicial, u"*")
				c.setFillColor(HexColor('#4da6ff'), alpha=0.5)
				c.rect(265, pos_inicial-4, 20, endl, stroke=0, fill=1)
				c.setFillColor(black)
				c.drawRightString( 280 , pos_inicial, str(i.absences))
				c.drawString( 285 , pos_inicial, u"=")
				#c.drawString( 300 , pos_inicial, u"S/.")
				tmpc3 = float('{:.2f}'.format(decimal.Decimal ("%0.2f" % (i.computable_remuneration/360* float(i.absences)) ))) 
				#c.drawRightString( 380 , pos_inicial, str(tmpc3) if i.for_days else "%.2f" %0)

				rend = tmpc + tmpc2 - tmpc3 - i.total_payment
				"""if i.total_payment - rend >= 0:
					c.drawString( 360 , pos_inicial, u"Redondeo ( S/. -"+"%.2f"%(abs(rend)+0.00000000000001)+" )")
				else:
					c.drawString( 360 , pos_inicial, u"Redondeo ( S/: +"+"%.2f"%(abs(rend)+0.00000000000001)+" )")"""

				c.drawString( 480 , pos_inicial, u"S/.")
				calcf = tmpc3 + rend
				c.drawRightString( 560 , pos_inicial, "%.2f"%(calcf+0.00000000000001) if i.absences != 0 else "%.2f"%0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.setFont("Arimo-Bold", font_size)
				c.drawString( 40 , pos_inicial, u"Total de CTS")
				c.setFillColor(HexColor('#cceeff'), alpha=0.5)
				c.rect(480, pos_inicial-4, 80, endl, stroke=1, fill=1)
				c.setFillColor(black)
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % i.total_payment )) if i.total_payment else "%.2f" %0)
				total_sum += i.total_payment

			if hllg.comp_date:
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*2,pagina)
				if pos_inicial < 90:
					c.showPage()
					inicio = 0
					pos_inicial = hReal-100
					pagina = 1
					textPos = 0	
					c.cabezera()
				c.setFont("Arimo-Bold", font_size)
				c.drawString( 30 , pos_inicial, u"B) Gratificaciones Truncas: De acuerdo a la ley 27735 del 28/05/2003")
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.setFillColor(HexColor('#99ccff'), alpha=0.5)
				c.rect(30, pos_inicial-4, 260, endl, stroke=0, fill=1)
				c.setFillColor(black)
				c.drawString( 30 , pos_inicial, u"Periodos que se liquidan: {0} al {1}".format(hllg.comp_date, hllg.cese_date))
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.setFont("Arimo-Regular", font_size)
				c.drawString( 40 , pos_inicial, u"Sextos")
				c.drawString( 140 , pos_inicial, u":")
				c.drawString( 175 , pos_inicial, u"S/.")
				c.drawRightString( 255 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllg.computable_remuneration )) if hllg.computable_remuneration else "%.2f" %0)
				c.drawString( 260 , pos_inicial, u"/")
				c.drawRightString( 280 , pos_inicial, u"6")
				c.drawString( 285 , pos_inicial, u"=")
				c.drawString( 300 , pos_inicial, u"S/.")
				c.drawRightString( 380 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (hllg.computable_remuneration / 6) )) if hllg.computable_remuneration else "%.2f" %0)
				c.drawString( 390 , pos_inicial, u"*")
				c.setFillColor(HexColor('#4da6ff'), alpha=0.5)
				c.rect(400, pos_inicial-4, 25, endl, stroke=0, fill=1)
				c.setFillColor(black)
				c.drawString( 400 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % hllg.computable_months )) if hllg.computable_months else "%.2f" %0)
				c.drawString( 430 , pos_inicial, u"=")
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllg.for_months )) if hllg.for_months else "%.2f" %0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.drawString( 40 , pos_inicial, u"Treintavos")
				c.drawString( 140 , pos_inicial, u":")
				c.drawString( 175 , pos_inicial, u"S/.")
				c.drawRightString( 255 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllg.computable_remuneration )) if hllg.computable_remuneration else "%.2f" %0)
				c.drawString( 260 , pos_inicial, u"/")
				c.drawRightString( 280 , pos_inicial, u"180")
				c.drawString( 285 , pos_inicial, u"=")
				c.drawString( 300 , pos_inicial, u"S/.")
				c.drawRightString( 380 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (hllg.computable_remuneration / 180) )) if hllg.computable_remuneration else "%.2f" %0)
				c.drawString( 390 , pos_inicial, u"*")
				c.setFillColor(HexColor('#4da6ff'), alpha=0.5)
				c.rect(400, pos_inicial-4, 25, endl, stroke=0, fill=1)
				c.setFillColor(black)
				c.drawString( 400 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % hllg.computable_days )) if hllg.computable_days else "%.2f" %0)
				c.drawString( 430 , pos_inicial, u"=")
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllg.for_days )) if hllg.for_days else "%.2f" %0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.drawString( 40 , pos_inicial, u"Inasistencias")
				c.drawString( 140 , pos_inicial, u":")
				c.drawString( 175 , pos_inicial, u"S/.")
				c.drawRightString( 255 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (hllg.computable_remuneration / 180) )) if hllg.computable_remuneration else "%.2f" %0)
				c.drawString( 260 , pos_inicial, u"*")
				c.setFillColor(HexColor('#4da6ff'), alpha=0.5)
				c.rect(265, pos_inicial-4, 20, endl, stroke=0, fill=1)
				c.setFillColor(black)
				c.drawRightString( 280 , pos_inicial, str(hllg.absences))
				c.drawString( 285 , pos_inicial, u"=")
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllg.absences_discount )) if hllg.absences_discount else "%.2f" %0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.setFont("Arimo-Bold", font_size)
				c.drawString( 40 , pos_inicial, u"Total de Gratificaciones")
				c.setFillColor(HexColor('#cceeff'), alpha=0.5)
				c.rect(480, pos_inicial-4, 80, endl, stroke=1, fill=1)
				c.setFillColor(black)
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllg.total_months )) if hllg.total_months else "%.2f" %0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.drawString( 40 , pos_inicial, u"Bono Extraordinario Temporal Gratif.")
				c.setFillColor(HexColor('#cceeff'), alpha=0.5)
				c.rect(480, pos_inicial-4, 80, endl, stroke=1, fill=1)
				c.setFillColor(black)
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllg.bonus )) if hllg.bonus else "%.2f" %0)
				total_sum += hllg.total_net

			if hllv.comp_date:
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*2,pagina)
				if pos_inicial < 90:
					c.showPage()
					inicio = 0
					pos_inicial = hReal-100
					pagina = 1
					textPos = 0	
					c.cabezera()
				c.setFont("Arimo-Bold", font_size)
				c.drawString( 30 , pos_inicial, u"C) Vacaciones Truncas:")
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.setFillColor(HexColor('#99ccff'), alpha=0.5)
				c.rect(30, pos_inicial-4, 260, endl, stroke=0, fill=1)
				c.setFillColor(black)
				c.drawString( 30 , pos_inicial, u"Periodos que se liquidan: {0} al {1}".format(hllv.comp_date, hllv.cese_date))
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.setFont("Arimo-Regular", font_size)
				c.drawString( 40 , pos_inicial, u"Dozavos")
				c.drawString( 140 , pos_inicial, u":")
				c.drawString( 175 , pos_inicial, u"S/.")
				c.drawRightString( 255 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllv.computable_remuneration )) if hllv.computable_remuneration else "%.2f" %0)
				c.drawString( 260 , pos_inicial, u"/")
				c.drawRightString( 280 , pos_inicial, u"12")
				c.drawString( 285 , pos_inicial, u"=")
				c.drawString( 300 , pos_inicial, u"S/.")
				c.drawRightString( 380 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (hllv.computable_remuneration / 12) )) if hllv.computable_remuneration else "%.2f" %0)
				c.drawString( 390 , pos_inicial, u"*")
				c.setFillColor(HexColor('#4da6ff'), alpha=0.5)
				c.rect(400, pos_inicial-4, 25, endl, stroke=0, fill=1)
				c.setFillColor(black)

				fmt = '%Y-%m-%d'
				f1 = datetime.datetime.strptime(hllv.comp_date, fmt)
				f2 = datetime.datetime.strptime(hllv.cese_date, fmt)
				d1 = f1
				d2 = f2 + datetime.timedelta(days=1)
				rd = rdelta.relativedelta(d2,d1)

				c.drawString( 400 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (rd.months+(rd.years*12)) )) if rd.months or rd.years else "%.2f" %0)
				c.drawString( 430 , pos_inicial, u"=")
				c.drawString( 480 , pos_inicial, u"S/.")
				tmpc = float('{:.2f}'.format(decimal.Decimal (hllv.computable_remuneration / 12* float((rd.months+(rd.years*12))) ) )) 
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (tmpc) )) if hllv.for_months else "%.2f" %0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.drawString( 40 , pos_inicial, u"Treintavos")
				c.drawString( 140 , pos_inicial, u":")
				c.drawString( 175 , pos_inicial, u"S/.")
				c.drawRightString( 255 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllv.computable_remuneration )) if hllv.computable_remuneration else "%.2f" %0)
				c.drawString( 260 , pos_inicial, u"/")
				c.drawRightString( 280 , pos_inicial, u"360")
				c.drawString( 285 , pos_inicial, u"=")
				c.drawString( 300 , pos_inicial, u"S/.")
				c.drawRightString( 380 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (hllv.computable_remuneration / 360) )) if hllv.computable_remuneration else "%.2f" %0)
				c.drawString( 390 , pos_inicial, u"*")
				c.setFillColor(HexColor('#4da6ff'), alpha=0.5)
				c.rect(400, pos_inicial-4, 25, endl, stroke=0, fill=1)
				c.setFillColor(black)
				c.drawString( 400 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % rd.days )) if rd.days else "%.2f" %0)
				c.drawString( 430 , pos_inicial, u"=")
				c.drawString( 480 , pos_inicial, u"S/.")
				tmpc2 = float('{:.2f}'.format(decimal.Decimal (hllv.computable_remuneration / 360* rd.days) )) 
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (tmpc2) )) if hllv.for_days else "%.2f" %0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.drawString( 40 , pos_inicial, u"Inasistencias")
				c.drawString( 140 , pos_inicial, u":")
				c.drawString( 175 , pos_inicial, u"S/.")
				c.drawRightString( 255 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ( "%0.2f" % (hllv.computable_remuneration / 360) )) if hllv.computable_remuneration else "%.2f" %0)
				c.drawString( 260 , pos_inicial, u"*")
				c.setFillColor(HexColor('#4da6ff'), alpha=0.5)
				c.rect(265, pos_inicial-4, 20, endl, stroke=0, fill=1)
				c.setFillColor(black)
				c.drawRightString( 280 , pos_inicial, str(hllv.absences))
				c.drawString( 285 , pos_inicial, u"=")
				#c.drawString( 300 , pos_inicial, u"S/.")
				tmpc3 = float('{:.2f}'.format(decimal.Decimal ("%0.2f" % (hllv.computable_remuneration / 360) ))) * float(hllv.absences)
				#c.drawRightString( 380 , pos_inicial, str(tmpc3) if hllv.for_days else "%.2f" %0)

				#print tmpc, tmpc2, tmpc3, hllv.total_holidays_sinva
				rend = tmpc + tmpc2 - tmpc3 - hllv.total_holidays_sinva
				"""if hllv.total_holidays_sinva - rend >= 0:
					c.drawString( 360 , pos_inicial, u"Redondeo ( S/. -"+"%.2f"%(abs(rend)+0.00000000000001)+" )")
				else:
					c.drawString( 360 , pos_inicial, u"Redondeo ( S/: +"+"%.2f"%(abs(rend)+0.00000000000001)+" )")"""

				c.drawString( 480 , pos_inicial, u"S/.")
				calcf = tmpc3 + rend
				c.drawRightString( 560 , pos_inicial, "%.2f"%(calcf+0.00000000000001) if hllv.absences != 0 else "%.2f"%0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.setFont("Arimo-Bold", font_size)
				c.drawString( 40 , pos_inicial, u"Total de Vacaciones Truncas")
				c.setFillColor(HexColor('#cceeff'), alpha=0.5)
				c.rect(480, pos_inicial-4, 80, endl, stroke=1, fill=1)
				c.setFillColor(black)
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllv.total_holidays_sinva )) if hllv.total_holidays_sinva else "%.2f" %0)
				total_sum += hllv.total_holidays_sinva

			if hllv.comp_date:
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*2,pagina)
				if pos_inicial < 90:
					c.showPage()
					inicio = 0
					pos_inicial = hReal-100
					pagina = 1
					textPos = 0	
					c.cabezera()
				c.setFont("Arimo-Bold", font_size)
				c.drawString( 30 , pos_inicial, u"D) Vacaciones Pendientes No Gozadas:")
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.setFillColor(HexColor('#cceeff'), alpha=0.5)
				c.rect(480, pos_inicial-4, 80, endl, stroke=1, fill=1)
				c.setFillColor(black)
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllv.fall_due_holidays )) if hllv.fall_due_holidays else "%.2f" %0)
				total_sum += hllv.fall_due_holidays

			if hllv.comp_date:
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*2,pagina)
				if pos_inicial < 90:
					c.showPage()
					inicio = 0
					pos_inicial = hReal-100
					pagina = 1
					textPos = 0	
					c.cabezera()
				c.setFont("Arimo-Bold", font_size)
				c.drawString( 30 , pos_inicial, u"E) Indemnización de Vacaciones No Gozadas:")
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.setFillColor(HexColor('#cceeff'), alpha=0.5)
				c.rect(480, pos_inicial-4, 80, endl, stroke=1, fill=1)
				c.setFillColor(black)
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllv.compensation )) if hllv.compensation else "%.2f" %0)
				total_sum += hllv.compensation

			total_res = hllv.ONP + hllv.AFP_JUB + hllv.AFP_SI + hllv.AFP_COM
			if hllv.comp_date:
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*2,pagina)
				if pos_inicial < 90:
					c.showPage()
					inicio = 0
					pos_inicial = hReal-100
					pagina = 1
					textPos = 0	
					c.cabezera()
				c.setFont("Arimo-Bold", font_size)
				c.drawString( 30 , pos_inicial, u"INGRESOS")
				c.line(30, pos_inicial-2, 72 , pos_inicial-2)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)

				back_endl = 1
				for in_con in hllv.ingresos_lines:
					c.setFont("Arimo-Regular", font_size)
					c.drawString( 30 , pos_inicial, self.particionar_text(in_con.concepto_id.name,18))
					c.drawString( 140 , pos_inicial, u":")
					c.drawString( 175 , pos_inicial, u"S/.")
					c.drawRightString( 255 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % in_con.monto )))
					pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
					total_sum += in_con.monto
					back_endl += 1

				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*-back_endl,pagina)
				c.setFont("Arimo-Bold", font_size)
				c.drawString( 320 , pos_inicial, u"DESCUENTOS")
				c.setFont("Arimo-Regular", font_size)
				c.line(320, pos_inicial-2, 372 , pos_inicial-2)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)

				c.drawString( 320 , pos_inicial, u"AFP Aporte Obligatorio")
				on = self.env['hr.membership.line'].search([('membership','=',hllv.employee_id.afiliacion.id),('periodo','=',hllv.liquidacion_id.period_id.id)])
				if len(on)>0:
					tmpon = on[0]
					if tmpon.membership.name != 'ONP':
						c.drawString( 420 , pos_inicial, u": {0} %".format(tmpon.tasa_pensiones) if tmpon.tasa_pensiones else ':')
					else:
						c.drawString( 420 , pos_inicial, u": {0} %".format("%.2f" % 0))
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllv.AFP_JUB )) if hllv.AFP_JUB else "%.2f" %0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.drawString( 320 , pos_inicial, u"AFP Seguro de Invalidez")
				if len(on)>0:
					tmpon = on[0]
					if tmpon.membership.name != 'ONP':
						c.drawString( 420 , pos_inicial, u": {0} %".format(tmpon.prima) if tmpon.prima else ':')
					else:
						c.drawString( 420 , pos_inicial, u": {0} %".format("%.2f" % 0))
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllv.AFP_SI )) if hllv.AFP_SI else "%.2f" %0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.drawString( 320 , pos_inicial, u"AFP Comisión")
				if len(on)>0:
					tmpon = on[0]
					if tmpon.membership.name != 'ONP':
						if hllv.employee_id.c_mixta:
							c.drawString( 420 , pos_inicial, u": {0} %".format(tmpon.c_mixta) if tmpon.c_mixta else ':')
						else:
							c.drawString( 420 , pos_inicial, u": {0} %".format(tmpon.c_variable) if tmpon.c_variable else ':')
					else:
						c.drawString( 420 , pos_inicial, u": {0} %".format("%.2f" % 0))
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllv.AFP_COM )) if hllv.AFP_COM else "%.2f" %0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				c.drawString( 320 , pos_inicial, u"ONP")
				if len(on)>0:
					tmpon = on[0]
					if tmpon.membership.name == 'ONP':
						c.drawString( 420 , pos_inicial, u": {0} %".format(tmpon.tasa_pensiones) if tmpon.tasa_pensiones else ':')
					else:
						c.drawString( 420 , pos_inicial, u": {0} %".format("%.2f" % 0))
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % hllv.ONP )) if hllv.ONP else "%.2f" %0)
				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
				for des_con in hllv.descuentos_lines:
					c.setFont("Arimo-Regular", font_size)
					c.drawString( 320 , pos_inicial, self.particionar_text(des_con.concepto_id.name,18))
					c.drawString( 420 , pos_inicial, u":")
					c.drawString( 480 , pos_inicial, u"S/.")
					c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % des_con.monto )))
					pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
					total_res += des_con.monto

				pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*2,pagina)
				c.setFont("Arimo-Bold", font_size)
				c.drawString( 30 , pos_inicial, u"Total de Ingresos")
				c.setFillColor(white, alpha=0.5)
				c.rect(175, pos_inicial-4, 80, endl, stroke=1, fill=0)
				c.setFillColor(black)
				c.drawString( 175 , pos_inicial, u"S/.")
				c.drawRightString( 255 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % total_sum )))
				c.drawString( 320 , pos_inicial, u"Total de Descuentos")
				c.setFillColor(white, alpha=0.5)
				c.rect(480, pos_inicial-4, 80, endl, stroke=1, fill=1)
				c.setFillColor(black)
				c.drawString( 480 , pos_inicial, u"S/.")
				c.drawRightString( 560 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % total_res )))

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*2,pagina)
			c.setFillColor(HexColor('#4da6ff'), alpha=0.5)
			c.rect(30, pos_inicial-4, 225, endl, stroke=1, fill=1)
			c.setFillColor(black)				
			c.drawString( 30 , pos_inicial, u"Neto a Pagar")
			c.drawString( 175 , pos_inicial, u"S/.")
			c.drawRightString( 255 , pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (total_sum - total_res) )))

			style = getSampleStyleSheet()["Normal"]
			style.leading = 12
			style.alignment = 4

			tot = '{:,.2f}'.format(decimal.Decimal("%0.2f" % (total_sum - total_res)))
			paragraph1 = Paragraph(
				"<font size=10>" + u"Declaro haber recibido la cantidad de S/." + tot + u"<b> (" + number_to_letter(float(tot.replace(',',''))).capitalize() + u" Nuevos Soles) </b> correspondientes a mis Beneficios Sociales(CTS, Vacaciones y Gratificaciones). En consecuencia no tengo nada que reclamar a <b>CALQUIPA SAC</b>" + " </font>",
				style
			)

			data= [[ paragraph1 ]]
			t=Table(data,colWidths=(560-45), rowHeights=(40))
			t.setStyle(TableStyle([
			('TEXTFONT', (0, 0), (-1, -1), 'Arimo-Regular'),
			('FONTSIZE',(0,0),(-1,-1),10)
			]))
			t.wrapOn(c,30,pos_inicial-50)
			t.drawOn(c,30,pos_inicial-50)

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*5,pagina)
			if i.issue_date:
				fecha_report = i.issue_date.split('-')
				c.drawString( 30 , pos_inicial, u"Arequipa " + fecha_report[2] + " de " + date_to_month(int(fecha_report[1])) + " del " + str(fecha_report[0]))
			else:
				c.drawString( 30 , pos_inicial, u"Arequipa____de_________del______")

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl*4,pagina)
			c.drawString( 30 , pos_inicial, "." * 80)
			c.drawString( 320 , pos_inicial, "." * 80)
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
			c.drawCentredString( 120 , pos_inicial, "CALQUIPA SAC")
			c.drawCentredString( 410 , pos_inicial, u"{0} {1} {2}".format(i.employee_id.last_name_father, i.employee_id.last_name_mother, i.employee_id.first_name_complete))
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,endl,pagina)
			c.drawCentredString( 120 , pos_inicial, "RUC: 20455959943")
			c.drawCentredString( 410 , pos_inicial, "DNI: " + i.employee_id.identification_id if i.employee_id.identification_id else "DNI: " + "_"*10)

			pagina += 1
			c.showPage()
			inicio = 0
			pos_inicial = hReal-100
			pagina = 1
			textPos = 0
		c.save()

	@api.multi
	def particionar_text(self,c,d):
		tet = ""
		for i in range(len(c)):
			tet += c[i]
			lines = simpleSplit(tet,'Arimo-Regular',8,d)
			if len(tet)>d:
				return tet[:-1]
		return tet


	@api.multi
	def verify_linea(self,c,wReal,hReal,posactual,valor,pagina):
		if posactual <10:
			c.showPage()
			self.cabezera(c,wReal,hReal)

			c.setFont("Arimo-Bold", 8)
			#c.drawCentredString(300,25,'Pag. ' + str(pagina+1))
			return pagina+1,hReal-100
		else:
			return pagina,posactual-valor

	@api.multi
	def open_cert_wizard(self):
		view_id = self.env.ref('hr_liquidaciones_it.view_hr_certificado_trabajo_wizard_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'hr.certificado.trabajo.wizard',
			# 'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
			'context'  : {'employees': [line.employee_id.id for line in self.lines_cts]},
		}


class hr_liquidaciones_lines_cts(models.Model):
	_name = 'hr.liquidaciones.lines.cts'

	liquidacion_id = fields.Many2one('hr.liquidaciones', 'liquidacion padre')

	code                     = fields.Char('Código', compute="get_code")
	employee_id              = fields.Many2one('hr.employee', 'Empleado')
	start_date               = fields.Date('Fecha Ingreso')
	comp_date                = fields.Date('Fecha Inicio Comp.')
	cese_date                = fields.Date('Fecha Cese')
	absences                 = fields.Integer('Faltas')
	basic_remuneration       = fields.Float('Remuneración Básica')
	nocturnal_surcharge_mean = fields.Float('Promedio Sobret Noc.')
	sixth_gratification      = fields.Float('1/6 Gratificación')
	computable_remuneration  = fields.Float('Remuneración Computable', compute="get_computable_remuneration")
	computable_months        = fields.Float('Meses Comp.')
	computable_days          = fields.Float('Días Comp.')
	for_months               = fields.Float('Por los Meses', digits=(12,2), compute="get_for_months")
	for_days                 = fields.Float('Por los Días', digits=(12,2), compute="get_for_days")
	absences_discount	     = fields.Float('Descuento Faltas', digits=(12,2), compute="get_absences_discount")
	total_payment            = fields.Float('Total a Pagar', digits=(12,2), compute="get_total_payment")
	issue_date               = fields.Date('Fecha Depósito')
	cese_reason              = fields.Text('Motivo de Cese')

	@api.one
	def get_code(self):
		self.code = self.employee_id.codigo_trabajador

	@api.one
	def get_computable_remuneration(self):
		self.computable_remuneration = self.basic_remuneration + self.nocturnal_surcharge_mean + self.sixth_gratification 

	@api.one
	def get_for_months(self):
		self.for_months = float(decimal.Decimal(str( (self.computable_remuneration / 12) * self.computable_months )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))

	@api.one
	def get_for_days(self):
		self.for_days = float(decimal.Decimal(str( ((self.computable_remuneration / 360) * self.computable_days) )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))
		"""if self.computable_months == 0:
			self.for_days = 0
		else:
			#self.for_days = float(decimal.Decimal(str( (((self.computable_remuneration / 12) / 30) * self.computable_days) )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))
			self.for_days = float(decimal.Decimal(str( ((self.computable_remuneration / 360) * self.computable_days) )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))"""

	@api.one
	def get_absences_discount(self):
		self.absences_discount = self.computable_remuneration/360.00*self.absences

	@api.one
	def get_total_payment(self):
		self.total_payment = float(decimal.Decimal(str( self.for_months + self.for_days - self.absences_discount)).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))

	@api.one
	def write(self, vals):
		t = super(hr_liquidaciones_lines_cts, self).write(vals)
		self.refresh()
		cont_noct = self.nocturnal_surcharge_mean
		falt = self.absences
		fd = self.issue_date
		obj = self.env['hr.liquidaciones.lines.grat'].search([('employee_id','=',self.employee_id.id),
																  ('liquidacion_id','=',self.liquidacion_id.id)])[0]
		if "flag_dont_write" in vals:
			pass
		else:
			obj.write({"nocturnal_surcharge_mean": cont_noct,
					   "absences": falt,
					   "flag_dont_write": True,
					   "flag_absences": True,
					   "issue_date": fd,
					   "cese_reason": self.cese_reason,})
			if 'absences' in vals:
				obj.refresh()
				if obj.comp_date:
					fmt = '%Y-%m-%d'
					f1 = datetime.datetime.strptime(obj.comp_date, fmt)
					f2 = datetime.datetime.strptime(obj.cese_date, fmt)
					d1 = f1
					# d2 = f2 - datetime.timedelta(days=obj.absences) + datetime.timedelta(days=1)
					d2 = f2 + datetime.timedelta(days=1)
					tmp_d1 = False
					if d1.day > 1:
						tmp_d1 = d1 + rdelta.relativedelta(days=monthrange(d1.year,d1.month)[1]-d1.day+1)
						d1 = tmp_d1
					rd = rdelta.relativedelta(d2,d1)
					obj.computable_months = rd.months + (rd.years*12)
					obj.computable_days = 0#rd.days

		obj2 = self.env['hr.liquidaciones.lines.vac'].search([('employee_id','=',self.employee_id.id),
																  ('liquidacion_id','=',self.liquidacion_id.id)])[0]
		if "flag_dont_write" in vals:
			pass
		else:
			obj2.write({"nocturnal_surcharge_mean": cont_noct, 
						"absences": falt,
						"flag_dont_write": True,
						"flag_absences": True,
						"issue_date": fd,
						"cese_reason": self.cese_reason,})
			if 'absences' in vals:
				obj2.refresh()
				if obj2.comp_date:
					fmt = '%Y-%m-%d'
					f1 = datetime.datetime.strptime(obj2.comp_date, fmt)
					f2 = datetime.datetime.strptime(obj2.cese_date, fmt)
					d1 = f1
					# d2 = f2 - datetime.timedelta(days=obj2.absences) + datetime.timedelta(days=1)
					d2 = f2 + datetime.timedelta(days=1)
					rd = rdelta.relativedelta(d2,d1)
					obj2.computable_months = rd.months + (rd.years*12)
					obj2.computable_days = rd.days

		if "flag_dont_write" in vals:
			pass
		else:
			self.write({"nocturnal_surcharge_mean": cont_noct, 
						"absences": falt,
						"flag_dont_write": True,
						"flag_absences": True,
						"issue_date": fd,
						"cese_reason": self.cese_reason,})
			if 'absences' in vals:
				self.refresh()
				if self.comp_date:
					fmt = '%Y-%m-%d'
					f1 = datetime.datetime.strptime(self.comp_date, fmt)
					f2 = datetime.datetime.strptime(self.cese_date, fmt)
					d1 = f1
					# d2 = f2 - datetime.timedelta(days=self.absences) + datetime.timedelta(days=1)
					d2 = f2 + datetime.timedelta(days=1)
					rd = rdelta.relativedelta(d2,d1)
					self.computable_months = rd.months + (rd.years*12)
					self.computable_days = rd.days


		if 'comp_date' in vals:
			if self.comp_date:
				fmt = '%Y-%m-%d'
				f1 = datetime.datetime.strptime(self.comp_date, fmt)
				f2 = datetime.datetime.strptime(self.cese_date, fmt)
				d1 = f1
				# d2 = f2 - datetime.timedelta(days=self.absences) + datetime.timedelta(days=1)
				d2 = f2 + datetime.timedelta(days=1)
				rd = rdelta.relativedelta(d2,d1)
				self.computable_months = rd.months + (rd.years*12)
				self.computable_days = rd.days

		if 'flag_dont_write' in vals:
			print "CTS"
			import pprint
			pprint.pprint(vals)

		return t

	@api.one
	def unlink(self):
		if 'cont' in self.env.context:
			pass
		else:
			obj = self.env['hr.liquidaciones.lines.grat'].search([('employee_id','=',self.employee_id.id),
																	  ('liquidacion_id','=',self.liquidacion_id.id)])[0]
			obj2 = self.env['hr.liquidaciones.lines.vac'].search([('employee_id','=',self.employee_id.id),
																	  ('liquidacion_id','=',self.liquidacion_id.id)])[0]

			obj.with_context({'cont':True}).unlink()
			obj2.with_context({'cont':True}).unlink()
		return super(hr_liquidaciones_lines_cts, self).unlink()




class hr_liquidaciones_lines_grat(models.Model):
	_name = 'hr.liquidaciones.lines.grat'

	liquidacion_id = fields.Many2one('hr.liquidaciones', 'liquidacion padre')

	code                      = fields.Char('Código', compute="get_code")
	employee_id               = fields.Many2one('hr.employee', 'Empleado')
	start_date                = fields.Date('Fecha Ingreso')
	comp_date                 = fields.Date('Fecha Inicio Comp.')
	cese_date                 = fields.Date('Fecha Cese')
	absences                  = fields.Integer('Faltas')
	basic_remuneration        = fields.Float('Remuneración Básica')
	nocturnal_surcharge_mean  = fields.Float('Promedio Sobret Noc.')
	computable_remuneration   = fields.Float('Remuneración Computable', compute="get_computable_remuneration")
	computable_months         = fields.Float('Meses Comp.')
	computable_days           = fields.Float('Días Comp.')
	for_months                = fields.Float('Por los Meses', digits=(12,2), compute="get_for_months")
	for_days                  = fields.Float('Por los Días', digits=(12,2), compute="get_for_days")
	absences_discount         = fields.Float('Descuento Faltas', digits=(12,2), compute="get_absences_discount")
	total_months              = fields.Float('Total Meses', digits=(12,2), compute="get_total_months")
	bonus                     = fields.Float('Bonificación 9%', digits=(12,2), compute="get_bonus")
	total_gratification_bonus = fields.Float('Total Gratificaciíón y Bono', digits=(12,2), compute="get_total_gratification_bonus")
	ONP                       = fields.Float('ONP')
	AFP_JUB                   = fields.Float('AFP JUB')
	AFP_SI                    = fields.Float('AFP SI')
	AFP_COM                   = fields.Float('AFP COM')
	total_net                 = fields.Float('Neto a Pagar', digits=(12,2), compute="get_total_net")
	issue_date                = fields.Date('Fecha Depósito')
	cese_reason               = fields.Text('Motivo de Cese')

	@api.one
	def get_code(self):
		self.code = self.employee_id.codigo_trabajador

	@api.one
	def get_computable_remuneration(self):
		self.computable_remuneration = self.basic_remuneration + self.nocturnal_surcharge_mean

	@api.one
	def get_for_months(self): 
		self.for_months = float(decimal.Decimal(str( (self.computable_remuneration / 6) * self.computable_months )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))

	@api.one
	def get_for_days(self):
		if self.computable_months == 0:
			self.for_days = 0
		else:
			self.for_days = float(decimal.Decimal(str( (self.computable_remuneration / 180) )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP)) * self.computable_days

	@api.one
	def get_absences_discount(self):
		if self.computable_months == 0:
			self.absences_discount = 0
		else:
			self.absences_discount = self.computable_remuneration/180.00*self.absences

	@api.one
	def get_total_months(self):
		self.total_months = self.for_months + self.for_days - self.absences_discount

	@api.one
	def get_bonus(self):
		if self.liquidacion_id.check_bonus == True:
			self.bonus = float(decimal.Decimal(str( self.total_months * 0.09 )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))
		else:
			self.bonus = 0

	@api.one
	def get_total_gratification_bonus(self):
		if self.liquidacion_id.check_bonus == True:
			self.total_gratification_bonus = self.total_months + self.bonus
		else:
			self.total_gratification_bonus = self.total_months

	@api.one
	def get_total_net(self):
		self.total_net = float(decimal.Decimal(str( self.total_gratification_bonus )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))

	@api.one
	def write(self, vals):
		t = super(hr_liquidaciones_lines_grat, self).write(vals)
		cont_noct = self.nocturnal_surcharge_mean
		falt = self.absences
		fd = self.issue_date
		obj = self.env['hr.liquidaciones.lines.cts'].search([('employee_id','=',self.employee_id.id),
																  ('liquidacion_id','=',self.liquidacion_id.id)])[0]
		if "flag_dont_write" in vals:
			pass
		else:
			obj.write({"nocturnal_surcharge_mean": cont_noct,
					   "absences": falt,
					   "flag_dont_write": True,
					   "flag_absences": True,
					   "issue_date": fd,
					   "cese_reason": self.cese_reason,})
			if 'absences' in vals:
				obj.refresh()
				if obj.comp_date:
					fmt = '%Y-%m-%d'
					f1 = datetime.datetime.strptime(obj.comp_date, fmt)
					f2 = datetime.datetime.strptime(obj.cese_date, fmt)
					d1 = f1
					# d2 = f2 - datetime.timedelta(days=obj.absences) + datetime.timedelta(days=1)
					d2 = f2 + datetime.timedelta(days=1)
					rd = rdelta.relativedelta(d2,d1)
					obj.computable_months = rd.months + (rd.years*12)
					obj.computable_days = rd.days


		obj2 = self.env['hr.liquidaciones.lines.vac'].search([('employee_id','=',self.employee_id.id),
																  ('liquidacion_id','=',self.liquidacion_id.id)])[0]
		if "flag_dont_write" in vals:
			pass
		else:
			obj2.write({"nocturnal_surcharge_mean": cont_noct, 
						"absences": falt,
						"flag_dont_write": True,
						"flag_absences": True,
						"issue_date": fd,
						"cese_reason": self.cese_reason,})
			if 'absences' in vals:
				obj2.refresh()
				if obj2.comp_date:
					fmt = '%Y-%m-%d'
					f1 = datetime.datetime.strptime(obj2.comp_date, fmt)
					f2 = datetime.datetime.strptime(obj2.cese_date, fmt)
					d1 = f1
					# d2 = f2 - datetime.timedelta(days=obj2.absences) + datetime.timedelta(days=1)
					d2 = f2 + datetime.timedelta(days=1)
					rd = rdelta.relativedelta(d2,d1)
					obj2.computable_months = rd.months + (rd.years*12)
					obj2.computable_days = rd.days

		if "flag_dont_write" in vals:
			pass
		else:
			self.write({"nocturnal_surcharge_mean": cont_noct, 
						"absences": falt,
						"flag_dont_write": True,
						"flag_absences": True,
						"issue_date": fd,
						"cese_reason": self.cese_reason,})
			if 'absences' in vals:
				self.refresh()
				if self.comp_date:
					fmt = '%Y-%m-%d'
					f1 = datetime.datetime.strptime(self.comp_date, fmt)
					f2 = datetime.datetime.strptime(self.cese_date, fmt)
					d1 = f1
					# d2 = f2 - datetime.timedelta(days=self.absences) + datetime.timedelta(days=1)
					d2 = f2 + datetime.timedelta(days=1)
					tmp_d1 = False
					if d1.day > 1:
						tmp_d1 = d1 + rdelta.relativedelta(days=monthrange(d1.year,d1.month)[1]-d1.day+1)
						d1 = tmp_d1
					rd = rdelta.relativedelta(d2,d1)
					self.computable_months = rd.months + (rd.years*12)
					self.computable_days = 0#rd.days

		if 'comp_date' in vals:
			if self.comp_date:
				fmt = '%Y-%m-%d'
				f1 = datetime.datetime.strptime(self.comp_date, fmt)
				f2 = datetime.datetime.strptime(self.cese_date, fmt)
				d1 = f1
				# d2 = f2 - datetime.timedelta(days=self.absences) + datetime.timedelta(days=1)
				d2 = f2 + datetime.timedelta(days=1)
				tmp_d1 = False
				if d1.day > 1:
					tmp_d1 = d1 + rdelta.relativedelta(days=monthrange(d1.year,d1.month)[1]-d1.day+1)
					d1 = tmp_d1
				rd = rdelta.relativedelta(d2,d1)
				self.computable_months = rd.months + (rd.years*12)
				self.computable_days = 0#rd.days

		if 'flag_dont_write' in vals:
			print "GRAT"
			import pprint
			pprint.pprint(vals)

		return t

	@api.one
	def unlink(self):
		if 'cont' in self.env.context:
			pass
		else:
			obj = self.env['hr.liquidaciones.lines.cts'].search([('employee_id','=',self.employee_id.id),
																	  ('liquidacion_id','=',self.liquidacion_id.id)])[0]
			obj2 = self.env['hr.liquidaciones.lines.vac'].search([('employee_id','=',self.employee_id.id),
																	  ('liquidacion_id','=',self.liquidacion_id.id)])[0]

			obj.with_context({'cont':True}).unlink()
			obj2.with_context({'cont':True}).unlink()
		return super(hr_liquidaciones_lines_grat, self).unlink()


class hr_liquidaciones_lines_vac(models.Model):
	_name = 'hr.liquidaciones.lines.vac'

	liquidacion_id = fields.Many2one('hr.liquidaciones', 'liquidacion padre')

	code                     = fields.Char('Código', compute="get_code")
	employee_id              = fields.Many2one('hr.employee', 'Empleado')
	start_date               = fields.Date('Fecha Ingreso')
	comp_date                = fields.Date('Fecha Inicio Comp.')
	cese_date                = fields.Date('Fecha Cese')
	absences                 = fields.Integer('Faltas')
	fall_due_holidays        = fields.Float('Vacaciones no Gozadas')
	basic_remuneration       = fields.Float('Remuneración Básica')
	nocturnal_surcharge_mean = fields.Float('Promedio Sobret Noc.')
	computable_remuneration  = fields.Float('Remuneración Computable', compute="get_computable_remuneration")
	computable_months        = fields.Float('Meses Comp.')
	computable_days          = fields.Float('Días Comp.')
	for_months               = fields.Float('Por los Meses', digits=(12,2), compute="get_for_months")
	for_days                 = fields.Float('Por los Días', digits=(12,2), compute="get_for_days")
	absences_discount        = fields.Float('Descuento Faltas', digits=(12,2), compute="get_absences_discount")
	total_holidays           = fields.Float('Total Vacaciones', digits=(12,2), compute="get_total_holidays")
	total_holidays_sinva     = fields.Float('Vacaciones', digits=(12,2), compute="get_total_holidays_sinva")
	ONP                      = fields.Float('ONP', digits=(12,2), compute="get_onp")
	AFP_JUB                  = fields.Float('AFP JUB', digits=(12,2), compute="get_afp_jub")
	AFP_SI                   = fields.Float('AFP SI', digits=(12,2), compute="get_afp_si")
	AFP_COM                  = fields.Float('AFP COM', digits=(12,2), compute="get_afp_com")
	compensation             = fields.Float('Indemnización')
	total_net                = fields.Float('Neto a Pagar', digits=(12,2), compute="get_total_net")
	issue_date               = fields.Date('Fecha Emisión')
	cese_reason              = fields.Text('Motivo de Cese')

	ingresos_lines			 = fields.One2many('hr.liquidaciones.ingresos.vac','line_vac_id','Ingresos')
	descuentos_lines		 = fields.One2many('hr.liquidaciones.descuentos.vac','line_vac_id','Descuentos')

	@api.multi
	def open_incomes(self):
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'hr.liquidaciones.lines.vac',
			'res_id': self.id,
			'target': 'new',
		}

	@api.multi
	def set_incomes(self):
		return True

	@api.one
	def get_code(self):
		self.code = self.employee_id.codigo_trabajador

	@api.one
	def get_computable_remuneration(self):
		self.computable_remuneration = self.basic_remuneration + self.nocturnal_surcharge_mean

	@api.one
	def get_for_months(self): 
		self.for_months = float(decimal.Decimal(str( (self.computable_remuneration / 12) * self.computable_months )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))

	@api.one
	def get_for_days(self):
		self.for_days = float(decimal.Decimal(str( ((self.computable_remuneration / 360) * self.computable_days) )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))
		# if self.computable_months == 0:
		# 	self.for_days = 0
		# else:
		# 	#self.for_days = float(decimal.Decimal(str( (((self.computable_remuneration / 12) / 30) * self.computable_days) )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))
		# 	self.for_days = float(decimal.Decimal(str( ((self.computable_remuneration / 360) * self.computable_days) )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))

	@api.one
	def get_absences_discount(self):
		self.absences_discount = self.computable_remuneration/360.00*self.absences

	@api.one
	def get_total_holidays_sinva(self):
		self.total_holidays_sinva = self.for_months + self.for_days - self.absences_discount
		# self.total_holidays_sinva = self.for_months + self.for_days

	@api.one
	def get_total_holidays(self):
		self.total_holidays = self.fall_due_holidays + self.total_holidays_sinva 

	@api.one
	def get_onp(self):
		on = self.env['hr.membership.line'].search([('membership','=',self.employee_id.afiliacion.id),('periodo','=',self.liquidacion_id.period_id.id)])
		if len(on)>0:
			tmpon = on[0]
			if tmpon.membership.name == 'ONP':
				incomes = 0
				self.ONP = float(decimal.Decimal(str( (self.total_holidays+incomes) * (tmpon.tasa_pensiones/100.00) )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))
			else:
				self.ONP = 0

	@api.one
	def get_afp_jub(self):
		on = self.env['hr.membership.line'].search([('membership','=',self.employee_id.afiliacion.id),('periodo','=',self.liquidacion_id.period_id.id)])
		if len(on)>0:
			tmpon = on[0]
			if tmpon.membership.name != 'ONP':
				incomes = 0
				self.AFP_JUB = float(decimal.Decimal(str( (self.total_holidays+incomes) * (tmpon.tasa_pensiones/100.00) )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))
			else:
				self.AFP_JUB = 0

	@api.one
	def get_afp_si(self):
		on = self.env['hr.membership.line'].search([('membership','=',self.employee_id.afiliacion.id),('periodo','=',self.liquidacion_id.period_id.id)])
		if len(on)>0:
			tmpon = on[0]
			if tmpon.membership.name != 'ONP':
				incomes = 0
				self.AFP_SI = float(decimal.Decimal(str( ((self.total_holidays+incomes) if self.total_holidays+incomes < tmpon.rma else tmpon.rma ) * (tmpon.prima/100.00) )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP)) 
				#Modifcacion Pendiente para revision de AFP PRIMA  JP.
			else:
				self.AFP_SI = 0

	@api.one
	def get_afp_com(self):
		on = self.env['hr.membership.line'].search([('membership','=',self.employee_id.afiliacion.id),('periodo','=',self.liquidacion_id.period_id.id)])
		if len(on)>0:
			tmpon = on[0]
			if tmpon.membership.name != 'ONP':
				incomes = 0
				if self.employee_id.c_mixta:
					self.AFP_COM = float(decimal.Decimal(str( (self.total_holidays+incomes) * (tmpon.c_mixta/100) )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))
				else:
					self.AFP_COM = float(decimal.Decimal(str( (self.total_holidays+incomes) * (tmpon.c_variable/100) )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))
			else:
				self.AFP_COM = 0

	@api.one
	def get_total_net(self):
		va = self.total_holidays - self.ONP - self.AFP_JUB - self.AFP_SI - self.AFP_COM + self.compensation
		self.total_net = float(decimal.Decimal(str( va )).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))

	@api.one
	def write(self, vals):
		t = super(hr_liquidaciones_lines_vac, self).write(vals)
		cont_noct = self.nocturnal_surcharge_mean
		falt = self.absences
		fd = self.issue_date
		obj = self.env['hr.liquidaciones.lines.cts'].search([('employee_id','=',self.employee_id.id),
																  ('liquidacion_id','=',self.liquidacion_id.id)])[0]
		if "flag_dont_write" in vals:
			pass
		else:
			obj.write({"nocturnal_surcharge_mean": cont_noct,
					   "absences": falt,
					   "flag_dont_write": True,
					   "flag_absences": True,
					   "issue_date": fd,
					   "cese_reason": self.cese_reason,})
			if 'absences' in vals:
				obj.refresh()
				if obj.comp_date:
					fmt = '%Y-%m-%d'
					f1 = datetime.datetime.strptime(obj.comp_date, fmt)
					f2 = datetime.datetime.strptime(obj.cese_date, fmt)
					d1 = f1
					# d2 = f2 - datetime.timedelta(days=obj.absences) + datetime.timedelta(days=1)
					d2 = f2 + datetime.timedelta(days=1)
					rd = rdelta.relativedelta(d2,d1)
					obj.computable_months = rd.months + (rd.years*12)
					obj.computable_days = rd.days

		obj2 = self.env['hr.liquidaciones.lines.grat'].search([('employee_id','=',self.employee_id.id),
																  ('liquidacion_id','=',self.liquidacion_id.id)])[0]
		if "flag_dont_write" in vals:
			pass
		else:
			obj2.write({"nocturnal_surcharge_mean": cont_noct, 
						"absences": falt,
						"flag_dont_write": True,
						"flag_absences": True,
						"issue_date": fd,
						"cese_reason": self.cese_reason,})
			if 'absences' in vals:
				obj2.refresh()
				if obj2.comp_date:
					fmt = '%Y-%m-%d'
					f1 = datetime.datetime.strptime(obj2.comp_date, fmt)
					f2 = datetime.datetime.strptime(obj2.cese_date, fmt)
					d1 = f1
					# d2 = f2 - datetime.timedelta(days=obj2.absences) + datetime.timedelta(days=1)
					d2 = f2 + datetime.timedelta(days=1)
					tmp_d1 = False
					if d1.day > 1:
						tmp_d1 = d1 + rdelta.relativedelta(days=monthrange(d1.year,d1.month)[1]-d1.day+1)
						d1 = tmp_d1
					rd = rdelta.relativedelta(d2,d1)
					obj2.computable_months = rd.months + (rd.years*12)
					obj2.computable_days = 0#rd.days

		if "flag_dont_write" in vals:
			pass
		else:
			self.write({"nocturnal_surcharge_mean": cont_noct, 
						"absences": falt,
						"flag_dont_write": True,
						"flag_absences": True,
						"issue_date": fd,
						"cese_reason": self.cese_reason,})
			if 'absences' in vals:
				self.refresh()
				if self.comp_date:
					fmt = '%Y-%m-%d'
					f1 = datetime.datetime.strptime(self.comp_date, fmt)
					f2 = datetime.datetime.strptime(self.cese_date, fmt)
					d1 = f1
					# d2 = f2 - datetime.timedelta(days=self.absences) + datetime.timedelta(days=1)
					d2 = f2 + datetime.timedelta(days=1)
					rd = rdelta.relativedelta(d2,d1)
					self.computable_months = rd.months + (rd.years*12)
					self.computable_days = rd.days

		if 'comp_date' in vals:
			if self.comp_date:
				fmt = '%Y-%m-%d'
				f1 = datetime.datetime.strptime(self.comp_date, fmt)
				f2 = datetime.datetime.strptime(self.cese_date, fmt)
				d1 = f1
				# d2 = f2 - datetime.timedelta(days=self.absences) + datetime.timedelta(days=1)
				d2 = f2 + datetime.timedelta(days=1)
				rd = rdelta.relativedelta(d2,d1)
				self.computable_months = rd.months + (rd.years*12)
				self.computable_days = rd.days

		if 'flag_dont_write' in vals:
			print "VAC"
			import pprint
			pprint.pprint(vals)

		return t

	@api.one
	def unlink(self):
		if 'cont' in self.env.context:
			pass
		else:
			obj = self.env['hr.liquidaciones.lines.cts'].search([('employee_id','=',self.employee_id.id),
																	  ('liquidacion_id','=',self.liquidacion_id.id)])[0]
			obj2 = self.env['hr.liquidaciones.lines.grat'].search([('employee_id','=',self.employee_id.id),
																	  ('liquidacion_id','=',self.liquidacion_id.id)])[0]

			obj.with_context({'cont':True}).unlink()
			obj2.with_context({'cont':True}).unlink()
		return super(hr_liquidaciones_lines_vac, self).unlink()


class hr_liquidaciones_ingresos_vac(models.Model):
	_name = 'hr.liquidaciones.ingresos.vac'

	line_vac_id = fields.Many2one('hr.liquidaciones.lines.vac', 'linea')

	concepto_id = fields.Many2one('hr.lista.conceptos', 'Concepto', required=True)
	monto		= fields.Float('Monto')

class hr_liquidaciones_descuentos_vac(models.Model):
	_name = 'hr.liquidaciones.descuentos.vac'

	line_vac_id = fields.Many2one('hr.liquidaciones.lines.vac', 'linea')

	concepto_id = fields.Many2one('hr.lista.conceptos', 'Concepto', required=True)
	monto		= fields.Float('Monto')



class hr_liquidaciones_view(models.Model):
	_name = 'hr.liquidaciones.view'
	_auto = False

	padre = fields.Many2one('hr.liquidaciones','Padre')
	cel = fields.Selection([('1','CTS'),('2','Gratificacion'),('3','Vacacion')],'Tipo')
	id_linea = fields.Integer('Linea')

	cts_id = fields.Many2one('hr.liquidaciones.lines.cts','Linea')
	grat_id = fields.Many2one('hr.liquidaciones.lines.grat','Linea')
	vac_id = fields.Many2one('hr.liquidaciones.lines.vac','Linea')

	code = fields.Char('Código', compute="get_code")
	start_date = fields.Date('Fecha Ingreso',compute='get_start_date')
	comp_date = fields.Date('Fecha Inicio Comp.',compute='get_comp_date')
	cese_date = fields.Date('Fecha Cese',compute='get_cese_date')
	absences = fields.Integer('Faltas',compute='get_absences')
	fall_due_holidays = fields.Float('Vacaciones Adeudadas', compute="get_fall_due_holidays")
	basic_remuneration = fields.Float('Remuneración Básica',compute='get_basic_remuneration')
	nocturnal_surcharge_mean = fields.Float('Promedio Sobret. Noc.',compute='get_nocturnal_surcharge_mean')
	sixth_gratification = fields.Float('1/6 Gratificación',compute='get_sixth_gratification')
	computable_remuneration = fields.Float('Remuneración Computable',compute='get_computable_remuneration')
	computable_months = fields.Integer('Meses Comp',compute='get_computable_months')
	computable_days = fields.Integer('Días Comp',compute='get_computable_days')
	for_months = fields.Float('Por los Meses',compute='get_for_months')
	for_days = fields.Float('Por los Días',compute='get_for_days')
	total_months = fields.Float('Total Meses', compute="get_total_months")
	bonus = fields.Float('Bonificación 9%', compute="get_bonus")
	total_gratification_bonus = fields.Float('Total Gratificación y Bono', compute="get_total_gratification_bonus")
	total_holidays = fields.Float('Total Vacaciones', compute="get_total_holidays")
	ONP = fields.Float('ONP',compute='get_onp')
	AFP_JUB = fields.Float('AFP JUB',compute='get_afp_jub')
	AFP_SI = fields.Float('AFP SI',compute='get_afp_si')
	AFP_COM = fields.Float('AFP COM',compute='get_afp_com')
	total_payment = fields.Float('Total a Pagar',compute='get_total_payment')

	trabajador = fields.Many2one('hr.employee','Trabajador')
	_order = 'cel'

	@api.one
	def get_code(self):
		if self.cel == '1':
			self.code = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].code
		elif self.cel == '2':
			self.code = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].code
		elif self.cel == '3':
			self.code = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].code

	@api.one
	def get_start_date(self):
		if self.cel == '1':
			self.start_date = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].start_date
		elif self.cel == '2':
			self.start_date = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].start_date
		elif self.cel == '3':
			self.start_date = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].start_date

	@api.one
	def get_comp_date(self):
		if self.cel == '1':
			self.comp_date = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].comp_date
		elif self.cel == '2':
			self.comp_date = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].comp_date
		elif self.cel == '3':
			self.comp_date = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].comp_date

	@api.one
	def get_cese_date(self):
		if self.cel == '1':
			self.cese_date = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].cese_date
		elif self.cel == '2':
			self.cese_date = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].cese_date
		elif self.cel == '3':
			self.cese_date = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].cese_date

	@api.one
	def get_absences(self):
		if self.cel == '1':
			self.absences = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].absences
		elif self.cel == '2':
			self.absences = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].absences
		elif self.cel == '3':
			self.absences = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].absences

	@api.one
	def get_fall_due_holidays(self):
		if self.cel == '3':
			self.fall_due_holidays = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].fall_due_holidays

	@api.one
	def get_basic_remuneration(self):
		if self.cel == '1':
			self.basic_remuneration = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].basic_remuneration
		elif self.cel == '2':
			self.basic_remuneration = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].basic_remuneration
		elif self.cel == '3':
			self.basic_remuneration = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].basic_remuneration

	@api.one
	def get_nocturnal_surcharge_mean(self):
		if self.cel == '1':
			self.nocturnal_surcharge_mean = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].nocturnal_surcharge_mean
		elif self.cel == '2':
			self.nocturnal_surcharge_mean = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].nocturnal_surcharge_mean
		elif self.cel == '3':
			self.nocturnal_surcharge_mean = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].nocturnal_surcharge_mean

	@api.one
	def get_sixth_gratification(self):
		if self.cel == '1':
			self.sixth_gratification = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].sixth_gratification
		else:
			self.sixth_gratification = False

	@api.one
	def get_computable_remuneration(self):
		if self.cel == '1':
			self.computable_remuneration = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].computable_remuneration
		elif self.cel == '2':
			self.computable_remuneration = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].computable_remuneration
		elif self.cel == '3':
			self.computable_remuneration = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].computable_remuneration

	@api.one
	def get_computable_months(self):
		if self.cel == '1':
			self.computable_months = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].computable_months
		elif self.cel == '2':
			self.computable_months = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].computable_months
		elif self.cel == '3':
			self.computable_months = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].computable_months

	@api.one
	def get_computable_days(self):
		if self.cel == '1':
			self.computable_days = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].computable_days
		elif self.cel == '2':
			self.computable_days = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].computable_days
		elif self.cel == '3':
			self.computable_days = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].computable_days

	@api.one
	def get_for_months(self):
		if self.cel == '1':
			self.for_months = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].for_months
		elif self.cel == '2':
			self.for_months = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].for_months
		elif self.cel == '3':
			self.for_months = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].for_months

	@api.one
	def get_for_days(self):
		if self.cel == '1':
			self.for_days = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].for_days
		elif self.cel == '2':
			self.for_days = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].for_days
		elif self.cel == '3':
			self.for_days = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].for_days

	@api.one
	def get_total_months(self):
		if self.cel == '2':
			self.total_months = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].total_months
		else:
			self.total_months = False

	@api.one
	def get_bonus(self):
		if self.cel == '2':
			self.bonus = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].bonus
		else:
			self.bonus = False
	
	@api.one
	def get_total_gratification_bonus(self):
		if self.cel == '2':
			self.total_gratification_bonus = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].total_gratification_bonus
		else:
			self.total_gratification_bonus = False

	@api.one
	def get_total_holidays(self):
		if self.cel == '3':
			self.total_holidays = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].total_holidays
		else:
			self.total_holidays = False

	@api.one
	def get_onp(self):
		if self.cel == '2':
			self.ONP = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].ONP
		elif self.cel =='3':
			self.ONP = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].ONP
		else:
			self.ONP = False

	@api.one
	def get_afp_jub(self):
		if self.cel == '2':
			self.AFP_JUB = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].AFP_JUB
		elif self.cel =='3':
			self.AFP_JUB = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].AFP_JUB
		else:
			self.AFP_JUB = False

	@api.one
	def get_afp_si(self):
		if self.cel == '2':
			self.AFP_SI = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].AFP_SI
		elif self.cel =='3':
			self.AFP_SI = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].AFP_SI
		else:
			self.AFP_SI = False


	@api.one
	def get_afp_com(self):
		if self.cel == '2':
			self.AFP_COM = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].AFP_COM
		elif self.cel =='3':
			self.AFP_COM = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].AFP_COM
		else:
			self.AFP_COM = False

	@api.one
	def get_total_payment(self):
		if self.cel == '1':
			self.total_payment = self.env['hr.liquidaciones.lines.cts'].search([('id','=',self.id_linea)])[0].total_payment
		elif self.cel == '2':
			self.total_payment = self.env['hr.liquidaciones.lines.grat'].search([('id','=',self.id_linea)])[0].total_net
		elif self.cel == '3':
			self.total_payment = self.env['hr.liquidaciones.lines.vac'].search([('id','=',self.id_linea)])[0].total_net

	def init(self,cr):
		cr.execute("""
			CREATE OR REPLACE view hr_liquidaciones_view as (
				SELECT row_number() OVER () AS id,* 
				FROM (

					select id as id_linea,'1' as cel,liquidacion_id as padre, employee_id as trabajador  from hr_liquidaciones_lines_cts where liquidacion_id is not null
					union all
					select id as id_linea, '2' as cel, liquidacion_id as padre, employee_id as trabajador from hr_liquidaciones_lines_grat where liquidacion_id is not null
					union all
					select id as id_linea,'3' as cel, liquidacion_id as padre, employee_id as trabajador from hr_liquidaciones_lines_vac where liquidacion_id is not null

				)T)

			""")