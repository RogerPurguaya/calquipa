# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import models, fields, api

class stock_picking(models.Model):
	_inherit = 'stock.picking'

	internal_name = fields.Char("Nombre auxiliar")

	@api.model
	def create(self,vals):
		sequence_id = self.env['ir.sequence'].search([('name','=','Picking Seq')])
		vals['name'] = self.env['ir.sequence'].get_id(sequence_id.id, 'id')
		return super(stock_picking,self).create(vals)

	@api.one
	def copy(self, default=None):
		default = dict(default or {})
		default.update({'name':''})
		t = super(stock_picking,self).copy(default)
		t.internal_name = False
		return t

	@api.cr_uid_ids_context
	def do_transfer(self, cr, uid, picking_ids, context=None):
		t = super(stock_picking, self).do_transfer(cr, uid, picking_ids, context)
		picking_id = self.pool.get('stock.picking').browse(cr,uid,picking_ids,context)
		if not picking_id.internal_name:
			obj_sequence = self.pool.get('ir.sequence')
			new_name = obj_sequence.next_by_id(cr,uid,picking_id.picking_type_id.sequence_id.id,context)
			picking_id.name = new_name
			picking_id.internal_name = new_name
		else:
			picking_id.name = picking_id.internal_name
		return t


class mrp_production(models.Model):
	_inherit = 'mrp.production'

	def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
		t = super(mrp_production,self).action_produce(cr, uid, production_id, production_qty, production_mode, wiz, context)
		production_id = self.pool.get('mrp.production').browse(cr,uid,production_id,context=context)
		if len(production_id.move_lines2)>0:
			if len(production_id.move_lines2[0].picking_id)>0:
				consumed_picking_id = production_id.move_lines2[0].picking_id[0]
				if consumed_picking_id.state == 'done':
					self.pool.get('stock.picking').do_transfer(cr,uid,consumed_picking_id.id,context=context)
		if len(production_id.move_created_ids2)>0:
			if len(production_id.move_created_ids2[0].picking_id)>0:
				produced_picking_id = production_id.move_created_ids2[0].picking_id[0]
				if produced_picking_id.state == 'done':
					self.pool.get('stock.picking').do_transfer(cr,uid,produced_picking_id.id,context=context)
		return t