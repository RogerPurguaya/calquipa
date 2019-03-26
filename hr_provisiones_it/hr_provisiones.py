# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp     import models, fields, api
import base64
import codecs

import datetime
import decimal

from xlsxwriter.workbook import Workbook
import pprint
import io
import sys
import os

class hr_provisiones(models.Model):
	_name = 'hr.provisiones'
	_rec_name = 'period_id'

	period_id = fields.Many2one('account.period','Periodo')

	lines_cts        = fields.One2many('hr.provisiones.lines.cts','provision_id', 'lineas CTS')
	lines_grat       = fields.One2many('hr.provisiones.lines.grat','provision_id', 'lineas Gratificación')
	lines_vac        = fields.One2many('hr.provisiones.lines.vac','provision_id', 'lineas Vacaciones')
	account_move_id  = fields.Many2one('account.move','Asiento contable')
	account_move2_id = fields.Many2one('account.move','Asiento distribuido')

	cts_account_haber_id   = fields.Many2one('account.account','CTS Haber')
	grati_account_haber_id = fields.Many2one('account.account','Gratificación Haber')
	bono_account_haber_id  = fields.Many2one('account.account','Bonificación Haber')
	vaca_account_haber_id  = fields.Many2one('account.account','Vacación Haber')

	@api.one
	def calculate(self):
		for i in self.env["hr.employee"].search([]):		
			if (i.fecha_ingreso <= self.period_id.date_stop and i.fecha_cese == False and i.fecha_ingreso is not False) or (i.fecha_cese > self.period_id.date_stop and i.fecha_cese is not False and i.fecha_ingreso is not False and i.fecha_ingreso <= self.period_id.date_stop):
				if len(self.env['hr.provisiones.lines.cts'].search([('provision_id','=',self.id), ('employee_id','=',i.id)])) > 0:
					pass
				else:
					data = {
						'doc_number': i.identification_id,
						'employee_id': i.id,
						'start_date': i.fecha_ingreso,

						'provision_id': self.id,
					}
					self.env['hr.provisiones.lines.cts'].create(data)
					self.env['hr.provisiones.lines.grat'].create(data)
					self.env['hr.provisiones.lines.vac'].create(data)

		for i in self.env['hr.provisiones.lines.cts'].search([('provision_id','=',self.id)]):
			if (i.employee_id.fecha_ingreso <= self.period_id.date_stop and i.employee_id.fecha_cese == False and i.employee_id.fecha_ingreso is not False) or (i.employee_id.fecha_cese > self.period_id.date_stop and i.employee_id.fecha_cese is not False and i.employee_id.fecha_ingreso is not False and i.employee_id.fecha_ingreso <= self.period_id.date_stop):
				obj = self.env['hr.employee'].search([('id','=',i.employee_id.id)])
				i.basic_remuneration = obj[0].basica
				i.start_date = obj[0].fecha_ingreso
				i.employee_id.children_number = obj[0].children_number
			else:
				i.unlink()
		for i in self.env['hr.provisiones.lines.grat'].search([('provision_id','=',self.id)]):
			if (i.employee_id.fecha_ingreso <= self.period_id.date_stop and i.employee_id.fecha_cese == False and i.employee_id.fecha_ingreso is not False) or (i.employee_id.fecha_cese > self.period_id.date_stop and i.employee_id.fecha_cese is not False and i.employee_id.fecha_ingreso is not False and i.employee_id.fecha_ingreso <= self.period_id.date_stop):
				obj = self.env['hr.employee'].search([('id','=',i.employee_id.id)])
				i.basic_remuneration = obj[0].basica
				i.start_date = obj[0].fecha_ingreso
				i.employee_id.children_number = obj[0].children_number
			else:
				i.unlink()
		for i in self.env['hr.provisiones.lines.vac'].search([('provision_id','=',self.id)]):
			if (i.employee_id.fecha_ingreso <= self.period_id.date_stop and i.employee_id.fecha_cese == False and i.employee_id.fecha_ingreso is not False) or (i.employee_id.fecha_cese > self.period_id.date_stop and i.employee_id.fecha_cese is not False and i.employee_id.fecha_ingreso is not False and i.employee_id.fecha_ingreso <= self.period_id.date_stop):
				obj = self.env['hr.employee'].search([('id','=',i.employee_id.id)])
				i.basic_remuneration = obj[0].basica
				i.start_date = obj[0].fecha_ingreso
				i.employee_id.children_number = obj[0].children_number
			else:
				i.unlink()

	@api.one
	def make_account_move(self):
		cts_debe   = self.env['hr.lista.conceptos'].search([('code','=','017')])[0].account_debe_id.id
		cts_haber  = self.env['hr.lista.conceptos'].search([('code','=','017')])[0].account_haber_id.id
		grat_debe  = self.env['hr.lista.conceptos'].search([('code','=','018')])[0].account_debe_id.id
		grat_haber = self.env['hr.lista.conceptos'].search([('code','=','018')])[0].account_haber_id.id
		vac_debe   = self.env['hr.lista.conceptos'].search([('code','=','004')])[0].account_debe_id.id
		vac_haber  = self.env['hr.lista.conceptos'].search([('code','=','051')])[0].account_haber_id.id
		bon_debe   = self.env['hr.lista.conceptos'].search([('code','=','020')])[0].account_debe_id.id
		bon_haber  = self.env['hr.lista.conceptos'].search([('code','=','020')])[0].account_haber_id.id

		if not (cts_debe and cts_haber and grat_debe and grat_haber and vac_debe and vac_haber and bon_debe and bon_haber):
			raise osv.except_osv("Alerta!", u"No se configuró las cuentas debe y/o haber de los conceptos con los siguientes códigos:\n-017\n-018\n-004\n-051\n-020") 

		d_dict = {
			cts_debe : 0,
			grat_debe: 0,
			vac_debe : 0,
			bon_debe : 0,
		}
		h_dict = {
			cts_haber : 0,
			grat_haber: 0,
			vac_haber : 0,
			bon_haber : 0,
		}

		for line in self.lines_cts:
			d_dict[cts_debe]  += line.provision
			h_dict[cts_haber] += line.provision

		for line in self.lines_grat:
			d_dict[grat_debe]  += line.provision
			h_dict[grat_haber] += line.provision
			d_dict[bon_debe]   += line.bonus
			h_dict[bon_haber]  += line.bonus

		for line in self.lines_vac:
			d_dict[vac_debe]  += line.provision
			h_dict[vac_haber] += line.provision

		aj = self.env['account.journal'].search([('code','=','11')])
		if len(aj) == 0:
			raise osv.except_osv("Alerta!", u"No existe el diario PLANILLA")

		if not self.account_move_id.id:
			n_vals = {
				'journal_id': aj[0].id,
				'period_id' : self.period_id.id,
				'date'      : self.period_id.date_stop,
				'name'      : 'Planilla '+self.period_id.code,
			}
			n_am = self.env['account.move'].create(n_vals)
			self.account_move_id = n_am.id
		else:
			n_vals = {
				'journal_id': aj[0].id,
				'period_id' : self.period_id.id,
				'date'      : self.period_id.date_stop,
				'name'      : 'Planilla '+self.period_id.code,
			}
			self.account_move_id.write(n_vals)

			for line in self.account_move_id.line_id:
				line.unlink()

		for k,v in d_dict.items():
			nl_vals = {
				'move_id'   : self.account_move_id.id,
				'account_id': k,
				'debit'     : float(decimal.Decimal(str( v )).quantize(decimal.Decimal('1.111111'),rounding=decimal.ROUND_HALF_UP)),
				'credit'    : 0,
				'name'      : 'Planilla '+self.period_id.code,
			}
			n_aml = self.env['account.move.line'].create(nl_vals)

		for k,v in h_dict.items():
			nl_vals = {
				'move_id'   : self.account_move_id.id,
				'account_id': k,
				'debit'     : 0,
				'credit'    : float(decimal.Decimal(str( v )).quantize(decimal.Decimal('1.111111'),rounding=decimal.ROUND_HALF_UP)),
				'name'      : 'Planilla '+self.period_id.code,
			}
			n_aml = self.env['account.move.line'].create(nl_vals)

	@api.one
	def make_account_move2(self):
		cts_debe   = self.env['hr.lista.conceptos'].search([('code','=','017')])[0]
		cts_haber  = self.env['hr.lista.conceptos'].search([('code','=','017')])[0]
		grat_debe  = self.env['hr.lista.conceptos'].search([('code','=','018')])[0]
		grat_haber = self.env['hr.lista.conceptos'].search([('code','=','018')])[0]
		vac_debe   = self.env['hr.lista.conceptos'].search([('code','=','004')])[0]
		vac_haber  = self.env['hr.lista.conceptos'].search([('code','=','051')])[0]
		bon_debe   = self.env['hr.lista.conceptos'].search([('code','=','020')])[0]
		bon_haber  = self.env['hr.lista.conceptos'].search([('code','=','020')])[0]

		if not (cts_haber.account_haber_id.id and grat_haber.account_haber_id.id and vac_haber.account_haber_id.id and bon_haber.account_haber_id.id ):
			raise osv.except_osv("Alerta!", u"No se configuró las cuentas debe y/o haber de los conceptos con los siguientes códigos:\n-017\n-018\n-004\n-051\n-020") 

		d_dis_dict = {}
		h_dis_dict = {
			cts_haber.account_haber_id.id : 0,
			grat_haber.account_haber_id.id: 0,
			bon_haber.account_haber_id.id : 0,
			vac_haber.account_haber_id.id : 0,
		}

		error_msg = ""

		for line in self.lines_cts:
			for dis in line.employee_id.dist_c.distribucion_lines:
				encontrado = False
				for cuenta in cts_debe.cuentas_line:
					if dis.analitica.id == cuenta.analytic_id.id:
						if cuenta.account_id.id not in d_dis_dict:
							d_dis_dict[cuenta.account_id.id] = line.provision * dis.porcentaje/100.00
						else:
							d_dis_dict[cuenta.account_id.id] += line.provision * dis.porcentaje/100.00
						encontrado = True
				if not encontrado:
						error_msg += (dis.analitica.name if dis.analitica.name else '') + "->" + cts_debe.name + "\n"

			h_dis_dict[cts_haber.account_haber_id.id] += line.provision

		for line in self.lines_grat:
			for dis in line.employee_id.dist_c.distribucion_lines:
				encontrado   = False
				encontrado_b = False
				for cuenta in grat_debe.cuentas_line:
					if dis.analitica.id == cuenta.analytic_id.id:
						if cuenta.account_id.id not in d_dis_dict:
							d_dis_dict[cuenta.account_id.id] = line.provision * dis.porcentaje/100.00
						else:
							d_dis_dict[cuenta.account_id.id] += line.provision * dis.porcentaje/100.00
						encontrado = True
				if not encontrado:
						error_msg += (dis.analitica.name if dis.analitica.name else '') + "->" + grat_debe.name + "\n"
				for cuenta in bon_debe.cuentas_line:
					if dis.analitica.id == cuenta.analytic_id.id:
						if cuenta.account_id.id not in d_dis_dict:
							d_dis_dict[cuenta.account_id.id] = line.bonus * dis.porcentaje/100.00
						else:
							d_dis_dict[cuenta.account_id.id] += line.bonus * dis.porcentaje/100.00
						encontrado_b = True
				if not encontrado:
						error_msg += (dis.analitica.name if dis.analitica.name else '') + "->" + bon_debe.name + "\n"

			h_dis_dict[grat_haber.account_haber_id.id] += line.provision
			h_dis_dict[bon_haber.account_haber_id.id]  += line.bonus

		for line in self.lines_vac:
			for dis in line.employee_id.dist_c.distribucion_lines:
				encontrado = False
				for cuenta in vac_debe.cuentas_line:
					if dis.analitica.id == cuenta.analytic_id.id:
						if cuenta.account_id.id not in d_dis_dict:
							d_dis_dict[cuenta.account_id.id] = line.provision * dis.porcentaje/100.00
						else:
							d_dis_dict[cuenta.account_id.id] += line.provision * dis.porcentaje/100.00
						encontrado = True
				if not encontrado:
						error_msg += (dis.analitica.name if dis.analitica.name else '') + "->" + vac_debe.name + "\n"

			h_dis_dict[vac_haber.account_haber_id.id] += line.provision

		aj = self.env['account.journal'].search([('code','=','11')])
		if len(aj) == 0:
			raise osv.except_osv("Alerta!", u"No existe el diario PLANILLA")

		if not self.account_move2_id.id:
			n_vals = {
				'journal_id': aj[0].id,
				'period_id' : self.period_id.id,
				'date'      : self.period_id.date_stop,
				'name'      : 'Planilla '+self.period_id.code,
			}
			n_am = self.env['account.move'].create(n_vals)
			self.account_move2_id = n_am.id
		else:
			n_vals = {
				'journal_id': aj[0].id,
				'period_id' : self.period_id.id,
				'date'      : self.period_id.date_stop,
				'name'      : 'Planilla '+self.period_id.code,
			}
			self.account_move2_id.write(n_vals)

			for line in self.account_move2_id.line_id:
				line.unlink()

		for k,v in d_dis_dict.items():
			nl_vals = {
				'move_id'   : self.account_move2_id.id,
				'account_id': k,
				'debit'     : float(decimal.Decimal(str( v )).quantize(decimal.Decimal('1.111111'),rounding=decimal.ROUND_HALF_UP)),
				'credit'    : 0,
				'name'      : 'Planilla '+self.period_id.code,
			}
			n_aml = self.env['account.move.line'].create(nl_vals)

		for k,v in h_dis_dict.items():
			nl_vals = {
				'move_id'   : self.account_move2_id.id,
				'account_id': k,
				'debit'     : 0,
				'credit'    : float(decimal.Decimal(str( v )).quantize(decimal.Decimal('1.111111'),rounding=decimal.ROUND_HALF_UP)),
				'name'      : 'Planilla '+self.period_id.code,
			}
			n_aml = self.env['account.move.line'].create(nl_vals)

	@api.multi
	def make_excel(self):
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		output = io.BytesIO()

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		title_wb = "Provisiones_"+self.period_id.code.replace("/","")+".xlsx"
		workbook = Workbook(direccion + title_wb)
		worksheet_cts = workbook.add_worksheet("CTS")
		worksheet_gra = workbook.add_worksheet("Gratificaciones")
		worksheet_vac = workbook.add_worksheet("Vacaciones")

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

		numeric_bold = numeric.copy()
		numeric_bold['bold'] = 1

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
		numeric_bold_format = workbook.add_format(numeric_bold)
		bold_format = workbook.add_format(bold)
		header_format = workbook.add_format(header)
		title_format = workbook.add_format(title)


		sheets = ['worksheet_cts','worksheet_gra','worksheet_vac']
		for it in sheets:
			sh = it+".write(0,0,'CALQUIPA',title_format)"
			eval(sh)
			sh = it+".write(1,0,'Periodo:',title_format)"
			eval(sh)
			sh = it+".write(1,1, self.period_id.code,basic_format)"
			eval(sh)

			sh = it+".set_column('A:N', 16)"
			eval(sh)

		fil = 3
		col = 0

		worksheet_cts.write(fil, col, u'Nro.', header_format)
		col += 1
		worksheet_cts.write(fil, col, u'Número de Documento', header_format)
		col += 1
		worksheet_cts.write(fil, col, u'Código', header_format)
		col += 1
		worksheet_cts.write(fil, col, u'Empleado', header_format)
		col += 1
		worksheet_cts.write(fil, col, u'Fecha Ingreso', header_format)
		col += 1
		worksheet_cts.write(fil, col, u'Remuneración Básica', header_format)
		col += 1
		worksheet_cts.write(fil, col, u'Asignación Familiar', header_format)
		col += 1
		worksheet_cts.write(fil, col, u'1/6 Gratificación', header_format)
		col += 1
		worksheet_cts.write(fil, col, u'Provisiones CTS', header_format)
		col += 1
		worksheet_cts.write(fil, col, u'Total CTS', header_format)

		fil += 1

		tot_cts = [0]*5
		for line in self.lines_cts:
			col = 0
			worksheet_cts.write(fil, col, line.number if line.number else '', basic_format)
			col += 1
			worksheet_cts.write(fil, col, line.doc_number if line.doc_number else '', basic_format)
			col += 1
			worksheet_cts.write(fil, col, line.code if line.code else '', basic_format)
			col += 1
			worksheet_cts.write(fil, col, line.employee_id.name_related if line.employee_id.name_related else '', basic_format)
			col += 1
			worksheet_cts.write(fil, col, line.start_date if line.start_date else '', basic_format)
			col += 1
			worksheet_cts.write(fil, col, line.basic_remuneration if line.basic_remuneration else 0, numeric_format)
			col += 1
			worksheet_cts.write(fil, col, line.familiar_assign if line.familiar_assign else 0, numeric_format)
			col += 1
			worksheet_cts.write(fil, col, line.c1_6 if line.c1_6 else 0, numeric_format)
			col += 1
			worksheet_cts.write(fil, col, line.provision if line.provision else 0, numeric_format)
			col += 1
			worksheet_cts.write(fil, col, line.total_w_conceptos if line.total_w_conceptos else 0, numeric_format)
			fil += 1

			tot_cts[0] += line.basic_remuneration
			tot_cts[1] += line.familiar_assign
			tot_cts[2] += line.c1_6
			tot_cts[3] += line.provision
			tot_cts[4] += line.total_w_conceptos

		col = 5
		worksheet_cts.write(fil, col, tot_cts[0], numeric_bold_format)
		col += 1
		worksheet_cts.write(fil, col, tot_cts[1], numeric_bold_format)
		col += 1
		worksheet_cts.write(fil, col, tot_cts[2], numeric_bold_format)
		col += 1
		worksheet_cts.write(fil, col, tot_cts[3], numeric_bold_format)
		col += 1
		worksheet_cts.write(fil, col, tot_cts[4], numeric_bold_format)
		col += 1


		fil = 3
		col = 0

		worksheet_gra.write(fil, col, u'Nro.', header_format)
		col += 1
		worksheet_gra.write(fil, col, u'Número de Documento', header_format)
		col += 1
		worksheet_gra.write(fil, col, u'Código', header_format)
		col += 1
		worksheet_gra.write(fil, col, u'Empleado', header_format)
		col += 1
		worksheet_gra.write(fil, col, u'Fecha Ingreso', header_format)
		col += 1
		worksheet_gra.write(fil, col, u'Remuneración Básica', header_format)
		col += 1
		worksheet_gra.write(fil, col, u'Asignación Familiar', header_format)
		col += 1
		worksheet_gra.write(fil, col, u'Provisiones Gratificación', header_format)
		col += 1
		worksheet_gra.write(fil, col, u'Bonificación de Gratificación', header_format)
		col += 1
		worksheet_gra.write(fil, col, u'Total', header_format)
		col += 1
		worksheet_gra.write(fil, col, u'Total grat.', header_format)

		fil += 1

		tot_gra = [0]*6
		for line in self.lines_grat:
			col = 0
			worksheet_gra.write(fil, col, line.number if line.number else '', basic_format)
			col += 1
			worksheet_gra.write(fil, col, line.doc_number if line.doc_number else '', basic_format)
			col += 1
			worksheet_gra.write(fil, col, line.code if line.code else '', basic_format)
			col += 1
			worksheet_gra.write(fil, col, line.employee_id.name_related if line.employee_id.name_related else '', basic_format)
			col += 1
			worksheet_gra.write(fil, col, line.start_date if line.start_date else '', basic_format)
			col += 1
			worksheet_gra.write(fil, col, line.basic_remuneration if line.basic_remuneration else 0, numeric_format)
			col += 1
			worksheet_gra.write(fil, col, line.familiar_assign if line.familiar_assign else 0, numeric_format)
			col += 1
			worksheet_gra.write(fil, col, line.provision if line.provision else 0, numeric_format)
			col += 1
			worksheet_gra.write(fil, col, line.bonus if line.bonus else 0, numeric_format)
			col += 1
			worksheet_gra.write(fil, col, line.total if line.total else 0, numeric_format)
			col += 1
			worksheet_gra.write(fil, col, line.total_w_conceptos if line.total_w_conceptos else 0, numeric_format)
			fil += 1

			tot_gra[0] += line.basic_remuneration
			tot_gra[1] += line.familiar_assign
			tot_gra[2] += line.provision
			tot_gra[3] += line.bonus
			tot_gra[4] += line.total
			tot_gra[5] += line.total_w_conceptos

		col = 5
		worksheet_gra.write(fil, col, tot_gra[0], numeric_bold_format)
		col += 1
		worksheet_gra.write(fil, col, tot_gra[1], numeric_bold_format)
		col += 1
		worksheet_gra.write(fil, col, tot_gra[2], numeric_bold_format)
		col += 1
		worksheet_gra.write(fil, col, tot_gra[3], numeric_bold_format)
		col += 1
		worksheet_gra.write(fil, col, tot_gra[4], numeric_bold_format)
		col += 1
		worksheet_gra.write(fil, col, tot_gra[5], numeric_bold_format)



		fil = 3
		col = 0

		worksheet_vac.write(fil, col, u'Nro.', header_format)
		col += 1
		worksheet_vac.write(fil, col, u'Número de Documento', header_format)
		col += 1
		worksheet_vac.write(fil, col, u'Código', header_format)
		col += 1
		worksheet_vac.write(fil, col, u'Empleado', header_format)
		col += 1
		worksheet_vac.write(fil, col, u'Fecha Ingreso', header_format)
		col += 1
		worksheet_vac.write(fil, col, u'Remuneración Básica', header_format)
		col += 1
		worksheet_vac.write(fil, col, u'Asignación Familiar', header_format)
		col += 1
		worksheet_vac.write(fil, col, u'Provisiones Vacación', header_format)
		col += 1
		worksheet_vac.write(fil, col, u'Total grat.', header_format)

		fil += 1

		tot_gra = [0]*4
		for line in self.lines_vac:
			col = 0
			worksheet_vac.write(fil, col, line.number if line.number else '', basic_format)
			col += 1
			worksheet_vac.write(fil, col, line.doc_number if line.doc_number else '', basic_format)
			col += 1
			worksheet_vac.write(fil, col, line.code if line.code else '', basic_format)
			col += 1
			worksheet_vac.write(fil, col, line.employee_id.name_related if line.employee_id.name_related else '', basic_format)
			col += 1
			worksheet_vac.write(fil, col, line.start_date if line.start_date else '', basic_format)
			col += 1
			worksheet_vac.write(fil, col, line.basic_remuneration if line.basic_remuneration else 0, numeric_format)
			col += 1
			worksheet_vac.write(fil, col, line.familiar_assign if line.familiar_assign else 0, numeric_format)
			col += 1
			worksheet_vac.write(fil, col, line.provision if line.provision else 0, numeric_format)
			col += 1
			worksheet_vac.write(fil, col, line.total_w_conceptos if line.total_w_conceptos else 0, numeric_format)
			fil += 1

			tot_gra[0] += line.basic_remuneration
			tot_gra[1] += line.familiar_assign
			tot_gra[2] += line.provision
			tot_gra[3] += line.total_w_conceptos

		col = 5
		worksheet_vac.write(fil, col, tot_gra[0], numeric_bold_format)
		col += 1
		worksheet_vac.write(fil, col, tot_gra[1], numeric_bold_format)
		col += 1
		worksheet_vac.write(fil, col, tot_gra[2], numeric_bold_format)
		col += 1
		worksheet_vac.write(fil, col, tot_gra[3], numeric_bold_format)


		
		workbook.close()

		f = open(direccion + title_wb, 'rb')
		
		vals = {
			'output_name': title_wb,
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
	def make_excel_ec(self):
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		output = io.BytesIO()

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		titulo    = u'Reporte_estado_de_cuenta'
		workbook  = Workbook(direccion + titulo + '.xlsx')

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

		numeric_int = basic.copy()
		numeric_int['align'] = 'right'

		numeric_int_bold = numeric.copy()
		numeric_int_bold['bold'] = 1

		numeric_bold = numeric.copy()
		numeric_bold['bold'] = 1
		numeric_bold['num_format'] = '#,##0.00'

		bold = basic.copy()
		bold['bold'] = 1

		header = bold.copy()
		header['bg_color'] = '#A9D0F5'
		header['border'] = 1
		header['align'] = 'center'

		title = bold.copy()
		title['font_size'] = 15

		highlight_line = basic.copy()
		highlight_line['bold'] = 1
		highlight_line['bg_color'] = '#C1E1FF'

		highlight_numeric_line = highlight_line.copy()
		highlight_numeric_line['num_format'] = '#,##0.00'
		highlight_numeric_line['align'] = 'right'
		
		basic_format                  = workbook.add_format(basic)
		bold_format                   = workbook.add_format(bold)
		numeric_int_format            = workbook.add_format(numeric_int)
		numeric_int_bold_format       = workbook.add_format(numeric_int_bold)
		numeric_format                = workbook.add_format(numeric)
		numeric_bold_format           = workbook.add_format(numeric_bold)
		title_format                  = workbook.add_format(title)
		header_format                 = workbook.add_format(header)
		highlight_line_format         = workbook.add_format(highlight_line)
		highlight_numeric_line_format = workbook.add_format(highlight_numeric_line)


		worksheet_c = workbook.add_worksheet("CTS")
		worksheet_g = workbook.add_worksheet("Gratificaciones")
		worksheet_v = workbook.add_worksheet("Vacaciones")

		rc = self.env['res.company'].search([])[0]

		sheets = ['worksheet_c','worksheet_g','worksheet_v']
		for it in sheets:
			sh = it+".write('A1:D1',rc.name if rc.name else '',title_format)"
			eval(sh)
			sh = it+".write('A2:D2','RUC: ' + (rc.partner_id.type_number if rc.partner_id.type_number else ''),title_format)"
			eval(sh)
			sh = it+".write('A3:D3','Listado de Provisiones',title_format)"
			eval(sh)
			sh = it+".set_column('A:A', 44)"
			eval(sh)
			sh = it+".set_column('B:T', 14)"
			eval(sh)

		fil = 4
		col = 0

		headers = ['Nombres']
		for pr in self.sorted(key=lambda r: r.period_id.date_start):
			headers.append(pr.period_id.code)
		headers.append('Total')

		for it in sheets:
			for pos in range(len(headers)): 
				sh = it+".write(fil,pos,headers[pos],header_format)"
				eval(sh)

		fil += 1
		ini_data = fil

		empleados_ids = []
		for pr in self.sorted(key=lambda r: r.period_id.date_start):
			for lc in pr.lines_cts:
				if lc.employee_id.id not in empleados_ids:
					empleados_ids.append(lc.employee_id.id)
			for lg in pr.lines_grat:
				if lg.employee_id.id not in empleados_ids:
					empleados_ids.append(lg.employee_id.id)
			for lv in pr.lines_vac:
				if lv.employee_id.id not in empleados_ids:
					empleados_ids.append(lv.employee_id.id)

		fil = ini_data
		for emp in self.env['hr.employee'].search([('id','in',empleados_ids)]).sorted(key=lambda r: r.name_related):
			for it in sheets:
				sh = it+".write(fil,col,emp.name_related if emp.name_related else '',basic_format)"
				eval(sh)
			fil += 1

		fil = ini_data
		col = 1
		for pr in self.sorted(key=lambda r: r.period_id.date_start):
			fil = ini_data
			for emp in self.env['hr.employee'].search([('id','in',empleados_ids)]).sorted(key=lambda r: r.name_related):				
				hplc = self.env['hr.provisiones.lines.cts'].search([('employee_id','=',emp.id),('provision_id','=',pr.id)])
				hplg = self.env['hr.provisiones.lines.grat'].search([('employee_id','=',emp.id),('provision_id','=',pr.id)])
				hplv = self.env['hr.provisiones.lines.vac'].search([('employee_id','=',emp.id),('provision_id','=',pr.id)])
				
				worksheet_c.write(fil,col,hplc[0].provision if len(hplc) else 0, numeric_format)
				worksheet_g.write(fil,col,hplg[0].total if len(hplg) else 0, numeric_format)
				worksheet_v.write(fil,col,hplv[0].provision if len(hplv) else 0, numeric_format)
				fil += 1
			col += 1

		for it in sheets:
			fil = ini_data
			ini_i = ord('B')
			fin_i = ini_i + len(self) - 1
			ini_c = str(unichr(ini_i))
			fin_c = str(unichr(fin_i))
			for pos in self.env['hr.employee'].search([('id','in',empleados_ids)]).sorted(key=lambda r: r.name_related): 
				ini_p = ini_c + str(fil+1)
				fin_p = fin_c + str(fil+1)
				sh = it+".write(fil,col,'=SUM("+ini_p+":"+fin_p+")',numeric_bold_format)"
				eval(sh)
				fil += 1
					

		
		workbook.close()

		f = open(direccion + titulo + '.xlsx', 'rb')
		
		vals = {
			'output_name': titulo + '.xlsx',
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

class hr_provisiones_lines_cts(models.Model):
	_name = 'hr.provisiones.lines.cts'

	provision_id  = fields.Many2one('hr.provisiones','provision padre')

	number             = fields.Integer('Nro.', compute="get_number")
	doc_number         = fields.Char('Número de Documento')
	code               = fields.Char('Código', compute="get_code")
	employee_id        = fields.Many2one('hr.employee', 'Empleado')
	start_date         = fields.Date('Fecha Ingreso')
	basic_remuneration = fields.Float('Remuneración Básica', compute="get_basic_remuneration")
	familiar_assign    = fields.Float('Asignación Familiar', compute="get_familiar_assign")
	c1_6               = fields.Float(u'1/6 Gratificación', compute="get_c1_6", digits=(20,2))
	provision          = fields.Float('Provisiones CTS', compute="get_provision", digits=(20,2))
	total_w_conceptos  = fields.Float('Total CTS', compute="get_total_w_conceptos")

	concepto_lines	   = fields.One2many('hr.conceptos.line.cts','line_id','Conceptos')

	@api.multi
	def get_number(self):
		for i in range(len(self)):
			self[i].number = i+1

	@api.one
	def get_code(self):
		self.code = self.employee_id.codigo_trabajador

	@api.one
	def get_basic_remuneration(self):
		if self.employee_id.is_practicant:
			self.basic_remuneration = self.employee_id.basica/2.00
		else:
			self.basic_remuneration = self.employee_id.basica

	@api.one
	def get_familiar_assign(self):
		em = self.employee_id.children_number
		if em > 0:
			self.familiar_assign = self.env['hr.parameters'].search([('num_tipo','=','10001')])[0].monto
		else:
			self.familiar_assign = 0

	@api.one
	def get_c1_6(self):
		self.c1_6 = self.basic_remuneration/6.00

	@api.one
	def get_provision(self):
		self.provision = (self.basic_remuneration + self.familiar_assign + self.c1_6 + self.total_w_conceptos)/12.00
		# self.provision = float(decimal.Decimal(str(provision)).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))

	@api.one
	def get_total_w_conceptos(self):
		res = 0
		for line in self.concepto_lines:
			res += line.monto
		self.total_w_conceptos = res

	@api.multi
	def open_concepts(self):
		view_id = self.env.ref('hr_provisiones_it.view_hr_provisiones_lines_cts_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'hr.provisiones.lines.cts',
			'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
		}

	@api.multi
	def close_wizard(self):
		return True


class hr_provisiones_lines_grat(models.Model):
	_name = 'hr.provisiones.lines.grat'

	provision_id  = fields.Many2one('hr.provisiones','provision padre')

	number             = fields.Integer('Nro.', compute="get_number")
	doc_number         = fields.Char('Número de Documento')
	code               = fields.Char('Código', compute="get_code")
	employee_id        = fields.Many2one('hr.employee', 'Empleado')
	start_date         = fields.Date('Fecha Ingreso')
	basic_remuneration = fields.Float('Remuneración Básica', compute="get_basic_remuneration")
	familiar_assign    = fields.Float('Asignación Familiar', compute="get_familiar_assign")
	provision          = fields.Float('Provisiones Gratificación', compute="get_provision", digits=(20,2))
	bonus              = fields.Float('Bonificación de Gratificación', compute="get_bonus", digits=(20,2))
	total              = fields.Float('Total', compute="get_total", digits=(20,2))
	total_w_conceptos  = fields.Float('Total grat.', compute="get_total_w_conceptos")

	concepto_lines	   = fields.One2many('hr.conceptos.line.grat','line_id','Conceptos')

	@api.multi
	def get_number(self):
		for i in range(len(self)):
			self[i].number = i+1

	@api.one
	def get_code(self):
		self.code = self.employee_id.codigo_trabajador

	@api.one
	def get_basic_remuneration(self):
		if self.employee_id.is_practicant:
			self.basic_remuneration = self.employee_id.basica/2.00
		else:
			self.basic_remuneration = self.employee_id.basica

	@api.one
	def get_familiar_assign(self):
		em = self.employee_id.children_number
		if em > 0:
			self.familiar_assign = self.env['hr.parameters'].search([('num_tipo','=','10001')])[0].monto
		else:
			self.familiar_assign = 0

	@api.one
	def get_provision(self):
		self.provision = (self.basic_remuneration + self.familiar_assign + self.total_w_conceptos) /6.00
		# self.provision = float(decimal.Decimal(str(provision)).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))

	@api.one
	def get_bonus(self):
		if self.employee_id.use_eps:
			self.bonus = (self.basic_remuneration + self.familiar_assign) * (self.env['hr.parameters'].search([('num_tipo','=','4')])[0].monto-self.env['hr.parameters'].search([('num_tipo','=','5')])[0].monto)/100.00/6.00
		else:
			self.bonus = (self.basic_remuneration + self.familiar_assign) * (self.env['hr.parameters'].search([('num_tipo','=','4')])[0].monto)/100.00/6.00

	@api.one
	def get_total(self):
		self.total = self.provision + self.bonus
		# self.total = float(decimal.Decimal(str(total)).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))

	@api.one
	def get_total_w_conceptos(self):
		res = 0
		for line in self.concepto_lines:
			res += line.monto
		self.total_w_conceptos = res

	@api.multi
	def open_concepts(self):
		view_id = self.env.ref('hr_provisiones_it.view_hr_provisiones_lines_grat_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'hr.provisiones.lines.grat',
			'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
		}

	@api.multi
	def close_wizard(self):
		return True

class hr_provisiones_lines_vac(models.Model):
	_name = 'hr.provisiones.lines.vac'

	provision_id  = fields.Many2one('hr.provisiones','provision padre')	

	number             = fields.Integer('Nro.', compute="get_number")
	doc_number         = fields.Char('Número de Documento')
	code               = fields.Char('Código', compute="get_code")
	employee_id        = fields.Many2one('hr.employee', 'Empleado')
	start_date         = fields.Date('Fecha Ingreso')
	basic_remuneration = fields.Float('Remuneración Básica', compute="get_basic_remuneration", digits=(20,2))
	familiar_assign    = fields.Float('Asignación Familiar', compute="get_familiar_assign", digits=(20,2))
	provision          = fields.Float('Provisiones Vacación', compute="get_provision", digits=(20,2))
	total_w_conceptos  = fields.Float('Total vac.', compute="get_total_w_conceptos")

	concepto_lines	   = fields.One2many('hr.conceptos.line.vac','line_id','Conceptos')

	@api.multi
	def get_number(self):
		for i in range(len(self)):
			self[i].number = i+1

	@api.one
	def get_code(self):
		self.code = self.employee_id.codigo_trabajador

	@api.one
	def get_basic_remuneration(self):
		if self.employee_id.is_practicant:
			self.basic_remuneration = self.employee_id.basica/2.00
		else:
			self.basic_remuneration = self.employee_id.basica

	@api.one
	def get_familiar_assign(self):
		em = self.employee_id.children_number
		if em > 0:
			self.familiar_assign = self.env['hr.parameters'].search([('num_tipo','=','10001')])[0].monto
		else:
			self.familiar_assign = 0

	@api.one
	def get_provision(self):
		self.provision = (self.basic_remuneration + self.familiar_assign + self.total_w_conceptos) /12.00
		# self.provision = float(decimal.Decimal(str(provision)).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))

	@api.one
	def get_total_w_conceptos(self):
		res = 0
		for line in self.concepto_lines:
			res += line.monto
		self.total_w_conceptos = res

	@api.multi
	def open_concepts(self):
		view_id = self.env.ref('hr_provisiones_it.view_hr_provisiones_lines_vac_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'hr.provisiones.lines.vac',
			'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
		}

	@api.multi
	def close_wizard(self):
		return True

class hr_conceptos_line_cts(models.Model):
	_name = 'hr.conceptos.line.cts'

	line_id = fields.Many2one('hr.provisiones.lines.cts','padre')

	concepto_id = fields.Many2one('hr.lista.conceptos','Concepto',required=True)
	monto       = fields.Float('Monto',required=True)

class hr_conceptos_line_grat(models.Model):
	_name = 'hr.conceptos.line.grat'

	line_id = fields.Many2one('hr.provisiones.lines.grat','padre')

	concepto_id = fields.Many2one('hr.lista.conceptos','Concepto',required=True)
	monto       = fields.Float('Monto',required=True)

class hr_conceptos_line_vac(models.Model):
	_name = 'hr.conceptos.line.vac'

	line_id = fields.Many2one('hr.provisiones.lines.vac','padre')

	concepto_id = fields.Many2one('hr.lista.conceptos','Concepto',required=True)
	monto       = fields.Float('Monto',required=True)