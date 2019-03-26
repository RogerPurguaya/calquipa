# -*- encoding: utf-8 -*-
import base64
from openerp import models, fields, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp

import calendar
import datetime
import decimal

class anivi_coke_pulverizado_combustible_solido(models.Model):
	_name = 'anivi.coke.pulverizado.combustible.solido'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')

	horas_operacion = fields.Float('Hrs Oper.')
	inventario_maez = fields.Float('Inventario Silo Maerz No. 1')
	tpd_real = fields.Float('TPD Prod. Real')
	tpd_nominal = fields.Float('TPH REAL')
	diesel = fields.Float('Consumo Diesel Gls')
	promedio_gls = fields.Float('Promedio Gls/Ton', compute="get_promedio_gls")
	energia = fields.Float('Consumo Energía Eléctrica')
	promedio_kwh = fields.Float('Promedio kwh/Ton', compute="get_promedio_kwh")
	calorifico = fields.Float('Poder Calorífico Percoke')
	malla = fields.Float('%  Finura Malla 170')
	humedad_entrada = fields.Float('%  Humedad Entrada')
	humedad_salida = fields.Float('%  Humedad Salida')

	# nuevas columnas 20180326

	coal_fuel_percent = fields.Float('% de Carbon en la Mezcla de Comustible %')
	coal_total = fields.Float('Consumo Total de Carbon (TN)', compute="get_coal_total")
	pet_coke_total = fields.Float('Consumo Total Pet Coke  (TN)', compute="get_petcoke_total")


	@api.one
	def get_coal_total(self):
		# que no es que no sepa usar los if en linea de python si no que me gusta más
		# usar los if clasicos es custion de gustos
		nres = 0
		if self.coal_fuel_percent:
			if self.coal_fuel_percent>0:
				nres = (self.tpd_real*(self.coal_fuel_percent/100)) 
		self.coal_total=nres

	@api.one
	def get_petcoke_total(self):
		nres = 0
		if self.tpd_real:
			if self.coal_total:
				nres = self.tpd_real-self.coal_total
		self.pet_coke_total=nres






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

	@api.one
	def get_promedio_gls(self):
		self.promedio_gls = (self.diesel / self.tpd_real) if self.tpd_real != 0 else 0

	@api.one
	def get_promedio_kwh(self):
		self.promedio_kwh = (self.promedio_gls / self.tpd_real) if self.tpd_real != 0 else 0

	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "anivi.coke.pulverizado.combustible.solido",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['anivi.coke.pulverizado.combustible.solido'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['anivi.coke.pulverizado.combustible.solido'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "anivi.coke.pulverizado.combustible.solido",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class anivi_coke_compra_insumos(models.Model):
	_name = 'anivi.coke.compra.insumos'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')

	vale_diesel = fields.Char(u'N° vale Diesel')
	diesel = fields.Float('Compra Diesel Gls.')

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
				"res_model": "anivi.coke.compra.insumos",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['anivi.coke.compra.insumos'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['anivi.coke.compra.insumos'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "anivi.coke.compra.insumos",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class anivi_coke_inventario_insumos(models.Model):
	_name = 'anivi.coke.inventario.insumos'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')

	diesel = fields.Float('Inventario Diesel Gls.', compute="compute_diesel")
	inv_diesel = fields.Float('Inventario Diesel Gls.', compute="compute_inv_diesel")

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

	@api.one
	def compute_inv_diesel(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		tid = self.env['anivi.coke.inventario.insumos'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(tid) > 0:
			tid = tid[-1]
			self.inv_diesel = tid.diesel
		else:
			self.inv_diesel = 0
			
		# prev_month = (self.month_id - 1) if self.month_id - 1 != 0 else 12
		# prev_year = (self.year_id - 1) if (self.month_id - 1) == 0 else self.year_id

		# tid = self.env['anivi.coke.inventario.insumos'].search([('month_id','=',prev_month),('year_id','=',prev_year)])
		# prev_total = 0
		# for i in tid:
		# 	prev_total += i.diesel

		# prev_total += tid[0].inv_diesel if len(tid) > 0 else 0
		# self.inv_diesel = prev_total

	@api.one
	def compute_diesel(self):
		sum_acii = 0
		for acii in self.env['anivi.coke.inventario.insumos'].search([]):
			acpcs = self.env['anivi.coke.pulverizado.combustible.solido'].search([('date','=',acii.date)])
			acci = self.env['anivi.coke.compra.insumos'].search([('date','=',acii.date)])
			if len(acci):
				sum_acii += acci[0].diesel
			if len(acpcs):
				sum_acii -= acpcs[0].diesel
			acii.diesel = sum_acii

		# acpcs = self.env['anivi.coke.pulverizado.combustible.solido'].search([('year_id','=',self.year_id),('month_id','=',self.month_id),('date','=',self.date)])
		# acci = self.env['anivi.coke.compra.insumos'].search([('year_id','=',self.year_id),('month_id','=',self.month_id),('date','=',self.date)])
		# if len(acpcs) > 0 and len(acci) > 0:
		# 	acpcs = acpcs[0]
		# 	acci = acci[0]
		# 	self.diesel = acci.diesel - acpcs.diesel
		# else:
		# 	self.diesel = 0

	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "anivi.coke.inventario.insumos",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['anivi.coke.inventario.insumos'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['anivi.coke.inventario.insumos'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "anivi.coke.inventario.insumos",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class anivi_coke_indicadores_operacion(models.Model):
	_name = 'anivi.coke.indicadores.operacion'

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
				"res_model": "anivi.coke.indicadores.operacion",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		
		conc = [(u'Objetivo Mes',u'Toneladas'),
				(u'Tendencia Mes',u'Toneladas'),
				(u'Acumulado Mes',u'Toneladas'),
				(u'Diferencia Objetivo vs Real',u'Toneladas'),
				(u'Objetivo de Hrs de Operación Mes',u'Horas'),
				(u'Hrs Empleadas Pulverizado',u'Horas'),
				(u'Promedio TPH',u'Tonelada por Hora'),
				(u'Promedio Día',u'Toneladas'),
				(u'Días de Producción',u'Días'),
				(u'Promedio de Humedad de Entrada',u'%'),
				(u'Promedio de Humedad de Salida',u'%'),
				(u'Promedio Finura Malla 170',u'%'),				
				(u'Promedio Poder Calorifico',u'[]'),
				(u'Promedio Consumo Diesel',u'Gls/Ton'),
				(u'Promedio Consumo Energia ',u'Kwh/Ton'),]
		dias_mes = calendar.monthrange(yr, mnth)[1]

		acio = self.env['anivi.coke.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth)])
		if len(acio) == 0:
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
					res = self.env['anivi.coke.funciones'].get_tpd_real(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = om-res

				if vals['concepto'] == conc[2][0]:
					vals['cantidad'] = self.env['anivi.coke.funciones'].get_tpd_real(mnth, yr)

				if vals['concepto'] == conc[3][0]:
					res = self.env['anivi.coke.funciones'].get_tpd_real(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = om-res

				if vals['concepto'] == conc[4][0]:
					vals['cantidad'] = oh

				if vals['concepto'] == conc[5][0]:
					re = self.env['anivi.coke.funciones'].get_tpd_real(mnth, yr)
					no = self.env['anivi.coke.funciones'].get_tpd_nominal(mnth, yr)
					vals['cantidad'] = 0

				if vals['concepto'] == conc[6][0]:
					acpcs = len(self.env['anivi.coke.pulverizado.combustible.solido'].search([('year_id','=',yr),('month_id','=',mnth)]))
					gtn = self.env['anivi.coke.funciones'].get_tpd_nominal(mnth, yr)
					if gtn == None:
						gtn = 0 
					vals['cantidad'] = (gtn / float(acpcs)) if acpcs != 0 else 0

				if vals['concepto'] == conc[7][0]:
					acpcs = len(self.env['anivi.coke.pulverizado.combustible.solido'].search([('year_id','=',yr),('month_id','=',mnth)]))
					gtr = self.env['anivi.coke.funciones'].get_tpd_real(mnth, yr)
					if gtr == None:
						gtr = 0
					vals['cantidad'] = (gtr / float(acpcs)) if acpcs != 0 else 0

				if vals['concepto'] == conc[8][0]:					
					vals['cantidad'] = acpcs = len(self.env['anivi.coke.pulverizado.combustible.solido'].search([('year_id','=',yr),('month_id','=',mnth)]))

				if vals['concepto'] == conc[9][0]:					
					vals['cantidad'] = 0

				if vals['concepto'] == conc[10][0]:					
					vals['cantidad'] = 0

				if vals['concepto'] == conc[11][0]:					
					vals['cantidad'] = 0

				if vals['concepto'] == conc[12][0]:					
					vals['cantidad'] = 0

				if vals['concepto'] == conc[13][0]:					
					vals['cantidad'] = 0

				if vals['concepto'] == conc[14][0]:					
					vals['cantidad'] = 0

				nacio = self.env['anivi.coke.indicadores.operacion'].create(vals)
		else:		
			for i in acio:
				i.dias_transcurridos = dt
				if i.concepto == conc[0][0]:
					i.cantidad = om
				if i.concepto == conc[4][0]:
					i.cantidad = oh

		return {
			"type": "ir.actions.act_window",
			"res_model": "anivi.coke.indicadores.operacion",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class anivi_coke_funciones(models.Model):
	_name = 'anivi.coke.funciones'

	def get_tpd_real(self, mnth, yr):
		self.env.cr.execute("""
			select sum(tpd_real) from anivi_coke_pulverizado_combustible_solido
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_horas_operacion(self, mnth, yr):
		self.env.cr.execute("""
			select sum(horas_operacion) from anivi_coke_pulverizado_combustible_solido
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_tpd_nominal(self, mnth, yr):
		self.env.cr.execute("""
			select sum(tpd_nominal) from anivi_coke_pulverizado_combustible_solido
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_diesel(self, mnth, yr):
		self.env.cr.execute("""
			select sum(diesel) from anivi_coke_pulverizado_combustible_solido
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

class anivi_coke_reporte(models.Model):
	_name = 'anivi.coke.reporte'

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
		workbook = Workbook( direccion + u'Anivi_Coke_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx')
		worksheet = workbook.add_worksheet("Anivi_Coke")

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


		worksheet.set_column("A:A", 3.86)
		# worksheet.set_column("O:O", 3.86)
		# worksheet.set_column("S:S", 3.86)

		worksheet.merge_range("B2:D8", '', merge_format_t)
		worksheet.merge_range("E2:S8", u'Calquipa', merge_format_t)
		worksheet.merge_range("T2:V2", u'Fecha:', merge_format_ca)
		worksheet.merge_range("W2:X2", datetime.datetime.today().strftime("%Y-%m-%d"), merge_format_ca2)
		worksheet.merge_range("T3:V3", u'Mes:', merge_format_ca)
		worksheet.merge_range("W3:X3", month2name[mnth], merge_format_ca2)
		worksheet.merge_range("T4:V4", u'Días de Mes:', merge_format_ca)
		worksheet.merge_range("W4:X4", calendar.monthrange(yr,mnth)[1], merge_format_ca2)
		worksheet.merge_range("T5:V5", u'Días Transcurridos Mes:', merge_format_ca)

		acio = self.env['anivi.coke.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
		if len(acio) > 0:
			acio = acio[0]
			worksheet.merge_range("W5:X5", acio.dias_transcurridos, merge_format_ca2)
		else:
			worksheet.merge_range("W5:X5", '', merge_format_ca2)

		worksheet.merge_range("T6:V6", u'Hrs Mes:', merge_format_ca)
		worksheet.merge_range("W6:X6", u'', merge_format_ca2)
		worksheet.merge_range("T7:V7", u'Clave SGI', merge_format_ca)
		worksheet.merge_range("W7:X7", u'', merge_format_ca2)
		worksheet.merge_range("T8:V8", u'Folio', merge_format_ca)
		worksheet.merge_range("W8:X8", u'', merge_format_ca2)

		worksheet.insert_image('B3', 'calquipalright.png', {'x_scale': 0.85, 'y_scale': 0.85, 'x_offset':4})
		worksheet.insert_image('E3', 'calquipalleft.png', {'x_scale': 0.85, 'y_scale': 0.85, 'x_offset':4})

		worksheet.set_row(9, 21)
		worksheet.merge_range("B10:X10", u'Reporte de Combustible Sólido', merge_format_t)

		worksheet.set_row(11, 20)
		worksheet.merge_range("B12:Q12", u'Pulverizado de Combustible Sólido', merge_format_t2)
		#worksheet.merge_range("P12:Q12", u'Compra de Insumos', merge_format_t2)
		#worksheet.merge_range("S12:T12", u'Inventario de Insumos', merge_format_t2)

		worksheet.set_row(12, 20.25)
		worksheet.set_row(13, 33)
		worksheet.set_row(14, 12)
		worksheet.merge_range("B13:B15", u'Fecha', merge_format_t31)
		worksheet.merge_range("C13:C15", u'Hrs Op', merge_format_t32)
		worksheet.merge_range("D13:D15", u'Inventario Silo Maerz No. 1', merge_format_t32)
		worksheet.merge_range("E13:E15", u'TPD Prod. Real', merge_format_t32)
		worksheet.merge_range("F13:F15", u'TPH REAL', merge_format_t32)
		

		worksheet.merge_range("G13:G15", u'% de Carbon en Mezcla Comustible %', merge_format_t32)
		worksheet.merge_range("H13:H15", u'Consumo Total de Carbon (TN)', merge_format_t32)
		worksheet.merge_range("I13:I15", u'Consumo Total Pet Coke (TN)', merge_format_t32)



		worksheet.merge_range("J13:J15", u'Consumo Diesel Gls', merge_format_t32)
		worksheet.merge_range("K13:K15", u'Promedio Gls/Ton', merge_format_t32)
		worksheet.merge_range("L13:L15", u'Consumo Energía Elec', merge_format_t32)
		worksheet.merge_range("M13:M15", u'Promedio kwh/Ton', merge_format_t32)
		worksheet.merge_range("N13:N15", u'Poder Calorífico Petcoke', merge_format_t32)
		worksheet.merge_range("O13:O15", u'%  Finura Malla 170', merge_format_t32)
		worksheet.merge_range("P13:P15", u'%  Humedad Entrada', merge_format_t32)
		worksheet.merge_range("Q13:Q15", u'%  Humedad Salida', merge_format_t32)

		worksheet.merge_range("S13:S15", u'Fecha', merge_format_t31)
		worksheet.merge_range("T13:T15", u'N° vale Diesel', merge_format_t32)
		worksheet.merge_range("U13:U15", u'Compra Diesel', merge_format_t32)

		worksheet.merge_range("W13:W14", u'Fecha', merge_format_t31)
		worksheet.merge_range("X13:X14", u'Inventario Diesel', merge_format_t32)

		pacii = self.env['anivi.coke.inventario.insumos'].search([('year_id','=',yr),('month_id','=',mnth)])
		worksheet.write("W15", u'Inv. Inicial', merge_format_t31)
		worksheet.write("X15", pacii[0].inv_diesel if len(pacii) > 0 else 0, data_format_drgr)

		acpcs = self.env['anivi.coke.pulverizado.combustible.solido'].search([('year_id','=',yr),('month_id','=',mnth)])
		acci = self.env['anivi.coke.compra.insumos'].search([('year_id','=',yr),('month_id','=',mnth)])
		acii = self.env['anivi.coke.inventario.insumos'].search([('year_id','=',yr),('month_id','=',mnth)])
		acio = self.env['anivi.coke.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])

		print len(acpcs),len(acio),len(acci),len(acii)
		if len(acpcs) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de PULVERIZADO DE COMBUSTIBLE SOLIDO para el periodo seleccionado.")
		if len(acio) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de INDICADORES DE OPERACION para el periodo seleccionado.")
		if len(acci) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de COMPRA DE INSUMOS para el periodo seleccionado.")
		if len(acii) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de INVENTARIO DE INSUMOS para el periodo seleccionado.")
		

		sum_acpcs = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		sum_acci = [0]
		sum_acii = [0]

		sum_acii[0] = acii[0].inv_diesel if len(acii) > 0 else 0 

		x = 15
		for i in range(len(acpcs)):
			fch = format(i+1,'02')+'-'+month2name[mnth][:3]
			worksheet.write(x,1, fch, data_format_dlr)
			worksheet.write(x,18, fch, data_format_dlr)
			worksheet.write(x,22, fch, data_format_dlr)
			if i % 2 == 0:
				worksheet.write(x,2, acpcs[i].horas_operacion, data_format_d)
				worksheet.write(x,3, acpcs[i].inventario_maez, data_format_d)
				worksheet.write(x,4, acpcs[i].tpd_real, data_format_d)
				worksheet.write(x,5, acpcs[i].tpd_nominal, data_format_dr)
				# coal_fuel_percent = fields.Float('% de Carbon en la Mezcla de Comustible %')
				# coal_total = fields.Float('Consumo Total de Carbon (TN)', compute="get_coal_total")
				# pet_coke_total = fields.Float('Consumo Total Pet Coke  (TN)', compute="get_petcoke_total")

				worksheet.write(x,6, acpcs[i].coal_fuel_percent, data_format_d)
				worksheet.write(x,7, acpcs[i].coal_total, data_format_d)
				worksheet.write(x,8, acpcs[i].pet_coke_total, data_format_dr)



				worksheet.write(x,9, acpcs[i].diesel, data_format_d)
				worksheet.write(x,10, acpcs[i].promedio_gls, data_format_d)
				worksheet.write(x,11, acpcs[i].energia, data_format_d)
				worksheet.write(x,12, acpcs[i].promedio_kwh, data_format_dr)
				worksheet.write(x,13, acpcs[i].calorifico, data_format_d)
				worksheet.write(x,14, acpcs[i].malla, data_format_d)
				worksheet.write(x,15, acpcs[i].humedad_entrada, data_format_d)
				worksheet.write(x,16, acpcs[i].humedad_salida, data_format_dr)

				worksheet.write(x,19, acci[i].vale_diesel if acci[i].vale_diesel else '', data_format_dr)
				worksheet.write(x,20, acci[i].diesel, data_format_dr)

				worksheet.write(x,23, acii[i].diesel, data_format_dr)

			else:
				worksheet.write(x,2, acpcs[i].horas_operacion, data_format_dgr)
				worksheet.write(x,3, acpcs[i].inventario_maez, data_format_dgr)
				worksheet.write(x,4, acpcs[i].tpd_real, data_format_dgr)
				worksheet.write(x,5, acpcs[i].tpd_nominal, data_format_drgr)

				worksheet.write(x,6, acpcs[i].coal_fuel_percent, data_format_dgr)
				worksheet.write(x,7, acpcs[i].coal_total, data_format_dgr)
				worksheet.write(x,8, acpcs[i].pet_coke_total, data_format_drgr)

				worksheet.write(x,9, acpcs[i].diesel, data_format_dgr)
				worksheet.write(x,10, acpcs[i].promedio_gls, data_format_dgr)
				worksheet.write(x,11, acpcs[i].energia, data_format_dgr)
				worksheet.write(x,12, acpcs[i].promedio_kwh, data_format_drgr)
				worksheet.write(x,13, acpcs[i].calorifico, data_format_dgr)
				worksheet.write(x,14, acpcs[i].malla, data_format_dgr)
				worksheet.write(x,15, acpcs[i].humedad_entrada, data_format_dgr)
				worksheet.write(x,16, acpcs[i].humedad_salida, data_format_drgr)

				worksheet.write(x,19, acci[i].vale_diesel if acci[i].vale_diesel else '', data_format_drgr)
				worksheet.write(x,20, acci[i].diesel, data_format_drgr)

				worksheet.write(x,23, acii[i].diesel, data_format_drgr)			
			
			sum_acpcs[0] += acpcs[i].horas_operacion
			sum_acpcs[1] += acpcs[i].inventario_maez
			sum_acpcs[2] += acpcs[i].tpd_real
			sum_acpcs[3] += acpcs[i].tpd_nominal

			sum_acpcs[4] += acpcs[i].coal_fuel_percent
			sum_acpcs[5] += acpcs[i].coal_total
			sum_acpcs[6] += acpcs[i].pet_coke_total

			sum_acpcs[7] += acpcs[i].diesel
			sum_acpcs[8] += acpcs[i].promedio_gls
			sum_acpcs[10] += acpcs[i].energia
			sum_acpcs[11] += acpcs[i].promedio_kwh
			sum_acpcs[12] += acpcs[i].calorifico
			sum_acpcs[0] += acpcs[i].malla
			sum_acpcs[13] += acpcs[i].humedad_entrada
			sum_acpcs[14] += acpcs[i].humedad_salida

			sum_acci[0] += acci[i].diesel

			sum_acii[0] += acii[i].diesel

			x += 1

		worksheet.write(x,1, u'Totales', data_format_total)
		worksheet.write(x,2, sum_acpcs[0], data_format_total)
		worksheet.write(x,3, sum_acpcs[1], data_format_total)
		worksheet.write(x,4, sum_acpcs[2], data_format_total)
		worksheet.write(x,5, sum_acpcs[3], data_format_total)
		worksheet.write(x,6, sum_acpcs[4], data_format_total)
		worksheet.write(x,7, sum_acpcs[5], data_format_total)
		worksheet.write(x,8, sum_acpcs[6], data_format_total)
		worksheet.write(x,9, sum_acpcs[7], data_format_total)
		worksheet.write(x,10, sum_acpcs[8], data_format_total)
		worksheet.write(x,11, sum_acpcs[9], data_format_total)
		worksheet.write(x,12, sum_acpcs[10], data_format_total)
		worksheet.write(x,13, sum_acpcs[11], data_format_total)

		worksheet.write(x,14, sum_acpcs[12], data_format_total)
		worksheet.write(x,15, sum_acpcs[13], data_format_total)
		worksheet.write(x,16, sum_acpcs[14], data_format_total)

		worksheet.write(x,18, u'Totales', data_format_total)
		worksheet.write(x,19, ' ', data_format_total)
		worksheet.write(x,20, sum_acci[0], data_format_total)

		worksheet.write(x,22, u'Totales', data_format_total)
		worksheet.write(x,23, sum_acii[0], data_format_total)

		x = 48

		worksheet.merge_range(x,2,x,13, u'Indicadores de Operación', merge_format_t32)
		x+=1
		worksheet.merge_range(x,2,x,5, u'Concepto', merge_format_t32)
		worksheet.merge_range(x,6,x,11, u'Cantidad', merge_format_t32)
		worksheet.merge_range(x,12,x,13, u'Unidades', merge_format_t32)

		x += 1
		tio = self.env['anivi.coke.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
		for i in range(len(tio)):
			if i % 2 == 0:
				if i == len(tio)-1:
					worksheet.merge_range(x,2,x,5, tio[i].concepto, data_format_dlrd)
					worksheet.merge_range(x,6,x,11, tio[i].cantidad, data_format_dlrd)
					worksheet.merge_range(x,12,x,13, tio[i].unidades, data_format_dlrd)

				else:
					worksheet.merge_range(x,2,x,5, tio[i].concepto, data_format_dlr)
					if i == 0:
						worksheet.merge_range(x,6,x,11, tio[i].cantidad, data_format_dlrg)
					else:
						worksheet.merge_range(x,6,x,11, tio[i].cantidad, data_format_dlr)
					worksheet.merge_range(x,12,x,13, tio[i].unidades, data_format_dlr)
			else:
				if i == len(tio)-1:
					worksheet.merge_range(x,2,x,5, tio[i].concepto, data_format_dlrdgr)
					worksheet.merge_range(x,6,x,11, tio[i].cantidad, data_format_dlrdgr)
					worksheet.merge_range(x,12,x,13, tio[i].unidades, data_format_dlrdgr)
				else:
					worksheet.merge_range(x,2,x,5, tio[i].concepto, data_format_dlrgr)
					if i == 0 or i == 4:
						worksheet.merge_range(x,6,x,11, tio[i].cantidad, data_format_dlrg)
					else:
						worksheet.merge_range(x,6,x,11, tio[i].cantidad, data_format_dlrgr)
					worksheet.merge_range(x,12,x,13, tio[i].unidades, data_format_dlrgr)
			x += 1

		workbook.close()
		
		f = open( direccion + u'Anivi_Coke_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx', 'rb')
			
		vals = {
			'output_name': u'Anivi_Coke_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx',
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