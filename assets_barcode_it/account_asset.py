# -*- coding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs
import pprint
import io
from xlsxwriter.workbook import Workbook
import sys
from datetime import datetime
import os


def isodd(x):
	return bool(x % 2)

class account_asset_asset(models.Model):
	_inherit = 'account.asset.asset'

	ean13 = fields.Char("Código EAN13")

	@api.model
	def _get_ean_next_code(self, product):
		sequence_obj = self.env['ir.sequence']
		ean_sequence_id = self.env['ir.sequence'].search([('name','=','Ean13 code')])
		print ean_sequence_id
		ean = sequence_obj.next_by_id(ean_sequence_id.id)
		ean = (len(ean[0:6]) == 6 and ean[0:6] or
			   ean[0:6].ljust(6, '0')) + ean[6:].rjust(6, '0')
		if len(ean) > 12:
			raise exceptions.Warning(
				_("Configuration Error!"
				  "The next sequence is longer than 12 characters. "
				  "It is not valid for an EAN13 needing 12 characters, "
				  "the 13 being used as a control digit"
				  "You will have to redefine the sequence or create a new one")
				)

		return ean

	def _get_ean_control_digit(self, code):
		sum = 0
		for i in range(12):
			if isodd(i):
				sum += 3 * int(code[i])
			else:
				sum += int(code[i])
		key = (10 - sum % 10) % 10
		return '%d' % key

	@api.model
	def _generate_ean13_value(self, product):
		ean = self._get_ean_next_code(product)
		if not ean:
			return None
		key = self._get_ean_control_digit(ean)
		ean13 = ean + key
		return ean13

	@api.one
	def generate_ean13(self):
		if not self.ean13:
			ean13 = self._generate_ean13_value(self)
			if ean13:
				self.write({'ean13': ean13})
		return True

	@api.one
	def generate_ean13_all(self):
		assets = self.env['account.asset.asset'].search([])
		for asset in assets:
			if not asset.ean13:
				ean13 = self._generate_ean13_value(asset)
				if ean13:
					asset.write({'ean13': ean13})
		return True

	@api.one
	def reset_ean13(self):
		self.write({'ean13': False})
		return True


	@api.multi
	def get_asset_list(self):
		#-------------------------------------------Datos---------------------------------------------------
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		output = io.BytesIO()

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion + 'Activos.xlsx')
		worksheet = workbook.add_worksheet("Activos")

		#----------------Formatos------------------
		basic = {
			'align'		: 'left',
			'valign'	: 'vcenter',
			'text_wrap'	: 1,
			'font_size'	: 9,
			'font_name'	: 'Calibri'
		}

		basic_center = basic.copy()
		basic_center['align'] = 'center'

		numeric = basic.copy()
		numeric['align'] = 'right'
		numeric['num_format'] = '0.00'

		numeric_bold_format = numeric.copy()
		numeric_bold_format['bold'] = 1

		bold = basic.copy()
		bold['bold'] = 1

		header = bold.copy()
		header['bg_color'] = '#A9D0F5'
		header['border'] = 1
		header['align'] = 'center'

		title = bold.copy()
		title['font_size'] = 12

		basic_format = workbook.add_format(basic)
		basic_center_format = workbook.add_format(basic_center)
		numeric_format = workbook.add_format(numeric)
		bold_format = workbook.add_format(bold)
		numeric_bold_format = workbook.add_format(numeric_bold_format)
		header_format = workbook.add_format(header)
		title_format = workbook.add_format(title)

		nro_columnas = 17
			
		tam_col = [0]*nro_columnas
		
		#----------------------------------------------Título--------------------------------------------------
		cabecera = "Calquipa S.A.C."
		worksheet.merge_range('A1:B1', cabecera, title_format)
		#---------------------------------------------Cabecera------------------------------------------------
		worksheet.merge_range('A2:D2', "Lista de Activos", bold_format)

		columnas = [u"Ubicación",u"Código",u"Código EAN13", u"Activo"]
		fil = 3
		for col in range(len(columnas)): 
			worksheet.write(fil, col, columnas[col], header_format)
		fil += 1

		#------------------------------------------Insertando Data----------------------------------------------	
		for line in self:
			col = 0
			worksheet.write(fil, col, line.ubicacion if line.ubicacion else '', basic_format)
			col += 1
			worksheet.write(fil, col, line.codigo if line.codigo else '', basic_format)
			col += 1
			worksheet.write(fil, col, line.ean13 if line.ean13 else '', basic_format)
			col += 1
			worksheet.write(fil, col, line.name, basic_format)
			col += 1
			fil += 1

		col_size = [25, 15, 70]
		
		worksheet.set_column('A:A', col_size[0])
		worksheet.set_column('B:C', col_size[1])
		worksheet.set_column('D:D', col_size[2])
		workbook.close()

		f = open(direccion + 'Activos.xlsx', 'rb')
		
		vals = {
			'output_name': 'Activos.xlsx',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		sfs_id = self.env['export.file.save'].create(vals)

		return {
		    "type": "ir.actions.act_window",
		    "res_model": "export.file.save",
		    "views": [[False, "form"]],
		    "res_id": sfs_id.id,
		    "target": "new",
		}