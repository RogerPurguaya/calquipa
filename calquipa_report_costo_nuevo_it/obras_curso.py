# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv


from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import magenta, red , black , blue, gray, Color, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table
from reportlab.lib.units import  cm,mm
from reportlab.lib.utils import simpleSplit
from cgi import escape
import decimal

class main_parameter(models.Model):
	_inherit = 'main.parameter'

	diario_asiento_costo = fields.Many2one('account.journal','Diario Asiento Costo')

	pproduct_costos_intermedia = fields.Many2one('product.product','Productos en Proceso Intermedia')
	pproduct_costos_extraccion = fields.Many2one('product.product','Productos en Proceso Extracción')
	pproduct_costos_calcinacion = fields.Many2one('product.product','Productos en Proceso Calcinación')
	pproduct_costos_trituracion = fields.Many2one('product.product','Productos en Proceso Trituración')
	pproduct_costos_micronizado = fields.Many2one('product.product','Productos en Proceso Micronizado')
	pproduct_costos_pet = fields.Many2one('product.product','Productos en Proceso Pet Coke')

	product_costos_intermedia = fields.Many2one('account.account','C. Productos en Proceso Intermedia')
	product_costos_extraccion = fields.Many2one('account.account','C. Productos en Proceso Extracción')
	product_costos_calcinacion = fields.Many2one('account.account','C. Productos en Proceso Calcinación')
	product_costos_trituracion = fields.Many2one('account.account','C. Productos en Proceso Trituración')
	product_costos_micronizado = fields.Many2one('account.account','C. Productos en Proceso Micronizado')
	product_costos_pet = fields.Many2one('account.account','C. Productos en Proceso Pet Coke')

	aa_variacion_almacenada_intermedia = fields.Many2one('account.account','Variación P. Almacenada Intermedia')
	aa_variacion_almacenada_extraccion = fields.Many2one('account.account','Variación P. Almacenada Extracción')
	aa_variacion_almacenada_calcinacion = fields.Many2one('account.account','Variación P. Almacenada Calcinación')
	aa_variacion_almacenada_trituracion = fields.Many2one('account.account','Variación P. Almacenada Trituración')
	aa_variacion_almacenada_micronizado = fields.Many2one('account.account','Variación P. Almacenada Micronizado')
	aa_variacion_almacenada_pet = fields.Many2one('account.account','Variación P. Almacenada Pet Coke')

	location_virtual_saldoinicial = fields.Many2one('stock.location','Ubicación Virtual Saldo Inicial') 
	location_virtual_produccion = fields.Many2one('stock.location','Ubicación Virtual Producción')
	location_existencias_intermedia = fields.Many2one('stock.location','Ubicación Existencias Intermedia')
	location_existencias_extraccion = fields.Many2one('stock.location','Ubicación Existencias Extracción')
	location_existencias_trituracion = fields.Many2one('stock.location','Ubicación Existencias Trituración')
	location_existencias_calcinacion = fields.Many2one('stock.location','Ubicación Existencias Calcinación')
	location_existencias_micronizado = fields.Many2one('stock.location','Ubicación Existencias Micronizado')
	location_existencias_pet = fields.Many2one('stock.location','Ubicación Existencias Pet Coke')

	location_perdidas_mermas = fields.Many2one('stock.location','Ubicación Calcinacion Perdidas Por Merma')
	location_micro_perdidas_mermas = fields.Many2one('stock.location','Ubicación Micronizado Perdidas Por Merma')




class costos_produccion_lineas(models.Model):
	_name = 'costos.produccion.lineas'

	periodo = fields.Many2one('account.period','Periodo',related='costos_id.periodo')
	centro_costo = fields.Char('Centro de Costo')
	monto = fields.Float('Monto',digits=(12,2))
	libro = fields.Many2one('account.journal','Libro')
	costos_id = fields.Many2one('costos.produccion','Costos')

class costos_produccion_asientos(models.Model):
	_name = 'costos.produccion.asientos'

	number = fields.Integer('Número')
	name = fields.Char('Descripción')
	asiento = fields.Many2one('account.move','Asiento')
	diario = fields.Many2one('account.journal','Diario',related="asiento.journal_id")
	periodo = fields.Many2one('account.period','Periodo',related="asiento.period_id")
	costos_id = fields.Many2one('costos.produccion','Costos')

class costos_produccion(models.Model):
	_name = 'costos.produccion'

	fiscal= fields.Many2one('account.fiscalyear','Ejercicio Fiscal')
	fecha = fields.Date('Fecha')
	periodo = fields.Many2one('account.period','Periodo')
	state = fields.Selection([('draft','Total Gastos'),('extraccion','C.C. Extracción'),('trituracion','C.C. Trituración'),('calcinacion','C.C. Calcinación'),('micronizado','C.C. Micronizado')],'Estado',default='draft')
	lineas = fields.One2many('costos.produccion.lineas','costos_id','Total Gastos')
	asiento_ids = fields.One2many('costos.produccion.asientos','costos_id','Total Gastos')





	@api.one
	def unlink(self):
		if len(self.asiento_ids)>0:
			raise osv.except_osv('Alerta!','No se puede eliminar si aun existen Asientos de Costos.')
		return super(costos_produccion,self).unlink()

	@api.one
	def verificador(self):		
		par = self.env['main.parameter'].search([])[0]
		if par.pproduct_costos_intermedia.id and par.pproduct_costos_extraccion.id and par.pproduct_costos_calcinacion.id and par.pproduct_costos_trituracion.id 		and par.pproduct_costos_micronizado.id 		and par.product_costos_intermedia.id and par.product_costos_extraccion.id and par.product_costos_calcinacion.id and par.product_costos_trituracion.id 		and par.product_costos_micronizado.id 		and par.aa_variacion_almacenada_intermedia.id and par.aa_variacion_almacenada_extraccion.id and par.aa_variacion_almacenada_calcinacion.id 		and par.aa_variacion_almacenada_trituracion.id and par.aa_variacion_almacenada_micronizado 		and par.location_virtual_produccion.id and par.location_existencias_intermedia.id and par.location_existencias_extraccion.id 		and par.location_existencias_trituracion.id and par.location_existencias_calcinacion.id and 		par.location_existencias_micronizado.id:
			pass
		else:
			raise osv.except_osv('Alerta!','No se configuro algun parametro de Costos.')
			return False

	@api.one
	def get_gastos_extraccion(self):
		self.verificador()
		rep = 0
		for i in self.lineas:
			if '921' in i.centro_costo:
				rep = i.monto
		self.gass_extra = rep

	@api.one
	def get_total_unidades_producidas_extraccion(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_extraccion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_extraccion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_extraccion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_extraccion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[0]

		self.tu_prod_extra = rep

	@api.one
	def get_c_uni_extra(self):
		self.verificador()
		if self.tu_prod_extra== 0:
			self.c_uni_extra = 0
		else:	
			self.c_uni_extra =  self.gass_extra / self.tu_prod_extra

	gass_extra = fields.Float('Total Gastos de Extracción',compute="get_gastos_extraccion",digits=(12,2))
	tu_prod_extra = fields.Float('Total Unidades Producidas',compute="get_total_unidades_producidas_extraccion",digits=(12,2))
	c_uni_extra = fields.Float('C. Unitario',compute="get_c_uni_extra",digits=(12,6))
	

	@api.one
	def get_prod_proc_anter_tri(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		fechaini = str(self.periodo.date_start).replace('-','')

		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute("""
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_extraccion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_extraccion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_extraccion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_extraccion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[1]

		self.prod_proc_anter_tri = rep

	@api.one
	def get_gastos_tri(self):
		self.verificador()
		rep = 0
		for i in self.lineas:
			if '922' in i.centro_costo:
				rep = i.monto
		self.gass_tri = rep

	@api.one
	def get_total_costo_tri(self):
		self.verificador()
		self.total_costo_tri= self.prod_proc_anter_tri + self.gass_tri

	@api.one
	def get_total_unidades_producidas_tri(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_trituracion.id) + """}') 
			where ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)


		for i in self.env.cr.fetchall():
			rep = i[0]

		self.tu_prod_tri = rep

	@api.one
	def get_c_uni_tri(self):
		self.verificador()
		if self.tu_prod_tri== 0:
			self.c_uni_tri=0
		else:
			self.c_uni_tri =  self.total_costo_tri / self.tu_prod_tri



	prod_proc_anter_tri = fields.Float('Producido en Procesos Anterior',compute="get_prod_proc_anter_tri",digits=(12,2))
	gass_tri = fields.Float('Total Gastos de Trituración',compute="get_gastos_tri",digits=(12,2))
	total_costo_tri = fields.Float('Total Costo de Proceso',compute="get_total_costo_tri",digits=(12,2))
	tu_prod_tri = fields.Float('Total Unidades Producidas',compute="get_total_unidades_producidas_tri",digits=(12,2))
	c_uni_tri = fields.Float('C. Unitario',compute="get_c_uni_tri",digits=(12,6))




	@api.one
	def get_prod_proc_anter_cal(self):
		self.verificador()

		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_intermedia.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)


		for i in self.env.cr.fetchall():
			rep = i[1]

		self.prod_proc_anter_cal = rep

	@api.one
	def get_gastos_cal(self):
		self.verificador()
		rep = 0
		for i in self.lineas:
			if '923' in i.centro_costo:
				rep = i.monto
		self.gass_cal = rep

	@api.one
	def get_total_costo_cal(self):
		self.verificador()
		self.total_costo_cal= self.prod_proc_anter_cal + self.gass_cal

	@api.one
	def get_total_unidades_producidas_cal(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_calcinacion.id) + """}') 
			where ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)


		for i in self.env.cr.fetchall():
			rep = i[0]


		self.tu_prod_cal = rep

	@api.one
	def get_c_uni_cal(self):
		self.verificador()
		if self.tu_prod_cal==0:
			self.c_uni_cal=0
		else:
			self.c_uni_cal =  self.total_costo_cal / self.tu_prod_cal



	prod_proc_anter_cal = fields.Float('Producido en Procesos Anterior',compute="get_prod_proc_anter_cal",digits=(12,2))
	gass_cal = fields.Float('Total Gastos de Calcinación',compute="get_gastos_cal",digits=(12,2))
	total_costo_cal = fields.Float('Total Costo de Proceso',compute="get_total_costo_cal",digits=(12,2))
	tu_prod_cal = fields.Float('Total Unidades Producidas',compute="get_total_unidades_producidas_cal",digits=(12,2))
	c_uni_cal = fields.Float('C. Unitario',compute="get_c_uni_cal",digits=(12,6))



	@api.one
	def get_prod_proc_anter_mic(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_calcinacion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)


		for i in self.env.cr.fetchall():
			rep = i[1]


		self.prod_proc_anter_mic = rep

	@api.one
	def get_gastos_mic(self):
		self.verificador()
		rep = 0
		for i in self.lineas:
			if '924' in i.centro_costo:
				rep = i.monto
		self.gass_mic = rep

	@api.one
	def get_total_costo_mic(self):
		self.verificador()
		self.total_costo_mic= self.prod_proc_anter_mic + self.gass_mic

	@api.one
	def get_total_unidades_producidas_mic(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_micronizado.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_micronizado.id) + """}') 
			where ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_micronizado.id) + """
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)		

		for i in self.env.cr.fetchall():
			rep = i[0]

		self.tu_prod_mic = rep

	@api.one
	def get_c_uni_mic(self):
		self.verificador()
		if self.tu_prod_mic==0:
			self.c_uni_mic=0
		else:
			self.c_uni_mic =  self.total_costo_mic / self.tu_prod_mic



	prod_proc_anter_mic = fields.Float('Producido en Procesos Anterior',compute="get_prod_proc_anter_mic",digits=(12,2))
	gass_mic = fields.Float('Total Gastos de Trituración',compute="get_gastos_mic",digits=(12,2))
	total_costo_mic = fields.Float('Total Costo de Proceso',compute="get_total_costo_mic",digits=(12,2))
	tu_prod_mic = fields.Float('Total Unidades Producidas',compute="get_total_unidades_producidas_mic",digits=(12,2))
	c_uni_mic = fields.Float('C. Unitario',compute="get_c_uni_mic",digits=(12,6))

	_rec_name = 'periodo'


	@api.one
	def crear_extraccion(self):
		self.verificador()
		#if self.c_uni_extra ==0:
		#	raise osv.except_osv('Alerta!',u'El precio unitario de Extracción es cero.')

		parametros = self.env['main.parameter'].search([])[0]

		self.env.cr.execute("""
		select sm.id  from stock_move sm 
		inner join stock_location sl on sl.id = sm.location_dest_id
		inner join stock_picking sp on sp.id = sm.picking_id
		inner join product_product pp on sm.product_id=pp.id
		inner join product_template pt on pt.id = pp.product_tmpl_id
		where (sm.location_id = """ + str(parametros.location_virtual_produccion.id) + """ and sm.location_dest_id = """ + str(parametros.location_existencias_extraccion.id) + """)
		and sm.state = 'done' and pt.type='product'
		and fecha_num(sp.date::date) >= fecha_num('""" + str(self.periodo.date_start) + """'::date) and fecha_num(sp.date::date) <= fecha_num('""" + str(self.periodo.date_stop) + """'::date)
		order by sp.date
		 """)

		for i in self.env.cr.fetchall():
			m = self.env['stock.move'].search([('id','=',i[0])])[0]
			m.precio_unitario_manual = self.c_uni_extra

		self.state= 'extraccion'


		if self.c_uni_extra !=0 and len(self.env['costos.produccion.asientos'].search([('costos_id','=',self.id),('number','=',1 )]) ) == 0:

			
			par = self.env['main.parameter'].search([])[0]
			#Extraccion
			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
			
			t = self.env['costos.produccion.lineas'].search([('centro_costo','=','921: Total Extracción'),('costos_id','=',self.id)])[0]			
			
			data = {
				'name':"Por el costo de produccion extraccion",
				'account_id':par.product_costos_extraccion.id,
				'debit':round(self.extra_pro_imp+0.00001,2),
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			data = {
				'name':"Por el costo de produccion extraccion",
				'account_id':par.aa_variacion_almacenada_extraccion.id,
				'debit':0,
				'credit':round(self.extra_pro_imp+0.00001,2),
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()

			new_data = {
				'number':1,
				'name':'Por el costo de produccion extraccion',
				'asiento':mkl.id,
				'costos_id':self.id,
			}
			new_asiento = self.env['costos.produccion.asientos'].create(new_data)


	@api.one
	def cancelar_extraccion(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]

		self.env.cr.execute("""
		select sm.id  from stock_move sm 
		inner join stock_location sl on sl.id = sm.location_dest_id
		inner join stock_picking sp on sp.id = sm.picking_id
		inner join product_product pp on sm.product_id=pp.id
		inner join product_template pt on pt.id = pp.product_tmpl_id
		where (sm.location_id = """ + str(parametros.location_virtual_produccion.id) + """ and sm.location_dest_id = """ + str(parametros.location_existencias_extraccion.id) + """)
		and sm.state = 'done' and pt.type='product'
		and fecha_num(sp.date::date) >= fecha_num('""" + str(self.periodo.date_start) + """'::date) and fecha_num(sp.date::date) <= fecha_num('""" + str(self.periodo.date_stop) + """'::date)
		order by sp.date
		 """)

		for i in self.env.cr.fetchall():
			m = self.env['stock.move'].search([('id','=',i[0])])[0]
			m.precio_unitario_manual = 0
		self.state= 'draft'

		for mi in self.env['costos.produccion.asientos'].search([('costos_id','=',self.id),('number','=',1 )]):
			if mi.asiento.id:
				if mi.asiento.state != 'draft':
					mi.asiento.button_cancel()
				mi.asiento.unlink()
			mi.unlink()

	@api.one
	def crear_trituracion(self):
		self.verificador()

		#if self.c_uni_tri ==0:
		#	raise osv.except_osv('Alerta!',u'El precio unitario de Trituración es cero.')

		parametros = self.env['main.parameter'].search([])[0]

		self.env.cr.execute("""
		select sm.id  from stock_move sm 
		inner join stock_location sl on sl.id = sm.location_dest_id
		inner join stock_picking sp on sp.id = sm.picking_id
		inner join product_product pp on sm.product_id=pp.id
		inner join product_template pt on pt.id = pp.product_tmpl_id
		where (sm.location_id = """ + str(parametros.location_virtual_produccion.id) + """ and sm.location_dest_id = """ + str(parametros.location_existencias_trituracion.id) + """)
		and sm.state = 'done' and pt.type='product'
		and fecha_num(sp.date::date) >= fecha_num('""" + str(self.periodo.date_start) + """'::date) and fecha_num(sp.date::date) <= fecha_num('""" + str(self.periodo.date_stop) + """'::date)
		order by sp.date
		 """)

		for i in self.env.cr.fetchall():
			m = self.env['stock.move'].search([('id','=',i[0])])[0]
			m.precio_unitario_manual = self.c_uni_tri


		parametros = self.env['main.parameter'].search([])[0]

		self.env.cr.execute("""
		select sm.id  from stock_move sm 
		inner join stock_location sl on sl.id = sm.location_dest_id
		inner join stock_picking sp on sp.id = sm.picking_id
		inner join product_product pp on sm.product_id=pp.id
		inner join product_template pt on pt.id = pp.product_tmpl_id
		where (sm.location_id = """ + str(parametros.location_virtual_produccion.id) + """ and sm.location_dest_id = """ + str(parametros.location_existencias_intermedia.id) + """)
		and sm.state = 'done' and pt.type='product'
		and fecha_num(sp.date::date) >= fecha_num('""" + str(self.periodo.date_start) + """'::date) and fecha_num(sp.date::date) <= fecha_num('""" + str(self.periodo.date_stop) + """'::date)
		order by sp.date
		 """)

		self.refresh()

		for i in self.env.cr.fetchall():
			m = self.env['stock.move'].search([('id','=',i[0])])[0]
			m.precio_unitario_manual = self.tritu_tt_cp

		self.state= 'trituracion'


		if self.c_uni_tri !=0 and len( self.env['costos.produccion.asientos'].search([('costos_id','=',self.id),('number','in',(2,3,4,5) )]) ) == 0:

			par = self.env['main.parameter'].search([])[0]
			#trituracion

			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
					
			data = {
				'name':"Por el traspaso de extraccion a trituracion",
				'account_id':par.aa_variacion_almacenada_extraccion.id,
				'debit':round(self.extra_tt_imp+0.00001,2),
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			data = {
				'name':"Por el traspaso de extraccion a trituracion",
				'account_id':par.product_costos_extraccion.id,
				'debit':0,
				'credit':round(self.extra_tt_imp+0.00001,2),
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()

			new_data = {
				'number':2,
				'name':'Por el traspaso de extraccion a trituracion',
				'asiento':mkl.id,
				'costos_id':self.id,
			}
			new_asiento = self.env['costos.produccion.asientos'].create(new_data)
			#-------------
			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
			
			t = self.env['costos.produccion.lineas'].search([('centro_costo','=','922: Total Trituración'),('costos_id','=',self.id)])[0]			
			
			"""
			data = {
				'name':"Por el costo de trituracion",
				'account_id':par.product_costos_trituracion.id,
				'debit':self.prod_proc_anter_tri,
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)"""
			data = {
				'name':"Por el costo de trituracion",
				'account_id':par.product_costos_trituracion.id,
				'debit': round(self.tritu_pro_imp+0.00001,2),
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			data = {
				'name':"Por el costo de trituracion",
				'account_id':par.aa_variacion_almacenada_trituracion.id,
				'debit':0,
				'credit': round(self.tritu_pro_imp+0.00001,2),
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()

			new_data = {
				'number':3,
				'name':'Por el costo de trituracion',
				'asiento':mkl.id,
				'costos_id':self.id,
			}
			new_asiento = self.env['costos.produccion.asientos'].create(new_data)
			#--------------------------

			parametros = self.env['main.parameter'].search([])[0]
			rep = 0

			fechaini = str(self.periodo.date_start).replace('-','')
			fecha_inianio = fechaini[:4] + '0101'
			fechafin = str(self.periodo.date_stop).replace('-','')

			#self.env.cr.execute(""" 
			#	select sum(ingreso) as ingreso,sum(round(credit,2)) as credit from (
			#	select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
			#	'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_trituracion.id) + """}') 
			#	where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
			#	or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """)
			#	) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

			#for i in self.env.cr.fetchall():
			#	rep = i[1]

			rep = self.tritu_tt_imp

			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
					
			data = {
				'name':"Por el traspaso al almacen patio",
				'account_id':par.aa_variacion_almacenada_trituracion.id,
				'debit': round(rep+0.00001,2),
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			data = {
				'name':"Por el traspaso al almacen patio",
				'account_id':par.product_costos_trituracion.id,
				'debit':0,
				'credit': round(rep+0.00001,2),
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()

			new_data = {
				'number':4,
				'name':'Por el traspaso al almacen patio',
				'asiento':mkl.id,
				'costos_id':self.id,
			}
			new_asiento = self.env['costos.produccion.asientos'].create(new_data)
			#-------------

			rep = self.piedra_pro_imp


			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
			
			data = {
				'name':"Por el ingreso al almacen patio",
				'account_id':par.product_costos_intermedia.id,
				'debit': round(rep+0.00001,2),
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			data = {
				'name':"Por el ingreso al almacen patio",
				'account_id':par.aa_variacion_almacenada_intermedia.id,
				'debit':0,
				'credit': round(rep+0.00001,2),
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()

			new_data = {
				'number':5,
				'name':'Por el ingreso al almacen patio',
				'asiento':mkl.id,
				'costos_id':self.id,
			}
			new_asiento = self.env['costos.produccion.asientos'].create(new_data)

	@api.one
	def cancelar_trituracion(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]

		self.env.cr.execute("""
		select sm.id  from stock_move sm 
		inner join stock_location sl on sl.id = sm.location_dest_id
		inner join stock_picking sp on sp.id = sm.picking_id
		inner join product_product pp on sm.product_id=pp.id
		inner join product_template pt on pt.id = pp.product_tmpl_id
		where (sm.location_id = """ + str(parametros.location_virtual_produccion.id) + """ and sm.location_dest_id = """ + str(parametros.location_existencias_trituracion.id) + """)
		and sm.state = 'done' and pt.type='product'
		and fecha_num(sp.date::date) >= fecha_num('""" + str(self.periodo.date_start) + """'::date) and fecha_num(sp.date::date) <= fecha_num('""" + str(self.periodo.date_stop) + """'::date)
		order by sp.date
		 """)

		for i in self.env.cr.fetchall():
			m = self.env['stock.move'].search([('id','=',i[0])])[0]
			m.precio_unitario_manual = 0

		self.env.cr.execute("""
		select sm.id  from stock_move sm 
		inner join stock_location sl on sl.id = sm.location_dest_id
		inner join stock_picking sp on sp.id = sm.picking_id
		inner join product_product pp on sm.product_id=pp.id
		inner join product_template pt on pt.id = pp.product_tmpl_id
		where (sm.location_id = """ + str(parametros.location_virtual_produccion.id) + """ and sm.location_dest_id = """ + str(parametros.location_existencias_intermedia.id) + """)
		and sm.state = 'done' and pt.type='product'
		and fecha_num(sp.date::date) >= fecha_num('""" + str(self.periodo.date_start) + """'::date) and fecha_num(sp.date::date) <= fecha_num('""" + str(self.periodo.date_stop) + """'::date)
		order by sp.date
		 """)

		for i in self.env.cr.fetchall():
			m = self.env['stock.move'].search([('id','=',i[0])])[0]
			m.precio_unitario_manual = 0



		self.state= 'extraccion'


		for mi in self.env['costos.produccion.asientos'].search([('costos_id','=',self.id),('number','in',(2,3,4,5) )]):
			if mi.asiento.id:
				if mi.asiento.state != 'draft':
					mi.asiento.button_cancel()
				mi.asiento.unlink()
			mi.unlink()

	@api.one
	def crear_calcinacion(self):
		self.verificador()

		#if self.c_uni_cal ==0:
		#	raise osv.except_osv('Alerta!',u'El precio unitario de Calcinación es cero.')

		parametros = self.env['main.parameter'].search([])[0]
		par = self.env['main.parameter'].search([])[0]

		self.env.cr.execute("""
		select sm.id  from stock_move sm 
		inner join stock_location sl on sl.id = sm.location_dest_id
		inner join stock_picking sp on sp.id = sm.picking_id
		inner join product_product pp on sm.product_id=pp.id
		inner join product_template pt on pt.id = pp.product_tmpl_id
		where (sm.location_id = """ + str(parametros.location_virtual_produccion.id) + """ and sm.location_dest_id = """ + str(parametros.location_existencias_calcinacion.id) + """)
		and sm.state = 'done' and pt.type='product'
		and fecha_num(sp.date::date) >= fecha_num('""" + str(self.periodo.date_start) + """'::date) and fecha_num(sp.date::date) <= fecha_num('""" + str(self.periodo.date_stop) + """'::date)
		order by sp.date
		 """)

		for i in self.env.cr.fetchall():
			m = self.env['stock.move'].search([('id','=',i[0])])[0]
			m.precio_unitario_manual = self.c_uni_cal

		self.state= 'calcinacion'
		#calcinacion



		if self.c_uni_cal !=0 and len(self.env['costos.produccion.asientos'].search([('costos_id','=',self.id),('number','in',(6,7) )]) )==0:

			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
					
			data = {
				'name':"Por el traspaso de patio a calcinacion",
				'account_id':par.aa_variacion_almacenada_intermedia.id,
				'debit': round(self.piedra_tt_imp+0.00001,2),
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			data = {
				'name':"Por el traspaso de patio a calcinacion",
				'account_id':par.product_costos_intermedia.id,
				'debit':0,
				'credit': round(self.piedra_tt_imp+0.00001,2),
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()

			new_data = {
				'number':6,
				'name':'Por el traspaso de patio a calcinacion',
				'asiento':mkl.id,
				'costos_id':self.id,
			}
			new_asiento = self.env['costos.produccion.asientos'].create(new_data)
			#-------------
			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
			
			t = self.env['costos.produccion.lineas'].search([('centro_costo','=','923: Total Calcinación'),('costos_id','=',self.id)])[0]			
			
			data = {
				'name':"Por el costo de calcinacion",
				'account_id':par.product_costos_calcinacion.id,
				'debit': round(self.calci_pro_imp+0.00001,2),
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			"""
			data = {
				'name':"Por el costo de calcinacion",
				'account_id':par.product_costos_calcinacion.id,
				'debit':t.monto,
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			"""
			data = {
				'name':"Por el costo de calcinacion",
				'account_id':par.aa_variacion_almacenada_calcinacion.id,
				'debit':0,
				'credit': round(self.calci_pro_imp+0.00001,2),
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()

			new_data = {
				'number':7,
				'name':'Por el costo de calcinacion',
				'asiento':mkl.id,
				'costos_id':self.id,
			}
			new_asiento = self.env['costos.produccion.asientos'].create(new_data)

	@api.one
	def cancelar_calcinacion(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]

		self.env.cr.execute("""
		select sm.id  from stock_move sm 
		inner join stock_location sl on sl.id = sm.location_dest_id
		inner join stock_picking sp on sp.id = sm.picking_id
		inner join product_product pp on sm.product_id=pp.id
		inner join product_template pt on pt.id = pp.product_tmpl_id
		where (sm.location_id = """ + str(parametros.location_virtual_produccion.id) + """ and sm.location_dest_id = """ + str(parametros.location_existencias_calcinacion.id) + """)
		and sm.state = 'done' and pt.type='product'
		and fecha_num(sp.date::date) >= fecha_num('""" + str(self.periodo.date_start) + """'::date) and fecha_num(sp.date::date) <= fecha_num('""" + str(self.periodo.date_stop) + """'::date)
		order by sp.date
		 """)

		for i in self.env.cr.fetchall():
			m = self.env['stock.move'].search([('id','=',i[0])])[0]
			m.precio_unitario_manual = 0
		self.state= 'trituracion'


		for mi in self.env['costos.produccion.asientos'].search([('costos_id','=',self.id),('number','in',(6,7) )]):
			if mi.asiento.id:
				if mi.asiento.state != 'draft':
					mi.asiento.button_cancel()
				mi.asiento.unlink()
			mi.unlink()


	@api.one
	def crear_micronizado(self):
		self.verificador()

		#if self.c_uni_mic ==0:
		#	raise osv.except_osv('Alerta!',u'El precio unitario de Micronizado es cero.')

		parametros = self.env['main.parameter'].search([])[0]
		par = self.env['main.parameter'].search([])[0]

		self.env.cr.execute("""
		select sm.id  from stock_move sm 
		inner join stock_location sl on sl.id = sm.location_dest_id
		inner join stock_picking sp on sp.id = sm.picking_id
		inner join product_product pp on sm.product_id=pp.id
		inner join product_template pt on pt.id = pp.product_tmpl_id
		where (sm.location_id = """ + str(parametros.location_virtual_produccion.id) + """ and sm.location_dest_id = """ + str(parametros.location_existencias_micronizado.id) + """)
		and sm.state = 'done' and pt.type='product'
		and fecha_num(sp.date::date) >= fecha_num('""" + str(self.periodo.date_start) + """'::date) and fecha_num(sp.date::date) <= fecha_num('""" + str(self.periodo.date_stop) + """'::date)
		order by sp.date
		 """)

		for i in self.env.cr.fetchall():
			m = self.env['stock.move'].search([('id','=',i[0])])[0]
			m.precio_unitario_manual = self.c_uni_mic

		self.state= 'micronizado'
		#micronizado


		if self.c_uni_mic !=0 and len( self.env['costos.produccion.asientos'].search([('costos_id','=',self.id),('number','in',(8,9) )]) )==0:

			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
					
			data = {
				'name':"Por el traspaso a micronizado",
				'account_id':par.aa_variacion_almacenada_calcinacion.id,
				'debit': round(self.calci_tt_imp+0.00001,2),
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			data = {
				'name':"Por el traspaso a micronizado",
				'account_id':par.product_costos_calcinacion.id,
				'debit':0,
				'credit': round(self.calci_tt_imp+0.00001,2),
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()

			new_data = {
				'number':8,
				'name':'Por el traspaso a micronizado',
				'asiento':mkl.id,
				'costos_id':self.id,
			}
			new_asiento = self.env['costos.produccion.asientos'].create(new_data)
			#-------------
			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
			
			t = self.env['costos.produccion.lineas'].search([('centro_costo','=','924: Total Micronizado'),('costos_id','=',self.id)])[0]			
			
			data = {
				'name':"Por el costo de micronizado",
				'account_id':par.product_costos_micronizado.id,
				'debit': round(self.micro_pro_imp+0.00001,2),
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			"""
			data = {
				'name':"Por el costo de micronizado",
				'account_id':par.product_costos_micronizado.id,
				'debit':t.monto,
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			"""
			data = {
				'name':"Por el costo de micronizado",
				'account_id':par.aa_variacion_almacenada_micronizado.id,
				'debit':0,
				'credit': round(self.micro_pro_imp+0.00001,2),
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()

			new_data = {
				'number':9,
				'name':'Por el costo de micronizado',
				'asiento':mkl.id,
				'costos_id':self.id,
			}
			new_asiento = self.env['costos.produccion.asientos'].create(new_data)

	@api.one
	def cancelar_micronizado(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]

		self.env.cr.execute("""
		select sm.id  from stock_move sm 
		inner join stock_location sl on sl.id = sm.location_dest_id
		inner join stock_picking sp on sp.id = sm.picking_id
		inner join product_product pp on sm.product_id=pp.id
		inner join product_template pt on pt.id = pp.product_tmpl_id
		where (sm.location_id = """ + str(parametros.location_virtual_produccion.id) + """ and sm.location_dest_id = """ + str(parametros.location_existencias_micronizado.id) + """)
		and sm.state = 'done' and pt.type='product'
		and fecha_num(sp.date::date) >= fecha_num('""" + str(self.periodo.date_start) + """'::date) and fecha_num(sp.date::date) <= fecha_num('""" + str(self.periodo.date_stop) + """'::date)
		order by sp.date
		 """)

		for i in self.env.cr.fetchall():
			m = self.env['stock.move'].search([('id','=',i[0])])[0]
			m.precio_unitario_manual = 0

		self.state= 'calcinacion'

		for mi in self.env['costos.produccion.asientos'].search([('costos_id','=',self.id),('number','in',(8,9) )]):
			if mi.asiento.id:
				if mi.asiento.state != 'draft':
					mi.asiento.button_cancel()
				mi.asiento.unlink()
			mi.unlink()


	@api.one
	def eliminar_asiento(self):
		self.verificador()
		for i in self.lineas:
			if i.asiento.id:
				if i.asiento.state!='draft':
					i.asiento.button_cancel()
				i.asiento.unlink()

	@api.one
	def crear_asiento(self):
		self.verificador()
		for i in self.lineas:
			if i.asiento.id:
				raise osv.except_osv('Alerta!','Existe asientos creados.')

		if len(self.lineas)!=4:
			raise  osv.except_osv('Alerta!','Debe Guardar Primero Costos.')
		par = self.env['main.parameter'].search([])[0]
		if par.diario_asiento_costo.id and par.product_costos_extraccion.id and par.product_costos_calcinacion.id and par.product_costos_trituracion.id and par.product_costos_micronizado.id and par.aa_variacion_almacenada_extraccion.id and par.aa_variacion_almacenada_calcinacion.id and par.aa_variacion_almacenada_trituracion.id and par.aa_variacion_almacenada_micronizado.id:
			#Extraccion
			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
			
			t = self.env['costos.produccion.lineas'].search([('centro_costo','=','921: Total Extracción'),('costos_id','=',self.id)])[0]			
			t.asiento = mkl.id		

			data = {
				'name':"Por el total de gastos de extraccion",
				'account_id':par.product_costos_extraccion.id,
				'debit':t.monto,
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			data = {
				'name':"Por el total de gastos de extraccion",
				'account_id':par.aa_variacion_almacenada_extraccion.id,
				'debit':0,
				'credit':t.monto,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()

			#Trituracion
			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
			
			t = self.env['costos.produccion.lineas'].search([('centro_costo','=','922: Total Trituración'),('costos_id','=',self.id)])[0]			
			t.asiento = mkl.id		

			data = {
				'name':"Por el total de gastos de trituracion",
				'account_id':par.product_costos_trituracion.id,
				'debit':t.monto,
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			data = {
				'name':"Por el total de gastos de trituracion",
				'account_id':par.aa_variacion_almacenada_trituracion.id,
				'debit':0,
				'credit':t.monto,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()



			#Calcinacion
			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
			
			t = self.env['costos.produccion.lineas'].search([('centro_costo','=','923: Total Calcinación'),('costos_id','=',self.id)])[0]			
			t.asiento = mkl.id		

			data = {
				'name':"Por el total de gastos de calcinacion",
				'account_id':par.product_costos_calcinacion.id,
				'debit':t.monto,
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			data = {
				'name':"Por el total de gastos de calcinacion",
				'account_id':par.aa_variacion_almacenada_calcinacion.id,
				'debit':0,
				'credit':t.monto,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()




			#Micronizado
			data_move = {
				'period_id': self.periodo.id,
				'journal_id':par.diario_asiento_costo.id,
				'date':self.fecha,
			}
			mkl = self.env['account.move'].create(data_move)
			
			t = self.env['costos.produccion.lineas'].search([('centro_costo','=','924: Total Micronizado'),('costos_id','=',self.id)])[0]			
			t.asiento = mkl.id		

			data = {
				'name':"Por el total de gastos de micronizado",
				'account_id':par.product_costos_micronizado.id,
				'debit':t.monto,
				'credit':0,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)
			data = {
				'name':"Por el total de gastos de micronizado",
				'account_id':par.aa_variacion_almacenada_micronizado.id,
				'debit':0,
				'credit':t.monto,
				'move_id':mkl.id,
			}		
			self.env['account.move.line'].create(data)

			if mkl.state == 'draft':
				mkl.button_validate()

		else:
			raise osv.except_osv('Alerta!','No estan configuracidos los parametros de Costos')

	@api.model
	def create(self,vals):
		self.verificador()
		t = super(costos_produccion,self).create(vals)


		if len ( self.env['costos.produccion'].search( [('periodo','=',t.periodo.id),('id','!=',t.id)] ) ) >0:
			raise osv.except_osv('Alerta!','Ya existe un Costo de Producción para Periodo Elegido' )

		parametros = self.env['main.parameter'].search([])[0]

		period_txt = t.periodo.code.split('/')
		period_txt = period_txt[1] + period_txt[0]

		self.env.cr.execute( """
		select substring(cuenta,1,3),sum(debe-haber) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
		where substring(cuenta,1,3)  in ('921','922','923','924')
		group by substring(cuenta,1,3) """)

		c_921 = 0
		c_922 = 0
		c_923 = 0
		c_924 = 0

		for i in self.env.cr.fetchall():
			if i[0]=='921':
				c_921 = i[1]
			if i[0]=='922':
				c_922 = i[1]
			if i[0]=='923':
				c_923 = i[1]
			if i[0]=='924':
				c_924 = i[1]

		data = {
			'costos_id':t.id,
			'libro':parametros.diario_asiento_costo.id,
			'monto':c_921,
			'centro_costo':'921: Total Extracción',
		}
		self.env['costos.produccion.lineas'].create(data)

		data['centro_costo'] = '922: Total Trituración'
		data['monto'] = c_922
		self.env['costos.produccion.lineas'].create(data)

		data['centro_costo'] = '923: Total Calcinación'
		data['monto'] = c_923
		self.env['costos.produccion.lineas'].create(data)

		data['centro_costo'] = '924: Total Micronizado'
		data['monto'] = c_924
		self.env['costos.produccion.lineas'].create(data)

		return t

	@api.one
	def write(self,vals):
		self.verificador()
		mt = super(costos_produccion,self).write(vals)
		self.refresh()

		if len ( self.env['costos.produccion'].search( [('periodo','=',self.periodo.id),('id','!=',self.id)] ) ) >0:
			raise osv.except_osv('Alerta!','Ya existe un Costo de Producción para el Periodo Elegido' )

		parametros = self.env['main.parameter'].search([])[0]

		period_txt = self.periodo.code.split('/')
		period_txt = period_txt[1] + period_txt[0]

		self.env.cr.execute( """
		select substring(cuenta,1,3),sum(debe-haber ) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
		where substring(cuenta,1,3)  in ('921','922','923','924')
		group by substring(cuenta,1,3) """)



		c_921 = 0
		c_922 = 0
		c_923 = 0
		c_924 = 0

		for i in self.env.cr.fetchall():
			if i[0]=='921':
				c_921 = i[1]
			if i[0]=='922':
				c_922 = i[1]
			if i[0]=='923':
				c_923 = i[1]
			if i[0]=='924':
				c_924 = i[1]

		
		t = self.env['costos.produccion.lineas'].search([('centro_costo','=','921: Total Extracción'),('costos_id','=',self.id)])[0]
		t.libro = parametros.diario_asiento_costo.id
		t.monto = c_921

		t = self.env['costos.produccion.lineas'].search([('centro_costo','=','922: Total Trituración'),('costos_id','=',self.id)])[0]
		t.libro = parametros.diario_asiento_costo.id
		t.monto = c_922

		t = self.env['costos.produccion.lineas'].search([('centro_costo','=','923: Total Calcinación'),('costos_id','=',self.id)])[0]
		t.libro = parametros.diario_asiento_costo.id
		t.monto = c_923

		t = self.env['costos.produccion.lineas'].search([('centro_costo','=','924: Total Micronizado'),('costos_id','=',self.id)])[0]
		t.libro = parametros.diario_asiento_costo.id
		t.monto = c_924

		return mt



	@api.one
	def get_extra_pro_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit   from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_extraccion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_extraccion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_extraccion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_extraccion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[0]

		self.extra_pro_ton = rep


	@api.one
	def get_extra_pro_imp(self):
		"""t = self.env['costos.produccion.lineas'].search([('centro_costo','=','921: Total Extracción'),('costos_id','=',self.id)])
		if t and t[0]:
			t = t[0]
			self.extra_pro_imp=t.monto
		else:
			self.extra_pro_imp= 0
		"""

		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, debit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_extraccion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_extraccion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_extraccion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_extraccion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[1]
			
		self.extra_pro_imp = rep

	@api.one
	def get_extra_pro_cp(self):
		if self.extra_pro_ton == 0:
			self.extra_pro_cp = 0
		else:
			self.extra_pro_cp = self.extra_pro_imp / self.extra_pro_ton


	@api.one
	def get_extra_tt_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, salida as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_extraccion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_extraccion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_extraccion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_extraccion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[0]

		self.extra_tt_ton = rep

	@api.one
	def get_extra_tt_imp(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_extraccion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_extraccion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_extraccion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_extraccion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[1]

		self.extra_tt_imp = rep

	@api.one
	def get_extra_tt_cp(self):
		if self.extra_tt_ton == 0:
			self.extra_tt_cp = 0
		else:
			self.extra_tt_cp = self.extra_tt_imp / self.extra_tt_ton


	@api.one
	def get_extra_final_ton(self):
		self.verificador()
		
		#parametros = self.env['main.parameter'].search([])[0]
		#rep = 0


		#fechaini = '01-01-2016'
		#fechaini = str(self.periodo.date_stop).split('-')[0] + '0101'
		#fechafin = str(self.periodo.date_stop).replace('-','')
		#self.env.cr.execute(""" 
		#	select saldof as ingreso,(round(credit,2)) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_extraccion.id) + """}',
		#	'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_extraccion.id) + """}') 
		#	where (ubicacion_destino = """ + str(parametros.location_existencias_extraccion.id) + """)
		#	or (ubicacion_origen = """ + str(parametros.location_existencias_extraccion.id) + """)
		#	""")

		#for i in self.env.cr.fetchall():
		#	rep = i[0]

		#self.extra_final_ton = rep
		self.extra_final_ton = self.extra_dis_ton - self.extra_tt_ton

	@api.one
	def get_extra_final_imp(self):
		self.verificador()

		#parametros = self.env['main.parameter'].search([])[0]
		#rep = 0


		#fechaini ='01-01-2016'
		#fechaini = str(self.periodo.date_stop).split('-')[0] + '0101'
		#fechafin = str(self.periodo.date_stop).replace('-','')

		#self.env.cr.execute(""" 
		#	select ingreso as ingreso,(round(saldov,2)) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_extraccion.id) + """}',
		#	'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_extraccion.id) + """}') 
		#	where ( ubicacion_destino = """ + str(parametros.location_existencias_extraccion.id) + """)
		#	or ( ubicacion_origen = """ + str(parametros.location_existencias_extraccion.id) + """)
		#	""")
		#for i in self.env.cr.fetchall():
		#	rep = i[1]

		self.extra_final_imp = self.extra_dis_imp - self.extra_tt_imp

	@api.one
	def get_extra_final_cp(self):
		if self.extra_final_ton == 0:
			self.extra_final_cp = 0
		else:
			self.extra_final_cp = self.extra_final_imp / self.extra_final_ton




	@api.one
	def get_extra_ini_ton(self):

		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		code_ant = self.periodo.code.split('/')
		mes = int(code_ant[0])
		anio = int(code_ant[1])

		if mes == 1:
			mes = 12
			anio -= 1
		else:
			mes -= 1

		code_ant = ("%2d"%mes).replace(' ','0') + '/' + str(anio)

		periodo_anterior = self.env['account.period'].search( [('code','=',code_ant)] )




		if mes == 12:

			fechaini = str(self.periodo.date_start).replace('-','')
			fechafin = str(self.periodo.date_stop).replace('-','')

			self.env.cr.execute(""" 
				select ingreso as ingreso,(credit) as credit from (
				select fecha, saldof as ingreso,(credit) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_extraccion.id) + """}',
				'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_extraccion.id) + """}') 
				where ( ubicacion_origen = """ + str(parametros.location_virtual_saldoinicial.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_extraccion.id) + """)
				or ( ubicacion_origen = """ + str(parametros.location_existencias_extraccion.id) + """ and ubicacion_destino = """ + str(parametros.location_virtual_saldoinicial.id) + """)
				) T""")

			for i in self.env.cr.fetchall():
				rep = i[0]

		else:
			if len(periodo_anterior )>0:
				
				fechaini = str(periodo_anterior.date_start).replace('-','')
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = str(periodo_anterior.date_stop).replace('-','')

				self.env.cr.execute(""" 
					select ingreso as ingreso,(credit) as credit from (
					select fecha ,saldof as ingreso,(credit) as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_extraccion.id) + """}',
					'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_extraccion.id) + """}') 
					where (ubicacion_destino = """ + str(parametros.location_existencias_extraccion.id) + """)
					or (ubicacion_origen = """ + str(parametros.location_existencias_extraccion.id) + """)
					) T """)

				for i in self.env.cr.fetchall():
					rep = i[0]

		self.extra_ini_ton = rep



		#if self.extra_tt_ton + self.extra_final_ton - self.extra_pro_ton >=0.05:
		#	self.extra_ini_ton = self.extra_tt_ton + self.extra_final_ton - self.extra_pro_ton
		#else:
		#	self.extra_ini_ton = 0

	@api.one
	def get_extra_ini_imp(self):

		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		code_ant = self.periodo.code.split('/')
		mes = int(code_ant[0])
		anio = int(code_ant[1])

		if mes == 1:
			mes = 12
			anio -= 1
		else:
			mes -= 1

		code_ant = ("%2d"%mes).replace(' ','0') + '/' + str(anio)

		periodo_anterior = self.env['account.period'].search( [('code','=',code_ant)] )



		if mes == 12:

			fechaini = str(self.periodo.date_start).replace('-','')
			fechafin = str(self.periodo.date_stop).replace('-','')

			self.env.cr.execute(""" 
				select ingreso as ingreso,(credit) as credit from (
				select fecha, saldov as ingreso,(credit) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_extraccion.id) + """}',
				'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_extraccion.id) + """}') 
				where ( ubicacion_origen = """ + str(parametros.location_virtual_saldoinicial.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_extraccion.id) + """)
				or ( ubicacion_origen = """ + str(parametros.location_existencias_extraccion.id) + """ and ubicacion_destino = """ + str(parametros.location_virtual_saldoinicial.id) + """)
				) T""")

			for i in self.env.cr.fetchall():
				rep = i[0]

		else:
			if len(periodo_anterior )>0:
				
				fechaini = str(periodo_anterior.date_start).replace('-','')
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = str(periodo_anterior.date_stop).replace('-','')


				self.env.cr.execute(""" 
					select ingreso as ingreso,(credit) as credit from (
					select fecha, ingreso as ingreso,(saldov) as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_extraccion.id) + """}',
					'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_extraccion.id) + """}') 
					where (ubicacion_destino = """ + str(parametros.location_existencias_extraccion.id) + """)
					or (ubicacion_origen = """ + str(parametros.location_existencias_extraccion.id) + """)
					) T """)
				
				for i in self.env.cr.fetchall():
					rep = i[1]

		self.extra_ini_imp = rep


		#if self.extra_tt_imp + self.extra_final_imp - self.extra_pro_imp >=0.05:
		#	self.extra_ini_imp = self.extra_tt_imp + self.extra_final_imp - self.extra_pro_imp
		#else:
		#	self.extra_ini_imp = 0

	@api.one
	def get_extra_ini_cp(self):
		if self.extra_ini_ton == 0:
			self.extra_ini_cp = 0
		else:
			self.extra_ini_cp = self.extra_ini_imp / self.extra_ini_ton
		

	@api.one
	def get_extra_dis_ton(self):
		self.extra_dis_ton = self.extra_ini_ton + self.extra_pro_ton

	@api.one
	def get_extra_dis_imp(self):
		self.extra_dis_imp = self.extra_ini_imp + self.extra_pro_imp

	@api.one
	def get_extra_dis_cp(self):
		if self.extra_dis_ton == 0:
			self.extra_dis_cp = 0
		else:
			self.extra_dis_cp = self.extra_dis_imp / self.extra_dis_ton


	extra_ini_ton = fields.Float('Inventario Inicial',compute="get_extra_ini_ton",digits=(12,2))
	extra_ini_imp = fields.Float('II Importe',compute="get_extra_ini_imp",digits=(12,2))
	extra_ini_cp = fields.Float('II Costo Prom.',compute="get_extra_ini_cp",digits=(12,6))
	
	extra_pro_ton = fields.Float('Producción',compute="get_extra_pro_ton",digits=(12,2))
	extra_pro_imp = fields.Float('II Importe',compute="get_extra_pro_imp",digits=(12,2))
	extra_pro_cp = fields.Float('II Costo Prom.',compute="get_extra_pro_cp",digits=(12,6))

	extra_dis_ton = fields.Float('Disponible',compute="get_extra_dis_ton",digits=(12,2))
	extra_dis_imp = fields.Float('II Importe',compute="get_extra_dis_imp",digits=(12,2))
	extra_dis_cp = fields.Float('II Costo Prom.',compute="get_extra_dis_cp",digits=(12,6))

	extra_tt_ton = fields.Float('Transpaso a Trituración',compute="get_extra_tt_ton",digits=(12,2))
	extra_tt_imp = fields.Float('II Importe',compute="get_extra_tt_imp",digits=(12,2))
	extra_tt_cp = fields.Float('II Costo Prom.',compute="get_extra_tt_cp",digits=(12,6))

	extra_final_ton = fields.Float('Inventario Final',compute="get_extra_final_ton",digits=(12,2))
	extra_final_imp = fields.Float('II Importe',compute="get_extra_final_imp",digits=(12,2))
	extra_final_cp = fields.Float('II Costo Prom.',compute="get_extra_final_cp",digits=(12,6))



	# esto es apartir de aki----------------------------------------


	@api.one
	def get_tritu_pro_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_trituracion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[0]

		self.tritu_pro_ton = rep


	@api.one
	def get_tritu_pro_imp(self):
		"""
		t = self.env['costos.produccion.lineas'].search([('centro_costo','=','922: Total Trituración'),('costos_id','=',self.id)])
		if t and t[0]:
			t = t[0]
			self.tritu_pro_imp=t.monto + self.extra_tt_imp
		else:
			self.tritu_pro_imp= 0 + self.extra_tt_imp"""


		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, debit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_trituracion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[1]
			
		self.tritu_pro_imp = rep

	@api.one
	def get_tritu_pro_cp(self):
		if self.tritu_pro_ton == 0:
			self.tritu_pro_cp = 0
		else:
			self.tritu_pro_cp = self.tritu_pro_imp / self.tritu_pro_ton


	@api.one
	def get_tritu_tt_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, salida as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_trituracion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[0]

		self.tritu_tt_ton = rep

	@api.one
	def get_tritu_tt_imp(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_trituracion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[1]

		self.tritu_tt_imp = rep

	@api.one
	def get_tritu_tt_cp(self):
		if self.tritu_tt_ton == 0:
			self.tritu_tt_cp = 0
		else:
			self.tritu_tt_cp = self.tritu_tt_imp / self.tritu_tt_ton


	@api.one
	def get_tritu_final_ton(self):
		self.verificador()
		#parametros = self.env['main.parameter'].search([])[0]
		#rep = 0


		#fechaini = '01-01-2016'
		#fechaini = str(self.periodo.date_stop).split('-')[0] + '0101'
		#fechafin = str(self.periodo.date_stop).replace('-','')

		#self.env.cr.execute(""" 
		#	select saldof as ingreso,(round(credit,2)) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
		#	'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_trituracion.id) + """}') 
		#	where (ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
		#	or ( ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """)
		#	""")

		#for i in self.env.cr.fetchall():
		#	rep = i[0]

		#self.tritu_final_ton = rep

		self.tritu_final_ton = self.tritu_dis_ton - self.tritu_tt_ton - self.tritu_ven_ton

	@api.one
	def get_tritu_final_imp(self):
		self.verificador()
		#parametros = self.env['main.parameter'].search([])[0]
		#rep = 0


		#fechaini = '01-01-2016'
		#fechaini = str(self.periodo.date_stop).split('-')[0] + '0101'
		#fechafin = str(self.periodo.date_stop).replace('-','')

		#self.env.cr.execute(""" 
		#	select ingreso as ingreso,(round(saldov,2)) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
		#	'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_trituracion.id) + """}') 
		#	where ( ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
		#	or ( ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """)
		#	""")

		#for i in self.env.cr.fetchall():
		#	rep = i[1]

		self.tritu_final_imp = self.tritu_dis_imp - self.tritu_tt_imp - self.tritu_ven_imp

	@api.one
	def get_tritu_final_cp(self):
		if self.tritu_final_ton == 0:
			self.tritu_final_cp = 0
		else:
			self.tritu_final_cp = self.tritu_final_imp / self.tritu_final_ton




	@api.one
	def get_tritu_ini_ton(self):

		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		code_ant = self.periodo.code.split('/')
		mes = int(code_ant[0])
		anio = int(code_ant[1])

		if mes == 1:
			mes = 12
			anio -= 1
		else:
			mes -= 1

		code_ant = ("%2d"%mes).replace(' ','0') + '/' + str(anio)

		periodo_anterior = self.env['account.period'].search( [('code','=',code_ant)] )




		if mes == 12:

			fechaini = str(self.periodo.date_start).replace('-','')
			fechafin = str(self.periodo.date_stop).replace('-','')

			self.env.cr.execute(""" 
				select ingreso as ingreso,(credit) as credit from (
				select fecha, saldof as ingreso,(credit) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
				'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_trituracion.id) + """}') 
				where ( ubicacion_origen = """ + str(parametros.location_virtual_saldoinicial.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
				or ( ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """ and ubicacion_destino = """ + str(parametros.location_virtual_saldoinicial.id) + """)
				) T""")

			for i in self.env.cr.fetchall():
				rep = i[0]

		else:
			if len(periodo_anterior )>0:
				
				fechaini = str(periodo_anterior.date_start).replace('-','')
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = str(periodo_anterior.date_stop).replace('-','')

				self.env.cr.execute(""" 
					select ingreso as ingreso,(credit) as credit from (
					select fecha, saldof as ingreso,(credit) as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
					'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_trituracion.id) + """}') 
					where ( ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
					or ( ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """)
					) T """)

				for i in self.env.cr.fetchall():
					rep = i[0]

		self.tritu_ini_ton = rep

		#if self.tritu_tt_ton + self.tritu_final_ton - self.tritu_pro_ton >=0.05:
		#	self.tritu_ini_ton = self.tritu_tt_ton + self.tritu_final_ton - self.tritu_pro_ton
		#else:
		#	self.tritu_ini_ton = 0

	@api.one
	def get_tritu_ini_imp(self):


		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		code_ant = self.periodo.code.split('/')
		mes = int(code_ant[0])
		anio = int(code_ant[1])

		if mes == 1:
			mes = 12
			anio -= 1
		else:
			mes -= 1

		code_ant = ("%2d"%mes).replace(' ','0') + '/' + str(anio)

		periodo_anterior = self.env['account.period'].search( [('code','=',code_ant)] )



		if mes == 12:

			fechaini = str(self.periodo.date_start).replace('-','')
			fechafin = str(self.periodo.date_stop).replace('-','')

			self.env.cr.execute(""" 
				select ingreso as ingreso,(credit) as credit from (
				select fecha, saldov as ingreso,(credit) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
				'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_trituracion.id) + """}') 
				where ( ubicacion_origen = """ + str(parametros.location_virtual_saldoinicial.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
				or ( ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """ and ubicacion_destino = """ + str(parametros.location_virtual_saldoinicial.id) + """)
				) T""")

			for i in self.env.cr.fetchall():
				rep = i[0]

		else:
			if len(periodo_anterior )>0:
				
				fechaini = str(periodo_anterior.date_start).replace('-','')
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = str(periodo_anterior.date_stop).replace('-','')

				self.env.cr.execute(""" 
					select ingreso as ingreso,(credit) as credit from (
					select fecha, saldov as ingreso,(credit) as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
					'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_trituracion.id) + """}') 
					where ( ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
					or ( ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """)
					) T """)

				for i in self.env.cr.fetchall():
					rep = i[0]

		self.tritu_ini_imp = rep

		#if self.tritu_tt_imp + self.tritu_final_imp - self.tritu_pro_imp >=0.05:
		#	self.tritu_ini_imp = self.tritu_tt_imp + self.tritu_final_imp - self.tritu_pro_imp
		#else:
		#	self.tritu_ini_imp = 0

	@api.one
	def get_tritu_ini_cp(self):
		if self.tritu_ini_ton == 0:
			self.tritu_ini_cp = 0
		else:
			self.tritu_ini_cp = self.tritu_ini_imp / self.tritu_ini_ton
		

	@api.one
	def get_tritu_dis_ton(self):
		self.tritu_dis_ton = self.tritu_ini_ton + self.tritu_pro_ton

	@api.one
	def get_tritu_dis_imp(self):
		self.tritu_dis_imp = self.tritu_ini_imp + self.tritu_pro_imp

	@api.one
	def get_tritu_dis_cp(self):
		if self.tritu_dis_ton == 0:
			self.tritu_dis_cp = 0
		else:
			self.tritu_dis_cp = self.tritu_dis_imp / self.tritu_dis_ton




	@api.one
	def get_tritu_ven_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		var_txt_con = """ 
		select (ingreso) as ingreso,(credit) as credit,ubicacion_destino ,ubicacion_origen from (
			select fecha,(salida - ingreso) as ingreso,(credit) as credit,ubicacion_destino ,ubicacion_origen from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','customer')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1


		self.env.cr.execute( var_txt_con +','+ str(parametros.location_existencias_trituracion.id)+"""}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','customer')]):
				if i[2] == ii.id or i[3] == ii.id :
					rep += i[0]

		self.tritu_ven_ton = rep

	@api.one
	def get_tritu_ven_imp(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		var_txt_con = """ 
		select (ingreso) as ingreso,(credit) as credit,ubicacion_destino ,ubicacion_origen from (
			select fecha,(salida - ingreso) as ingreso,(credit-debit) as credit,ubicacion_destino ,ubicacion_origen from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_trituracion.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','customer')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+str(parametros.location_existencias_trituracion.id) + """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_trituracion.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_trituracion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)


		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','customer')]):
				if i[2] == ii.id or i[3] == ii.id :
					rep += i[1]

		self.tritu_ven_imp = rep

	@api.one
	def get_tritu_ven_cp(self):
		if self.tritu_ven_ton == 0:
			self.tritu_ven_cp = 0
		else:
			self.tritu_ven_cp = self.tritu_ven_imp / self.tritu_ven_ton



	tritu_ini_ton = fields.Float('Inventario Inicial',compute="get_tritu_ini_ton",digits=(12,2))
	tritu_ini_imp = fields.Float('II Importe',compute="get_tritu_ini_imp",digits=(12,2))
	tritu_ini_cp = fields.Float('II Costo Prom.',compute="get_tritu_ini_cp",digits=(12,6))
	
	tritu_pro_ton = fields.Float('Producción',compute="get_tritu_pro_ton",digits=(12,2))
	tritu_pro_imp = fields.Float('II Importe',compute="get_tritu_pro_imp",digits=(12,2))
	tritu_pro_cp = fields.Float('II Costo Prom.',compute="get_tritu_pro_cp",digits=(12,6))

	tritu_dis_ton = fields.Float('Disponible',compute="get_tritu_dis_ton",digits=(12,2))
	tritu_dis_imp = fields.Float('II Importe',compute="get_tritu_dis_imp",digits=(12,2))
	tritu_dis_cp = fields.Float('II Costo Prom.',compute="get_tritu_dis_cp",digits=(12,6))

	tritu_tt_ton = fields.Float('Transpaso a HM',compute="get_tritu_tt_ton",digits=(12,2))
	tritu_tt_imp = fields.Float('II Importe',compute="get_tritu_tt_imp",digits=(12,2))
	tritu_tt_cp = fields.Float('II Costo Prom.',compute="get_tritu_tt_cp",digits=(12,6))

	tritu_ven_ton = fields.Float('Ventas',compute="get_tritu_ven_ton",digits=(12,2))
	tritu_ven_imp = fields.Float('II Importe',compute="get_tritu_ven_imp",digits=(12,2))
	tritu_ven_cp = fields.Float('II Costo Prom.',compute="get_tritu_ven_cp",digits=(12,6))

	tritu_final_ton = fields.Float('Inventario Final',compute="get_tritu_final_ton",digits=(12,2))
	tritu_final_imp = fields.Float('II Importe',compute="get_tritu_final_imp",digits=(12,2))
	tritu_final_cp = fields.Float('II Costo Prom.',compute="get_tritu_final_cp",digits=(12,6))



	# esto es apartir de aki----------------------------------------


	@api.one
	def get_piedra_pro_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_intermedia.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[0]

		self.piedra_pro_ton = rep


	@api.one
	def get_piedra_pro_imp(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, debit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_intermedia.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[1]

		self.piedra_pro_imp = rep

	@api.one
	def get_piedra_pro_cp(self):
		if self.piedra_pro_ton == 0:
			self.piedra_pro_cp= 0
		else:
			self.piedra_pro_cp = self.piedra_pro_imp / self.piedra_pro_ton
		


	@api.one
	def get_piedra_tt_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4]  + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, salida as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_intermedia.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[0]

		self.piedra_tt_ton = rep

	@api.one
	def get_piedra_tt_imp(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_intermedia.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[1]

		self.piedra_tt_imp = rep

	@api.one
	def get_piedra_tt_cp(self):
		if self.piedra_tt_ton == 0:
			self.piedra_tt_cp = 0
		else:
			self.piedra_tt_cp = self.piedra_tt_imp / self.piedra_tt_ton


	@api.one
	def get_piedra_final_ton(self):
		self.verificador()
		#parametros = self.env['main.parameter'].search([])[0]
		#rep = 0


		#fechaini = '01-01-2016'
		#fechaini = str(self.periodo.date_stop).split('-')[0] + '0101'
		#fechafin = str(self.periodo.date_stop).replace('-','')

		#self.env.cr.execute(""" 
		#	select saldof as ingreso,(round(credit,2)) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
		#	'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_intermedia.id) + """}') 
		#	where (ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
		#	or ( ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """)
		#	""")

		#for i in self.env.cr.fetchall():
		#	rep = i[0]

		#self.piedra_final_ton = rep

		self.piedra_final_ton = self.piedra_dis_ton - self.piedra_tt_ton - self.piedra_ven_ton

	@api.one
	def get_piedra_final_imp(self):
		self.verificador()
		#parametros = self.env['main.parameter'].search([])[0]
		#rep = 0


		#fechaini = '01-01-2016'
		#fechaini = str(self.periodo.date_stop).split('-')[0] + '0101'
		#fechafin = str(self.periodo.date_stop).replace('-','')

		#self.env.cr.execute(""" 
		#	select ingreso as ingreso,(round(saldov,2)) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
		#	'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_intermedia.id) + """}') 
		#	where ( ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
		#	or (ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """)
		#	""")

		#for i in self.env.cr.fetchall():
		#	rep = i[1]

		#self.piedra_final_imp = rep

		self.piedra_final_imp = self.piedra_dis_imp - self.piedra_tt_imp - self.piedra_ven_imp

	@api.one
	def get_piedra_final_cp(self):
		if self.piedra_final_ton == 0:
			self.piedra_final_cp = 0
		else:
			self.piedra_final_cp = self.piedra_final_imp / self.piedra_final_ton




	@api.one
	def get_piedra_ini_ton(self):
		
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		code_ant = self.periodo.code.split('/')
		mes = int(code_ant[0])
		anio = int(code_ant[1])

		if mes == 1:
			mes = 12
			anio -= 1
		else:
			mes -= 1

		code_ant = ("%2d"%mes).replace(' ','0') + '/' + str(anio)

		periodo_anterior = self.env['account.period'].search( [('code','=',code_ant)] )



		if mes == 12:

			fechaini = str(self.periodo.date_start).replace('-','')
			fechafin = str(self.periodo.date_stop).replace('-','')

			self.env.cr.execute(""" 
				select ingreso as ingreso,(credit) as credit from (
				select fecha, saldof as ingreso,(credit) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
				'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_intermedia.id) + """}') 
				where ( ubicacion_origen = """ + str(parametros.location_virtual_saldoinicial.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
				or ( ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """ and ubicacion_destino = """ + str(parametros.location_virtual_saldoinicial.id) + """)
				) T""")

			for i in self.env.cr.fetchall():
				rep = i[0]

		else:
			if len(periodo_anterior )>0:
				
				fechaini = str(periodo_anterior.date_start).replace('-','')
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = str(periodo_anterior.date_stop).replace('-','')

				self.env.cr.execute(""" 
					select ingreso as ingreso,(credit) as credit from (
					select fecha, saldof as ingreso,(credit) as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
					'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_intermedia.id) + """}') 
					where (ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
					or (ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """)
					) T """)

				for i in self.env.cr.fetchall():
					rep = i[0]

		self.piedra_ini_ton = rep

	@api.one
	def get_piedra_ini_imp(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		code_ant = self.periodo.code.split('/')
		mes = int(code_ant[0])
		anio = int(code_ant[1])

		if mes == 1:
			mes = 12
			anio -= 1
		else:
			mes -= 1

		code_ant = ("%2d"%mes).replace(' ','0') + '/' + str(anio)

		periodo_anterior = self.env['account.period'].search( [('code','=',code_ant)] )



		if mes == 12:

			fechaini = str(self.periodo.date_start).replace('-','')
			fechafin = str(self.periodo.date_stop).replace('-','')

			self.env.cr.execute(""" 
				select ingreso as ingreso,(credit) as credit from (
				select fecha, saldov as ingreso,(credit) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
				'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_intermedia.id) + """}') 
				where ( ubicacion_origen = """ + str(parametros.location_virtual_saldoinicial.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
				or ( ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """ and ubicacion_destino = """ + str(parametros.location_virtual_saldoinicial.id) + """)
				) T""")

			for i in self.env.cr.fetchall():
				rep = i[0]

		else:
			if len(periodo_anterior )>0:
				
				fechaini = str(periodo_anterior.date_start).replace('-','')
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = str(periodo_anterior.date_stop).replace('-','')

				self.env.cr.execute(""" 
					select ingreso as ingreso,(credit) as credit from (
					select fecha, saldov as ingreso,(credit) as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
					'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_intermedia.id) + """}') 
					where (ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
					or ( ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """)
					) T """)

				for i in self.env.cr.fetchall():
					rep = i[0]

		self.piedra_ini_imp = rep

	@api.one
	def get_piedra_ini_cp(self):
		if self.piedra_ini_ton == 0:
			self.piedra_ini_cp = 0
		else:
			self.piedra_ini_cp = self.piedra_ini_imp / self.piedra_ini_ton
		

	@api.one
	def get_piedra_dis_ton(self):
		self.piedra_dis_ton = self.piedra_ini_ton + self.piedra_pro_ton

	@api.one
	def get_piedra_dis_imp(self):
		self.piedra_dis_imp = self.piedra_ini_imp + self.piedra_pro_imp

	@api.one
	def get_piedra_dis_cp(self):
		if self.piedra_dis_ton == 0:
			self.piedra_dis_cp = 0
		else:
			self.piedra_dis_cp = self.piedra_dis_imp / self.piedra_dis_ton




	@api.one
	def get_piedra_ven_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		var_txt_con = """ 
		select (ingreso) as ingreso,(credit) as credit, ubicacion_destino, ubicacion_origen from (
			select fecha, (salida-ingreso) as ingreso,(credit) as credit, ubicacion_destino, ubicacion_origen from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','customer')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+ str(parametros.location_existencias_intermedia.id)+ """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','customer')]):
				if i[2] == ii.id or i[3] == ii.id :
					rep += i[0]

		self.piedra_ven_ton = rep

	@api.one
	def get_piedra_ven_imp(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		var_txt_con = """ 
		select (ingreso) as ingreso,(credit) as credit, ubicacion_destino, ubicacion_origen from (
			select fecha, (salida - ingreso) as ingreso,(credit-debit) as credit, ubicacion_destino, ubicacion_origen from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_intermedia.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','customer')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+str(parametros.location_existencias_intermedia.id)+ """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_intermedia.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_intermedia.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)


		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','customer')]):
				if i[2] == ii.id or i[3] == ii.id :
					rep += i[1]

		self.piedra_ven_imp = rep

	@api.one
	def get_piedra_ven_cp(self):
		if self.piedra_ven_ton == 0:
			self.piedra_ven_cp = 0
		else:
			self.piedra_ven_cp = self.piedra_ven_imp / self.piedra_ven_ton




	piedra_ini_ton = fields.Float('Inventario Inicial',compute="get_piedra_ini_ton",digits=(12,2))
	piedra_ini_imp = fields.Float('II Importe',compute="get_piedra_ini_imp",digits=(12,2))
	piedra_ini_cp = fields.Float('II Costo Prom.',compute="get_piedra_ini_cp",digits=(12,6))
	
	piedra_pro_ton = fields.Float('Producción',compute="get_piedra_pro_ton",digits=(12,2))
	piedra_pro_imp = fields.Float('II Importe',compute="get_piedra_pro_imp",digits=(12,2))
	piedra_pro_cp = fields.Float('II Costo Prom.',compute="get_piedra_pro_cp",digits=(12,6))

	piedra_dis_ton = fields.Float('Disponible',compute="get_piedra_dis_ton",digits=(12,2))
	piedra_dis_imp = fields.Float('II Importe',compute="get_piedra_dis_imp",digits=(12,2))
	piedra_dis_cp = fields.Float('II Costo Prom.',compute="get_piedra_dis_cp",digits=(12,6))

	piedra_tt_ton = fields.Float('Transpaso a Trituración',compute="get_piedra_tt_ton",digits=(12,2))
	piedra_tt_imp = fields.Float('II Importe',compute="get_piedra_tt_imp",digits=(12,2))
	piedra_tt_cp = fields.Float('II Costo Prom.',compute="get_piedra_tt_cp",digits=(12,6))

	piedra_ven_ton = fields.Float('Ventas',compute="get_piedra_ven_ton",digits=(12,2))
	piedra_ven_imp = fields.Float('II Importe',compute="get_piedra_ven_imp",digits=(12,2))
	piedra_ven_cp = fields.Float('II Costo Prom.',compute="get_piedra_ven_cp",digits=(12,6))

	piedra_final_ton = fields.Float('Inventario Final',compute="get_piedra_final_ton",digits=(12,2))
	piedra_final_imp = fields.Float('II Importe',compute="get_piedra_final_imp",digits=(12,2))
	piedra_final_cp = fields.Float('II Costo Prom.',compute="get_piedra_final_cp",digits=(12,6))
	




	# esto es apartir de aki----------------------------------------


	@api.one
	def get_calci_pro_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_calcinacion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[0]

		self.calci_pro_ton = rep


	@api.one
	def get_calci_pro_imp(self):
		"""
		t = self.env['costos.produccion.lineas'].search([('centro_costo','=','923: Total Calcinación'),('costos_id','=',self.id)])
		if t and t[0]:
			t = t[0]
			self.calci_pro_imp=t.monto + self.piedra_tt_imp
		else:
			self.calci_pro_imp= 0 + self.piedra_tt_imp"""

		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, debit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_calcinacion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[1]

		self.calci_pro_imp = rep

	@api.one
	def get_calci_pro_cp(self):
		if self.calci_pro_ton == 0:
			self.calci_pro_cp = 0
		else:
			self.calci_pro_cp = self.calci_pro_imp / self.calci_pro_ton


	@api.one
	def get_calci_tt_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, salida as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_calcinacion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[0]

		self.calci_tt_ton = rep

	@api.one
	def get_calci_tt_imp(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_calcinacion.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[1]

		self.calci_tt_imp = rep

	@api.one
	def get_calci_tt_cp(self):
		if self.calci_tt_ton == 0:
			self.calci_tt_cp = 0
		else:
			self.calci_tt_cp = self.calci_tt_imp / self.calci_tt_ton


	@api.one
	def get_calci_final_ton(self):
		self.verificador()
		#parametros = self.env['main.parameter'].search([])[0]
		#rep = 0


		#fechaini = '01-01-2016'
		#fechaini = str(self.periodo.date_stop).split('-')[0] + '0101'
		#fechafin = str(self.periodo.date_stop).replace('-','')

		#self.env.cr.execute(""" 
		#	select saldof as ingreso,(round(credit,2)) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
		#	'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_calcinacion.id) + """}') 
		#	where (ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
		#	or (ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """)
		#	""")

		#for i in self.env.cr.fetchall():
		#	rep = i[0]

		#self.calci_final_ton = rep

		self.calci_final_ton = self.calci_dis_ton - self.calci_tt_ton - self.calci_ven_ton

	@api.one
	def get_calci_final_imp(self):
		self.verificador()
		#parametros = self.env['main.parameter'].search([])[0]
		#rep = 0


		#fechaini = '01-01-2016'
		#fechaini = str(self.periodo.date_stop).split('-')[0] + '0101'
		#fechafin = str(self.periodo.date_stop).replace('-','')

		#self.env.cr.execute(""" 
		#	select ingreso as ingreso,(round(saldov,2)) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
		#	'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_calcinacion.id) + """}') 
		#	where ( ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
		#	or ( ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """)
		#	""")

		#for i in self.env.cr.fetchall():
		#	rep = i[1]

		#self.calci_final_imp = rep

		self.calci_final_imp = self.calci_dis_imp - self.calci_tt_imp - self.calci_ven_imp

	@api.one
	def get_calci_final_cp(self):
		if self.calci_final_ton == 0:
			self.calci_final_cp = 0
		else:
			self.calci_final_cp = self.calci_final_imp / self.calci_final_ton




	@api.one
	def get_calci_ini_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		code_ant = self.periodo.code.split('/')
		mes = int(code_ant[0])
		anio = int(code_ant[1])

		if mes == 1:
			mes = 12
			anio -= 1
		else:
			mes -= 1

		code_ant = ("%2d"%mes).replace(' ','0') + '/' + str(anio)

		periodo_anterior = self.env['account.period'].search( [('code','=',code_ant)] )

		if mes == 12:

			fechaini = str(self.periodo.date_start).replace('-','')
			fechafin = str(self.periodo.date_stop).replace('-','')

			self.env.cr.execute(""" 
				select ingreso as ingreso,(credit) as credit from (
				select fecha, saldof as ingreso,(credit) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
				'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_calcinacion.id) + """}') 
				where ( ubicacion_origen = """ + str(parametros.location_virtual_saldoinicial.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
				or ( ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """ and ubicacion_destino = """ + str(parametros.location_virtual_saldoinicial.id) + """)
				) T""")

			for i in self.env.cr.fetchall():
				rep = i[0]

		else:
			if len(periodo_anterior )>0:
				
				fechaini = str(periodo_anterior.date_start).replace('-','')
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = str(periodo_anterior.date_stop).replace('-','')

				self.env.cr.execute(""" 
					select ingreso as ingreso,(credit) as credit from (
					select fecha, saldof as ingreso,(credit) as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
					'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_calcinacion.id) + """}') 
					where ( ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
					or ( ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """)
					) T""")

				for i in self.env.cr.fetchall():
					rep = i[0]

		self.calci_ini_ton = rep

	@api.one
	def get_calci_ini_imp(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		code_ant = self.periodo.code.split('/')
		mes = int(code_ant[0])
		anio = int(code_ant[1])

		if mes == 1:
			mes = 12
			anio -= 1
		else:
			mes -= 1

		code_ant = ("%2d"%mes).replace(' ','0') + '/' + str(anio)

		periodo_anterior = self.env['account.period'].search( [('code','=',code_ant)] )



		if mes == 12:

			fechaini = str(self.periodo.date_start).replace('-','')
			fechafin = str(self.periodo.date_stop).replace('-','')

			self.env.cr.execute(""" 
				select ingreso as ingreso,(credit) as credit from (
				select fecha, saldov as ingreso,(credit) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
				'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_calcinacion.id) + """}') 
				where ( ubicacion_origen = """ + str(parametros.location_virtual_saldoinicial.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
				or ( ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """ and ubicacion_destino = """ + str(parametros.location_virtual_saldoinicial.id) + """)
				) T""")

			for i in self.env.cr.fetchall():
				rep = i[0]

		else:
			if len(periodo_anterior )>0:
				
				fechaini = str(periodo_anterior.date_start).replace('-','')
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = str(periodo_anterior.date_stop).replace('-','')

				self.env.cr.execute(""" 
					select ingreso as ingreso,(credit) as credit from (
					select fecha, saldov as ingreso,(credit) as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
					'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_calcinacion.id) + """}') 
					where (ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
					or (ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """)
					) T """)

				for i in self.env.cr.fetchall():
					rep = i[0]

		self.calci_ini_imp = rep

	@api.one
	def get_calci_ini_cp(self):
		if self.calci_ini_ton == 0:
			self.calci_ini_cp = 0
		else:
			self.calci_ini_cp = self.calci_ini_imp / self.calci_ini_ton
		

	@api.one
	def get_calci_dis_ton(self):
		self.calci_dis_ton = self.calci_ini_ton + self.calci_pro_ton

	@api.one
	def get_calci_dis_imp(self):
		self.calci_dis_imp = self.calci_ini_imp + self.calci_pro_imp

	@api.one
	def get_calci_dis_cp(self):
		if self.calci_dis_ton == 0:
			self.calci_dis_cp = 0
		else:
			self.calci_dis_cp = self.calci_dis_imp / self.calci_dis_ton




	@api.one
	def get_calci_ven_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		var_txt_con = """ 
		select (ingreso) as ingreso,(credit) as credit, ubicacion_destino, ubicacion_origen from (
			select fecha, (salida - ingreso) as ingreso,(credit) as credit, ubicacion_destino, ubicacion_origen from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','customer')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+str(parametros.location_existencias_calcinacion.id)+ """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','customer')]):
				if (i[2] == ii.id and i[3] == parametros.location_existencias_calcinacion.id ) or ( i[2] == parametros.location_existencias_calcinacion.id and i[3] == ii.id  ):
					rep += i[0]

		self.calci_ven_ton = rep

	@api.one
	def get_calci_ven_imp(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		var_txt_con = """ 
		select (ingreso) as ingreso,(credit) as credit, ubicacion_destino, ubicacion_origen from (
			select fecha, (salida - ingreso) as ingreso,(credit-debit) as credit, ubicacion_destino, ubicacion_origen from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_calcinacion.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','customer')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+str(parametros.location_existencias_calcinacion.id)+ """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_calcinacion.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_calcinacion.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)


		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','customer')]):
				if i[2] == ii.id  or i[3] == ii.id  :
					rep += i[1]


		self.calci_ven_imp = rep

	@api.one
	def get_calci_ven_cp(self):
		if self.calci_ven_ton == 0:
			self.calci_ven_cp = 0
		else:
			self.calci_ven_cp = self.calci_ven_imp / self.calci_ven_ton



	calci_ini_ton = fields.Float('Inventario Inicial',compute="get_calci_ini_ton",digits=(12,2))
	calci_ini_imp = fields.Float('II Importe',compute="get_calci_ini_imp",digits=(12,2))
	calci_ini_cp = fields.Float('II Costo Prom.',compute="get_calci_ini_cp",digits=(12,6))
	
	calci_pro_ton = fields.Float('Producción',compute="get_calci_pro_ton",digits=(12,2))
	calci_pro_imp = fields.Float('II Importe',compute="get_calci_pro_imp",digits=(12,2))
	calci_pro_cp = fields.Float('II Costo Prom.',compute="get_calci_pro_cp",digits=(12,6))

	calci_dis_ton = fields.Float('Disponible',compute="get_calci_dis_ton",digits=(12,2))
	calci_dis_imp = fields.Float('II Importe',compute="get_calci_dis_imp",digits=(12,2))
	calci_dis_cp = fields.Float('II Costo Prom.',compute="get_calci_dis_cp",digits=(12,6))

	calci_tt_ton = fields.Float('Transpaso a Trituración',compute="get_calci_tt_ton",digits=(12,2))
	calci_tt_imp = fields.Float('II Importe',compute="get_calci_tt_imp",digits=(12,2))
	calci_tt_cp = fields.Float('II Costo Prom.',compute="get_calci_tt_cp",digits=(12,6))

	calci_ven_ton = fields.Float('Ventas',compute="get_calci_ven_ton",digits=(12,2))
	calci_ven_imp = fields.Float('II Importe',compute="get_calci_ven_imp",digits=(12,2))
	calci_ven_cp = fields.Float('II Costo Prom.',compute="get_calci_ven_cp",digits=(12,6))

	calci_final_ton = fields.Float('Inventario Final',compute="get_calci_final_ton",digits=(12,2))
	calci_final_imp = fields.Float('II Importe',compute="get_calci_final_imp",digits=(12,2))
	calci_final_cp = fields.Float('II Costo Prom.',compute="get_calci_final_cp",digits=(12,6))
	



	# esto es apartir de aki----------------------------------------


	@api.one
	def get_micro_pro_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, credit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_micronizado.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_micronizado.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_micronizado.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_micronizado.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[0]

		self.micro_pro_ton = rep


	@api.one
	def get_micro_pro_imp(self):
		"""
		t = self.env['costos.produccion.lineas'].search([('centro_costo','=','924: Total Micronizado'),('costos_id','=',self.id)])
		if t and t[0]:
			t = t[0]
			self.micro_pro_imp=t.monto + self.calci_tt_imp
		else:
			self.micro_pro_imp= 0 + self.calci_tt_imp"""

		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		self.env.cr.execute(""" 
			select sum(ingreso) as ingreso,sum(credit) as credit from (
			select fecha, ingreso as ingreso, debit as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_micronizado.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_micronizado.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_micronizado.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_micronizado.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			rep = i[1]
			
		self.micro_pro_imp = rep


		
	@api.one
	def get_micro_pro_cp(self):
		if self.micro_pro_ton == 0:
			self.micro_pro_cp = 0
		else:
			self.micro_pro_cp = self.micro_pro_imp / self.micro_pro_ton


	@api.one
	def get_micro_final_ton(self):
		self.verificador()
		#parametros = self.env['main.parameter'].search([])[0]
		#rep = 0


		#fechaini = '01-01-2016'
		#fechaini = str(self.periodo.date_stop).split('-')[0] + '0101'
		#fechafin = str(self.periodo.date_stop).replace('-','')

		#self.env.cr.execute(""" 
		#	select saldof as ingreso,(round(credit,2)) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_micronizado.id) + """}',
		#	'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_micronizado.id) + """}') 
		#	where ( ubicacion_destino = """ + str(parametros.location_existencias_micronizado.id) + """)
		#	or ( ubicacion_origen = """ + str(parametros.location_existencias_micronizado.id) + """)
		#	""")

		#for i in self.env.cr.fetchall():
		#	rep = i[0]

		#self.micro_final_ton = rep

		self.micro_final_ton = self.micro_dis_ton -  self.micro_ven_ton
	@api.one
	def get_micro_final_imp(self):
		self.verificador()
		#parametros = self.env['main.parameter'].search([])[0]
		#rep = 0


		#fechaini = '01-01-2016'
		#fechaini = str(self.periodo.date_stop).split('-')[0] + '0101'
		#fechafin = str(self.periodo.date_stop).replace('-','')

		#self.env.cr.execute(""" 
		#	select ingreso as ingreso,(round(saldov,2)) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_micronizado.id) + """}',
		#	'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_micronizado.id) + """}') 
		#	where ( ubicacion_destino = """ + str(parametros.location_existencias_micronizado.id) + """)
		#	or ( ubicacion_origen = """ + str(parametros.location_existencias_micronizado.id) + """)
		#	""")

		#for i in self.env.cr.fetchall():
		#	rep = i[1]

		#self.micro_final_imp = rep

		self.micro_final_imp = self.micro_dis_imp - self.micro_ven_imp

	@api.one
	def get_micro_final_cp(self):
		if self.micro_final_ton == 0:
			self.micro_final_cp = 0
		else:
			self.micro_final_cp = self.micro_final_imp / self.micro_final_ton




	@api.one
	def get_micro_ini_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		code_ant = self.periodo.code.split('/')
		mes = int(code_ant[0])
		anio = int(code_ant[1])

		if mes == 1:
			mes = 12
			anio -= 1
		else:
			mes -= 1

		code_ant = ("%2d"%mes).replace(' ','0') + '/' + str(anio)

		periodo_anterior = self.env['account.period'].search( [('code','=',code_ant)] )



		if mes == 12:

			fechaini = str(self.periodo.date_start).replace('-','')
			fechafin = str(self.periodo.date_stop).replace('-','')

			self.env.cr.execute(""" 
				select ingreso as ingreso,(credit) as credit from (
				select fecha, saldof as ingreso,(credit) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_micronizado.id) + """}',
				'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_micronizado.id) + """}') 
				where ( ubicacion_origen = """ + str(parametros.location_virtual_saldoinicial.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_micronizado.id) + """)
				or ( ubicacion_origen = """ + str(parametros.location_existencias_micronizado.id) + """ and ubicacion_destino = """ + str(parametros.location_virtual_saldoinicial.id) + """)
				) T""")

			for i in self.env.cr.fetchall():
				rep = i[0]

		else:
			if len(periodo_anterior )>0:
				
				fechaini = str(periodo_anterior.date_start).replace('-','')
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = str(periodo_anterior.date_stop).replace('-','')

				self.env.cr.execute(""" 
					select ingreso as ingreso,(credit) as credit from (
					select fecha, saldof as ingreso,(credit) as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_micronizado.id) + """}',
					'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_micronizado.id) + """}') 
					where ( ubicacion_destino = """ + str(parametros.location_existencias_micronizado.id) + """)
					or ( ubicacion_origen = """ + str(parametros.location_existencias_micronizado.id) + """)
					) T """)

				for i in self.env.cr.fetchall():
					rep = i[0]

		self.micro_ini_ton = rep

	@api.one
	def get_micro_ini_imp(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0

		code_ant = self.periodo.code.split('/')
		mes = int(code_ant[0])
		anio = int(code_ant[1])

		if mes == 1:
			mes = 12
			anio -= 1
		else:
			mes -= 1

		code_ant = ("%2d"%mes).replace(' ','0') + '/' + str(anio)

		periodo_anterior = self.env['account.period'].search( [('code','=',code_ant)] )



		if mes == 12:

			fechaini = str(self.periodo.date_start).replace('-','')
			fechafin = str(self.periodo.date_stop).replace('-','')

			self.env.cr.execute(""" 
				select ingreso as ingreso,(credit) as credit from (
				select fecha, saldov as ingreso,(credit) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_micronizado.id) + """}',
				'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_micronizado.id) + """}') 
				where ( ubicacion_origen = """ + str(parametros.location_virtual_saldoinicial.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_micronizado.id) + """)
				or ( ubicacion_origen = """ + str(parametros.location_existencias_micronizado.id) + """ and ubicacion_destino = """ + str(parametros.location_virtual_saldoinicial.id) + """)
				) T""")

			for i in self.env.cr.fetchall():
				rep = i[0]

		else:
			if len(periodo_anterior )>0:
				
				fechaini = str(periodo_anterior.date_start).replace('-','')
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = str(periodo_anterior.date_stop).replace('-','')

				self.env.cr.execute(""" 
					select ingreso as ingreso,(credit) as credit from (
					select fecha, saldov as ingreso,(credit) as credit from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_micronizado.id) + """}',
					'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_micronizado.id) + """}') 
					where ( ubicacion_destino = """ + str(parametros.location_existencias_micronizado.id) + """)
					or ( ubicacion_origen = """ + str(parametros.location_existencias_micronizado.id) + """)
					) T  """)

				for i in self.env.cr.fetchall():
					rep = i[0]

		self.micro_ini_imp = rep

	@api.one
	def get_micro_ini_cp(self):
		if self.micro_ini_ton == 0:
			self.micro_ini_cp = 0
		else:
			self.micro_ini_cp = self.micro_ini_imp / self.micro_ini_ton
		

	@api.one
	def get_micro_dis_ton(self):
		self.micro_dis_ton = self.micro_ini_ton + self.micro_pro_ton

	@api.one
	def get_micro_dis_imp(self):
		self.micro_dis_imp = self.micro_ini_imp + self.micro_pro_imp

	@api.one
	def get_micro_dis_cp(self):
		if self.micro_dis_ton == 0:
			self.micro_dis_cp = 0
		else:
			self.micro_dis_cp = self.micro_dis_imp / self.micro_dis_ton




	@api.one
	def get_micro_ven_ton(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		var_txt_con = """ 
		select (ingreso) as ingreso,(credit) as credit, ubicacion_destino,ubicacion_origen from (
			select fecha, (salida - ingreso) as ingreso,(credit) as credit, ubicacion_destino,ubicacion_origen from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_micronizado.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','customer')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+str(parametros.location_existencias_micronizado.id)+ """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_micronizado.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_micronizado.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)

		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','customer')]):
				if i[2] == ii.id or i[3] == ii.id :
					rep += i[0]

		self.micro_ven_ton = rep

	@api.one
	def get_micro_ven_imp(self):
		self.verificador()
		parametros = self.env['main.parameter'].search([])[0]
		rep = 0


		fechaini = str(self.periodo.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.periodo.date_stop).replace('-','')

		var_txt_con = """ 
		select (ingreso) as ingreso,(credit) as credit,ubicacion_destino,ubicacion_origen from (
			select fecha, (salida - ingreso) as ingreso,(credit-debit) as credit,ubicacion_destino,ubicacion_origen from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_micronizado.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','customer')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+str(parametros.location_existencias_micronizado.id)+ """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_micronizado.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_micronizado.id) + """)
			) T where fecha >= '"""+str(self.periodo.date_start)+"""' and fecha <= '"""+str(self.periodo.date_stop)+"""' """)


		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','customer')]):
				if i[2] == ii.id or i[3] == ii.id :
					rep += i[1]

		self.micro_ven_imp = rep

	@api.one
	def get_micro_ven_cp(self):
		if self.micro_ven_ton == 0:
			self.micro_ven_cp = 0
		else:
			self.micro_ven_cp = self.micro_ven_imp / self.micro_ven_ton



	micro_ini_ton = fields.Float('Inventario Inicial',compute="get_micro_ini_ton",digits=(12,2))
	micro_ini_imp = fields.Float('II Importe',compute="get_micro_ini_imp",digits=(12,2))
	micro_ini_cp = fields.Float('II Costo Prom.',compute="get_micro_ini_cp",digits=(12,6))
	
	micro_pro_ton = fields.Float('Producción',compute="get_micro_pro_ton",digits=(12,2))
	micro_pro_imp = fields.Float('II Importe',compute="get_micro_pro_imp",digits=(12,2))
	micro_pro_cp = fields.Float('II Costo Prom.',compute="get_micro_pro_cp",digits=(12,6))

	micro_dis_ton = fields.Float('Disponible',compute="get_micro_dis_ton",digits=(12,2))
	micro_dis_imp = fields.Float('II Importe',compute="get_micro_dis_imp",digits=(12,2))
	micro_dis_cp = fields.Float('II Costo Prom.',compute="get_micro_dis_cp",digits=(12,6))

	micro_ven_ton = fields.Float('Ventas',compute="get_micro_ven_ton",digits=(12,2))
	micro_ven_imp = fields.Float('II Importe',compute="get_micro_ven_imp",digits=(12,2))
	micro_ven_cp = fields.Float('II Costo Prom.',compute="get_micro_ven_cp",digits=(12,6))

	micro_final_ton = fields.Float('Inventario Final',compute="get_micro_final_ton",digits=(12,2))
	micro_final_imp = fields.Float('II Importe',compute="get_micro_final_imp",digits=(12,2))
	micro_final_cp = fields.Float('II Costo Prom.',compute="get_micro_final_cp",digits=(12,6))



	@api.multi
	def exportarpdf(self):
		self.reporteador()
		
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		import os

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		vals = {
			'output_name': 'CostoProduccion.pdf',
			'output_file': open(direccion + "costoproduccion.pdf", "rb").read().encode("base64"),	
		}
		sfs_id = self.env['export.file.save'].create(vals)
		result = {}
		view_ref = mod_obj.get_object_reference('account_contable_book_it', 'export_file_save_action')
		view_id = view_ref and view_ref[1] or False
		result = act_obj.read( [view_id] )
		print sfs_id
		return {
			"type": "ir.actions.act_window",
			"res_model": "export.file.save",
			"views": [[False, "form"]],
			"res_id": sfs_id.id,
			"target": "new",
		}



	@api.multi
	def cabezera(self,c,wReal,hReal):

		c.setFont("Calibri-Bold", 14)
		c.setFillColor(black)
		c.drawString(70,hReal, self.env["res.company"].search([])[0].name.upper())

		equivalente = {
			'01':'Enero',
			'02':'Febrero',
			'03':'Marzo',
			'04':'Abril',
			'05':'Mayo',
			'06':'Junio',
			'07':'Julio',
			'08':'Agosto',
			'09':'Septiembre',
			'10':'Octubre',
			'11':'Noviembre',
			'12':'Diciembre',
		}
		c.drawString(70,hReal-16, u"Costo de Producción "+ equivalente[ self.periodo.code.split('/')[0] ] +" "+ self.fiscal.name  )


	@api.multi
	def reporteador(self):

		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')


		pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
		pdfmetrics.registerFont(TTFont('Calibri-Bold', 'CalibriBold.ttf'))

		width ,height  = A4  # 595 , 842
		wReal = width- 30
		hReal = height - 40

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		c = canvas.Canvas( direccion + "costoproduccion.pdf", pagesize= A4 )

		pos_inicial = hReal-28
		pagina = 1
		textPos = 0
		
		self.cabezera(c,wReal,hReal)


		if self.state != 'draft':

			c.setFont("Calibri-Bold", 10)
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)		
			c.drawString( 50 ,pos_inicial, u"EXTRACCION" )

			
			fondo = HexColor('#d1d1d1')
			c.setFillColor(fondo)
			c.rect(60+145 +5,pos_inicial-3,110,11,fill=True,stroke=True)
			c.rect(60+145 +5+110,pos_inicial-3,110,11,fill=True,stroke=True)
			c.rect(60+145 +5+220,pos_inicial-3,110,11,fill=True,stroke=True)
			c.setFillColor(black)

			c.drawCentredString( 60+145 +10 +50 ,pos_inicial, "Toneladas" )
			c.drawCentredString( 60+145 +10 +50 + 110 ,pos_inicial, "Importe" )
			c.drawCentredString( 60+145 +10 +50 + 110 +110 ,pos_inicial, "Costo Promedio" )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,16,pagina)


			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Inventario Inicial")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_ini_ton )) )

			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_ini_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.extra_ini_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Producción")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_pro_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_pro_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.extra_pro_cp )) )

			c.line( 60+145+10 , pos_inicial - 7, 60+145+10+100 , pos_inicial - 7)
			c.line( 60+145+10+110 , pos_inicial - 7, 60+145+10+110 +100 , pos_inicial - 7)

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,15,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Disponible")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_dis_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_dis_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.extra_dis_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Traspaso a Trituración")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_tt_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_tt_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.extra_tt_cp )) )

			c.line( 60+145+10 , pos_inicial - 5, 60+145+10+100 , pos_inicial - 5)
			c.line( 60+145+10+110 , pos_inicial - 5, 60+145+10+110 +100 , pos_inicial - 5)
			c.line( 60+145+10 , pos_inicial - 8, 60+145+10+100 , pos_inicial - 8)
			c.line( 60+145+10+110 , pos_inicial - 8, 60+145+10+110 +100 , pos_inicial - 8)

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,17,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Inventario Final")
			c.setFont("Calibri-Bold", 9)
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_final_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_final_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.extra_final_cp )) )
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,5,pagina)


		if self.state != 'draft' and self.state != 'extraccion':

			c.setFont("Calibri-Bold", 10)
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)		
			c.drawString( 50 ,pos_inicial, u"TRITURACION" )



			
			fondo = HexColor('#d1d1d1')
			c.setFillColor(fondo)
			c.rect(60+145 +5,pos_inicial-3,110,11,fill=True,stroke=True)
			c.rect(60+145 +5+110,pos_inicial-3,110,11,fill=True,stroke=True)
			c.rect(60+145 +5+220,pos_inicial-3,110,11,fill=True,stroke=True)
			c.setFillColor(black)

			c.drawCentredString( 60+145 +10 +50 ,pos_inicial, "Toneladas" )
			c.drawCentredString( 60+145 +10 +50 + 110 ,pos_inicial, "Importe" )
			c.drawCentredString( 60+145 +10 +50 + 110 +110 ,pos_inicial, "Costo Promedio" )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,16,pagina)


			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Inventario Inicial")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.tritu_ini_ton )) )

			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.tritu_ini_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.tritu_ini_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Producción")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.tritu_pro_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.tritu_pro_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.tritu_pro_cp )) )

			c.line( 60+145+10 , pos_inicial - 7, 60+145+10+100 , pos_inicial - 7)
			c.line( 60+145+10+110 , pos_inicial - 7, 60+145+10+110 +100 , pos_inicial - 7)

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,15,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Disponible")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.tritu_dis_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.tritu_dis_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.tritu_dis_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Traspaso a HM")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.tritu_tt_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.tritu_tt_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.tritu_tt_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Ventas")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.tritu_ven_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.tritu_ven_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.tritu_ven_cp )) )

			c.line( 60+145+10 , pos_inicial - 5, 60+145+10+100 , pos_inicial - 5)
			c.line( 60+145+10+110 , pos_inicial - 5, 60+145+10+110 +100 , pos_inicial - 5)
			c.line( 60+145+10 , pos_inicial - 8, 60+145+10+100 , pos_inicial - 8)
			c.line( 60+145+10+110 , pos_inicial - 8, 60+145+10+110 +100 , pos_inicial - 8)

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,17,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Inventario Final")
			c.setFont("Calibri-Bold", 9)
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.tritu_final_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.tritu_final_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.tritu_final_cp )) )
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,5,pagina)


			# MODIFICAR A --------------------------------------------

			c.setFont("Calibri-Bold", 10)
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)		
			c.drawString( 50 ,pos_inicial, u"ALMACEN DE PIEDRA HM" )



			
			fondo = HexColor('#d1d1d1')
			c.setFillColor(fondo)
			c.rect(60+145 +5,pos_inicial-3,110,11,fill=True,stroke=True)
			c.rect(60+145 +5+110,pos_inicial-3,110,11,fill=True,stroke=True)
			c.rect(60+145 +5+220,pos_inicial-3,110,11,fill=True,stroke=True)
			c.setFillColor(black)

			c.drawCentredString( 60+145 +10 +50 ,pos_inicial, "Toneladas" )
			c.drawCentredString( 60+145 +10 +50 + 110 ,pos_inicial, "Importe" )
			c.drawCentredString( 60+145 +10 +50 + 110 +110 ,pos_inicial, "Costo Promedio" )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,16,pagina)


			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Inventario Inicial")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_ini_ton )) )

			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_ini_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.piedra_ini_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Entrada de Piedra de Trituración")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_pro_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_pro_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.piedra_pro_cp )) )

			c.line( 60+145+10 , pos_inicial - 7, 60+145+10+100 , pos_inicial - 7)
			c.line( 60+145+10+110 , pos_inicial - 7, 60+145+10+110 +100 , pos_inicial - 7)

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,15,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Disponible")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_dis_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_dis_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.piedra_dis_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Traspaso a Calcinación")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_tt_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_tt_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.piedra_tt_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Ventas")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_ven_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_ven_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.piedra_ven_cp )) )

			c.line( 60+145+10 , pos_inicial - 5, 60+145+10+100 , pos_inicial - 5)
			c.line( 60+145+10+110 , pos_inicial - 5, 60+145+10+110 +100 , pos_inicial - 5)
			c.line( 60+145+10 , pos_inicial - 8, 60+145+10+100 , pos_inicial - 8)
			c.line( 60+145+10+110 , pos_inicial - 8, 60+145+10+110 +100 , pos_inicial - 8)

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,17,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Inventario Final")
			c.setFont("Calibri-Bold", 9)
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_final_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_final_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.piedra_final_cp )) )
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,5,pagina)




		if self.state != 'draft' and self.state != 'extraccion' and self.state != 'trituracion':

			c.setFont("Calibri-Bold", 10)
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)		
			c.drawString( 50 ,pos_inicial, u"CALCINACION" )



			
			fondo = HexColor('#d1d1d1')
			c.setFillColor(fondo)
			c.rect(60+145 +5,pos_inicial-3,110,11,fill=True,stroke=True)
			c.rect(60+145 +5+110,pos_inicial-3,110,11,fill=True,stroke=True)
			c.rect(60+145 +5+220,pos_inicial-3,110,11,fill=True,stroke=True)
			c.setFillColor(black)

			c.drawCentredString( 60+145 +10 +50 ,pos_inicial, "Toneladas" )
			c.drawCentredString( 60+145 +10 +50 + 110 ,pos_inicial, "Importe" )
			c.drawCentredString( 60+145 +10 +50 + 110 +110 ,pos_inicial, "Costo Promedio" )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,16,pagina)


			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Inventario Inicial")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.calci_ini_ton )) )

			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.calci_ini_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.calci_ini_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Producción")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.calci_pro_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.calci_pro_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.calci_pro_cp )) )

			c.line( 60+145+10 , pos_inicial - 7, 60+145+10+100 , pos_inicial - 7)
			c.line( 60+145+10+110 , pos_inicial - 7, 60+145+10+110 +100 , pos_inicial - 7)

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,15,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Disponible")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.calci_dis_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.calci_dis_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.calci_dis_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Traspaso a Micronizado")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.calci_tt_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.calci_tt_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.calci_tt_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Ventas")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.calci_ven_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.calci_ven_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.calci_ven_cp )) )

			c.line( 60+145+10 , pos_inicial - 5, 60+145+10+100 , pos_inicial - 5)
			c.line( 60+145+10+110 , pos_inicial - 5, 60+145+10+110 +100 , pos_inicial - 5)
			c.line( 60+145+10 , pos_inicial - 8, 60+145+10+100 , pos_inicial - 8)
			c.line( 60+145+10+110 , pos_inicial - 8, 60+145+10+110 +100 , pos_inicial - 8)

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,17,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Inventario Final")
			c.setFont("Calibri-Bold", 9)
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.calci_final_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.calci_final_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.calci_final_cp )) )
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,5,pagina)


		if self.state != 'draft' and self.state != 'extraccion' and self.state != 'trituracion' and self.state != 'calcinacion':

			c.setFont("Calibri-Bold", 10)
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)		
			c.drawString( 50 ,pos_inicial, u"MICRONIZADO" )



			
			fondo = HexColor('#d1d1d1')
			c.setFillColor(fondo)
			c.rect(60+145 +5,pos_inicial-3,110,11,fill=True,stroke=True)
			c.rect(60+145 +5+110,pos_inicial-3,110,11,fill=True,stroke=True)
			c.rect(60+145 +5+220,pos_inicial-3,110,11,fill=True,stroke=True)
			c.setFillColor(black)

			c.drawCentredString( 60+145 +10 +50 ,pos_inicial, "Toneladas" )
			c.drawCentredString( 60+145 +10 +50 + 110 ,pos_inicial, "Importe" )
			c.drawCentredString( 60+145 +10 +50 + 110 +110 ,pos_inicial, "Costo Promedio" )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,16,pagina)


			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Inventario Inicial")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.micro_ini_ton )) )

			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.micro_ini_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.micro_ini_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Producción")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.micro_pro_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.micro_pro_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.micro_pro_cp )) )

			c.line( 60+145+10 , pos_inicial - 7, 60+145+10+100 , pos_inicial - 7)
			c.line( 60+145+10+110 , pos_inicial - 7, 60+145+10+110 +100 , pos_inicial - 7)

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,15,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Disponible")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.micro_dis_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.micro_dis_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.micro_dis_cp )) )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Ventas")
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.micro_ven_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.micro_ven_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.micro_ven_cp )) )

			c.line( 60+145+10 , pos_inicial - 5, 60+145+10+100 , pos_inicial - 5)
			c.line( 60+145+10+110 , pos_inicial - 5, 60+145+10+110 +100 , pos_inicial - 5)
			c.line( 60+145+10 , pos_inicial - 8, 60+145+10+100 , pos_inicial - 8)
			c.line( 60+145+10+110 , pos_inicial - 8, 60+145+10+110 +100 , pos_inicial - 8)

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,17,pagina)

			c.setFont("Calibri", 9)
			c.drawString( 60, pos_inicial, u"Inventario Final")

			c.setFont("Calibri-Bold", 9)
			c.drawRightString( 60+145+10 +100 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.micro_final_ton )) )
			c.drawRightString( 60+145+10 +100 + 110 ,pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.micro_final_imp )) )
			c.drawRightString( 60+145+10 +100 + 220 ,pos_inicial, '{:,.6f}'.format(decimal.Decimal ("%0.6f" % self.micro_final_cp )) )
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,17,pagina)



		if self.state != 'draft':
			c.setFont("Calibri-Bold", 9)
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.drawString( 50, pos_inicial, u"Costos")
			c.drawString( 160, pos_inicial, u"Extracción")

			c.drawRightString( 480, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_pro_imp ))  )



		if self.state != 'draft'  and self.state != 'extraccion':
			c.setFont("Calibri-Bold", 9)
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,19,pagina)

			c.drawString( 50, pos_inicial, u"Traspaso de Extracción")
			c.setFont("Calibri", 9)
			c.drawRightString( 260, pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_tt_ton ))  )
			c.drawRightString( 370, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_tt_cp ))  )
			c.drawRightString( 480, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.extra_tt_imp ))  )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri-Bold", 9)
			c.drawString( 50, pos_inicial, u"Costo del Mes Trituración")
			c.setFont("Calibri", 9)
			c.drawRightString( 480, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.tritu_pro_imp -self.extra_tt_imp )  ))  )
			c.line( 380 , pos_inicial - 7, 480 , pos_inicial - 7)
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,15,pagina)
			c.setFont("Calibri-Bold", 9)
			c.drawRightString( 480, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.tritu_pro_imp  )  ))  )


		if self.state != 'draft' and self.state != 'extraccion' and self.state != 'trituracion' :
			c.setFont("Calibri-Bold", 9)
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,19,pagina)

			c.drawString( 50, pos_inicial, u"Traspaso de Almacen de Piedra")
			c.setFont("Calibri", 9)
			c.drawRightString( 260, pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_tt_ton ))  )
			c.drawRightString( 370, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_tt_cp ))  )
			c.drawRightString( 480, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % self.piedra_tt_imp ))  )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)

			c.setFont("Calibri-Bold", 9)
			c.drawString( 50, pos_inicial, u"Costo del Mes Calcinación")
			c.setFont("Calibri", 9)
			c.drawRightString( 480, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.calci_pro_imp -self.piedra_tt_imp )  ))  )
			c.line( 380 , pos_inicial - 7, 480 , pos_inicial - 7)
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,15,pagina)
			c.setFont("Calibri-Bold", 9)
			c.drawRightString( 480, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.calci_pro_imp  )  ))  )



		c.setFont("Calibri-Bold", 9)
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,25,pagina)

		fondo = HexColor('#d1d1d1')
		fondo = HexColor('#ffffff')
		c.setFillColor(fondo)
		c.rect(10+50+65 ,pos_inicial-3,210,11,fill=True,stroke=True)
		c.rect(10+50+65 +210,pos_inicial-3,210,11,fill=True,stroke=True)
		c.setFillColor(black)

		c.drawCentredString(10+115+ 105, pos_inicial,'Toneladas')
		c.drawCentredString(10+115+ 105+210, pos_inicial,'Importes')

		# segunda linea
		c.setFont("Calibri-Bold", 9)
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,10,pagina)

		fondo = HexColor('#d1d1d1')
		c.setFillColor(fondo)
		c.rect(10+50+65 ,pos_inicial-3,70,11,fill=True,stroke=True)
		c.rect(10+50+65 +70,pos_inicial-3,70,11,fill=True,stroke=True)
		c.rect(10+50+65 +140,pos_inicial-3,70,11,fill=True,stroke=True)
		c.rect(10+50+65 +210,pos_inicial-3,70,11,fill=True,stroke=True)
		c.rect(10+50+65 +280,pos_inicial-3,70,11,fill=True,stroke=True)
		c.rect(10+50+65 +350,pos_inicial-3,70,11,fill=True,stroke=True)

		c.setFillColor(black)

		c.drawCentredString(10+115+ 35, pos_inicial,'Inventario Inicial')
		c.drawCentredString(10+115+ 105, pos_inicial,'Inventario Final')
		c.drawCentredString(10+115+ 175, pos_inicial,'Disponible')
		c.drawCentredString(10+115+ 245, pos_inicial,'Inventario Inicial')
		c.drawCentredString(10+115+ 315, pos_inicial,'Inventario Final')
		c.drawCentredString(10+115+ 385, pos_inicial,'Disponible')


		if self.state != 'draft' :
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)
			c.setFont("Calibri-Bold", 9)
			c.drawString(50, pos_inicial,'Extracción')
			c.setFont("Calibri", 9)
			c.drawRightString( 10+115+65,     pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.extra_ini_ton  )  ))  )
			c.drawRightString( 10+115+65+ 70, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.extra_final_ton  )  ))  )
			c.drawRightString( 10+115+65+140, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.extra_ini_ton- self.extra_final_ton  )  ))  )
			c.drawRightString( 10+115+65+210, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.extra_ini_imp  )  ))  )
			c.drawRightString( 10+115+65+280, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.extra_final_imp  )  ))  )
			c.drawRightString( 10+115+65+350, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.extra_ini_imp- self.extra_final_imp )  ))  )


		if self.state != 'draft' and self.state != 'extraccion' :
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)
			c.setFont("Calibri-Bold", 9)
			c.drawString(50, pos_inicial,'Trituración')
			c.setFont("Calibri", 9)
			c.drawRightString( 10+115+65,     pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.tritu_ini_ton  )  ))  )
			c.drawRightString( 10+115+65+ 70, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.tritu_final_ton  )  ))  )
			c.drawRightString( 10+115+65+140, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.tritu_ini_ton- self.tritu_final_ton  )  ))  )
			c.drawRightString( 10+115+65+210, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.tritu_ini_imp  )  ))  )
			c.drawRightString( 10+115+65+280, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.tritu_final_imp  )  ))  )
			c.drawRightString( 10+115+65+350, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.tritu_ini_imp- self.tritu_final_imp )  ))  )

			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)
			c.setFont("Calibri-Bold", 9)
			c.drawString(50, pos_inicial,'Almacen de Piedra')
			c.setFont("Calibri", 9)
			c.drawRightString( 10+115+65,     pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.piedra_ini_ton  )  ))  )
			c.drawRightString( 10+115+65+ 70, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.piedra_final_ton  )  ))  )
			c.drawRightString( 10+115+65+140, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.piedra_ini_ton- self.piedra_final_ton  )  ))  )
			c.drawRightString( 10+115+65+210, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.piedra_ini_imp  )  ))  )
			c.drawRightString( 10+115+65+280, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.piedra_final_imp  )  ))  )
			c.drawRightString( 10+115+65+350, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.piedra_ini_imp- self.piedra_final_imp )  ))  )

		if self.state != 'draft' and self.state != 'extraccion' and self.state != 'trituracion' :
			pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)
			c.setFont("Calibri-Bold", 9)
			c.drawString(50, pos_inicial,'Calcinación')
			c.setFont("Calibri", 9)
			c.drawRightString( 10+115+65,     pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.calci_ini_ton  )  ))  )
			c.drawRightString( 10+115+65+ 70, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.calci_final_ton  )  ))  )
			c.drawRightString( 10+115+65+140, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.calci_ini_ton- self.calci_final_ton  )  ))  )
			c.drawRightString( 10+115+65+210, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.calci_ini_imp  )  ))  )
			c.drawRightString( 10+115+65+280, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.calci_final_imp  )  ))  )
			c.drawRightString( 10+115+65+350, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % (self.calci_ini_imp- self.calci_final_imp )  ))  )

		total_tonel = 0
		total_impor = 0

		if self.state != 'draft' :
			total_tonel += self.extra_ini_ton- self.extra_final_ton
			total_impor += self.extra_ini_imp- self.extra_final_imp

		if self.state != 'draft' and self.state != 'extraccion' :
			total_tonel += self.piedra_ini_ton- self.piedra_final_ton
			total_impor += self.piedra_ini_imp- self.piedra_final_imp
			total_tonel += self.tritu_ini_ton- self.tritu_final_ton
			total_impor += self.tritu_ini_imp- self.tritu_final_imp

		if self.state != 'draft' and self.state != 'extraccion' and self.state != 'trituracion' :
			total_tonel += self.calci_ini_ton- self.calci_final_ton
			total_impor += self.calci_ini_imp- self.calci_final_imp


		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,17,pagina)

		c.setFont("Calibri-Bold", 9)
		c.drawString(50, pos_inicial,'Variación de Inventarios')
		c.drawRightString( 10+115+65+140, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % ( total_tonel  )  ))  )
		c.drawRightString( 10+115+65+350, pos_inicial ,  '{:,.2f}'.format(decimal.Decimal ("%0.2f" % ( total_impor )  ))  )		

		c.save()


	@api.multi
	def particionar_text(self,c,tam):
		tet = ""
		for i in range(len(c)):
			tet += c[i]
			lines = simpleSplit(tet,'Calibri',8,tam)
			if len(lines)>1:
				return tet[:-1]
		return tet

	@api.multi
	def verify_linea(self,c,wReal,hReal,posactual,valor,pagina):
		if posactual <40:
			c.showPage()
			self.cabezera(c,wReal,hReal)

			c.setFont("Calibri-Bold", 8)
			#c.drawCentredString(300,25,'Pág. ' + str(pagina+1))
			return pagina+1,hReal-83
		else:
			return pagina,posactual-valor




	@api.multi
	def exportarexcel(self):

		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		########### PRIMERA HOJA DE LA DATA EN TABLA
		#workbook = Workbook(output, {'in_memory': True})

		direccion = self.env['main.parameter'].search([])[0].dir_create_file

		workbook = Workbook(direccion +'costos_detalle.xlsx')
		worksheet = workbook.add_worksheet("Costos")
		bold = workbook.add_format({'bold': True})
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(9)
		boldbord.set_bg_color('#DCE6F1')
		numbersix = workbook.add_format({'num_format':'0.000000'})
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		bord = workbook.add_format()
		bord.set_border(style=1)
		numberdos.set_border(style=1)
		numbertres.set_border(style=1)			
		numbersix.set_border(style=1)			
		x= 3				
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')


		equivalente = {
			'01':'Enero',
			'02':'Febrero',
			'03':'Marzo',
			'04':'Abril',
			'05':'Mayo',
			'06':'Junio',
			'07':'Julio',
			'08':'Agosto',
			'09':'Septiembre',
			'10':'Octubre',
			'11':'Noviembre',
			'12':'Diciembre',
		}
		worksheet.write(0,0, self.env["res.company"].search([])[0].name.upper() , bold)
		worksheet.write(1,0, u"Costo de Producción "+ equivalente[ self.periodo.code.split('/')[0] ] +" "+ self.fiscal.name  ,bold)

		#worksheet.write(1,1, total.date.strftime('%Y-%m-%d %H:%M'),bord)
		

		#ven aki


		if self.state != 'draft':


			worksheet.write(x,0, u"EXTRACCION",boldbord)

			worksheet.write(x,2, u"Toneladas",boldbord)
			worksheet.write(x,3, u"Importe",boldbord)
			worksheet.write(x,4, u"Costo Promedio",boldbord)

			x+= 1
			worksheet.write(x,0, u"Inventario Inicial",bord)

			worksheet.write(x,2, self.extra_ini_ton,numberdos)
			worksheet.write(x,3, self.extra_ini_imp,numberdos)
			worksheet.write(x,4, self.extra_ini_cp,numbersix)
			x+= 1
			worksheet.write(x,0, u"Producción",bord)

			worksheet.write(x,2, self.extra_pro_ton,numberdos)
			worksheet.write(x,3, self.extra_pro_imp,numberdos)
			worksheet.write(x,4, self.extra_pro_cp,numbersix)


			x+= 1
			worksheet.write(x,0, u"Disponible",bord)

			worksheet.write(x,2, self.extra_dis_ton,numberdos)
			worksheet.write(x,3, self.extra_dis_imp,numberdos)
			worksheet.write(x,4, self.extra_dis_cp,numbersix)

			x+= 1
			worksheet.write(x,0, u"Traspaso a Trituración",bord)

			worksheet.write(x,2, self.extra_tt_ton,numberdos)
			worksheet.write(x,3, self.extra_tt_imp,numberdos)
			worksheet.write(x,4, self.extra_tt_cp,numbersix)


			x+= 1
			worksheet.write(x,0, u"Inventario Final",bord)

			worksheet.write(x,2, self.extra_final_ton,numberdos)
			worksheet.write(x,3, self.extra_final_imp,numberdos)
			worksheet.write(x,4, self.extra_final_cp,numbersix)

			x+= 1

		if self.state != 'draft' and self.state != 'extraccion':


			x+= 1

			worksheet.write(x,0, u"TRITURACION",boldbord)

			worksheet.write(x,2, u"Toneladas",boldbord)
			worksheet.write(x,3, u"Importe",boldbord)
			worksheet.write(x,4, u"Costo Promedio",boldbord)

			x+= 1
			worksheet.write(x,0, u"Inventario Inicial",bord)

			worksheet.write(x,2, self.tritu_ini_ton,numberdos)
			worksheet.write(x,3, self.tritu_ini_imp,numberdos)
			worksheet.write(x,4, self.tritu_ini_cp,numbersix)
			x+= 1

			worksheet.write(x,0, u"Producción",bord)

			worksheet.write(x,2, self.tritu_pro_ton,numberdos)
			worksheet.write(x,3, self.tritu_pro_imp,numberdos)
			worksheet.write(x,4, self.tritu_pro_cp,numbersix)
			x+= 1

			worksheet.write(x,0, u"Disponible",bord)

			worksheet.write(x,2, self.tritu_dis_ton,numberdos)
			worksheet.write(x,3, self.tritu_dis_imp,numberdos)
			worksheet.write(x,4, self.tritu_dis_cp,numbersix)
			x+= 1


			worksheet.write(x,0, u"Traspaso a HM",bord)

			worksheet.write(x,2, self.tritu_tt_ton,numberdos)
			worksheet.write(x,3, self.tritu_tt_imp,numberdos)
			worksheet.write(x,4, self.tritu_tt_cp,numbersix)
			x+= 1


			worksheet.write(x,0, u"Ventas",bord)

			worksheet.write(x,2, self.tritu_ven_ton,numberdos)
			worksheet.write(x,3, self.tritu_ven_imp,numberdos)
			worksheet.write(x,4, self.tritu_ven_cp,numbersix)
			x+= 1


			worksheet.write(x,0, u"Inventario Final",bord)

			worksheet.write(x,2, self.tritu_final_ton,numberdos)
			worksheet.write(x,3, self.tritu_final_imp,numberdos)
			worksheet.write(x,4, self.tritu_final_cp,numbersix)
			x+= 1
			x+= 1


			worksheet.write(x,0, u"ALMACEN DE PIEDRA HM",boldbord)

			worksheet.write(x,2, u"Toneladas",boldbord)
			worksheet.write(x,3, u"Importe",boldbord)
			worksheet.write(x,4, u"Costo Promedio",boldbord)


			x+= 1


			worksheet.write(x,0, u"Inventario Final",bord)

			worksheet.write(x,2, self.piedra_ini_ton,numberdos)
			worksheet.write(x,3, self.piedra_ini_imp,numberdos)
			worksheet.write(x,4, self.piedra_ini_cp,numbersix)
			x+= 1


			worksheet.write(x,0, u"Entrada de Piedra de Trituración",bord)

			worksheet.write(x,2, self.piedra_pro_ton,numberdos)
			worksheet.write(x,3, self.piedra_pro_imp,numberdos)
			worksheet.write(x,4, self.piedra_pro_cp,numbersix)

			x+= 1


			worksheet.write(x,0, u"Disponible",bord)

			worksheet.write(x,2, self.piedra_dis_ton,numberdos)
			worksheet.write(x,3, self.piedra_dis_imp,numberdos)
			worksheet.write(x,4, self.piedra_dis_cp,numbersix)


			x+= 1


			worksheet.write(x,0, u"Traspaso a Calcinación",bord)

			worksheet.write(x,2, self.piedra_tt_ton,numberdos)
			worksheet.write(x,3, self.piedra_tt_imp,numberdos)
			worksheet.write(x,4, self.piedra_tt_cp,numbersix)


			x+= 1

			worksheet.write(x,0, u"Ventas",bord)

			worksheet.write(x,2, self.piedra_ven_ton,numberdos)
			worksheet.write(x,3, self.piedra_ven_imp,numberdos)
			worksheet.write(x,4, self.piedra_ven_cp,numbersix)


			x+= 1

			worksheet.write(x,0, u"Inventario Final",bord)

			worksheet.write(x,2, self.piedra_final_ton,numberdos)
			worksheet.write(x,3, self.piedra_final_imp,numberdos)
			worksheet.write(x,4, self.piedra_final_cp,numbersix)

			x+= 1



		if self.state != 'draft' and self.state != 'extraccion' and self.state != 'trituracion':



			x+= 1

			worksheet.write(x,0, u"CALCINACION",boldbord)

			worksheet.write(x,2, u"Toneladas",boldbord)
			worksheet.write(x,3, u"Importe",boldbord)
			worksheet.write(x,4, u"Costo Promedio",boldbord)

			x+= 1
			worksheet.write(x,0, u"Inventario Inicial",bord)

			worksheet.write(x,2, self.calci_ini_ton,numberdos)
			worksheet.write(x,3, self.calci_ini_imp,numberdos)
			worksheet.write(x,4, self.calci_ini_cp,numbersix)
			x+= 1

			worksheet.write(x,0, u"Producción",bord)

			worksheet.write(x,2, self.calci_pro_ton,numberdos)
			worksheet.write(x,3, self.calci_pro_imp,numberdos)
			worksheet.write(x,4, self.calci_pro_cp,numbersix)
			x+= 1

			worksheet.write(x,0, u"Disponible",bord)

			worksheet.write(x,2, self.calci_dis_ton,numberdos)
			worksheet.write(x,3, self.calci_dis_imp,numberdos)
			worksheet.write(x,4, self.calci_dis_cp,numbersix)
			x+= 1


			worksheet.write(x,0, u"Traspaso a Micronizado",bord)

			worksheet.write(x,2, self.calci_tt_ton,numberdos)
			worksheet.write(x,3, self.calci_tt_imp,numberdos)
			worksheet.write(x,4, self.calci_tt_cp,numbersix)
			x+= 1


			worksheet.write(x,0, u"Ventas",bord)

			worksheet.write(x,2, self.calci_ven_ton,numberdos)
			worksheet.write(x,3, self.calci_ven_imp,numberdos)
			worksheet.write(x,4, self.calci_ven_cp,numbersix)
			x+= 1


			worksheet.write(x,0, u"Inventario Final",bord)

			worksheet.write(x,2, self.calci_final_ton,numberdos)
			worksheet.write(x,3, self.calci_final_imp,numberdos)
			worksheet.write(x,4, self.calci_final_cp,numbersix)
			x+= 1


		if self.state != 'draft' and self.state != 'extraccion' and self.state != 'trituracion' and self.state != 'calcinacion':

			x+= 1

			worksheet.write(x,0, u"MICRONIZADO",boldbord)

			worksheet.write(x,2, u"Toneladas",boldbord)
			worksheet.write(x,3, u"Importe",boldbord)
			worksheet.write(x,4, u"Costo Promedio",boldbord)

			x+= 1
			worksheet.write(x,0, u"Inventario Inicial",bord)

			worksheet.write(x,2, self.micro_ini_ton,numberdos)
			worksheet.write(x,3, self.micro_ini_imp,numberdos)
			worksheet.write(x,4, self.micro_ini_cp,numbersix)
			x+= 1

			worksheet.write(x,0, u"Producción",bord)

			worksheet.write(x,2, self.micro_pro_ton,numberdos)
			worksheet.write(x,3, self.micro_pro_imp,numberdos)
			worksheet.write(x,4, self.micro_pro_cp,numbersix)
			x+= 1

			worksheet.write(x,0, u"Disponible",bord)

			worksheet.write(x,2, self.micro_dis_ton,numberdos)
			worksheet.write(x,3, self.micro_dis_imp,numberdos)
			worksheet.write(x,4, self.micro_dis_cp,numbersix)
			x+= 1

			worksheet.write(x,0, u"Ventas",bord)

			worksheet.write(x,2, self.micro_ven_ton,numberdos)
			worksheet.write(x,3, self.micro_ven_imp,numberdos)
			worksheet.write(x,4, self.micro_ven_cp,numbersix)
			x+= 1


			worksheet.write(x,0, u"Inventario Final",bord)

			worksheet.write(x,2, self.micro_final_ton,numberdos)
			worksheet.write(x,3, self.micro_final_imp,numberdos)
			worksheet.write(x,4, self.micro_final_cp,numbersix)
			x+= 1



		if self.state != 'draft':

			x+= 2

			worksheet.write(x,0, u"Costos",boldbord)

			worksheet.write(x,2, u"Extraccion",boldbord)
			worksheet.write(x,4, self.extra_pro_imp ,numberdos)


		if self.state != 'draft'  and self.state != 'extraccion':

			x+= 2

			worksheet.write(x,0, u"Traspaso de Extracción",bord)

			worksheet.write(x,2, self.extra_tt_ton ,numberdos)
			worksheet.write(x,3, self.extra_tt_cp ,numberdos)
			worksheet.write(x,4, self.extra_tt_imp ,numberdos)

			x+= 1

			worksheet.write(x,0, u"Costo del Mes Trituración",bord)

			worksheet.write(x,4, self.tritu_pro_imp -self.extra_tt_imp ,numberdos)
			
			x+= 1

			worksheet.write(x,0, u"Total",boldbord)

			worksheet.write(x,4, self.tritu_pro_imp ,numberdos)


		if self.state != 'draft' and self.state != 'extraccion' and self.state != 'trituracion' :



			x+= 1

			worksheet.write(x,0, u"Traspaso de Almacen de Piedra",bord)
			worksheet.write(x,2, self.piedra_tt_ton ,numberdos)
			worksheet.write(x,3, self.piedra_tt_cp ,numberdos)
			worksheet.write(x,4, self.piedra_tt_imp ,numberdos)
			x+= 1
			worksheet.write(x,0, u"Costo del Mes Calcinación",bord)
			worksheet.write(x,4, self.calci_pro_imp -self.piedra_tt_imp ,numberdos)
			x+= 1
			worksheet.write(x,0, u"Total",boldbord)
			worksheet.write(x,4, self.calci_pro_imp ,numberdos)


		x+= 2

		worksheet.merge_range(x,1,x,3, 'Toneladas',boldbord)
		worksheet.merge_range(x,4,x,6, 'Importes',boldbord)

		x+= 1
		
		worksheet.write(x,1, u"Inventario Inicial",boldbord)
		worksheet.write(x,2, u"Inventario Final",boldbord)
		worksheet.write(x,3, u"Disponible",boldbord)
		worksheet.write(x,4, u"Inventario Inicial",boldbord)
		worksheet.write(x,5, u"Inventario Final",boldbord)
		worksheet.write(x,6, u"Disponible",boldbord)

		x+= 1

		if self.state != 'draft' :
			
			worksheet.write(x,0, u"Disponible", bord)

			worksheet.write(x,1, self.extra_ini_ton , numberdos)
			worksheet.write(x,2, self.extra_final_ton , numberdos)
			worksheet.write(x,3, self.extra_ini_ton-self.extra_final_ton , numberdos)
			worksheet.write(x,4, self.extra_ini_imp , numberdos)
			worksheet.write(x,5, self.extra_final_imp , numberdos)
			worksheet.write(x,6, self.extra_ini_imp-self.extra_final_imp , numberdos)
			x+= 1

		if self.state != 'draft' and self.state != 'extraccion' :

			worksheet.write(x,0, u"Trituración", bord)

			worksheet.write(x,1, self.tritu_ini_ton , numberdos)
			worksheet.write(x,2, self.tritu_final_ton , numberdos)
			worksheet.write(x,3, self.tritu_ini_ton-self.tritu_final_ton , numberdos)
			worksheet.write(x,4, self.tritu_ini_imp , numberdos)
			worksheet.write(x,5, self.tritu_final_imp , numberdos)
			worksheet.write(x,6, self.tritu_ini_imp-self.tritu_final_imp , numberdos)
			x+= 1
			worksheet.write(x,0, u"Almacen de Piedra", bord)

			worksheet.write(x,1, self.piedra_ini_ton , numberdos)
			worksheet.write(x,2, self.piedra_final_ton , numberdos)
			worksheet.write(x,3, self.piedra_ini_ton-self.piedra_final_ton , numberdos)
			worksheet.write(x,4, self.piedra_ini_imp , numberdos)
			worksheet.write(x,5, self.piedra_final_imp , numberdos)
			worksheet.write(x,6, self.piedra_ini_imp-self.piedra_final_imp , numberdos)
			x+= 1


		if self.state != 'draft' and self.state != 'extraccion' and self.state != 'trituracion' :

			worksheet.write(x,0, u"Calcinación", bord)

			worksheet.write(x,1, self.calci_ini_ton , numberdos)
			worksheet.write(x,2, self.calci_final_ton , numberdos)
			worksheet.write(x,3, self.calci_ini_ton-self.calci_final_ton , numberdos)
			worksheet.write(x,4, self.calci_ini_imp , numberdos)
			worksheet.write(x,5, self.calci_final_imp , numberdos)
			worksheet.write(x,6, self.calci_ini_imp-self.calci_final_imp , numberdos)
			x+= 1


		total_tonel = 0
		total_impor = 0

		if self.state != 'draft' :
			total_tonel += self.extra_ini_ton- self.extra_final_ton
			total_impor += self.extra_ini_imp- self.extra_final_imp

		if self.state != 'draft' and self.state != 'extraccion' :
			total_tonel += self.piedra_ini_ton- self.piedra_final_ton
			total_impor += self.piedra_ini_imp- self.piedra_final_imp
			total_tonel += self.tritu_ini_ton- self.tritu_final_ton
			total_impor += self.tritu_ini_imp- self.tritu_final_imp

		if self.state != 'draft' and self.state != 'extraccion' and self.state != 'trituracion' :
			total_tonel += self.calci_ini_ton- self.calci_final_ton
			total_impor += self.calci_ini_imp- self.calci_final_imp


		worksheet.write(x,0, u"Variación de Inventarios", bord)
		worksheet.write(x,3, total_tonel , numberdos)
		worksheet.write(x,6, total_impor , numberdos)

		tam_col = [32,24,24,24,24,24,24,24,24,24,24,24,11,14,14,10,16,16,20,36]


		worksheet.set_column('A:A', tam_col[0])
		worksheet.set_column('B:B', tam_col[1])
		worksheet.set_column('C:C', tam_col[2])
		worksheet.set_column('D:D', tam_col[3])
		worksheet.set_column('E:E', tam_col[4])
		worksheet.set_column('F:F', tam_col[5])
		worksheet.set_column('G:G', tam_col[6])
		worksheet.set_column('H:H', tam_col[7])
		worksheet.set_column('I:I', tam_col[8])
		worksheet.set_column('J:J', tam_col[9])
		worksheet.set_column('K:K', tam_col[10])
		worksheet.set_column('L:L', tam_col[11])
		worksheet.set_column('M:M', tam_col[12])
		worksheet.set_column('N:N', tam_col[13])
		worksheet.set_column('O:O', tam_col[14])
		worksheet.set_column('P:P', tam_col[15])
		worksheet.set_column('Q:Q', tam_col[16])
		worksheet.set_column('R:R', tam_col[17])
		worksheet.set_column('S:S', tam_col[18])
		worksheet.set_column('T:T', tam_col[19])

		workbook.close()
		
		f = open(direccion + 'costos_detalle.xlsx', 'rb')
		
		
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'Costos.xlsx',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		sfs_id = self.env['export.file.save'].create(vals)
		result = {}
		view_ref = mod_obj.get_object_reference('account_contable_book_it', 'export_file_save_action')
		view_id = view_ref and view_ref[1] or False
		result = act_obj.read( [view_id] )
		print sfs_id

		#import os
		#os.system('c:\\eSpeak2\\command_line\\espeak.exe -ves-f1 -s 170 -p 100 "Se Realizo La exportación exitosamente Y A EDWARD NO LE GUSTA XDXDXDXDDDDDDDDDDDD" ')

		return {
		    "type": "ir.actions.act_window",
		    "res_model": "export.file.save",
		    "views": [[False, "form"]],
		    "res_id": sfs_id.id,
		    "target": "new",
		}
