# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv

class grupo_report_extraccion(models.Model):
	_name = 'grupo.report.extraccion'

	titulo = fields.Char('Name',required=True)
	order = fields.Integer('Order',required=True)

	@api.one
	def get_name_person(self):
		self.name = str(self.order) + '-' + self.titulo

	name = fields.Char('Name',compute="get_name_person")


class rm_report_extraccion_line(models.Model):
	_name = 'rm.report.extracción.line'


	@api.one
	def get_enero(self):
		if self.rm_report_extraccion_id.id:
			period_txt = self.rm_report_extraccion_id.fiscal.name + '01'

			self.env.cr.execute( """
			select cuenta,sum(round(debe-haber,2)) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
			where cuenta = '""" + self.cuenta.code + """'
			group by cuenta """)

			c_data = 0

			for i in self.env.cr.fetchall():
				c_data = i[1]

			self.enere=c_data
		else:
			self.enero= 0


	@api.one
	def get_febrero(self):
		if self.rm_report_extraccion_id.id:
			period_txt = self.rm_report_extraccion_id.fiscal.name + '02'

			self.env.cr.execute( """
			select cuenta,sum(round(debe-haber,2)) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
			where cuenta = '""" + self.cuenta.code + """'
			group by cuenta """)

			c_data = 0

			for i in self.env.cr.fetchall():
				c_data = i[1]

			self.febrero=c_data
		else:
			self.febrero= 0


	@api.one
	def get_marzo(self):
		if self.rm_report_extraccion_id.id:
			period_txt = self.rm_report_extraccion_id.fiscal.name + '03'

			self.env.cr.execute( """
			select cuenta,sum(round(debe-haber,2)) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
			where cuenta = '""" + self.cuenta.code + """'
			group by cuenta """)

			c_data = 0

			for i in self.env.cr.fetchall():
				c_data = i[1]

			self.marzo=c_data
		else:
			self.marzo= 0


	@api.one
	def get_abril(self):
		if self.rm_report_extraccion_id.id:
			period_txt = self.rm_report_extraccion_id.fiscal.name + '04'

			self.env.cr.execute( """
			select cuenta,sum(round(debe-haber,2)) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
			where cuenta = '""" + self.cuenta.code + """'
			group by cuenta """)

			c_data = 0

			for i in self.env.cr.fetchall():
				c_data = i[1]

			self.abril=c_data
		else:
			self.abril= 0


	@api.one
	def get_mayo(self):
		if self.rm_report_extraccion_id.id:
			period_txt = self.rm_report_extraccion_id.fiscal.name + '05'

			self.env.cr.execute( """
			select cuenta,sum(round(debe-haber,2)) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
			where cuenta = '""" + self.cuenta.code + """'
			group by cuenta """)

			c_data = 0

			for i in self.env.cr.fetchall():
				c_data = i[1]

			self.mayo=c_data
		else:
			self.mayo= 0


	@api.one
	def get_junio(self):
		if self.rm_report_extraccion_id.id:
			period_txt = self.rm_report_extraccion_id.fiscal.name + '06'

			self.env.cr.execute( """
			select cuenta,sum(round(debe-haber,2)) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
			where cuenta = '""" + self.cuenta.code + """'
			group by cuenta """)

			c_data = 0

			for i in self.env.cr.fetchall():
				c_data = i[1]

			self.junio=c_data
		else:
			self.junio= 0


	@api.one
	def get_julio(self):
		if self.rm_report_extraccion_id.id:
			period_txt = self.rm_report_extraccion_id.fiscal.name + '07'

			self.env.cr.execute( """
			select cuenta,sum(round(debe-haber,2)) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
			where cuenta = '""" + self.cuenta.code + """'
			group by cuenta """)

			c_data = 0

			for i in self.env.cr.fetchall():
				c_data = i[1]

			self.julio=c_data
		else:
			self.julio= 0


	@api.one
	def get_agosto(self):
		if self.rm_report_extraccion_id.id:
			period_txt = self.rm_report_extraccion_id.fiscal.name + '08'

			self.env.cr.execute( """
			select cuenta,sum(round(debe-haber,2)) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
			where cuenta = '""" + self.cuenta.code + """'
			group by cuenta """)

			c_data = 0

			for i in self.env.cr.fetchall():
				c_data = i[1]

			self.agosto=c_data
		else:
			self.agosto= 0


	@api.one
	def get_septiembre(self):
		if self.rm_report_extraccion_id.id:
			period_txt = self.rm_report_extraccion_id.fiscal.name + '09'

			self.env.cr.execute( """
			select cuenta,sum(round(debe-haber,2)) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
			where cuenta = '""" + self.cuenta.code + """'
			group by cuenta """)

			c_data = 0

			for i in self.env.cr.fetchall():
				c_data = i[1]

			self.septiembre=c_data
		else:
			self.septiembre= 0


	@api.one
	def get_octubre(self):
		if self.rm_report_extraccion_id.id:
			period_txt = self.rm_report_extraccion_id.fiscal.name + '10'

			self.env.cr.execute( """
			select cuenta,sum(round(debe-haber,2)) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
			where cuenta = '""" + self.cuenta.code + """'
			group by cuenta """)

			c_data = 0

			for i in self.env.cr.fetchall():
				c_data = i[1]

			self.octubre=c_data
		else:
			self.octubre= 0


	@api.one
	def get_noviembre(self):
		if self.rm_report_extraccion_id.id:
			period_txt = self.rm_report_extraccion_id.fiscal.name + '11'

			self.env.cr.execute( """
			select cuenta,sum(round(debe-haber,2)) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
			where cuenta = '""" + self.cuenta.code + """'
			group by cuenta """)

			c_data = 0

			for i in self.env.cr.fetchall():
				c_data = i[1]

			self.noviembre=c_data
		else:
			self.noviembre= 0


	@api.one
	def get_diciembre(self):
		if self.rm_report_extraccion_id.id:
			period_txt = self.rm_report_extraccion_id.fiscal.name + '12'

			self.env.cr.execute( """
			select cuenta,sum(round(debe-haber,2)) from get_hoja_trabajo_detalle_registro(false,"""+period_txt+ ""","""+period_txt+ """)
			where cuenta = '""" + self.cuenta.code + """'
			group by cuenta """)

			c_data = 0

			for i in self.env.cr.fetchall():
				c_data = i[1]

			self.diciembre=c_data
		else:
			self.diciembre= 0

		

	cuenta = fields.Many2one('account.account','Cuenta',required=True)
	grupo = fields.Many2one('grupo.report.extraccion','Grupo',required=True)

	enero = fields.Float('Enero',digits=(12,2),compute="get_enero")
	febrero = fields.Float('Febrero',digits=(12,2),compute="get_febrero")
	marzo = fields.Float('Marzo',digits=(12,2),compute="get_marzo")
	abril = fields.Float('Abril',digits=(12,2),compute="get_abril")
	mayo = fields.Float('Mayo',digits=(12,2),compute="get_mayo")
	junio = fields.Float('Junio',digits=(12,2),compute="get_junio")
	julio = fields.Float('Julio',digits=(12,2),compute="get_julio")
	agosto = fields.Float('Agosto',digits=(12,2),compute="get_agosto")
	septiembre = fields.Float('Septiembre',digits=(12,2),compute="get_septiembre")
	octubre = fields.Float('Octubre',digits=(12,2),compute="get_octubre")
	noviembre = fields.Float('Noviembre',digits=(12,2),compute="get_noviembre")
	diciembre = fields.Float('Diciembre',digits=(12,2),compute="get_diciembre")

	rm_report_extraccion_id = fields.Many2one('rm.report.extraccion','Cabezera')

	_order = 'grupo, cuenta'


class rm_report_extraccion(models.Model):
	_name= 'rm.report.extraccion'

	fiscal = fields.Many2one('account.fiscalyear','Anexo de Operación',required=True)
	sitio = fields.Char('Sitio',required=True)
	centro_de_costo = fields.Char('Centro de Costo',readonly=True,default='Extracción')
	fecha_emision_reporte = fields.Date('Fecha de Emisión del Reporte',required=True)
	usuario = fields.Many2one('res.users','Usuario',readonly=True)
	conf_line_ids = fields.One2many('rm.report.extraccion.line','rm_report_extraccion_id','Lineas de Configuración')



