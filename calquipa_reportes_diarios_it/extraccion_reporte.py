# -*- encoding: utf-8 -*-
import base64
from openerp import models, fields, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp

import calendar
import datetime
import decimal

class extraccion_perforacion(models.Model):
	_name = 'extraccion.perforacion'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')

	horas_operacion = fields.Float('Hrs Oper. Perf. No. 1')
	metros_lineales = fields.Float('Metros lineales Perfo.')
	metros_hora = fields.Float('Metros/Hora', compute="get_metros_hora")
	consumo_diesel = fields.Float('Consumo Diesel')
	consumo_gls = fields.Float('Consumo Gls/Mt', compute="get_consumo_gls")
	pit1_produc = fields.Float('Pit1 Tons (Produc.)')
	pit1_desmont = fields.Float('Pit1 Tons (Desmont.)')
	pit2_tons = fields.Float('Pit2 Tons')
	pit3_tons = fields.Float('pit3 Tons')
	pit4_tons = fields.Float('pit4 Tons')
	boster = fields.Float('Alto Explosivo, Boster (Unidades)')
	anfo = fields.Float('Bajo Explosivo, Anfo (KG)')
	mecha = fields.Float('Mecha para Explosivo (m)')
	exanel = fields.Float('Det. no Elec. Exanel')
	fulminante = fields.Float('Fulminante Detonador')
	np = fields.Float(u'Cordón NP')
	unidireccional = fields.Float('Retaro, Conect Unidireccional')
	cons_explosivo = fields.Float('Cons. Explosivo')
	grs_ton = fields.Float('Grs/Ton', compute="get_grs_ton")

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
	def get_metros_hora(self):
		if self.horas_operacion != 0:
			self.metros_hora = (self.metros_lineales / self.horas_operacion) if self.horas_operacion != 0 else 0
		else:
			self.metros_hora = 0

	@api.one
	def get_consumo_gls(self):
		if self.metros_lineales != 0:
			self.consumo_gls = (self.consumo_diesel / self.metros_lineales) if self.metros_lineales != 0 else 0
		else:
			self.consumo_gls = 0

	@api.one
	def get_grs_ton(self):
		sump = self.pit1_produc + self.pit1_desmont + self.pit2_tons + self.pit3_tons + self.pit4_tons
		if sump != 0:
			self.grs_ton = (self.cons_explosivo / sump) if sump != 0 else 0
		else:
			self.grs_ton = 0

	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "extraccion.perforacion",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['extraccion.perforacion'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['extraccion.perforacion'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "extraccion.perforacion",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class extraccion_carga_acarreo(models.Model):
	_name = 'extraccion.carga.acarreo'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')

	hrs_oper = fields.Float('Hrs Oper. Cargador')
	consumo_diesel = fields.Float('Consumo Diesel')
	hrs_excavd2 = fields.Float('Hrs Oper. Excav336 d2')
	costo_hr_d2 = fields.Float('Costo S/./Hr')
	hrs_martillo = fields.Float('Hrs Oper. Excav336 dl MARTILLO')
	costo_hr_martillo = fields.Float('Costo S/./Hr')
	hrs_excavdl = fields.Float('Hrs Oper. Excav336 dl CUCHARON')
	costo_hr_dl = fields.Float('Costo S/./Hr')
	hrs_volq01 = fields.Float('Hrs Oper. Volq 01 V7L 746')
	costo_volq01 = fields.Float('Costo S/./Hr')
	hrs_volq02 = fields.Float('Hrs Oper. Volq 02 AJW 935')
	costo_volq02 = fields.Float('Costo S/./Hr')
	hrs_volq03 = fields.Float('Hrs Oper. Volq 03 V7P 815')
	costo_volq03 = fields.Float('Costo S/./Hr')
	hrs_volq04 = fields.Float('Hrs Oper. Volq 04 V7T 855')
	costo_volq04 = fields.Float('Costo S/./Hr')
	hrs_volq05 = fields.Float('Hrs Oper. Volq 05 AFL 874')
	costo_volq05 = fields.Float('Costo S/./Hr')
	hrs_volq06 = fields.Float('Hrs Oper. Volq 06 AFK 817')
	costo_volq06 = fields.Float('Costo S/./Hr')
	hrs_volqv5 = fields.Float('Hrs Oper. Volq V5M 856')
	costo_volqv5 = fields.Float('Costo S/./Hr')
	hrs_volq07 = fields.Float('Hrs Oper. Volq 07 F2P 701')
	costo_volq07 = fields.Float('Costo S/./Hr')
	hrs_d7r = fields.Float('Hrs Oper. D7R')
	costo_d7r = fields.Float('Costo S/./Hr')
	hrs_rodillo = fields.Float('Hrs Oper. Rodillo')
	costo_rodillo = fields.Float('Costo S/./Hr')
	hrs_motoconf = fields.Float('Hrs Oper. Motoconf')
	costo_motoconf = fields.Float('Costo S/./Hr')
	hrs_cargador = fields.Float('Hrs Oper. Cargador')
	costo_cargador = fields.Float('Costo S/./Hr')
	total_diesel_acarreo = fields.Float('Total Diesel Acarreo', compute="get_total_diesel_acarreo")
	total_diesel_exac = fields.Float('Total Diesel Ext y Acarreo', compute="get_total_diesel_exac")
	consumo_h2o = fields.Float('Consumo H2O Caminos')

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
	def get_total_diesel_acarreo(self):
		self.total_diesel_acarreo = self.consumo_diesel

	@api.one
	def get_total_diesel_exac(self):
		ep = self.env['extraccion.perforacion'].search([('date','=',self.date)])
		if len(ep) > 0:
			ep = ep[0]
			self.total_diesel_exac = ep.consumo_diesel + self.total_diesel_acarreo
		else:
			self.total_diesel_exac = self.total_diesel_acarreo

	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "extraccion.carga.acarreo",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['extraccion.carga.acarreo'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['extraccion.carga.acarreo'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "extraccion.carga.acarreo",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class extraccion_compra_insumos(models.Model):
	_name = 'extraccion.compra.insumos'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')

	boster = fields.Float('Alto Explosivo, Boster (Unidades)')
	anfo = fields.Float('Bajo Explosivo, Anfo (KG)')
	mecha = fields.Float('Mecha para Explosivo (m)')
	exanel = fields.Float('Det. no Elec. Exanel')
	fulminante = fields.Float('Fulminante Detonador')
	np = fields.Float(u'Cordón NP')
	unidireccional = fields.Float('Retaro, Conect Unidireccional')
	vale_perfora = fields.Char(u'N° de vale perforadora')
	diesel = fields.Float('Diesel de perforadora')
	vale_cargador = fields.Char(u'N° de vale de cargador frontal')
	cargador = fields.Float(u'Diesel de cargador frontal')
	nro_vale = fields.Char(u'Nro de vale')
	excavadora = fields.Float(u'Excavadora')

	agua = fields.Float('Agua')

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
				"res_model": "extraccion.compra.insumos",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['extraccion.compra.insumos'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['extraccion.compra.insumos'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "extraccion.compra.insumos",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class extraccion_inventario_insumos(models.Model):
	_name = 'extraccion.inventario.insumos'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')

	boster = fields.Float('Alto Explosivo, Boster (Unidades)', compute="compute_boster")
	anfo = fields.Float('Bajo Explosivo, Anfo (KG)', compute="compute_anfo")
	mecha = fields.Float('Mecha para Explosivo (m)', compute="compute_mecha")
	exanel = fields.Float('Det. no Elec. Exanel', compute="compute_exanel")
	fulminante = fields.Float('Fulminante Detonador', compute="compute_fulminante")
	np = fields.Float(u'Cordón NP', compute="compute_np")
	unidireccional = fields.Float('Retaro, Conect Unidireccional', compute="compute_unidireccional")
	diesel = fields.Float('Diesel perforadora', compute="get_diesel")
	diesel_carga = fields.Float('Diesel cargador', compute="get_diesel_carga")
	agua = fields.Float('Agua', compute="get_agua")

	"""                         INVENTARIO INICIAL                         """

	inv_boster = fields.Float('Alto Explosivo, Boster (Unidades)', compute="compute_inv_boster")
	inv_anfo = fields.Float('Bajo Explosivo, Anfo (KG)', compute="compute_inv_anfo")
	inv_mecha = fields.Float('Mecha para Explosivo (m)', compute="compute_inv_mecha")
	inv_exanel = fields.Float('Det. no Elec. Exanel', compute="compute_inv_exanel")
	inv_fulminante = fields.Float('Fulminante Detonador', compute="compute_inv_fulminante")
	inv_np = fields.Float(u'Cordón NP', compute="compute_inv_np")
	inv_unidireccional = fields.Float('Retaro, Conect Unidireccional', compute="compute_inv_unidireccional")
	inv_diesel = fields.Float('Diesel', compute="compute_inv_diesel")
	inv_diesel_carg = fields.Float('Diesel Cargador', compute="compute_inv_diesel_carg")

	@api.one
	def compute_inv_boster(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(eii) > 0:
			eii = eii[-1]
			self.inv_boster = eii.boster
		else:
			self.inv_boster = 0

	@api.one
	def compute_inv_anfo(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(eii) > 0:
			eii = eii[-1]
			self.inv_anfo = eii.anfo
		else:
			self.inv_anfo = 0

	@api.one
	def compute_inv_mecha(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(eii) > 0:
			eii = eii[-1]
			self.inv_mecha = eii.mecha
		else:
			self.inv_mecha = 0

		# eii = self.env['extraccion.inventario.insumos'].search([('month_id','=',prev_month),('year_id','=',prev_year)])
		# prev_total = 0
		# for i in eii:
		# 	prev_total += i.mecha

		# prev_total += eii[0].inv_mecha if len(eii) > 0 else 0
		# self.inv_mecha = prev_total

	@api.one
	def compute_inv_exanel(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(eii) > 0:
			eii = eii[-1]
			self.inv_exanel = eii.exanel
		else:
			self.inv_exanel = 0

	@api.one
	def compute_inv_fulminante(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(eii) > 0:
			eii = eii[-1]
			self.inv_fulminante = eii.fulminante
		else:
			self.inv_fulminante = 0

	@api.one
	def compute_inv_np(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(eii) > 0:
			eii = eii[-1]
			self.inv_np = eii.np
		else:
			self.inv_np = 0

	@api.one
	def compute_inv_unidireccional(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(eii) > 0:
			eii = eii[-1]
			self.inv_unidireccional = eii.unidireccional
		else:
			self.inv_unidireccional = 0

	@api.one
	def compute_inv_diesel(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(eii) > 0:
			eii = eii[-1]
			self.inv_diesel = eii.diesel
		else:
			self.inv_diesel = 0

	@api.one
	def compute_inv_diesel_carg(self):
		prev_date = datetime.datetime.strptime(self.date,"%Y-%m-%d") - datetime.timedelta(days=1)
		eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)]).sorted(key=lambda r: r.date)
		if len(eii) > 0:
			eii = eii[-1]
			self.inv_diesel_carg = eii.diesel_carga
		else:
			self.inv_diesel_carg = 0

	@api.multi
	def compute_boster(self):
		sum_eii = 0
		for eii in self.env['extraccion.inventario.insumos'].search([]):
			ep  = self.env['extraccion.perforacion'].search([('date','=',eii.date)])
			eci = self.env['extraccion.compra.insumos'].search([('date','=',eii.date)])
			if len(ep):
				sum_eii -= ep[0].boster
			if len(eci):
				sum_eii += eci[0].boster
			eii.boster = sum_eii

		# prev_date = datetime.datetime.strptime(self.date, "%Y-%m-%d") - datetime.timedelta(days=1)
		# ep = self.env['extraccion.perforacion'].search([('date','=',self.date)])
		# eci = self.env['extraccion.compra.insumos'].search([('date','=',self.date)])
		# eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)])
		# if (len(eii) > 0 and len(ep) > 0 and len(eci) > 0):
		# 	eii = eii[0]
		# 	ep = ep[0]
		# 	eci = eci[0]
		# 	self.boster = eii.boster - ep.boster + eci.boster
		# else:
		# 	self.boster = 0

	@api.multi
	def compute_anfo(self):
		sum_eii = 0
		for eii in self.env['extraccion.inventario.insumos'].search([]):
			ep  = self.env['extraccion.perforacion'].search([('date','=',eii.date)])
			eci = self.env['extraccion.compra.insumos'].search([('date','=',eii.date)])
			if len(ep):
				sum_eii -= ep[0].anfo
			if len(eci):
				sum_eii += eci[0].anfo
			eii.anfo = sum_eii
		# prev_date = datetime.datetime.strptime(self.date, "%Y-%m-%d") - datetime.timedelta(days=1)
		# ep = self.env['extraccion.perforacion'].search([('date','=',self.date)])
		# eci = self.env['extraccion.compra.insumos'].search([('date','=',self.date)])
		# eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)])
		# if (len(eii) > 0 and len(ep) > 0 and len(eci) > 0):
		# 	eii = eii[0]
		# 	ep = ep[0]
		# 	eci = eci[0]
		# 	self.anfo = eii.anfo - ep.anfo + eci.anfo
		# else:
		# 	self.anfo = 0

	@api.multi
	def compute_mecha(self):
		sum_eii = 0
		for eii in self.env['extraccion.inventario.insumos'].search([]):
			ep  = self.env['extraccion.perforacion'].search([('date','=',eii.date)])
			eci = self.env['extraccion.compra.insumos'].search([('date','=',eii.date)])
			if len(ep):
				sum_eii -= ep[0].mecha
			if len(eci):
				sum_eii += eci[0].mecha
			eii.mecha = sum_eii
		# prev_date = datetime.datetime.strptime(self.date, "%Y-%m-%d") - datetime.timedelta(days=1)
		# ep = self.env['extraccion.perforacion'].search([('date','=',self.date)])
		# eci = self.env['extraccion.compra.insumos'].search([('date','=',self.date)])
		# eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)])
		# if (len(eii) > 0 and len(ep) > 0 and len(eci) > 0):
		# 	eii = eii[0]
		# 	ep = ep[0]
		# 	eci = eci[0]
		# 	self.mecha = eii.mecha - ep.mecha + eci.mecha
		# else:
		# 	self.mecha = 0

	@api.multi
	def compute_exanel(self):
		sum_eii = 0
		for eii in self.env['extraccion.inventario.insumos'].search([]):
			ep  = self.env['extraccion.perforacion'].search([('date','=',eii.date)])
			eci = self.env['extraccion.compra.insumos'].search([('date','=',eii.date)])
			if len(ep):
				sum_eii -= ep[0].exanel
			if len(eci):
				sum_eii += eci[0].exanel
			eii.exanel = sum_eii
		# prev_date = datetime.datetime.strptime(self.date, "%Y-%m-%d") - datetime.timedelta(days=1)
		# ep = self.env['extraccion.perforacion'].search([('date','=',self.date)])
		# eci = self.env['extraccion.compra.insumos'].search([('date','=',self.date)])
		# eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)])
		# if (len(eii) > 0 and len(ep) > 0 and len(eci) > 0):
		# 	eii = eii[0]
		# 	ep = ep[0]
		# 	eci = eci[0]
		# 	self.exanel = eii.exanel - ep.exanel + eci.exanel
		# else:
		# 	self.exanel = 0

	@api.multi
	def compute_fulminante(self):
		sum_eii = 0
		for eii in self.env['extraccion.inventario.insumos'].search([]):
			ep  = self.env['extraccion.perforacion'].search([('date','=',eii.date)])
			eci = self.env['extraccion.compra.insumos'].search([('date','=',eii.date)])
			if len(ep):
				sum_eii -= ep[0].fulminante
			if len(eci):
				sum_eii += eci[0].fulminante
			eii.fulminante = sum_eii
		# prev_date = datetime.datetime.strptime(self.date, "%Y-%m-%d") - datetime.timedelta(days=1)
		# ep = self.env['extraccion.perforacion'].search([('date','=',self.date)])
		# eci = self.env['extraccion.compra.insumos'].search([('date','=',self.date)])
		# eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)])
		# if (len(eii) > 0 and len(ep) > 0 and len(eci) > 0):
		# 	eii = eii[0]
		# 	ep = ep[0]
		# 	eci = eci[0]
		# 	self.fulminante = eii.fulminante - ep.fulminante + eci.fulminante
		# else:
		# 	self.fulminante = 0

	@api.multi
	def compute_np(self):
		sum_eii = 0
		for eii in self.env['extraccion.inventario.insumos'].search([]):
			ep  = self.env['extraccion.perforacion'].search([('date','=',eii.date)])
			eci = self.env['extraccion.compra.insumos'].search([('date','=',eii.date)])
			if len(ep):
				sum_eii -= ep[0].np
			if len(eci):
				sum_eii += eci[0].np
			eii.np = sum_eii
		# prev_date = datetime.datetime.strptime(self.date, "%Y-%m-%d") - datetime.timedelta(days=1)
		# ep = self.env['extraccion.perforacion'].search([('date','=',self.date)])
		# eci = self.env['extraccion.compra.insumos'].search([('date','=',self.date)])
		# eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)])
		# if (len(eii) > 0 and len(ep) > 0 and len(eci) > 0):
		# 	eii = eii[0]
		# 	ep = ep[0]
		# 	eci = eci[0]
		# 	self.np = eii.np - ep.np + eci.np
		# else:
		# 	self.np = 0

	@api.multi
	def compute_unidireccional(self):
		sum_eii = 0
		for eii in self.env['extraccion.inventario.insumos'].search([]):
			ep  = self.env['extraccion.perforacion'].search([('date','=',eii.date)])
			eci = self.env['extraccion.compra.insumos'].search([('date','=',eii.date)])
			if len(ep):
				sum_eii -= ep[0].unidireccional
			if len(eci):
				sum_eii += eci[0].unidireccional
			eii.unidireccional = sum_eii
		# prev_date = datetime.datetime.strptime(self.date, "%Y-%m-%d") - datetime.timedelta(days=1)
		# ep = self.env['extraccion.perforacion'].search([('date','=',self.date)])
		# eci = self.env['extraccion.compra.insumos'].search([('date','=',self.date)])
		# eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)])
		# if (len(eii) > 0 and len(ep) > 0 and len(eci) > 0):
		# 	eii = eii[0]
		# 	ep = ep[0]
		# 	eci = eci[0]			
		# 	self.unidireccional = eii.unidireccional - ep.unidireccional + eci.unidireccional
		# else:
		# 	self.unidireccional = 0

	@api.multi
	def get_diesel(self):
		sum_eii = 0
		for eii in self.env['extraccion.inventario.insumos'].search([]):
			eca = self.env['extraccion.carga.acarreo'].search([('date','=',eii.date)])
			eci = self.env['extraccion.compra.insumos'].search([('date','=',eii.date)])
			if len(eca):
				sum_eii -= eca[0].total_diesel_exac
			if len(eci):
				sum_eii += eci[0].diesel
			eii.diesel = sum_eii
		# prev_date = datetime.datetime.strptime(self.date, "%Y-%m-%d") - datetime.timedelta(days=1)
		# eca = self.env['extraccion.carga.acarreo'].search([('date','=',self.date)])
		# eci = self.env['extraccion.compra.insumos'].search([('date','=',self.date)])
		# eii = self.env['extraccion.inventario.insumos'].search([('date','=',prev_date)])
		# if (len(eii) > 0 and len(eca) > 0 and len(eci) > 0):
		# 	eii = eii[0]
		# 	eca = eca[0]
		# 	eci = eci[0]
		# 	self.diesel = eii.diesel - eca.total_diesel_exac + eci.diesel
		# else:
		# 	self.diesel = 0

	@api.multi
	def get_diesel_carga(self):
		sum_eii = 0
		for eii in self.env['extraccion.inventario.insumos'].search([]):
			eca = self.env['extraccion.carga.acarreo'].search([('date','=',eii.date)])
			eci = self.env['extraccion.compra.insumos'].search([('date','=',eii.date)])
			if len(eca):
				sum_eii -= eca[0].consumo_diesel
			if len(eci):
				sum_eii += eci[0].cargador
			eii.diesel_carga = sum_eii

	@api.one
	def get_agua(self):
		ecl = self.env['extraccion.compra.insumos'].search([('date','=',self.date)])
		eca = self.env['extraccion.carga.acarreo'].search([('date','=',self.date)])
		self.agua = 0
		if len(ecl) > 0:
			ecl = ecl[0]
			self.agua += ecl.agua + eca.consumo_h2o
		else:
			self.agua += 0

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
				"res_model": "extraccion.inventario.insumos",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['extraccion.inventario.insumos'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['extraccion.inventario.insumos'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "extraccion.inventario.insumos",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class extraccion_indicadores_operacion(models.Model):
	_name = 'extraccion.indicadores.operacion'

	_order = 'id'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	concepto = fields.Char('Concepto')
	cantidad = fields.Float('Cantidad')
	unidades = fields.Char('Unidades')

	dias_transcurridos = fields.Integer('Dias Transcurridos')

	@api.multi
	def display_q(self, mnth, yr, dt, om, oh, hp):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "extraccion.indicadores.operacion",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		
		conc = [(u'Objetivo Mes',u'Metros'),
				(u'Tendencia Mes',u'Metros'),
				(u'Acumulado Mes',u'Metros'),
				(u'Diferencia Objetivo vs Real',u'Metros'),
				(u'Objetivo de Hrs de Operación Mes',u'Horas'),
				(u'Hrs Empleadas Perforación',u'Horas'),
				(u'Promedio Metros Perforados',u'Mts/Hr'),
				(u'Promedio Día',u'Mts/Día'),
				(u'Días de Perforación',u'Días'),
				(u'Toneladas Explotadas',u'Toneladas'),
				(u'Promedio de Consumo Explosivo',u'Grs/Ton'),
				(u'Promedio de Consumo Diesel',u'Galones/Metro'),]
		dias_mes = calendar.monthrange(yr, mnth)[1]

		eio = self.env['extraccion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth)])
		if len(eio) == 0:
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
					vals['cantidad'] = self.env['extraccion.funciones'].get_metros_lineales_dt(mnth, yr, dt, dias_mes)

				if vals['concepto'] == conc[2][0]:
					vals['cantidad'] = self.env['extraccion.funciones'].get_metros_lineales(mnth, yr)

				if vals['concepto'] == conc[3][0]:
					eioc1 = self.env['extraccion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',conc[0][0])])[0]
					eioc3 = self.env['extraccion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',conc[2][0])])[0]
					vals['cantidad'] = eioc1.cantidad - eioc3.cantidad

				if vals['concepto'] == conc[4][0]:
					vals['cantidad'] = oh

				if vals['concepto'] == conc[5][0]:
					vals['cantidad'] = hp

				if vals['concepto'] == conc[6][0]:
					ep = self.env['extraccion.perforacion'].search([('year_id','=',yr),('month_id','=',mnth)])
					s = 0
					for i in ep:
						s += i.metros_hora
					vals['cantidad'] = s/len(ep)

				if vals['concepto'] == conc[7][0]:
					eioc7 = self.env['extraccion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',conc[6][0])])[0]
					vals['cantidad'] = eioc7.cantidad * 24

				if vals['concepto'] == conc[8][0]:
					vals['cantidad'] = self.env['extraccion.funciones'].get_horas_operacion(mnth, yr)

				if vals['concepto'] == conc[9][0]:
					vals['cantidad'] = self.env['extraccion.funciones'].get_pit4_tons(mnth, yr)

				if vals['concepto'] == conc[10][0]:
					vals['cantidad'] = self.env['extraccion.funciones'].get_cons_explosivo(mnth, yr)

				if vals['concepto'] == conc[11][0]:
					vals['cantidad'] = self.env['extraccion.funciones'].get_consumo_diesel(mnth, yr)

				neio = self.env['extraccion.indicadores.operacion'].create(vals)
		else:		
			for i in eio:
				i.dias_transcurridos = dt
				if i.concepto == conc[0][0]:
					i.cantidad = om
				if i.concepto == conc[4][0]:
					i.cantidad = oh
				if i.concepto == conc[5][0]:
					i.cantidad = hp

		return {
			"type": "ir.actions.act_window",
			"res_model": "extraccion.indicadores.operacion",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class extraccion_funciones(models.Model):
	_name = 'extraccion.funciones'

	def get_metros_lineales_dt(self, mnth, yr, dt, dias_mes):
		self.env.cr.execute("""
			select sum(metros_lineales)/"""+str(dias_mes)+"""*"""+str(dt)+""" from extraccion_perforacion
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+""" and
				fecha_num(date::date) between fecha_num('"""+str(yr)+"""-"""+format(mnth,'02')+"""-01'::date) and fecha_num('"""+str(yr)+"""-"""+format(mnth,'02')+"""-"""+format(dt,'02')+"""'::date)
		""")
		return self.env.cr.fetchall()[0][0]

	def get_metros_lineales(self, mnth, yr):
		self.env.cr.execute("""
			select sum(metros_lineales) from extraccion_perforacion
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_horas_operacion(self, mnth, yr):
		self.env.cr.execute("""
			select sum(horas_operacion)/24 from extraccion_perforacion
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_pit4_tons(self,mnth, yr):
		self.env.cr.execute("""
			select sum(pit4_tons) from extraccion_perforacion
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_cons_explosivo(self, mnth, yr):
		self.env.cr.execute("""
			select sum(cons_explosivo)/sum(pit1_produc)*1000 from extraccion_perforacion
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_consumo_diesel(self, mnth, yr):
		self.env.cr.execute("""
			select sum(consumo_diesel)/sum(metros_lineales) from extraccion_perforacion
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]


class extraccion_reporte(models.Model):
	_name = 'extraccion.reporte'

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
		workbook = Workbook( direccion + u'Extraccion_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx')
		worksheet = workbook.add_worksheet("Extraccion")

		month2name = {
			1: u"Enero",
			2: u"Febrero",
			3: u"Marzo",
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
		worksheet.set_column("V:V", 3.86)
		worksheet.set_column("BG:BG", 3.86)
		worksheet.set_column("BV:BV", 3.86)

		worksheet.set_column("B:B", 7.86)
		worksheet.set_column("C:C", 9.14)
		worksheet.set_column("D:D", 11.86)
		worksheet.set_column("E:E", 10.57)
		worksheet.set_column("F:F", 10.29)
		worksheet.set_column("G:G", 10.71)

		worksheet.merge_range("B2:G8", '', merge_format_t)
		worksheet.merge_range("H2:BY8", u'Calquipa', merge_format_t)
		worksheet.merge_range("BZ2:CB2", u'Fecha:', merge_format_ca)
		worksheet.merge_range("CC2:CD2", datetime.datetime.today().strftime("%Y-%m-%d"), merge_format_ca2)
		worksheet.merge_range("BZ3:CB3", u'Mes:', merge_format_ca)
		worksheet.merge_range("CC3:CD3", month2name[mnth], merge_format_ca2)
		worksheet.merge_range("BZ4:CB4", u'Días de Mes:', merge_format_ca)
		worksheet.merge_range("CC4:CD4", calendar.monthrange(yr,mnth)[1], merge_format_ca2)
		worksheet.merge_range("BZ5:CB5", u'Días Transcurridos Mes:', merge_format_ca)

		eio = self.env['extraccion.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
		if len(eio) > 0:
			eio = eio[0]
			worksheet.merge_range("CC5:CD5", eio.dias_transcurridos, merge_format_ca2)
		else:
			worksheet.merge_range("CC5:CD5", '', merge_format_ca2)

		worksheet.merge_range("BZ6:CB6", u'Hrs Mes:', merge_format_ca)
		worksheet.merge_range("CC6:CD6", u'', merge_format_ca2)
		worksheet.merge_range("BZ7:CB7", u'Clave SGI', merge_format_ca)
		worksheet.merge_range("CC7:CD7", u'', merge_format_ca2)
		worksheet.merge_range("BZ8:CB8", u'Folio', merge_format_ca)
		worksheet.merge_range("CC8:CD8", u'', merge_format_ca2)

		worksheet.insert_image('C3', 'calquipalright.png', {'x_scale': 1.5, 'y_scale': 1.5})
		worksheet.insert_image('I3', 'calquipalleft.png', {'x_scale': 1.5, 'y_scale': 1.5})

		worksheet.set_row(9, 21)
		worksheet.merge_range("B10:CF10", u'Extracción', merge_format_t)

		worksheet.set_row(11, 20)
		worksheet.merge_range("B12:U12", u'Perforación', merge_format_t2)
		worksheet.merge_range("W12:BF12", u'Carga y Acarreo', merge_format_t2)
		worksheet.merge_range("BH12:BU12", u'Compra de Insumos', merge_format_t2)
		worksheet.merge_range("BW12:CF12", u'Inventario de Insumos', merge_format_t2)

		worksheet.set_row(12, 20.25)
		worksheet.set_row(13, 33)
		worksheet.set_row(14, 12)
		worksheet.merge_range("B13:B15", u'Fecha', merge_format_t31)
		worksheet.merge_range("C13:C15", u'Hrs. Oper\n Perf. No 1', merge_format_t32)
		worksheet.merge_range("D13:D15", u'Metros\n lineales Perfo', merge_format_t32)
		worksheet.merge_range("E13:E15", u'Metros/\n Hora', merge_format_t32)
		worksheet.merge_range("F13:F15", u'Consumo\n Diesel', merge_format_t32)
		worksheet.merge_range("G13:G15", u'Consumo\n Gls / Mt', merge_format_t32)
		worksheet.merge_range("H13:U13", u'Explosivo', merge_format_t32)
		worksheet.merge_range("H14:I14", u'PIT No.1 Tons', merge_format_t32)
		worksheet.write("H15", u'Produc.', merge_format_t32)
		worksheet.write("I15", u'Desmonte', merge_format_t32)
		worksheet.merge_range("J14:J15",'PIT No.2\n Tons', merge_format_t32)
		worksheet.merge_range("K14:K15",'PIT No.3\n Tons', merge_format_t32)
		worksheet.merge_range("L14:L15",'PIT No.4\n Tons', merge_format_t32)
		worksheet.merge_range("M14:M15",'Alto Explosivo, Boster (Unidades)', merge_format_t32)
		worksheet.merge_range("N14:N15",'Bajo Explosivo, Anfo (KG)', merge_format_t32)
		worksheet.merge_range("O14:O15",'Mecha para Explosivo (m)', merge_format_t32)
		worksheet.merge_range("P14:P15",'Det. no Elec. Exanel', merge_format_t32)
		worksheet.merge_range("Q14:Q15",'Fulminante Detonador', merge_format_t32)
		worksheet.merge_range("R14:R15",u'Cordón NP', merge_format_t32)
		worksheet.merge_range("S14:S15",'Retaro, Conect Unidireccional', merge_format_t32)
		worksheet.merge_range("T14:T15",'Cons. Explosivo kgs', merge_format_t32)
		worksheet.merge_range("U14:U15",'Gls/Ton', merge_format_t32)

		worksheet.merge_range("W13:W15", u'Fecha', merge_format_t31)
		worksheet.merge_range("X13:X15", u'Hrs. Oper\n Cargador', merge_format_t32)
		worksheet.merge_range("Y13:Y15", u'Consumo\n Diesel', merge_format_t32)
		worksheet.merge_range("Z13:Z15", u'Hrs Oper.\n Excav336\nd2', merge_format_t32)
		worksheet.merge_range("AA13:AA15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AB13:AB15", u'Hrs Oper.\n Excav336 dl MARTILLO', merge_format_t32)
		worksheet.merge_range("AC13:AC15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AD13:AD15", u'Hrs Oper.\n Excav336 dl CUCHARON', merge_format_t32)
		worksheet.merge_range("AE13:AE15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AF13:AF15", u'Hrs Oper.\n Volq 01 V7L 746', merge_format_t32)
		worksheet.merge_range("AG13:AG15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AH13:AH15", u'Hrs Oper.\n Volq 02 AJW 935', merge_format_t32)
		worksheet.merge_range("AI13:AI15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AJ13:AJ15", u'Hrs Oper.\n Volq 03 V7P 815', merge_format_t32)
		worksheet.merge_range("AK13:AK15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AL13:AL15", u'Hrs Oper.\n Volq 04 V7T 855', merge_format_t32)
		worksheet.merge_range("AM13:AM15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AN13:AN15", u'Hrs Oper.\n Volq 05 AFL 874', merge_format_t32)
		worksheet.merge_range("AO13:AO15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AP13:AP15", u'Hrs Oper.\n Volq 06 AFK 817', merge_format_t32)
		worksheet.merge_range("AQ13:AQ15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AR13:AR15", u'Hrs Oper.\n Volq V5M 856', merge_format_t32)
		worksheet.merge_range("AS13:AS15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AT13:AT15", u'Hrs Oper.\n Volq 07 F2P 701', merge_format_t32)
		worksheet.merge_range("AU13:AU15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AV13:AV15", u'Hrs Oper.\n D7R', merge_format_t32)
		worksheet.merge_range("AW13:AW15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AX13:AX15", u'Hrs Oper.\n Rodillo', merge_format_t32)
		worksheet.merge_range("AY13:AY15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("AZ13:AZ15", u'Hrs Oper.\n Motoconf', merge_format_t32)
		worksheet.merge_range("BA13:BA15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("BB13:BB15", u'Hrs Oper.\n Cargador frontal', merge_format_t32)
		worksheet.merge_range("BC13:BC15", u'Costo\n S/. / Hr', merge_format_t32)
		worksheet.merge_range("BD13:BD15", u'Total Diesel\n Acarreo', merge_format_t32)
		worksheet.merge_range("BE13:BE15", u'Total Diesel\n Ext y Acarreo', merge_format_t32)
		worksheet.merge_range("BF13:BF15", u'Consumo\n H2O Caminos', merge_format_t32)

		worksheet.merge_range("BH13:BH15", u'Fecha', merge_format_t31)
		worksheet.merge_range("BI13:BO13", u'Explosivo', merge_format_t32)
		worksheet.merge_range("BI14:BI15",'Alto Explosivo, Boster (Unidades)', merge_format_t32)
		worksheet.merge_range("BJ14:BJ15",'Bajo Explosivo, Anfo (KG)', merge_format_t32)
		worksheet.merge_range("BK14:BK15",'Mecha para Explosivo (m)', merge_format_t32)
		worksheet.merge_range("BL14:BL15",'Det. no Elec. Exanel', merge_format_t32)
		worksheet.merge_range("BM14:BM15",'Fulminante Detonador', merge_format_t32)
		worksheet.merge_range("BN14:BN15",u'Cordón NP', merge_format_t32)
		worksheet.merge_range("BO14:BO15",'Retaro, Conect Unidireccional', merge_format_t32)
		worksheet.merge_range("BP13:BP15", u'N° de vale perforadora', merge_format_t32)
		worksheet.merge_range("BQ13:BQ15", u'Diesel de perforadora', merge_format_t32)
		worksheet.merge_range("BR13:BR15", u'N° de vale de cargador frontal', merge_format_t32)
		worksheet.merge_range("BS13:BS15", u'Diesel de cargador frontal', merge_format_t32)
		worksheet.merge_range("BT13:BT15", u'Nro Vale Excavadora 336', merge_format_t32)
		worksheet.merge_range("BU13:BU15", u'Excavadora 336', merge_format_t32)
		#worksheet.merge_range("BO13:BO15", u'Agua', merge_format_t32)

		worksheet.merge_range("BW13:BW14", u'Fecha', merge_format_t31)
		worksheet.merge_range("BX13:CD13", u'Explosivo', merge_format_t32)
		worksheet.write("BX14",'Alto Explosivo, Boster (Unidades)', merge_format_t32)
		worksheet.write("BY14",'Bajo Explosivo, Anfo (KG)', merge_format_t32)
		worksheet.write("BZ14",'Mecha para Explosivo (m)', merge_format_t32)
		worksheet.write("CA14",'Det. no Elec. Exanel', merge_format_t32)
		worksheet.write("CB14",'Fulminante Detonador', merge_format_t32)
		worksheet.write("CC14",u'Cordón NP', merge_format_t32)
		worksheet.write("CD14",'Retaro, Conect Unidireccional', merge_format_t32)
		worksheet.merge_range("CE13:CE14", u'Diesel perforadora', merge_format_t32)
		worksheet.merge_range("CF13:CF14", u'Diesel cargador', merge_format_t32)		
		#worksheet.write("BZ13:BZ15", u'Agua', merge_format_t32)

		peii = self.env['extraccion.inventario.insumos'].search([('year_id','=',yr),('month_id','=',mnth)])
		worksheet.write("BW15", u'Inv. Inicial', merge_format_t31)
		worksheet.write("BX15", peii[0].inv_boster if len(peii)>0 else 0, data_format_drgr)
		worksheet.write("BY15", peii[0].inv_anfo if len(peii)>0 else 0, data_format_drgr)
		worksheet.write("BZ15", peii[0].inv_mecha if len(peii)>0 else 0, data_format_drgr)
		worksheet.write("CA15", peii[0].inv_exanel if len(peii)>0 else 0, data_format_drgr)
		worksheet.write("CB15", peii[0].inv_fulminante if len(peii)>0 else 0, data_format_drgr)
		worksheet.write("CC15", peii[0].inv_np if len(peii)>0 else 0, data_format_drgr)
		worksheet.write("CD15", peii[0].inv_unidireccional if len(peii)>0 else 0, data_format_drgr)
		worksheet.write("CE15", peii[0].inv_diesel if len(peii)>0 else 0, data_format_drgr)
		worksheet.write("CF15", peii[0].inv_diesel_carg if len(peii)>0 else 0, data_format_drgr)

		ep = self.env['extraccion.perforacion'].search([('year_id','=',yr),('month_id','=',mnth)])
		eca = self.env['extraccion.carga.acarreo'].search([('year_id','=',yr),('month_id','=',mnth)])
		eci = self.env['extraccion.compra.insumos'].search([('year_id','=',yr),('month_id','=',mnth)])
		eii = self.env['extraccion.inventario.insumos'].search([('year_id','=',yr),('month_id','=',mnth)])
		eio = self.env['extraccion.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])

		print len(ep),len(eca),len(eci),len(eii),len(eio)
		if len(ep) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de PERFORACION para el periodo seleccionado.")
		if len(eca) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de CARGA Y ACARREO para el periodo seleccionado.")
		if len(eci) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de CONSUMO DE INSUMOS para el periodo seleccionado.")
		if len(eii) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de INVENTARIO DE INSUMOS para el periodo seleccionado.")
		if len(eio) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de INDICADORES DE OPERACION para el periodo seleccionado.")
		

		sum_ep = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		sum_eca = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		sum_eci = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		sum_eii = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

		sum_eii[0] += eii[0].inv_boster if len(eii) > 0 else 0
		sum_eii[1] += eii[0].inv_anfo if len(eii) > 0 else 0
		sum_eii[2] += eii[0].inv_mecha if len(eii) > 0 else 0
		sum_eii[3] += eii[0].inv_exanel if len(eii) > 0 else 0
		sum_eii[4] += eii[0].inv_fulminante if len(eii) > 0 else 0
		sum_eii[5] += eii[0].inv_np if len(eii) > 0 else 0
		sum_eii[6] += eii[0].inv_unidireccional if len(eii) > 0 else 0
		sum_eii[7] += eii[0].inv_diesel if len(eii) > 0 else 0
		sum_eii[8] += eii[0].inv_diesel_carg if len(eii) > 0 else 0

		x = 15
		for i in range(len(ep)):
			fch = format(i+1,'02')+'-'+month2name[mnth][:3]
			worksheet.write(x,1, fch, data_format_dlr)
			worksheet.write(x,22, fch, data_format_dlr)
			worksheet.write(x,59, fch, data_format_dlr)
			worksheet.write(x,74, fch, data_format_dlr)
			if i % 2 == 0:
				worksheet.write(x,2, ep[i].horas_operacion, data_format_d)
				worksheet.write(x,3, ep[i].metros_lineales, data_format_d)
				worksheet.write(x,4, ep[i].metros_hora, data_format_d)
				worksheet.write(x,5, ep[i].consumo_diesel, data_format_d)
				worksheet.write(x,6, ep[i].consumo_gls, data_format_dr)
				worksheet.write(x,7, ep[i].pit1_produc, data_format_dr)
				worksheet.write(x,8, ep[i].pit1_desmont, data_format_dr)
				worksheet.write(x,9, ep[i].pit2_tons, data_format_dr)
				worksheet.write(x,10, ep[i].pit3_tons, data_format_dr)
				worksheet.write(x,11, ep[i].pit4_tons, data_format_dr)
				worksheet.write(x,12, ep[i].boster, data_format_dr)
				worksheet.write(x,13, ep[i].anfo, data_format_dr)
				worksheet.write(x,14, ep[i].mecha, data_format_dr)
				worksheet.write(x,15, ep[i].exanel, data_format_dr)
				worksheet.write(x,16, ep[i].fulminante, data_format_dr)
				worksheet.write(x,17, ep[i].np, data_format_dr)
				worksheet.write(x,18, ep[i].unidireccional, data_format_dr)
				worksheet.write(x,19, ep[i].cons_explosivo, data_format_dr)
				worksheet.write(x,20, ep[i].grs_ton, data_format_dr)
				
				worksheet.write(x,23, eca[i].hrs_oper, data_format_d)
				worksheet.write(x,24, eca[i].consumo_diesel, data_format_dr)
				worksheet.write(x,25, eca[i].hrs_excavd2, data_format_d)
				worksheet.write(x,26, eca[i].costo_hr_d2, data_format_dr)
				worksheet.write(x,27, eca[i].hrs_martillo, data_format_d)
				worksheet.write(x,28, eca[i].costo_hr_martillo, data_format_dr)
				worksheet.write(x,29, eca[i].hrs_excavdl, data_format_d)
				worksheet.write(x,30, eca[i].costo_hr_dl, data_format_dr)
				worksheet.write(x,31, eca[i].hrs_volq01, data_format_d)
				worksheet.write(x,32, eca[i].costo_volq01, data_format_dr)
				worksheet.write(x,33, eca[i].hrs_volq02, data_format_d)
				worksheet.write(x,34, eca[i].costo_volq02, data_format_dr)
				worksheet.write(x,35, eca[i].hrs_volq03, data_format_d)
				worksheet.write(x,36, eca[i].costo_volq03, data_format_dr)
				worksheet.write(x,37, eca[i].hrs_volq04, data_format_d)
				worksheet.write(x,38, eca[i].costo_volq04, data_format_dr)
				worksheet.write(x,39, eca[i].hrs_volq05, data_format_d)
				worksheet.write(x,40, eca[i].costo_volq05, data_format_dr)
				worksheet.write(x,41, eca[i].hrs_volq06, data_format_d)
				worksheet.write(x,42, eca[i].costo_volq06, data_format_dr)
				worksheet.write(x,43, eca[i].hrs_volqv5, data_format_d)
				worksheet.write(x,44, eca[i].costo_volqv5, data_format_dr)
				worksheet.write(x,45, eca[i].hrs_volq07, data_format_d)
				worksheet.write(x,46, eca[i].costo_volq07, data_format_dr)
				worksheet.write(x,47, eca[i].hrs_d7r, data_format_d)
				worksheet.write(x,48, eca[i].costo_d7r, data_format_dr)
				worksheet.write(x,49, eca[i].hrs_rodillo, data_format_d)
				worksheet.write(x,50, eca[i].costo_rodillo, data_format_dr)
				worksheet.write(x,51, eca[i].hrs_motoconf, data_format_d)
				worksheet.write(x,52, eca[i].costo_motoconf, data_format_dr)
				worksheet.write(x,53, eca[i].hrs_cargador, data_format_d)
				worksheet.write(x,54, eca[i].costo_cargador, data_format_dr)
				worksheet.write(x,55, eca[i].total_diesel_acarreo, data_format_d)
				worksheet.write(x,56, eca[i].total_diesel_exac, data_format_d)
				worksheet.write(x,57, eca[i].consumo_h2o, data_format_dr)
				
				worksheet.write(x,60, eci[i].boster, data_format_d)
				worksheet.write(x,61, eci[i].anfo, data_format_d)
				worksheet.write(x,62, eci[i].mecha, data_format_d)
				worksheet.write(x,63, eci[i].exanel, data_format_d)
				worksheet.write(x,64, eci[i].fulminante, data_format_d)
				worksheet.write(x,65, eci[i].np, data_format_d)
				worksheet.write(x,66, eci[i].unidireccional, data_format_dr)
				worksheet.write(x,67, eci[i].vale_perfora if eci[i].vale_perfora else '', data_format_dr)
				worksheet.write(x,68, eci[i].diesel, data_format_dr)
				worksheet.write(x,69, eci[i].vale_cargador if eci[i].vale_cargador else '', data_format_dr)
				worksheet.write(x,70, eci[i].cargador, data_format_dr)
				worksheet.write(x,71, eci[i].nro_vale if eci[i].nro_vale else '', merge_format_ca)
				worksheet.write(x,72, eci[i].excavadora if eci[i].excavadora else '', data_format_dr)
				#worksheet.write(x,66, eci[i].agua, data_format_dr)

				worksheet.write(x,75, eii[i].boster, data_format_d)
				worksheet.write(x,76, eii[i].anfo, data_format_d)
				worksheet.write(x,77, eii[i].mecha, data_format_d)
				worksheet.write(x,78, eii[i].exanel, data_format_d)
				worksheet.write(x,79, eii[i].fulminante, data_format_d)
				worksheet.write(x,80, eii[i].np, data_format_d)
				worksheet.write(x,81, eii[i].unidireccional, data_format_dr)
				worksheet.write(x,82, eii[i].diesel, data_format_dr)
				worksheet.write(x,83, eii[i].diesel_carga, data_format_dr)
				#worksheet.write(x,77, eii[i].agua, data_format_dr)

			else:
				worksheet.write(x,2, ep[i].horas_operacion, data_format_dgr)
				worksheet.write(x,3, ep[i].metros_lineales, data_format_dgr)
				worksheet.write(x,4, ep[i].metros_hora, data_format_dgr)
				worksheet.write(x,5, ep[i].consumo_diesel, data_format_dgr)
				worksheet.write(x,6, ep[i].consumo_gls, data_format_drgr)
				worksheet.write(x,7, ep[i].pit1_produc, data_format_drgr)
				worksheet.write(x,8, ep[i].pit1_desmont, data_format_drgr)
				worksheet.write(x,9, ep[i].pit2_tons, data_format_drgr)
				worksheet.write(x,10, ep[i].pit3_tons, data_format_drgr)
				worksheet.write(x,11, ep[i].pit4_tons, data_format_drgr)
				worksheet.write(x,12, ep[i].boster, data_format_drgr)
				worksheet.write(x,13, ep[i].anfo, data_format_drgr)
				worksheet.write(x,14, ep[i].mecha, data_format_drgr)
				worksheet.write(x,15, ep[i].exanel, data_format_drgr)
				worksheet.write(x,16, ep[i].fulminante, data_format_drgr)
				worksheet.write(x,17, ep[i].np, data_format_drgr)
				worksheet.write(x,18, ep[i].unidireccional, data_format_drgr)
				worksheet.write(x,19, ep[i].cons_explosivo, data_format_drgr)
				worksheet.write(x,20, ep[i].grs_ton, data_format_drgr)
				
				worksheet.write(x,23, eca[i].hrs_oper, data_format_dgr)
				worksheet.write(x,24, eca[i].consumo_diesel, data_format_drgr)
				worksheet.write(x,25, eca[i].hrs_excavd2, data_format_dgr)
				worksheet.write(x,26, eca[i].costo_hr_d2, data_format_drgr)
				worksheet.write(x,27, eca[i].hrs_martillo, data_format_dgr)
				worksheet.write(x,28, eca[i].costo_hr_martillo, data_format_drgr)
				worksheet.write(x,29, eca[i].hrs_excavdl, data_format_dgr)
				worksheet.write(x,30, eca[i].costo_hr_dl, data_format_drgr)
				worksheet.write(x,31, eca[i].hrs_volq01, data_format_dgr)
				worksheet.write(x,32, eca[i].costo_volq01, data_format_drgr)
				worksheet.write(x,33, eca[i].hrs_volq02, data_format_dgr)
				worksheet.write(x,34, eca[i].costo_volq02, data_format_drgr)
				worksheet.write(x,35, eca[i].hrs_volq03, data_format_dgr)
				worksheet.write(x,36, eca[i].costo_volq03, data_format_drgr)
				worksheet.write(x,37, eca[i].hrs_volq04, data_format_dgr)
				worksheet.write(x,38, eca[i].costo_volq04, data_format_drgr)
				worksheet.write(x,39, eca[i].hrs_volq05, data_format_dgr)
				worksheet.write(x,40, eca[i].costo_volq05, data_format_drgr)
				worksheet.write(x,41, eca[i].hrs_volq06, data_format_dgr)
				worksheet.write(x,42, eca[i].costo_volq06, data_format_drgr)
				worksheet.write(x,43, eca[i].hrs_volqv5, data_format_dgr)
				worksheet.write(x,44, eca[i].costo_volqv5, data_format_drgr)
				worksheet.write(x,45, eca[i].hrs_volq07, data_format_dgr)
				worksheet.write(x,46, eca[i].costo_volq07, data_format_drgr)
				worksheet.write(x,47, eca[i].hrs_d7r, data_format_dgr)
				worksheet.write(x,48, eca[i].costo_d7r, data_format_drgr)
				worksheet.write(x,49, eca[i].hrs_rodillo, data_format_dgr)
				worksheet.write(x,50, eca[i].costo_rodillo, data_format_drgr)
				worksheet.write(x,51, eca[i].hrs_motoconf, data_format_dgr)
				worksheet.write(x,52, eca[i].costo_motoconf, data_format_drgr)
				worksheet.write(x,53, eca[i].hrs_cargador, data_format_dgr)
				worksheet.write(x,54, eca[i].costo_cargador, data_format_drgr)
				worksheet.write(x,55, eca[i].total_diesel_acarreo, data_format_dgr)
				worksheet.write(x,56, eca[i].total_diesel_exac, data_format_dgr)
				worksheet.write(x,57, eca[i].consumo_h2o, data_format_drgr)
				
				worksheet.write(x,60, eci[i].boster, data_format_dgr)
				worksheet.write(x,61, eci[i].anfo, data_format_dgr)
				worksheet.write(x,62, eci[i].mecha, data_format_dgr)
				worksheet.write(x,63, eci[i].exanel, data_format_dgr)
				worksheet.write(x,64, eci[i].fulminante, data_format_dgr)
				worksheet.write(x,65, eci[i].np, data_format_dgr)
				worksheet.write(x,66, eci[i].unidireccional, data_format_drgr)
				worksheet.write(x,67, eci[i].vale_perfora if eci[i].vale_perfora else '', data_format_drgr)
				worksheet.write(x,68, eci[i].diesel, data_format_drgr)
				worksheet.write(x,69, eci[i].vale_cargador if eci[i].vale_cargador else '', data_format_drgr)
				worksheet.write(x,70, eci[i].cargador, data_format_drgr)
				worksheet.write(x,71, eci[i].nro_vale if eci[i].nro_vale else '', data_format_drgr)
				worksheet.write(x,72, eci[i].excavadora if eci[i].excavadora else '', data_format_drgr)

				worksheet.write(x,75, eii[i].boster, data_format_dgr)
				worksheet.write(x,76, eii[i].anfo, data_format_dgr)
				worksheet.write(x,77, eii[i].mecha, data_format_dgr)
				worksheet.write(x,78, eii[i].exanel, data_format_dgr)
				worksheet.write(x,79, eii[i].fulminante, data_format_dgr)
				worksheet.write(x,80, eii[i].np, data_format_dgr)
				worksheet.write(x,81, eii[i].unidireccional, data_format_drgr)
				worksheet.write(x,82, eii[i].diesel, data_format_drgr)
				worksheet.write(x,83, eii[i].diesel_carga, data_format_drgr)
				#worksheet.write(x,77, eii[i].agua, data_format_drgr)
			
			sum_ep[0] += ep[i].horas_operacion
			sum_ep[1] += ep[i].metros_lineales
			sum_ep[2] += ep[i].metros_hora
			sum_ep[3] += ep[i].consumo_diesel
			sum_ep[4] += ep[i].consumo_gls
			sum_ep[5] += ep[i].pit1_produc
			sum_ep[6] += ep[i].pit1_desmont
			sum_ep[7] += ep[i].pit2_tons
			sum_ep[8] += ep[i].pit3_tons
			sum_ep[9] += ep[i].pit4_tons
			sum_ep[10] += ep[i].boster
			sum_ep[11] += ep[i].anfo
			sum_ep[12] += ep[i].mecha
			sum_ep[13] += ep[i].exanel
			sum_ep[14] += ep[i].fulminante
			sum_ep[15] += ep[i].np
			sum_ep[16] += ep[i].unidireccional
			sum_ep[17] += ep[i].cons_explosivo
			sum_ep[18] += ep[i].grs_ton
			
			sum_eca[0] += eca[i].hrs_oper
			sum_eca[1] += eca[i].consumo_diesel
			sum_eca[2] += eca[i].hrs_excavd2
			sum_eca[3] += eca[i].costo_hr_d2
			sum_eca[4] += eca[i].hrs_martillo
			sum_eca[5] += eca[i].costo_hr_martillo
			sum_eca[6] += eca[i].hrs_excavdl
			sum_eca[7] += eca[i].costo_hr_dl
			sum_eca[8] += eca[i].hrs_volq01
			sum_eca[9] += eca[i].costo_volq01
			sum_eca[10] += eca[i].hrs_volq02
			sum_eca[11] += eca[i].costo_volq02
			sum_eca[12] += eca[i].hrs_volq03
			sum_eca[13] += eca[i].costo_volq03
			sum_eca[14] += eca[i].hrs_volq04
			sum_eca[15] += eca[i].costo_volq04
			sum_eca[16] += eca[i].hrs_volq05
			sum_eca[17] += eca[i].costo_volq05
			sum_eca[18] += eca[i].hrs_volq06
			sum_eca[19] += eca[i].costo_volq06
			sum_eca[20] += eca[i].hrs_volqv5
			sum_eca[21] += eca[i].costo_volqv5
			sum_eca[22] += eca[i].hrs_volq07
			sum_eca[23] += eca[i].costo_volq07
			sum_eca[24] += eca[i].hrs_d7r
			sum_eca[25] += eca[i].costo_d7r
			sum_eca[26] += eca[i].hrs_rodillo
			sum_eca[27] += eca[i].costo_rodillo
			sum_eca[28] += eca[i].hrs_motoconf
			sum_eca[29] += eca[i].costo_motoconf
			sum_eca[30] += eca[i].hrs_cargador
			sum_eca[31] += eca[i].costo_cargador
			sum_eca[32] += eca[i].total_diesel_acarreo
			sum_eca[33] += eca[i].total_diesel_exac
			sum_eca[34] += eca[i].consumo_h2o

			sum_eci[0] += eci[i].boster
			sum_eci[1] += eci[i].anfo
			sum_eci[2] += eci[i].mecha
			sum_eci[3] += eci[i].exanel
			sum_eci[4] += eci[i].fulminante
			sum_eci[5] += eci[i].np
			sum_eci[6] += eci[i].unidireccional
			sum_eci[7] += eci[i].diesel
			sum_eci[8] += eci[i].cargador
			#sum_eci[9] += eci[i].cargador
			sum_eci[10] += eci[i].excavadora if eci[i].excavadora else 0
			#sum_eci[6] += eci[i].agua

			sum_eii[0] += eii[i].boster
			sum_eii[1] += eii[i].anfo
			sum_eii[2] += eii[i].mecha
			sum_eii[3] += eii[i].exanel
			sum_eii[4] += eii[i].fulminante
			sum_eii[5] += eii[i].np
			sum_eii[6] += eii[i].unidireccional
			sum_eii[7] += eii[i].diesel
			sum_eii[7] += eii[i].diesel_carga
			#sum_eii[6] += eii[i].agua

			x += 1

		worksheet.write(x,1, u'Totales', data_format_total)
		worksheet.write(x,2, sum_ep[0] , data_format_total)
		worksheet.write(x,3, sum_ep[1] , data_format_total)
		worksheet.write(x,4, (sum_ep[2]/float(len(ep))) if len(ep) != 0 else 0, data_format_total)
		worksheet.write(x,5, (sum_ep[3]/sum_ep[1]) if sum_ep[1] != 0 else 0, data_format_total)
		worksheet.write(x,6, sum_ep[4] , data_format_total)
		worksheet.write(x,7, sum_ep[5] , data_format_total)
		worksheet.write(x,8, sum_ep[6] , data_format_total)
		worksheet.write(x,9, sum_ep[7] , data_format_total)
		worksheet.write(x,10, sum_ep[8] , data_format_total)
		worksheet.write(x,11, sum_ep[9] , data_format_total)
		worksheet.write(x,12, sum_ep[10] , data_format_total)
		worksheet.write(x,13, sum_ep[11] , data_format_total)
		worksheet.write(x,14, sum_ep[12] , data_format_total)
		worksheet.write(x,15, sum_ep[13] , data_format_total)
		worksheet.write(x,16, sum_ep[14] , data_format_total)
		worksheet.write(x,17, sum_ep[15] , data_format_total)
		worksheet.write(x,18, sum_ep[16] , data_format_total)
		worksheet.write(x,19, sum_ep[17] , data_format_total)
		worksheet.write(x,20, (sum_ep[17]/sum_ep[5]) if sum_ep[5] != 0 else 0, data_format_total)

		worksheet.write(x,22, u'Totales', data_format_total)
		worksheet.write(x,23, sum_eca[0], data_format_total)
		worksheet.write(x,24, sum_eca[1], data_format_total)
		worksheet.write(x,25, sum_eca[2], data_format_total)
		worksheet.write(x,26, sum_eca[3], data_format_total)
		worksheet.write(x,27, sum_eca[4], data_format_total)
		worksheet.write(x,28, sum_eca[5], data_format_total)
		worksheet.write(x,29, sum_eca[6], data_format_total)
		worksheet.write(x,30, sum_eca[7], data_format_total)
		worksheet.write(x,31, sum_eca[8], data_format_total)
		worksheet.write(x,32, sum_eca[9], data_format_total)
		worksheet.write(x,33, sum_eca[10], data_format_total)
		worksheet.write(x,34, sum_eca[11], data_format_total)
		worksheet.write(x,35, sum_eca[12], data_format_total)
		worksheet.write(x,36, sum_eca[13], data_format_total)
		worksheet.write(x,37, sum_eca[14], data_format_total)
		worksheet.write(x,38, sum_eca[15], data_format_total)
		worksheet.write(x,39, sum_eca[16], data_format_total)
		worksheet.write(x,40, sum_eca[17], data_format_total)
		worksheet.write(x,41, sum_eca[18], data_format_total)
		worksheet.write(x,42, sum_eca[19], data_format_total)
		worksheet.write(x,43, sum_eca[20], data_format_total)
		worksheet.write(x,44, sum_eca[21], data_format_total)
		worksheet.write(x,45, sum_eca[22], data_format_total)
		worksheet.write(x,46, sum_eca[23], data_format_total)
		worksheet.write(x,47, sum_eca[24], data_format_total)
		worksheet.write(x,48, sum_eca[25], data_format_total)
		worksheet.write(x,49, sum_eca[26], data_format_total)
		worksheet.write(x,50, sum_eca[27], data_format_total)
		worksheet.write(x,51, sum_eca[28], data_format_total)
		worksheet.write(x,52, sum_eca[29], data_format_total)
		worksheet.write(x,53, sum_eca[30], data_format_total)
		worksheet.write(x,54, sum_eca[31], data_format_total)
		worksheet.write(x,55, sum_eca[32], data_format_total)
		worksheet.write(x,56, sum_eca[33], data_format_total)
		worksheet.write(x,57, sum_eca[34], data_format_total)

		worksheet.write(x,59, u'Totales', data_format_total)
		worksheet.write(x,60, sum_eci[0], data_format_total)
		worksheet.write(x,61, sum_eci[1], data_format_total)
		worksheet.write(x,62, sum_eci[2], data_format_total)
		worksheet.write(x,63, sum_eci[3], data_format_total)
		worksheet.write(x,64, sum_eci[4], data_format_total)
		worksheet.write(x,65, sum_eci[5], data_format_total)
		worksheet.write(x,66, sum_eci[6], data_format_total)
		worksheet.write(x,67, ' ', data_format_total)
		worksheet.write(x,68, sum_eci[7], data_format_total)
		worksheet.write(x,69, ' ', data_format_total)
		worksheet.write(x,70, sum_eci[8], data_format_total)
		worksheet.write(x,71, ' ', data_format_total)
		worksheet.write(x,72, sum_eci[10], data_format_total)
		#worksheet.write(x,66, sum_eci[6], data_format_total)

		worksheet.write(x,74, u'Totales', data_format_total)
		worksheet.write(x,75, eii[-1].boster if len(eii) > 0 else 0, data_format_total)
		worksheet.write(x,76, eii[-1].anfo if len(eii) > 0 else 0, data_format_total)
		worksheet.write(x,77, eii[-1].mecha if len(eii) > 0 else 0, data_format_total)
		worksheet.write(x,78, eii[-1].exanel if len(eii) > 0 else 0, data_format_total)
		worksheet.write(x,79, eii[-1].fulminante if len(eii) > 0 else 0, data_format_total)
		worksheet.write(x,80, eii[-1].np if len(eii) > 0 else 0, data_format_total)
		worksheet.write(x,81, eii[-1].unidireccional if len(eii) > 0 else 0, data_format_total)
		worksheet.write(x,82, eii[-1].diesel if len(eii) > 0 else 0, data_format_total)
		worksheet.write(x,83, eii[-1].diesel_carga if len(eii) > 0 else 0, data_format_total)
		#worksheet.write(x,77, sum_eii[8], data_format_total)

		x = 48

		worksheet.merge_range(x,2,x,13, u'Indicadores de Operación', merge_format_t32)
		x+=1
		worksheet.merge_range(x,2,x,5, u'Concepto', merge_format_t32)
		worksheet.merge_range(x,6,x,11, u'Cantidad', merge_format_t32)
		worksheet.merge_range(x,12,x,13, u'Unidades', merge_format_t32)

		x += 1
		eio = self.env['extraccion.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
		for i in range(len(eio)):
			if i % 2 == 0:
				if i == len(eio)-1:
					worksheet.merge_range(x,2,x,5, eio[i].concepto, data_format_dlrd)
					worksheet.merge_range(x,6,x,11, eio[i].cantidad, data_format_dlrd)
					worksheet.merge_range(x,12,x,13, eio[i].unidades, data_format_dlrd)

				else:
					worksheet.merge_range(x,2,x,5, eio[i].concepto, data_format_dlr)
					if i == 0 or i == 4:
						worksheet.merge_range(x,6,x,11, eio[i].cantidad, data_format_dlrg)
					else:
						worksheet.merge_range(x,6,x,11, eio[i].cantidad, data_format_dlr)
					worksheet.merge_range(x,12,x,13, eio[i].unidades, data_format_dlr)
			else:
				if i == len(eio)-1:
					worksheet.merge_range(x,2,x,5, eio[i].concepto, data_format_dlrdgr)
					worksheet.merge_range(x,6,x,11, eio[i].cantidad, data_format_dlrdgr)
					worksheet.merge_range(x,12,x,13, eio[i].unidades, data_format_dlrdgr)
				else:
					worksheet.merge_range(x,2,x,5, eio[i].concepto, data_format_dlrgr)
					if i == 0 or i == 4:
						worksheet.merge_range(x,6,x,11, eio[i].cantidad, data_format_dlrg)
					else:
						worksheet.merge_range(x,6,x,11, eio[i].cantidad, data_format_dlrgr)
					worksheet.merge_range(x,12,x,13, eio[i].unidades, data_format_dlrgr)
			x += 1

		workbook.close()
		
		f = open( direccion + u'Extraccion_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx', 'rb')
			
		vals = {
			'output_name': u'Extraccion_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx',
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