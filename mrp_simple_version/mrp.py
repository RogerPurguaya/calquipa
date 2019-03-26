# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp

from openerp import models, fields, api
from openerp.osv import osv
from openerp.tools.translate import _

import pprint

class mrp_production(models.Model):
	_inherit='mrp.production'
	
	def _virtual_src_id_default(self, cr, uid, ids, context=None):
		try:
			location_id = self.pool.get('stock.location').search(cr, uid, [('usage', '=', 'production')])[0]
		except (orm.except_orm, ValueError):
			location_id = False
		return location_id
	
	
	def create(self, cr, uid, vals, context=None):
		if vals:
			if 'product_id' in vals:
				if vals['product_id'] == False:
					product_id = self.pool.get('product.product').search(cr, uid,[('es_produccion', '=', True)])
					if len(product_id) == 0:
						raise osv.except_osv('Alerta!', 'No existe ningun producto base para la produccion. Contacte a su administrador')
					vals.update({'product_id': product_id[0]})
			if 'product_qty' in vals:
				if vals['product_qty'] == False:
					vals.update({'product_qty': 1.0})
			if 'product_uom' in vals:
				if vals['product_uom'] == False:
					product_uom_id = self.pool.get('product.uom').search(cr, uid,[('es_produccion', '=', True)])
					if len(product_uom_id) == 0:
						raise osv.except_osv('Alerta!', 'No existe ningun producto base para la produccion. Contacte a su administrador')
					vals.update({'product_uom': product_uom_id[0]})
		pprint.pprint(vals)
		return super(mrp_production, self).create(cr, uid, vals, context=context)
	
	move_created_ids = fields.One2many('stock.move', 'production_id', 'Products to Produce',
            domain=[('state', 'not in', ('done', 'cancel'))], readonly=True, states={'draft': [('readonly', False)]})
	virtual_location_src_id = fields.Many2one('stock.location', 'Destino Mat. Primas Produccion',
			readonly=True, states={'draft': [('readonly', False)]})
	picking_ids = fields.One2many('stock.picking', 'production_id', 'Related Pickings')
	
	_defaults = {
		'virtual_location_src_id': _virtual_src_id_default,
	}
	
	'''
	def _make_production_produce_line(self, cr, uid, production, context=None):
		move_id = super(mrp_production,self)._make_production_produce_line(cr,uid,production,context)
		stock_move = self.pool.get('stock.move').browse(cr,uid,move_id,context)
		self.pool.get('stock.move').write(cr,uid,[move_id],{
				'location_id': production.virtual_location_src_id.id, 
				'location_dest_id': production.location_dest_id.id},context=context)
		return move_id
	#def _make_production_consume_line(self, cr, uid, production_line, parent_move_id, source_location_id=False, context=None):
	def _make_production_consume_line(self, cr, uid, line, context=None):
		#move_id = super(mrp_production,self)._make_production_consume_line(cr, uid, production_line, parent_move_id, source_location_id, context)
		move_id = super(mrp_production,self)._make_production_consume_line(cr, uid, line, context)
		stock_move = self.pool.get('stock.move').browse(cr,uid,move_id,context)
		original_qty = stock_move.product_qty
		self.pool.get('stock.move').write(cr,uid,[move_id],{'original_qty':original_qty},context=context)
		return move_id
	'''