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
import os
from dateutil.relativedelta import *
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

class hr_reward(models.Model):
	_name = "hr.reward"
	_rec_name = 'year'

	year         = fields.Many2one('account.fiscalyear', u"Año", required=1)
	period_id    = fields.Many2one('account.period','Periodo',required=True)
	period       = fields.Selection([('07',"Gratificación Fiestas Patrias"),('12',"Gratificación Navidad")], "Mes", required=1)
	plus_9       = fields.Boolean("Considerar Bono 9%")
	reward_lines = fields.One2many('hr.reward.line', 'reward', "Lineas")

	def name_get(self, cr, uid, ids, context=None):
		res = []
		for record in self.browse(cr, uid, ids, context=context):
			if record.period == '07':
				res.append((record.id, record.year.code+' - '+'Fiestas Patrias'))
			else:
				res.append((record.id, record.year.code+' - '+'Navidad'))
		return res

	@api.multi
	def open_wizard(self):
		return {
            'name'		: ('Agregar/Reemplazar Empleado'),
            'view_type'	: 'form',
            'view_mode'	: 'form',
            'res_model'	: 'reward.employee.wizard',
            'view_id'	: False,
            'type'		: 'ir.actions.act_window',
            'target'	: 'new',
        }

	@api.one
	def get_rewards(self):
		employees = self.env['hr.employee'].search([])
		tareos    = self.env['hr.tareo'].search([])
		reward_line = self.env['hr.reward.line']
		for line in self.env['hr.reward.line'].search([('reward','=',self.id)]):
			line.unlink()
		if self.period == '07':
			final_date = datetime.strptime(self.year.code+'-07-01', '%Y-%m-%d')
			for employee in employees:
				if not employee.fecha_ingreso:
					raise osv.except_osv('Alerta!',"No existe fecha de ingreso para el empleado "+employee.name)
				in_date = datetime.strptime(str(employee.fecha_ingreso), '%Y-%m-%d')
				#Verifica que el empleado no haya sido despedido antes de la fecha de gratificación
				if  (not employee.fecha_cese) or (datetime.strptime(str(employee.fecha_cese), '%Y-%m-%d').year == int(self.year.code) and datetime.strptime(str(employee.fecha_cese), '%Y-%m-%d').month > 6):
					total_days = (final_date - in_date).days
					days = 0
					if total_days > 180:
						months = 6
					else:
						months = total_days / 30.00
						months = int(months)
					if months >= 1:
						hr_param = self.env['hr.parameters'].search([])	
						a_familiar = 0
						if employee.children_number > 0:
							a_familiar = self.env['hr.parameters'].search([('num_tipo','=','10001')])[0].monto
						he_night = []
						ex_plus  = [] 
						comision  = []
						absences = 0
						for tareo in tareos:
							periodo = tareo.periodo.code.split("/")
							if periodo[1] == self.year.code and periodo[0] in ['01', '02', '03', '04', '05', '06']:
								tmp_fecha = datetime.strptime("-".join([periodo[1],periodo[0],"01"]),"%Y-%m-%d")
								if in_date <= tmp_fecha:
									#Cálculo de faltas
									htl = self.env['hr.tareo.line'].search([('tareo_id','=',tareo.id),('employee_id','=',employee.id)])
									absences += htl.dias_suspension_perfecta
									#Cálculo bonificación
									hcl = self.env['hr.concepto.line'].search([('tareo_line_id','=',htl.id),('concepto_id.code','=','010')])
									if hcl.monto > 0.00:
										ex_plus.append(hcl.monto)
									#Cálculo de sobre tasa nocturna
									hcl_st = self.env['hr.concepto.line'].search([('tareo_line_id','=',htl.id),('concepto_id.code','in',['007','008','009'])])
									res = 0
									for concept in hcl_st:
										res += concept.monto
									if res > 0.00:
										he_night.append(res)
									#calculo comision
									hcl_com = self.env['hr.concepto.line'].search([('tareo_line_id','=',htl.id),('concepto_id.code','=','011')])
									if hcl_com.monto > 0.00:
										comision.append(hcl_com.monto)
						st_nocturna = 0
						tot_ex_plus = sum(ex_plus)
						tot_comision = 0
						if len(he_night) >= 3:
							st_nocturna = sum(he_night)/6.00
						else:
							st_nocturna = 0
						if len(ex_plus) >= 3:
							tot_ex_plus = sum(ex_plus)/6.00
						else:
							tot_ex_plus = 0
						if len(comision) >= 3:
							tot_comision = sum(comision)/6.00
						else:
							tot_comision = 0

						emp_base = employee.basica if not employee.is_practicant else employee.basica/2.00
						complete_amount = emp_base + a_familiar + st_nocturna + tot_ex_plus + tot_comision
						
						vals = {
							'reward'				: self.id,
							'employee_id'			: employee.id,
							'identification_number'	: employee.identification_id,
							'code'					: employee.codigo_trabajador,
							'last_name_father'		: employee.last_name_father,
							'last_name_mother'		: employee.last_name_mother,
							'names'					: employee.first_name_complete,
							'in_date'				: employee.fecha_ingreso,
							'months'				: months,
							'days'					: days,
							'absences'				: absences,
							'basic'					: emp_base,
							'ex_plus'				: tot_ex_plus,
							'comision'				: tot_comision,
							'a_familiar'			: a_familiar,
							'he_night'				: st_nocturna,
							'complete_amount'		: complete_amount,
							'monthly_amount'		: complete_amount/6.00,
							'dayly_amount'			: complete_amount/180.00,
							'months_reward'			: months*round(complete_amount/6.00,2),
							'days_reward'			: days*round(complete_amount/180.00,2),
							'absences_amount'		: absences*round(complete_amount/180.00,2),
						}	
						vals['total_reward'] = vals['months_reward'] + vals['days_reward'] - vals['absences_amount']
						vals['plus_9']       = 0
						if self.plus_9:
							hp = self.env['hr.parameters'].search([('num_tipo','=',4)])
							if employee.use_eps:
								hp2 = self.env['hr.parameters'].search([('num_tipo','=',5)])
								vals['plus_9'] = vals['total_reward']*(hp.monto-hp2.monto)/100.00
							else:
								vals['plus_9'] = vals['total_reward']*hp.monto/100.00
						vals['total'] = vals['total_reward'] + vals['plus_9']
						reward_line.create(vals)
		else:
			final_date = datetime.strptime(str(int(self.year.code)+1)+'-01-01', '%Y-%m-%d')
			for employee in employees:
				if not employee.fecha_ingreso:
					raise osv.except_osv('Alerta!',"No existe fecha de ingreso para el empleado "+employee.name)
				in_date = datetime.strptime(str(employee.fecha_ingreso), '%Y-%m-%d')
				#Verifica que el empleado no haya sido despedido antes de la fecha de gratificación
				if  (not employee.fecha_cese) or datetime.strptime(str(employee.fecha_cese), '%Y-%m-%d').year > int(self.year.code):
					total_days = (final_date - in_date).days
					days = 0
					if total_days > 180:
						months = 6
					else:
						months = total_days / 30.00
						months = int(months)
					if months >= 1:
						hr_param = self.env['hr.parameters'].search([])	
						a_familiar = 0
						if employee.children_number > 0:
							a_familiar = self.env['hr.parameters'].search([('num_tipo','=','10001')])[0].monto
						he_night = []
						ex_plus  = []
						comision = []
						absences = 0
						for tareo in tareos:
							periodo = self.env['account.period'].search([('id','=',tareo.periodo.id)]).code.split("/")
							if periodo[1] == self.year.code and periodo[0] in ['07', '08', '09', '10', '11', '12']:
								tmp_fecha = datetime.strptime("-".join([periodo[1],periodo[0],"01"]),"%Y-%m-%d")
								if in_date <= tmp_fecha:
									#Cálculo de faltas
									htl = self.env['hr.tareo.line'].search([('tareo_id','=',tareo.id),('employee_id','=',employee.id)])
									absences += htl.dias_suspension_perfecta
									#Cálculo bonificación
									hcl = self.env['hr.concepto.line'].search([('tareo_line_id','=',htl.id),('concepto_id.code','=','010')])
									if hcl.monto > 0.00:
										ex_plus.append(hcl.monto)
									#Cálculo de sobre tasa nocturna
									hcl_st = self.env['hr.concepto.line'].search([('tareo_line_id','=',htl.id),('concepto_id.code','in',['007','008','009'])])
									res = 0
									for concept in hcl_st:
										res += concept.monto
									if res > 0.00:
										he_night.append(res)
									#calculo comision
									hcl_com = self.env['hr.concepto.line'].search([('tareo_line_id','=',htl.id),('concepto_id.code','=','011')])
									if hcl_com.monto > 0.00:
										comision.append(hcl_com.monto)
						st_nocturna = 0
						tot_ex_plus = sum(ex_plus)
						tot_comision = 0
						if len(he_night) >= 3:
							st_nocturna = sum(he_night)/6.00
						else:
							st_nocturna = 0
						if len(ex_plus) >= 3:
							tot_ex_plus = sum(ex_plus)/6.00
						else:
							tot_ex_plus = 0
						if len(comision) >= 3:
							tot_comision = sum(comision)/6.00
						else:
							tot_comision = 0
						
						emp_base = employee.basica if not employee.is_practicant else employee.basica/2.00
						complete_amount = emp_base + a_familiar + st_nocturna + tot_ex_plus + tot_comision						
						
						vals = {
							'reward'				: self.id,
							'employee_id'			: employee.id,
							'identification_number'	: employee.identification_id,
							'code'					: employee.codigo_trabajador,
							'last_name_father'		: employee.last_name_father,
							'last_name_mother'		: employee.last_name_mother,
							'names'					: employee.first_name_complete,
							'in_date'				: employee.fecha_ingreso,
							'months'				: months,
							'days'					: days,
							'absences'				: absences,
							'basic'					: emp_base,
							'ex_plus'				: tot_ex_plus,
							'comision'				: tot_comision,
							'a_familiar'			: a_familiar,
							'he_night'				: st_nocturna,
							'complete_amount'		: complete_amount,
							'monthly_amount'		: complete_amount/6.00,
							'dayly_amount'			: complete_amount/180.00,
							'months_reward'			: months*round(complete_amount/6.00,2),
							'days_reward'			: days*round(complete_amount/180.00,2),
							'absences_amount'		: absences*round(complete_amount/180.00,2),
						}		
						vals['total_reward'] = vals['months_reward'] + vals['days_reward'] - vals['absences_amount']
						vals['plus_9']       = 0
						if self.plus_9:
							hp = self.env['hr.parameters'].search([('num_tipo','=',4)])
							if employee.use_eps:
								hp2 = self.env['hr.parameters'].search([('num_tipo','=',5)])
								vals['plus_9'] = vals['total_reward']*(hp.monto-hp2.monto)/100.00
							else:
								vals['plus_9'] = vals['total_reward']*hp.monto/100.00
						vals['total'] = vals['total_reward'] + vals['plus_9']
						reward_line.create(vals)

	@api.multi
	def get_excel(self):
		#-------------------------------------------Datos---------------------------------------------------
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		output = io.BytesIO()

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion + 'Gratificaciones.xlsx')
		worksheet = workbook.add_worksheet("Gratificaciones")

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
		title['font_size'] = 15

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
		cabecera = "Calquipa"
		worksheet.merge_range('A1:B1', cabecera, title_format)
		#---------------------------------------------Cabecera------------------------------------------------
		worksheet.merge_range('A2:D2', "Gratificaciones", bold_format)
		worksheet.write('A3', u"Año :", bold_format)

		worksheet.write('B3', self.year.code, bold_format)

		columnas = ["Orden",
					"Nro Documento", 
					u"Código", 
					"Apellido\nPaterno",
					"Apellido\nMaterno",
					"Nombres",
					"Fecha\nIngreso",
					"Meses",
					u"Días",
					"Faltas",
					u"Básico",
					u"Bonificación",
					u"Comisión",
					"A.\nFamiliar",
					"Pro.\nHE.",
					"Rem.\nCom.",
					"M. por\nMes",
					u"M. por\nDía",
					"Grat. Por\nlos Meses",
					u"Grat. Por\nlos Días",
					"Total\nFaltas",
					u"Total\nGratificación",
					"Bonif.\n9%",
					"Total\nPagar"]
		fil = 4

		for col in range(len(columnas)): 
			worksheet.write(fil, col, columnas[col], header_format)

		#------------------------------------------Insertando Data----------------------------------------------
		fil = 5
		lines = self.env['hr.reward.line'].search([('reward',"=",self.id)])
		totals = [0]*14
		
		for line in lines:
			col = 0
			worksheet.write(fil, col, line.order, basic_format)
			col += 1
			worksheet.write(fil, col, line.identification_number, basic_format)
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
			worksheet.write(fil, col, line.months, basic_center_format)
			col += 1
			worksheet.write(fil, col, line.days, basic_center_format)
			col += 1
			worksheet.write(fil, col, line.absences, basic_center_format)
			col += 1
			worksheet.write(fil, col, line.basic, numeric_format)
			totals[col-10] += line.basic
			col += 1
			worksheet.write(fil, col, line.ex_plus, numeric_format)
			totals[col-10] += line.ex_plus
			col += 1
			worksheet.write(fil, col, line.comision, numeric_format)
			totals[col-10] += line.comision
			col += 1
			worksheet.write(fil, col, line.a_familiar, numeric_format)
			totals[col-10] += line.a_familiar
			col += 1
			worksheet.write(fil, col, line.he_night, numeric_format)
			totals[col-10] += line.he_night
			col += 1
			worksheet.write(fil, col, line.complete_amount, numeric_format)
			totals[col-10] += line.complete_amount
			col += 1
			worksheet.write(fil, col, line.monthly_amount, numeric_format)
			totals[col-10] += line.monthly_amount
			col += 1
			worksheet.write(fil, col, line.dayly_amount, numeric_format)
			totals[col-10] += line.dayly_amount
			col += 1
			worksheet.write(fil, col, line.months_reward, numeric_format)
			totals[col-10] += line.months_reward
			col += 1
			worksheet.write(fil, col, line.days_reward, numeric_format)
			totals[col-10] += line.days_reward
			col += 1
			worksheet.write(fil, col, line.absences_amount, numeric_format)
			totals[col-10] += line.absences_amount
			col += 1
			worksheet.write(fil, col, line.total_reward, numeric_format)
			totals[col-10] += line.total_reward
			col += 1
			worksheet.write(fil, col, line.plus_9, numeric_format)
			totals[col-10] += line.plus_9
			col += 1
			worksheet.write(fil, col, line.total, numeric_format)
			totals[col-10] += line.total
			col += 1
			fil += 1

		col = 10
		for i in range(len(totals)):
			worksheet.write(fil, col, totals[i], numeric_bold_format)
			col += 1

		col_size = [5, 12, 20]
		worksheet.set_column('A:A', col_size[0])
		worksheet.set_column('B:E', col_size[1])
		worksheet.set_column('F:F', col_size[2])
		worksheet.set_column('G:U', col_size[1])
		workbook.close()

		f = open(direccion + 'Gratificaciones.xlsx', 'rb')
		
		vals = {
			'output_name': 'Gratificaciones.xlsx',
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
	def open_email_boleta_wizard(self):
		view_id = self.env.ref('hr_reward.view_boleta_empleado_reward_wizard_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'boleta.empleado.reward.wizard',
			# 'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
			'context'  : {'employees' : [line.employee_id.id for line in self.reward_lines],
						  'comes_from': 'generar_email',},
		}

	@api.multi
	def make_email(self, htl_id, digital_sgn):
		if not hasattr(htl_id, '__iter__'):
			htl_id = [htl_id]

		lines = self.env['hr.reward.line'].search([('reward','=',self.id),('id','in',htl_id)])

		to_send = []
		error_msg = ""
		for reward_line in lines:
			em_pdf = self.get_pdf(reward_line.id, digital_sgn)
			if 'title_pdf' in em_pdf:
				f   = open(em_pdf['title_pdf'],'rb')
				em  = reward_line.employee_id.work_email if reward_line.employee_id.work_email else False
				if not em:
					error_msg += reward_line.employee_id.name_related + "\n"
				txt = u"""
					<h2>Boleta de Gratificaciones """+self.period_id.code+u"""</h2>
					<p>-------------------------------------------------</p>
				"""
				att = {
					'name'       : u"Boleta "+reward_line.employee_id.name_related+".pdf",
					'type'       : 'binary',
					'datas'      : base64.encodestring(''.join(f.readlines())),
					'datas_fname': u"Boleta "+reward_line.employee_id.name_related+".pdf",
				}
				att_id = self.pool.get('ir.attachment').create(self.env.cr,self.env.uid,att,self.env.context)

				values                   = {}
				values['subject']        = u"Boleta "+reward_line.employee_id.name_related
				values['email_to']       = em
				values['body_html']      = txt
				values['res_id']         = False
				values['attachment_ids'] = [(6,0,[att_id])]

				to_send.append(values)

		if len(error_msg):
			raise osv.except_osv("Alerta!", u"Todos los empleados deben tener un email asignado\n"+error_msg)

		for item in to_send:
			msg_id = self.env['mail.mail'].create(item)
			if msg_id:
				msg_id.send()

	@api.multi
	def open_boleta_empleado_wizard(self):
		view_id = self.env.ref('hr_reward.view_boleta_empleado_reward_wizard_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'boleta.empleado.reward.wizard',
			# 'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
			'context'  : {'employees' : [line.employee_id.id for line in self.reward_lines],
						  'comes_from': 'generar_pdf',},
		}


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
		doc = SimpleDocTemplate(direccion+"Boletas.pdf", pagesize=(600,900))

		IDGS = False
		if digital_sgn:
			fim = open(direccion+'tmprw.png','wb')
			fim.write(digital_sgn.decode('base64'))
			fim.close()
			IDGS = Image(direccion+'tmprw.png')
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
				('SPAN',(0,3),(7,3)),
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
		lines = self.env['hr.reward.line'].search([('reward','=',self.id),('id','in',htl_id)])

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
				[u'Periodo : '+self.period+'/'+self.year.code,'','','','','','',''],
				['Documento de identidad','','Nombre y Apellidos','','','',U'Situación',''],
				['Tipo',u'Número','','','','','',''],
				[employee.type_document_id.code,line.identification_number,name,'','','','ACTIVO O SUBSIDIADO',''],
				['Fecha de ingreso','',u'Título del Trabajo','','Régimen Pensionario','','CUSPP',''],
				[line.in_date,'',employee.job_id.name,'',employee.afiliacion.name,'',employee.cusspp if employee.cusspp else '',''],
				['Código','Conceptos','','','','Ingresos S/.','Descuentos S/.','Neto S/.'],	
				['Ingresos','','','','','','',''],
				['0406','GRATIFICACIONES DE FIESTAS PATRIAS Y NAVIDAD - LEY 29351','','','','{:10,.2f}'.format(line.total_reward),'',''],
				['0313','BONIFICACION EXTRAORDINARIA PROPORCIONAL - LEY 29351','','','','{:10,.2f}'.format(line.plus_9),'',''],
				['Descuentos','','','','','','',''],
				['','','','','','','',''],
				['Aportes del Trabajador','','','','','','',''],
				['','','','','','','',''],
				['Neto a Pagar','','','','','','','{:10,.2f}'.format(line.total)],
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

		f = open(direccion + 'Boletas.pdf', 'rb')

		vals = {
			'output_name': 'Boletas.pdf',
			'output_file': f.read().encode("base64"),		
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
		    "title_pdf": direccion+"Boletas.pdf",
			"only_file": "Boletas.pdf",
		}

	

class hr_reward_line(models.Model):
	_name = 'hr.reward.line'

	reward                = fields.Many2one('hr.reward', "Reward")
	employee_id           = fields.Many2one('hr.employee', "Empleado")
	order                 = fields.Integer("Orden", compute='get_order')
	identification_number = fields.Char("Nro Documento", size=9)
	code                  = fields.Char("Código", size=4)
	last_name_father      = fields.Char("Apellido Paterno")
	last_name_mother      = fields.Char("Apellido Materno")
	names                 = fields.Char("Nombres")
	in_date               = fields.Date("Fecha Ingreso")
	months                = fields.Integer("Meses") 
	days                  = fields.Integer(u"Días")
	absences              = fields.Integer("Faltas")
	basic                 = fields.Float(u"Básico", digits=(10,2))
	comision			  = fields.Float(u'Comisión', digits=(10,2))
	ex_plus               = fields.Float(u"Bonificación", digits=(10,2))
	a_familiar            = fields.Float("A. Familiar", digits=(10,2))
	he_night              = fields.Float("Pro. HE.", digits=(10,2))
	complete_amount       = fields.Float("Rem. Com.", digits=(10,2))
	monthly_amount        = fields.Float("M. por Mes", digits=(10,2))
	dayly_amount          = fields.Float(u"M. por Día", digits=(10,2))
	months_reward         = fields.Float("Grat. Por los\nMeses", digits=(10,2))
	days_reward           = fields.Float(u"Grat. Por los\nDías", digits=(10,2))
	absences_amount       = fields.Float(u"Total Faltas", digits=(10,2))
	total_reward          = fields.Float(u"Total\nGratificación", digits=(10,2))
	plus_9                = fields.Float(u"Bonif. 9%", digits=(10,2))
	total                 = fields.Float(u"Total Pagar", digits=(10,2))

	conceptos_lines       = fields.One2many('hr.reward.conceptos','line_reward_id','Ingresos')

	@api.multi
	def get_order(self):
		order = 1
		for line in self:
			line.order = order
			order      += 1

	@api.multi
	def open_concepts(self):
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'hr.reward.line',
			'res_id': self.id,
			'target': 'new',
		}

	@api.multi
	def set_concepts(self):
		sum_con = 0
		for con in self.conceptos_lines:
			sum_con += con.monto
		self.complete_amount = self.employee_id.basica + self.a_familiar + self.he_night + self.ex_plus + sum_con
		self.monthly_amount  = self.complete_amount/6.00
		self.dayly_amount    = self.complete_amount/180.00
		self.months_reward   = self.months*round(self.complete_amount/6.00,2)
		self.days_reward     = self.days*round(self.complete_amount/180.00,2)
		self.absences_amount = self.absences*round(self.complete_amount/180.00,2)
		self.total_reward    = self.months_reward + self.days_reward - self.absences_amount

		if self.reward.plus_9:
			hp = self.env['hr.parameters'].search([('num_tipo','=',4)])
			if self.employee_id.use_eps:
				hp2 = self.env['hr.parameters'].search([('num_tipo','=',5)])
				self.plus_9 = self.total_reward*(hp.monto-hp2.monto)/100.00
			else:
				self.plus_9 = self.total_reward*hp.monto/100.00

		self.total = self.total_reward + self.plus_9
		return True

class hr_reward_conceptos(models.Model):
	_name = 'hr.reward.conceptos'

	line_reward_id = fields.Many2one('hr.reward.line', 'linea')
	
	concepto_id    = fields.Many2one('hr.lista.conceptos', 'Concepto', required=True)
	monto          = fields.Float('Monto')