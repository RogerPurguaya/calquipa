# -*- encoding: utf-8 -*-
import base64
from openerp import models, fields, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp

import calendar
import datetime
import decimal

class maerz_calcinacion(models.Model):
	_name = 'maerz.calcinacion'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')
	horas_operacion = fields.Float(u'Horas Operación', compute="get_horas_operacion")
	ton_caco3 = fields.Float(u'Toneladas Ca CO3')
	ton_cao = fields.Float(u'Toneladas Ca O')
	ton_cao_debajo = fields.Float(u'Toneladas Ca O debajo >')
	porc_cao_debajo = fields.Float(u'% de CaO por debajo')
	prod_nominal = fields.Float(u'Prod. Nominal')
	coke_pulv = fields.Float(u'Kgs Coke Pulverizado')
	consumo_coke_kgs = fields.Float(u'Consumo Total Coke kgs', compute="get_consumo_coke_kgs")
	consumo_mcal = fields.Float(u'Consumo Total Mcal', compute="get_consumo_mcal")
	consumo_ton_cao = fields.Float(u'Consumo Total Ton/CaO', compute="get_consumo_ton_cao")
	mcal_ton = fields.Float(u'Mcal / Ton, CaO', compute="get_mcal_ton")
	kwh_total = fields.Float(u'kwh Total')
	kwh_ton = fields.Float(u'kwh / Ton')
	ppc = fields.Float(u'PPC')
	cao_disp = fields.Float(u'%  CaO Disponible')
	cao_total = fields.Float(u'%  CaO Total')
	reactividad = fields.Float(u'Reactividad')
	pc_polvos = fields.Float(u'%  PC Polvos')

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
	def get_horas_operacion(self):
		self.horas_operacion = (self.ton_cao / self.prod_nominal * 24) if self.prod_nominal != 0 else 0

	@api.one
	def get_consumo_coke_kgs(self):
		self.consumo_coke_kgs = self.coke_pulv

	@api.one
	def get_consumo_mcal(self):
		self.consumo_mcal = self.consumo_coke_kgs*8

	@api.one
	def get_consumo_ton_cao(self):
		self.consumo_ton_cao = (self.consumo_coke_kgs / self.ton_cao) if self.ton_cao != 0 else 0

	@api.one
	def get_mcal_ton(self):
		self.mcal_ton = (self.consumo_coke_kgs / self.consumo_mcal) if self.consumo_mcal != 0 else 0

	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "maerz.calcinacion",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['maerz.calcinacion'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['maerz.calcinacion'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "maerz.calcinacion",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class compra_diesel(models.Model):
	_name = 'compra.diesel'

	_rec_name = 'date'
	_order    = 'date'

	year_id  = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date    = fields.Date('Fecha')
	vale_qas_500 = fields.Char(u'N° vale QAS 500 1')
	qas_500 = fields.Float(u'Generador QAS 500 1')
	vale_qas_115 = fields.Char(u'N° vale QAS 500')
	qas_115 = fields.Float(u'Generador QAS 115')
	vale_heli = fields.Char(u'N° vale Montacargas HELI')
	heli    = fields.Float(u'Montacargas HELI')
	vale_cat = fields.Char(u'N° vale CAT DP 30 NM')
	cat     = fields.Float(u'Montacargas CAT DP 30 NM')

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
		print mnth,yr
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "compra.diesel",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['compra.diesel'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['compra.diesel'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "compra.diesel",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class consumo_diesel(models.Model):
	_name = 'consumo.diesel'

	_rec_name = 'date'
	_order    = 'date'

	year_id  = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date    = fields.Date('Fecha')
	qas_500 = fields.Float(u'Generador QAS 500 1')
	qas_115 = fields.Float(u'Generador QAS 115')
	heli    = fields.Float(u'Montacargas HELI')
	cat     = fields.Float(u'Montacargas CAT DP 30 NM')

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
				"res_model": "consumo.diesel",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['consumo.diesel'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['consumo.diesel'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "consumo.diesel",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class saldos_diesel(models.Model):
	_name = 'saldos.diesel'

	_rec_name = 'date'
	_order    = 'date'

	year_id  = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date    = fields.Date('Fecha')
	qas_500 = fields.Float(u'Generador QAS 500 1', compute="compute_qas_500")
	qas_115 = fields.Float(u'Generador QAS 115', compute="compute_qas_115")
	heli    = fields.Float(u'Montacargas HELI', compute="compute_heli")
	cat     = fields.Float(u'Montacargas CAT DP 30 NM', compute="compute_cat")

	"""           INVENTARIO INCIAL           """
	inv_qas_500 = fields.Float(u'Generador QAS 500 1', compute="compute_inv_qas_500")
	inv_qas_115 = fields.Float(u'Generador QAS 115', compute="compute_inv_qas_115")
	inv_heli    = fields.Float(u'Montacargas HELI', compute="compute_inv_heli")
	inv_cat     = fields.Float(u'Montacargas CAT DP 30 NM', compute="compute_inv_cat")

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
	def compute_inv_qas_500(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		sd = self.env['saldos.diesel'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(sd) > 0:
			sd = sd[-1]
			self.inv_qas_500 = sd.qas_500
		else:
			self.inv_qas_500 = 0

	@api.one
	def compute_inv_qas_115(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		sd = self.env['saldos.diesel'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(sd) > 0:
			sd = sd[-1]
			self.inv_qas_115 = sd.qas_115
		else:
			self.inv_qas_115 = 0

	@api.one
	def compute_inv_heli(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		sd = self.env['saldos.diesel'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(sd) > 0:
			sd = sd[-1]
			self.inv_heli = sd.heli
		else:
			self.inv_heli = 0

	@api.one
	def compute_inv_cat(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		sd = self.env['saldos.diesel'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(sd) > 0:
			sd = sd[-1]
			self.inv_cat = sd.cat
		else:
			self.inv_cat = 0

	@api.multi
	def compute_qas_500(self):
		sum_sd = 0
		for sd in self.env['saldos.diesel'].search([]):
			cmd = self.env['compra.diesel'].search([('date','=',sd.date)])
			cnd = self.env['consumo.diesel'].search([('date','=',sd.date)])
			if len(cmd):
				sum_sd += cmd[0].qas_500
			if len(cnd):
				sum_sd -= cnd[0].qas_500
			sd.qas_500 = sum_sd

	@api.multi
	def compute_qas_115(self):
		sum_sd = 0
		for sd in self.env['saldos.diesel'].search([]):
			cmd = self.env['compra.diesel'].search([('date','=',sd.date)])
			cnd = self.env['consumo.diesel'].search([('date','=',sd.date)])
			if len(cmd):
				sum_sd += cmd[0].qas_115
			if len(cnd):
				sum_sd -= cnd[0].qas_115
			sd.qas_115 = sum_sd

	@api.multi
	def compute_heli(self):
		sum_sd = 0
		for sd in self.env['saldos.diesel'].search([]):
			cmd = self.env['compra.diesel'].search([('date','=',sd.date)])
			cnd = self.env['consumo.diesel'].search([('date','=',sd.date)])
			if len(cmd):
				sum_sd += cmd[0].heli
			if len(cnd):
				sum_sd -= cnd[0].heli
			sd.heli = sum_sd

	@api.multi
	def compute_cat(self):
		sum_sd = 0
		for sd in self.env['saldos.diesel'].search([]):
			cmd = self.env['compra.diesel'].search([('date','=',sd.date)])
			cnd = self.env['consumo.diesel'].search([('date','=',sd.date)])
			if len(cmd):
				sum_sd += cmd[0].cat
			if len(cnd):
				sum_sd -= cnd[0].cat
			sd.cat = sum_sd

	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "saldos.diesel",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['saldos.diesel'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['saldos.diesel'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "saldos.diesel",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class maerz_funciones(models.Model):
	_name = 'maerz.funciones'

	def get_ton_cao(self, mnth, yr):
		self.env.cr.execute("""
			select sum(ton_cao) from maerz_calcinacion
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

class maerz_indicadores_operacion(models.Model):
	_name = 'maerz.indicadores.operacion'

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
				"res_model": "maerz.indicadores.operacion",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		
		conc = [(u'Objetivo Mes',u'Toneladas'),
				(u'Tendencia Mes',u'Toneladas'),
				(u'Acumulado Mes',u'Toneladas'),
				(u'Diferencia Objetivo vs Real',u'Toneladas'),
				(u'Objetivo de Hrs de Operación Mes',u'Horas'),
				(u'Hrs Empleadas Calcinación',u'Horas'),
				(u'Promedio TPH',u'Tonelada por Hora'),
				(u'Promedio Día',u'Toneladas'),
				(u'Días de Producción',u'Días'),
				(u'Días Dentro de Calidad',u'[-]'),
				(u'Promedio Calidad CaO',u'%'),
				(u'Promedio PPC',u'[-]'),				
				(u'Promedio Consumo Conbustible',u'Mcal/Ton'),
				(u'Promedio Consumo Conbustible',u'kgs/Ton'),
				(u'Promedio Consumo Energía',u'kwh/Ton'),
				(u'Promedio Consumo Diesel',u'Galones'),]
		dias_mes = calendar.monthrange(yr, mnth)[1]

		mio = self.env['maerz.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth)])
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
					res = self.env['maerz.funciones'].get_ton_cao(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = om-res

				if vals['concepto'] == conc[2][0]:
					vals['cantidad'] = 0

				if vals['concepto'] == conc[3][0]:
					res = self.env['maerz.funciones'].get_ton_cao(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = om-res

				if vals['concepto'] == conc[4][0]:
					vals['cantidad'] = oh

				if vals['concepto'] == conc[5][0]:
					vals['cantidad'] = 0

				if vals['concepto'] == conc[6][0]:
					vals['cantidad'] = 0

				if vals['concepto'] == conc[7][0]:
					res = self.env['maerz.funciones'].get_ton_cao(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = (res / dias_mes) if dias_mes != 0 else 0

				if vals['concepto'] == conc[8][0]:
					vals['cantidad'] = dias_mes

				if vals['concepto'] == conc[9][0]:
					mc = self.env['maerz.calcinacion'].search([('year_id','=',yr),('month_id','=',mnth)])
					cont = 0
					for i in mc:
						if i.cao_total > 85:
							cont += 1
					vals['cantidad'] = cont

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

				if vals['concepto'] == conc[15][0]:
					vals['cantidad'] = 0

				nmio = self.env['maerz.indicadores.operacion'].create(vals)
		else:		
			for i in mio:
				i.dias_transcurridos = dt
				if i.concepto == conc[0][0]:
					i.cantidad = om
				if i.concepto == conc[4][0]:
					i.cantidad = oh

		return {
			"type": "ir.actions.act_window",
			"res_model": "maerz.indicadores.operacion",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class maerz_reporte(models.Model):
	_name = 'maerz.reporte'

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
		workbook = Workbook( direccion + u'Maerz_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx')
		worksheet = workbook.add_worksheet("Maerz")

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
		worksheet.set_column("T:T", 3.86)
		worksheet.set_column("AD:AD", 3.86)
		worksheet.set_column("AJ:AJ", 3.86)

		worksheet.merge_range("B2:D8", '', merge_format_t)
		worksheet.merge_range("E2:AJ8", u'Calquipa', merge_format_t)
		worksheet.merge_range("AK2:AM2", u'Fecha:', merge_format_ca)
		worksheet.merge_range("AN2:AO2", datetime.datetime.today().strftime("%Y-%m-%d"), merge_format_ca2)
		worksheet.merge_range("AK3:AM3", u'Mes:', merge_format_ca)
		worksheet.merge_range("AN3:AO3", month2name[mnth], merge_format_ca2)
		worksheet.merge_range("AK4:AM4", u'Días de Mes:', merge_format_ca)
		worksheet.merge_range("AN4:AO4", calendar.monthrange(yr,mnth)[1], merge_format_ca2)
		worksheet.merge_range("AK5:AM5", u'Días Transcurridos Mes:', merge_format_ca)

		acio = self.env['maerz.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
		if len(acio) > 0:
			acio = acio[0]
			worksheet.merge_range("AN5:AO5", acio.dias_transcurridos, merge_format_ca2)
		else:
			worksheet.merge_range("AN5:AO5", '', merge_format_ca2)

		worksheet.merge_range("AK6:AM6", u'Hrs Mes:', merge_format_ca)
		worksheet.merge_range("AN6:AO6", u'', merge_format_ca2)
		worksheet.merge_range("AK7:AM7", u'Clave SGI', merge_format_ca)
		worksheet.merge_range("AN7:AO7", u'', merge_format_ca2)
		worksheet.merge_range("AK8:AM8", u'Folio', merge_format_ca)
		worksheet.merge_range("AN8:AO8", u'', merge_format_ca2)

		worksheet.insert_image('B3', 'calquipalright.png', {'x_scale': 0.85, 'y_scale': 0.85, 'x_offset':4})
		worksheet.insert_image('E3', 'calquipalleft.png', {'x_scale': 0.85, 'y_scale': 0.85, 'x_offset':4})

		worksheet.set_row(9, 21)
		worksheet.merge_range("B10:AO10", u'Maerz', merge_format_t)

		worksheet.set_row(11, 20)
		worksheet.merge_range("B12:T12", u'Calcinación', merge_format_t2)
		worksheet.merge_range("V12:AD12", u'Compras de Diesel y GSL', merge_format_t2)
		worksheet.merge_range("AF12:AJ12", u'Consumos de Diesel y GSL', merge_format_t2)
		worksheet.merge_range("AL12:AP12", u'Saldos de Diesel y GSL', merge_format_t2)

		worksheet.set_row(12, 20.25)
		worksheet.set_row(13, 33)
		worksheet.set_row(14, 12)
		worksheet.merge_range("B13:B15", u'Fecha', merge_format_t31)
		worksheet.merge_range("C13:C15", u'Hrs Op', merge_format_t32)
		worksheet.merge_range("D13:D15", u'Toneladas Ca CO3', merge_format_t32)
		worksheet.merge_range("E13:E15", u'Toneladas Ca O', merge_format_t32)
		worksheet.merge_range("F13:F15", u'Toneladas Ca O debajo >', merge_format_t32)
		worksheet.merge_range("G13:G15", u'%  de Cao por debajo', merge_format_t32)
		worksheet.merge_range("H13:H15", u'Prod. Nominal', merge_format_t32)
		worksheet.merge_range("I13:I15", u'Kgs Coke Pulverizado', merge_format_t32)
		worksheet.merge_range("J13:J15", u'Consumo Total Coke kgs', merge_format_t32)
		worksheet.merge_range("K13:K15", u'Consumo Total Mcal', merge_format_t32)
		worksheet.merge_range("L13:L15", u'Consumo Total Ton/CaO', merge_format_t32)
		worksheet.merge_range("M13:M15", u'Mcal / Ton, CaO', merge_format_t32)
		worksheet.merge_range("N13:N15", u'kwh Total', merge_format_t32)
		worksheet.merge_range("O13:O15", u'kwh / Ton', merge_format_t32)
		worksheet.merge_range("P13:P15", u'PPC', merge_format_t32)
		worksheet.merge_range("Q13:Q15", u'%  CaO Disponible', merge_format_t32)
		worksheet.merge_range("R13:R15", u'%  CaO Total', merge_format_t32)
		worksheet.merge_range("S13:S15", u'Reactividad', merge_format_t32)
		worksheet.merge_range("T13:T15", u'%  PC Polvos', merge_format_t32)

		worksheet.merge_range("V13:V15", 'Fecha', merge_format_t31)
		worksheet.merge_range("W13:W15", u'N° vale QAS 500 1', merge_format_t32)
		worksheet.merge_range("X13:X15", u'Generador QAS 500 1', merge_format_t32)
		worksheet.merge_range("Y13:Y15", u'N° vale QAS 500', merge_format_t32)
		worksheet.merge_range("Z13:Z15", u'Generador QAS 115', merge_format_t32)
		worksheet.merge_range("AA13:AA15", u'N° vale Montacargas HELI', merge_format_t32)
		worksheet.merge_range("AB13:AB15", u'Montacargas HELI', merge_format_t32)
		worksheet.merge_range("AC13:AC15", u'N° vale CAT DP 30 NM', merge_format_t32)
		worksheet.merge_range("AD13:AD15", u'Montacargas CAT DP 30 NM', merge_format_t32)

		worksheet.merge_range("AF13:AF15", 'Fecha', merge_format_t31)
		worksheet.merge_range("AG13:AG15", u'Generador QAS 500 1', merge_format_t32)
		worksheet.merge_range("AH13:AH15", u'Generador QAS 115', merge_format_t32)
		worksheet.merge_range("AI13:AI15", u'Montacargas HELI', merge_format_t32)
		worksheet.merge_range("AJ13:AJ15", u'Montacargas CAT DP 30 NM', merge_format_t32)

		worksheet.merge_range("AL13:AL14", 'Fecha', merge_format_t31)
		worksheet.merge_range("AM13:AM14", u'Generador QAS 500 1', merge_format_t32)
		worksheet.merge_range("AN13:AN14", u'Generador QAS 115', merge_format_t32)
		worksheet.merge_range("AO13:AO14", u'Montacargas HELI', merge_format_t32)
		worksheet.merge_range("AP13:AP14", u'Montacargas CAT DP 30 NM', merge_format_t32)

		sd = self.env['saldos.diesel'].search([('year_id','=',yr),('month_id','=',mnth)])
		worksheet.write("AL15", u'Inv. Inicial', merge_format_t31)
		worksheet.write("AM15", sd[0].inv_qas_500 if len(sd) > 0 else 0, data_format_drgr)
		worksheet.write("AN15", sd[0].inv_qas_115 if len(sd) > 0 else 0, data_format_drgr)
		worksheet.write("AO15", sd[0].inv_heli if len(sd) > 0 else 0, data_format_drgr)
		worksheet.write("AP15", sd[0].inv_cat if len(sd) > 0 else 0, data_format_drgr)

		cmd = self.env['compra.diesel'].search([('year_id','=',yr),('month_id','=',mnth)])
		cnd = self.env['consumo.diesel'].search([('year_id','=',yr),('month_id','=',mnth)])
		mc  = self.env['maerz.calcinacion'].search([('year_id','=',yr),('month_id','=',mnth)])
		mio = self.env['maerz.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])

		print len(mc),len(mio),len(cmd),len(cnd),len(sd)
		if len(mc) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de CALCINACION para el periodo seleccionado.")
		if len(mio) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de INDICADORES DE OPERACION para el periodo seleccionado.")
		if len(cmd) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de COMPRAS DE DIESEL Y GSL para el periodo seleccionado.")
		if len(cnd) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de CONSUMO DE DIESEL Y GSL para el periodo seleccionado.")
		if len(sd) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de SALDOS DE DIESEL Y GSL para el periodo seleccionado.")
		
		sum_mc  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		sum_cmd = [0,0,0,0]
		sum_cnd = [0,0,0,0]
		sum_sd  = [0,0,0,0]

		x = 15
		for i in range(len(mc)):
			fch = format(i+1,'02')+'-'+month2name[mnth][:3]
			worksheet.write(x,1, fch, data_format_dlr)
			worksheet.write(x,21, fch, data_format_dlr)
			worksheet.write(x,31, fch, data_format_dlr)
			worksheet.write(x,37, fch, data_format_dlr)
			if i % 2 == 0:
				worksheet.write(x,2, mc[i].horas_operacion, data_format_d)
				worksheet.write(x,3, mc[i].ton_caco3, data_format_d)
				worksheet.write(x,4, mc[i].ton_cao, data_format_d)
				worksheet.write(x,5, mc[i].ton_cao_debajo, data_format_d)
				worksheet.write(x,6, mc[i].porc_cao_debajo, data_format_dr)
				worksheet.write(x,7, mc[i].prod_nominal, data_format_dr)
				worksheet.write(x,8, mc[i].coke_pulv, data_format_d)
				worksheet.write(x,9, mc[i].consumo_coke_kgs, data_format_d)
				worksheet.write(x,10, mc[i].consumo_mcal, data_format_d)
				worksheet.write(x,11, mc[i].consumo_ton_cao, data_format_d)
				worksheet.write(x,12, mc[i].mcal_ton, data_format_dr)
				worksheet.write(x,13, mc[i].kwh_total, data_format_d)
				worksheet.write(x,14, mc[i].kwh_ton, data_format_d)
				worksheet.write(x,15, mc[i].ppc, data_format_d)
				worksheet.write(x,16, mc[i].cao_disp, data_format_d)
				worksheet.write(x,17, mc[i].cao_total, data_format_d)
				worksheet.write(x,18, mc[i].reactividad, data_format_dr)
				worksheet.write(x,19, mc[i].pc_polvos, data_format_dr)

				worksheet.write(x,22, cmd[i].vale_qas_500 if cmd[i].vale_qas_500 else '', data_format_dr)
				worksheet.write(x,23, cmd[i].qas_500, data_format_dr)
				worksheet.write(x,24, cmd[i].vale_qas_115 if cmd[i].vale_qas_115 else '', data_format_dr)
				worksheet.write(x,25, cmd[i].qas_115, data_format_dr)
				worksheet.write(x,26, cmd[i].vale_heli if cmd[i].vale_heli else '', data_format_dr)
				worksheet.write(x,27, cmd[i].heli, data_format_dr)
				worksheet.write(x,28, cmd[i].vale_cat if cmd[i].vale_cat else '', data_format_dr)
				worksheet.write(x,29, cmd[i].cat, data_format_dr)

				worksheet.write(x,32, cnd[i].qas_500, data_format_dr)
				worksheet.write(x,33, cnd[i].qas_115, data_format_dr)
				worksheet.write(x,34, cnd[i].heli, data_format_dr)
				worksheet.write(x,35, cnd[i].cat, data_format_dr)

				worksheet.write(x,38, sd[i].qas_500, data_format_dr)
				worksheet.write(x,39, sd[i].qas_115, data_format_dr)
				worksheet.write(x,40, sd[i].heli, data_format_dr)
				worksheet.write(x,41, sd[i].cat, data_format_dr)

			else:
				worksheet.write(x,2, mc[i].horas_operacion, data_format_dgr)
				worksheet.write(x,3, mc[i].ton_caco3, data_format_dgr)
				worksheet.write(x,4, mc[i].ton_cao, data_format_dgr)
				worksheet.write(x,5, mc[i].ton_cao_debajo, data_format_dgr)
				worksheet.write(x,6, mc[i].porc_cao_debajo, data_format_dgr)
				worksheet.write(x,7, mc[i].prod_nominal, data_format_drgr)
				worksheet.write(x,8, mc[i].coke_pulv, data_format_dgr)
				worksheet.write(x,9, mc[i].consumo_coke_kgs, data_format_dgr)
				worksheet.write(x,10, mc[i].consumo_mcal, data_format_dgr)
				worksheet.write(x,11, mc[i].consumo_ton_cao, data_format_dgr)
				worksheet.write(x,12, mc[i].mcal_ton, data_format_drgr)
				worksheet.write(x,13, mc[i].kwh_total, data_format_dgr)
				worksheet.write(x,14, mc[i].kwh_ton, data_format_dgr)
				worksheet.write(x,15, mc[i].ppc, data_format_dgr)				
				worksheet.write(x,16, mc[i].cao_disp, data_format_dgr)
				worksheet.write(x,17, mc[i].cao_total, data_format_dgr)
				worksheet.write(x,18, mc[i].reactividad, data_format_drgr)
				worksheet.write(x,19, mc[i].pc_polvos, data_format_drgr)

				worksheet.write(x,22, cmd[i].vale_qas_500 if cmd[i].vale_qas_500 else '', data_format_drgr)
				worksheet.write(x,23, cmd[i].qas_500, data_format_drgr)
				worksheet.write(x,24, cmd[i].vale_qas_115 if cmd[i].vale_qas_115 else '', data_format_drgr)
				worksheet.write(x,25, cmd[i].qas_115, data_format_drgr)
				worksheet.write(x,26, cmd[i].vale_heli if cmd[i].vale_heli else '', data_format_drgr)
				worksheet.write(x,27, cmd[i].heli, data_format_drgr)
				worksheet.write(x,28, cmd[i].vale_cat if cmd[i].vale_cat else '', data_format_drgr)
				worksheet.write(x,29, cmd[i].cat, data_format_drgr)

				worksheet.write(x,32, cnd[i].qas_500, data_format_drgr)
				worksheet.write(x,33, cnd[i].qas_115, data_format_drgr)
				worksheet.write(x,34, cnd[i].heli, data_format_drgr)
				worksheet.write(x,35, cnd[i].cat, data_format_drgr)

				worksheet.write(x,38, sd[i].qas_500, data_format_drgr)
				worksheet.write(x,39, sd[i].qas_115, data_format_drgr)
				worksheet.write(x,40, sd[i].heli, data_format_drgr)
				worksheet.write(x,41, sd[i].cat, data_format_drgr)
			
			sum_mc[0] += mc[i].horas_operacion
			sum_mc[1] += mc[i].ton_caco3
			sum_mc[2] += mc[i].ton_cao
			sum_mc[3] += mc[i].ton_cao_debajo
			sum_mc[4] += mc[i].prod_nominal
			sum_mc[5] += mc[i].coke_pulv
			sum_mc[6] += mc[i].consumo_coke_kgs
			sum_mc[7] += mc[i].consumo_mcal
			sum_mc[8] += mc[i].consumo_ton_cao
			sum_mc[9] += mc[i].mcal_ton
			sum_mc[10] += mc[i].kwh_total
			sum_mc[11] += mc[i].kwh_ton
			sum_mc[12] += mc[i].ppc
			sum_mc[13] += mc[i].cao_disp
			sum_mc[14] += mc[i].cao_total
			sum_mc[15] += mc[i].reactividad
			sum_mc[16] += mc[i].pc_polvos

			sum_cmd[0] += cmd[i].qas_500
			sum_cmd[1] += cmd[i].qas_115
			sum_cmd[2] += cmd[i].heli
			sum_cmd[3] += cmd[i].cat

			sum_cnd[0] += cnd[i].qas_500
			sum_cnd[1] += cnd[i].qas_115
			sum_cnd[2] += cnd[i].heli
			sum_cnd[3] += cnd[i].cat

			sum_sd[0] += sd[i].qas_500
			sum_sd[1] += sd[i].qas_115
			sum_sd[2] += sd[i].heli
			sum_sd[3] += sd[i].cat

			x += 1

		worksheet.write(x,1, u'Totales', data_format_total)
		worksheet.write(x,2, sum_mc[0], data_format_total)
		worksheet.write(x,3, sum_mc[1], data_format_total)
		worksheet.write(x,4, sum_mc[2], data_format_total)
		worksheet.write(x,5, sum_mc[3], data_format_total)

		worksheet.write(x,6, 0, data_format_total)
		worksheet.write(x,7, sum_mc[4], data_format_total)
		worksheet.write(x,8, sum_mc[5], data_format_total)
		worksheet.write(x,9, sum_mc[6], data_format_total)
		worksheet.write(x,10, sum_mc[7], data_format_total)
		worksheet.write(x,11, sum_mc[8], data_format_total)
		worksheet.write(x,12, sum_mc[9], data_format_total)
		worksheet.write(x,13, sum_mc[10], data_format_total)
		worksheet.write(x,14, sum_mc[11], data_format_total)
		worksheet.write(x,15, sum_mc[12], data_format_total)
		worksheet.write(x,16, sum_mc[13], data_format_total)
		worksheet.write(x,17, sum_mc[14], data_format_total)
		worksheet.write(x,18, sum_mc[15], data_format_total)
		worksheet.write(x,19, sum_mc[16], data_format_total)

		worksheet.write(x,21, u'Totales', data_format_total)
		worksheet.write(x,22, u' ', data_format_total)
		worksheet.write(x,23, sum_cmd[0], data_format_total)
		worksheet.write(x,24, u' ', data_format_total)
		worksheet.write(x,25, sum_cmd[1], data_format_total)
		worksheet.write(x,26, u' ', data_format_total)
		worksheet.write(x,27, sum_cmd[2], data_format_total)
		worksheet.write(x,28, u' ', data_format_total)
		worksheet.write(x,29, sum_cmd[3], data_format_total)

		worksheet.write(x,31, u'Totales', data_format_total)
		worksheet.write(x,32, sum_cnd[0], data_format_total)
		worksheet.write(x,33, sum_cnd[1], data_format_total)
		worksheet.write(x,34, sum_cnd[2], data_format_total)
		worksheet.write(x,35, sum_cnd[3], data_format_total)

		worksheet.write(x,37, u'Totales', data_format_total)
		worksheet.write(x,38, sd[-1].qas_500, data_format_total)
		worksheet.write(x,39, sd[-1].qas_115, data_format_total)
		worksheet.write(x,40, sd[-1].heli, data_format_total)
		worksheet.write(x,41, sd[-1].cat, data_format_total)

		x = 48

		worksheet.merge_range(x,2,x,13, u'Indicadores de Operación', merge_format_t32)
		x+=1
		worksheet.merge_range(x,2,x,5, u'Concepto', merge_format_t32)
		worksheet.merge_range(x,6,x,11, u'Cantidad', merge_format_t32)
		worksheet.merge_range(x,12,x,13, u'Unidades', merge_format_t32)

		x += 1
		mio = self.env['maerz.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
		for i in range(len(mio)):
			if i % 2 == 0:
				if i == len(mio)-1:
					worksheet.merge_range(x,2,x,5, mio[i].concepto, data_format_dlrd)
					worksheet.merge_range(x,6,x,11, mio[i].cantidad, data_format_dlrd)
					worksheet.merge_range(x,12,x,13, mio[i].unidades, data_format_dlrd)

				else:
					worksheet.merge_range(x,2,x,5, mio[i].concepto, data_format_dlr)
					if i == 0:
						worksheet.merge_range(x,6,x,11, mio[i].cantidad, data_format_dlrg)
					else:
						worksheet.merge_range(x,6,x,11, mio[i].cantidad, data_format_dlr)
					worksheet.merge_range(x,12,x,13, mio[i].unidades, data_format_dlr)
			else:
				if i == len(mio)-1:
					worksheet.merge_range(x,2,x,5, mio[i].concepto, data_format_dlrdgr)
					worksheet.merge_range(x,6,x,11, mio[i].cantidad, data_format_dlrdgr)
					worksheet.merge_range(x,12,x,13, mio[i].unidades, data_format_dlrdgr)
				else:
					worksheet.merge_range(x,2,x,5, mio[i].concepto, data_format_dlrgr)
					if i == 0 or i == 4:
						worksheet.merge_range(x,6,x,11, mio[i].cantidad, data_format_dlrg)
					else:
						worksheet.merge_range(x,6,x,11, mio[i].cantidad, data_format_dlrgr)
					worksheet.merge_range(x,12,x,13, mio[i].unidades, data_format_dlrgr)
			x += 1

		workbook.close()
		
		f = open( direccion + u'Maerz_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx', 'rb')
			
		vals = {
			'output_name': u'Maerz_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx',
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