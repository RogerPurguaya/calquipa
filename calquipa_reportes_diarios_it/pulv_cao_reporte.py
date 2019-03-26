# -*- encoding: utf-8 -*-
import base64
from openerp import models, fields, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp

import calendar
import datetime
import decimal

class pulv_cao_pulverizado_oxido(models.Model):
	_name = 'pulv.cao.pulverizado.oxido'

	_rec_name = 'date'
	_order = 'date'

	year_id = fields.Integer(u'Año')
	month_id = fields.Integer(u'Mes')

	date = fields.Date('Fecha')
	horas_operacion = fields.Float(u'Horas Operación')
	silo = fields.Float(u'Silo')
	tpd_real = fields.Float(u'TPD Prod. Real')
	ton_cao = fields.Float(u'Toneladas Ca O debajo >')
	tpd_nominal = fields.Float(u'TPD Prod. Nominal')
	consumo_energia = fields.Float(u'Consumo Energía Eléc.')
	promedio_kwh = fields.Float(u'Promedio kwh/Ton', compute="get_promedio_kwh")
	calidad_cao = fields.Float(u'Calidad de CaO Disp')
	ppc = fields.Float(u'PPC')
	finura_100 = fields.Float(u'Finura M. 100 %')
	finura_200 = fields.Float(u'Finura M. 200 %')

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
	def get_promedio_kwh(self):
		self.promedio_kwh = (self.consumo_energia / self.tpd_real) if self.tpd_real != 0 else 0

	@api.multi
	def display_q(self, mnth, yr):
		if mnth in (0,13):
			return {
				"type": "ir.actions.act_window",
				"res_model": "pulv.cao.pulverizado.oxido",
				"view_type": "form",
				"view_mode": "tree",
				"target": "current",
			}

		ran = calendar.monthrange(yr,mnth)[1]
		for i in range(ran):
			cd = str(yr) + "-" + format(mnth, '02') + "-" + str(i+1)
			ep = self.env['pulv.cao.pulverizado.oxido'].search([('month_id','=',mnth),('date','=',cd)])
			if len(ep) == 0:
				vals = {
					'year_id': yr,
					'month_id': mnth,
					'date': cd,
				}
				nep = self.env['pulv.cao.pulverizado.oxido'].create(vals)
		
		return {
			"type": "ir.actions.act_window",
			"res_model": "pulv.cao.pulverizado.oxido",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class pulv_cao_funciones(models.Model):
	_name = 'pulv.cao.funciones'

	def get_silo(self, mnth, yr):
		self.env.cr.execute("""
			select sum(silo) from pulv_cao_pulverizado_oxido
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_horas_operacion(self, mnth, yr):
		self.env.cr.execute("""
			select sum(horas_operacion) from pulv_cao_pulverizado_oxido
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_calidad_cao(self, mnth, yr):
		self.env.cr.execute("""
			select sum(calidad_cao) from pulv_cao_pulverizado_oxido
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_ppc(self, mnth, yr):
		self.env.cr.execute("""
			select sum(ppc) from pulv_cao_pulverizado_oxido
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_finura_100(self, mnth, yr):
		self.env.cr.execute("""
			select sum(finura_100) from pulv_cao_pulverizado_oxido
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

	def get_finura_200(self, mnth, yr):
		self.env.cr.execute("""
			select sum(finura_200) from pulv_cao_pulverizado_oxido
			where 
				year_id = """+str(yr)+""" and 
				month_id = """+str(mnth)+"""
		""")
		return self.env.cr.fetchall()[0][0]

class pulv_cao_indicadores_operacion(models.Model):
	_name = 'pulv.cao.indicadores.operacion'

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
				"res_model": "pulv.cao.indicadores.operacion",
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
				(u'Promedio TPH',u'TPH'),
				(u'Promedio Día',u'TPD'),
				(u'Días de Producción',u'Días'),
				(u'Promedio de Calidad CaO Total',u'%'),
				(u'Promedio de Calidad CaO Disponible',u'%'),
				(u'Promedio PPC',u'[-]'),				
				(u'Promedio Finura M. 100',u'%'),
				(u'Promedio Finura M. 200',u'%'),
				(u'Promedio Consumo Energía',u'kwh/Ton'),]
		dias_mes = calendar.monthrange(yr, mnth)[1]

		mio = self.env['pulv.cao.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth)])
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
					res = self.env['pulv.cao.funciones'].get_silo(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = om-res

				if vals['concepto'] == conc[2][0]:
					res = self.env['pulv.cao.funciones'].get_silo(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = res

				if vals['concepto'] == conc[3][0]:
					res = self.env['pulv.cao.funciones'].get_silo(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = om-res

				if vals['concepto'] == conc[4][0]:
					vals['cantidad'] = oh

				if vals['concepto'] == conc[5][0]:
					res = self.env['pulv.cao.funciones'].get_horas_operacion(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = res

				if vals['concepto'] == conc[6][0]:
					r1 = self.env['pulv.cao.funciones'].get_silo(mnth, yr)
					r2 = self.env['pulv.cao.funciones'].get_horas_operacion(mnth, yr)
					if r1 == None:
						r1 = 0
					if r2 == None:
						r2 = 0
					vals['cantidad'] = (r1 / r2) if r2 != 0 else 0

				if vals['concepto'] == conc[7][0]:
					res = self.env['pulv.cao.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',u'Promedio TPH')])[0]
					if res.cantidad == None:
						res.cantidad = 0
					vals['cantidad'] = res.cantidad * 24

				if vals['concepto'] == conc[8][0]:
					vals['cantidad'] = dias_mes

				if vals['concepto'] == conc[9][0]:
					vals['cantidad'] = 0

				if vals['concepto'] == conc[10][0]:
					res = self.env['pulv.cao.funciones'].get_calidad_cao(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = res/dias_mes

				if vals['concepto'] == conc[11][0]:
					res = self.env['pulv.cao.funciones'].get_ppc(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = res/dias_mes

				if vals['concepto'] == conc[12][0]:
					res = self.env['pulv.cao.funciones'].get_finura_100(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = res/dias_mes

				if vals['concepto'] == conc[13][0]:
					res = self.env['pulv.cao.funciones'].get_finura_200(mnth, yr)
					if res == None:
						res = 0
					vals['cantidad'] = res/dias_mes

				if vals['concepto'] == conc[14][0]:
					res = self.env['pulv.cao.pulverizado.oxido'].search([('year_id','=',yr),('month_id','=',mnth)])
					tmp = 0
					for i in res:
						tmp += (i.consumo_energia / i.tpd_real) if i.tpd_real != 0 else 0
					vals['cantidad'] = tmp / dias_mes

				nmio = self.env['pulv.cao.indicadores.operacion'].create(vals)
		else:		
			for i in mio:
				i.dias_transcurridos = dt
				if i.concepto == conc[0][0]:
					i.cantidad = om
				if i.concepto == conc[4][0]:
					i.cantidad = oh

		return {
			"type": "ir.actions.act_window",
			"res_model": "pulv.cao.indicadores.operacion",
			"view_type": "form",
			"view_mode": "tree",
			"context": {"search_default_year_id":yr, "search_default_month_id":mnth, },
			"target": "current",
		}

class pulv_cao_reporte(models.Model):
	_name = 'pulv.cao.reporte'

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
		workbook = Workbook( direccion + u'Pulv_CaO_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx')
		worksheet = workbook.add_worksheet("Pulv_CaO")

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
		worksheet.set_column("X:X", 3.86)

		worksheet.merge_range("B2:D8", '', merge_format_t)
		worksheet.merge_range("E2:H8", u'Calquipa', merge_format_t)
		worksheet.merge_range("I2:K2", u'Fecha:', merge_format_ca)
		worksheet.merge_range("L2:M2", datetime.datetime.today().strftime("%Y-%m-%d"), merge_format_ca2)
		worksheet.merge_range("I3:K3", u'Mes:', merge_format_ca)
		worksheet.merge_range("L3:M3", month2name[mnth], merge_format_ca2)
		worksheet.merge_range("I4:K4", u'Días de Mes:', merge_format_ca)
		worksheet.merge_range("L4:M4", calendar.monthrange(yr,mnth)[1], merge_format_ca2)
		worksheet.merge_range("I5:K5", u'Días Transcurridos Mes:', merge_format_ca)

		acio = self.env['pulv.cao.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
		if len(acio) > 0:
			acio = acio[0]
			worksheet.merge_range("L5:M5", acio.dias_transcurridos, merge_format_ca2)
		else:
			worksheet.merge_range("L5:M5", '', merge_format_ca2)

		worksheet.merge_range("I6:K6", u'Hrs Mes:', merge_format_ca)
		worksheet.merge_range("L6:M6", u'', merge_format_ca2)
		worksheet.merge_range("I7:K7", u'Clave SGI', merge_format_ca)
		worksheet.merge_range("L7:M7", u'', merge_format_ca2)
		worksheet.merge_range("I8:K8", u'Folio', merge_format_ca)
		worksheet.merge_range("L8:M8", u'', merge_format_ca2)

		worksheet.insert_image('B3', 'calquipalright.png', {'x_scale': 0.85, 'y_scale': 0.85, 'x_offset':4})
		worksheet.insert_image('E3', 'calquipalleft.png', {'x_scale': 0.85, 'y_scale': 0.85, 'x_offset':4})

		worksheet.set_row(9, 21)
		worksheet.merge_range("B10:M10", u'Pulv CaO', merge_format_t)

		worksheet.set_row(11, 20)
		worksheet.merge_range("B12:M12", u'Pulverizado de Oxido', merge_format_t2)

		worksheet.set_row(12, 20.25)
		worksheet.set_row(13, 33)
		worksheet.set_row(14, 12)
		worksheet.merge_range("B13:B15", u'Fecha', merge_format_t31)
		worksheet.merge_range("C13:C15", u'Hrs Op', merge_format_t32)
		worksheet.merge_range("D13:D15", u'Silo', merge_format_t32)
		worksheet.merge_range("E13:E15", u'TPD Prod. Real', merge_format_t32)
		worksheet.merge_range("F13:F15", u'Toneladas Ca O debajo >', merge_format_t32)
		worksheet.merge_range("G13:G15", u'TPD Prod. Nominal', merge_format_t32)
		worksheet.merge_range("H13:H15", u'Consumo Energía Eléc.', merge_format_t32)
		worksheet.merge_range("I13:I15", u'Promedio kwh/Ton', merge_format_t32)
		worksheet.merge_range("J13:J15", u'Calidad de CaO Disp', merge_format_t32)
		worksheet.merge_range("K13:K15", u'PPC', merge_format_t32)
		worksheet.merge_range("L13:L15", u'Finura M. 100 %', merge_format_t32)
		worksheet.merge_range("M13:M15", u'Finura M. 200 %', merge_format_t32)

		pcpo = self.env['pulv.cao.pulverizado.oxido'].search([('year_id','=',yr),('month_id','=',mnth)])
		pcio = self.env['pulv.cao.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])

		print len(pcpo),len(pcio)
		if len(pcpo) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de PULVERIZADO OXIDO para el periodo seleccionado.")
		if len(pcio) == 0:
			raise osv.except_osv('Alerta!', u"No se crearon datos de INDICADORES DE OPERACION para el periodo seleccionado.")
		

		sum_pcpo = [0,0,0,0,0,0,0,0,0,0,0]

		x = 15
		for i in range(len(pcpo)):
			fch = format(i+1,'02')+'-'+month2name[mnth][:3]
			worksheet.write(x,1, fch, data_format_dlr)
			if i % 2 == 0:
				worksheet.write(x,2, pcpo[i].horas_operacion, data_format_d)
				worksheet.write(x,3, pcpo[i].silo, data_format_d)
				worksheet.write(x,4, pcpo[i].tpd_real, data_format_d)
				worksheet.write(x,5, pcpo[i].ton_cao, data_format_d)
				worksheet.write(x,6, pcpo[i].tpd_nominal, data_format_dr)
				worksheet.write(x,7, pcpo[i].consumo_energia, data_format_d)
				worksheet.write(x,8, pcpo[i].promedio_kwh, data_format_d)
				worksheet.write(x,9, pcpo[i].calidad_cao, data_format_d)
				worksheet.write(x,10, pcpo[i].ppc, data_format_d)
				worksheet.write(x,11, pcpo[i].finura_100, data_format_d)
				worksheet.write(x,12, pcpo[i].finura_200, data_format_dr)			

			else:
				worksheet.write(x,2, pcpo[i].horas_operacion, data_format_dgr)
				worksheet.write(x,3, pcpo[i].silo, data_format_dgr)
				worksheet.write(x,4, pcpo[i].tpd_real, data_format_dgr)
				worksheet.write(x,5, pcpo[i].ton_cao, data_format_dgr)
				worksheet.write(x,6, pcpo[i].tpd_nominal, data_format_drgr)
				worksheet.write(x,7, pcpo[i].consumo_energia, data_format_dgr)
				worksheet.write(x,8, pcpo[i].promedio_kwh, data_format_dgr)
				worksheet.write(x,9, pcpo[i].calidad_cao, data_format_dgr)
				worksheet.write(x,10, pcpo[i].ppc, data_format_dgr)
				worksheet.write(x,11, pcpo[i].finura_100, data_format_dgr)
				worksheet.write(x,12, pcpo[i].finura_200, data_format_drgr)
				
			
			sum_pcpo[0] += pcpo[i].horas_operacion
			sum_pcpo[1] += pcpo[i].silo
			sum_pcpo[2] += pcpo[i].tpd_real
			sum_pcpo[3] += pcpo[i].ton_cao
			sum_pcpo[4] += pcpo[i].tpd_nominal
			sum_pcpo[5] += pcpo[i].consumo_energia
			sum_pcpo[6] += pcpo[i].promedio_kwh
			sum_pcpo[7] += pcpo[i].calidad_cao
			sum_pcpo[8] += pcpo[i].ppc
			sum_pcpo[9] += pcpo[i].finura_100
			sum_pcpo[10] += pcpo[i].finura_200

			x += 1

		worksheet.write(x,1, u'Totales', data_format_total)
		worksheet.write(x,2, sum_pcpo[0], data_format_total)
		worksheet.write(x,3, sum_pcpo[1], data_format_total)
		worksheet.write(x,4, sum_pcpo[2], data_format_total)
		worksheet.write(x,5, sum_pcpo[3], data_format_total)
		worksheet.write(x,6, sum_pcpo[4], data_format_total)
		worksheet.write(x,7, sum_pcpo[5], data_format_total)
		sum_6 = self.env['pulv.cao.pulverizado.oxido'].search([('year_id','=',yr),('month_id','=',mnth)])
		tmp = 0
		for i in sum_6:
			tmp += (i.consumo_energia / i.tpd_real) if i.tpd_real != 0 else 0
		worksheet.write(x,8, (tmp/float(len(pcpo))) , data_format_total)
		worksheet.write(x,9, (sum_pcpo[7]/float(len(pcpo))) , data_format_total)
		worksheet.write(x,10, (sum_pcpo[8]/float(len(pcpo))) , data_format_total)
		worksheet.write(x,11, (sum_pcpo[9]/float(len(pcpo))) , data_format_total)
		worksheet.write(x,12, (sum_pcpo[10]/float(len(pcpo))) , data_format_total)

		x = 48

		worksheet.merge_range(x,2,x,13, u'Indicadores de Operación', merge_format_t32)
		x+=1
		worksheet.merge_range(x,2,x,5, u'Concepto', merge_format_t32)
		worksheet.merge_range(x,6,x,11, u'Cantidad', merge_format_t32)
		worksheet.merge_range(x,12,x,13, u'Unidades', merge_format_t32)

		x += 1
		pcio = self.env['pulv.cao.indicadores.operacion'].search([('month_id','=',mnth),('year_id','=',yr)])
		for i in range(len(pcio)):
			if i % 2 == 0:
				if i == len(pcio)-1:
					worksheet.merge_range(x,2,x,5, pcio[i].concepto, data_format_dlrd)
					worksheet.merge_range(x,6,x,11, pcio[i].cantidad, data_format_dlrd)
					worksheet.merge_range(x,12,x,13, pcio[i].unidades, data_format_dlrd)

				else:
					worksheet.merge_range(x,2,x,5, pcio[i].concepto, data_format_dlr)
					if i == 0:
						worksheet.merge_range(x,6,x,11, pcio[i].cantidad, data_format_dlrg)
					else:
						worksheet.merge_range(x,6,x,11, pcio[i].cantidad, data_format_dlr)
					worksheet.merge_range(x,12,x,13, pcio[i].unidades, data_format_dlr)
			else:
				if i == len(pcio)-1:
					worksheet.merge_range(x,2,x,5, pcio[i].concepto, data_format_dlrdgr)
					worksheet.merge_range(x,6,x,11, pcio[i].cantidad, data_format_dlrdgr)
					worksheet.merge_range(x,12,x,13, pcio[i].unidades, data_format_dlrdgr)
				else:
					worksheet.merge_range(x,2,x,5, pcio[i].concepto, data_format_dlrgr)
					if i == 0 or i == 4:
						worksheet.merge_range(x,6,x,11, pcio[i].cantidad, data_format_dlrg)
					else:
						worksheet.merge_range(x,6,x,11, pcio[i].cantidad, data_format_dlrgr)
					worksheet.merge_range(x,12,x,13, pcio[i].unidades, data_format_dlrgr)
			x += 1

		workbook.close()
		
		f = open( direccion + u'Pulv_CaO_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx', 'rb')
			
		vals = {
			'output_name': u'Pulv_CaO_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx',
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