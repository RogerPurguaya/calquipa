# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp     import models, fields, api
import base64
import codecs

import datetime
import decimal

class stock_picking(models.Model):
	_inherit = 'stock.picking'

	picking_importador_id = fields.Many2one('stock.picking.importador', 'Importador')

class tabla_importacion_saldos(models.Model):
	_name = 'tabla.importacion.saldos'

	codigo                 = fields.Char(u'Código')
	cantidad               = fields.Char(u'Cantidad')
	precio_unitario_manual = fields.Char(u'Precio Unitario Manual')

class stock_picking_importador(models.Model):
	_name     = 'stock.picking.importador'
	_rec_name = 'csv_file_txt'

	state           = fields.Selection([('draft','Borrador'),('done','Importado')],'Estado',default='draft')
	date            = fields.Datetime(u'Fecha',required=True)
	csv_file        = fields.Binary(u'Archivo (.csv)', required=True)
	csv_file_txt    = fields.Char(u'Archivo (.csv)')
	delimiter       = fields.Char(u'Delimitador', size=1, required=True, default=',')
	max_lines       = fields.Integer(u'Máximo de lineas en albarán', required=True, default=30)
	picking_type_id = fields.Many2one('stock.picking.type', 'Albarán', required=True)
	errores         = fields.Binary(u'Errores encontrados')
	errores_txt     = fields.Char(u'Errores encontrados')
	feedback        = fields.Char(u'Resultado', default="------")

	@api.one
	def importar(self):
		#LIMPIA LA TABLA
		self.env.cr.execute("""
			DELETE FROM tabla_importacion_saldos
		""")

		#CREA EL CSV QUE SE INGRESO EN LA PANTALLA
		mp = self.env['main.parameter'].search([])[0]
		info     = base64.b64decode(self.csv_file)
		file_csv = open(mp.dir_create_file + 'si_imp.csv','wb')
		file_csv.write(info)
		file_csv.close()

		#INSERTA EL CSV EN LA TABLA
		self.env.cr.execute("""
			COPY tabla_importacion_saldos (codigo, cantidad, precio_unitario_manual) FROM '"""+str(mp.dir_create_file) + """si_imp.csv'""" + """ DELIMITER '"""+self.delimiter+"""' CSV HEADER
		""")

		#VALIDACION DE CODIGOS EXISTENTES
		self.errores = False
		self.env.cr.execute("""
			SELECT DISTINCT codigo FROM tabla_importacion_saldos WHERE codigo NOT IN (SELECT DISTINCT default_code FROM product_product WHERE default_code IS NOT NULL)
		""")
		data = self.env.cr.dictfetchall()
		err  = ""
		for reg in data:
			err += "-" + " " + reg['codigo'] + "\n"
		if len(err):
			err_file = open(str(mp.dir_create_file)+'errores_encontrados.txt','wb')
			err_file.write(u"Los siguientes códigos no existen:\n")
			err_file.write(err)
			err_file.close()
			self.errores  = base64.encodestring( open(str(mp.dir_create_file)+'errores_encontrados.txt','r').read() )
			self.feedback = "Error al importar. Verificar el archivo 'Errores encontrados'."
		else:
			#CREA LOS STOCK PICKING NECESARIOS PARA LA IMPORTACION EN BASE AL LIMITE DE LINEAS ASIGNADO
			self.env.cr.execute("""
				SELECT count(*) FROM tabla_importacion_saldos
			""")
			lineas_len  = self.env.cr.fetchall()[0][0]
			picking_qty = lineas_len / self.max_lines
			if lineas_len % self.max_lines:
				picking_qty += 1

			picking_ids = []

			# spi = datetime.datetime.now()
			# print spi

			for i in range(picking_qty):
				picking_name = self.id
				picking_seq  = self.pool.get('ir.sequence').next_by_id(self.env.cr, self.env.uid, self.picking_type_id.sequence_id.id, self.env.context)
				insert_sql =\
				"""
					INSERT INTO stock_picking
					(
					priority,
					picking_type_id,
					move_type,
					company_id,
					state,
					date,
					name,
					invoice_state,
					motivo_guia,
					picking_importador_id,
					weight_uom_id
					)
					VALUES 
					(
					'1',
					"""+str(self.picking_type_id.id)+""","""+\
					"""'direct'"""+""","""+\
					"""1"""+""","""+\
					"""'done'"""+""","""+\
					"""'"""+str(self.date)+"""'"""+""","""+\
					"""'"""+str(picking_seq)+"""'"""+""","""+\
					"""'none'"""+""","""+\
					"""'15'"""+""","""+\
					str(self.id)+""","""+\
					str(self.env['stock.picking']._get_default_uom())+\
					""")
					RETURNING id;
				"""
				self.env.cr.execute(insert_sql)
				picking_ids.append(self.env.cr.fetchall()[0][0])

			#CREA LOS STOCK MOVE Y LOS DISTRIBUYE EN TODOS LOS PICKING CREADOS
			self.env.cr.execute("""
				SELECT * FROM tabla_importacion_saldos
			""")
			data  = self.env.cr.dictfetchall()
			count = 0
			for reg in data:
				pp = self.env['product.product'].search([('default_code','=',reg['codigo'])])[0]
				insert_sql =\
				"""
					INSERT INTO stock_move
					(
					product_uos_qty,
					product_uom,
					product_uom_qty,
					company_id,
					date,
					date_expected,
					product_qty,
					product_uos,
					location_id,
					location_dest_id,
					priority,
					picking_type_id,
					state,
					name,
					warehouse_id,
					partially_available,
					propagate,
					procure_method,
					product_id,
					picking_id,
					invoice_state,
					price_unit,
					weight_uom_id,
					precio_unitario_manual
					)
					VALUES
					("""+\
					reg['cantidad'].replace(',','')+""","""+\
					str(pp.uom_id.id)+""","""+\
					reg['cantidad'].replace(',','')+""","""+\
					'1'+""","""+\
					"""'"""+str(self.date)+"""'"""+""","""+\
					"""'"""+str(self.date)+"""'"""+""","""+\
					reg['cantidad'].replace(',','')+""","""+\
					str(pp.uom_id.id)+""","""+\
					str(self.picking_type_id.default_location_src_id.id)+""","""+\
					str(self.picking_type_id.default_location_dest_id.id)+""","""+\
					'1'+""","""+\
					str(self.picking_type_id.id)+""","""+\
					"""'done'"""+""","""+\
					"""'"""+"""["""+pp.default_code+"""] """+pp.name_template+"""'"""+""","""+\
					str(self.picking_type_id.warehouse_id.id)+""","""+\
					"""false"""+""","""+\
					"""true"""+""","""+\
					"""'make_to_stock'"""+""","""+\
					str(pp.id)+""","""+\
					str(picking_ids[count/self.max_lines])+""","""+\
					"""'none'"""+""","""+\
					"""0"""+""","""+\
					str(self.env['stock.picking']._get_default_uom())+""","""+\
					reg['precio_unitario_manual'].replace(',','')+\
					""")
				"""
				self.env.cr.execute(insert_sql)
				count += 1
			self.feedback = u"Importación finalizada."
			self.state 	  = 'done'
			self.errores  = False

			# spf = datetime.datetime.now()
			# print spf

			# print spf-spi

	@api.one
	def anular(self):
		#ELIMINA LOS STOCK MOVE
		self.env.cr.execute("""
			DELETE FROM stock_move WHERE picking_id in (SELECT id FROM stock_picking WHERE picking_importador_id = """+str(self.id)+""")
		""")
		#ELIMINA LOS STOCK PICKING
		self.env.cr.execute("""
			DELETE FROM stock_picking WHERE picking_importador_id = """+str(self.id)+"""
		""")
		self.state    = 'draft'
		self.feedback = "-"
		self.errores  = False