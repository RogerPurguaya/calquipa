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


class reporte_parametros(models.Model):
	_name = 'reporte.parametros'

	name= fields.Char('Parametro',default='Parametros')

	tributos = fields.Many2one('rm.balance.config.mexicano.line','Tributos')
	impuesto_recuperar = fields.Many2one('rm.balance.config.mexicano.line','Impuesto x Recuperar')
	impuesto_pagar = fields.Many2one('rm.balance.config.mexicano.line','Impuesto x Pagar')
	saldo_inicial_periodo = fields.Many2one('rm.balance.config.mexicano.line','Saldo Inicial Periodo')


	def init(self, cr):
		cr.execute('select id from reporte_parametros')
		ids = cr.fetchall()

		if len(ids) == 0:
			cr.execute("""INSERT INTO reporte_parametros (name) VALUES ('Parámetros')""")

