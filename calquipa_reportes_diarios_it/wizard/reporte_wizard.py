# -*- encoding: utf-8 -*-
import base64
from openerp import models, fields, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp

import calendar
import datetime

class reporte_wizard(models.TransientModel):
	_name = 'reporte.wizard'

	fiscalyear_id = fields.Many2one('account.fiscalyear',u'Año Fiscal', required=True)
	period_id = fields.Many2one('account.period','Periodo', required=True)

	@api.multi
	def do_rebuild(self):
		con = self.env.context
		month = self.period_id.code.split('/')
		if len(month) > 0:
			month = month[0]
			if con['tipo_rep'] == 'expe':
				return self.env['extraccion.perforacion'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'excaac':
				return self.env['extraccion.carga.acarreo'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'excoin':
				return self.env['extraccion.compra.insumos'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'exinin':
				return self.env['extraccion.inventario.insumos'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'exreex':
				return self.env['extraccion.reporte'].generar_excel(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'trneaf':
				return self.env['trituracion.negro.africano'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'trhoma':
				return self.env['trituracion.horno.maez'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'trcodi':
				return self.env['trituracion.compra.diesel'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'trindi':
				return self.env['trituracion.inventario.diesel'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'trretr':
				return self.env['trituracion.reporte'].generar_excel(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'ancopucoso':
				return self.env['anivi.coke.pulverizado.combustible.solido'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'ancocoin':
				return self.env['anivi.coke.compra.insumos'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'ancoinin':
				return self.env['anivi.coke.inventario.insumos'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'ancoreanco':
				return self.env['anivi.coke.reporte'].generar_excel(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'coanpucoso':
				return self.env['control.antracita.pulverizado.combustible.solido'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'coancoin':
				return self.env['control.antracita.compra.insumos'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'coaninin':
				return self.env['control.antracita.inventario.insumos'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'coanreanco':
				return self.env['control.antracita.reporte'].generar_excel(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'maca':
				return self.env['maerz.calcinacion'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'macomdi':
				return self.env['compra.diesel'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'macondi':
				return self.env['consumo.diesel'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'masaldi':
				return self.env['saldos.diesel'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'marema':
				return self.env['maerz.reporte'].generar_excel(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'pucapuox':
				return self.env['pulv.cao.pulverizado.oxido'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'pucarepuca':
				return self.env['pulv.cao.reporte'].generar_excel(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'sacaox':
				return self.env['salida.cao.oxido'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'sacaenpi':
				return self.env['salida.cao.entrada.piedra'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'sacaenpeco':
				return self.env['salida.cao.entrada.pet.coke'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'sacasagra':
				return self.env['salida.cao.salida.grava'].display_q(int(month), int(self.fiscalyear_id.code))
			elif con['tipo_rep'] == 'sacaresaca':
				return self.env['salida.cao.reporte'].generar_excel(int(month), int(self.fiscalyear_id.code))
			else:
				return 1
		return 1

class reporte_operacion_wizard(models.TransientModel):
	_name = 'reporte.operacion.wizard'

	def get_dias(self):
		return datetime.datetime.today().day

	fiscalyear_id = fields.Many2one('account.fiscalyear',u'Año Fiscal', required=True)
	period_id = fields.Many2one('account.period','Periodo', required=True)

	dias = fields.Integer(u'Dias Transcurridos', required=True, default=get_dias)

	obj_mes = fields.Integer('Objetivo Mes', required=True)
	obj_hrs = fields.Integer(u'Objetivo de Hrs. de Operación Mes', required=True)
	hrs_perf = fields.Integer(u'Hrs Empleadas Perforación', required=True)

	@api.onchange('period_id')
	def onchange_period_id(self):
		if self.period_id.id != False:
			if self.env.context['tipo_rep'] == 'exinop':
				month = self.period_id.code.split('/')
				if len(month) > 0:
					month = month[0] 
					eioc1 = self.env['extraccion.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo Mes')])
					eioc2 = self.env['extraccion.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo de Hrs de Operación Mes')])
					eioc3 = self.env['extraccion.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Hrs Empleadas Perforación')])
					if len(eioc1) > 0:
						eioc1 = eioc1[0]
						self.obj_mes = eioc1.cantidad
					else:
						self.obj_mes = 0
					if len(eioc2) > 0:
						eioc2 = eioc2[0]
						self.obj_hrs = eioc2.cantidad
					else:
						self.obj_hrs = 0
					if len(eioc3) > 0:
						eioc3 = eioc3[0]
						self.hrs_perf = eioc3.cantidad
					else:
						self.hrs_perf = 0

	@api.multi
	def do_rebuild(self):
		con = self.env.context
		month = self.period_id.code.split('/')
		if len(month) > 0:
			month = month[0]
			if self.dias > calendar.monthrange(int(self.fiscalyear_id.code), int(month))[1] or self.dias < 1:
				raise osv.except_osv('Alerta!', "Dias Transcurridos Incorrecto.")
			if con['tipo_rep'] == 'exinop':
				return self.env['extraccion.indicadores.operacion'].display_q(int(month), int(self.fiscalyear_id.code), self.dias, self.obj_mes, self.obj_hrs, self.hrs_perf)
			else: 
				return 1
		return 1

class reporte_operacion_trituracion_wizard(models.TransientModel):
	_name = 'reporte.operacion.trituracion.wizard'

	def get_dias(self):
		return datetime.datetime.today().day

	fiscalyear_id = fields.Many2one('account.fiscalyear',u'Año Fiscal', required=True)
	period_id = fields.Many2one('account.period','Periodo', required=True)

	dias = fields.Integer(u'Dias Transcurridos', required=True, default=get_dias)

	obj_mes = fields.Integer('Objetivo Mes', required=True)
	obj_hrs = fields.Integer(u'Objetivo de Hrs. de Operación Mes', required=True)
	hrs_perf = fields.Integer(u'Hrs Empleadas Trituración', required=True)
	hornos = fields.Float(u'%  de Aprov. Hornos', required=True)
	promedio_calidad = fields.Float(u'Promedio Calidad Ca CO3', required=True)
	promedio_silice = fields.Float(u'Promedio %  Silice', required=True)

	@api.onchange('period_id')
	def onchange_period_id(self):
		if self.period_id.id != False:
			if self.env.context['tipo_rep'] == 'trinop':
				month = self.period_id.code.split('/')
				if len(month) > 0:
					month = month[0] 
					eioc1 = self.env['trituracion.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo Mes')])
					eioc2 = self.env['trituracion.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo de Hrs de Operación Mes')])
					eioc3 = self.env['trituracion.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Hrs Empleadas Trituración')])
					eioc4 = self.env['trituracion.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'%  de Aprov. Hornos')])
					eioc5 = self.env['trituracion.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Promedio Calidad Ca CO3')])
					eioc6 = self.env['trituracion.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Promedio %  Silice')])
					if len(eioc1) > 0:
						eioc1 = eioc1[0]
						self.obj_mes = eioc1.cantidad
					else:
						self.obj_mes = 0
					if len(eioc2) > 0:
						eioc2 = eioc2[0]
						self.obj_hrs = eioc2.cantidad
					else:
						self.obj_hrs = 0
					if len(eioc3) > 0:
						eioc3 = eioc3[0]
						self.hrs_perf = eioc3.cantidad
					else:
						self.hrs_perf = 0
					if len(eioc4) > 0:
						eioc4 = eioc4[0]
						self.hornos = eioc4.cantidad
					else:
						self.hornos = 0
					if len(eioc5) > 0:
						eioc5 = eioc5[0]
						self.promedio_calidad = eioc5.cantidad
					else:
						self.promedio_calidad = 0
					if len(eioc6) > 0:
						eioc6 = eioc6[0]
						self.promedio_silice = eioc6.cantidad
					else:
						self.promedio_silice = 0

	@api.multi
	def do_rebuild(self):
		con = self.env.context
		month = self.period_id.code.split('/')
		if len(month) > 0:
			month = month[0]
			if self.dias > calendar.monthrange(int(self.fiscalyear_id.code), int(month))[1] or self.dias < 1:
				raise osv.except_osv('Alerta!', "Dias Transcurridos Incorrecto.")
			if con['tipo_rep'] == 'trinop':
				return self.env['trituracion.indicadores.operacion'].display_q(int(month), int(self.fiscalyear_id.code), self.dias, self.obj_mes, self.obj_hrs, self.hrs_perf, self.hornos, self.promedio_calidad, self.promedio_silice)
			else: 
				return 1
		return 1

class reporte_operacion_anivi_coke_wizard(models.TransientModel):
	_name = 'reporte.operacion.anivi.coke.wizard'

	def get_dias(self):
		return datetime.datetime.today().day

	fiscalyear_id = fields.Many2one('account.fiscalyear',u'Año Fiscal', required=True)
	period_id = fields.Many2one('account.period','Periodo', required=True)

	dias = fields.Integer(u'Dias Transcurridos', required=True, default=get_dias)

	obj_mes = fields.Integer('Objetivo Mes', required=True)
	obj_hrs = fields.Integer(u'Objetivo de Hrs. de Operación Mes', required=True)
	
	@api.onchange('period_id')
	def onchange_period_id(self):
		if self.period_id.id != False:
			if self.env.context['tipo_rep'] == 'ancoinop':
				month = self.period_id.code.split('/')
				if len(month) > 0:
					month = month[0] 
					acioc1 = self.env['anivi.coke.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo Mes')])
					acioc2 = self.env['anivi.coke.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo de Hrs de Operación Mes')])
					if len(acioc1) > 0:
						acioc1 = acioc1[0]
						self.obj_mes = acioc1.cantidad
					else:
						self.obj_mes = 0
					if len(acioc2) > 0:
						acioc2 = acioc2[0]
						self.obj_hrs = acioc2.cantidad
					else:
						self.obj_hrs = 0
			if self.env.context['tipo_rep'] == 'coaninop':
				month = self.period_id.code.split('/')
				if len(month) > 0:
					month = month[0] 
					acioc1 = self.env['control.antracita.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo Mes')])
					acioc2 = self.env['control.antracita.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo de Hrs de Operación Mes')])
					if len(acioc1) > 0:
						acioc1 = acioc1[0]
						self.obj_mes = acioc1.cantidad
					else:
						self.obj_mes = 0
					if len(acioc2) > 0:
						acioc2 = acioc2[0]
						self.obj_hrs = acioc2.cantidad
					else:
						self.obj_hrs = 0
			if self.env.context['tipo_rep'] == 'mainop':
				month = self.period_id.code.split('/')
				if len(month) > 0:
					month = month[0] 
					mioc1 = self.env['maerz.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo Mes')])
					mioc2 = self.env['maerz.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo de Hrs de Operación Mes')])
					if len(mioc1) > 0:
						mioc1 = mioc1[0]
						self.obj_mes = mioc1.cantidad
					else:
						self.obj_mes = 0
					if len(mioc2) > 0:
						mioc2 = mioc2[0]
						self.obj_hrs = mioc2.cantidad
					else:
						self.obj_hrs = 0
			if self.env.context['tipo_rep'] == 'pucainop':
				month = self.period_id.code.split('/')
				if len(month) > 0:
					month = month[0] 
					pcioc1 = self.env['pulv.cao.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo Mes')])
					pcioc2 = self.env['pulv.cao.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo de Hrs de Operación Mes')])
					if len(pcioc1) > 0:
						pcioc1 = pcioc1[0]
						self.obj_mes = pcioc1.cantidad
					else:
						self.obj_mes = 0
					if len(pcioc2) > 0:
						pcioc2 = pcioc2[0]
						self.obj_hrs = pcioc2.cantidad
					else:
						self.obj_hrs = 0
			if self.env.context['tipo_rep'] == 'sacainop':
				month = self.period_id.code.split('/')
				if len(month) > 0:
					month = month[0] 
					scioc1 = self.env['salida.cao.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo Mes')])
					scioc2 = self.env['salida.cao.indicadores.operacion'].search([('year_id','=',int(self.fiscalyear_id.code)),('month_id','=',int(month)),('concepto','=',u'Objetivo de Hrs de Operación Mes')])
					if len(scioc1) > 0:
						scioc1 = scioc1[0]
						self.obj_mes = scioc1.cantidad
					else:
						self.obj_mes = 0
					if len(scioc2) > 0:
						scioc2 = scioc2[0]
						self.obj_hrs = scioc2.cantidad
					else:
						self.obj_hrs = 0

	@api.multi
	def do_rebuild(self):
		con = self.env.context
		month = self.period_id.code.split('/')
		if len(month) > 0:
			month = month[0]
			if self.dias > calendar.monthrange(int(self.fiscalyear_id.code), int(month))[1] or self.dias < 1:
				raise osv.except_osv('Alerta!', "Dias Transcurridos Incorrecto.")
			if con['tipo_rep'] == 'ancoinop':
				return self.env['anivi.coke.indicadores.operacion'].display_q(int(month), int(self.fiscalyear_id.code), self.dias, self.obj_mes, self.obj_hrs)
			if con['tipo_rep'] == 'coaninop':
				return self.env['control.antracita.indicadores.operacion'].display_q(int(month), int(self.fiscalyear_id.code), self.dias, self.obj_mes, self.obj_hrs)
			elif con['tipo_rep'] == 'mainop':
				return self.env['maerz.indicadores.operacion'].display_q(int(month), int(self.fiscalyear_id.code), self.dias, self.obj_mes, self.obj_hrs)
			elif con['tipo_rep'] == 'pucainop':
				return self.env['pulv.cao.indicadores.operacion'].display_q(int(month), int(self.fiscalyear_id.code), self.dias, self.obj_mes, self.obj_hrs)
			elif con['tipo_rep'] == 'sacainop':
				return self.env['salida.cao.indicadores.operacion'].display_q(int(month), int(self.fiscalyear_id.code), self.dias, self.obj_mes, self.obj_hrs)
			else: 
				return 1
		return 1

class reporte_final_wizard(models.TransientModel):
	_name = 'reporte.final.wizard'

	def get_dias(self):
		return datetime.datetime.today().day

	fiscalyear_id = fields.Many2one('account.fiscalyear',u'Año Fiscal', required=True)
	period_id = fields.Many2one('account.period','Periodo', required=True)

	dias = fields.Integer(u'Dias Transcurridos', required=True, default=get_dias)

	@api.multi
	def do_rebuild(self):
		con = self.env.context
		month = self.period_id.code.split('/')
		if len(month) > 0:
			month = month[0]
			if self.dias > calendar.monthrange(int(self.fiscalyear_id.code), int(month))[1] or self.dias < 1:
				raise osv.except_osv('Alerta!', "Dias Transcurridos Incorrecto.")
			if con['tipo_rep'] == 'refi':
				return self.env['reporte.final'].generar_excel(int(month), int(self.fiscalyear_id.code), self.dias)
			else: 
				return 1
		return 1