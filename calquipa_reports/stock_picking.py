# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv

class stock_picking(models.Model):
	_name="stock.picking"
	_inherit="stock.picking"

	def maketxtinter(self,cr,uid,ids,context=None):
		reporteador = self.pool.get('calquipa.picking')
		# raise osv.except_osv('Alerta', reporteador)
		s = reporteador.get_head_single(cr,uid,ids,context)
		self.pool.get('make.txt').makefile(cr,uid,s,'nsalu',context)

	@api.multi
	def get_type_stock_picking_per(self):
		print 'LLEGO ACA'
		for i in self:
			print 'picking_type_id.code', i.picking_type_id.code
			i.type_code_stock = i.picking_type_id.code

	type_code_stock = fields.Char('Tipo Stock', compute='get_type_stock_picking_per')

	#type_code_stock = fields.Selection('Tipo Stock', compute='get_type_stock_picking_per')

	def maketxt(self,cr,uid,ids,context=None):
		reporteador = self.pool.get('calquipa.picking.in')
		s = reporteador.get_head_in(cr,uid,ids,context)
		self.pool.get('make.txt').makefile(cr,uid,s,'ningreu',context)
		
	def maketxt_prod(self,cr,uid,ids,context=None):
		reporteador_prod = self.pool.get('calquipa.picking.in.prod')
		s = reporteador_prod.get_head_in(cr,uid,ids,context)
		self.pool.get('make.txt').makefile(cr,uid,s,'nilp',context)

	def maketxtout(self,cr,uid,ids,context=None):
		reporteador = self.pool.get('calquipa.guiarem')
		context.update({'logistica':False})
		s = reporteador.get_head_txt(cr,uid,ids,context)
		self.pool.get('make.txt').makefile(cr,uid,s,'gsv',context)
	def maketxt_logi(self,cr,uid,ids,context=None):
		reporteador = self.pool.get('calquipa.guiarem')
		context.update({'logistica':True})
		s = reporteador.get_head_txt_log(cr,uid,ids,context)
		self.pool.get('make.txt').makefile(cr,uid,s,'gsa',context)
	def maketxt_sal(self,cr,uid,ids,context=None):
		reporteador = self.pool.get('calquipa.picking')
		# raise osv.except_osv('Alerta', reporteador)
		s = reporteador.get_head(cr,uid,ids,context)
		self.pool.get('make.txt').makefile(cr,uid,s,'nsv',context)