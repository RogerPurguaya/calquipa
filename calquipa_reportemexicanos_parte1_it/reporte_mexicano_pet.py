# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import magenta, red , black, white, blue, gray, Color, HexColor, PCMYKColor, PCMYKColorSep
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, A4, legal
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table
from reportlab.lib.units import  cm,mm
from reportlab.lib.utils import simpleSplit
from cgi import escape

import decimal
import calendar

def dig_5(n):
	return ("%5d" % n).replace(' ','0')

class grupo_report_pet(models.Model):
	_name = 'grupo.report.pet'

	titulo = fields.Char('Name',required=True)
	order = fields.Integer('Order',required=True)

	@api.one
	def get_name_person(self):
		self.name = str(self.order) + '-' + self.titulo

	name = fields.Char('Name',compute="get_name_person")


class tipo_report_pet(models.Model):
	_name = 'tipo.report.pet'

	titulo = fields.Char('Name',required=True)
	order = fields.Integer('Order',required=True)

	@api.one
	def get_name_person(self):
		self.name = str(self.order) + '-' + self.titulo

	name = fields.Char('Name',compute="get_name_person")


class rm_report_pet_line(models.Model):
	_name = 'rm.report.pet.line'


	rm_report_pet_id = fields.Many2one('rm.report.pet','Cabezera')

		

	cuenta = fields.Char('Cuenta')
	tipo = fields.Many2one('tipo.report.pet','Tipo',required=True)
	concepto = fields.Char('Concepto',required=True)
	grupo = fields.Many2one('grupo.report.pet','Grupo',required=True)

	enero = fields.Float('Enero',digits=(12,2),readonly=True,default=0)
	febrero = fields.Float('Febrero',digits=(12,2),readonly=True,default=0)
	marzo = fields.Float('Marzo',digits=(12,2),readonly=True,default=0)
	abril = fields.Float('Abril',digits=(12,2),readonly=True,default=0)
	mayo = fields.Float('Mayo',digits=(12,2),readonly=True,default=0)
	junio = fields.Float('Junio',digits=(12,2),readonly=True,default=0)
	julio = fields.Float('Julio',digits=(12,2),readonly=True,default=0)
	agosto = fields.Float('Agosto',digits=(12,2),readonly=True,default=0)
	septiembre = fields.Float('Septiembre',digits=(12,2),readonly=True,default=0)
	octubre = fields.Float('Octubre',digits=(12,2),readonly=True,default=0)
	noviembre = fields.Float('Noviembre',digits=(12,2),readonly=True,default=0)
	diciembre = fields.Float('Diciembre',digits=(12,2),readonly=True,default=0)

	porcentaje = fields.Float ('Porcentage %')

	@api.one
	def get_monto(self):
		m = str(self.rm_report_pet_id.period_actual.code).split('/')
		m = int(m[0])
		mont = 0
		cant = {
			1: self.enero,
			2: self.febrero,
			3: self.marzo,
			4: self.abril,
			5: self.mayo,
			6: self.junio,
			7: self.julio,
			8: self.agosto,
			9: self.septiembre,
			10: self.octubre,
			11: self.noviembre,
			12: self.diciembre,
		}
		mont = cant[int(self.rm_report_pet_id.period_actual.code.split('/')[0])]
		self.monto = mont * float(self.porcentaje)/float(100)
	monto = fields.Float('Monto', digits=(12,2), readonly=True, default=0, compute="get_monto")

	@api.one
	def get_acumulado(self):
		self.acumulado = self.enero + self.febrero + self.marzo + self.abril + self.mayo + self.junio + self.julio + self.agosto + self.septiembre + self.octubre + self.noviembre + self.diciembre
		self.acumulado = self.acumulado * float(self.porcentaje)/float(100)
	acumulado = fields.Float('Acumulado', readonly=True, default=0, compute="get_acumulado")

	@api.one
	def get_acumulado_pciento(self):
		if self.acumulado != 0:
			self.acumulado_pciento = self.acumulado / self.rm_report_pet_id.total_general
		else:
			self.acumulado_pciento = 0
	acumulado_pciento = fields.Float('%  ACUM', readonly=True, compute="get_acumulado_pciento")

	@api.one
	def get_promedio(self):
		if self.acumulado != 0:
			self.promedio = self.acumulado / 1
			self.promedio = self.promedio * float(self.porcentaje)/float(100)
		else:
			self.promedio = 0
	promedio = fields.Float('Promedio', readonly=True, compute="get_promedio")

	@api.one
	def get_promedio_pciento(self):
		if self.acumulado != 0:
			self.promedio_pciento = self.promedio / self.rm_report_pet_id.total_promedio_general
		else:
			self.promedio_pciento = 0
	promedio_pciento = fields.Float('%  PROM', readonly=True, compute="get_promedio_pciento")

class rm_report_pet(models.Model):
	_name= 'rm.report.pet'

	fiscal = fields.Many2one('account.fiscalyear','Año Fiscal',required=True)
	sitio = fields.Char('Sitio',required=False)
	centro_de_costo = fields.Char('Centro de Costo',readonly=True,default='Pet Coke')
	proposito = fields.Char('Propósito')
	fecha_emision_reporte = fields.Date('Fecha de Emisión del Reporte',required=True)
	usuario = fields.Many2one('res.users','Usuario',readonly=True)
	conf_line_ids = fields.One2many('rm.report.pet.line','rm_report_pet_id','Lineas de Configuración')
	period_actual = fields.Many2one('account.period','Periodo Actual Informe',required=True)

	porcentaje = fields.Float ('Porcentage %')

	@api.one
	def get_total_general(self):
		self.total_general = 0
		for i in self.conf_line_ids:
			self.total_general += i.acumulado
		print self.total_general
	total_general = fields.Float('Total general', compute="get_total_general")

	@api.one	
	def get_total_promedio_general(self):
		self.total_promedio_general = 0
		for i in self.conf_line_ids:
			self.total_promedio_general += i.promedio
		print self.total_promedio_general
	total_promedio_general = fields.Float('Total general', compute="get_total_promedio_general")

	@api.one
	def unlink(self):
		if len(self.conf_line_ids) > 0:
			raise osv.except_osv('Alerta!', "No se puede eliminar un reporte que contenga lineas.")
		return super(rm_report_pet,self).unlink()

	@api.one
	def copy(self,default):
		t= super(rm_report_pet,self).copy(default)
		for i in self.conf_line_ids:
			vals_i = {
				'rm_report_pet_id':t.id,
				'cuenta':i.cuenta,
				'tipo':i.tipo.id,
				'concepto':i.concepto,
				'grupo':i.grupo.id,
				'enero':0,
				'febrero':0,
				'marzo':0,
				'abril':0,
				'mayo':0,
				'junio':0,
				'julio':0,
				'agosto':0,
				'septiembre':0,
				'octubre':0,
				'noviembre':0,
				'diciembre':0,
				'porcentaje': i.porcentaje,
			}
			self.env['rm.report.pet.line'].create(vals_i)
		return t

	@api.one
	def get_name_set(self):
		self.name = self.fiscal.name + '-'+ self.centro_de_costo

	name = fields.Char('Nombre',compute='get_name_set')


	@api.model
	def create(self,vals):
		vals['usuario']= self.env.uid
		return super(rm_report_pet,self).create(vals)


	@api.one
	def calculate(self):
		m = str(self.period_actual.code).split('/')
		limite = m[1]+ m[0]

		self.env.cr.execute("""
update rm_report_pet_line opt set
enero= 0, febrero = 0,
marzo= 0, abril= 0,
mayo= 0, junio= 0,
julio= 0, agosto= 0,
septiembre= 0, octubre= 0,
noviembre= 0, diciembre= 0
where opt.rm_report_pet_id = """ + str(self.id) + """
""")

		self.env.cr.execute("""
update rm_report_pet_line opt set
enero= saldos.saldo01, febrero = saldos.saldo02,
marzo= saldos.saldo03, abril= saldos.saldo04,
mayo= saldos.saldo05, junio= saldos.saldo06,
julio= saldos.saldo07, agosto= saldos.saldo08,
septiembre= saldos.saldo09, octubre= saldos.saldo10,
noviembre= saldos.saldo11, diciembre= saldos.saldo12
from (
select t1.id,left(t1.code,9)as nivel1,left(t1.code,3) as nivel2,left(t1.code,6) as nivel3,t1.code,t1.name,t1.type,
coalesce(saldo01,0) as saldo01,coalesce(saldo02,0) as saldo02,coalesce(saldo03,0) as saldo03,coalesce(saldo04,0) as saldo04,
coalesce(saldo05,0) as saldo05,coalesce(saldo06,0) as saldo06,coalesce(saldo07,0) as saldo07,coalesce(saldo08,0) as saldo08,
coalesce(saldo09,0) as saldo09,coalesce(saldo10,0) as saldo10,coalesce(saldo11,0) as saldo11,coalesce(saldo12,0) as saldo12,
saldo01+saldo02+saldo03+saldo04+saldo05+saldo06+saldo07+saldo08+saldo09+saldo10+saldo11+saldo12 as total from account_account t1
left join (select left(aa.code,9) as cuenta,sum(debit)-sum(credit) as saldo01 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '01/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by left(aa.code,9)) t2 on t2.cuenta= left(t1.code,9)
left join (select left(aa.code,9) as cuenta,sum(debit)-sum(credit) as saldo02 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '02/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by left(aa.code,9)) t3 on t3.cuenta= left(t1.code,9)
left join (select left(aa.code,9) as cuenta,sum(debit)-sum(credit) as saldo03 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '03/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by left(aa.code,9)) t4 on t4.cuenta= left(t1.code,9)
left join (select left(aa.code,9) as cuenta,sum(debit)-sum(credit) as saldo04 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '04/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by left(aa.code,9)) t5 on t5.cuenta= left(t1.code,9)
left join (select left(aa.code,9) as cuenta,sum(debit)-sum(credit) as saldo05 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '05/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by left(aa.code,9)) t6 on t6.cuenta= left(t1.code,9)
left join (select left(aa.code,9) as cuenta,sum(debit)-sum(credit) as saldo06 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '06/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by left(aa.code,9)) t7 on t7.cuenta= left(t1.code,9)
left join (select left(aa.code,9) as cuenta,sum(debit)-sum(credit) as saldo07 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '07/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by left(aa.code,9)) t8 on t8.cuenta= left(t1.code,9)
left join (select left(aa.code,9) as cuenta,sum(debit)-sum(credit) as saldo08 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '08/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by left(aa.code,9)) t9 on t9.cuenta= left(t1.code,9)
left join (select left(aa.code,9) as cuenta,sum(debit)-sum(credit) as saldo09 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '09/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by left(aa.code,9)) t10 on t10.cuenta= left(t1.code,9)
left join (select left(aa.code,9) as cuenta,sum(debit)-sum(credit) as saldo10 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '10/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by left(aa.code,9)) t11 on t11.cuenta= left(t1.code,9)
left join (select left(aa.code,9) as cuenta,sum(debit)-sum(credit) as saldo11 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '11/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by left(aa.code,9)) t12 on t12.cuenta= left(t1.code,9)
left join (select left(aa.code,9) as cuenta,sum(debit)-sum(credit) as saldo12 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '12/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by left(aa.code,9)) t13 on t13.cuenta= left(t1.code,9)
where t1.type<>'view') saldos
where opt.cuenta = saldos.nivel1 and opt.rm_report_pet_id = """ + str(self.id) + """
			""")

	@api.one
	def get_pie_pagina(self):

		parametros = self.env['main.parameter'].search([])[0]
		fecha_split = str(self.period_actual.code).split('/')
		fecha_split = [fecha_split[1],fecha_split[0]]
		#fecha_split = str(self.fecha_emision_reporte).split('-')
		dia_ultimo = ("%2d"%calendar.monthrange(int(fecha_split[0]),int(fecha_split[1]))[1]).replace(' ','0')

		fechaini = fecha_split[0] + fecha_split[1] + '01'
		fechafin = fecha_split[0] + fecha_split[1] + dia_ultimo

		fechainiEnero = fecha_split[0]  + '0101'
		rpt = []
		#### la primera linea
		rpt.append([0,0,0,0,0,0])

		#### la segunda linea
		tmp = []
		self.env.cr.execute(""" 
		   select sum(ingreso) as ingreso,sum(round(debit,2)) as debit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
		   '{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_pet.id) + """}') 
		   where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
		   or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
		""")
		num_tmp = 0
		for w in self.env.cr.fetchall():
			num_tmp = w[0]
		if num_tmp == None:
			num_tmp = 0
		tmp.append(num_tmp)
		tmp.append(0)

		self.env.cr.execute(""" 
		   select sum(ingreso) as ingreso,sum(round(debit,2)) as debit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
		   '{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_pet.id) + """}') 
		   where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
		   or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
		""")
		num_tmp = 0
		for w in self.env.cr.fetchall():
			num_tmp = w[1]
		if num_tmp == None:
			num_tmp = 0
		tmp.append(num_tmp)
		tmp[1]= 0 if tmp[0]==0 else float(tmp[2] / tmp[0])


		self.env.cr.execute(""" 
		   select sum(ingreso) as ingreso,sum(round(debit,2)) as debit from get_kardex_v("""+fechainiEnero+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
		   '{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_pet.id) + """}') 
		   where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
		   or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
		""")
		num_tmp = 0
		for w in self.env.cr.fetchall():
			num_tmp = w[0]
		if num_tmp == None:
			num_tmp = 0
		tmp.append(num_tmp)
		tmp.append(0)

		self.env.cr.execute(""" 
		   select sum(ingreso) as ingreso,sum(round(debit,2)) as debit from get_kardex_v("""+fechainiEnero+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
		   '{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_pet.id) + """}') 
		   where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
		   or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
		""")
		num_tmp = 0
		for w in self.env.cr.fetchall():
			num_tmp = w[1]
		if num_tmp == None:
			num_tmp = 0
		tmp.append(num_tmp)
		tmp[4]= 0 if tmp[3]==0 else float(tmp[5] / tmp[3])
		
		rpt.append(tmp)


		## la linea 3 Inventario inicial
		rpt.append([0,0,0,0,0,0])

		## la linea 4 COmpras
		tmp = []

		var_txt_con = """
			select (ingreso) as ingreso,(round(debit,2)) as credit, ubicacion_destino, ubicacion_origen from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','supplier')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+str(parametros.location_existencias_pet.id)+ """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
			""")
		rep_ingreso = 0
		rep_debit = 0
		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','supplier')]):
				if i[2] == ii.id or i[3] == ii.id :
					rep_ingreso += i[0]
					rep_debit += i[1]
		rep_cp = 0 if rep_ingreso == 0 else rep_debit / rep_ingreso

		tmp.append(rep_ingreso)
		tmp.append(rep_cp)
		tmp.append(rep_debit)




		var_txt_con = """
			select (ingreso) as ingreso,(round(debit,2)) as credit, ubicacion_destino, ubicacion_origen from get_kardex_v("""+fechainiEnero+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','supplier')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+str(parametros.location_existencias_pet.id)+ """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
			""")
		rep_ingreso = 0
		rep_debit = 0
		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','supplier')]):
				if i[2] == ii.id or i[3] == ii.id :
					rep_ingreso += i[0]
					rep_debit += i[1]
		rep_cp = 0 if rep_ingreso == 0 else rep_debit / rep_ingreso

		tmp.append(rep_ingreso)
		tmp.append(rep_cp)
		tmp.append(rep_debit)

		rpt.append(tmp)

		### la linea 5 disponible
		rpt.append([0,0,0,0,0,0])

		### la linea 6 envio tr
		rpt.append([0,0,0,0,0,0])

		### la linea 7 traspaso a trituracion

		tmp = []
		self.env.cr.execute(""" 
		   select sum(salida) as ingreso,sum(round(credit,2)) as debit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
		   '{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_pet.id) + """}') 
		   where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
		   or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
		""")
		num_salida = 0
		num_importe = 0
		for w in self.env.cr.fetchall():
			num_salida = w[0]
			num_importe = w[1]
		if num_salida == None:
			num_salida = 0
			num_importe = 0

		num_cp = 0 if num_salida == 0 else float(num_importe / num_salida)

		tmp.append(num_salida)
		tmp.append(num_cp)
		tmp.append(num_importe)
		

		self.env.cr.execute(""" 
		   select sum(salida) as ingreso,sum(round(credit,2)) as debit from get_kardex_v("""+fechainiEnero+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
		   '{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_pet.id) + """}') 
		   where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
		   or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
		""")
		num_salida = 0
		num_importe = 0
		for w in self.env.cr.fetchall():
			num_salida = w[0]
			num_importe = w[1]
		if num_salida == None:
			num_salida = 0
			num_importe = 0

		num_cp = 0 if num_salida == 0 else float(num_importe / num_salida)

		tmp.append(num_salida)
		tmp.append(num_cp)
		tmp.append(num_importe)

		rpt.append(tmp)

		### la linea 8 transpaso a agregaods

		rpt.append([0,0,0,0,0,0])

		### la linea 9 ventas

		tmp = []

		var_txt_con = """
			select (ingreso) as ingreso,(round(debit,2)) as credit, ubicacion_destino, ubicacion_origen from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','customer')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+str(parametros.location_existencias_pet.id)+ """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
			""")
		rep_ingreso = 0
		rep_debit = 0
		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','customer')]):
				if i[2] == ii.id or i[3] == ii.id :
					rep_ingreso += i[0]
					rep_debit += i[1]
		rep_cp = 0 if rep_ingreso == 0 else rep_debit / rep_ingreso

		tmp.append(rep_ingreso)
		tmp.append(rep_cp)
		tmp.append(rep_debit)




		var_txt_con = """
			select (ingreso) as ingreso,(round(debit,2)) as credit, ubicacion_destino, ubicacion_origen from get_kardex_v("""+fechainiEnero+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','customer')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+str(parametros.location_existencias_pet.id)+ """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
			""")
		rep_ingreso = 0
		rep_debit = 0
		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','customer')]):
				if i[2] == ii.id or i[3] == ii.id :
					rep_ingreso += i[0]
					rep_debit += i[1]
		rep_cp = 0 if rep_ingreso == 0 else rep_debit / rep_ingreso

		tmp.append(rep_ingreso)
		tmp.append(rep_cp)
		tmp.append(rep_debit)

		rpt.append(tmp)


		### la linea 10 inventory 

		tmp = []

		var_txt_con = """
			select (ingreso) as ingreso,(round(debit,2)) as credit, ubicacion_destino, ubicacion_origen from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','inventory')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+str(parametros.location_existencias_pet.id)+ """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
			""")

		rep_ingreso = 0
		rep_debit = 0
		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','inventory')]):
				if i[2] == ii.id or i[3] == ii.id :
					rep_ingreso += i[0]
					rep_debit += i[1]
		rep_cp = 0 if rep_ingreso == 0 else rep_debit / rep_ingreso

		tmp.append(rep_ingreso)
		tmp.append(rep_cp)
		tmp.append(rep_debit)




		var_txt_con = """
			select (ingreso) as ingreso,(round(debit,2)) as credit, ubicacion_destino, ubicacion_origen from get_kardex_v("""+fechainiEnero+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
			'{"""

		flag_c = 0
		for i in self.env['stock.location'].search([('usage','=','inventory')]):
			if flag_c == 0:
				var_txt_con += str(i.id)
			else:
				var_txt_con += ',' + str(i.id)
			flag_c += 1

		self.env.cr.execute( var_txt_con +','+str(parametros.location_existencias_pet.id)+ """}') 
			where ( ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
			or ( ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
			""")
		rep_ingreso = 0
		rep_debit = 0
		for i in self.env.cr.fetchall():
			for ii in self.env['stock.location'].search([('usage','=','inventory')]):
				if i[2] == ii.id or i[3] == ii.id :
					rep_ingreso += i[0]
					rep_debit += i[1]
		rep_cp = 0 if rep_ingreso == 0 else rep_debit / rep_ingreso

		tmp.append(rep_ingreso)
		tmp.append(rep_cp)
		tmp.append(rep_debit)

		rpt.append(tmp)


		### la linea 11 otras salidas
		rpt.append([0,0,0,0,0,0])

		### la linea 12 inventario final

		tmp=[]
		self.env.cr.execute(""" 
			select saldof as ingreso, saldov as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_pet.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
			""")

		rep_ingreso = 0
		rep_debit = 0

		for i in self.env.cr.fetchall():
			rep_ingreso = i[0]
			rep_debit = i[1]

		rep_cp = 0 if rep_ingreso == 0 else rep_debit / rep_ingreso

		tmp.append(rep_ingreso)
		tmp.append(rep_cp)
		tmp.append(rep_debit)


		self.env.cr.execute(""" 
			select saldof as ingreso, saldov as credit from get_kardex_v("""+fechainiEnero+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
			'{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_pet.id) + """}') 
			where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
			or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
			""")

		rep_ingreso = 0
		rep_debit = 0

		for i in self.env.cr.fetchall():
			rep_ingreso = i[0]
			rep_debit = i[1]

		rep_cp = 0 if rep_ingreso == 0 else rep_debit / rep_ingreso

		tmp.append(rep_ingreso)
		tmp.append(rep_cp)
		tmp.append(rep_debit)
		rpt.append(tmp)



		### recalcular inventario inicial [2]

		rpt[2][0] = (rpt[6][0] - rpt[9][0] + rpt[11][0] - rpt[1][0]) if rpt[6][0] - rpt[9][0] + rpt[11][0] - rpt[1][0] >=0.05 else 0
		rpt[2][2] = (rpt[6][2] - rpt[9][2] + rpt[11][2] - rpt[1][2]) if rpt[6][2] - rpt[9][2] + rpt[11][2] - rpt[1][2] >=0.05 else 0
		rpt[2][1] = 0 if rpt[2][0] == 0 else  float (rpt[2][2]/ rpt[2][0])
		rpt[2][3] = (rpt[6][3] - rpt[9][3] + rpt[11][3] - rpt[1][3]) if rpt[6][3] - rpt[9][3] + rpt[11][3] - rpt[1][3] >=0.05 else 0
		rpt[2][5] = (rpt[6][5] - rpt[9][5] + rpt[11][5] - rpt[1][5]) if rpt[6][5] - rpt[9][5] + rpt[11][5] - rpt[1][5] >=0.05 else 0
		rpt[2][4] = 0 if rpt[2][3] == 0 else  float (rpt[2][5]/ rpt[2][3])

		### recalcular disponible  [4]

		rpt[4][0] =  rpt[1][0] + rpt[2][0] +rpt[3][0]
		rpt[4][2] =  rpt[1][2] + rpt[2][2] +rpt[3][2]
		rpt[4][1] = 0 if rpt[4][0] == 0 else  float (rpt[4][2]/ rpt[4][0])
		rpt[4][3] =  rpt[1][3] + rpt[2][3] +rpt[3][3]
		rpt[4][5] =  rpt[1][5] + rpt[2][5] +rpt[3][5]
		rpt[4][4] = 0 if rpt[4][3] == 0 else  float (rpt[4][5]/ rpt[4][3])

		return rpt


	@api.one
	def get_valores(self):
		rpt = []
		arr = []
		val = []
		parametros = self.env['main.parameter'].search([])[0]
		for i in range(12):
			fech = calendar.monthrange(int(self.fiscal.name), i+1)
			arr.append((self.fiscal.name+'-'+("%2d"%(i+1)).replace(' ','0')+'-01', self.fiscal.name+'-'+("%2d"%(i+1)).replace(' ','0')+'-'+str(fech[1])))
		for i in arr:
			fechaini = str(i[0]).replace('-','')
			fechafin = str(i[1]).replace('-','')

			self.env.cr.execute(""" 
			   select sum(ingreso) as ingreso,sum(round(credit,2)) as credit from get_kardex_v("""+fechaini+""","""+fechafin+""",'{""" + str(parametros.pproduct_costos_pet.id) + """}',
			   '{""" + str(parametros.location_virtual_produccion.id) + """,""" + str(parametros.location_existencias_pet.id) + """}') 
			   where (ubicacion_origen = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_destino = """ + str(parametros.location_existencias_pet.id) + """)
			   or (ubicacion_destino = """ + str(parametros.location_virtual_produccion.id) + """ and ubicacion_origen = """ + str(parametros.location_existencias_pet.id) + """)
			""")
			num_tmp = 0
			for w in self.env.cr.fetchall():
				num_tmp = w[0]
			if num_tmp == None:
				num_tmp = 0
			val.append(num_tmp)
		rpt.append(val)
		for i in range(5):
			rpt.append([0,0,0,0,0,0,0,0,0,0,0,0])

		tmp = []
		for k in range(12):

			self.env.cr.execute( """
				select cuenta,sum(round(debe-haber,2)) from get_reporte_hoja_registro_2(false,"""+self.fiscal.name+(("%2d"%(k+1)).replace(' ','0'))+ ""","""+self.fiscal.name+(("%2d"%(k+1)).replace(' ','0'))+ """)
				where cuenta like '""" + "9211.4.01" + """%'
				group by cuenta """)
			num_tmp = 0
			for w in self.env.cr.fetchall():
				num_tmp = w[1]
			tmp.append(num_tmp)
		rpt.append(tmp)

		tmp = []
		for k in range(12):

			self.env.cr.execute( """
				select cuenta,sum(round(debe-haber,2)) from get_reporte_hoja_registro_2(false,"""+self.fiscal.name+(("%2d"%(k+1)).replace(' ','0'))+ ""","""+self.fiscal.name+(("%2d"%(k+1)).replace(' ','0'))+ """)
				where cuenta like '""" + "9211.4.03" + """%'
				group by cuenta """)
			num_tmp = 0
			for w in self.env.cr.fetchall():
				num_tmp = w[1]
			tmp.append(num_tmp)
		rpt.append(tmp)

		tmp = []
		for k in range(12):

			self.env.cr.execute( """
				select cuenta,sum(round(debe-haber,2)) from get_reporte_hoja_registro_2(false,"""+self.fiscal.name+(("%2d"%(k+1)).replace(' ','0'))+ ""","""+self.fiscal.name+(("%2d"%(k+1)).replace(' ','0'))+ """)
				where cuenta like '""" + "9210.4.01" + """%'
				group by cuenta """)
			num_tmp = 0
			for w in self.env.cr.fetchall():
				num_tmp = w[1]
			tmp.append(num_tmp)
		rpt.append(tmp)

		tmp = []
		for k in range(12):

			self.env.cr.execute( """
				select cuenta,sum(round(debe-haber,2)) from get_reporte_hoja_registro_2(false,"""+self.fiscal.name+(("%2d"%(k+1)).replace(' ','0'))+ ""","""+self.fiscal.name+(("%2d"%(k+1)).replace(' ','0'))+ """)
				where cuenta like '""" + "9210.4.02" + """%'
				group by cuenta """)
			num_tmp = 0
			for w in self.env.cr.fetchall():
				num_tmp = w[1]
			tmp.append(num_tmp)
		rpt.append(tmp)

		tmp = []
		for k in range(12):

			self.env.cr.execute( """
				select cuenta,sum(round(debe-haber,2)) from get_reporte_hoja_registro_2(false,"""+self.fiscal.name+(("%2d"%(k+1)).replace(' ','0'))+ ""","""+self.fiscal.name+(("%2d"%(k+1)).replace(' ','0'))+ """)
				where cuenta like '""" + "9210.4.05" + """%'
				group by cuenta """)
			num_tmp = 0
			for w in self.env.cr.fetchall():
				num_tmp = w[1]
			tmp.append(num_tmp)
		rpt.append(tmp)

		for conteo in range(len(rpt)):
			for lml in range(int(self.period_actual.code.split('/')[0]),12):
				print conteo, lml
				rpt[conteo][lml]=0
		return rpt

	""" ----------------------------- REPORTE EXCEL ----------------------------- """

	@api.multi
	def export_excel(self):
		import io
		from xlsxwriter.workbook import Workbook

		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')

		output = io.BytesIO()
		########### PRIMERA HOJA DE LA DATA EN TABLA
		#workbook = Workbook(output, {'in_memory': True})

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		if not direccion:
			raise osv.except_osv('Alerta!', u"No fue configurado el directorio para los archivos en Configuracion.")

		workbook = Workbook(direccion +'Reporte_Pet.xlsx')
		worksheet = workbook.add_worksheet(u"PET")
		bold = workbook.add_format({'bold': True})
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(9)
		boldbord.set_bg_color('#DCE6F1')
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'#,##0.00'})
		bord = workbook.add_format()
		bord.set_border(style=1)
		numberdos.set_border(style=1)
		numbertres.set_border(style=1)	

		numberdoscon = workbook.add_format({'num_format':'#,##0.00'})

		boldtotal = workbook.add_format({'bold': True})
		boldtotal.set_align('right')
		boldtotal.set_align('vright')

		merge_format = workbook.add_format({
											'bold': 1,
											'border': 1,
											'align': 'center',
											'valign': 'vcenter',
											})	
		merge_format.set_bg_color('#DCE6F1')
		merge_format.set_text_wrap()
		merge_format.set_font_size(9)

		bordredtext = workbook.add_format()
		bordredtext.set_font_color('red')

		m = str(self.period_actual.code).split('/')
		m = int(m[0])
		doce = 12

		worksheet.insert_image('C2', 'calidra.jpg')
		worksheet.write(1,8, u'ANEXO DE OPERACIÓN {0}'.format(self.fiscal.name), bold)
		worksheet.write(2,8, 'Sitio:', bold)
		worksheet.write(2,12, self.sitio if self.sitio else '', normal)
		worksheet.write(3,8, 'Centro de Costo:', bold)
		worksheet.write(3,12, self.centro_de_costo if self.centro_de_costo else '', normal)
		worksheet.write(4,8, u'Propósito:', bold)
		worksheet.write(4,12, self.proposito if self.proposito else '', normal)
		worksheet.write(5,8, u'Fecha de Emisión del Reporte:', bold)
		worksheet.write(5,12, self.fecha_emision_reporte if self.fecha_emision_reporte else '', normal)
		worksheet.write(6,8, 'Usuario:', bold)
		worksheet.write(6,12, self.usuario.name if self.usuario.name else '', normal)

		colum = {
			1: "Enero",
			2: "Febrero",
			3: "Marzo",
			4: "Abril",
			5: "Mayo",
			6: "Junio",
			7: "Julio",
			8: "Agosto",
			9: "Septiembre",
			10: "Octubre",
			11: "Noviembre",
			12: "Diciembre",
		}

		worksheet.write(14,0, u'TIPO COSTO', boldbord)
		worksheet.write(14,1, u'Porcentaje', boldbord)
		col = 2
		mon = 0
		while mon+1 <= doce:
			worksheet.write(14,col, u'{0}'.format(colum[mon+1]), boldbord)
			col += 1
			mon += 1
		worksheet.write(14,col, u'Acumulado', boldbord)
		col+=1
		worksheet.write(14,col, u'%  ACUM', boldbord)
		col+=1
		worksheet.write(14,col, u'Promedio', boldbord)
		col+=1
		worksheet.write(14,col, u'%  PROM', boldbord)
		col+=1
		
		elements = self.env['rm.report.pet.line'].search([('rm_report_pet_id','=',self.id)]).sorted(key=lambda r: dig_5(r.tipo.order)+dig_5(r.grupo.order))
		flag = True
		n_grupo = None
		n_tipo = None
		ultimo_elem = None

		sub_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tot_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tot_tot_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

		x= 15
		for i in elements:
			if n_tipo == None:
				n_tipo = i.tipo
				worksheet.write(x,0, u'{0}'.format(i.tipo.titulo), bold)
				x += 1
			if n_grupo == None:
				n_grupo = i.grupo
				worksheet.write(x,0, u'{0}'.format(i.grupo.titulo), bold)
				x += 1
			if n_tipo != i.tipo:
				worksheet.write(x,0, u'SUB TOTAL', boldtotal)
				col = 2
				mon = 0
				while mon+1 <= doce:
					worksheet.write(x,col, ((sub_tot[mon])), numberdos)
					col += 1
					mon += 1
				worksheet.write(x,col, ((sub_tot[-4])), numberdos)
				col += 1
				worksheet.write(x,col, ((sub_tot[-3])), numberdos)
				col += 1
				worksheet.write(x,col, ((sub_tot[-2])), numberdos)
				col += 1
				worksheet.write(x,col, ((sub_tot[-1])), numberdos)

				tot_tot[0] += sub_tot[0]
				tot_tot[1] += sub_tot[1]
				tot_tot[2] += sub_tot[2]
				tot_tot[3] += sub_tot[3]
				tot_tot[4] += sub_tot[4]
				tot_tot[5] += sub_tot[5]
				tot_tot[6] += sub_tot[6]
				tot_tot[7] += sub_tot[7]
				tot_tot[8] += sub_tot[8]
				tot_tot[9] += sub_tot[9]
				tot_tot[10] += sub_tot[10]
				tot_tot[11] += sub_tot[11]
				tot_tot[12] += sub_tot[12]
				tot_tot[13] += sub_tot[13]
				tot_tot[14] += sub_tot[14]
				tot_tot[15] += sub_tot[15]
				tot_tot_tot[0] += tot_tot[0]
				tot_tot_tot[1] += tot_tot[1]
				tot_tot_tot[2] += tot_tot[2]
				tot_tot_tot[3] += tot_tot[3]
				tot_tot_tot[4] += tot_tot[4]
				tot_tot_tot[5] += tot_tot[5]
				tot_tot_tot[6] += tot_tot[6]
				tot_tot_tot[7] += tot_tot[7]
				tot_tot_tot[8] += tot_tot[8]
				tot_tot_tot[9] += tot_tot[9]
				tot_tot_tot[10] += tot_tot[10]
				tot_tot_tot[11] += tot_tot[11]
				tot_tot_tot[12] += tot_tot[12]
				tot_tot_tot[13] += tot_tot[13]
				tot_tot_tot[14] += tot_tot[14]
				tot_tot_tot[15] += tot_tot[15]

				x += 1
				worksheet.write(x,0, u"TOTAL " + n_tipo.titulo.upper(), boldtotal)
				col = 2
				mon = 0
				while mon+1 <= doce:
					worksheet.write(x,col, ((tot_tot[mon])), numberdos)
					col += 1
					mon += 1
				worksheet.write(x,col, ((tot_tot[-4])), numberdos)
				col += 1
				worksheet.write(x,col, ((tot_tot[-3])), numberdos)
				col += 1
				worksheet.write(x,col, ((tot_tot[-2])), numberdos)
				col += 1
				worksheet.write(x,col, ((tot_tot[-1])), numberdos)
				col += 1

				sub_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
				tot_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

				x += 1
				worksheet.write(x,0, u'{0}'.format(i.tipo.titulo), bold)
				x += 1
				worksheet.write(x,0, u'{0}'.format(i.grupo.titulo), bold)
				x += 1
				worksheet.write(x,0, u'{0}'.format(i.concepto), normal)
				worksheet.write(x,1, u'{0} %'.format(int(i.porcentaje)), bordredtext)
				mon_m = {
					0: i.enero * i.porcentaje/float(100),
					1: i.febrero * i.porcentaje/float(100),
					2: i.marzo * i.porcentaje/float(100),
					3: i.abril * i.porcentaje/float(100),
					4: i.mayo * i.porcentaje/float(100),
					5: i.junio * i.porcentaje/float(100),
					6: i.julio * i.porcentaje/float(100),
					7: i.agosto * i.porcentaje/float(100),
					8: i.septiembre * i.porcentaje/float(100),
					9: i.octubre * i.porcentaje/float(100),
					10: i.noviembre * i.porcentaje/float(100),
					11: i.diciembre * i.porcentaje/float(100),
				}
				col = 2
				mon = 0
				while mon+1 <= doce:
					worksheet.write(x,col, ((mon_m[mon])), numberdoscon)
					col += 1
					mon += 1
				worksheet.write(x,col, ((i.acumulado)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.acumulado_pciento)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.promedio)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.promedio_pciento)), numberdoscon)

				sub_tot[0] += i.enero * i.porcentaje/float(100)
				sub_tot[1] += i.febrero * i.porcentaje/float(100)
				sub_tot[2] += i.marzo * i.porcentaje/float(100)
				sub_tot[3] += i.abril * i.porcentaje/float(100)
				sub_tot[4] += i.mayo * i.porcentaje/float(100)
				sub_tot[5] += i.junio * i.porcentaje/float(100)
				sub_tot[6] += i.julio * i.porcentaje/float(100)
				sub_tot[7] += i.agosto * i.porcentaje/float(100)
				sub_tot[8] += i.septiembre * i.porcentaje/float(100)
				sub_tot[9] += i.octubre * i.porcentaje/float(100)
				sub_tot[10] += i.noviembre * i.porcentaje/float(100)
				sub_tot[11] += i.diciembre * i.porcentaje/float(100)
				sub_tot[12] += i.acumulado
				sub_tot[13] += i.acumulado_pciento
				sub_tot[14] += i.promedio
				sub_tot[15] += i.promedio_pciento
				x += 1
				n_grupo = i.grupo
				n_tipo = i.tipo
			elif n_grupo != i.grupo:
				worksheet.write(x,0, u'SUB TOTAL', boldtotal)
				col = 2
				mon = 0
				while mon+1 <= doce:
					worksheet.write(x,col, ((sub_tot[mon])), numberdos)
					col += 1
					mon += 1
				worksheet.write(x,col, ((sub_tot[-4])), numberdos)
				col += 1
				worksheet.write(x,col, ((sub_tot[-3])), numberdos)
				col += 1
				worksheet.write(x,col, ((sub_tot[-2])), numberdos)
				col += 1
				worksheet.write(x,col, ((sub_tot[-1])), numberdos)
				
				tot_tot[0] += sub_tot[0]
				tot_tot[1] += sub_tot[1]
				tot_tot[2] += sub_tot[2]
				tot_tot[3] += sub_tot[3]
				tot_tot[4] += sub_tot[4]
				tot_tot[5] += sub_tot[5]
				tot_tot[6] += sub_tot[6]
				tot_tot[7] += sub_tot[7]
				tot_tot[8] += sub_tot[8]
				tot_tot[9] += sub_tot[9]
				tot_tot[10] += sub_tot[10]
				tot_tot[11] += sub_tot[11]
				tot_tot[12] += sub_tot[12]
				tot_tot[13] += sub_tot[13]
				tot_tot[14] += sub_tot[14]
				tot_tot[15] += sub_tot[15]
				sub_tot = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
				x += 1
				worksheet.write(x,0, u'{0}'.format(i.grupo.titulo), bold)
				x += 1
				
				worksheet.write(x,0, u'{0}'.format(i.concepto), normal)
				worksheet.write(x,1, u'{0} %'.format(int(i.porcentaje)), bordredtext)
				mon_m = {
					0: i.enero * i.porcentaje/float(100),
					1: i.febrero * i.porcentaje/float(100),
					2: i.marzo * i.porcentaje/float(100),
					3: i.abril * i.porcentaje/float(100),
					4: i.mayo * i.porcentaje/float(100),
					5: i.junio * i.porcentaje/float(100),
					6: i.julio * i.porcentaje/float(100),
					7: i.agosto * i.porcentaje/float(100),
					8: i.septiembre * i.porcentaje/float(100),
					9: i.octubre * i.porcentaje/float(100),
					10: i.noviembre * i.porcentaje/float(100),
					11: i.diciembre * i.porcentaje/float(100),
				}
				col = 2
				mon = 0
				while mon+1 <= doce:
					worksheet.write(x,col, ((mon_m[mon])), numberdoscon)
					col += 1
					mon += 1
				worksheet.write(x,col, ((i.acumulado)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.acumulado_pciento)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.promedio)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.promedio_pciento)), numberdoscon)
				
				sub_tot[0] += i.enero * i.porcentaje/float(100)
				sub_tot[1] += i.febrero * i.porcentaje/float(100)
				sub_tot[2] += i.marzo * i.porcentaje/float(100)
				sub_tot[3] += i.abril * i.porcentaje/float(100)
				sub_tot[4] += i.mayo * i.porcentaje/float(100)
				sub_tot[5] += i.junio * i.porcentaje/float(100)
				sub_tot[6] += i.julio * i.porcentaje/float(100)
				sub_tot[7] += i.agosto * i.porcentaje/float(100)
				sub_tot[8] += i.septiembre * i.porcentaje/float(100)
				sub_tot[9] += i.octubre * i.porcentaje/float(100)
				sub_tot[10] += i.noviembre * i.porcentaje/float(100)
				sub_tot[11] += i.diciembre * i.porcentaje/float(100)
				sub_tot[12] += i.acumulado
				sub_tot[13] += i.acumulado_pciento
				sub_tot[14] += i.promedio
				sub_tot[15] += i.promedio_pciento
				x += 1
				n_grupo = i.grupo
			else:
				
				worksheet.write(x,0, u'{0}'.format(i.concepto), normal)
				worksheet.write(x,1, u'{0} %'.format(int(i.porcentaje)), bordredtext)
				mon_m = {
					0: i.enero * i.porcentaje/float(100),
					1: i.febrero * i.porcentaje/float(100),
					2: i.marzo * i.porcentaje/float(100),
					3: i.abril * i.porcentaje/float(100),
					4: i.mayo * i.porcentaje/float(100),
					5: i.junio * i.porcentaje/float(100),
					6: i.julio * i.porcentaje/float(100),
					7: i.agosto * i.porcentaje/float(100),
					8: i.septiembre * i.porcentaje/float(100),
					9: i.octubre * i.porcentaje/float(100),
					10: i.noviembre * i.porcentaje/float(100),
					11: i.diciembre * i.porcentaje/float(100),
				}
				col = 2
				mon = 0
				while mon+1 <= doce:
					worksheet.write(x,col, ((mon_m[mon])), numberdoscon)
					col += 1
					mon += 1
				worksheet.write(x,col, ((i.acumulado)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.acumulado_pciento)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.promedio)), numberdoscon)
				col += 1
				worksheet.write(x,col, ((i.promedio_pciento)), numberdoscon)
				
				sub_tot[0] += i.enero * i.porcentaje/float(100)
				sub_tot[1] += i.febrero * i.porcentaje/float(100)
				sub_tot[2] += i.marzo * i.porcentaje/float(100)
				sub_tot[3] += i.abril * i.porcentaje/float(100)
				sub_tot[4] += i.mayo * i.porcentaje/float(100)
				sub_tot[5] += i.junio * i.porcentaje/float(100)
				sub_tot[6] += i.julio * i.porcentaje/float(100)
				sub_tot[7] += i.agosto * i.porcentaje/float(100)
				sub_tot[8] += i.septiembre * i.porcentaje/float(100)
				sub_tot[9] += i.octubre * i.porcentaje/float(100)
				sub_tot[10] += i.noviembre * i.porcentaje/float(100)
				sub_tot[11] += i.diciembre * i.porcentaje/float(100)
				sub_tot[12] += i.acumulado
				sub_tot[13] += i.acumulado_pciento
				sub_tot[14] += i.promedio
				sub_tot[15] += i.promedio_pciento
				x += 1

			ultimo_elem = i
			
		tot_tot[0] += sub_tot[0]
		tot_tot[1] += sub_tot[1]
		tot_tot[2] += sub_tot[2]
		tot_tot[3] += sub_tot[3]
		tot_tot[4] += sub_tot[4]
		tot_tot[5] += sub_tot[5]
		tot_tot[6] += sub_tot[6]
		tot_tot[7] += sub_tot[7]
		tot_tot[8] += sub_tot[8]
		tot_tot[9] += sub_tot[9]
		tot_tot[10] += sub_tot[10]
		tot_tot[11] += sub_tot[11]
		tot_tot[12] += sub_tot[12]
		tot_tot[13] += sub_tot[13]
		tot_tot[14] += sub_tot[14]
		tot_tot[15] += sub_tot[15]

		tot_tot_tot[0] += tot_tot[0]
		tot_tot_tot[1] += tot_tot[1]
		tot_tot_tot[2] += tot_tot[2]
		tot_tot_tot[3] += tot_tot[3]
		tot_tot_tot[4] += tot_tot[4]
		tot_tot_tot[5] += tot_tot[5]
		tot_tot_tot[6] += tot_tot[6]
		tot_tot_tot[7] += tot_tot[7]
		tot_tot_tot[8] += tot_tot[8]
		tot_tot_tot[9] += tot_tot[9]
		tot_tot_tot[10] += tot_tot[10]
		tot_tot_tot[11] += tot_tot[11]
		tot_tot_tot[12] += tot_tot[12]
		tot_tot_tot[13] += tot_tot[13]
		tot_tot_tot[14] += tot_tot[14]
		tot_tot_tot[15] += tot_tot[15]

		worksheet.write(x,0, u'SUB TOTAL', boldtotal)
		col = 2
		mon = 0
		while mon+1 <= doce:
			worksheet.write(x,col, ((sub_tot[mon])), numberdos)
			col += 1
			mon += 1
		worksheet.write(x,col, ((sub_tot[-4])), numberdos)
		col += 1
		worksheet.write(x,col, ((sub_tot[-3])), numberdos)
		col += 1
		worksheet.write(x,col, ((sub_tot[-2])), numberdos)
		col += 1
		worksheet.write(x,col, ((sub_tot[-1])), numberdos)
		x += 1

		worksheet.write(x,0, u"TOTAL " + n_tipo.titulo.upper(), boldtotal)
		col = 2
		mon = 0
		while mon+1 <= doce:
			worksheet.write(x,col, ((tot_tot[mon])), numberdos)
			col += 1
			mon += 1
		worksheet.write(x,col, ((tot_tot[-4])), numberdos)
		col += 1
		worksheet.write(x,col, ((tot_tot[-3])), numberdos)
		col += 1
		worksheet.write(x,col, ((tot_tot[-2])), numberdos)
		col += 1
		worksheet.write(x,col, ((tot_tot[-1])), numberdos)
		col += 1
		x += 1

		worksheet.write(x,0, u"COSTO TOTAL DEL PROCESO", boldtotal)
		col = 2
		mon = 0
		while mon+1 <= doce:
			worksheet.write(x,col, ((tot_tot_tot[mon])), numberdos)
			col += 1
			mon += 1
		worksheet.write(x,col, ((tot_tot_tot[-4])), numberdos)
		col += 1
		worksheet.write(x,col, ((tot_tot_tot[-3])), numberdos)
		col += 1
		worksheet.write(x,col, ((tot_tot_tot[-2])), numberdos)
		col += 1
		worksheet.write(x,col, ((tot_tot_tot[-1])), numberdos)
		col += 1
		x += 1

		t = 11.86
		worksheet.set_column('A:A', 49)
		worksheet.set_column('B:B', t)
		worksheet.set_column('C:C', t)
		worksheet.set_column('D:D', t)
		worksheet.set_column('E:E', t)
		worksheet.set_column('F:F', t)
		worksheet.set_column('G:G', t)
		worksheet.set_column('H:H', t)
		worksheet.set_column('I:I', t)
		worksheet.set_column('J:J', t)
		worksheet.set_column('K:K', t)
		worksheet.set_column('L:L', t)
		worksheet.set_column('M:M', t)
		worksheet.set_column('N:N', t)
		worksheet.set_column('O:O', t)
		worksheet.set_column('P:P', t)
		worksheet.set_column('Q:Q', t)


		x += 2
		worksheet.write(x,0, u'Otros datos Informativos'.format(i.tipo.titulo), bold)
		x += 1

		nombres = ["TONELADAS PRODUCIDAS","COSTO PROCESO POR TONELADA", "COSTO POR TONELADA SIN EXPLOSIVOS", "COSTO DE EXPLOSIVOS", "COSTO LABORATORIO POR TON.", u"COSTO POR TON. SIN DEPRECIACIÓN"]
		valores = [[0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0]]
		valores = self.get_valores()[0]
		for k in range(12):
			if valores[0][k] == 0:
				valores[1][k] = 0
				valores[2][k] = 0
				valores[3][k] = 0
				valores[4][k] = 0
				valores[5][k] = 0
			else:
				valores[1][k] = tot_tot_tot[k] / valores[0][k]
				valores[2][k] = (tot_tot_tot[k] - valores[6][k])/valores[0][k]
				valores[3][k] = valores[6][k] / valores[0][k]
				valores[4][k] = valores[7][k] / valores[0][k]
				valores[5][k] = (tot_tot_tot[k] - (valores[8][k] + valores[9][k] + valores[10][k]))/valores[0][k]

		
		worksheet.write(x,0, u'CONCEPTO', boldbord)
		col = 1
		mon = 0
		while mon+1 <= doce:
			worksheet.write(x,col, u'{0}'.format(colum[mon+1]), boldbord)
			col += 1
			mon += 1

		x += 1


		for i in range(0,6):
			worksheet.write(x,0, u'{0}'.format(nombres[i]), normal)
			col = 1
			mon = 0
			while mon+1 <= doce:
				worksheet.write(x,col, ((valores[i][mon])), numberdoscon)
				col += 1
				mon += 1
			x += 1

		x += 2
		worksheet.write(x,0, u'Pie de Página', bold)
		x += 1
		worksheet.merge_range(x,0,x+1,0, u'CONCEPTO', merge_format)
		worksheet.merge_range(x,1,x,3, u'MES ACTUAL', merge_format)
		worksheet.merge_range(x,4,x,6, u'ACUMULADO', merge_format)
		x += 1
		worksheet.write(x,1, u'TONS', boldbord)
		worksheet.write(x,2, u'PROMEDIO', boldbord)
		worksheet.write(x,3, u'IMPORTE', boldbord)
		worksheet.write(x,4, u'TONS', boldbord)
		worksheet.write(x,5, u'PROMEDIO', boldbord)
		worksheet.write(x,6, u'IMPORTE', boldbord)
		x += 1

		nombres = ["TRASPASO PROCESO ANTERIOR","PRODUCCION COSTO POR TONELADA","INVENTARIO INICIAL","COMPRAS","DISPONIBLE","ENVIO TR","TRASPASO A TRITURACION","TRASPASO A AGREGADOS","VENTAS","AJUSTE DE INVENTARIO","OTRAS SALIDAS","INVENTARIO FINAL"]
		
		data_final_pagina = self.get_pie_pagina()[0]

		for i in range(12):
			worksheet.write(x,0, nombres[i], normal)
			worksheet.write(x,1, ((data_final_pagina[i][0])), numberdoscon)
			worksheet.write(x,2, ((data_final_pagina[i][1])), numberdoscon)
			worksheet.write(x,3, ((data_final_pagina[i][2])), numberdoscon)
			worksheet.write(x,4, ((data_final_pagina[i][3])), numberdoscon)
			worksheet.write(x,5, ((data_final_pagina[i][4])), numberdoscon)
			worksheet.write(x,6, ((data_final_pagina[i][5])), numberdoscon)
			x += 1

		workbook.close()
		
		f = open(direccion + 'Reporte_Pet.xlsx', 'rb')
		
		vals = {
			'output_name': 'Reportes_Mexicanos_Pet.xlsx',
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

	""" ----------------------------- REPORTE EXCEL ----------------------------- """