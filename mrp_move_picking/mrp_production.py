# -*- encoding: utf-8 -*-
import pprint

from openerp.osv import fields
from openerp.osv import osv
from openerp import api


class mrp_production(osv.osv):
	_name='mrp.production'
	_inherit='mrp.production'

	_columns = {
	'is_mercaderia' : fields.boolean('Es Mercaderia'),
	'is_envasado' : fields.boolean('Es Envasado'),
	}
	
	@api.model
	def create(self,vals):
		t = super(mrp_production,self).create(vals)
		t.write({})
		return t

	@api.one
	def write(self,vals):
		t = super(mrp_production,self).write(vals)
		self.refresh()
		
		if self.is_envasado and len(self.move_created_ids) >0 and len(self.move_lines)>0 and self.state == 'draft':
			print self.move_created_ids, self.move_lines

			if self.move_created_ids and self.move_created_ids[0].id:
				product_uom_salida = self.move_lines[0].product_uom
				product_uom_entrada = self.move_created_ids[0].product_uom

				total = self.move_lines[0].product_uom_qty
				if product_uom_salida.uom_type == 'smaller':
					total = total % product_uom_salida.factor_inv
				if product_uom_salida.uom_type == 'bigger':
					total = total * product_uom_salida.factor_inv



				if product_uom_entrada.uom_type == 'smaller':
					total = total * product_uom_entrada.factor_inv
				if product_uom_salida.uom_type == 'bigger':
					total = total / product_uom_entrada.factor_inv

				print total,self.move_created_ids[0].product_uom_qty

				if total != self.move_created_ids[0].product_uom_qty:
					raise osv.except_osv('Alerta!', 'No se convirtio correctamente el envase')
				if self.move_created_ids[0].product_uom_qty != int(self.move_created_ids[0].product_uom_qty):
					raise osv.except_osv('Alerta!', 'Las cantidades embasadas no son exactas.')

		return t
		
	def action_confirm(self, cr, uid, ids, context=None):
		shipment_act= super(mrp_production,self).action_confirm(cr, uid, ids, context)
		print 'HAS HAS HAS'
		if not hasattr(ids, "__iter__"):
			ids =[ids]
		prod = self.pool.get('mrp.production').browse(cr,uid,ids,context)[0]
		############################################
		# creamos un picking
		############################################
		picking_id=False
		self.pool.get('stock.picking').write(cr,uid,[shipment_act],{'date':prod.date_planned,'min_date':prod.date_planned},context)
		# sm=self.pool.get('stock.picking').browse(cr,uid,shipment_act,context)
		# for move in sm.move_lines:
		# 	self.pool.get('stock.move').write(cr,uid,[move.id],{'date_expected':prod.date_planned,'date':prod.date_planned},context)
		pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking')
		useract=self.pool.get('res.users').browse(cr,uid,uid)
		production_loc = self.pool.get('stock.location').search(cr,uid,[('usage','=','production')])
		if production_loc==[]:
			raise osv.except_osv('Alerta!', 'No se ha creado una ubicación de tipo produccion')
		production_loc=production_loc[0]
		ptype=self.pool.get('stock.picking.type').search(cr,uid,
			[
			('default_location_src_id','=',prod.location_src_id.id),
			('default_location_dest_id','=',production_loc),
			])

		if ptype ==[]:
			raise osv.except_osv('Alerta!', 'No se ha generado un Tipo de Operación con almacenes de origen igual al la Orden de producción y destino un almacen tipo "produccion"')
		if prod.move_lines:
			movedate=prod.move_lines[0]
			data_picking={
				'name':pick_name,
				'date':prod.date_planned,
				'min_date':prod.date_planned,
				'outcoming_point':movedate.location_id.id,
				'incoming_point':movedate.location_dest_id.id,
				'type':'internal',
				'state':'draft',
				'origin':prod.name,
				'note':'Creado para los productos a consumir',
				'operation_type':'7',
				'motivo_guia':'7',
				'picking_type_id':ptype[0],
				'company_id':useract.company_id.id,
			}
			picking_id = self.pool.get('stock.picking').create(cr, uid,data_picking, context=context)					
			pick1=self.pool.get('stock.picking').browse(cr,uid,picking_id,context)
			print 2
		
		pick_name_produce = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking')
		ptype2=self.pool.get('stock.picking.type').search(cr,uid,
			[
			('default_location_src_id','=',production_loc),
			('default_location_dest_id','=',prod.location_dest_id.id),
			])

		if ptype2 ==[]:
			raise osv.except_osv('Alerta!', 'No se ha generado un Tipo de Operación con almacen de origen igual almacen tipo "produccion" y destino al de la Orden de produccion')
		if prod.move_created_ids:
			movedate=prod.move_created_ids[0]
			data_picking_produce={
				'name':pick_name_produce,
				'date':prod.date_planned,
				'min_date':prod.date_planned,
				'outcoming_point':movedate.location_id.id,
				'incoming_point':movedate.location_dest_id.id,
				'type':'internal',
				'state':'draft',
				'origin':prod.name,
				'note':'Creado para los productos a producir',
				'operation_type':'8',
				'motivo_guia':'8',
				'picking_type_id':ptype2[0],
				'company_id':useract.company_id.id,
			}
			picking_id_produce = self.pool.get('stock.picking').create(cr, uid,data_picking_produce, context=context)					
		

		picks = []
		if picking_id:
			picks.append(picking_id)
		if picking_id_produce:
			picks.append(picking_id_produce)
		prod.write({'picking_ids':[(6,0,picks)]})
			
		vals={}
		for produc in self.browse(cr,uid,ids,context):
			for move in produc.move_lines:
				if picking_id:
					vals['picking_id']=picking_id
					vals['date_expected']=prod.date_planned
					vals['date']=prod.date_planned
					self.pool.get('stock.move').write(cr,uid,[move.id],vals,context)
					print 4
			for move in produc.move_created_ids:
				if picking_id_produce:
					vals['date_expected']=prod.date_planned
					vals['date']=prod.date_planned
					vals['picking_id']=picking_id_produce
					self.pool.get('stock.move').write(cr,uid,[move.id],vals,context)
					print 5

				if move.product_id.id == prod.product_id.id:
					move.action_cancel()
					move.write({'state': 'cancel'})
					move.write({'state': 'draft'})
					self.pool.get('stock.move').unlink(cr,uid,[move.id],context)
					print 6
			#pprint.pprint(produc.move_lines)
			#pprint.pprint(produc.move_created_ids)
		
		#raise osv.except_osv('Alerta!', 'WO WO WO')		
		return 0


mrp_production()
