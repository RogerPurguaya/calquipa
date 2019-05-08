# -*- encoding: utf-8 -*-
import base64
from openerp import models, fields, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp

import calendar
import datetime
import decimal

class trituracion_negro_africano(models.Model):
	_name = 'trituracion.negro.africano'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')

	horas_operacion = fields.Float('Horas Trabajadas')
	nro_viajes = fields.Float(u'Número de Viajes')

	# camppos nuevos al 20180326

	stone_fron_extract = fields.Float(u'Piedra Viene de Extracción')
	stone_repross_b3 = fields.Float('Piedra Reprocesada Banda 3')
	ts_alimentadas_2018 = fields.Float('Toneladas Alimentadas', compute="get_tn_alim")

	ts_alimentadas = fields.Float('Toneladas Alimentadas')
	viajes_cancha = fields.Float('Viajes Cancha')
	tons_cancha = fields.Float('Tons Cancha')
	consumo_cancha = fields.Float('Consumo Cancha')
	tn_banda_1 = fields.Float('Tons Banda 1')
	tn_banda_2 = fields.Float('Tons Banda 2')
	tn_banda_3 = fields.Float('Tons Banda 3 (Maerz)')
	total_tn = fields.Float('Total de Toneladas', compute="get_total_tn")
	tph = fields.Float('TPH Promedio', compute="get_tph")
	horno = fields.Float('%  Horno', compute="get_horno")
	niebla = fields.Float('Consumo Agua Niebla')
	agua_tn = fields.Float('Consumo Agua Tons', compute="get_agua_tn")
	consumo_diesel_1 = fields.Float('Consumo Diesel Generador No. 1')
	consumo_diesel_2 = fields.Float('Consumo Diesel Generador No. 2')
	cummins = fields.Float('Consumo Diesel Generador Cummins')
	tn_diesel = fields.Float('Consumo Diesel 50kw', compute="get_tn_diesel")
	energia = fields.Float('Consumo Energia kwh')
	consumo_kwh = fields.Float('Consumo kwh/Ton', compute="get_consumo_kwh")
	co3 = fields.Float('Calidad Ca CO3')
	silice = fields.Float('Calidad Silice')




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
	def get_tn_alim(self):
		self.ts_alimentadas_2018 = self.stone_fron_extract + self.stone_repross_b3

	@api.one
	def get_total_tn(self):
		self.total_tn = self.tn_banda_1 + self.tn_banda_2 + self.tn_banda_3

	@api.one
	def get_tph(self):
		self.tph = (self.total_tn / self.horas_operacion) if self.horas_operacion != 0 else 0

	@api.one
	def get_horno(self):
		self.horno = (self.tn_banda_3 / self.total_tn) if self.total_tn != 0 else 0

	@api.one
	def get_agua_tn(self):
		self.agua_tn = (self.tn_banda_3 / self.niebla) if self.niebla != 0 else 0

	@api.one
	def get_tn_diesel(self):
		self.tn_diesel = ((self.consumo_diesel_1 + self.consumo_diesel_2) / self.total_tn) if self.total_tn != 0 else 0

	@api.one
	def get_consumo_kwh(self):
		self.consumo_kwh = (self.energia / self.total_tn) if self.total_tn != 0 else 0

	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "trituracion.negro.africano",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['trituracion.negro.africano'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['trituracion.negro.africano'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "trituracion.negro.africano",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class trituracion_horno_maez(models.Model):
	_name = 'trituracion.horno.maez'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')

	piedra_1er = fields.Float(u'Envío Piedra 1er Turno')
	piedra_2da = fields.Float(u'Envío Piedra 2da Turno')
	total_tn = fields.Float(u'Total Tons Enviadas Cal', compute="get_total_tn")

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
	def get_total_tn(self):
		self.total_tn = self.piedra_1er + self.piedra_2da

	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "trituracion.horno.maez",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['trituracion.horno.maez'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['trituracion.horno.maez'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "trituracion.horno.maez",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class trituracion_compra_diesel(models.Model):
	_name = 'trituracion.compra.diesel'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')
	nro_vale_gen1 = fields.Char(u'vale 1')
	diesel_gen1 = fields.Float(u'Compra Diesel Generador no. 1')
	nro_vale_gen2 = fields.Char(u'vale 2')
	diesel_gen2 = fields.Float(u'Compra Diesel Generador no. 2')
	nro_vale_gen3 = fields.Char(u'vale 3')
	diesel_comp = fields.Float(u'Compra Diesel Generador Cummins')
	agua_comp = fields.Float(u'Compra Agua Gls/Ton')

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
				"res_model": "trituracion.compra.diesel",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['trituracion.compra.diesel'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['trituracion.compra.diesel'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "trituracion.compra.diesel",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class trituracion_inventario_diesel(models.Model):
	_name = 'trituracion.inventario.diesel'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')

	diesel_gen1 = fields.Float(u'Inventario Diesel Generador no. 1', compute="compute_diesel_gen1")
	diesel_gen2 = fields.Float(u'Inventario Diesel Generador no. 2', compute="compute_diesel_gen2")
	diesel_comp = fields.Float(u'Inventario Diesel Generador Cummins', compute="compute_diesel_comp")
	agua_comp = fields.Float(u'Inventario Agua Gls/Ton', compute="compute_agua_comp")

	inv_diesel_gen1 = fields.Float(u'Inventario Diesel Generador no. 1', compute="compute_inv_diesel_gen1")
	inv_diesel_gen2 = fields.Float(u'Inventario Diesel Generador no. 2', compute="compute_inv_diesel_gen2")
	inv_diesel_comp = fields.Float(u'Inventario Diesel Generador Cummins', compute="compute_inv_diesel_comp")
	inv_agua_comp = fields.Float(u'Inventario Agua Gls/Ton', compute="compute_inv_agua_comp")

	@api.one
	def compute_inv_diesel_gen1(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		tid = self.env['trituracion.inventario.diesel'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(tid) > 0:
			tid = tid[-1]
			self.inv_diesel_gen1 = tid.diesel_gen1
		else:
			self.inv_diesel_gen1 = 0

	@api.one
	def compute_inv_diesel_gen2(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		tid = self.env['trituracion.inventario.diesel'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(tid) > 0:
			tid = tid[-1]
			self.inv_diesel_gen2 = tid.diesel_gen2
		else:
			self.inv_diesel_gen2 = 0

	@api.one
	def compute_inv_diesel_comp(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		tid = self.env['trituracion.inventario.diesel'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(tid) > 0:
			tid = tid[-1]
			self.inv_diesel_comp = tid.diesel_comp
		else:
			self.inv_diesel_comp = 0

	@api.one
	def compute_inv_agua_comp(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		tid = self.env['trituracion.inventario.diesel'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(tid) > 0:
			tid = tid[-1]
			self.inv_agua_comp = tid.agua_comp
		else:
			self.inv_agua_comp = 0

	@api.multi
	def compute_diesel_gen1(self):
		sum_tid = 0
		for tid in self.env['trituracion.inventario.diesel'].search([]):
			tna = self.env['trituracion.negro.africano'].search([('date','=',tid.date)])
			tcd = self.env['trituracion.compra.diesel'].search([('date','=',tid.date)])
			if len(tna):
				sum_tid -= tna[0].consumo_diesel_1
			if len(tcd):
				sum_tid += tcd[0].diesel_gen1
			tid.diesel_gen1 = sum_tid

		# prev_date = datetime.datetime.strptime(self.date, "%Y-%m-%d") - datetime.timedelta(days=1)
		# tna = self.env['trituracion.negro.africano'].search([('date','=',self.date)])
		# tcd = self.env['trituracion.compra.diesel'].search([('date','=',self.date)])
		# tid = self.env['trituracion.inventario.diesel'].search([('date','=',prev_date)])
		# if len(tid) > 0 and len(tna) > 0 and len(tcd) > 0:
		# 	tid = tid[0]
		# 	tna = tna[0]
		# 	tcd = tcd[0]
		# 	self.diesel_gen1 = tid.diesel_gen1 + tcd.diesel_gen1 - tna.consumo_diesel_1
		# else:
		# 	self.diesel_gen1 = 0

	@api.multi
	def compute_diesel_gen2(self):
		sum_tid = 0
		for tid in self.env['trituracion.inventario.diesel'].search([]):
			tna = self.env['trituracion.negro.africano'].search([('date','=',tid.date)])
			tcd = self.env['trituracion.compra.diesel'].search([('date','=',tid.date)])
			if len(tna):
				sum_tid -= tna[0].consumo_diesel_2
			if len(tcd):
				sum_tid += tcd[0].diesel_gen2
			tid.diesel_gen2 = sum_tid

		# prev_date = datetime.datetime.strptime(self.date, "%Y-%m-%d") - datetime.timedelta(days=1)
		# tna = self.env['trituracion.negro.africano'].search([('date','=',self.date)])
		# tcd = self.env['trituracion.compra.diesel'].search([('date','=',self.date)])
		# tid = self.env['trituracion.inventario.diesel'].search([('date','=',prev_date)])
		# if len(tid) > 0 and len(tna) > 0 and len(tcd) > 0:
		# 	tid = tid[0]
		# 	tna = tna[0]
		# 	tcd = tcd[0]
		# 	self.diesel_gen2 = tid.diesel_gen2 + tcd.diesel_gen2 - tna.consumo_diesel_2
		# else:
		# 	self.diesel_gen2 = 0

	@api.multi
	def compute_diesel_comp(self):
		sum_tid = 0
		for tid in self.env['trituracion.inventario.diesel'].search([]):
			tna = self.env['trituracion.negro.africano'].search([('date','=',tid.date)])
			tcd = self.env['trituracion.compra.diesel'].search([('date','=',tid.date)])
			if len(tna):
				sum_tid -= tna[0].cummins
			if len(tcd):
				sum_tid += tcd[0].diesel_comp
			tid.diesel_comp = sum_tid

		# prev_date = datetime.datetime.strptime(self.date, "%Y-%m-%d") - datetime.timedelta(days=1)
		# tna = self.env['trituracion.negro.africano'].search([('date','=',self.date)])
		# tcd = self.env['trituracion.compra.diesel'].search([('date','=',self.date)])
		# tid = self.env['trituracion.inventario.diesel'].search([('date','=',prev_date)])
		# if len(tid) > 0 and len(tna) > 0 and len(tcd) > 0:
		# 	tid = tid[0]
		# 	tna = tna[0]
		# 	tcd = tcd[0]
		# 	self.diesel_comp = tid.diesel_comp + tcd.diesel_comp - tna.cummins
		# else:
		# 	self.diesel_comp = 0

	@api.multi
	def compute_agua_comp(self):
		sum_tid = 0
		for tid in self.env['trituracion.inventario.diesel'].search([]):
			tna = self.env['trituracion.negro.africano'].search([('date','=',tid.date)])
			tcd = self.env['trituracion.compra.diesel'].search([('date','=',tid.date)])
			if len(tna):
				sum_tid -= tna[0].niebla
			if len(tcd):
				sum_tid += tcd[0].agua_comp
			tid.agua_comp = sum_tid

		# prev_date = datetime.datetime.strptime(self.date, "%Y-%m-%d") - datetime.timedelta(days=1)
		# tna = self.env['trituracion.negro.africano'].search([('date','=',self.date)])
		# tcd = self.env['trituracion.compra.diesel'].search([('date','=',self.date)])
		# tid = self.env['trituracion.inventario.diesel'].search([('date','=',prev_date)])
		# if len(tid) > 0 and len(tna) > 0 and len(tcd) > 0:
		# 	tid = tid[0]
		# 	tna = tna[0]
		# 	tcd = tcd[0]
		# 	self.agua_comp = tid.agua_comp + tcd.agua_comp - tna.niebla
		# else:
		# 	self.agua_comp = 0

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
				"res_model": "trituracion.inventario.diesel",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['trituracion.inventario.diesel'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['trituracion.inventario.diesel'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "trituracion.inventario.diesel",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class trituracion_indicadores_operacion(models.Model):
	_name = 'trituracion.indicadores.operacion'

	_order = 'id'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	concepto = fields.Char('Concepto')
	cantidad = fields.Float('Cantidad')
	unidades = fields.Char('Unidades')

	dias_transcurridos = fields.Integer('Dias Transcurridos')

	@api.multi
	def display_q(self, mnth, yr, dt, om, oh, hp, ah, pc, ps):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "trituracion.indicadores.operacion",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		
		conc = [(u'Objetivo Mes',u'Toneladas'),
				(u'Tendencia Mes',u'Toneladas'),
				(u'Acumulado Mes',u'Toneladas'),
				(u'Diferencia Objetivo vs Real',u'Toneladas'),
				(u'Objetivo de Hrs de Operación Mes',u'Horas'),
				(u'Hrs Empleadas Trituración',u'Horas'),
				(u'Promedio TPH',u'Tonelada por Hora'),
				(u'Promedio Día',u'Toneladas'),
				(u'Días de Producción',u'Días'),
				(u'%  de Aprov. Hornos',u'%'),
				(u'Promedio Calidad Ca CO3',u'%'),
				(u'Promedio %  Silice',u'%'),
				(u'Promedio Consumo Diesel',u'Galónes'),
				(u'Promedio Consumo Energia',u'kwh/ton'),]
		dias_mes = calendar.monthrange(yr, mnth)[1]

		tio = self.env['trituracion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth)])
		if len(tio) == 0:
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
					vals['cantidad'] = self.env['trituracion.funciones'].get_tn_banda_3(mnth, yr)

				if vals['concepto'] == conc[3][0]:
					tioc1 = self.env['trituracion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',conc[0][0])])[0]
					tioc3 = self.env['trituracion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',conc[2][0])])[0]
					vals['cantidad'] = tioc1.cantidad - tioc3.cantidad

				if vals['concepto'] == conc[4][0]:
					vals['cantidad'] = oh

				if vals['concepto'] == conc[5][0]:
					vals['cantidad'] = hp

				if vals['concepto'] == conc[6][0]:
					ep = self.env['trituracion.negro.africano'].search([('year_id','=',yr),('month_id','=',mnth)])
					s = 0
					for i in ep:
						s += i.tph
					vals['cantidad'] = (s/len(ep)) if len(ep) != 0 else 0

				if vals['concepto'] == conc[7][0]:
					vals['cantidad'] = 0

				if vals['concepto'] == conc[8][0]:
					vals['cantidad'] = 24

				if vals['concepto'] == conc[9][0]:
					vals['cantidad'] = ah

				if vals['concepto'] == conc[10][0]:
					vals['cantidad'] = pc

				if vals['concepto'] == conc[11][0]:
					vals['cantidad'] = ps

				if vals['concepto'] == conc[12][0]:
					vals['cantidad'] = self.env['trituracion.funciones'].get_consumo_diesel_1(mnth, yr)

				if vals['concepto'] == conc[13][0]:
					vals['cantidad'] = self.env['trituracion.funciones'].get_energia(mnth, yr)

				ntio = self.env['trituracion.indicadores.operacion'].create(vals)
		else:		
			for i in tio:
				i.dias_transcurridos = dt
				if i.concepto == conc[0][0]:
					i.cantidad = om
				if i.concepto == conc[4][0]:
					i.cantidad = oh
				if i.concepto == conc[5][0]:
					i.cantidad = hp
				if i.concepto == conc[9][0]:
					i.cantidad = ah
				if i.concepto == conc[10][0]:
					i.cantidad = pc
				if i.concepto == conc[11][0]:
					i.cantidad = ps

		return {
			"type": "ir.actions.act_window",
			"res_model": "trituracion.indicadores.operacion",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class trituracion_funciones(models.Model):
	_name = 'trituracion.funciones'

	def get_tn_banda_3(self,mnth,yr):
		self.env.cr.execute("""
			select sum(tn_banda_3) from trituracion_negro_africano
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_consumo_diesel_1(self,mnth,yr):
		self.env.cr.execute("""
			select sum(consumo_diesel_1) from trituracion_negro_africano
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_energia(self,mnth,yr):
		self.env.cr.execute("""
			select sum(energia) from trituracion_negro_africano
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

class trituracion_reporte(models.Model):
	_name = 'trituracion.reporte'

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
		workbook = Workbook( direccion + u'Trituracion_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx')
		worksheet = workbook.add_worksheet("Trituracion")

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
		worksheet.set_column("Y:Y", 3.86)
		# worksheet.set_column("AD:AD", 3.86)
		# worksheet.set_column("AJ:AJ", 3.86)

		worksheet.set_column("B:B", 7.86)
		worksheet.set_column("C:C", 9.14)
		worksheet.set_column("D:D", 11.86)
		worksheet.set_column("E:E", 10.57)
		worksheet.set_column("F:F", 10.29)
		worksheet.set_column("G:G", 10.71)

		worksheet.merge_range("B2:G8", '', merge_format_t)
		worksheet.merge_range("H2:AL8", u'Calquipa', merge_format_t)
		worksheet.merge_range("AM2:AO2", u'Fecha:', merge_format_ca)
		worksheet.merge_range("AP2:AQ2", datetime.datetime.today().strftime("%Y-%m-%d"), merge_format_ca2)
		worksheet.merge_range("AM3:AO3", u'Mes:', merge_format_ca)
		worksheet.merge_range("AP3:AQ3", month2name[mnth], merge_format_ca2)
		worksheet.merge_range("AM4:AO4", u'Días de Mes:', merge_format_ca)
		worksheet.merge_range("AP4:AQ4", calendar.monthrange(yr,mnth)[1], merge_format_ca2)
		worksheet.merge_range("AM5:AO5", u'Días Transcurridos Mes:', merge_format_ca)

		tio = self.env['trituracion.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
		if len(tio) > 0:
			tio = tio[0]
			worksheet.merge_range("AP5:AQ5", tio.dias_transcurridos, merge_format_ca2)
		else:
			worksheet.merge_range("AP5:AQ5", '', merge_format_ca2)

		worksheet.merge_range("AM6:AO6", u'Hrs Mes:', merge_format_ca)
		worksheet.merge_range("AP6:AQ6", u'', merge_format_ca2)
		worksheet.merge_range("AM7:AO7", u'Clave SGI', merge_format_ca)
		worksheet.merge_range("AP7:AQ7", u'', merge_format_ca2)
		worksheet.merge_range("AM8:AO8", u'Folio', merge_format_ca)
		worksheet.merge_range("AP8:AQ8", u'', merge_format_ca2)

		worksheet.insert_image('C3', 'calquipalright.png', {'x_scale': 1.5, 'y_scale': 1.5})
		worksheet.insert_image('I3', 'calquipalleft.png', {'x_scale': 1.5, 'y_scale': 1.5})

		worksheet.set_row(9, 21)
		worksheet.merge_range("B10:AQ10", u'Trituración', merge_format_t)

		worksheet.set_row(11, 20)
		worksheet.merge_range("B12:Z12", u'Trituración Negro Africano Calquipa', merge_format_t2)
		worksheet.merge_range("AB12:AE12", u'Envio Piedra a Horno Maez', merge_format_t2)
		worksheet.merge_range("AG12:AN12", u'Compra de Insumos', merge_format_t2)
		worksheet.merge_range("AP12:AT12", u'Inventario de Insumos', merge_format_t2)

		worksheet.set_row(12, 20.25)
		worksheet.set_row(13, 33)
		worksheet.set_row(14, 12)
		worksheet.merge_range("B13:B15", u'Fecha', merge_format_t31)
		worksheet.merge_range("C13:C15", u'Horas Trabajadas', merge_format_t32)
		worksheet.merge_range("D13:D15", u'Númer de Viajes', merge_format_t32)

		worksheet.merge_range("E13:E15", u'Piedra Viene de Extracción', merge_format_t32)
		worksheet.merge_range("F13:F15", u'Piedra Reprocesada Banda 3', merge_format_t32)

		worksheet.merge_range("G13:G15", u'Tons Alimentadas', merge_format_t32)
		worksheet.merge_range("H13:H15", u'Viajes Cancha', merge_format_t32)
		worksheet.merge_range("I13:I15", u'Tons Cancha', merge_format_t32)
		worksheet.merge_range("J13:J15", u'Consumo Cancha', merge_format_t32)
		worksheet.merge_range("K13:K15", u'Tons Banda 1', merge_format_t32)
		worksheet.merge_range("L13:L15", u'Tons Banda 2', merge_format_t32)
		worksheet.merge_range("M13:M15", u'Tons Banda 3 (Maez)', merge_format_t32)
		worksheet.merge_range("N13:N15", u'Total de Toneladas', merge_format_t32)
		worksheet.merge_range("O13:O15", u'TPH Promedio', merge_format_t32)
		worksheet.merge_range("P13:P15", u'%  Horno', merge_format_t32)
		worksheet.merge_range("Q13:Q15", u'Consumo Agua Niebla', merge_format_t32)
		worksheet.merge_range("R13:R15", u'Consumo Agua/Ton', merge_format_t32)
		worksheet.merge_range("S13:S15", u'Consumo Diesel Generador no. 1', merge_format_t32)
		worksheet.merge_range("T13:T15", u'Consumo Diesel Generador no. 2', merge_format_t32)
		worksheet.merge_range("U13:U15", u'Consumo Diesel Generador Cummins', merge_format_t32)
		worksheet.merge_range("V13:V15", u'Consumo Diesel Gls/Ton', merge_format_t32)
		worksheet.merge_range("W13:W15", u'Consumo Energia kwh', merge_format_t32)
		worksheet.merge_range("X13:X15", u'Consumo kwh/Ton', merge_format_t32)
		worksheet.merge_range("Y13:Y15", u'Calidad Ca CO3', merge_format_t32)
		worksheet.merge_range("Z13:Z15", u'Calidad Silice', merge_format_t32)

		worksheet.merge_range("AB13:AB15", u'Fecha', merge_format_t31)
		worksheet.merge_range("AC13:AC15", u'Envío Piedra 1er Turno', merge_format_t32)
		worksheet.merge_range("AD13:AD15", u'Envío Piedra 2do Turno', merge_format_t32)
		worksheet.merge_range("AE13:AE15", u'Total Tons Enviadass Cal', merge_format_t32)

		worksheet.merge_range("AG13:AG15", u'Fecha', merge_format_t31)
		worksheet.merge_range("AH13:AH15", u'Nro de Vale Generador no. 1', merge_format_t32)
		worksheet.merge_range("AI13:AI15", u'Compra Diesel Generador no. 1', merge_format_t32)
		worksheet.merge_range("AJ13:AJ15", u'Nro de Vale Generador no. 2', merge_format_t32)
		worksheet.merge_range("AK13:AK15", u'Compra Diesel Generador no. 2', merge_format_t32)
		worksheet.merge_range("AL13:AL15", u'Nro de Vale Cummins', merge_format_t32)
		worksheet.merge_range("AM13:AM15", u'Compra Cummins', merge_format_t32)
		worksheet.merge_range("AN13:AN15", u'Compra Agua Gls/Ton', merge_format_t32)

		worksheet.merge_range("AP13:AP14", u'Fecha', merge_format_t31)
		worksheet.merge_range("AQ13:AQ14", u'Inventario Diesel Generador no. 1', merge_format_t32)
		worksheet.merge_range("AR13:AR14", u'Inventario Diesel Generador no. 2', merge_format_t32)
		worksheet.merge_range("AS13:AS14", u'Inventario Cummins', merge_format_t32)
		worksheet.merge_range("AT13:AT14", u'Inventario Agua Gls/Ton', merge_format_t32)

		ptid = self.env['trituracion.inventario.diesel'].search([('year_id','=',yr),('month_id','=',mnth)])
		worksheet.write("AP15", u'Inv. Inicial', merge_format_t31)
		worksheet.write("AQ15", ptid[0].inv_diesel_gen1 if len(ptid) > 0 else 0, data_format_drgr)
		worksheet.write("AR15", ptid[0].inv_diesel_gen2 if len(ptid) > 0 else 0, data_format_drgr)
		worksheet.write("AS15", ptid[0].inv_diesel_comp if len(ptid) > 0 else 0, data_format_drgr)
		worksheet.write("AT15", ptid[0].inv_agua_comp if len(ptid) > 0 else 0, data_format_drgr)

		tna = self.env['trituracion.negro.africano'].search([('year_id','=',yr),('month_id','=',mnth)])
		thm = self.env['trituracion.horno.maez'].search([('year_id','=',yr),('month_id','=',mnth)])
		tcd = self.env['trituracion.compra.diesel'].search([('year_id','=',yr),('month_id','=',mnth)])
		tid = self.env['trituracion.inventario.diesel'].search([('year_id','=',yr),('month_id','=',mnth)])
		tio = self.env['trituracion.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])

		print len(tna),len(thm),len(tcd),len(tid),len(tio)
		if len(tna) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de NEGRO AFRICANO para el periodo seleccionado.")
		if len(thm) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de HORNO MAEZ para el periodo seleccionado.")
		if len(tcd) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de COMPRA DE DIESEL Y AGUA para el periodo seleccionado.")
		if len(tid) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de INVENTARIO DE DIESEL Y AGUA para el periodo seleccionado.")
		if len(tio) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de INDICADORES DE OPERACION para el periodo seleccionado.")

		sum_tna = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		sum_tep = [0,0,0]
		sum_tcd = [0,0,0,0]
		sum_tid = [0,0,0,0]

		sum_tid[0] += tid[0].inv_diesel_gen1 if len(tid) > 0 else 0
		sum_tid[1] += tid[1].inv_diesel_gen2 if len(tid) > 0 else 0
		sum_tid[2] += tid[2].inv_diesel_comp if len(tid) > 0 else 0
		sum_tid[3] += tid[3].inv_agua_comp if len(tid) > 0 else 0

		x = 15
		for i in range(len(tna)):
			fch = format(i+1,'02')+'-'+month2name[mnth][:3]
			worksheet.write(x,1, fch, data_format_dlr)
			worksheet.write(x,27, fch, data_format_dlr)
			worksheet.write(x,32, fch, data_format_dlr)
			worksheet.write(x,41, fch, data_format_dlr)

			if i % 2 == 0:
				worksheet.write(x,2, tna[i].horas_operacion, data_format_d)
				worksheet.write(x,3, tna[i].nro_viajes, data_format_d)

				worksheet.write(x,4, tna[i].stone_fron_extract, data_format_d)
				worksheet.write(x,5, tna[i].stone_repross_b3, data_format_d)
				worksheet.write(x,6, tna[i].ts_alimentadas_2018, data_format_d)


				# worksheet.write(x,4, tna[i].ts_alimentadas, data_format_d)
				worksheet.write(x,7, tna[i].viajes_cancha, data_format_d)
				worksheet.write(x,8, tna[i].tons_cancha, data_format_d)
				worksheet.write(x,9, tna[i].consumo_cancha, data_format_d)
				worksheet.write(x,10, tna[i].tn_banda_1, data_format_d)
				worksheet.write(x,11, tna[i].tn_banda_2, data_format_d)
				worksheet.write(x,12, tna[i].tn_banda_3, data_format_d)
				worksheet.write(x,13, tna[i].total_tn, data_format_d)
				worksheet.write(x,14, tna[i].tph, data_format_d)
				worksheet.write(x,15, tna[i].horno, data_format_dr)				
				worksheet.write(x,16, tna[i].niebla, data_format_d)
				worksheet.write(x,17, tna[i].agua_tn, data_format_d)
				worksheet.write(x,18, tna[i].consumo_diesel_1, data_format_d)
				worksheet.write(x,19, tna[i].consumo_diesel_2, data_format_d)
				worksheet.write(x,20, tna[i].cummins, data_format_d)
				worksheet.write(x,21, tna[i].tn_diesel, data_format_d)
				worksheet.write(x,22, tna[i].energia, data_format_d)
				worksheet.write(x,23, tna[i].consumo_kwh, data_format_dr)
				worksheet.write(x,24, tna[i].co3, data_format_d)
				worksheet.write(x,25, tna[i].silice, data_format_dr)

				worksheet.write(x,28, thm[i].piedra_1er, data_format_d)			
				worksheet.write(x,29, thm[i].piedra_2da, data_format_d)	
				worksheet.write(x,30, thm[i].total_tn, data_format_dr)

				worksheet.write(x,33, tcd[i].nro_vale_gen1 if tcd[i].nro_vale_gen1 else '', data_format_d)			
				worksheet.write(x,34, tcd[i].diesel_gen1, data_format_d)
				worksheet.write(x,35, tcd[i].nro_vale_gen2 if tcd[i].nro_vale_gen2 else '', data_format_d)	
				worksheet.write(x,36, tcd[i].diesel_gen2, data_format_d)
				worksheet.write(x,37, tcd[i].nro_vale_gen3 if tcd[i].nro_vale_gen3 else '', data_format_d)	
				worksheet.write(x,38, tcd[i].diesel_comp, data_format_d)
				worksheet.write(x,39, tcd[i].agua_comp, data_format_dr)

				worksheet.write(x,42, tid[i].diesel_gen1, data_format_d)			
				worksheet.write(x,43, tid[i].diesel_gen2, data_format_d)	
				worksheet.write(x,44, tid[i].diesel_comp, data_format_d)	
				worksheet.write(x,45, tid[i].agua_comp, data_format_dr)

			else:
				worksheet.write(x,2, tna[i].horas_operacion, data_format_dgr)
				worksheet.write(x,3, tna[i].nro_viajes, data_format_dgr)
				
				worksheet.write(x,4, tna[i].stone_fron_extract, data_format_dgr)
				worksheet.write(x,5, tna[i].stone_repross_b3, data_format_dgr)
				worksheet.write(x,6, tna[i].ts_alimentadas_2018, data_format_dgr)

				# worksheet.write(x,4, tna[i].ts_alimentadas, data_format_dgr)
				worksheet.write(x,7, tna[i].viajes_cancha, data_format_dgr)
				worksheet.write(x,8, tna[i].tons_cancha, data_format_dgr)
				worksheet.write(x,9, tna[i].consumo_cancha, data_format_dgr)
				worksheet.write(x,10, tna[i].tn_banda_1, data_format_dgr)
				worksheet.write(x,11, tna[i].tn_banda_2, data_format_dgr)
				worksheet.write(x,12, tna[i].tn_banda_3, data_format_dgr)
				worksheet.write(x,13, tna[i].total_tn, data_format_dgr)
				worksheet.write(x,14, tna[i].tph, data_format_dgr)
				worksheet.write(x,15, tna[i].horno, data_format_drgr)				
				worksheet.write(x,16, tna[i].niebla, data_format_dgr)
				worksheet.write(x,17, tna[i].agua_tn, data_format_dgr)
				worksheet.write(x,18, tna[i].consumo_diesel_1, data_format_dgr)
				worksheet.write(x,19, tna[i].consumo_diesel_2, data_format_dgr)
				worksheet.write(x,20, tna[i].cummins, data_format_dgr)
				worksheet.write(x,21, tna[i].tn_diesel, data_format_dgr)
				worksheet.write(x,22, tna[i].energia, data_format_dgr)
				worksheet.write(x,23, tna[i].consumo_kwh, data_format_drgr)
				worksheet.write(x,24, tna[i].co3, data_format_dgr)
				worksheet.write(x,25, tna[i].silice, data_format_drgr)

				worksheet.write(x,28, thm[i].piedra_1er, data_format_dgr)			
				worksheet.write(x,29, thm[i].piedra_2da, data_format_dgr)	
				worksheet.write(x,30, thm[i].total_tn, data_format_drgr)

				worksheet.write(x,33, tcd[i].nro_vale_gen1 if tcd[i].nro_vale_gen1 else '', data_format_dgr)			
				worksheet.write(x,34, tcd[i].diesel_gen1, data_format_dgr)
				worksheet.write(x,35, tcd[i].nro_vale_gen2 if tcd[i].nro_vale_gen2 else '', data_format_dgr)	
				worksheet.write(x,36, tcd[i].diesel_gen2, data_format_dgr)
				worksheet.write(x,37, tcd[i].nro_vale_gen3 if tcd[i].nro_vale_gen3 else '', data_format_dgr)	
				worksheet.write(x,38, tcd[i].diesel_comp, data_format_dgr)
				worksheet.write(x,39, tcd[i].agua_comp, data_format_dgr)

				worksheet.write(x,42, tid[i].diesel_gen1, data_format_dgr)			
				worksheet.write(x,43, tid[i].diesel_gen2, data_format_dgr)	
				worksheet.write(x,44, tid[i].diesel_comp, data_format_dgr)	
				worksheet.write(x,45, tid[i].agua_comp, data_format_drgr)
			
			sum_tna[0] += tna[i].horas_operacion
			sum_tna[1] += tna[i].nro_viajes
			sum_tna[2] += tna[i].stone_fron_extract
			sum_tna[3] += tna[i].stone_repross_b3
			sum_tna[4] += tna[i].ts_alimentadas_2018
			# sum_tna[5] += tna[i].ts_alimentadas
			sum_tna[5] += tna[i].viajes_cancha
			sum_tna[6] += tna[i].tons_cancha
			sum_tna[7] += tna[i].consumo_cancha
			sum_tna[8] += tna[i].tn_banda_1
			sum_tna[9] += tna[i].tn_banda_2
			sum_tna[10] += tna[i].tn_banda_3
			sum_tna[11] += tna[i].total_tn
			sum_tna[12] += tna[i].tph
			sum_tna[13] += tna[i].horno
			sum_tna[14] += tna[i].niebla
			sum_tna[15] += tna[i].agua_tn
			sum_tna[16] += tna[i].consumo_diesel_1
			sum_tna[17] += tna[i].consumo_diesel_2
			sum_tna[18] += tna[i].cummins
			sum_tna[19] += tna[i].tn_diesel
			sum_tna[20] += tna[i].energia
			sum_tna[21] += tna[i].consumo_kwh
			sum_tna[22] += tna[i].co3
			sum_tna[23] += tna[i].silice
			
			sum_tep[0] += thm[i].piedra_1er
			sum_tep[1] += thm[i].piedra_2da
			sum_tep[2] += thm[i].total_tn

			sum_tcd[0] += tcd[i].diesel_gen1
			sum_tcd[1] += tcd[i].diesel_gen2
			sum_tcd[2] += tcd[i].diesel_comp
			sum_tcd[3] += tcd[i].agua_comp

			sum_tid[0] += tid[i].diesel_gen1
			sum_tid[1] += tid[i].diesel_gen2
			sum_tid[2] += tid[i].diesel_comp
			sum_tid[3] += tid[i].agua_comp

			x += 1

		worksheet.write(x,1, u'Totales', data_format_total)
		worksheet.write(x,2, sum_tna[0], data_format_total)
		worksheet.write(x,3, sum_tna[1], data_format_total)
		worksheet.write(x,4, sum_tna[2], data_format_total)
		worksheet.write(x,5, sum_tna[3], data_format_total)
		worksheet.write(x,6, sum_tna[4], data_format_total)
		worksheet.write(x,7, sum_tna[5], data_format_total)
		worksheet.write(x,8, sum_tna[6], data_format_total)
		worksheet.write(x,9, sum_tna[7], data_format_total)
		worksheet.write(x,10, sum_tna[8], data_format_total)
		worksheet.write(x,11, sum_tna[9], data_format_total)

		worksheet.write(x,12, sum_tna[10], data_format_total)
		worksheet.write(x,13, sum_tna[11], data_format_total)

		worksheet.write(x,14, (sum_tna[12]/float(len(tna))), data_format_total)
		worksheet.write(x,15, (sum_tna[13]/float(len(tna))), data_format_total)
		worksheet.write(x,16, sum_tna[14], data_format_total)
		worksheet.write(x,17, (sum_tna[14]/sum_tna[11]) if sum_tna[9] != 0 else 0, data_format_total)
		worksheet.write(x,18, sum_tna[16], data_format_total)
		worksheet.write(x,19, sum_tna[17], data_format_total)
		worksheet.write(x,20, sum_tna[18], data_format_total)
		worksheet.write(x,21, ((sum_tna[16]+sum_tna[16])/sum_tna[11]) if sum_tna[11] != 0 else 0, data_format_total)
		worksheet.write(x,22, sum_tna[19], data_format_total)
		worksheet.write(x,23, (sum_tna[20]/float(len(tna))), data_format_total)
		worksheet.write(x,24, (sum_tna[21]/float(len(tna))), data_format_total)
		worksheet.write(x,25, (sum_tna[22]/float(len(tna))), data_format_total)


		worksheet.write(x,27, u'Totales', data_format_total)
		worksheet.write(x,28, sum_tep[0], data_format_total)
		worksheet.write(x,29, sum_tep[1], data_format_total)
		worksheet.write(x,30, sum_tep[2], data_format_total)

		worksheet.write(x,32, u'Totales', data_format_total)
		worksheet.write(x,33, '', data_format_total)
		worksheet.write(x,34, sum_tcd[0], data_format_total)
		worksheet.write(x,35, '', data_format_total)
		worksheet.write(x,36, sum_tcd[1], data_format_total)
		worksheet.write(x,37, '', data_format_total)
		worksheet.write(x,38, sum_tcd[2], data_format_total)
		worksheet.write(x,39, sum_tcd[3], data_format_total)

		worksheet.write(x,41,'Totales', data_format_total)
		worksheet.write(x,42, tid[-1].diesel_gen1 if len(tid) > 0 else 0, data_format_total)
		worksheet.write(x,43, tid[-1].diesel_gen2 if len(tid) > 0 else 0, data_format_total)
		worksheet.write(x,44, tid[-1].diesel_comp if len(tid) > 0 else 0, data_format_total)
		worksheet.write(x,45, tid[-1].agua_comp if len(tid) > 0 else 0, data_format_total)

		x = 48

		worksheet.merge_range(x,2,x,13, u'Indicadores de Operación', merge_format_t32)
		x+=1
		worksheet.merge_range(x,2,x,5, u'Concepto', merge_format_t32)
		worksheet.merge_range(x,6,x,11, u'Cantidad', merge_format_t32)
		worksheet.merge_range(x,12,x,13, u'Unidades', merge_format_t32)

		x += 1
		tio = self.env['trituracion.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
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
		
		f = open( direccion + u'Trituracion_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx', 'rb')
			
		vals = {
			'output_name': u'Trituracion_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx',
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