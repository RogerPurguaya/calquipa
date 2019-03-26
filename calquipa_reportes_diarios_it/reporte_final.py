# -*- encoding: utf-8 -*-
import base64
from openerp import models, fields, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp

import calendar
import datetime
import decimal

class reporte_final(models.Model):
	_name = 'reporte.final'

	@api.multi
	def generar_excel(self, mnth, yr, ds):
		import io
		from xlsxwriter.workbook import Workbook

		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		output = io.BytesIO()
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		if not direccion:
			raise osv.except_osv('Alerta!', u"No fue configurado el directorio para los archivos en Configuracion.")
		workbook = Workbook( direccion + u'Reporte_Diario_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx')
		worksheet = workbook.add_worksheet("Reporte_Diario")

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
			11: u"Noviember",
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
		merge_format_t31.set_bg_color("#0056D6")

		merge_format_t31_tr = workbook.add_format()
		merge_format_t31_tr.set_border(style=1)
		merge_format_t31_tr.set_bold()
		merge_format_t31_tr.set_align('center')
		merge_format_t31_tr.set_align('vcenter')
		merge_format_t31_tr.set_font_size(10)
		merge_format_t31_tr.set_font_color("#FFFFFF")
		merge_format_t31_tr.set_bg_color("#CE9418")

		merge_format_t31_ac = workbook.add_format()
		merge_format_t31_ac.set_border(style=1)
		merge_format_t31_ac.set_bold()
		merge_format_t31_ac.set_align('center')
		merge_format_t31_ac.set_align('vcenter')
		merge_format_t31_ac.set_font_size(10)
		merge_format_t31_ac.set_font_color("#FFFFFF")
		merge_format_t31_ac.set_bg_color("#000000")

		merge_format_t31_mae = workbook.add_format()
		merge_format_t31_mae.set_border(style=1)
		merge_format_t31_mae.set_bold()
		merge_format_t31_mae.set_align('center')
		merge_format_t31_mae.set_align('vcenter')
		merge_format_t31_mae.set_font_size(10)
		merge_format_t31_mae.set_font_color("#FFFFFF")
		merge_format_t31_mae.set_bg_color("#156110")

		merge_format_t31_pul = workbook.add_format()
		merge_format_t31_pul.set_border(style=1)
		merge_format_t31_pul.set_bold()
		merge_format_t31_pul.set_align('center')
		merge_format_t31_pul.set_align('vcenter')
		merge_format_t31_pul.set_font_size(10)
		merge_format_t31_pul.set_font_color("#FFFFFF")
		merge_format_t31_pul.set_bg_color("#206384")

		merge_format_t31_sal = workbook.add_format()
		merge_format_t31_sal.set_border(style=1)
		merge_format_t31_sal.set_bold()
		merge_format_t31_sal.set_align('center')
		merge_format_t31_sal.set_align('vcenter')
		merge_format_t31_sal.set_font_size(10)
		merge_format_t31_sal.set_font_color("#FFFFFF")
		merge_format_t31_sal.set_bg_color("#FF004D")

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

		merge_format_ca3 = workbook.add_format()
		merge_format_ca3.set_border(style=1)

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


		worksheet.set_column("C:C", 7.71)
		worksheet.set_column("D:D", 22)
		worksheet.set_column("E:E", 24.43)
		worksheet.set_column("F:F", 15.86)
		worksheet.set_column("G:G", 10.71)
		worksheet.set_column("H:H", 9.29)
		worksheet.set_column("I:I", 13.43)
		worksheet.set_column("J:J", 11.57)
		worksheet.set_column("K:K", 10.71)
		worksheet.set_column("L:L", 10.71)

		worksheet.merge_range("C3:D9", '', merge_format_t)
		worksheet.merge_range("E3:H9", 'Calquipa', merge_format_t)
		worksheet.merge_range("I3:J3", u'Fecha:', merge_format_ca)
		worksheet.merge_range("K3:L3", datetime.datetime.today().strftime("%Y-%m-%d"), merge_format_ca2)
		worksheet.merge_range("I4:J4", u'Mes:', merge_format_ca)
		worksheet.merge_range("K4:L4", month2name[mnth], merge_format_ca2)
		worksheet.merge_range("I5:J5", u'Días de Mes:', merge_format_ca)
		worksheet.merge_range("K5:L5", calendar.monthrange(yr,mnth)[1], merge_format_ca2)
		worksheet.merge_range("I6:J6", u'Días Transcurridos Mes:', merge_format_ca)
		worksheet.merge_range("K6:L6", ds, merge_format_ca2)
		worksheet.merge_range("I7:J7", u'Hrs Mes:', merge_format_ca)
		worksheet.merge_range("K7:L7", u'', merge_format_ca2)
		worksheet.merge_range("I8:J8", u'Clave SGI', merge_format_ca)
		worksheet.merge_range("K8:L8", u'', merge_format_ca2)
		worksheet.merge_range("I9:J9", u'Folio', merge_format_ca)
		worksheet.merge_range("K9:L9", u'', merge_format_ca2)

		worksheet.insert_image('C4', 'calquipalright.png', {'x_scale': 1, 'y_scale': 1, 'x_offset': 15, 'y_offset': 10})
		worksheet.insert_image('E4', 'calquipalleft.png', {'x_scale': 0.75, 'y_scale': 0.75, 'x_offset': 15, 'y_offset': 10})

		worksheet.merge_range("C11:L11", u'Comportamiento Extracción', merge_format_t31)
		worksheet.merge_range("C13:E13", u'Concepto', merge_format_t31)
		worksheet.merge_range("F13:H13", u'Cantidad', merge_format_t31)
		worksheet.write("I13", u'Unidad', merge_format_t31)
		worksheet.merge_range("J13:L13", u'Comentario', merge_format_t31)


		cnc = [u'Objetivo de Produccion Mensual en perforación',
			   u'Acumulado de Produccion Mensual',
			   u'Tendencia de Produccion Mensual',
			   u'Promedio de Metros lineales Perforados',
			   u'Promedio  Consumo de Explosivo',
			   u'Promedio de Consumo de Combustible',
			   u'Promedio  Consumo de Agua Caminos',
			   u'Costo Promedio de Producir una Tonelada']

		cnt = []
		eioc1 = self.env['extraccion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',u'Objetivo Mes')])
		if len(eioc1) > 0:
			eioc1 = eioc1[0]
			cnt.append(eioc1.cantidad)
		else:
			cnt.append(0)
		eioc2 = self.env['extraccion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',u'Acumulado Mes')])
		if len(eioc2) > 0:
			eioc2 = eioc2[0]
			cnt.append(eioc2.cantidad)
		else:
			cnt.append(0)
		if len(eioc1) > 0 and len(eioc2) > 0:
			cnt.append(eioc1.cantidad-eioc2.cantidad)
		else:
			cnt.append(0)
		eioc3 = self.env['extraccion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',u'Promedio Día')])
		if len(eioc3) > 0:
			eioc3 = eioc3[0]
			cnt.append(eioc3.cantidad)
		else:
			cnt.append(0)
		eioc4 = self.env['extraccion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',u'Promedio de Consumo Explosivo')])
		if len(eioc4) > 0:
			eioc4 = eioc4[0]
			cnt.append(eioc4.cantidad)
		else:
			cnt.append(0)
		eioc5 = self.env['extraccion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',u'Promedio de Consumo Diesel')])
		if len(eioc5) > 0:
			eioc5 = eioc5[0]
			cnt.append(eioc5.cantidad)
		else:
			cnt.append(0)

		cnt.append(0)
		cnt.append(0)

		und = [u'metros lineales',
			   u'metros lineales',
			   u'metros lineales',
			   u'Mts / Hr',
			   u'Grs / Ton',
			   u'Gls / ml perf',
			   u'Lts / Dia',
			   u'Soles / Ton']

		x = 13
		for i in range(len(cnc)):
			if x % 2 == 0:
				if i == len(cnc)-1:
					worksheet.merge_range(x,2,x,4,cnc[i], data_format_dlrd)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrd)
					worksheet.write(x,8, und[i], data_format_dlrd)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrd)
				else:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlr)
					worksheet.write(x,8, und[i], data_format_dlr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlr)
			else:
				if i == len(cnc)-1:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrdgr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrdgr)
					worksheet.write(x,8, und[i], data_format_dlrdgr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrdgr)
				else:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrgr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrgr)
					worksheet.write(x,8, und[i], data_format_dlrgr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrgr)
			x += 1

		x += 1

		worksheet.merge_range(x,2,x,11, u'Comportamiento Trituración', merge_format_t31_tr)
		x += 2
		worksheet.merge_range(x,2,x,4, u'Concepto', merge_format_t31_tr)
		worksheet.merge_range(x,5,x,7, u'Cantidad', merge_format_t31_tr)
		worksheet.write(x,8, u'Unidad', merge_format_t31_tr)
		worksheet.merge_range(x,9,x,11, u'Comentario', merge_format_t31_tr)

		x += 1

		cnc = [u'Objetivo de Produccion Mensual',
			   u'Acumulado de Produccion Mensual',
			   u'Tendencia de Produccion Mensual',
			   u'Aprovechamiento de Piedra Horno',
			   u'Promedio Productividad',
			   u'Promedio Envío Piedra a Planta de Calcinación',
			   u'Calidad de Carbonato',
			   u'Calidad de Silice en la Piedra',
			   u'Promedio de Consumo de Combustible',
			   u'Promedio de Consumo de Energia Eléctrica',
			   u'Promedio de Consumo de Agua Niebla Seca',
			   u'Costo Promedio de Producir una Tonelada',]

		cnt = []
		#1
		tioc1 = self.env['trituracion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',u'Objetivo Mes')])
		if len(tioc1) > 0:
			tioc1 = tioc1[0]
			cnt.append(tioc1.cantidad)
		else:
			cnt.append(0)
		#2
		tioc2 = self.env['trituracion.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',u'Acumulado Mes')])
		if len(tioc2) > 0:
			tioc2 = tioc2[0]
			cnt.append(tioc2.cantidad)
		else:
			cnt.append(0)
		#3
		cnt.append(cnt[0]-cnt[1])
		#4
		tioc4 = self.env['trituracion.negro.africano'].search([('year_id','=',yr),('month_id','=',mnth)])
		qty4 = 0
		for i in tioc4:
			qty4 += i.horno
		r4 = (qty4/float(len(tioc4))) if float(len(tioc4)) != 0 else 0
		cnt.append(r4)
		#5
		tioc5 = self.env['trituracion.negro.africano'].search([('year_id','=',yr),('month_id','=',mnth)])
		qty5 = 0
		for i in tioc5:
			qty5 += i.tph
		r5 = (qty5/float(len(tioc5))) if float(len(tioc5)) != 0 else 0
		cnt.append(r5)
		#6
		cnt.append(0)
		#7
		tioc7 = self.env['trituracion.negro.africano'].search([('year_id','=',yr),('month_id','=',mnth)])
		qty7 = 0
		for i in tioc7:
			qty7 += i.co3
		r7 = (qty7/(float(100)*float(len(tioc7)))) if (float(100)*float(len(tioc7))) != 0 else 0
		cnt.append(r7)
		#8
		tioc8 = self.env['trituracion.negro.africano'].search([('year_id','=',yr),('month_id','=',mnth)])
		qty8 = 0
		for i in tioc8:
			qty8 += i.silice
		r8 = (qty8/(float(100)*float(len(tioc8)))) if (float(100)*float(len(tioc8))) != 0 else 0
		cnt.append(r8)
		#9
		tioc9 = self.env['trituracion.negro.africano'].search([('year_id','=',yr),('month_id','=',mnth)])
		qty9 = 0
		qty92 = 0
		qty93 = 0
		for i in tioc9:
			qty9 += i.consumo_diesel_1
			qty92 += i.consumo_diesel_2
			qty93 += i.total_tn
		r9 = ((qty9+qty92)/qty93) if qty93 != 0 else 0
		cnt.append(r9)
		#10
		tioc10 = self.env['trituracion.negro.africano'].search([('year_id','=',yr),('month_id','=',mnth)])
		qty10 = 0
		for i in tioc10:
			qty10 += i.silice
		cnt.append(qty10)
		#11
		tioc11 = self.env['trituracion.negro.africano'].search([('year_id','=',yr),('month_id','=',mnth)])
		qty11 = 0
		qty112 = 0
		for i in tioc11:
			qty11 += i.niebla
			qty112 += i.total_tn
		r11 = (qty11/qty112) if qty112 != 0 else 0
		cnt.append(r11)
		#12
		cnt.append(0)

		und = [u'Tons',
			   u'Tons',
			   u'Tons',
			   u'%',
			   u'TPH',
			   u'Ton / Día',
			   u'%  CaCO3',
			   u'%  silice',
			   u'Gls / Ton',
			   u'kwh / Ton',
			   u'Lts / Ton',
			   u'Soles / Ton']

		for i in range(len(cnc)):
			if x % 2 == 0:
				if i == len(cnc)-1:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrd)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrd)
					worksheet.write(x,8, und[i], data_format_dlrd)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrd)
				else:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlr)
					worksheet.write(x,8, und[i], data_format_dlr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlr)
			else:
				if i == len(cnc)-1:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrdgr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrdgr)
					worksheet.write(x,8, und[i], data_format_dlrdgr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrdgr)
				else:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrgr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrgr)
					worksheet.write(x,8, und[i], data_format_dlrgr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrgr)
			x += 1

		x += 1

		worksheet.merge_range(x,2,x,11, u'Comportamiento Pulverizado Combustible Sólido', merge_format_t31_ac)
		x += 2
		worksheet.merge_range(x,2,x,4, u'Concepto', merge_format_t31_ac)
		worksheet.merge_range(x,5,x,7, u'Cantidad', merge_format_t31_ac)
		worksheet.write(x,8, u'Unidad', merge_format_t31_ac)
		worksheet.merge_range(x,9,x,11, u'Comentario', merge_format_t31_ac)

		x += 1

		cnc = [u'Objetivo de Produccion Mensual',
			   u'Acumulado de Produccion Mensual',
			   u'Tendencia de Produccion Mensual',
			   u'Promedio Productividad',
			   u'Promedio Finura M. 170',
			   u'Promedio Poder Calorífico',
			   u'Promedio Humedad Petcoke Pulverizado',
			   u'Promedio de Consumo de Diesel',
			   u'Promedio de Consumo de Energía Eléctrica',
			   u'Costo Promedio de Producir una Tonelada',]

		cnt = []

		#1
		acioc1 = self.env['anivi.coke.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',u'Objetivo Mes')])
		if len(acioc1) > 0:
			acioc1 = acioc1[0]
			cnt.append(acioc1.cantidad)
		else:
			cnt.append(0)
		#2
		acioc2 = self.env['anivi.coke.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',u'Acumulado Mes')])
		if len(acioc2) > 0:
			acioc2 = acioc2[0]
			cnt.append(acioc2.cantidad)
		else:
			cnt.append(0)
		#3
		cnt.append(0)
		#4
		cnt.append(0)
		#5
		cnt.append(0)		
		#6
		cnt.append(0)
		#7
		cnt.append(0)		
		#8
		cnt.append(0)		
		#9
		cnt.append(0)		
		#10
		cnt.append(0)		

		und = [u'Tons',
			   u'Tons',
			   u'Tons',
			   u'TPH',
			   u'%',
			   u'kcal / kg',
			   u'%',
			   u'Gls / Ton',
			   u'kwh / Ton',
			   u'Soles / Ton',]

		for i in range(len(cnc)):
			if x % 2 == 0:
				if i == len(cnc)-1:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrd)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrd)
					worksheet.write(x,8, und[i], data_format_dlrd)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrd)
				else:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlr)
					worksheet.write(x,8, und[i], data_format_dlr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlr)
			else:
				if i == len(cnc)-1:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrdgr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrdgr)
					worksheet.write(x,8, und[i], data_format_dlrdgr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrdgr)
				else:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrgr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrgr)
					worksheet.write(x,8, und[i], data_format_dlrgr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrgr)
			x += 1

		x += 1

		worksheet.merge_range(x,2,x,11, u'Comportamiento Horno Maerz No. 1', merge_format_t31_mae)
		x += 2
		worksheet.merge_range(x,2,x,4, u'Concepto', merge_format_t31_mae)
		worksheet.merge_range(x,5,x,7, u'Cantidad', merge_format_t31_mae)
		worksheet.write(x,8, u'Unidad', merge_format_t31_mae)
		worksheet.merge_range(x,9,x,11, u'Comentario', merge_format_t31_mae)

		x += 1

		cnc = [u'Objetivo de Produccion Mensual',
			   u'Acumulado de Produccion Mensual',
			   u'Tendencia de Produccion Mensual',
			   u'Promedio Operación de Horno',
			   u'Promedio de PPC',
			   u'Promedio de CaO Disponible',
			   u'Promedio de Poder Calorífico de Polvos Colector',
			   u'Promedio de Consumo de Combustible',
			   u'Promedio de Consumo de Combustible',
			   u'Promedio de Consumo de Energia Eléctrica',
			   u'Costo Promedio de Producir una Tonelada',]

		cnt = []
		#1
		mioc1 = self.env['maerz.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',u'Objetivo Mes')])
		if len(mioc1) > 0:
			mioc1 = mioc1[0]
			cnt.append(mioc1.cantidad)
		else:
			cnt.append(0)
		#2
		cnt.append(0)
		#3
		cnt.append(0)
		#4
		cnt.append(0)
		#5
		cnt.append(0)
		#6
		cnt.append(0)
		#7
		cnt.append(0)
		#8
		cnt.append(0)
		#9
		cnt.append(0)
		#10
		cnt.append(0)
		#11
		cnt.append(0)

		und = [u'Tons',
			   u'Tons',
			   u'Tons',
			   u'Hrs / Día',
			   u'[-]',
			   u'%',
			   u'kcal / kg',
			   u'kgs / ton',
			   u'Mcal / TonCal',
			   u'kwh / Ton',
			   u'Soles / Ton',]

		for i in range(len(cnc)):
			if x % 2 == 0:
				if i == len(cnc)-1:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrd)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrd)
					worksheet.write(x,8, und[i], data_format_dlrd)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrd)
				else:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlr)
					worksheet.write(x,8, und[i], data_format_dlr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlr)
			else:
				if i == len(cnc)-1:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrdgr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrdgr)
					worksheet.write(x,8, und[i], data_format_dlrdgr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrdgr)
				else:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrgr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrgr)
					worksheet.write(x,8, und[i], data_format_dlrgr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrgr)
			x += 1

		x += 1

		worksheet.merge_range(x,2,x,11, u'Comportamiento Pulverizado CaO', merge_format_t31_pul)
		x += 2
		worksheet.merge_range(x,2,x,4, u'Concepto', merge_format_t31_pul)
		worksheet.merge_range(x,5,x,7, u'Cantidad', merge_format_t31_pul)
		worksheet.write(x,8, u'Unidad', merge_format_t31_pul)
		worksheet.merge_range(x,9,x,11, u'Comentario', merge_format_t31_pul)

		x += 1

		cnc = [u'Objetivo de Produccion Mensual',
			   u'Acumulado de Produccion Mensual',
			   u'Tendencia de Produccion Mensual',
			   u'Productividad',
			   u'Promedio de Finura M. 100',
			   u'Promedio de Finura M. 200',
			   u'Promedio de CaO Total',
			   u'Promedio de Consumo de Energia Eléctrica',
			   u'Costo Promedio de Producir una Tonelada',]

		cnt = []
		#1
		pcioc1 = self.env['pulv.cao.indicadores.operacion'].search([('year_id','=',yr),('month_id','=',mnth),('concepto','=',u'Objetivo Mes')])
		if len(pcioc1) > 0:
			pcioc1 = pcioc1[0]
			cnt.append(pcioc1.cantidad)
		else:
			cnt.append(0)
		#2
		cnt.append(0)
		#3
		cnt.append(0)
		#4
		cnt.append(0)
		#5
		cnt.append(0)
		#6
		cnt.append(0)
		#7
		cnt.append(0)
		#8
		cnt.append(0)
		#9
		cnt.append(0)

		und = [u'Tons',
			   u'Tons',
			   u'Tons',
			   u'TPH',
			   u'%',
			   u'%',
			   u'%',
			   u'kwh / Ton',
			   u'Soles / Ton',]

		for i in range(len(cnc)):
			if x % 2 == 0:
				if i == len(cnc)-1:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrd)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrd)
					worksheet.write(x,8, und[i], data_format_dlrd)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrd)
				else:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlr)
					worksheet.write(x,8, und[i], data_format_dlr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlr)
			else:
				if i == len(cnc)-1:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrdgr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrdgr)
					worksheet.write(x,8, und[i], data_format_dlrdgr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrdgr)
				else:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrgr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrgr)
					worksheet.write(x,8, und[i], data_format_dlrgr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrgr)
			x += 1

		x += 1

		worksheet.merge_range(x,2,x,11, u'Comportamiento Ventas Cal Viva', merge_format_t31_sal)
		x += 2
		worksheet.merge_range(x,2,x,4, u'Concepto', merge_format_t31_sal)
		worksheet.merge_range(x,5,x,7, u'Cantidad', merge_format_t31_sal)
		worksheet.write(x,8, u'Unidad', merge_format_t31_sal)
		worksheet.merge_range(x,9,x,11, u'Comentario', merge_format_t31_sal)

		x += 1

		cnc = [u'Objetivo de Ventas Mensual Cal Viva Granel',
			   u'Acumulado de Ventas Mensual Cal Viva Granel',
			   u'Tendencia de Ventas Mensual Cal Viva Granel',
			   u'Objetivo de Ventas Mensual Cal Viva Pulverizado',
			   u'Acumulado de Ventas Mensual Cal Viva Pulverizado',
			   u'Tendencia de Ventas Mensual Cal Viva Pulverizado',
			   u'Promedio de Ventas Diarias',
			   u'Total de Ventas de Cal Viva',
			   u'Inventario Actual de Cal Viva Granel',
			   u'Inventario Actual de Cal Viva Pulverizada',]

		cnt = []
		#1
		cnt.append(0)
		#2
		cnt.append(0)
		#3
		cnt.append(0)
		#4
		cnt.append(0)
		#5
		cnt.append(0)
		#6
		cnt.append(0)
		#7
		cnt.append(0)
		#8
		cnt.append(0)
		#9
		cnt.append(0)
		#10
		cnt.append(0)

		und = [u'Tons',
			   u'Tons',
			   u'Tons',
			   u'Tons',
			   u'Tons',
			   u'Tons',
			   u'Tons',
			   u'Tons',
			   u'Tons',
			   u'Tons',]

		for i in range(len(cnc)):
			if x % 2 == 0:
				if i == len(cnc)-1:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrd)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrd)
					worksheet.write(x,8, und[i], data_format_dlrd)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrd)
				else:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlr)
					worksheet.write(x,8, und[i], data_format_dlr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlr)
			else:
				if i == len(cnc)-1:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrdgr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrdgr)
					worksheet.write(x,8, und[i], data_format_dlrdgr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrdgr)
				else:
					worksheet.merge_range(x,2,x,4, cnc[i], data_format_dlrgr)
					worksheet.merge_range(x,5,x,7, cnt[i], data_format_dlrgr)
					worksheet.write(x,8, und[i], data_format_dlrgr)
					worksheet.merge_range(x,9,x,11, '', data_format_dlrgr)
			x += 1

		workbook.close()
		
		f = open( direccion + u'Reporte_Diario_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx', 'rb')
			
		vals = {
			'output_name': u'Reporte_Diario_'+str(yr)+'_'+format(mnth, '02')+'_'+'.xlsx',
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