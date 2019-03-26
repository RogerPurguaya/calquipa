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

class resumen_patrimonio_line_peruano(models.Model):
	_name = 'resumen.patrimonio.line.peruano'
	
	partidaperuana = fields.Char('Rubro Peruano')
	monto= fields.Float('Moneda Soles',digits=(12,2))
	monto_dolares= fields.Float('Moneda Dolares',digits=(12,2))
	tc= fields.Float('Tipo de Cambio',digits=(12,3))
	patrimonio_id = fields.Many2one('reporte.patrimonio','Padre')
	
class resumen_patrimonio_line(models.Model):
	_name = 'resumen.patrimonio.line'
	
	partida = fields.Char('Rubro Mexicano')
	moi= fields.Float('M.O.I (sol) Moneda de Registro',digits=(12,2))
	tc_ant= fields.Float('T.C. Día Ant. Fecha Adquisición',digits=(12,4))
	dlls= fields.Float('Valor (DLLS) Moneda Funcional',digits=(12,2))
	conver_dlls= fields.Float('Efecto Conversión a DLLS',digits=(12,2))
	tc_ant_mex= fields.Float('T.C. Día Ant. Fecha Adquisición',digits=(12,4))
	valor_mxn= fields.Float('Valor (MXN) Moneda de Reporte',digits=(12,2))
	conver_mxn= fields.Float('Efecto Conversión a MXN',digits=(12,2))
	patrimonio_id = fields.Many2one('reporte.patrimonio','Padre')


class reporte_patrimonio_line(models.Model):
	_name = 'reporte.patrimonio.line'
	
	partida = fields.Char('Rubro Mexicano')
	partidaperuana = fields.Char('Rubro Peruano')
	fecha = fields.Date('Fecha')
	descripcion = fields.Char('Descripción')
	moi= fields.Float('M.O.I (sol) Moneda de Registro',digits=(12,2))
	tc_ant= fields.Float('T.C. Día Ant. Fecha Adquisición',digits=(12,4))
	dlls= fields.Float('Valor (DLLS) Moneda Funcional',digits=(12,2))
	conver_dlls= fields.Float('Efecto Conversión a DLLS',digits=(12,2))
	tc_ant_mex= fields.Float('T.C. Día Ant. Fecha Adquisición',digits=(12,4))
	valor_mxn= fields.Float('Valor (MXN) Moneda de Reporte',digits=(12,2))
	conver_mxn= fields.Float('Efecto Conversión a MXN',digits=(12,2))

	eliminar = fields.Boolean('Importado',copy=False,default=False)
	patrimonio_id = fields.Many2one('reporte.patrimonio','Padre')


class reporte_patrimonio(models.Model):
	_name = 'reporte.patrimonio'

	fiscal_id = fields.Many2one('account.fiscalyear','Año Fiscal',required=True)
	name = fields.Many2one('account.period','Periodo',required=True)
	
	line_ids = fields.One2many('reporte.patrimonio.line','patrimonio_id','Patrimonio')
	resumen_ids = fields.One2many('resumen.patrimonio.line','patrimonio_id','Resumen Patrimonio')

	resumen_ids_peru = fields.One2many('resumen.patrimonio.line.peruano','patrimonio_id','Resumen Patrimonio ')
	csv_import = fields.Binary('CSV Importación')
	
	@api.one
	def copy(self,default=None):
		t =super(reporte_patrimonio,self).copy(default)
		if len(t.line_ids)== 0:
			for i in self.line_ids:
				data = {
				'partida': i.partida,
				'fecha': i.fecha,
				'descripcion': i.descripcion,
				'moi': i.moi,
				'tc_ant': i.tc_ant,
				'dlls': i.dlls,
				'conver_dlls': i.conver_dlls,
				'tc_ant_mex': i.tc_ant_mex,
				'valor_mxn': i.valor_mxn,
				'conver_mxn': i.conver_mxn,
				'patrimonio_id': t.id,
				'eliminar':False,
				}
				self.env['reporte.patrimonio.line'].create(data)


		return t

	@api.one
	def cargar_patrimonio_line(self):

		for i in self.line_ids:
			if i.eliminar:
				i.unlink()

		self.env.cr.execute(""" 
			select rbc.orden, am.date, aml.name,
			aml.credit - aml.debit,
		--	coalesce(rcr.type_sale,1),
			CASE WHEN aml.amount_currency is not null and aml.amount_currency != 0 THEN
			(aml.credit - aml.debit) / -aml.amount_currency else 
			coalesce(rcr.type_sale,1) end,

			CASE WHEN aml.amount_currency is not null and aml.amount_currency != 0 THEN
			-aml.amount_currency else 
			(aml.credit - aml.debit)/coalesce(rcr.type_sale,1) end,

			( CASE WHEN aml.amount_currency is not null and aml.amount_currency != 0 THEN
			-aml.amount_currency else 
			(aml.credit - aml.debit)/coalesce(rcr.type_sale,1) end )-(aml.credit - aml.debit),
			
			coalesce(rcm.tipo_cambio,1),

			(CASE WHEN aml.amount_currency is not null and aml.amount_currency != 0 THEN
			-aml.amount_currency else 
			(aml.credit - aml.debit)/coalesce(rcr.type_sale,1) end )*coalesce(rcm.tipo_cambio,1),
			( (CASE WHEN aml.amount_currency is not null and aml.amount_currency != 0 THEN
			-aml.amount_currency else 
			(aml.credit - aml.debit)/coalesce(rcr.type_sale,1) end )*coalesce(rcm.tipo_cambio,1) ) - (CASE WHEN aml.amount_currency is not null and aml.amount_currency != 0 THEN
			-aml.amount_currency else 
			(aml.credit - aml.debit)/coalesce(rcr.type_sale,1) end )

			from account_move am
			inner join account_move_line aml on aml.move_id = am.id
			inner join account_period ap on ap.id = am.period_id
			inner join account_account aa on aa.id = aml.account_id
			inner join rm_balance_config_mexicano_line rbc on rbc.id = aa.balance_type_mex_id
			left join res_currency rc on rc.name = 'USD'
			left join res_currency_rate rcr on rcr.currency_id = rc.id and rcr.name = am.date
			left join res_currency_mex rcm on rcm.fecha = am.date
			where ap.id = """ +str(self.name.id)+ """ and aa.patrimony_type is not null
			""")

		for obj in self.env.cr.fetchall():
			data = {
			'partida': obj[0],
			'fecha': obj[1],
			'descripcion': obj[2],
			'moi': obj[3],
			'tc_ant': obj[4],
			'dlls': obj[5],
			'conver_dlls': obj[6],
			'tc_ant_mex': obj[7],
			'valor_mxn': obj[8],
			'conver_mxn': obj[9],
			'patrimonio_id': self.id,
			'eliminar':True,
			}
			self.env['reporte.patrimonio.line'].create(data)


	@api.one
	def import_csv(self):
		for i in self.line_ids:
			i.unlink()

		if self.csv_import:
			texto = base64.decodestring(self.csv_import)
			texto = texto.split('\n')

			for i in texto:
				obj = i.split('|')
				data = {
				'partida': obj[0],
				'fecha': obj[1],
				'descripcion': obj[2],
				'moi': float(obj[3]),
				'tc_ant': float(obj[4]),
				'dlls': float(obj[5]),
				'conver_dlls': float(obj[6]),
				'tc_ant_mex': float(obj[7]),
				'valor_mxn': float(obj[8]),
				'conver_mxn': float(obj[9]),
				'patrimonio_id': self.id,
				}
				self.env['reporte.patrimonio.line'].create(data)

	@api.one
	def resumen_generate(self):
		for i in self.resumen_ids:
			i.unlink()

		for i in self.resumen_ids_peru:
			i.unlink()
		tmp = None
		t1 = 0
		t2 = 0
		t3 = 0
		t4 = 0
		t5 = 0
		t6 = 0
		t7 = 0

		for i in self.env['reporte.patrimonio.line'].search( [('patrimonio_id','=',self.id)] ).sorted(lambda r: r.partida):
			if tmp == None:
				tmp = i.partida
				t1 += i.moi
				t2 += i.tc_ant
				t3 += i.dlls
				t4 += i.conver_dlls
				t5 += i.tc_ant_mex
				t6 += i.valor_mxn
				t7 += i.conver_mxn

			elif tmp == i.partida:	
				t1 += i.moi
				t2 += i.tc_ant
				t3 += i.dlls
				t4 += i.conver_dlls
				t5 += i.tc_ant_mex
				t6 += i.valor_mxn
				t7 += i.conver_mxn
			else:
				data = {
				'partida': tmp,
				'moi': t1,
				'tc_ant': t2,
				'dlls': t3,
				'conver_dlls': t4,
				'tc_ant_mex': t5,
				'valor_mxn': t6,
				'conver_mxn': t7,
				'patrimonio_id': self.id,
				}
				self.env['resumen.patrimonio.line'].create(data)

				tmp = None
				t1 = 0
				t2 = 0
				t3 = 0
				t4 = 0
				t5 = 0
				t6 = 0
				t7 = 0

				tmp = i.partida
				t1 += i.moi
				t2 += i.tc_ant
				t3 += i.dlls
				t4 += i.conver_dlls
				t5 += i.tc_ant_mex
				t6 += i.valor_mxn
				t7 += i.conver_mxn

		if tmp != None:
			data = {
			'partida': tmp,
			'moi': t1,
			'tc_ant': t2,
			'dlls': t3,
			'conver_dlls': t4,
			'tc_ant_mex': t5,
			'valor_mxn': t6,
			'conver_mxn': t7,
			'patrimonio_id': self.id,
			}
			self.env['resumen.patrimonio.line'].create(data)




		tmp = None
		t1 = 0
		t2 = 0
		t3 = 0
		t4 = 0
		t5 = 0
		t6 = 0
		t7 = 0

		for i in self.env['reporte.patrimonio.line'].search( [('patrimonio_id','=',self.id)] ).sorted(lambda r: r.partidaperuana):
			if tmp == None:
				tmp = i.partidaperuana
				t1 += i.moi
				t2 += i.dlls
				
			elif tmp == i.partidaperuana:	
				t1 += i.moi
				t2 += i.dlls
			else:
				data = {
				'partidaperuana': tmp,
				'monto': t1,
				'monto_dolares': t2,
				'tc': t1/t2 if t2 != 0 else 0,
				'patrimonio_id': self.id,
				}
				self.env['resumen.patrimonio.line.peruano'].create(data)

				tmp = None
				t1 = 0
				t2 = 0
				t3 = 0
				t4 = 0
				t5 = 0
				t6 = 0
				t7 = 0

				tmp = i.partidaperuana
				t1 += i.moi
				t2 += i.dlls

		if tmp != None:
			data = {
			'partidaperuana': tmp,
			'monto': t1,
			'monto_dolares': t2,
			'tc': t1/t2 if t2 != 0 else 0,
			'patrimonio_id': self.id,
			}
			self.env['resumen.patrimonio.line.peruano'].create(data)
