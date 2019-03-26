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

class resumen_proyecto_line(models.Model):
	_name = 'resumen.proyecto.line'
	
	
	rubro = fields.Char('Rubro')
	moi= fields.Float('M.O.I (sol) Moneda de Registro',digits=(12,2))
	tc_ant= fields.Float('SOL vs USD T.C. Hist (Compra)',digits=(12,4))
	dlls= fields.Float('Valor (DLLS) Moneda Funcional',digits=(12,2))
	conver_dlls= fields.Float('Aj. Efecto Conversión a DLLS',digits=(12,2))
	tc_ant_mex= fields.Float('T.C. HIST. USD vs MXN',digits=(12,4))
	valor_mxn= fields.Float('Valor (MXN) Moneda de Reporte',digits=(12,2))
	conver_mxn= fields.Float('Aj. Efecto Conversión a MXN',digits=(12,2))
	proyecto_id = fields.Many2one('reporte.proyecto','Padre')



class reporte_proyecto_line(models.Model):
	_name = 'reporte.proyecto.line'
	
	tipo = fields.Char('Tipo')
	rubro = fields.Char('Rubro')
	fecha = fields.Date('Fecha Alta Adq.')
	descripcion = fields.Char('Descripción')
	moi= fields.Float('M.O.I (sol) Moneda de Registro',digits=(12,2))
	tc_ant= fields.Float('SOL vs USD T.C. Hist (Compra)',digits=(12,4))
	dlls= fields.Float('Valor (DLLS) Moneda Funcional',digits=(12,2))
	conver_dlls= fields.Float('Aj. Efecto Conversión a DLLS',digits=(12,2))
	tc_ant_mex= fields.Float('T.C. HIST. USD vs MXN',digits=(12,4))
	valor_mxn= fields.Float('Valor (MXN) Moneda de Reporte',digits=(12,2))
	conver_mxn= fields.Float('Aj. Efecto Conversión a MXN',digits=(12,2))
	proyecto_id = fields.Many2one('reporte.proyecto','Padre')


class reporte_proyecto(models.Model):
	_name = 'reporte.proyecto'

	fiscal_id = fields.Many2one('account.fiscalyear','Año Fiscal',required=True)
	name = fields.Many2one('account.period','Periodo',required=True)
	
	line_ids = fields.One2many('reporte.proyecto.line','proyecto_id','proyecto')
	resumen_ids = fields.One2many('resumen.proyecto.line','proyecto_id','Resumen proyecto')
	csv_import = fields.Binary('CSV Importación')
	
	@api.one
	def import_csv(self):
		for i in self.line_ids:
			i.unlink()

		if self.csv_import:
			texto = base64.decodestring(self.csv_import_af)
			texto = texto.split('\n')

			for i in texto:
				obj = i.split('|')
				data = {
				'tipo': obj[0],
				'rubro': obj[1],
				'fecha': obj[2],
				'descripcion': obj[3],
				'moi': float(obj[4]),
				'tc_ant': float(obj[5]),
				'dlls': float(obj[6]),
				'conver_dlls': float(obj[7]),
				'tc_ant_mex': float(obj[8]),
				'valor_mxn': float(obj[9]),
				'conver_mxn': float(obj[10]),
				'proyecto_id': self.id,
				}
				self.env['reporte.proyecto.line'].create(data)

	@api.one
	def resumen_generate(self):
		for i in self.resumen_ids:
			i.unlink()

		tmp = None
		t1 = 0
		t2 = 0
		t3 = 0
		t4 = 0
		t5 = 0
		t6 = 0
		t7 = 0

		for i in self.env['reporte.proyecto.line'].search( [('proyecto_id','=',self.id)] ).sorted(lambda r: r.rubro):
			if tmp == None:
				tmp = i.rubro
				t1 += i.moi
				t2 += i.tc_ant
				t3 += i.dlls
				t4 += i.conver_dlls
				t5 += i.tc_ant_mex
				t6 += i.valor_mxn
				t7 += i.conver_mxn

			elif tmp == i.rubro:	
				t1 += i.moi
				t2 += i.tc_ant
				t3 += i.dlls
				t4 += i.conver_dlls
				t5 += i.tc_ant_mex
				t6 += i.valor_mxn
				t7 += i.conver_mxn
			else:
				data = {
				'rubro': tmp,
				'moi': t1,
				'tc_ant': t2,
				'dlls': t3,
				'conver_dlls': t4,
				'tc_ant_mex': t5,
				'valor_mxn': t6,
				'conver_mxn': t7,
				'proyecto_id': self.id,
				}
				self.env['resumen.proyecto.line'].create(data)

				tmp = None
				t1 = 0
				t2 = 0
				t3 = 0
				t4 = 0
				t5 = 0
				t6 = 0
				t7 = 0

				tmp = i.rubro
				t1 += i.moi
				t2 += i.tc_ant
				t3 += i.dlls
				t4 += i.conver_dlls
				t5 += i.tc_ant_mex
				t6 += i.valor_mxn
				t7 += i.conver_mxn

		if tmp != None:
			data = {
			'rubro': tmp,
			'moi': t1,
			'tc_ant': t2,
			'dlls': t3,
			'conver_dlls': t4,
			'tc_ant_mex': t5,
			'valor_mxn': t6,
			'conver_mxn': t7,
			'proyecto_id': self.id,
			}
			self.env['resumen.proyecto.line'].create(data)
