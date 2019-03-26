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

class grupo_report_nuevesiete(models.Model):
	_name = 'grupo.report.nuevesiete'

	titulo = fields.Char('Name',required=True)
	order = fields.Integer('Order',required=True)

	@api.one
	def get_name_person(self):
		self.name = str(self.order) + '-' + self.titulo

	name = fields.Char('Name',compute="get_name_person")


class tipo_report_nuevesiete(models.Model):
	_name = 'tipo.report.nuevesiete'

	titulo = fields.Char('Name',required=True)
	order = fields.Integer('Order',required=True)

	@api.one
	def get_name_person(self):
		self.name = str(self.order) + '-' + self.titulo

	name = fields.Char('Name',compute="get_name_person")


class rm_report_nuevesiete_line(models.Model):
	_name = 'rm.report.nuevesiete.line'


	rm_report_nuevesiete_id = fields.Many2one('rm.report.nuevesiete','Cabezera')

		

	cuenta = fields.Char('Cuenta',required=False)
	tipo = fields.Many2one('tipo.report.nuevesiete','Tipo',required=True)
	concepto = fields.Char('Concepto',required=True)
	grupo = fields.Many2one('grupo.report.nuevesiete','Grupo',required=True)

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

	@api.one
	def get_monto(self):
		m = str(self.rm_report_nuevesiete_id.period_actual.code).split('/')
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
		mont = cant[int(self.rm_report_nuevesiete_id.period_actual.code.split('/')[0])]
		self.monto = mont
	monto = fields.Float('Monto', digits=(12,2), readonly=True, default=0, compute="get_monto")

	@api.one
	def get_acumulado(self):
		self.acumulado = self.enero + self.febrero + self.marzo + self.abril + self.mayo + self.junio + self.julio + self.agosto + self.septiembre + self.octubre + self.noviembre + self.diciembre
	acumulado = fields.Float('Acumulado', readonly=True, default=0, compute="get_acumulado")

	@api.one
	def get_acumulado_pciento(self):
		if self.acumulado != 0:
			self.acumulado_pciento = self.acumulado / self.rm_report_nuevesiete_id.total_general
		else:
			self.acumulado_pciento = 0
	acumulado_pciento = fields.Float('%  ACUM', readonly=True, compute="get_acumulado_pciento")

	@api.one
	def get_promedio(self):
		if self.acumulado != 0:
			self.promedio = self.acumulado / 1
		else:
			self.promedio = 0
	promedio = fields.Float('Promedio', readonly=True, compute="get_promedio")

	@api.one
	def get_promedio_pciento(self):
		if self.acumulado != 0:
			self.promedio_pciento = self.promedio / self.rm_report_nuevesiete_id.total_promedio_general
		else:
			self.promedio_pciento = 0
	promedio_pciento = fields.Float('%  PROM', readonly=True, compute="get_promedio_pciento")


class rm_report_nuevesiete(models.Model):
	_name= 'rm.report.nuevesiete'

	fiscal = fields.Many2one('account.fiscalyear','Año Fiscal',required=True)
	sitio = fields.Char('Sitio',required=False)
	centro_de_costo = fields.Char('Centro de Costo',readonly=True,default='97')
	proposito = fields.Char('Propósito')
	fecha_emision_reporte = fields.Date('Fecha de Emisión del Reporte',required=True)
	usuario = fields.Many2one('res.users','Usuario',readonly=True)
	conf_line_ids = fields.One2many('rm.report.nuevesiete.line','rm_report_nuevesiete_id','Lineas de Configuración')
	period_actual = fields.Many2one('account.period','Periodo Actual Informe',required=True)

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
		return super(rm_report_nuevesiete,self).unlink()

	@api.one
	def copy(self,default):
		t= super(rm_report_nuevesiete,self).copy(default)
		for i in self.conf_line_ids:
			vals_i = {
				'rm_report_nuevesiete_id':t.id,
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
			}
			self.env['rm.report.nuevesiete.line'].create(vals_i)
		return t

	@api.one
	def get_name_set(self):
		self.name = self.fiscal.name + '-'+ self.centro_de_costo

	name = fields.Char('Nombre',compute='get_name_set')


	@api.model
	def create(self,vals):
		vals['usuario']= self.env.uid
		return super(rm_report_nuevesiete,self).create(vals)


	@api.one
	def calculate(self):
		m = str(self.period_actual.code).split('/')
		limite = m[1]+ m[0]
		

		self.env.cr.execute("""
update rm_report_nuevesiete_line opt set
enero= 0, febrero = 0,
marzo= 0, abril= 0,
mayo= 0, junio= 0,
julio= 0, agosto= 0,
septiembre= 0, octubre= 0,
noviembre= 0, diciembre= 0
where opt.rm_report_nuevesiete_id = """ + str(self.id) + """
""")


		self.env.cr.execute("""
update rm_report_nuevesiete_line opt set
enero= saldos.saldo01, febrero = saldos.saldo02,
marzo= saldos.saldo03, abril= saldos.saldo04,
mayo= saldos.saldo05, junio= saldos.saldo06,
julio= saldos.saldo07, agosto= saldos.saldo08,
septiembre= saldos.saldo09, octubre= saldos.saldo10,
noviembre= saldos.saldo11, diciembre= saldos.saldo12
from (
select t1.id,t1.code as nivel1,t1.code as nivel2,t1.code as nivel3,t1.code,t1.name,t1.type,
coalesce(saldo01,0) as saldo01,coalesce(saldo02,0) as saldo02,coalesce(saldo03,0) as saldo03,coalesce(saldo04,0) as saldo04,
coalesce(saldo05,0) as saldo05,coalesce(saldo06,0) as saldo06,coalesce(saldo07,0) as saldo07,coalesce(saldo08,0) as saldo08,
coalesce(saldo09,0) as saldo09,coalesce(saldo10,0) as saldo10,coalesce(saldo11,0) as saldo11,coalesce(saldo12,0) as saldo12,
saldo01+saldo02+saldo03+saldo04+saldo05+saldo06+saldo07+saldo08+saldo09+saldo10+saldo11+saldo12 as total from account_account t1
left join (select aa.code as cuenta,sum(debit)-sum(credit) as saldo01 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '01/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by aa.code) t2 on t2.cuenta= t1.code
left join (select aa.code as cuenta,sum(debit)-sum(credit) as saldo02 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '02/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by aa.code) t3 on t3.cuenta= t1.code
left join (select aa.code as cuenta,sum(debit)-sum(credit) as saldo03 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '03/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by aa.code) t4 on t4.cuenta= t1.code
left join (select aa.code as cuenta,sum(debit)-sum(credit) as saldo04 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '04/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by aa.code) t5 on t5.cuenta= t1.code
left join (select aa.code as cuenta,sum(debit)-sum(credit) as saldo05 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '05/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by aa.code) t6 on t6.cuenta= t1.code
left join (select aa.code as cuenta,sum(debit)-sum(credit) as saldo06 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '06/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by aa.code) t7 on t7.cuenta= t1.code
left join (select aa.code as cuenta,sum(debit)-sum(credit) as saldo07 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '07/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by aa.code) t8 on t8.cuenta= t1.code
left join (select aa.code as cuenta,sum(debit)-sum(credit) as saldo08 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '08/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by aa.code) t9 on t9.cuenta= t1.code
left join (select aa.code as cuenta,sum(debit)-sum(credit) as saldo09 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '09/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by aa.code) t10 on t10.cuenta= t1.code
left join (select aa.code as cuenta,sum(debit)-sum(credit) as saldo10 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '10/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by aa.code) t11 on t11.cuenta= t1.code
left join (select aa.code as cuenta,sum(debit)-sum(credit) as saldo11 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '11/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by aa.code) t12 on t12.cuenta= t1.code
left join (select aa.code as cuenta,sum(debit)-sum(credit) as saldo12 from account_move_line aml inner join account_move am on am.id = aml.move_id inner join account_account aa on aa.id = aml.account_id inner join account_period ap on ap.id = am.period_id and ap.date_stop <= '""" +str(self.period_actual.date_stop)+ """'::date and ap.code = '12/""" +str(self.period_actual.code).split('/')[1]+ """' where am.state != 'draft' group by aa.code) t13 on t13.cuenta= t1.code
where t1.type<>'view') saldos
where opt.cuenta = saldos.nivel1 and opt.rm_report_nuevesiete_id = """ + str(self.id) + """
			""")


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

		workbook = Workbook(direccion +'Reporte_97.xlsx')
		worksheet = workbook.add_worksheet(u"97")
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

		boldtotal = workbook.add_format({'bold': True})
		boldtotal.set_align('right')
		boldtotal.set_align('vright')

		boldtotalsum = workbook.add_format({'bold':True,
										   'font_color': 'red'})
		boldtotalsumval = workbook.add_format({'bold':True,
										    'font_color': 'red',
										    'num_format': '0.00'})
		boldsegment = workbook.add_format({'bold':True,
										   'font_color': 'blue'})
		numberdoscon = workbook.add_format({'num_format':'#,##0.00'})
		numberdosconblue = workbook.add_format({'num_format':'#,##0.00','font_color':'blue','bold':True})

		merge_format = workbook.add_format({
											'bold': 1,
											'align': 'center',
											'valign': 'vcenter',
											})
		merge_format.set_text_wrap()
		merge_format.set_font_size(9)

		worksheet.insert_image('C2', 'calidra.jpg')
		worksheet.write(1,5, u'ANEXO DE OPERACIÓN {0}'.format(self.fiscal.name), bold)
		worksheet.write(2,5, 'Sitio:', bold)
		worksheet.write(2,9, self.sitio if self.sitio else '', normal)
		worksheet.write(3,5, 'Centro de Costo:', bold)
		worksheet.write(3,9, self.centro_de_costo if self.centro_de_costo else '', normal)
		worksheet.write(4,5, u'Propósito:', bold)
		worksheet.write(4,9, self.proposito if self.proposito else '', normal)
		worksheet.write(5,5, u'Fecha de Emisión del Reporte:', bold)
		worksheet.write(5,9, self.fecha_emision_reporte if self.fecha_emision_reporte else '', normal)
		worksheet.write(6,5, 'Usuario:', bold)
		worksheet.write(6,9, self.usuario.name if self.usuario.name else '', normal)

		worksheet.write(10,0, u'TOTAL', boldtotalsum)
		worksheet.merge_range(10,1,10,3,'',merge_format)
		
		elements = self.env['rm.report.nuevesiete.line'].search([('rm_report_nuevesiete_id','=',self.id)]).sorted(key=lambda r: r.cuenta)
		x= 11
		segment = ""
		segment_actual = None
		cuenta_puesta = False
		sum_segment = 0
		cont_con = 1
		total = 0
		for i in elements:
			segment = i.cuenta.split('.')[0]
			if segment != segment_actual:
				if segment_actual != None:
					worksheet.write(x - cont_con,3, ((sum_segment)), numberdosconblue)
					worksheet.write(x - cont_con,2, '', numberdosconblue)
					total += sum_segment 
					sum_segment = 0
					cont_con = 1
				segment_actual = segment
				worksheet.write(x,0, u'{0}'.format(segment), boldsegment)
				if segment == '971':
					worksheet.write(x,1, u'Comisiones Bancarias', boldsegment)
				elif segment == '972':
					worksheet.write(x,1, u'Factoraje', boldsegment)
				elif segment == '973':
					worksheet.write(x,1, u'Gastos en operaciones de endeudamiento otros', boldsegment)
				elif segment == '974':
					worksheet.write(x,1, u'Intereses por prestamos instituciones financieras y otras entidades', boldsegment)
				elif segment == '975':
					worksheet.write(x,1, u'intereses por prestamos INTERCOMPAÑIAS', boldsegment)
				elif segment == '977':
					worksheet.write(x,1, u'Perdida por mekdicion de activos pasivos financieros a valor razonable', boldsegment)
				elif segment == '978':
					worksheet.write(x,1, u'Participacion de resultados en entidades relacionadas', boldsegment)
				elif segment == '979':
					worksheet.write(x,1, u'Otros gastos financieros', boldsegment)
				else:
					worksheet.write(x,1, u'', boldsegment)
				worksheet.write(x,4, u'PEN', boldsegment)
				worksheet.write(x,5, u'Vista', boldsegment)
				x += 1
			
			worksheet.write(x,0, u'{0}'.format(i.cuenta), normal)
			worksheet.write(x,1, u'{0}'.format(i.concepto), normal)
			worksheet.write(x,2, ((i.monto)), numberdoscon)
			worksheet.write(x,4, u'PEN', normal)
			worksheet.write(x,5, u'Regular', normal)
			
			sum_segment += i.monto
			x += 1
			cont_con += 1

		worksheet.write(x - cont_con,3, ((sum_segment)), numberdosconblue)
		worksheet.write(x - cont_con,2, '', numberdosconblue)
		total += sum_segment

		worksheet.write(10,4, ((total)), boldtotalsumval)

		worksheet.set_column('A:A', 15.71)
		worksheet.set_column('B:B', 76)
		worksheet.set_column('C:Q', 15.71)

		workbook.close()
		
		f = open(direccion + 'Reporte_97.xlsx', 'rb')
		
		vals = {
			'output_name': 'Reportes_Mexicanos_97.xlsx',
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