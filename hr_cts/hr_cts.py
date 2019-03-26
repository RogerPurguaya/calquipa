# -*- coding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs
import pprint
import io
from xlsxwriter.workbook import Workbook
import sys
from datetime import datetime
from datetime import timedelta
import os
from dateutil.relativedelta import *
import decimal
import calendar

from openerp import models, fields, api
from reportlab.lib.enums import TA_JUSTIFY,TA_CENTER,TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import magenta, red , black , blue, gray, Color, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, PageBreak, Spacer
from reportlab.lib.units import  cm,mm
from reportlab.lib.utils import simpleSplit
from cgi import escape
from reportlab import platypus

class hr_employee(models.Model):
	_inherit = 'hr.employee'

	currency = fields.Many2one('res.currency', 'Moneda')


class hr_cts(models.Model):
	_name = 'hr.cts'
	_rec_name = 'year'

	year = fields.Many2one('account.fiscalyear', u"Año Fiscal", required=1)
	period = fields.Selection([("05", "Depósito Mayo"),("11","Depósito Noviembre")],"Mes", required=1)
	period_id = fields.Many2one('account.period','Periodo',required=True)
	reward_id = fields.Many2one('hr.reward', u"Gratificación", required=1)
	change = fields.Float("Tipo de Cambio", digits=(2,3), required=1)
	cts_lines1 = fields.One2many('hr.cts.line', 'cts')
	cts_lines2 = fields.One2many('hr.cts.line', 'cts')
	state = fields.Selection([('open','Abierto'),('payed','Pagado')],string = 'Estado')

	_defaults = {
	'state':'open',
	}

	@api.one
	def get_cts(self):
		if self.change <= 0.00:
			raise osv.except_osv("Alert!", "El tipo de cambio no es correcto")
		periods = []
		in_date = ''
		end_date = ''
		ref_date = ''
		employees = self.env['hr.employee'].search([])
		tareos = self.env['hr.tareo'].search([])
		cts_line = self.env['hr.cts.line']
		count = 1
		periodoscomputables = []
		if self.period == '05':
			periods = ['11', '12', '01', '02', '03', '04']
			periodoscomputables.append('11/'+str(int(self.year.code)-1))
			periodoscomputables.append('12/'+str(int(self.year.code)-1))
			periodoscomputables.append('01/'+str(int(self.year.code)))
			periodoscomputables.append('02/'+str(int(self.year.code)))
			periodoscomputables.append('03/'+str(int(self.year.code)))
			periodoscomputables.append('04/'+str(int(self.year.code)))
			prev_periods = [
			'05/'+str(int(self.year.code)-1),
			'06/'+str(int(self.year.code)-1),
			'07/'+str(int(self.year.code)-1), 
			'08/'+str(int(self.year.code)-1), 
			'09/'+str(int(self.year.code)-1), 
			'10/'+str(int(self.year.code)-1)]
			prev_years = [str(int(self.year.code)-1)]
			years = [self.year.code, str(int(self.year.code)-1)]
			ref_date = datetime.strptime(self.year.code+'-05-01', '%Y-%m-%d')
		else:
			periods = ['05', '06', '07', '08', '09', '10']
			years = [self.year.code]
			periodoscomputables.append('05/'+str(int(self.year.code)))
			periodoscomputables.append('06/'+str(int(self.year.code)))
			periodoscomputables.append('07/'+str(int(self.year.code)))
			periodoscomputables.append('08/'+str(int(self.year.code)))
			periodoscomputables.append('09/'+str(int(self.year.code)))
			periodoscomputables.append('10/'+str(int(self.year.code)))
			prev_periods = [
			'11/'+str(int(self.year.code)-1), 
			'12/'+str(int(self.year.code)-1), 
			'01/'+str(int(self.year.code)), 
			'02/'+str(int(self.year.code)), 
			'03/'+str(int(self.year.code)), 
			'04/'+str(int(self.year.code))
			]
			prev_years = [self.year.code]
			ref_date = datetime.strptime(self.year.code+'-11-01', '%Y-%m-%d')
		for line in self.env['hr.cts.line'].search([('cts','=',self.id)]):
			line.unlink()
		print 'años', years
		print 'meses', prev_periods

		for employee in employees:
			he_night = {}
			absences = {}
			bonuses = {}
			comision = {}
			in_date = datetime.strptime(str(employee.fecha_ingreso), '%Y-%m-%d')
			if employee.fecha_cese:
				end_date = datetime.strptime(str(employee.fecha_ingreso), '%Y-%m-%d')
			###################################
			# PARA NO COSIDERAR LOS QUE TIENEN
			# FECHA DE INGRESO MAYOR QUE 
			# MAYO Y NOVIEMBRE
			###################################
			elif datetime.strptime(str(employee.fecha_ingreso), '%Y-%m-%d') < ref_date:
				end_date = False
			else:
				end_date = ref_date
			#######################
			# FIN DE CONSIDERACION
			#######################
			for per in periodoscomputables:
				he_night[per]=0
				bonuses[per]=0
				comision[per]=0

			
			absence_subsi_tot = 0
			tareos_sub = []
			if (not end_date) or end_date > ref_date:
				for tareo in tareos:
					absence = 0
					absence_lsg = 0
					absence_subsi = 0
					absence_imperf = 0
					periodo = tareo.periodo.code.split("/")
					if tareo.periodo.code in periodoscomputables:
						tmp_fecha = datetime.strptime("-".join([periodo[1],periodo[0],"01"]),"%Y-%m-%d")
						# if in_date <= tmp_fecha:
						htl = self.env['hr.tareo.line'].search([('tareo_id','=',tareo.id),('employee_id','=',employee.id)])
						hcl = self.env['hr.concepto.line'].search([('tareo_line_id','=',htl.id),('concepto_id.code','in',['007','008','009'])])
						res = 0
						for concept in hcl:
							res += concept.monto
						if res > 0.00:
							he_night[tareo.periodo.code] = res
						# absence = self.env['hr.tareo.line'].search([('tareo_id','=',tareo.id),('employee_id','=',employee.id)]).dias_suspension_perfecta
						tareoline = htl
						absence = tareoline.dias_suspension_perfecta
						# no se ha contemplao la licencia sin goce en esta instancia
						# absence_lsg = tareoline.licencia_sin_goce
						absence_subsi = tareoline.num_days_subs
						absence_imperf =  tareoline.dias_suspension_imperfecta

						if absence or absence_lsg:
							absences[tareo.periodo.code] = absence+absence_lsg
						
						if absence_imperf:
							if tareo.periodo.code in absences.keys():
								absences[tareo.periodo.code] = absences[periodo[0]]+absence_imperf
							else:
								absences[tareo.periodo.code] = absence_imperf

						if absence_subsi:
							if tareoline.dias_trabajador == absence_subsi:
								absence_subsi_tot = absence_subsi_tot+30
							else:	
								absence_subsi_tot = absence_subsi_tot+absence_subsi
							tareos_sub.append(tareoline.id)


						# if absence:
						# 	absences[periodo[0]] = absence
						hclb = self.env['hr.concepto.line'].search([('tareo_line_id','=',htl.id),('concepto_id.code','=','010')])
						if hclb.monto > 0.00:
							bonuses[tareo.periodo.code] = hclb.monto
						hcl2 = self.env['hr.concepto.line'].search([('tareo_line_id','=',htl.id),('concepto_id.code','=','011')])
						if hcl2.monto > 0.00:
							comision[tareo.periodo.code] = hcl2.monto
					# vamos a obtener los subsidios que corresponden a la cts anterior
					# para ello nos apoyamos en el campo cts_is_payed de las lineas
					# del tareo que nos indican si ya se pagaron esos elementos
					if self.period != '05':
						
						if tareo.periodo.code in prev_periods:
							absence_subsi=0
							htl = self.env['hr.tareo.line'].search([('tareo_id','=',tareo.id),('dni','=',employee.identification_id)])
							tareoline= self.env['hr.tareo.line'].search([('tareo_id','=',tareo.id),('dni','=',employee.identification_id),('cts_is_payed','=',False)])
							# tareoline= self.env['hr.tareo.line'].search([('tareo_id','=',tareo.id),('dni','=',employee.identification_id)])
							absence_subsi = tareoline.num_days_subs
							absence_subsi_tot = absence_subsi_tot+absence_subsi
							tareos_sub.append(tareoline.id)
					
				st_nocturna = 0
				bonuses_total = 0
				comision_total = 0

				cons_he=False
				cont_nocons_he=0
				contador = 0
				# esto es para las horas extras
				
				for periodo in periodoscomputables:
					# print periodo,he_night[periodo]
					if he_night[periodo] >0:
						cont_nocons_he=cont_nocons_he+1
						contador = contador+1
					else:
						contador = 0
					if contador > 2:
						cons_he=True
						break
				cons_bo=False
				cont_nocons_bo=0
				contador = 0
				# esto es para bonificaciones
				for periodo in periodoscomputables:
					# print periodo,he_night[periodo]
					if bonuses[periodo] >0:
						cont_nocons_bo=cont_nocons_bo+1
						contador = contador+1
					else:
						contador = 0
					if contador > 2:
						cons_bo=True
						break

				# esto es para bonificaciones
				cons_co=False
				cont_nocons_co=0
				contador = 0
				for periodo in periodoscomputables:
					# print periodo,he_night[periodo]
					if comision[periodo] >0:
						cont_nocons_co=cont_nocons_co+1
						contador = contador+1
					else:
						contador = 0
					if contador > 2:
						cons_co=True
						break

				if cont_nocons_he>3:
				 	cons_he=True

				if cont_nocons_bo>3:
					cons_bo=True

				if cont_nocons_co>3:
					cons_co=True

				if cons_he:
					st_nocturna = sum(he_night.values())
				if cons_bo:
					bonuses_total = sum(bonuses.values())/6.00
				if cons_co:
					comision_total = sum(comision.values())/6.00
				absences_total = sum(absences.values())


				if absence_subsi_tot>60:
				 	absences_total=absences_total+(absence_subsi_tot-60)
					for linetar in self.env['hr.tareo.line'].search([('id','in',tareos_sub)]):
						# linetar.cts_for_pay=True
						linetar.cts_dep_id=self.id


				di = in_date #+ timedelta(days=absences_total)
				final_day = calendar.monthrange(di.year,di.month)
				end_month = datetime.strptime(str(di.year)+'-'+str(di.month)+'-'+str(final_day[1]), '%Y-%m-%d')
				days = relativedelta(end_month+timedelta(days=1),di).days
				diff = relativedelta(ref_date,di)
				months = diff.months
				if months >= 6 or diff.years > 0:
					months = 6
					days = 0
				reward = self.env['hr.reward.line'].search([('reward','=',self.reward_id.id),('employee_id','=',employee.id)])
				hr_param = self.env['hr.parameters'].search([])	
				a_familiar = 0
				if employee.children_number > 0:
					a_familiar = self.env['hr.parameters'].search([('num_tipo','=','10001')])[0].monto
				emp_base = employee.basica if not employee.is_practicant else employee.basica/2.00
				base_amount = emp_base + st_nocturna/6.00 + reward.total_reward/6.00 + a_familiar + bonuses_total + comision_total
				cts_soles = (months*base_amount/12.00) + (days*base_amount/360.00) - (absences_total*base_amount/360.00)
				vals = {
						'cts'				: self.id,
						'employee_id'		: employee.id,
						'order'				: count,
						'nro_doc'			: employee.identification_id,
						'code'				: employee.codigo_trabajador,
						'last_name_father'	: employee.last_name_father,
						'last_name_mother'	: employee.last_name_mother,
						'names'				: employee.first_name_complete,
						'in_date'			: employee.fecha_ingreso,
						'basic_amount'		: emp_base,
						'a_familiar'		: a_familiar,
						'reward_amount'		: reward.total_reward/6.00,
						'overtime_night1'	: he_night['01/'+str(int(self.year.code))] if '01/'+str(int(self.year.code)) in he_night.keys() else 0.0, 
						'overtime_night2'	: he_night['02/'+str(int(self.year.code))] if '02/'+str(int(self.year.code)) in he_night.keys() else 0.0,
						'overtime_night3'	: he_night['03/'+str(int(self.year.code))] if '03/'+str(int(self.year.code)) in he_night.keys() else 0.0,
						'overtime_night4'	: he_night['04/'+str(int(self.year.code))] if '04/'+str(int(self.year.code)) in he_night.keys() else 0.0,
						'overtime_night5'	: he_night['05/'+str(int(self.year.code))] if '05/'+str(int(self.year.code)) in he_night.keys() else 0.0,
						'overtime_night6'	: he_night['06/'+str(int(self.year.code))] if '06/'+str(int(self.year.code)) in he_night.keys() else 0.0,
						'overtime_night7'	: he_night['07/'+str(int(self.year.code))] if '07/'+str(int(self.year.code)) in he_night.keys() else 0.0,
						'overtime_night8'	: he_night['08/'+str(int(self.year.code))] if '08/'+str(int(self.year.code)) in he_night.keys() else 0.0,
						'overtime_night9'	: he_night['09/'+str(int(self.year.code))] if '09/'+str(int(self.year.code)) in he_night.keys() else 0.0,
						'overtime_night10'	: he_night['10/'+str(int(self.year.code))] if '10/'+str(int(self.year.code)) in he_night.keys() else 0.0,
						'overtime_night11'	: he_night['11/'+str(int(self.year.code)-1)] if '11/'+str(int(self.year.code)) in he_night.keys() else 0.0,
						'overtime_night12'	: he_night['12/'+str(int(self.year.code)-1)] if '12/'+str(int(self.year.code)) in he_night.keys() else 0.0,
						'overtime_total'	: st_nocturna,
						'overtime_6'		: st_nocturna/6.00,
						'comision'			: comision_total,
						'bonus'				: bonuses_total,
						'base_amount'		: base_amount,
						'monthly_amount'	: base_amount/12.00,
						'dayly_amount'		: base_amount/360.00,
						'absences1'			: absences['01/'+str(int(self.year.code))] if '01/'+str(int(self.year.code)) in absences.keys() else 0.0,
						'absences2'			: absences['02/'+str(int(self.year.code))] if '02/'+str(int(self.year.code)) in absences.keys() else 0.0 ,
						'absences3'			: absences['03/'+str(int(self.year.code))] if '03/'+str(int(self.year.code)) in absences.keys() else 0.0,
						'absences4'			: absences['04/'+str(int(self.year.code))] if '04/'+str(int(self.year.code)) in absences.keys() else 0.0,
						'absences5'			: absences['05/'+str(int(self.year.code))] if '05/'+str(int(self.year.code)) in absences.keys() else 0.0,
						'absences6'			: absences['06/'+str(int(self.year.code))] if '06/'+str(int(self.year.code)) in absences.keys() else 0.0,
						'absences7'			: absences['07/'+str(int(self.year.code))] if '07/'+str(int(self.year.code)) in absences.keys() else 0.0,
						'absences8'			: absences['08/'+str(int(self.year.code))] if '08/'+str(int(self.year.code)) in absences.keys() else 0.0,
						'absences9'			: absences['09/'+str(int(self.year.code))] if '09/'+str(int(self.year.code)) in absences.keys() else 0.0,
						'absences10'		: absences['10/'+str(int(self.year.code))] if '10/'+str(int(self.year.code)) in absences.keys() else 0.0,
						'absences11'		: absences['11/'+str(int(self.year.code)-1)] if '11/'+str(int(self.year.code)) in absences.keys() else 0.0,
						'absences12'		: absences['12/'+str(int(self.year.code)-1)] if '12/'+str(int(self.year.code)) in absences.keys() else 0.0,
						'absences_total'	: absences_total,
						'months'			: months,
						'days'				: days,
						'amount_x_month'	: round(months*round(base_amount/12.00,2),2),
						'amount_x_day'		: round(days*round(base_amount/360.00,2),2),
						'absences_discount' : absences_total*base_amount/360.00,
						'cts_soles'			: cts_soles,
						'change'			: self.change,
						'cts_dolars'		: cts_soles/self.change,
						'account'			: employee.cta_cts,
						'bank'				: employee.banco_cts,
					}		
				cts_line.create(vals)
				count += 1

	@api.one
	def set_payed(self):
		cadsql = "update hr_tareo_line set cts_is_payed = true where cts_dep_id = "+str(self.id)
		self.env.cr.execute(cadsql)
		self.state = 'payed'

	@api.one
	def set_open(self):
		cadsql = "update hr_tareo_line set cts_is_payed = false,cts_dep_id=null where cts_dep_id = "+str(self.id)
		self.env.cr.execute(cadsql)
		self.state = 'open'

	@api.multi
	def get_excel(self):
		#-------------------------------------------Datos---------------------------------------------------
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		output = io.BytesIO()

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion + 'CTS.xlsx')
		worksheet = workbook.add_worksheet("CTS")

		#----------------Formatos------------------
		basic = {
			'align'		: 'left',
			'valign'	: 'vcenter',
			'text_wrap'	: 1,
			'font_size'	: 9,
			'font_name'	: 'Calibri'
		}

		basic_center = basic.copy()
		basic_center['align'] = 'center'

		numeric = basic.copy()
		numeric['align'] = 'right'
		numeric['num_format'] = '0.00'

		numeric_bold_format = numeric.copy()
		numeric_bold_format['bold'] = 1

		bold = basic.copy()
		bold['bold'] = 1

		header = bold.copy()
		header['bg_color'] = '#A9D0F5'
		header['border'] = 1
		header['align'] = 'center'

		title = bold.copy()
		title['font_size'] = 12

		basic_format = workbook.add_format(basic)
		basic_center_format = workbook.add_format(basic_center)
		numeric_format = workbook.add_format(numeric)
		bold_format = workbook.add_format(bold)
		numeric_bold_format = workbook.add_format(numeric_bold_format)
		header_format = workbook.add_format(header)
		title_format = workbook.add_format(title)

		nro_columnas = 17
			
		tam_col = [0]*nro_columnas
		
		#----------------------------------------------Título--------------------------------------------------
		cabecera = "Calquipa S.A.C."
		worksheet.merge_range('A1:B1', cabecera, title_format)
		#---------------------------------------------Cabecera------------------------------------------------
		worksheet.merge_range('A2:D2', "CTS", bold_format)
		worksheet.write('A3', u"Año :", bold_format)

		worksheet.write('B3', self.period + '/' + self.year.code, bold_format)

		columnas1 = ["Orden","Nro Documento", u"Código", "Apellido\nPaterno","Apellido\nMaterno","Nombres","Fecha\nIngreso","Sueldo",u"A.\nFamiliar","1/6\nGratif."]
		meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre']
		if self.period == '05':
			columnas1.append('H.E.\n'+'Noviembre')
			columnas1.append('H.E.\n'+'Diciembre')
			columnas1.append('H.E.\n'+'Enero')
			columnas1.append('H.E.\n'+'Febrero')
			columnas1.append('H.E.\n'+'Marzo')
			columnas1.append('H.E.\n'+'Abril')
		else:
			columnas1.append('H.E.\n'+'Mayo')
			columnas1.append('H.E.\n'+'Junio')
			columnas1.append('H.E.\n'+'Julio')
			columnas1.append('H.E.\n'+'Agosto')
			columnas1.append('H.E.\n'+'Setiembre')
			columnas1.append('H.E.\n'+'Octubre')
		columnas2 = ['S.N\nTotal','1/6\nSobret.\nNoc',u'Bonificación',u'Comisión','Base','Monto\nMes',u'Monto\nDía']
		if self.period == '05':
			columnas2.append(u'Días\nInasist.\n'+'Noviembre')
			columnas2.append(u'Días\nInasist.\n'+'Diciembre')
			columnas2.append(u'Días\nInasist.\n'+'Enero')
			columnas2.append(u'Días\nInasist.\n'+'Febrero')
			columnas2.append(u'Días\nInasist.\n'+'Marzo')
			columnas2.append(u'Días\nInasist.\n'+'Abril')
		else:
			columnas2.append(u'Días\nInasist.\n'+'Mayo')
			columnas2.append(u'Días\nInasist.\n'+'Junio')
			columnas2.append(u'Días\nInasist.\n'+'Julio')
			columnas2.append(u'Días\nInasist.\n'+'Agosto')
			columnas2.append(u'Días\nInasist.\n'+'Setiembre')
			columnas2.append(u'Días\nInasist.\n'+'Octubre')
		columnas3 = ['Total\nFaltas','Meses',u'Días','Monto\nPor\nMes',u'Monto\nPor\nDía', 'CTS\nSoles','Tipo de\nCambio\nVenta',u'CTS\nDólares','Cuenta CTS','Banco']
		columnas = columnas1+columnas2+columnas3

		fil = 4
		for col in range(len(columnas)): 
			worksheet.write(fil, col, columnas[col], header_format)

		#------------------------------------------Insertando Data----------------------------------------------
		fil = 5
		lines = self.env['hr.cts.line'].search([('cts',"=",self.id)])
		totals = [0]*len(columnas)
		
		for line in lines:
			col = 0
			worksheet.write(fil, col, line.order, basic_format)
			col += 1
			worksheet.write(fil, col, line.nro_doc, basic_format)
			col += 1
			worksheet.write(fil, col, line.code, basic_format)
			col += 1
			worksheet.write(fil, col, line.last_name_father, basic_format)
			col += 1
			worksheet.write(fil, col, line.last_name_mother, basic_format)
			col += 1
			worksheet.write(fil, col, line.names, basic_format)
			col += 1
			worksheet.write(fil, col, line.in_date, basic_center_format)
			col += 1
			worksheet.write(fil, col, line.basic_amount, numeric_format)
			totals[col] += line.basic_amount
			col += 1
			worksheet.write(fil, col, line.a_familiar, numeric_format)
			totals[col] += line.a_familiar
			col += 1
			worksheet.write(fil, col, line.reward_amount, numeric_format)
			totals[col] += line.reward_amount
			col += 1
			if self.period == '05':
				worksheet.write(fil, col, line.overtime_night11, numeric_format)
				totals[col] += line.overtime_night11
				col += 1
				worksheet.write(fil, col, line.overtime_night12, numeric_format)
				totals[col] += line.overtime_night12
				col += 1
				worksheet.write(fil, col, line.overtime_night1, numeric_format)
				totals[col] += line.overtime_night1
				col += 1
				worksheet.write(fil, col, line.overtime_night2, numeric_format)
				totals[col] += line.overtime_night2
				col += 1
				worksheet.write(fil, col, line.overtime_night3, numeric_format)
				totals[col] += line.overtime_night3
				col += 1
				worksheet.write(fil, col, line.overtime_night4, numeric_format)
				totals[col] += line.overtime_night4
				col += 1
			else:
				worksheet.write(fil, col, line.overtime_night5, numeric_format)
				totals[col] += line.overtime_night5
				col += 1
				worksheet.write(fil, col, line.overtime_night6, numeric_format)
				totals[col] += line.overtime_night6
				col += 1
				worksheet.write(fil, col, line.overtime_night7, numeric_format)
				totals[col] += line.overtime_night7
				col += 1
				worksheet.write(fil, col, line.overtime_night8, numeric_format)
				totals[col] += line.overtime_night8
				col += 1
				worksheet.write(fil, col, line.overtime_night9, numeric_format)
				totals[col] += line.overtime_night9
				col += 1
				worksheet.write(fil, col, line.overtime_night10, numeric_format)
				totals[col] += line.overtime_night10
				col += 1
			worksheet.write(fil, col, line.overtime_total, numeric_format)
			totals[col] += line.overtime_total
			col += 1
			worksheet.write(fil, col, line.overtime_6, numeric_format)
			totals[col] += line.overtime_6
			col += 1
			worksheet.write(fil, col, line.bonus, numeric_format)
			totals[col] += line.bonus
			col += 1
			worksheet.write(fil, col, line.comision, numeric_format)
			totals[col] += line.comision
			col += 1
			worksheet.write(fil, col, line.base_amount, numeric_format)
			totals[col] += line.base_amount
			col += 1
			worksheet.write(fil, col, line.monthly_amount, numeric_format)
			totals[col] += line.monthly_amount
			col += 1
			worksheet.write(fil, col, line.dayly_amount, numeric_format)
			totals[col] += line.dayly_amount
			col += 1
			if self.period == '05':
				worksheet.write(fil, col, line.absences11, basic_center_format)
				totals[col] += line.absences11
				col += 1
				worksheet.write(fil, col, line.absences12, basic_center_format)
				totals[col] += line.absences12
				col += 1
				worksheet.write(fil, col, line.absences1, basic_center_format)
				totals[col] += line.absences1
				col += 1
				worksheet.write(fil, col, line.absences2, basic_center_format)
				totals[col] += line.absences2
				col += 1
				worksheet.write(fil, col, line.absences3, basic_center_format)
				totals[col] += line.absences3
				col += 1
				worksheet.write(fil, col, line.absences4, basic_center_format)
				totals[col] += line.absences4
				col += 1
			else:
				worksheet.write(fil, col, line.absences5, basic_center_format)
				totals[col] += line.absences5
				col += 1
				worksheet.write(fil, col, line.absences6, basic_center_format)
				totals[col] += line.absences6
				col += 1
				worksheet.write(fil, col, line.absences7, basic_center_format)
				totals[col] += line.absences7
				col += 1
				worksheet.write(fil, col, line.absences8, basic_center_format)
				totals[col] += line.absences8
				col += 1
				worksheet.write(fil, col, line.absences9, basic_center_format)
				totals[col] += line.absences9
				col += 1
				worksheet.write(fil, col, line.absences10, basic_center_format)
				totals[col] += line.absences10
				col += 1
			worksheet.write(fil, col, line.absences_total, basic_center_format)
			totals[col] += line.absences_total
			col += 1
			worksheet.write(fil, col, line.months, numeric_format)
			totals[col] += line.months
			col += 1
			worksheet.write(fil, col, line.days, numeric_format)
			totals[col] += line.days
			col += 1
			worksheet.write(fil, col, line.amount_x_month, numeric_format)
			totals[col] += line.amount_x_month
			col += 1
			worksheet.write(fil, col, line.amount_x_day, numeric_format)
			totals[col] += line.amount_x_day
			col += 1
			worksheet.write(fil, col, line.cts_soles, numeric_format)
			totals[col] += line.cts_soles
			col += 1
			worksheet.write(fil, col, line.change, numeric_format)
			totals[col] += line.change
			col += 1
			worksheet.write(fil, col, line.cts_dolars, numeric_format)
			totals[col] += line.cts_dolars
			col += 1
			worksheet.write(fil, col, line.account if line.account else '', basic_format)
			col += 1
			worksheet.write(fil, col, line.bank if line.bank else '', basic_format)
			col += 1
			fil += 1

		col = 0
		for total in totals:
			if col >= 7 and col <= 36:
				worksheet.write(fil, col, total, numeric_bold_format)
			col += 1

		col_size = [5, 12, 20, 9]
		
		worksheet.set_column('A:A', col_size[0])
		worksheet.set_column('B:E', col_size[1])
		worksheet.set_column('F:F', col_size[2])
		worksheet.set_column('G:AI', col_size[3])
		worksheet.set_column('AK:AL', col_size[2])
		workbook.close()

		f = open(direccion + 'CTS.xlsx', 'rb')
		
		vals = {
			'output_name': 'CTS.xlsx',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		sfs_id = self.env['export.file.save'].create(vals)

		return {
		    "type": "ir.actions.act_window",
		    "res_model": "export.file.save",
		    "views": [[False, "form"]],
		    "res_id": sfs_id.id,
		    "target": "new",
		}

	@api.multi
	def open_reportes_wizard(self):
		view_id = self.env.ref('hr_cts.view_cts_wizard_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'cts.wizard',
			# 'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
			'context'  : {'employees' : [line.employee_id.id for line in self.cts_lines2]},
		}

	@api.multi
	def open_boletas_wizard(self):
		view_id = self.env.ref('hr_cts.view_boleta_cts_wizard_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'boleta.cts.wizard',
			# 'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
			'context'  : {'employees' : [line.employee_id.id for line in self.cts_lines2]},
		}

	@api.multi
	def open_mails_wizard(self):
		view_id = self.env.ref('hr_cts.view_mail_empleado_wizard_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'mail.empleado.wizard',
			# 'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
			'context'  : {'employees' : [line.employee_id.id for line in self.cts_lines2]},
		}

	@api.multi
	def make_email(self, htl_id, digital_sgn, checks, add_data):
		if not hasattr(htl_id, '__iter__'):
			htl_id = [htl_id]

		lines = self.env['hr.cts.line'].search([('cts','=',self.id),('id','in',htl_id)])

		to_send = []
		error_msg = ""
		for cts_line in lines:
			em  = cts_line.employee_id.work_email if cts_line.employee_id.work_email else False
			if not em:
				error_msg += cts_line.employee_id.name_related + "\n"
			txt = u"""
				<h1>CTS"""+self.period_id.code+u"""</h1>
				<h2>Envío de:</h2>"""+\
				"""<ul>"""+\
				("""<li>Reporte</li>""" if checks['reporte'] else """""")+\
				("""<li>Boleta</li>""" if checks['boleta'] else """""")+\
				"""</ul>
				<p>-------------------------------------------------</p>
			"""
			
			att_ids = []
			if checks['reporte']:
				cw = self.env['cts.wizard'].create({'in_charge':add_data['in_charge'], 
												 	'date':add_data['date'], 
												  	'forma':'2', 
												  	'employee_id':cts_line.employee_id.id, 
												  	'digital_sgn':digital_sgn})
				em_pdf = cw.with_context({'active_id':self.id}).get_pdf(cts_line.id, digital_sgn)
				f   = open(em_pdf['title_pdf'],'rb')
				att_rep = {
					'name'       : u"Reporte "+cts_line.employee_id.name_related+".pdf",
					'type'       : 'binary',
					'datas'      : base64.encodestring(''.join(f.readlines())),
					'datas_fname': u"Reporte "+cts_line.employee_id.name_related+".pdf",
				}
				att_rep_id = self.pool.get('ir.attachment').create(self.env.cr,self.env.uid,att_rep,self.env.context)
				att_ids.append(att_rep_id)

			if checks['boleta']:
				em_pdf = self.get_pdf(cts_line.id, digital_sgn)
				f   = open(em_pdf['title_pdf'],'rb')
				att_bol = {
					'name'       : u"Boleta "+cts_line.employee_id.name_related+".pdf",
					'type'       : 'binary',
					'datas'      : base64.encodestring(''.join(f.readlines())),
					'datas_fname': u"Boleta "+cts_line.employee_id.name_related+".pdf",
				}
				att_bol_id = self.pool.get('ir.attachment').create(self.env.cr,self.env.uid,att_bol,self.env.context)
				att_ids.append(att_bol_id)

			values                   = {}
			values['subject']        = u"Boleta "+cts_line.employee_id.name_related
			values['email_to']       = em
			values['body_html']      = txt
			values['res_id']         = False
			values['attachment_ids'] = [(6,0,att_ids)]

			to_send.append(values)

		if len(error_msg):
			raise osv.except_osv("Alerta!", u"Todos los empleados deben tener un email asignado\n"+error_msg)

		for item in to_send:
			msg_id = self.env['mail.mail'].create(item)
			if msg_id:
				msg_id.send()

	@api.multi
	def get_pdf(self, htl_id, digital_sgn):
		if not hasattr(htl_id, '__iter__'):
			htl_id = [htl_id]

		pdfmetrics.registerFont(TTFont('ARIAL', 'Arial.ttf'))
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		width , height = A4  # 595 , 842
		wReal = width- 30
		hReal = height - 40
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		doc = SimpleDocTemplate(direccion+"Boletas_CTS.pdf", pagesize=(600,900))

		IDGS = False
		if digital_sgn:
			fim = open(direccion+'tmpcts.png','wb')
			fim.write(digital_sgn.decode('base64'))
			fim.close()
			IDGS = Image(direccion+'tmpcts.png')
			IDGS.drawHeight = 40
			IDGS.drawWidth = 120

		colorfondo = colors.lightblue
		elements=[]
		#Definiendo los estilos de la cabecera.
		estilo_c = [
					('SPAN',(0,0),(1,0)),
					('SPAN',(2,0),(3,0)),
					('ALIGN',(2,0),(3,0),'RIGHT'),
				]

		#Definiendo los estilos que tendrán las filas.
		estilo=[
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('ALIGN',(0,4),(7,8),'CENTER'),
				('FONTSIZE', (0, 0), (-1, -1), 7),
				('FONT', (0, 0), (-1,-1),'ARIAL'),
				('BOX',(0,0),(7,3),0.5,colors.black),
				('SPAN',(0,0),(7,0)),
				('SPAN',(0,1),(7,1)),
				('SPAN',(0,2),(7,2)),
				('SPAN',(0,3),(5,3)),
				('SPAN',(6,3),(7,3)),
				('BACKGROUND',(0,0),(7,3), colorfondo),
				('SPAN',(0,4),(1,4)),
				('GRID',(0,4),(7,8),0.5,colors.black),
				('SPAN',(2,4),(5,5)),
				('SPAN',(6,4),(7,5)),
				('BACKGROUND',(0,4),(7,5), colorfondo),
				('SPAN',(2,6),(5,6)),
				('SPAN',(6,6),(7,6)),
				('SPAN',(0,7),(1,7)),
				('SPAN',(2,7),(3,7)),
				('SPAN',(4,7),(5,7)),
				('SPAN',(6,7),(7,7)),
				('BACKGROUND',(0,7),(7,7), colorfondo),
				('SPAN',(0,8),(1,8)),
				('SPAN',(2,8),(3,8)),
				('SPAN',(4,8),(5,8)),
				('SPAN',(6,8),(7,8)),
				('SPAN',(1,9),(4,9)),
				('GRID',(0,9),(7,9),0.5,colors.black),
				('BACKGROUND',(0,9),(7,10), colorfondo),
				('SPAN',(1,11),(4,11)),
				('SPAN',(1,12),(4,12)),
				('ALIGN',(5,11),(5,12),'RIGHT'),
				('BACKGROUND',(0,13),(7,13), colorfondo),
				('SPAN',(0,15),(7,15)),
				('BACKGROUND',(0,15),(7,15), colorfondo),
				('SPAN',(0,17),(6,17)),
				('BACKGROUND',(0,17),(7,17), colorfondo),
				('ALIGN',(7,17),(7,17),'RIGHT'),
				('BOX',(0,10),(7,17),0.5,colors.black),
				('SPAN',(0,20),(2,20)),
				('SPAN',(0,23),(2,23)),
				('SPAN',(5,23),(7,23)),
				('LINEABOVE',(0,23),(2,23),1.1,colors.black),
				('SPAN',(0,24),(2,24)),
				('SPAN',(5,24),(7,24)),
				('LINEABOVE',(5,23),(7,23),1.1,colors.black),				
				('ALIGN',(0,20),(7,24),'CENTER'),
			]

		#------------------------------------------------------Insertando Data-----------------------------------------
		lines = self.env['hr.cts.line'].search([('cts','=',self.id),('id','in',htl_id)], order='code asc')		
		company = self.env['res.users'].browse(self.env.uid).company_id
		count = 0
		for line in lines:
			employee = self.env['hr.employee'].search([('id','=',line.employee_id.id)])
			name = line.names + ' ' + line.last_name_father + ' ' + line.last_name_mother
			#--------------------------------------------------Cabecera
			a = Image(direccion+"calquipalleft.png")  
			a.drawHeight = 50
			a.drawWidth = 95
			b = Image(direccion+"calquipalright.png")  
			b.drawHeight = 60
			b.drawWidth = 80
			cabecera = [[a,'',b,''],]
			table_c = Table(cabecera, colWidths=[120]*2, rowHeights=50, style=estilo_c)
			#----------------------------------------------------Datos
			data = [
				['RUC: '+company.partner_id.type_number,'','','','','','',''],
				['Empleador : '+company.partner_id.name,'','','','','','',''],
				[u'Dirección : '+company.partner_id.street,'','','','','','',''],
				[u'Periodo : '+self.period+'/'+self.year.code,'','','','','',u'Código de Trabajador: '+(employee.codigo_trabajador if employee.codigo_trabajador else ''),''],
				['Documento de identidad','','Nombre y Apellidos','','','',U'Situación',''],
				['Tipo',u'Número','','','','','',''],
				[(employee.type_document_id.code if employee.type_document_id.code else ''),line.nro_doc,name,'','','','ACTIVO O SUBSIDIADO',''],
				['Fecha de ingreso','','Tipo de Trabajador','','Régimen Pensionario','','CUSPP',''],
				[line.in_date,'',(employee.tipo_trabajador.name if employee.tipo_trabajador.name else ''),'',(employee.afiliacion.name if employee.afiliacion.name else ''),'',employee.cusspp if employee.cusspp else '',''],
				['Código','Conceptos','','','','Ingresos S/.','Descuentos S/.','Neto S/.'],	
				['Ingresos','','','','','','',''],
				['0904','CONMPENSACION POR TIEMPO DE SERVICIOS','','','','{:10,.2f}'.format(line.cts_soles),'',''],
				['','','','','','','',''],
				['Descuentos','','','','','','',''],
				['','','','','','','',''],
				['Aportes del Trabajador','','','','','','',''],
				['','','','','','','',''],
				['Neto a Pagar','','','','','','','{:10,.2f}'.format(line.cts_soles)],
				['','','','','','','',''],
				['','','','','','','',''],
				[IDGS if IDGS else '','','','','','','',''],
				['','','','','','','',''],
				['','','','','','','',''],
				[company.partner_id.name.upper(),'','','','',name,'',''],
				['EMPLEADOR','','','','','TRABAJADOR','',''],
			]
			t=Table(data, colWidths=[60]*8,rowHeights=12,style=estilo)
			elements.append(table_c)
			elements.append(t)
			elements.append(Spacer(0,90))
			elements.append(table_c)
			elements.append(t)
			elements.append(PageBreak())
		doc.bottomMargin = 0
		doc.topMargin = 50
		doc.build(elements)

		f = open(direccion + 'Boletas_CTS.pdf', 'rb')

		vals = {
			'output_name': 'Boletas_CTS.pdf',
			'output_file': f.read().encode("base64"),		
		}
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		sfs_id = self.env['export.file.save'].create(vals)

		return {
			"type"     : "ir.actions.act_window",
			"res_model": "export.file.save",
			"views"    : [[False, "form"]],
			"res_id"   : sfs_id.id,
			"target"   : "new",
			"title_pdf": direccion+"Boletas_CTS.pdf",
			"only_file": "Boletas_CTS.pdf",
		}



class hr_cts_line(models.Model):
	_name = 'hr.cts.line'

	cts               = fields.Many2one('hr.cts')
	order             = fields.Integer("Orden", readonly=1)
	employee_id       = fields.Many2one('hr.employee')
	nro_doc           = fields.Char("Nro Documento")
	code              = fields.Char("Código")
	last_name_father  = fields.Char("Apellido\nPaterno")
	last_name_mother  = fields.Char("Apellido\nMaterno")
	names             = fields.Char("Nombres")
	in_date           = fields.Date("Fecha\nIngreso")
	basic_amount      = fields.Float("Sueldo", digits=(10,2))
	a_familiar        = fields.Float("A. Familiar", digits=(10,2))
	reward_amount     = fields.Float("1/6\nGratif.", digits=(10,2))
	overtime_night1   = fields.Float("H.E.\nEnero", digits=(10,2))
	overtime_night2   = fields.Float("H.E.\nFebrero", digits=(10,2))
	overtime_night3   = fields.Float("H.E.\nMarzo", digits=(10,2))
	overtime_night4   = fields.Float("H.E.\nAbril", digits=(10,2))
	overtime_night5   = fields.Float("H.E.\nMayo", digits=(10,2))
	overtime_night6   = fields.Float("H.E.\nJunio", digits=(10,2))
	overtime_night7   = fields.Float("H.E.\nJulio", digits=(10,2))
	overtime_night8   = fields.Float("H.E.\nAgosto", digits=(10,2))
	overtime_night9   = fields.Float("H.E.\nSetiembre", digits=(10,2))
	overtime_night10  = fields.Float("H.E.\nOctubre", digits=(10,2))
	overtime_night11  = fields.Float("H.E.\nNoviembre", digits=(10,2))
	overtime_night12  = fields.Float("H.E.\nDiciembre", digits=(10,2))
	overtime_total    = fields.Float("H.E.\nTotal", digits=(10,2))
	overtime_6        = fields.Float("1/6\nSobret.\nNoc.", digits=(10,2))
	comision          = fields.Float(u"Comisión", digits=(10,2))
	bonus             = fields.Float("Bonificación", digits=(10,2))
	base_amount       = fields.Float("Base", digits=(10,2))
	monthly_amount    = fields.Float("Monto\nMes", digits=(10,2))
	dayly_amount      = fields.Float(u"Monto\nDía", digits=(10,2))
	absences1         = fields.Integer(u"Días\nInasist.\nEnero")
	absences2         = fields.Integer(u"Días\nInasist.\nFebrero")
	absences3         = fields.Integer(u"Días\nInasist.\nMarzo")
	absences4         = fields.Integer(u"Días\nInasist.\nAbril")
	absences5         = fields.Integer(u"Días\nInasist.\nMayo")
	absences6         = fields.Integer(u"Días\nInasist.\nJunio")
	absences7         = fields.Integer(u"Días\nInasist.\nJulio")
	absences8         = fields.Integer(u"Días\nInasist.\nAgosto")
	absences9         = fields.Integer(u"Días\nInasist.\nSetiembre")
	absences10        = fields.Integer(u"Días\nInasist.\nOctubre")
	absences11        = fields.Integer(u"Días\nInasist.\nNoviembre")
	absences12        = fields.Integer(u"Días\nInasist.\nDiciembre")
	absences_total    = fields.Integer(u"Total\nFaltas")
	months            = fields.Integer("Meses")
	days              = fields.Integer(u"Días")
	amount_x_month    = fields.Float("Monto\nPor\nMeses", digits=(10,2))
	amount_x_day      = fields.Float(u"Monto\nPor\nDías", digits=(10,2))
	absences_discount = fields.Float('Dscto. Inasistencias', digits=(10,2))
	cts_soles         = fields.Float("CTS\nSoles", digits=(10,2))
	change            = fields.Float("Tipo de\nCambio\nVenta", digits=(10,3))
	cts_dolars        = fields.Float(u"CTS\nDólares", digits=(10,2))
	account           = fields.Char("Cuenta CTS")
	bank              = fields.Char("Banco")

	conceptos_lines   = fields.One2many('hr.cts.conceptos','line_cts_id','conceptos')

	@api.multi
	def open_concepts(self):
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'hr.cts.line',
			'res_id': self.id,
			'target': 'new',
		}

	@api.multi
	def set_concepts(self):
		sum_con = 0
		for con in self.conceptos_lines:
			sum_con += con.monto
		self.base_amount       = self.basic_amount + self.overtime_6 + self.reward_amount + self.a_familiar + self.bonus + self.comision + sum_con
		self.monthly_amount    = self.base_amount/12.00
		self.dayly_amount      = self.base_amount/360.00
		self.amount_x_month    = round(self.months*round(self.base_amount/12.00,2),2)
		self.amount_x_day      = round(self.days*round(self.base_amount/360.00,2),2)
		self.absences_discount = self.absences_total*self.base_amount/360.00
		self.cts_soles         = (self.months*self.base_amount/12.00) + (self.days*self.base_amount/360.00) - (self.absences_total*self.base_amount/360.00)
		self.cts_dolars        = self.cts_soles/self.cts.change
		self.account           = self.employee_id.cta_cts
		self.bank              = self.employee_id.banco_cts

		return True

class hr_cts_conceptos(models.Model):
	_name = 'hr.cts.conceptos'

	line_cts_id = fields.Many2one('hr.cts.line', 'linea')
	
	concepto_id    = fields.Many2one('hr.lista.conceptos', 'Concepto', required=True)
	monto          = fields.Float('Monto')