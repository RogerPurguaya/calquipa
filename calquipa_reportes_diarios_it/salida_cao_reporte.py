# -*- encoding: utf-8 -*-
import base64
from openerp import models, fields, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp

import calendar
import datetime
import decimal

class salida_cao_oxido(models.Model):
	_name = 'salida.cao.oxido'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')
	no_oc_viva = fields.Float(u'No. O.C. (Cal Viva)')
	real_viva = fields.Float(u'Real (Cal Viva)')
	no_oc2_viva = fields.Float(u'Turno 2do O.C. (Cal Viva)')
	real2_viva = fields.Float(u'Turno 2do Real (Cal Viva)')
	no_oc_total_viva = fields.Float(u'Total Día O.C. (Cal Viva)')
	real_total_viva = fields.Float(u'Total Día Real (Cal Viva)')

	no_oc_granel = fields.Float(u'No. O.C. (CaO Granel)')
	real_granel = fields.Float(u'Real (CaO Granel)')
	no_oc2_granel = fields.Float(u'Turno 2do O.C. (CaO Granel)')
	real2_granel = fields.Float(u'Turno 2do Real (CaO Granel)')
	no_oc_total_granel = fields.Float(u'Total Día O.C. (CaO Granel)')
	real_total_granel = fields.Float(u'Total Día Real (CaO Granel)')

	no_oc_envasado = fields.Float(u'No. O.C. (CaO Env)')
	real_envasado = fields.Float(u'Real (CaO Env)')
	no_oc2_envasado = fields.Float(u'Turno 2do O.C. (CaO Env)')
	real2_envasado = fields.Float(u'Turno 2do Real (CaO Env)')
	no_oc_total_envasado = fields.Float(u'Total Día O.C. (CaO Env)')
	real_total_envasado = fields.Float(u'Total Día Real (CaO Env)')

	total_oc = fields.Float(u'Total O.C.')
	total_real = fields.Float(u'Total Real')

	@api.one
	def compute_check_period(self):
		code = format(self.month_id, '02') + '/' + str(self.year_id)
		ap = self.env['account.period'].search([('code','=',code)])
		if len(ap) > 0:
			ap = ap[0]
			if ap.state == 'done':
				self.check_period = True
			else:
				self.check_period = False
	check_period = fields.Boolean('check period', compute="compute_check_period")


	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "salida.cao.oxido",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['salida.cao.oxido'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['salida.cao.oxido'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "salida.cao.oxido",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class salida_cao_entrada_piedra(models.Model):
	_name = 'salida.cao.entrada.piedra'
	_rec_name = 'partner_id'

	@api.onchange('partner_id')
	def onchange_partner_id(self):
		return {
			'domain':{
				'invoice_id':[('partner_id','=',self.partner_id.id)]
			}
		}

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	partner_id = fields.Many2one('res.partner','Proveedor', required=True)
	placa = fields.Char('Placa')
	date = fields.Date('Fecha', required=True)
	viajes = fields.Integer(u'N° Viajes')
	tara = fields.Float('Tara')
	peso_neto = fields.Float('Peso Neto')
	peso_bruto = fields.Float('Peso Bruto')
	guia = fields.Char(u'Guía de Remisión')
	ticket = fields.Char('Ticket Pesado')
	precio_un = fields.Float('Precio Unitario Dolares', digits=(5,5))
	valor_total = fields.Float('Valor Total Dolares', compute="compute_valor_total", store=True)
	invoice_id = fields.Many2one('account.invoice', 'Factura')

	@api.one
	def compute_check_period(self):
		code = format(self.month_id, '02') + '/' + str(self.year_id)
		ap = self.env['account.period'].search([('code','=',code)])
		if len(ap) > 0:
			ap = ap[0]
			if ap.state == 'done':
				self.check_period = True
			else:
				self.check_period = False
	check_period = fields.Boolean('check period', compute="compute_check_period")

	@api.depends('peso_neto','precio_un')
	@api.one
	def compute_valor_total(self):
		self.valor_total = self.peso_neto * self.precio_un

	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "salida.cao.entrada.piedra",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "salida.cao.entrada.piedra",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

	@api.model
	def create(self,vals):
		t = super(salida_cao_entrada_piedra,self).create(vals)
		f = datetime.datetime.strptime(t.date, "%Y-%m-%d")
		t.month_id = f.month
		t.year_id = f.year
		return t

	@api.one
	def write(self,vals):
		t = super(salida_cao_entrada_piedra,self).write(vals)
		self.refresh()
		if 'date' in vals:			
			f = datetime.datetime.strptime(self.date, "%Y-%m-%d")
			self.month_id = f.month
			self.year_id = f.year
		return t

class salida_cao_entrada_pet_coke(models.Model):
	_name = 'salida.cao.entrada.pet.coke'
	_rec_name = 'partner_id'

	@api.onchange('partner_id')
	def onchange_partner_id(self):
		return {
			'domain':{
				'invoice_id':[('partner_id','=',self.partner_id.id)]
			}
		}

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	partner_id = fields.Many2one('res.partner','Proveedor', required=True)
	placa = fields.Char('Placa')
	date = fields.Date('Fecha', required=True)
	volquete = fields.Integer('Nro. Volquete')
	viajes = fields.Integer(u'N° Viajes')
	tara = fields.Float('Tara')
	peso_neto = fields.Float('Peso Neto')
	peso_bruto = fields.Float('Peso Bruto')
	guia = fields.Char(u'Guía de Remisión')
	ticket = fields.Char('Ticket Pesado')
	precio_un = fields.Float('Precio Unitario Dolares', digits=(5,5))
	valor_total = fields.Float('Valor Total Dolares', compute="compute_valor_total", store=True)
	invoice_id = fields.Many2one('account.invoice', 'Factura')

	@api.one
	def compute_check_period(self):
		code = format(self.month_id, '02') + '/' + str(self.year_id)
		ap = self.env['account.period'].search([('code','=',code)])
		if len(ap) > 0:
			ap = ap[0]
			if ap.state == 'done':
				self.check_period = True
			else:
				self.check_period = False
	check_period = fields.Boolean('check period', compute="compute_check_period")

	@api.depends('peso_neto','precio_un')
	@api.one
	def compute_valor_total(self):
		self.valor_total = self.peso_neto * self.precio_un

	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "salida.cao.entrada.pet.coke",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "salida.cao.entrada.pet.coke",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

	@api.model
	def create(self,vals):
		t = super(salida_cao_entrada_pet_coke,self).create(vals)
		f = datetime.datetime.strptime(t.date, "%Y-%m-%d")
		t.month_id = f.month
		t.year_id = f.year
		return t

	@api.one
	def write(self,vals):
		t = super(salida_cao_entrada_pet_coke,self).write(vals)
		self.refresh()
		if 'date' in vals:			
			f = datetime.datetime.strptime(self.date, "%Y-%m-%d")
			self.month_id = f.month
			self.year_id = f.year
		return t

class salida_cao_salida_grava(models.Model):
	_name = 'salida.cao.salida.grava'
	_rec_name = 'partner_id'

	@api.onchange('partner_id')
	def onchange_partner_id(self):
		return {
			'domain':{
				'invoice_id':[('partner_id','=',self.partner_id.id)],
				'sale_id':[('partner_id','=',self.partner_id.id)]
			}
		}

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha Salida', required=True)
	sale_id = fields.Many2one('sale.order', 'Nro. OV')
	saldo_inicial = fields.Float('Saldo Inicial OV')
	precio_un = fields.Float('Precio Unitario', digits=(5,2))
	invoice_id = fields.Many2one('account.invoice', 'Nro. Factura')
	guia = fields.Char(u'Guía de Remisión')
	guia_trans = fields.Char(u'Guía de Transportista')
	placa = fields.Char('Placa')
	unidad = fields.Char('Unidad')
	partner_id = fields.Many2one('res.partner','Transportista', required=True)
	product_id = fields.Many2one('product.product', 'Producto')
	peso_bruto = fields.Float('Peso Bruto Kg.')
	tara = fields.Float('Tara')
	peso_neto = fields.Float('Peso Neto Kg', compute="compute_peso_neto")
	peso_neto_tn = fields.Float('Peso Neto en Tn' , compute="compute_peso_neto_tn", store=True)
	saldo_ton = fields.Float('Saldo en Tn por OV', compute="compute_saldo_ton")
	densidad = fields.Float('Densidad')
	eq_m3 = fields.Float('Equivalente a M3', compute="compute_eq_m3", store=True)
	saldo_m3 = fields.Float('Saldo en M3', compute="compute_saldo_m3")
	sub_total = fields.Float('Sub Total', compute="compute_sub_total")
	igv = fields.Float('IGV 18%', compute="compute_igv")
	total = fields.Float('Total', compute="compute_total")
	obs = fields.Text('Observaciones')

	@api.one
	def compute_peso_neto(self):
		self.peso_neto = self.peso_bruto - self.tara

	@api.depends('peso_neto')
	@api.one
	def compute_peso_neto_tn(self):
		self.peso_neto_tn = self.peso_neto / float(1000)

	@api.one
	def compute_saldo_ton(self):
		self.saldo_ton = self.saldo_inicial - self.peso_neto_tn

	@api.depends('peso_neto_tn','densidad')
	@api.one
	def compute_eq_m3(self):
		self.eq_m3 = (self.peso_neto_tn / self.densidad) if self.densidad != 0 else 0

	@api.one
	def compute_saldo_m3(self):
		self.saldo_m3 = (self.saldo_inicial / self.densidad) if self.densidad != 0 else 0

	@api.one
	def compute_sub_total(self):
		self.sub_total = self.total / 1.18

	@api.one
	def compute_igv(self):
		self.igv = self.sub_total * 0.18

	@api.one
	def compute_total(self):
		self.total = self.peso_neto_tn * self.precio_un

	@api.one
	def compute_check_period(self):
		code = format(self.month_id, '02') + '/' + str(self.year_id)
		ap = self.env['account.period'].search([('code','=',code)])
		if len(ap) > 0:
			ap = ap[0]
			if ap.state == 'done':
				self.check_period = True
			else:
				self.check_period = False
	check_period = fields.Boolean('check period', compute="compute_check_period")

	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "salida.cao.salida.grava",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "salida.cao.salida.grava",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

	@api.model
	def create(self,vals):
		t = super(salida_cao_salida_grava,self).create(vals)
		f = datetime.datetime.strptime(t.date, "%Y-%m-%d")
		t.month_id = f.month
		t.year_id = f.year
		return t

	@api.one
	def write(self,vals):
		t = super(salida_cao_salida_grava,self).write(vals)
		self.refresh()
		if 'date' in vals:			
			f = datetime.datetime.strptime(self.date, "%Y-%m-%d")
			self.month_id = f.month
			self.year_id = f.year
		return t

class salida_cao_indicadores_operacion(models.Model):
	_name = 'salida.cao.indicadores.operacion'

	_order = 'id'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	concepto = fields.Char('Concepto')
	cantidad = fields.Float('Cantidad')
	unidades = fields.Char('Unidades')

	dias_transcurridos = fields.Integer('Dias Transcurridos')

	@api.multi
	def display_q(self, mnth, yr, dt, om, oh):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "salida.cao.indicadores.operacion",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		
		conc = [(u'Objetivo Mes',u'Toneladas'),
				(u'Tendencia Mes',u'Toneladas'),
				(u'Acumulado Mes',u'Toneladas'),
				(u'Diferencia Objetivo vs Real',u'Toneladas'),]
		dias_mes = calendar.monthrange(yr, mnth)[1]

		mio = self.env['salida.cao.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth)])
		if len(mio) == 0:
			vals = dict.fromkeys(['year_id','month_id','concepto','cantidad','unidades','dias_transcurridos'],0)

			for i in conc:
				vals['year_id'] = yr
				vals['month_id'] = mnth
				vals['concepto'] = i[0]
				vals['cantidad'] = 0
				vals['unidades'] = i[1]
				vals['dias_transcurridos'] = dt

				if vals['concepto'] == conc[0][0]:
					vals['cantidad'] = om

				if vals['concepto'] == conc[1][0]:
					vals['cantidad'] = 0

				if vals['concepto'] == conc[2][0]:
					vals['cantidad'] = 0

				if vals['concepto'] == conc[3][0]:
					vals['cantidad'] = 0

				nmio = self.env['salida.cao.indicadores.operacion'].create(vals)
		else:		
			for i in mio:
				i.dias_transcurridos = dt
				if i.concepto == conc[0][0]:
					i.cantidad = om

		return {
			"type": "ir.actions.act_window",
			"res_model": "salida.cao.indicadores.operacion",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class salida_cao_reporte(models.Model):
	_name = 'salida.cao.reporte'

	@api.multi
	def generar_excel(self, mnth, yr):
		import io
		from xlsxwriter.workbook import Workbook

		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		output = io.BytesIO()
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		if not direccion:
			raise osv.except_osv('Alerta!', u"No fue configurado el directorio para los archivos en Configuracion.")
		workbook = Workbook( direccion + u'Entradas_Salidas_Planta_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx')
		worksheet = workbook.add_worksheet("Entradas_Salidas_Planta")

		month2name = {
			1: u"Enero",
			2: u"Febrero",
			3: u"Mazro",
			4: u"Abril",
			5: u"Mayo",
			6: u"Junio",
			7: u"Julio",
			8: u"Agosto",
			9: u"Setiembre",
			10: u"Octubre",
			11: u"Noviembre",
			12: u"Diciembre",
		}

		merge_format_t = workbook.add_format()
		merge_format_t.set_border(style=1)
		merge_format_t.set_bold()
		merge_format_t.set_italic()
		merge_format_t.set_align('center')
		merge_format_t.set_align('vcenter')
		merge_format_t.set_font_size(26)

		merge_format_t2 = workbook.add_format()
		merge_format_t2.set_border(style=1)
		merge_format_t2.set_bold()
		merge_format_t2.set_italic()
		merge_format_t2.set_align('center')
		merge_format_t2.set_align('vcenter')
		merge_format_t2.set_font_size(14)

		merge_format_t31 = workbook.add_format()
		merge_format_t31.set_border(style=1)
		merge_format_t31.set_bold()
		merge_format_t31.set_align('center')
		merge_format_t31.set_align('vcenter')
		merge_format_t31.set_font_size(10)
		merge_format_t31.set_font_color("#FFFFFF")
		merge_format_t31.set_bg_color("#0000FF")

		merge_format_t32 = workbook.add_format()
		merge_format_t32.set_border(style=1)
		merge_format_t32.set_bold()
		merge_format_t32.set_align('center')
		merge_format_t32.set_align('vcenter')
		merge_format_t32.set_font_size(10)
		merge_format_t32.set_text_wrap()

		merge_format_ca = workbook.add_format()
		merge_format_ca.set_border(style=1)
		merge_format_ca.set_align('right')

		merge_format_ca2 = workbook.add_format()
		merge_format_ca2.set_border(style=1)
		merge_format_ca2.set_align('center')

		data_format_d = workbook.add_format()
		data_format_d.set_align('center')
		data_format_d.set_num_format('#,##0.00')

		data_format_dlr = workbook.add_format()
		data_format_dlr.set_left(1)
		data_format_dlr.set_right(1)
		data_format_dlr.set_align('center')
		data_format_dlr.set_num_format('#,##0.00')

		data_format_tlr = workbook.add_format()
		data_format_tlr.set_left(1)
		data_format_tlr.set_right(1)
		data_format_tlr.set_num_format('#,##0.00')

		data_format_dl = workbook.add_format()
		data_format_dl.set_left(1)
		data_format_dl.set_align('center')
		data_format_dl.set_num_format('#,##0.00')

		data_format_dr = workbook.add_format()
		data_format_dr.set_right(1)
		data_format_dr.set_align('center')
		data_format_dr.set_num_format('#,##0.00')

		data_format_dgr = workbook.add_format()
		data_format_dgr.set_align('center')
		data_format_dgr.set_num_format('#,##0.00')
		data_format_dgr.set_bg_color("#BBBBBB")
		
		data_format_dlrgr = workbook.add_format()
		data_format_dlrgr.set_left(1)
		data_format_dlrgr.set_right(1)
		data_format_dlrgr.set_align('center')
		data_format_dlrgr.set_num_format('#,##0.00')
		data_format_dlrgr.set_bg_color("#BBBBBB")

		data_format_tlrgr = workbook.add_format()
		data_format_tlrgr.set_left(1)
		data_format_tlrgr.set_right(1)
		data_format_tlrgr.set_num_format('#,##0.00')
		data_format_tlrgr.set_bg_color("#BBBBBB")

		data_format_dlgr = workbook.add_format()
		data_format_dlgr.set_left(1)
		data_format_dlgr.set_align('center')
		data_format_dlgr.set_num_format('#,##0.00')
		data_format_dlgr.set_bg_color("#BBBBBB")

		data_format_drgr = workbook.add_format()
		data_format_drgr.set_right(1)
		data_format_drgr.set_align('center')
		data_format_drgr.set_num_format('#,##0.00')
		data_format_drgr.set_bg_color("#BBBBBB")

		data_format_dlrdgr = workbook.add_format()
		data_format_dlrdgr.set_left(1)
		data_format_dlrdgr.set_right(1)
		data_format_dlrdgr.set_bottom(1)
		data_format_dlrdgr.set_align('center')
		data_format_dlrdgr.set_num_format('#,##0.00')
		data_format_dlrdgr.set_bg_color("#BBBBBB")

		data_format_dlrd = workbook.add_format()
		data_format_dlrd.set_left(1)
		data_format_dlrd.set_right(1)
		data_format_dlrd.set_bottom(1)
		data_format_dlrd.set_align('center')
		data_format_dlrd.set_num_format('#,##0.00')

		data_format_dld = workbook.add_format()
		data_format_dld.set_left(1)
		data_format_dld.set_bottom(1)
		data_format_dld.set_align('center')
		data_format_dld.set_num_format('#,##0.00')

		data_format_drd = workbook.add_format()
		data_format_drd.set_right(1)
		data_format_drd.set_bottom(1)
		data_format_drd.set_align('center')
		data_format_drd.set_num_format('#,##0.00')

		data_format_dlrg = workbook.add_format()
		data_format_dlrg.set_right(1)
		data_format_dlrg.set_align('center')
		data_format_dlrg.set_num_format('#,##0.00')
		data_format_dlrg.set_bg_color("#137519")


		data_format_total = workbook.add_format()
		data_format_total.set_border(style=1)
		data_format_total.set_bold()
		data_format_total.set_align('center')
		data_format_total.set_font_size(10)
		data_format_total.set_bg_color("#8F8F8F")
		data_format_total.set_num_format('#,##0.00')

		empty_top = workbook.add_format()
		empty_top.set_top(1)




		worksheet.set_column("A:A", 3.86)
		worksheet.set_column("X:X", 3.86)
		worksheet.set_column("AL:AL", 3.86)
		worksheet.set_column("BA:BA", 3.86)

		worksheet.merge_range("B2:E8", '', merge_format_t)
		worksheet.merge_range("F2:BS8", u'Calquipa', merge_format_t)
		worksheet.merge_range("BT2:BV2", u'Fecha:', merge_format_ca)
		worksheet.merge_range("BW2:BX2", datetime.datetime.today().strftime("%Y-%m-%d"), merge_format_ca2)
		worksheet.merge_range("BT3:BV3", u'Mes:', merge_format_ca)
		worksheet.merge_range("BW3:BX3", month2name[mnth], merge_format_ca2)
		worksheet.merge_range("BT4:BV4", u'Días de Mes:', merge_format_ca)
		worksheet.merge_range("BW4:BX4", calendar.monthrange(yr,mnth)[1], merge_format_ca2)
		worksheet.merge_range("BT5:BV5", u'Días Transcurridos Mes:', merge_format_ca)

		acio = self.env['salida.cao.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
		if len(acio) > 0:
			acio = acio[0]
			worksheet.merge_range("BW5:BX5", acio.dias_transcurridos, merge_format_ca2)
		else:
			worksheet.merge_range("BW5:BX5", '', merge_format_ca2)

		worksheet.merge_range("BT6:BV6", u'Hrs Mes:', merge_format_ca)
		worksheet.merge_range("BW6:BX6", u'', merge_format_ca2)
		worksheet.merge_range("BT7:BV7", u'Clave SGI', merge_format_ca)
		worksheet.merge_range("BW7:BX7", u'', merge_format_ca2)
		worksheet.merge_range("BT8:BV8", u'Folio', merge_format_ca)
		worksheet.merge_range("BW8:BX8", u'', merge_format_ca2)

		worksheet.insert_image('B3', 'calquipalright.png', {'x_scale': 1.5, 'y_scale': 1.5, 'x_offset':4})
		worksheet.insert_image('F3', 'calquipalleft.png', {'x_scale': 1.5, 'y_scale': 1.5, 'x_offset':4})

		worksheet.set_row(9, 21)
		worksheet.merge_range("B10:BX10", u'Entradas y Salidas de Planta', merge_format_t)

		worksheet.set_row(11, 20)
		worksheet.merge_range("B12:V12", u'Salidas de Oxido', merge_format_t2)
		worksheet.merge_range("Y12:AJ12", u'Entradas de Piedra', merge_format_t2)
		worksheet.merge_range("AM12:AY12", u'Entradas de Pet Coke', merge_format_t2)
		worksheet.merge_range("BB12:BX12", u'Salidas de Grava', merge_format_t2)

		worksheet.set_row(12, 20.25)
		worksheet.set_row(13, 33)
		worksheet.set_row(14, 12)
		worksheet.merge_range("B13:B15", u'Fecha', merge_format_t31)
		worksheet.merge_range("C13:H13", u'Cal Viva', merge_format_t32)
		worksheet.merge_range("C14:C15", u'Turno 1er O.C.', merge_format_t32)
		worksheet.merge_range("D14:D15", u'Turno 1er Real', merge_format_t32)
		worksheet.merge_range("E14:E15", u'Turno 2do O.C.', merge_format_t32)
		worksheet.merge_range("F14:F15", u'Turno 2do Real', merge_format_t32)
		worksheet.merge_range("G14:G15", u'Total Día O.C.', merge_format_t32)
		worksheet.merge_range("H14:H15", u'Total Día Real', merge_format_t32)
		worksheet.merge_range("I13:N13", u'Micronizado de CaO Granel', merge_format_t32)
		worksheet.merge_range("I14:I15", u'Turno 1er O.C.', merge_format_t32)
		worksheet.merge_range("J14:J15", u'Turno 1er Real', merge_format_t32)
		worksheet.merge_range("K14:K15", u'Turno 2do O.C.', merge_format_t32)
		worksheet.merge_range("L14:L15", u'Turno 2do Real', merge_format_t32)
		worksheet.merge_range("M14:M15", u'Total Día O.C.', merge_format_t32)
		worksheet.merge_range("N14:N15", u'Total Día Real', merge_format_t32)
		worksheet.merge_range("O13:T13", u'CaO Envasado', merge_format_t32)
		worksheet.merge_range("O14:O15", u'Turno 1er O.C.', merge_format_t32)
		worksheet.merge_range("P14:P15", u'Turno 1er Real', merge_format_t32)
		worksheet.merge_range("Q14:Q15", u'Turno 2do O.C.', merge_format_t32)
		worksheet.merge_range("R14:R15", u'Turno 2do Real', merge_format_t32)
		worksheet.merge_range("S14:S15", u'Total Día O.C.', merge_format_t32)
		worksheet.merge_range("T14:T15", u'Total Día Real', merge_format_t32)
		worksheet.merge_range("U13:V13", u'Total del Día', merge_format_t32)
		worksheet.merge_range("U14:U15", u'Total Día O.C.', merge_format_t32)
		worksheet.merge_range("V14:V15", u'Total Día Real', merge_format_t32)

		sco = self.env['salida.cao.oxido'].search([('year_id','=',yr),('month_id','=',mnth)])
		scio = self.env['salida.cao.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
		scep = self.env['salida.cao.entrada.piedra'].search([('month_id','=',mnth),('year_id','=',yr)])
		scepc = self.env['salida.cao.entrada.pet.coke'].search([('month_id','=',mnth),('year_id','=',yr)])
		scsg = self.env['salida.cao.salida.grava'].search([('month_id','=',mnth),('year_id','=',yr)])

		print len(sco),len(scio),len(scep), len(scepc), len(scsg)
		if len(sco) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de SALIDA OXIDO para el periodo seleccionado.")
		if len(scio) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de INDICADORES DE OPERACION para el periodo seleccionado.")
		

		sum_sco = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

		x = 15
		for i in range(len(sco)):
			fch = format(i+1,'02')+'-'+month2name[mnth][:3]
			worksheet.write(x,1, fch, data_format_dlr)
			if i % 2 == 0:
				worksheet.write(x,2, sco[i].no_oc_viva, data_format_d)
				worksheet.write(x,3, sco[i].real_viva, data_format_d)
				worksheet.write(x,4, sco[i].no_oc2_viva, data_format_d)
				worksheet.write(x,5, sco[i].real2_viva, data_format_d)
				worksheet.write(x,6, sco[i].no_oc_total_viva, data_format_d)
				worksheet.write(x,7, sco[i].real_total_viva, data_format_dr)
				worksheet.write(x,8, sco[i].no_oc_granel, data_format_d)
				worksheet.write(x,9, sco[i].real_granel, data_format_d)
				worksheet.write(x,10, sco[i].no_oc2_granel, data_format_d)
				worksheet.write(x,11, sco[i].real2_granel, data_format_d)
				worksheet.write(x,12, sco[i].no_oc_total_granel, data_format_d)
				worksheet.write(x,13, sco[i].real_total_granel, data_format_dr)
				worksheet.write(x,14, sco[i].no_oc_envasado, data_format_d)
				worksheet.write(x,15, sco[i].real_envasado, data_format_d)
				worksheet.write(x,16, sco[i].no_oc2_envasado, data_format_d)
				worksheet.write(x,17, sco[i].real2_envasado, data_format_d)
				worksheet.write(x,18, sco[i].no_oc_total_envasado, data_format_d)
				worksheet.write(x,19, sco[i].real_total_envasado, data_format_dr)
				worksheet.write(x,20, sco[i].total_oc, data_format_d)
				worksheet.write(x,21, sco[i].total_real, data_format_dr)		

			else:
				worksheet.write(x,2, sco[i].no_oc_viva, data_format_dgr)
				worksheet.write(x,3, sco[i].real_viva, data_format_dgr)
				worksheet.write(x,4, sco[i].no_oc2_viva, data_format_dgr)
				worksheet.write(x,5, sco[i].real2_viva, data_format_dgr)
				worksheet.write(x,6, sco[i].no_oc_total_viva, data_format_dgr)
				worksheet.write(x,7, sco[i].real_total_viva, data_format_drgr)
				worksheet.write(x,8, sco[i].no_oc_granel, data_format_dgr)
				worksheet.write(x,9, sco[i].real_granel, data_format_dgr)
				worksheet.write(x,10, sco[i].no_oc2_granel, data_format_dgr)
				worksheet.write(x,11, sco[i].real2_granel, data_format_dgr)
				worksheet.write(x,12, sco[i].no_oc_total_granel, data_format_dgr)
				worksheet.write(x,13, sco[i].real_total_granel, data_format_drgr)
				worksheet.write(x,14, sco[i].no_oc_envasado, data_format_dgr)
				worksheet.write(x,15, sco[i].real_envasado, data_format_dgr)
				worksheet.write(x,16, sco[i].no_oc2_envasado, data_format_dgr)
				worksheet.write(x,17, sco[i].real2_envasado, data_format_dgr)
				worksheet.write(x,18, sco[i].no_oc_total_envasado, data_format_dgr)
				worksheet.write(x,19, sco[i].real_total_envasado, data_format_drgr)
				worksheet.write(x,20, sco[i].total_oc, data_format_dgr)
				worksheet.write(x,21, sco[i].total_real, data_format_drgr)		
			
			sum_sco[0] += sco[i].no_oc_viva
			sum_sco[1] += sco[i].real_viva
			sum_sco[2] += sco[i].no_oc2_viva
			sum_sco[3] += sco[i].real2_viva
			sum_sco[4] += sco[i].no_oc_total_viva
			sum_sco[5] += sco[i].real_total_viva
			sum_sco[6] += sco[i].no_oc_granel
			sum_sco[7] += sco[i].real_granel
			sum_sco[8] += sco[i].no_oc2_granel
			sum_sco[9] += sco[i].real2_granel
			sum_sco[10] += sco[i].no_oc_total_granel
			sum_sco[11] += sco[i].real_total_granel
			sum_sco[12] += sco[i].no_oc_envasado
			sum_sco[13] += sco[i].real_envasado
			sum_sco[14] += sco[i].no_oc2_envasado
			sum_sco[15] += sco[i].real2_envasado
			sum_sco[16] += sco[i].no_oc_total_envasado
			sum_sco[17] += sco[i].real_total_envasado
			sum_sco[18] += sco[i].total_oc
			sum_sco[19] += sco[i].total_real

			x += 1

		worksheet.write(x,1, u'Totales', data_format_total)
		worksheet.write(x,2, sum_sco[0], data_format_total)
		worksheet.write(x,3, sum_sco[1], data_format_total)
		worksheet.write(x,4, sum_sco[2], data_format_total)
		worksheet.write(x,5, sum_sco[3], data_format_total)
		worksheet.write(x,6, sum_sco[4], data_format_total)
		worksheet.write(x,7, sum_sco[5], data_format_total)
		worksheet.write(x,8, sum_sco[6], data_format_total)
		worksheet.write(x,9, sum_sco[7], data_format_total)
		worksheet.write(x,10, sum_sco[8], data_format_total)
		worksheet.write(x,11, sum_sco[9], data_format_total)
		worksheet.write(x,12, sum_sco[10], data_format_total)
		worksheet.write(x,13, sum_sco[11], data_format_total)
		worksheet.write(x,14, sum_sco[12], data_format_total)
		worksheet.write(x,15, sum_sco[13], data_format_total)
		worksheet.write(x,16, sum_sco[14], data_format_total)
		worksheet.write(x,17, sum_sco[15], data_format_total)
		worksheet.write(x,18, sum_sco[16], data_format_total)
		worksheet.write(x,19, sum_sco[17], data_format_total)
		worksheet.write(x,20, sum_sco[18], data_format_total)
		worksheet.write(x,21, sum_sco[19], data_format_total)

		x = 48

		worksheet.merge_range(x,2,x,13, u'Indicadores de Operación', merge_format_t32)
		x+=1
		worksheet.merge_range(x,2,x,5, u'Concepto', merge_format_t32)
		worksheet.merge_range(x,6,x,11, u'Cantidad', merge_format_t32)
		worksheet.merge_range(x,12,x,13, u'Unidades', merge_format_t32)

		x += 1
		scio = self.env['salida.cao.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
		for i in range(len(scio)):
			if i % 2 == 0:
				if i == len(scio)-1:
					worksheet.merge_range(x,2,x,5, scio[i].concepto, data_format_dlrd)
					worksheet.merge_range(x,6,x,11, scio[i].cantidad, data_format_dlrd)
					worksheet.merge_range(x,12,x,13, scio[i].unidades, data_format_dlrd)

				else:
					worksheet.merge_range(x,2,x,5, scio[i].concepto, data_format_dlr)
					if i == 0:
						worksheet.merge_range(x,6,x,11, scio[i].cantidad, data_format_dlrg)
					else:
						worksheet.merge_range(x,6,x,11, scio[i].cantidad, data_format_dlr)
					worksheet.merge_range(x,12,x,13, scio[i].unidades, data_format_dlr)
			else:
				if i == len(scio)-1:
					worksheet.merge_range(x,2,x,5, scio[i].concepto, data_format_dlrdgr)
					worksheet.merge_range(x,6,x,11, scio[i].cantidad, data_format_dlrdgr)
					worksheet.merge_range(x,12,x,13, scio[i].unidades, data_format_dlrdgr)
				else:
					worksheet.merge_range(x,2,x,5, scio[i].concepto, data_format_dlrgr)
					if i == 0 or i == 4:
						worksheet.merge_range(x,6,x,11, scio[i].cantidad, data_format_dlrg)
					else:
						worksheet.merge_range(x,6,x,11, scio[i].cantidad, data_format_dlrgr)
					worksheet.merge_range(x,12,x,13, scio[i].unidades, data_format_dlrgr)
			x += 1



		""" OTROS REPORTES, DISTINTA LOGICA """

		worksheet.set_column("Y:Y", 68.86)
		worksheet.set_column("A:A", 11.14)
		worksheet.set_column("AJ:AJ", 12.43)
		worksheet.set_column("Z:Z", 10.86)
		worksheet.set_column("AA:AA", 10.86)
		worksheet.set_column("AN:AN", 10.86)
		worksheet.set_column("AO:AO", 10.86)
		worksheet.set_column("AY:AY", 12.43)

		worksheet.merge_range("Y13:Y15", u'Proveedor', merge_format_t32)
		worksheet.merge_range("Z13:Z15", 'Placa', merge_format_t32)
		worksheet.merge_range("AA13:AA15", 'Fecha', merge_format_t32)
		worksheet.merge_range("AB13:AB15", u'N° Viajes', merge_format_t32)
		worksheet.merge_range("AC13:AC15", 'Tara', merge_format_t32)
		worksheet.merge_range("AD13:AD15", 'Peso Neto', merge_format_t32)
		worksheet.merge_range("AE13:AE15", 'Peso Bruto', merge_format_t32)
		worksheet.merge_range("AF13:AF15", u'Guía de Remisión', merge_format_t32)
		worksheet.merge_range("AG13:AG15", 'Ticket Pesado', merge_format_t32)
		worksheet.merge_range("AH13:AH15", 'Precio Unitario Dolares', merge_format_t32)
		worksheet.merge_range("AI13:AI15", 'Valor Total Dolares', merge_format_t32)
		worksheet.merge_range("AJ13:AJ15", 'Factura', merge_format_t32)

		x = 15
		for i in range(len(scep)):
			if i % 2 == 0:
				worksheet.write(x,24, scep[i].partner_id.name if scep[i].partner_id.name else '', data_format_tlr)
				worksheet.write(x,25, scep[i].placa if scep[i].placa else '', data_format_dr)
				worksheet.write(x,26, scep[i].date if scep[i].date else '', data_format_dr)
				worksheet.write(x,27, scep[i].viajes if scep[i].viajes else 0, data_format_dr)
				worksheet.write(x,28, scep[i].tara if scep[i].tara else 0, data_format_dr)
				worksheet.write(x,29, scep[i].peso_neto if scep[i].peso_neto else 0, data_format_dr)
				worksheet.write(x,30, scep[i].peso_bruto if scep[i].peso_bruto else 0, data_format_dr)
				worksheet.write(x,31, scep[i].guia if scep[i].guia else '', data_format_dr)
				worksheet.write(x,32, scep[i].ticket if scep[i].ticket else '', data_format_dr)
				worksheet.write(x,33, scep[i].precio_un if scep[i].precio_un else 0, data_format_dr)
				worksheet.write(x,34, scep[i].valor_total if scep[i].valor_total else 0, data_format_dr)
				worksheet.write(x,35, scep[i].invoice_id.number if scep[i].invoice_id.number else '', data_format_dr)
			else:
				worksheet.write(x,24, scep[i].partner_id.name if scep[i].partner_id.name else '', data_format_tlrgr)
				worksheet.write(x,25, scep[i].placa if scep[i].placa else '', data_format_drgr)
				worksheet.write(x,26, scep[i].date if scep[i].date else '', data_format_drgr)
				worksheet.write(x,27, scep[i].viajes if scep[i].viajes else 0, data_format_drgr)
				worksheet.write(x,28, scep[i].tara if scep[i].tara else 0, data_format_drgr)
				worksheet.write(x,29, scep[i].peso_neto if scep[i].peso_neto else 0, data_format_drgr)
				worksheet.write(x,30, scep[i].peso_bruto if scep[i].peso_bruto else 0, data_format_drgr)
				worksheet.write(x,31, scep[i].guia if scep[i].guia else '', data_format_drgr)
				worksheet.write(x,32, scep[i].ticket if scep[i].ticket else '', data_format_drgr)
				worksheet.write(x,33, scep[i].precio_un if scep[i].precio_un else 0, data_format_drgr)
				worksheet.write(x,34, scep[i].valor_total if scep[i].valor_total else 0, data_format_drgr)
				worksheet.write(x,35, scep[i].invoice_id.number if scep[i].invoice_id.number else '', data_format_drgr)
			x += 1

		worksheet.write(x,24, ' ', empty_top)
		worksheet.write(x,25, ' ', empty_top)
		worksheet.write(x,26, ' ', empty_top)
		worksheet.write(x,27, ' ', empty_top)
		worksheet.write(x,28, ' ', empty_top)
		worksheet.write(x,29, ' ', empty_top)
		worksheet.write(x,30, ' ', empty_top)
		worksheet.write(x,31, ' ', empty_top)
		worksheet.write(x,32, ' ', empty_top)
		worksheet.write(x,33, ' ', empty_top)
		worksheet.write(x,34, ' ', empty_top)
		worksheet.write(x,35, ' ', empty_top)

		x += 2

		worksheet.merge_range(x,24,x,31, u'Resumen al Día', merge_format_t2)
		x += 1

		worksheet.write(x,24, u'Proveedor', merge_format_ca2)
		worksheet.write(x,25, 'Fecha', merge_format_t32)
		worksheet.write(x,26, u'N° Viajes', merge_format_t32)
		worksheet.write(x,27, 'Tara', merge_format_t32)
		worksheet.write(x,28, 'Peso Neto', merge_format_t32)
		worksheet.write(x,29, 'Peso Bruto', merge_format_t32)
		worksheet.write(x,30, u'Precio Unitario', merge_format_t32)
		worksheet.write(x,31, u'Valor Total', merge_format_t32)
		x += 1


		self.env.cr.execute("""			
			select scep.partner_id,
			       scep.date,
			       sum(scep.viajes) as viajes,
			       sum(scep.tara) as tara,
			       sum(scep.peso_neto) as peso_neto,
			       sum(scep.peso_bruto) as peso_bruto,
			       sum(scep.precio_un) as precio_un,
			       sum(scep.valor_total) as valor_total
			from salida_cao_entrada_piedra scep
			where year_id = """+str(yr)+""" and """+str(mnth)+""" = 11
			group by scep.partner_id,
		         	 scep.date
		    order by scep.date
		""")

		qry = self.env.cr.dictfetchall()

		for i in qry:
			if qry.index(i) % 2 == 0:
				rp = self.env['res.partner'].search([('id','=',i['partner_id'])])[0]
				worksheet.write(x,24, rp.name if rp.name else '', data_format_tlr)
				worksheet.write(x,25, i['date'] if i['date'] else '', data_format_dr)
				worksheet.write(x,26, i['viajes'] if i['viajes'] else 0, data_format_dr)
				worksheet.write(x,27, i['tara'] if i['tara'] else 0, data_format_dr)
				worksheet.write(x,28, i['peso_neto'] if i['peso_neto'] else 0, data_format_dr)
				worksheet.write(x,29, i['peso_bruto'] if i['peso_bruto'] else 0, data_format_dr)
				worksheet.write(x,30, i['precio_un'] if i['precio_un'] else 0, data_format_dr)
				worksheet.write(x,31, i['valor_total'] if i['valor_total'] else 0, data_format_dr)
			else:
				rp = self.env['res.partner'].search([('id','=',i['partner_id'])])[0]
				worksheet.write(x,24, rp.name if rp.name else '', data_format_tlrgr)
				worksheet.write(x,25, i['date'] if i['date'] else '', data_format_drgr)
				worksheet.write(x,26, i['viajes'] if i['viajes'] else 0, data_format_drgr)
				worksheet.write(x,27, i['tara'] if i['tara'] else 0, data_format_drgr)
				worksheet.write(x,28, i['peso_neto'] if i['peso_neto'] else 0, data_format_drgr)
				worksheet.write(x,29, i['peso_bruto'] if i['peso_bruto'] else 0, data_format_drgr)
				worksheet.write(x,30, i['precio_un'] if i['precio_un'] else 0, data_format_drgr)
				worksheet.write(x,31, i['valor_total'] if i['valor_total'] else 0, data_format_drgr)
			x += 1

		worksheet.write(x,24, ' ', empty_top)
		worksheet.write(x,25, ' ', empty_top)
		worksheet.write(x,26, ' ', empty_top)
		worksheet.write(x,27, ' ', empty_top)
		worksheet.write(x,28, ' ', empty_top)
		worksheet.write(x,29, ' ', empty_top)
		worksheet.write(x,30, ' ', empty_top)
		worksheet.write(x,31, ' ', empty_top)

		worksheet.set_column("AM:AM", 68.86)

		worksheet.merge_range("AM13:AM15", u'Proveedor', merge_format_t32)
		worksheet.merge_range("AN13:AN15", 'Placa', merge_format_t32)
		worksheet.merge_range("AO13:AO15", 'Fecha', merge_format_t32)
		worksheet.merge_range("AP13:AP15", 'Nro. Volquete', merge_format_t32)
		worksheet.merge_range("AQ13:AQ15", u'N° Viajes', merge_format_t32)
		worksheet.merge_range("AR13:AR15", 'Tara', merge_format_t32)
		worksheet.merge_range("AS13:AS15", 'Peso Neto', merge_format_t32)
		worksheet.merge_range("AT13:AT15", 'Peso Bruto', merge_format_t32)
		worksheet.merge_range("AU13:AU15", u'Guía de Remisión', merge_format_t32)
		worksheet.merge_range("AV13:AV15", 'Ticket Pesado', merge_format_t32)
		worksheet.merge_range("AW13:AW15", 'Precio Unitario Dolares', merge_format_t32)
		worksheet.merge_range("AX13:AX15", 'Valor Total Dolares', merge_format_t32)
		worksheet.merge_range("AY13:AY15", 'Factura', merge_format_t32)

		x = 15
		for i in range(len(scepc)):
			if i % 2 == 0:
				worksheet.write(x,38, scepc[i].partner_id.name if scepc[i].partner_id.name else '', data_format_tlr)
				worksheet.write(x,39, scepc[i].placa if scepc[i].placa else '', data_format_dr)
				worksheet.write(x,40, scepc[i].date if scepc[i].date else '', data_format_dr)
				worksheet.write(x,41, scepc[i].volquete if scepc[i].volquete else '', data_format_dr)
				worksheet.write(x,42, scepc[i].viajes if scepc[i].viajes else '', data_format_dr)
				worksheet.write(x,43, scepc[i].tara if scepc[i].tara else '', data_format_dr)
				worksheet.write(x,44, scepc[i].peso_neto if scepc[i].peso_neto else '', data_format_dr)
				worksheet.write(x,45, scepc[i].peso_bruto if scepc[i].peso_bruto else '', data_format_dr)
				worksheet.write(x,46, scepc[i].guia if scepc[i].guia else '', data_format_dr)
				worksheet.write(x,47, scepc[i].ticket if scepc[i].ticket else '', data_format_dr)
				worksheet.write(x,48, scepc[i].precio_un if scepc[i].precio_un else '', data_format_dr)
				worksheet.write(x,49, scepc[i].valor_total if scepc[i].valor_total else '', data_format_dr)
				worksheet.write(x,50, scepc[i].invoice_id.number if scepc[i].invoice_id.number else '', data_format_dr)
			else:
				worksheet.write(x,38, scepc[i].partner_id.name if scepc[i].partner_id.name else '', data_format_tlrgr)
				worksheet.write(x,39, scepc[i].placa if scepc[i].placa else '', data_format_drgr)
				worksheet.write(x,40, scepc[i].date if scepc[i].date else '', data_format_drgr)
				worksheet.write(x,41, scepc[i].volquete if scepc[i].volquete else '', data_format_drgr)
				worksheet.write(x,42, scepc[i].viajes if scepc[i].viajes else '', data_format_drgr)
				worksheet.write(x,43, scepc[i].tara if scepc[i].tara else '', data_format_drgr)
				worksheet.write(x,44, scepc[i].peso_neto if scepc[i].peso_neto else '', data_format_drgr)
				worksheet.write(x,45, scepc[i].peso_bruto if scepc[i].peso_bruto else '', data_format_drgr)
				worksheet.write(x,46, scepc[i].guia if scepc[i].guia else '', data_format_drgr)
				worksheet.write(x,47, scepc[i].ticket if scepc[i].ticket else '', data_format_drgr)
				worksheet.write(x,48, scepc[i].precio_un if scepc[i].precio_un else '', data_format_drgr)
				worksheet.write(x,49, scepc[i].valor_total if scepc[i].valor_total else '', data_format_drgr)
				worksheet.write(x,50, scepc[i].invoice_id.number if scepc[i].invoice_id.number else '', data_format_drgr)
			x += 1

		worksheet.write(x,38, ' ', empty_top)
		worksheet.write(x,39, ' ', empty_top)
		worksheet.write(x,40, ' ', empty_top)
		worksheet.write(x,41, ' ', empty_top)
		worksheet.write(x,42, ' ', empty_top)
		worksheet.write(x,43, ' ', empty_top)
		worksheet.write(x,44, ' ', empty_top)
		worksheet.write(x,45, ' ', empty_top)
		worksheet.write(x,46, ' ', empty_top)
		worksheet.write(x,47, ' ', empty_top)
		worksheet.write(x,48, ' ', empty_top)
		worksheet.write(x,49, ' ', empty_top)
		worksheet.write(x,50, ' ', empty_top)

		x += 2

		worksheet.merge_range(x,38,x,45, u'Resumen al Día', merge_format_t2)
		x += 1

		worksheet.write(x,38, u'Proveedor', merge_format_t32)
		worksheet.write(x,39, 'Fecha', merge_format_t32)
		worksheet.write(x,40, u'N° Viajes', merge_format_t32)
		worksheet.write(x,41, 'Tara', merge_format_t32)
		worksheet.write(x,42, 'Peso Neto', merge_format_t32)
		worksheet.write(x,43, 'Peso Bruto', merge_format_t32)
		worksheet.write(x,44, u'Precio Unitario', merge_format_t32)
		worksheet.write(x,45, u'Valor Total', merge_format_t32)
		x += 1

		self.env.cr.execute("""
			select scepc.partner_id,
			       scepc.date,
			       sum(scepc.viajes) as viajes,
			       sum(scepc.tara) as tara,
			       sum(scepc.peso_neto) as peso_neto,
			       sum(scepc.peso_bruto) as peso_bruto,
			       sum(scepc.precio_un) as precio_un,
			       sum(scepc.valor_total) as valor_total
			from salida_cao_entrada_pet_coke scepc
			where year_id = """+str(yr)+""" and month_id = """+str(mnth)+"""
			group by scepc.partner_id,
         			 scepc.date
			order by scepc.date
		""")

		qry = self.env.cr.dictfetchall()

		for i in qry:
			if qry.index(i) % 2 == 0:
				rp = self.env['res.partner'].search([('id','=',i['partner_id'])])[0]
				worksheet.write(x,38, rp.name if rp.name else '', data_format_tlr)
				worksheet.write(x,39, i['date'] if i['date'] else '', data_format_dr)
				worksheet.write(x,40, i['viajes'] if i['viajes'] else 0, data_format_dr)
				worksheet.write(x,41, i['tara'] if i['tara'] else 0, data_format_dr)
				worksheet.write(x,42, i['peso_neto'] if i['peso_neto'] else 0, data_format_dr)
				worksheet.write(x,43, i['peso_bruto'] if i['peso_bruto'] else 0, data_format_dr)
				worksheet.write(x,44, i['precio_un'] if i['precio_un'] else 0, data_format_dr)
				worksheet.write(x,45, i['valor_total'] if i['valor_total'] else 0, data_format_dr)
			else:
				rp = self.env['res.partner'].search([('id','=',i['partner_id'])])[0]
				worksheet.write(x,38, rp.name if rp.name else '', data_format_tlrgr)
				worksheet.write(x,39, i['date'] if i['date'] else '', data_format_drgr)
				worksheet.write(x,40, i['viajes'] if i['viajes'] else 0, data_format_drgr)
				worksheet.write(x,41, i['tara'] if i['tara'] else 0, data_format_drgr)
				worksheet.write(x,42, i['peso_neto'] if i['peso_neto'] else 0, data_format_drgr)
				worksheet.write(x,43, i['peso_bruto'] if i['peso_bruto'] else 0, data_format_drgr)
				worksheet.write(x,44, i['precio_un'] if i['precio_un'] else 0, data_format_drgr)
				worksheet.write(x,45, i['valor_total'] if i['valor_total'] else 0, data_format_drgr)
			x += 1

		worksheet.write(x,38, ' ', empty_top)
		worksheet.write(x,39, ' ', empty_top)
		worksheet.write(x,40, ' ', empty_top)
		worksheet.write(x,41, ' ', empty_top)
		worksheet.write(x,42, ' ', empty_top)
		worksheet.write(x,43, ' ', empty_top)
		worksheet.write(x,44, ' ', empty_top)
		worksheet.write(x,45, ' ', empty_top)


		worksheet.set_column("BK:BK", 68.86)
		worksheet.set_column("BB:BB", 25.86)
		worksheet.set_column("BL:BL", 68.86)

		worksheet.merge_range("BB13:BB15", 'Fecha', merge_format_t32)
		worksheet.merge_range("BC13:BC15", 'Nro. OV', merge_format_t32)
		worksheet.merge_range("BD13:BD15", 'Saldo Inicial OV', merge_format_t32)
		worksheet.merge_range("BE13:BE15", 'Precio Unitario', merge_format_t32)
		worksheet.merge_range("BF13:BF15", 'Nro. Factura', merge_format_t32)
		worksheet.merge_range("BG13:BG15", u'Guía de Remisión', merge_format_t32)
		worksheet.merge_range("BH13:BH15", u'Guía de Transportista', merge_format_t32)
		worksheet.merge_range("BI13:BI15", 'Placa', merge_format_t32)
		worksheet.merge_range("BJ13:BJ15", 'Unidad', merge_format_t32)
		worksheet.merge_range("BK13:BK15", 'Transportista', merge_format_t32)
		worksheet.merge_range("BL13:BL15", 'Producto', merge_format_t32)
		worksheet.merge_range("BM13:BM15", 'Peso Bruto Kg.', merge_format_t32)
		worksheet.merge_range("BN13:BN15", 'Tara', merge_format_t32)
		worksheet.merge_range("BO13:BO15", 'Peso Neto Kg', merge_format_t32)
		worksheet.merge_range("BP13:BP15", 'Peso Neto en Tn', merge_format_t32)
		worksheet.merge_range("BQ13:BQ15", 'Saldo en Tn por OV', merge_format_t32)
		worksheet.merge_range("BR13:BR15", 'Densidad', merge_format_t32)
		worksheet.merge_range("BS13:BS15", 'Equivalente a M3', merge_format_t32)
		worksheet.merge_range("BT13:BT15", 'Saldo en M3', merge_format_t32)
		worksheet.merge_range("BU13:BU15", 'Sub Total', merge_format_t32)
		worksheet.merge_range("BV13:BV15", 'IGV 18%', merge_format_t32)
		worksheet.merge_range("BW13:BW15", 'Total', merge_format_t32)
		worksheet.merge_range("BX13:BX15", 'Observaciones', merge_format_t32)

		x = 15
		for i in range(len(scsg)):
			if i % 2 == 0:
				worksheet.write(x,53, scsg[i].date if scsg[i].date else '', data_format_dlr)
				worksheet.write(x,54, scsg[i].sale_id.name if scsg[i].sale_id.name else '', data_format_dr)
				worksheet.write(x,55, scsg[i].saldo_inicial if scsg[i].saldo_inicial else '', data_format_dr)
				worksheet.write(x,56, scsg[i].precio_un if scsg[i].precio_un else '', data_format_dr)
				worksheet.write(x,57, scsg[i].invoice_id.number if scsg[i].invoice_id.number else '', data_format_dr)
				worksheet.write(x,58, scsg[i].guia if scsg[i].guia else '', data_format_dr)
				worksheet.write(x,59, scsg[i].guia_trans if scsg[i].guia_trans else '', data_format_dr)
				worksheet.write(x,60, scsg[i].placa if scsg[i].placa else '', data_format_dr)
				worksheet.write(x,61, scsg[i].unidad if scsg[i].unidad else '', data_format_dr)
				worksheet.write(x,62, scsg[i].partner_id.name if scsg[i].partner_id.name else '', data_format_tlr)
				worksheet.write(x,63, scsg[i].product_id.name_template if scsg[i].product_id.name_template else '', data_format_tlr)
				worksheet.write(x,64, scsg[i].peso_bruto if scsg[i].peso_bruto else '', data_format_dr)
				worksheet.write(x,65, scsg[i].tara if scsg[i].tara else '', data_format_dr)
				worksheet.write(x,66, scsg[i].peso_neto if scsg[i].peso_neto else '', data_format_dr)
				worksheet.write(x,67, scsg[i].peso_neto_tn if scsg[i].peso_neto_tn else '', data_format_dr)
				worksheet.write(x,68, scsg[i].saldo_ton if scsg[i].saldo_ton else '', data_format_dr)
				worksheet.write(x,69, scsg[i].densidad if scsg[i].densidad else '', data_format_dr)
				worksheet.write(x,70, scsg[i].eq_m3 if scsg[i].eq_m3 else '', data_format_dr)
				worksheet.write(x,71, scsg[i].saldo_m3 if scsg[i].saldo_m3 else '', data_format_dr)
				worksheet.write(x,72, scsg[i].sub_total if scsg[i].sub_total else '', data_format_dr)
				worksheet.write(x,73, scsg[i].igv if scsg[i].igv else '', data_format_dr)
				worksheet.write(x,74, scsg[i].total if scsg[i].total else '', data_format_dr)
				worksheet.write(x,75, scsg[i].obs if scsg[i].obs else '', data_format_dr)
			else:
				worksheet.write(x,53, scsg[i].date if scsg[i].date else '', data_format_dlrgr)
				worksheet.write(x,54, scsg[i].sale_id.name if scsg[i].sale_id.name else '', data_format_drgr)
				worksheet.write(x,55, scsg[i].saldo_inicial if scsg[i].saldo_inicial else '', data_format_drgr)
				worksheet.write(x,56, scsg[i].precio_un if scsg[i].precio_un else '', data_format_drgr)
				worksheet.write(x,57, scsg[i].invoice_id.number if scsg[i].invoice_id.number else '', data_format_drgr)
				worksheet.write(x,58, scsg[i].guia if scsg[i].guia else '', data_format_drgr)
				worksheet.write(x,59, scsg[i].guia_trans if scsg[i].guia_trans else '', data_format_drgr)
				worksheet.write(x,60, scsg[i].placa if scsg[i].placa else '', data_format_drgr)
				worksheet.write(x,61, scsg[i].unidad if scsg[i].unidad else '', data_format_drgr)
				worksheet.write(x,62, scsg[i].partner_id.name if scsg[i].partner_id.name else '', data_format_tlrgr)
				worksheet.write(x,63, scsg[i].product_id.name_template if scsg[i].product_id.name_template else '', data_format_tlrgr)
				worksheet.write(x,64, scsg[i].peso_bruto if scsg[i].peso_bruto else '', data_format_drgr)
				worksheet.write(x,65, scsg[i].tara if scsg[i].tara else '', data_format_drgr)
				worksheet.write(x,66, scsg[i].peso_neto if scsg[i].peso_neto else '', data_format_drgr)
				worksheet.write(x,67, scsg[i].peso_neto_tn if scsg[i].peso_neto_tn else '', data_format_drgr)
				worksheet.write(x,68, scsg[i].saldo_ton if scsg[i].saldo_ton else '', data_format_drgr)
				worksheet.write(x,69, scsg[i].densidad if scsg[i].densidad else '', data_format_drgr)
				worksheet.write(x,70, scsg[i].eq_m3 if scsg[i].eq_m3 else '', data_format_drgr)
				worksheet.write(x,71, scsg[i].saldo_m3 if scsg[i].saldo_m3 else '', data_format_drgr)
				worksheet.write(x,72, scsg[i].sub_total if scsg[i].sub_total else '', data_format_drgr)
				worksheet.write(x,73, scsg[i].igv if scsg[i].igv else '', data_format_drgr)
				worksheet.write(x,74, scsg[i].total if scsg[i].total else '', data_format_drgr)
				worksheet.write(x,75, scsg[i].obs if scsg[i].obs else '', data_format_drgr)
			x += 1

		worksheet.write(x,53, ' ', empty_top)
		worksheet.write(x,54, ' ', empty_top)
		worksheet.write(x,55, ' ', empty_top)
		worksheet.write(x,56, ' ', empty_top)
		worksheet.write(x,57, ' ', empty_top)
		worksheet.write(x,58, ' ', empty_top)
		worksheet.write(x,59, ' ', empty_top)
		worksheet.write(x,60, ' ', empty_top)
		worksheet.write(x,61, ' ', empty_top)
		worksheet.write(x,62, ' ', empty_top)
		worksheet.write(x,63, ' ', empty_top)
		worksheet.write(x,64, ' ', empty_top)
		worksheet.write(x,65, ' ', empty_top)
		worksheet.write(x,66, ' ', empty_top)
		worksheet.write(x,67, ' ', empty_top)
		worksheet.write(x,68, ' ', empty_top)
		worksheet.write(x,69, ' ', empty_top)
		worksheet.write(x,70, ' ', empty_top)
		worksheet.write(x,71, ' ', empty_top)
		worksheet.write(x,72, ' ', empty_top)
		worksheet.write(x,73, ' ', empty_top)
		worksheet.write(x,74, ' ', empty_top)
		worksheet.write(x,75, ' ', empty_top)

		x += 2

		worksheet.merge_range(x,53,x,58, u'Resumen al Día', merge_format_t2)
		x += 1

		worksheet.write(x,53, u'Cliente', merge_format_t32)
		worksheet.write(x,54, u'Orden Venta', merge_format_t32)
		worksheet.write(x,55, u'Ton. Entregadas', merge_format_t32)
		worksheet.write(x,56, u'M3 Entregados', merge_format_t32)
		worksheet.write(x,57, u'Precio Unit.', merge_format_t32)
		worksheet.write(x,58, u'Monto por Tonelada', merge_format_t32)
		x += 1

		self.env.cr.execute("""
			select scsg.partner_id,
	        	   scsg.sale_id,
	       		   sum(scsg.peso_neto_tn) as peso_neto_tn,
	      		   sum(scsg.eq_m3) as eq_m3,
	       		   scsg.precio_un,
	       		   sum(scsg.peso_neto_tn) * scsg.precio_un as monto_por_tn
			from salida_cao_salida_grava scsg
			where year_id = """+str(yr)+""" and month_id = """+str(mnth)+"""
			group by scsg.partner_id,
	 				 scsg.sale_id,
	 				 scsg.date,
	 				 scsg.precio_un
			order by scsg.sale_id
		""")

		qry = self.env.cr.dictfetchall()

		for i in qry:
			if qry.index(i) % 2 == 0:
				rp = self.env['res.partner'].search([('id','=',i['partner_id'])])[0]
				worksheet.write(x,53, rp.name if rp.name else '', data_format_tlr)
				so = self.env['sale.order'].search([('id','=',i['sale_id'])])[0]
				worksheet.write(x,54, so.name if so.name else '', data_format_tlr)
				worksheet.write(x,55, i['peso_neto_tn'] if i['peso_neto_tn'] else '', data_format_dr)
				worksheet.write(x,56, i['eq_m3'] if i['eq_m3'] else '', data_format_dr)
				worksheet.write(x,57, i['precio_un'] if i['precio_un'] else '', data_format_dr)
				worksheet.write(x,58, i['monto_por_tn'] if i['monto_por_tn'] else '', data_format_dr)
			else:
				rp = self.env['res.partner'].search([('id','=',i['partner_id'])])[0]
				worksheet.write(x,53, rp.name if rp.name else '', data_format_tlrgr)
				so = self.env['sale.order'].search([('id','=',i['sale_id'])])[0]
				worksheet.write(x,54, so.name if so.name else '', data_format_tlrgr)
				worksheet.write(x,55, i['peso_neto_tn'] if i['peso_neto_tn'] else '', data_format_drgr)
				worksheet.write(x,56, i['eq_m3'] if i['eq_m3'] else '', data_format_drgr)
				worksheet.write(x,57, i['precio_un'] if i['precio_un'] else '', data_format_drgr)
				worksheet.write(x,58, i['monto_por_tn'] if i['monto_por_tn'] else '', data_format_drgr)
			x += 1

		worksheet.write(x,53, ' ', empty_top)
		worksheet.write(x,54, ' ', empty_top)
		worksheet.write(x,55, ' ', empty_top)
		worksheet.write(x,56, ' ', empty_top)
		worksheet.write(x,57, ' ', empty_top)
		worksheet.write(x,58, ' ', empty_top)

		workbook.close()
		
		f = open( direccion + u'Entradas_Salidas_Planta_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx', 'rb')
			
		vals = {
			'output_name': u'Entradas_Salidas_Planta_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx',
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