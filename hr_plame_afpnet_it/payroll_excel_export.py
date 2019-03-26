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

class hr_planilla1(models.Model):
	_inherit = 'hr.planilla1'

	@api.multi
	def export_plame(self):
		#-------------------------------------------Datos---------------------------------------------------
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		output = io.BytesIO()

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion + 'Planilla.xlsx')
		worksheet = workbook.add_worksheet("Reporte Planilla")

		#----------------Formatos------------------
		basic = {
			'align'		: 'left',
			'valign'	: 'vcenter',
			'text_wrap'	: 1,
			'font_size'	: 9,
			'font_name'	: 'Calibri'
		}

		numeric = basic.copy()
		numeric['align'] = 'right'
		numeric['num_format'] = '#,##0.00'

		numeric_bold_format = numeric.copy()
		numeric_bold_format['bold'] = 1
		numeric_bold_format['num_format'] = '#,##0.00'

		bold = basic.copy()
		bold['bold'] = 1

		header = bold.copy()
		header['bg_color'] = '#A9D0F5'
		header['border'] = 1
		header['align'] = 'center'

		title = bold.copy()
		title['font_size'] = 15

		basic_format = workbook.add_format(basic)
		numeric_format = workbook.add_format(numeric)
		bold_format = workbook.add_format(bold)
		numeric_bold_format = workbook.add_format(numeric_bold_format)
		header_format = workbook.add_format(header)
		title_format = workbook.add_format(title)

		nro_columnas = 8
			
		tam_col = [0]*nro_columnas
		
		#----------------------------------------------Título--------------------------------------------------
		cabecera = "Calquipa"
		worksheet.merge_range('A1:B1', cabecera, title_format)
		
		#---------------------------------------------Cabecera-----------------------------------------------
		worksheet.merge_range('A2:D2', "Planilla Mensual", bold_format)
		#worksheet.write('A3', "Periodo :", bold_format)
		fil = 5
		col = 0
		worksheet.write(fil, col, "Periodo", header_format)
		col += 1
		worksheet.write(fil, col, "Tipo Documento", header_format)
		col += 1
		worksheet.write(fil, col, "Nro. Documento", header_format)
		col += 1
		worksheet.write(fil, col, u"Código", header_format)
		col += 1
		worksheet.write(fil, col, "Nombre", header_format)
		col += 1
		worksheet.write(fil, col, u"Cargo", header_format)
		col += 1
		worksheet.write(fil, col, u"Afiliación", header_format)
		col += 1
		worksheet.write(fil, col, u"Tipo Comisión", header_format)
		col += 1

		im = self.env['ir.model'].search([('name','=',self._inherit)])
		hlc = self.env['hr.lista.conceptos'].search([]).sorted(key=lambda r: r.position)
		for concepto in hlc:
			imf = self.env['ir.model.fields'].search([('model_id','=',im[0].id),('state','=','manual'),('name','=','x_'+concepto.code)])
			if len(imf) > 0:
				worksheet.write(fil, col, imf[0].field_description, header_format)
				col += 1

		worksheet.write(fil, col, u"Total a Pagar", header_format)
		col += 1

		fil = 6
		totals = [0]*len(hlc)
		planilla = self.env['hr.planilla1'].search([])

		for line in planilla:
			col = 0
			worksheet.write(fil, col, line.periodo.code if line.periodo.code else '', basic_format)
			col += 1
			worksheet.write(fil, col, line.type_doc if line.type_doc else '', basic_format)
			col += 1
			worksheet.write(fil, col, line.dni if line.dni else '', basic_format)
			col += 1
			worksheet.write(fil, col, line.codigo_trabajador if line.codigo_trabajador else '', basic_format)
			col += 1
			worksheet.write(fil, col, line.nombre_tra if line.nombre_tra else '', basic_format)
			col += 1
			worksheet.write(fil, col, line.cargo.name if line.cargo.name else '', basic_format)
			col += 1
			worksheet.write(fil, col, line.afiliacion.name if line.afiliacion.name else '', basic_format)
			col += 1
			worksheet.write(fil, col, "SI COM. MIXTA" if line.tipo_comision else "NO COM. MIXTA", basic_format)
			col += 1
			for concepto in hlc:
				imf = self.env['ir.model.fields'].search([('model_id','=',im[0].id),('state','=','manual'),('name','=','x_'+concepto.code)])
				if len(imf) > 0:
					f = "line." + eval("imf[0].name")
					worksheet.write(fil, col, eval(f), numeric_format)
					totals[col-8] += eval(f)
					col += 1

			val_total = 0

			for tareo_line in self.env['hr.tareo.line'].search([('employee_id.codigo_trabajador','=',line.codigo_trabajador),('tareo_id.periodo','=',line.periodo.id)]):
				ningresos   = 0
				ndescuentos = 0
				npos  = 0

				cr_ingresos_ids           = [line.id for line in self.env['hr.lista.conceptos'].search([('check_boleta','=',True),('payroll_group','=','1')])]
				cr_descuentos_ids         = [line.id for line in self.env['hr.lista.conceptos'].search([('check_boleta','=',True),('payroll_group','in',['2','5'])])]
				cr_aportes_trabajador_ids = [line.id for line in self.env['hr.lista.conceptos'].search([('check_boleta','=',True),('payroll_group','=','3')])]
				cr_aportes_empleador_ids  = [line.id for line in self.env['hr.lista.conceptos'].search([('check_boleta','=',True),('payroll_group','=','4')])]
				hcl_ingresos           = self.env['hr.concepto.line'].search([('tareo_line_id','=',tareo_line.id),('concepto_id','in',cr_ingresos_ids)])	
				hcl_descuentos         = self.env['hr.concepto.line'].search([('tareo_line_id','=',tareo_line.id),('concepto_id','in',cr_descuentos_ids)])
				hcl_aportes_trabajador = self.env['hr.concepto.line'].search([('tareo_line_id','=',tareo_line.id),('concepto_id','in',cr_aportes_trabajador_ids)])
				hcl_aportes_empleador  = self.env['hr.concepto.line'].search([('tareo_line_id','=',tareo_line.id),('concepto_id','in',cr_aportes_empleador_ids)])
			
				for item in hcl_ingresos:
					if item.monto != 0:
						npos += 1
						ningresos += item.monto
						
				npos += 1
				for item in hcl_descuentos:
					if item.monto != 0:
						npos += 1
						ndescuentos += item.monto
						
				npos += 1
				for item in hcl_aportes_trabajador:
					if item.monto != 0:

						#################################################################
						## LAMENTO EL DESORDEN DE ESTA SECCION, CULPABLE --> CALQUIPA <3
						## TODA ESTA PARTE ES LA MISMA COSA QUE EL TAREO, SOLO QUE AHORA
						## SE CONSIDERAN LOS CONCEPTOS QUE TIENEN EL CHECK DE BOLETA ¬¬
						#################################################################
						if item.concepto_id.code == '028':
							if tareo_line.afiliacion.code:
								raw_base = 0
								if tareo_line.afiliacion.code == 'ONP':
									for item_con in tareo_line.conceptos_ingresos_lines: #SUMA DE INGRESOS
										if item_con.concepto_id.check_boleta:
											hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
											if len(hcrl) > 0:
												hcrl = hcrl[0]
												if hcrl.onp:
													raw_base += item_con.monto
									for item_con in tareo_line.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
										if item_con.concepto_id.check_boleta:
											hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
											if len(hcrl) > 0:
												hcrl = hcrl[0]
												if hcrl.onp:
													raw_base -= item_con.monto
								
									hml = self.env['hr.membership.line'].search([('membership','=',tareo_line.afiliacion.id),('periodo','=',tareo_line.tareo_id.periodo.id)])
									if len(hml) > 0: #PORCENTAJE DE ONP
										raw_base *= hml[0].tasa_pensiones/100.00

								if raw_base != 0:
									ndescuentos += raw_base
									npos += 1
								
						elif item.concepto_id.code == '029':
							if tareo_line.afiliacion.code:
								raw_base_j = 0
								if tareo_line.afiliacion.code != 'ONP':
									for item_con in tareo_line.conceptos_ingresos_lines: #SUMA DE INGRESOS
										if item_con.concepto_id.check_boleta:
											hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
											if len(hcrl) > 0:
												hcrl = hcrl[0]
												if hcrl.afp_fon_pen:
													raw_base_j += item_con.monto
									for item_con in tareo_line.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
										if item_con.concepto_id.check_boleta:
											hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
											if len(hcrl) > 0:
												hcrl = hcrl[0]
												if hcrl.afp_fon_pen:
													raw_base_j -= item_con.monto
								
									hml = self.env['hr.membership.line'].search([('membership','=',tareo_line.afiliacion.id),('periodo','=',tareo_line.tareo_id.periodo.id)])
									if len(hml) > 0: #PORCENTAJE DE AFP
										raw_base_j *= hml[0].tasa_pensiones/100.00
								if raw_base_j != 0:
									ndescuentos += raw_base_j
									npos += 1
								
						elif item.concepto_id.code == '030':
							if tareo_line.afiliacion.code:
								raw_base_p = 0
								if tareo_line.afiliacion.code != 'ONP':
									for item_con in tareo_line.conceptos_ingresos_lines: #SUMA DE INGRESOS
										if item_con.concepto_id.check_boleta:
											hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
											if len(hcrl) > 0:
												hcrl = hcrl[0]
												if hcrl.afp_pri_se:
													raw_base_p += item_con.monto
									for item_con in tareo_line.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
										if item_con.concepto_id.check_boleta:
											hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
											if len(hcrl) > 0:
												hcrl = hcrl[0]
												if hcrl.afp_pri_se:
													raw_base_p -= item_con.monto
								
									hml = self.env['hr.membership.line'].search([('membership','=',tareo_line.afiliacion.id),('periodo','=',tareo_line.tareo_id.periodo.id)])
									if len(hml) > 0: #PORCENTAJE DE AFP
										#PRIMA JP.
										if raw_base_p < hml[0].rma:
											pass
										else:
											raw_base_p = hml[0].rma
										raw_base_p *= hml[0].prima/100.00							

								if raw_base_p != 0:
									ndescuentos += raw_base_p
									npos += 1
								
						elif item.concepto_id.code == '031':
							if tareo_line.afiliacion.code:
								raw_base_c = 0
								if tareo_line.afiliacion.code != 'ONP':
									for item_con in tareo_line.conceptos_ingresos_lines: #SUMA DE INGRESOS
										if item_con.concepto_id.check_boleta:
											hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
											if len(hcrl) > 0:
												hcrl = hcrl[0]
												if tareo_line.employee_id.c_mixta:
													if hcrl.afp_co_mix:
														raw_base_c += item_con.monto
												else:
													if hcrl.afp_co_va:
														raw_base_c += item_con.monto
									for item_con in tareo_line.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
										if item_con.concepto_id.check_boleta:
											hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
											if len(hcrl) > 0:
												hcrl = hcrl[0]
												if tareo_line.employee_id.c_mixta:
													if hcrl.afp_co_mix:
														raw_base_c -= item_con.monto
												else:
													if hcrl.afp_co_va:
														raw_base_c -= item_con.monto
								
									hml = self.env['hr.membership.line'].search([('membership','=',tareo_line.afiliacion.id),('periodo','=',tareo_line.tareo_id.periodo.id)])
									if len(hml) > 0: #PORCENTAJE DE AFP
										if tareo_line.employee_id.c_mixta:
											raw_base_c *= hml[0].c_mixta/100.00
										else:
											raw_base_c *= hml[0].c_variable/100.00
								if raw_base_c != 0:
									ndescuentos += raw_base_c
									npos += 1
									
						else:
							ndescuentos += item.monto
							npos += 1

				val_total = ningresos-ndescuentos

			worksheet.write(fil, col, val_total,numeric_format)
			col+= 1
			fil += 1

		col = 8
		for tot in totals:
			worksheet.write(fil, col, tot, numeric_bold_format)
			col += 1

		tam_col = [10, 20, 15, 11]
		worksheet.set_column('A:A', tam_col[0])
		worksheet.set_column('B:B', tam_col[0])
		worksheet.set_column('C:C', tam_col[0])
		worksheet.set_column('D:D', tam_col[1])
		worksheet.set_column('E:E', tam_col[2])
		worksheet.set_column('F:AX', tam_col[3])
		worksheet.set_column('AY:AY', tam_col[2])
		worksheet.set_column('AZ:CC', tam_col[3])

		workbook.close()

		f = open(direccion + 'Planilla.xlsx', 'rb')
		
		vals = {
			'output_name': 'Planilla.xlsx',
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
	def export_afp_net(self):
		#-------------------------------------------Datos---------------------------------------------------
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		output = io.BytesIO()

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion + 'AFP Net.xlsx')
		worksheet = workbook.add_worksheet("Reporte AFP")

		#----------Formatos---------------------
		basic = {
			'align'		: 'left',
			'valign'	: 'vcenter',
			'text_wrap'	: 1,
			'font_size'	: 9,
			'font_name'	: 'Calibri'
		}

		numeric = basic.copy()
		numeric['num_format'] = '0.00'
		numeric['align'] = 'right'

		bold = basic.copy()
		bold['bold'] = 1

		header = bold.copy()
		header['bg_color'] = '#2ECCFA'
		header['border'] = 1
		header['align'] = 'center'

		title = bold.copy()
		title['font_size'] = 15

		basic_format = workbook.add_format(basic)
		numeric_format = workbook.add_format(numeric)
		bold_format = workbook.add_format(bold)
		header_format = workbook.add_format(header)
		title_format = workbook.add_format(title)

		nro_columnas = 17
			
		tam_col = [0]*nro_columnas
		
		#----------------------------------------------Título--------------------------------------------------
		
		#---------------------------------------------Cabecera------------------------------------------------

		#------------------------------------------Insertando Data----------------------------------------------
		fil = 0
		col = 0
		planilla = self.env['hr.planilla1'].search([])
		hlc = self.env['hr.lista.conceptos'].search([('code','=','047')])
		for line in planilla:
			col = 0
			employee = self.env['hr.employee'].search([('id','=', line.employee_id.id)])
			if employee.afiliacion.name not in ['ONP','SIN REGIMEN']:
				period = line.periodo.code.split("/")
				worksheet.write(fil, col, fil+1, basic_format)
				col += 1
				worksheet.write(fil, col, employee.cusspp if employee.cusspp else "", basic_format)
				col += 1
				worksheet.write(fil, col, employee.type_document_id.afpnet_code if employee.type_document_id.afpnet_code else '', basic_format)
				col += 1
				worksheet.write(fil, col, employee.identification_id, basic_format)
				col += 1
				worksheet.write(fil, col, employee.last_name_father, basic_format)
				col += 1
				worksheet.write(fil, col, employee.last_name_mother, basic_format)
				col += 1
				worksheet.write(fil, col, employee.first_name_complete, basic_format)
				col += 1
				worksheet.write(fil, col, 'S', basic_format)
				col += 1
				if employee.fecha_ingreso:
					date_employee = datetime.strptime(str(employee.fecha_ingreso), '%Y-%m-%d')
					if date_employee.month == int(period[0]) and date_employee.year == int(period[1]):
						worksheet.write(fil, col, 'S', basic_format)
					else:
						worksheet.write(fil, col, 'N', basic_format)
				else:
					worksheet.write(fil, col, 'N', basic_format)
				col += 1
				if employee.fecha_cese:
					date_employee = datetime.strptime(str(employee.fecha_cese), '%Y-%m-%d')
					if date_employee.month == int(period[0]) and date_employee.year == int(period[1]):
						worksheet.write(fil, col, 'S', basic_format)
					else:
						worksheet.write(fil, col, 'N', basic_format)
				else:
					worksheet.write(fil, col, 'N', basic_format)
				col += 1
				worksheet.write(fil, col, " ", numeric_format)
				col += 1
				if len(hlc) > 0:
					hlc = hlc[0]
					f = "line.x_"+hlc.code
					worksheet.write(fil, col, eval(f), numeric_format)
				else:
					worksheet.write(fil, col, 0, numeric_format)
				col += 1
				worksheet.write(fil, col, 0, basic_format)
				col += 1
				worksheet.write(fil, col, 0, basic_format)
				col += 1
				worksheet.write(fil, col, 0, basic_format)
				col += 1
				worksheet.write(fil, col, 'M', basic_format)
				col += 1
				worksheet.write(fil, col, " ", basic_format)
				col += 1
				fil += 1

		col_size = [3, 12, 18]
		worksheet.set_column('A:A', col_size[0])
		worksheet.set_column('B:B', col_size[1])
		worksheet.set_column('C:C', col_size[0])
		worksheet.set_column('D:F', col_size[1])
		worksheet.set_column('G:G', col_size[2])
		worksheet.set_column('H:K', col_size[0])
		worksheet.set_column('M:Q', col_size[0])
		workbook.close()

		f = open(direccion + 'AFP Net.xlsx', 'rb')
		
		vals = {
			'output_name': 'AFP Net.xlsx',
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


