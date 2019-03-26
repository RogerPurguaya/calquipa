# -*- encoding: utf-8 -*-
import base64
from openerp     import models, fields, api
from openerp.osv import osv, expression

import io
import sys
import os

import datetime
from calendar               import monthrange
from dateutil.relativedelta import relativedelta
from xlsxwriter.workbook    import Workbook

class hr_quincenales(models.Model):
	_name     = 'hr.quincenales'
	_rec_name = 'fecha'

	fecha = fields.Date('Fecha', required=True)	
	state = fields.Selection([('draft','Borrador'),('done','Generado')],'estados', default="draft")

	quincenales_lines = fields.One2many('hr.quincenales.lines','quincenal_id','lineas')

	@api.model
	def create(self, vals):
		if len(self.env['hr.quincenales'].search([('fecha','=',vals['fecha'])])):
			raise osv.except_osv("Alerta!", u"Ya existe un registro de quincena con la fecha "+vals['fecha'])
		t = super(hr_quincenales, self).create(vals)
		return t

	@api.one
	def write(self,vals):
		t = super(hr_quincenales, self).write(vals)
		self.refresh()
		
		if 'fecha' in vals:
			if len(self.env['hr.quincenales'].search([('fecha','=',vals['fecha'])])) > 1:
				raise osv.except_osv("Alerta!", u"Ya existe un registro de quincena con la fecha "+vals['fecha'])

			for i in self.quincenales_lines:
				i.unlink()

		return t

	@api.one
	def unlink(self):
		for i in self.quincenales_lines:
			for j in i.quincenales_ingresos_lines:
				j.unlink()
			for k in i.quincenales_descuentos_lines:
				k.unlink()
			i.unlink()
		return super(hr_quincenales, self).unlink()

	@api.multi
	def generate(self):	
		he = self.env['hr.employee'].search([('fecha_cese','=',False),('fecha_ingreso','<=',self.fecha)])
		not_found = []
		to_create = []
		error_msg = ""
		for employee in he:
			hp  = self.env['hr.parameters'].search([('num_tipo','=',10001)])
			hta = self.env['hr.table.adelanto'].search([('code','in',['001'])])

			fch = self.fecha.split('-')
			fch = fch[1] + "/" + fch[0]
			hml = self.env['hr.membership.line'].search([('periodo.code','=',fch),('membership','=',employee.afiliacion.id)])

			if len(hml) > 0:
				hml = hml[0]

				ad = False
				for i in hta:
					if employee.tipo_trabajador.id == i.tipo_trabajador.id:
						ad = i.id
						break
				
				base_dsct = (employee.basica + (hp[0].monto if employee.children_number > 0 else 0))
				base_mod  = employee.basica
				
				quin_desc = 0

				mes_anterior = datetime.datetime.strptime(self.fecha, "%Y-%m-%d")
				mes_anterior -= relativedelta(months=1)
				code_comp = format(mes_anterior.month,'02') + "/" + str(mes_anterior.year)
				ht = self.env['hr.tareo'].search([('periodo.code','=',code_comp)])
				if len(ht) > 0:
					ht = ht[0]
					htl = self.env['hr.tareo.line'].search([('tareo_id','=',ht.id),('employee_id','=',employee.id)])
					if len(htl) > 0:
						htl = htl[0]
						hcl = self.env['hr.concepto.line'].search([('tareo_line_id','=',htl.id),('concepto_id.code','in',['033','069'])])
						for h in hcl:
							quin_desc += h.monto

				fecha_in = datetime.datetime.strptime(employee.fecha_ingreso,"%Y-%m-%d")
				fecha_qu = datetime.datetime.strptime(self.fecha,"%Y-%m-%d")
				fecha_im = datetime.datetime.strptime("-".join([self.fecha.split("-")[0],self.fecha.split("-")[1],"01"]),"%Y-%m-%d")
				if fecha_in.day != 1 and fecha_in >= fecha_im:
					diff = relativedelta(fecha_qu,fecha_in) + relativedelta(days=1)
					base_mod = base_mod / 30.00 * diff.days

				vals = {
					'quincenal_id' : self.id,

					'employee_id'        : employee.id,
					'codigo_trabajador'  : employee.codigo_trabajador,
					'nombres'            : employee.name_related,
					'fecha_ingreso'		 : employee.fecha_ingreso,
					'adelanto_id'		 : ad,
					'basico'             : base_mod,
					'asignacion_familiar': (hp[0].monto if employee.children_number > 0 else 0),
					'onp'                : ((base_mod+(hp[0].monto if employee.children_number > 0 else 0)) * hml.tasa_pensiones/100.00) if employee.afiliacion.code == 'ONP' else 0,
					'afp_com'            : ((base_mod+(hp[0].monto if employee.children_number > 0 else 0)) * hml.tasa_pensiones/100.00) if employee.afiliacion.code != 'ONP' else 0,
					'afp_prima'          : ((base_mod+(hp[0].monto if employee.children_number > 0 else 0)) * hml.c_mixta/100.00) if employee.afiliacion.code != 'ONP' else 0,
					'afp_jub'            : ((base_mod+(hp[0].monto if employee.children_number > 0 else 0)) * hml.c_variable/100.00) if employee.afiliacion.code != 'ONP' else 0,
					'quinta_cat'         : quin_desc,					
				}
				to_create.append(vals)

			else:
				error_msg += "- " + employee.name_related + " / " + (employee.afiliacion.name if employee.afiliacion.name else '') + "\n"

		if len(error_msg) > 0:
			raise osv.except_osv("Alerta!", u"No se econtró afiliación con la fecha indicada para los siguientes empleados.\n"+error_msg)
		
		for v in to_create:
			hql = self.env['hr.quincenales.lines'].search([('employee_id','=',v['employee_id']),('quincenal_id','=',v['quincenal_id'])])
			if len(hql):
				hql[0].write(v)
			else:
				n_ha = self.env['hr.quincenales.lines'].create(v)

	@api.multi
	def crear_adelantos(self):
		for i in self.quincenales_lines:
			vals = {
				'codigo_trabajador': i.codigo_trabajador,
				'employee'         : i.employee_id.id,
				'monto'            : i.quincena,
				'adelanto_id'      : i.adelanto_id.id,
				'fecha'            : self.fecha,
			}

			adelanto_existe = self.env['hr.adelanto'].search([('fecha','=',self.fecha),('employee','=',i.employee_id.id)])
			if len(adelanto_existe):
				adelanto_existe[0].write(vals)
			else:
				self.env['hr.adelanto'].create(vals)
		self.state = "done"

	@api.multi
	def regresar_borrador(self):
		self.state = "draft"

	@api.multi
	def generar_excel(self):
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		output = io.BytesIO()

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

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		titulo    = u'Quincenal_'+self.fecha
		workbook  = Workbook(direccion + titulo + '.xlsx')

		worksheet = workbook.add_worksheet("Centro de Costo")
		worksheet_sin_cc = workbook.add_worksheet("Sin Distribucion C.C.")
		
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


		rc = self.env['res.company'].search([])[0]
		worksheet.merge_range('A1:D1', rc.name if rc.name else '', title_format)
		worksheet.merge_range('A2:D2', "RUC: "+rc.partner_id.type_number if rc.partner_id.type_number else 'RUC: ', title_format)

		headers = [u'Código Trabajador',
				   u'Nombres y Apellidos',
				   u'Adelanto',
				   u'Fecha de Ingreso',
				   u'Básico',
				   u'Asignación Familiar',
				   u'Ingresos Adicionales',
				   u'ONP',
				   u'AFP Com.',
				   u'AFP Prima.',
				   u'AFP Jub',
				   u'5ta Categoría',
				   u'Descuentos Adicionales',
				   u'Total',
				   u'Monto',
				   u'Ingresos Quincenales',
				   u'Adelantos',
				   u'Quincena']				   

		row = 2
		col = 0

		row += 1
		for pos in range(len(headers)):
			worksheet.write(row,pos, headers[pos], header_format)

		row += 1
		for data in self.quincenales_lines:
			ing_adi  = 0
			desc_adi = 0
			ing_adi2 = 0
			for ing in data.quincenales_ingresos_lines:
				ing_adi += ing.monto
			for desc in data.quincenales_descuentos_lines:
				desc_adi += desc.monto
			for ing2 in data.quincenales_ingresos2_lines:
				ing_adi2 += ing2.monto

			col = 0
			worksheet.write(row,col,data.codigo_trabajador if data.codigo_trabajador else '',basic_format)
			col += 1
			worksheet.write(row,col,data.employee_id.name_related if data.employee_id.name_related else '',basic_format)
			col += 1
			worksheet.write(row,col,data.adelanto_id.name if data.adelanto_id.name else '',basic_format)
			col += 1
			worksheet.write(row,col,data.fecha_ingreso if data.fecha_ingreso else '',basic_format)
			col += 1
			worksheet.write(row,col,data.basico if data.basico else 0,numeric_format)
			col += 1
			worksheet.write(row,col,data.asignacion_familiar if data.asignacion_familiar else 0,numeric_format)
			col += 1
			worksheet.write(row,col,ing_adi if ing_adi else 0,numeric_format)
			col += 1
			worksheet.write(row,col,data.onp if data.onp else 0,numeric_format)
			col += 1
			worksheet.write(row,col,data.afp_com if data.afp_com else 0,numeric_format)
			col += 1
			worksheet.write(row,col,data.afp_prima if data.afp_prima else 0,numeric_format)
			col += 1
			worksheet.write(row,col,data.afp_jub if data.afp_jub else 0,numeric_format)
			col += 1
			worksheet.write(row,col,data.quinta_cat if data.quinta_cat else 0,numeric_format)
			col += 1
			worksheet.write(row,col,desc_adi if desc_adi else 0,numeric_format)
			col += 1
			worksheet.write(row,col,data.total if data.total else 0,numeric_format)
			col += 1
			worksheet.write(row,col,data.monto if data.monto else 0,numeric_format)
			col += 1
			worksheet.write(row,col,ing_adi2 if ing_adi2 else 0,numeric_format)
			col += 1
			worksheet.write(row,col,data.adelantos if data.adelantos else 0,numeric_format)
			col += 1
			worksheet.write(row,col,data.quincena if data.quincena else 0,numeric_format)
			col += 1
			row += 1

		col_sizes = [10.00, 16.00, 41.43]
		worksheet.set_column('A:C', col_sizes[1])
		worksheet.set_column('D:P', col_sizes[0])

		workbook.close()

		f = open(direccion + titulo + '.xlsx', 'rb')
		
		vals = {
			'output_name': titulo + '.xlsx',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		sfs_id  = self.env['export.file.save'].create(vals)

		return {
			"type"     : "ir.actions.act_window",
			"res_model": "export.file.save",
			"views"    : [[False, "form"]],
			"res_id"   : sfs_id.id,
			"target"   : "new",
		}


class hr_quincenales_lines(models.Model):
	_name = 'hr.quincenales.lines'

	quincenal_id = fields.Many2one('hr.quincenales','padre')

	state               = fields.Selection([('draft','Borrador'),('done','Generado')],'estados', related="quincenal_id.state")
	employee_id         = fields.Many2one('hr.employee','Empleado')
	codigo_trabajador   = fields.Char(u'Código Trabajador')
	nombres             = fields.Char(u'Nombres y Apellidos')
	fecha_ingreso       = fields.Date(u'Fecha de Ingreso')
	basico              = fields.Float(u'Básico')
	asignacion_familiar = fields.Float(u'Asignación Familiar')
	adelanto_id         = fields.Many2one('hr.table.adelanto','Adelanto')
	onp                 = fields.Float(u'ONP')
	afp_com             = fields.Float(u'AFP Com.')
	afp_prima           = fields.Float(u'AFP Prima.')
	afp_jub             = fields.Float(u'AFP Jub')
	quinta_cat          = fields.Float(u'5ta Categoría')
	total               = fields.Float(u'Total', compute="compute_total")
	monto               = fields.Float(u'Monto', compute="compute_monto")
	adelantos           = fields.Float(u'Adelantos', compute="compute_adelantos")
	quincena            = fields.Float(u'Quincena', compute="compute_quincena")

	quincenales_ingresos_lines   = fields.One2many('hr.quincenales.ingresos.lines','quincenal_line_id','ingresos')
	quincenales_descuentos_lines = fields.One2many('hr.quincenales.descuentos.lines','quincenal_line_id','descuentos')
	quincenales_ingresos2_lines   = fields.One2many('hr.quincenales.ingresos2.lines','quincenal_line_id','ingresos')
	
	@api.one
	def compute_total(self):
		res = (self.basico + self.asignacion_familiar - self.onp - self.afp_com - self.afp_prima - self.afp_jub - self.quinta_cat)
		for i in self.quincenales_ingresos_lines:
			res += i.monto
		for i in self.quincenales_descuentos_lines:
			res -= i.monto
		self.total = res

	@api.one
	def compute_monto(self):
		fecha_in = datetime.datetime.strptime(self.employee_id.fecha_ingreso,"%Y-%m-%d")
		fecha_qu = datetime.datetime.strptime(self.quincenal_id.fecha,"%Y-%m-%d")
		fecha_im = datetime.datetime.strptime("-".join([self.quincenal_id.fecha.split("-")[0],self.quincenal_id.fecha.split("-")[1],"01"]),"%Y-%m-%d")
		if fecha_in.day != 1 and fecha_in >= fecha_im:
			self.monto = self.total
		else:
			self.monto = self.total / 2.00

	@api.one
	def compute_adelantos(self):
		fechai_eva = datetime.datetime.strptime(self.quincenal_id.fecha.split('-')[0]+"-"+self.quincenal_id.fecha.split('-')[1]+"-"+"01","%Y-%m-%d")
		fechaf_eva = datetime.datetime.strptime(self.quincenal_id.fecha,"%Y-%m-%d")

		res = 0
		ha = self.env['hr.adelanto'].search([('fecha','>=',fechai_eva),('fecha','<=',fechaf_eva),('fecha','!=',self.quincenal_id.fecha),('adelanto_id.code','!=','001'),('employee','=',self.employee_id.id)])
		for i in ha:
			res += i.monto
		self.adelantos = res

	@api.one
	def compute_quincena(self):
		res = 0
		for i in self.quincenales_ingresos2_lines:
			res += i.monto
		self.quincena = self.monto + res - self.adelantos


	@api.multi
	def ingresos_wizard(self):
		view_id = self.env.ref('hr_nomina_it.view_hr_quincenales_lines_ing_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'hr.quincenales.lines',
			'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
		}

	@api.multi
	def descuentos_wizard(self):
		view_id = self.env.ref('hr_nomina_it.view_hr_quincenales_lines_desc_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'hr.quincenales.lines',
			'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
		}

	@api.multi
	def ingresos2_wizard(self):
		view_id = self.env.ref('hr_nomina_it.view_hr_quincenales_lines_ing2_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'hr.quincenales.lines',
			'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
		}

	@api.one
	def save_datai(self):
		self.write({})

	@api.one
	def save_datad(self):
		self.write({})

	@api.one
	def save_datai2(self):
		self.write({})

class hr_quincenales_ingresos_lines(models.Model):
	_name = 'hr.quincenales.ingresos.lines'

	quincenal_line_id = fields.Many2one('hr.quincenales.lines','padre')

	concepto_id = fields.Many2one('hr.lista.conceptos','Concepto', required=True)
	monto       = fields.Float('Monto', required=True)

class hr_quincenales_descuentos_lines(models.Model):
	_name = 'hr.quincenales.descuentos.lines'

	quincenal_line_id = fields.Many2one('hr.quincenales.lines','padre')

	concepto_id = fields.Many2one('hr.lista.conceptos','Concepto', required=True)
	monto       = fields.Float('Monto', required=True)

class hr_quincenales_ingresos2_lines(models.Model):
	_name = 'hr.quincenales.ingresos2.lines'

	quincenal_line_id = fields.Many2one('hr.quincenales.lines','padre')

	concepto_id = fields.Many2one('hr.lista.conceptos','Concepto', required=True)
	monto       = fields.Float('Monto', required=True)
	
class hr_adelanto(models.Model):
	_name = 'hr.adelanto'
	_rec_name = 'employee'

	fecha             = fields.Date('Fecha Adelanto')
	monto             = fields.Float('Monto',digits=(12,2))
	employee          = fields.Many2one('hr.employee','Trabajador')
	codigo_trabajador = fields.Char(u'Código',store=True,related='employee.codigo_trabajador')
	adelanto_id		  = fields.Many2one('hr.table.adelanto', 'Tipo de Adelanto')