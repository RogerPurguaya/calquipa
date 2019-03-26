# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp import http



class corrector_linea_compra_anulado(models.Model):
	_name = 'corrector.linea.compra.anulado'

	libro = fields.Many2one('account.journal','Libro')
	estado = fields.Char('Estado')
	corrector_id = fields.Many2one('corrector.ple.compra','Corrector')

class corrector_linea_compra_estadodocumento(models.Model):
	_name = 'corrector.linea.compra.estadodocumento'

	documento = fields.Many2one('it.type.document','Tipo Documento')
	libro = fields.Many2one('account.journal','Libro')
	estado = fields.Char('Estado')
	corrector_id = fields.Many2one('corrector.ple.compra','Corrector')


class corrector_linea_compra_estadofecha(models.Model):
	_name = 'corrector.linea.compra.estadofecha'

	documento = fields.Many2one('it.type.document','Tipo Documento')
	libro = fields.Many2one('account.journal','Libro')
	estado = fields.Char('Estado')
	corrector_id = fields.Many2one('corrector.ple.compra','Corrector')

class corrector_ple_compra(models.Model):
	_name = 'corrector.ple.compra'	

	period_id = fields.Many2one('account.period','Periodo',required=True)
	anulados = fields.One2many('corrector.linea.compra.anulado','corrector_id',string='Anulados')
	estado_documento = fields.One2many('corrector.linea.compra.estadodocumento','corrector_id','Estado Documento')
	fecha = fields.One2many('corrector.linea.compra.estadofecha','corrector_id','Fecha')

	anulados_mal = fields.Integer('Por Corregir Anulados')
	estadodocumento_mal = fields.Integer('Por Corregir Estado Documento')
	fecha_mal = fields.Integer('Por Corregir Fecha')

	@api.one
	def calcular(self):
		conta= 0
		parametros= self.env['main.parameter'].search([])[0]		
		for i in self.anulados:
			self.env.cr.execute(""" 
					select *  from account_move 
							where period_id = """ +str(self.period_id.id)+ """
							and journal_id = """ +str(i.libro.id)+ """
							and partner_id = """ +str(parametros.partner_null_id.id)+ """
							and ple_compra != '""" +i.estado+ """'
					""")
			conta += len(self.env.cr.fetchall())

		self.anulados_mal = conta

		#####
		conta = 0

		for i in self.estado_documento:
			self.env.cr.execute(""" 
				select * from  account_move 
						where period_id = """ +str(self.period_id.id)+ """
						and journal_id = """ +str(i.libro.id)+ """						
						and dec_reg_type_document_id = """ +str(i.documento.id)+ """
						and ple_compra != '""" +i.estado+ """'
						
				""")
			conta += len(self.env.cr.fetchall())
		self.estadodocumento_mal = conta

		######
		conta = 0

		for i in self.fecha:
			self.env.cr.execute(""" 
				select * from  account_move 
						where period_id = """ +str(self.period_id.id)+ """
						and journal_id = """ +str(i.libro.id)+ """						
						and dec_reg_type_document_id = """ +str(i.documento.id)+ """
						and date < '""" + str(self.period_id.date_start) + """'
						and ple_compra != '""" +i.estado+ """'
						
				""")
			conta += len(self.env.cr.fetchall())
		self.fecha_mal = conta


	@api.one
	def reparar(self):
		self.corregir_anulados()
		self.corregir_estadodocumento()
		self.corregir_estadofecha()
		self.calcular()




	@api.one
	def corregir_anulados(self):
		parametros= self.env['main.parameter'].search([])[0]		
		for i in self.anulados:
			self.env.cr.execute(""" 
					UPDATE account_move SET
							ple_compra = '""" +i.estado+ """'
							where period_id = """ +str(self.period_id.id)+ """
							and journal_id = """ +str(i.libro.id)+ """
							and partner_id = """ +str(parametros.partner_null_id.id)+ """
					""")


	@api.one
	def corregir_estadodocumento(self):		
		for i in self.estado_documento:
			self.env.cr.execute(""" 
				UPDATE account_move SET
						ple_compra = '""" +i.estado+ """'
						where period_id = """ +str(self.period_id.id)+ """
						and journal_id = """ +str(i.libro.id)+ """						
						and dec_reg_type_document_id = """ +str(i.documento.id)+ """
				""")


	@api.one
	def corregir_estadofecha(self):		
		for i in self.fecha:
			self.env.cr.execute(""" 
				UPDATE account_move SET
						ple_compra = '""" +i.estado+ """'
						where period_id = """ +str(self.period_id.id)+ """
						and journal_id = """ +str(i.libro.id)+ """						
						and dec_reg_type_document_id = """ +str(i.documento.id)+ """
						and date < '""" + str(self.period_id.date_start) + """'
				""")






















class corrector_linea_venta_estadofecha(models.Model):
	_name = 'corrector.linea.venta.estadofecha'

	documento = fields.Many2one('it.type.document','Tipo Documento')
	libro = fields.Many2one('account.journal','Libro')
	estado = fields.Char('Estado')
	corrector_id = fields.Many2one('corrector.ple.compra','Corrector')




class corrector_linea_venta_anulado(models.Model):
	_name = 'corrector.linea.venta.anulado'

	libro = fields.Many2one('account.journal','Libro')
	estado = fields.Char('Estado')
	corrector_id = fields.Many2one('corrector.ple.venta','Corrector')

class corrector_linea_venta_estadodocumento(models.Model):
	_name = 'corrector.linea.venta.estadodocumento'

	documento = fields.Many2one('it.type.document','Tipo Documento')
	libro = fields.Many2one('account.journal','Libro')
	estado = fields.Char('Estado')
	corrector_id = fields.Many2one('corrector.ple.venta','Corrector')

class corrector_ple_venta(models.Model):
	_name = 'corrector.ple.venta'	

	period_id = fields.Many2one('account.period','Periodo',required=True)
	anulados = fields.One2many('corrector.linea.venta.anulado','corrector_id','Anulados')
	estado_documento = fields.One2many('corrector.linea.venta.estadodocumento','corrector_id','Estado Documento')
	fecha = fields.One2many('corrector.linea.venta.estadofecha','corrector_id','Fecha')


	anulados_mal = fields.Integer('Por Corregir Anulados')
	estadodocumento_mal = fields.Integer('Por Corregir Estado Documento')
	fecha_mal = fields.Integer('Por Corregir Fecha')


	@api.one
	def calcular(self):
		conta= 0
		parametros= self.env['main.parameter'].search([])[0]		
		for i in self.anulados:
			self.env.cr.execute(""" 
					select *  from account_move 
							where period_id = """ +str(self.period_id.id)+ """
							and journal_id = """ +str(i.libro.id)+ """
							and partner_id = """ +str(parametros.partner_null_id.id)+ """
							and ple_venta != '""" +i.estado+ """'
					""")
			conta += len(self.env.cr.fetchall())

		self.anulados_mal = conta

		#####
		conta = 0

		for i in self.estado_documento:
			self.env.cr.execute(""" 
				select * from  account_move 
						where period_id = """ +str(self.period_id.id)+ """
						and journal_id = """ +str(i.libro.id)+ """						
						and dec_reg_type_document_id = """ +str(i.documento.id)+ """
						and ple_venta != '""" +i.estado+ """'
						
				""")
			conta += len(self.env.cr.fetchall())
		self.estadodocumento_mal = conta

		######
		conta = 0

		for i in self.fecha:
			self.env.cr.execute(""" 
				select * from  account_move 
						where period_id = """ +str(self.period_id.id)+ """
						and journal_id = """ +str(i.libro.id)+ """						
						and dec_reg_type_document_id = """ +str(i.documento.id)+ """
						and date < '""" + str(self.period_id.date_start) + """'
						and ple_venta != '""" +i.estado+ """'
						
				""")
			conta += len(self.env.cr.fetchall())
		self.fecha_mal = conta


	@api.one
	def reparar(self):
		self.corregir_anulados()
		self.corregir_estadodocumento()
		self.corregir_estadofecha()
		self.calcular()


	@api.one
	def corregir_anulados(self):
		parametros= self.env['main.parameter'].search([])[0]		
		for i in self.anulados:
			self.env.cr.execute(""" 
				UPDATE account_move SET
						ple_venta = '""" +i.estado+ """'
						where period_id = """ +str(self.period_id.id)+ """
						and journal_id = """ +str(i.libro.id)+ """
						and partner_id = """ +str(parametros.partner_null_id.id)+ """
				""")

	@api.one
	def corregir_estadodocumento(self):		
		for i in self.estado_documento:
			self.env.cr.execute(""" 
				UPDATE account_move SET
						ple_venta = '""" +i.estado+ """'
						where period_id = """ +str(self.period_id.id)+ """
						and journal_id = """ +str(i.libro.id)+ """						
						and dec_reg_type_document_id = """ +str(i.documento.id)+ """
				""")

	@api.one
	def corregir_estadofecha(self):		
		for i in self.fecha:
			self.env.cr.execute(""" 
				UPDATE account_move SET
						ple_venta = '""" +i.estado+ """'
						where period_id = """ +str(self.period_id.id)+ """
						and journal_id = """ +str(i.libro.id)+ """						
						and dec_reg_type_document_id = """ +str(i.documento.id)+ """
						and date < '""" + str(self.period_id.date_start) + """'
				""")



