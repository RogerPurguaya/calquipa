# -*- encoding: utf-8 -*-
import time
import openerp.addons.decimal_precision as dp

from openerp.osv import fields
from openerp.osv import osv
from openerp import netsvc

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp import SUPERUSER_ID
from openerp.addons.product import _common
from datetime import date, datetime, timedelta
from openerp.tools import float_compare, float_is_zero

class mrp_production(osv.osv):
	_name='mrp.production'
	_inherit='mrp.production'


	def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
		#Continua con los stock_moves
		is_total=True
		if is_total:

			"""production =self.browse(cr, uid, production_id, context=context)
			if production.move_lines:
				if production.move_lines[0].picking_id:
					picking_id= production.move_lines[0].picking_id.id
					picking_id.state = 'done'
					#picking_id.write(cr,uid,{'state':'done'})
			if production.move_created_ids:
				if production.move_created_ids[0].picking_id:
					picking_id=production.move_created_ids[0].picking_id.id
					picking_id.state = 'done'
					#picking_id.write({'state':'done'})
				
			if production.move_created_ids2:
				if production.move_created_ids2[0].picking_id:
					if production.is_mercaderia:
						picking_id=production.move_created_ids2[0].picking_id.id
						picking_id.operation_type = '10'
						picking_id.motivo_guia = '10'
						#picking_id.write({'operation_type':'10','motivo_guia':'10'})
			"""

			stock_mov_obj = self.pool.get('stock.move')
			production = self.browse(cr, uid, production_id, context=context)

			wf_service = netsvc.LocalService("workflow")
			if not production.move_lines and production.state == 'ready':
				# trigger workflow if not products to consume (eg: services)
				wf_service.trg_validate(uid, 'mrp.production', production_id, 'button_produce', cr)

			produced_qty = 0
			for produced_product in production.move_created_ids2:
				if (produced_product.scrapped) or (produced_product.product_id.id != production.product_id.id):
					continue
				produced_qty += produced_product.product_qty
			if production_mode in ['consume','consume_produce']:
				consumed_data = {}

				# Calculate already consumed qtys
				for consumed in production.move_lines2:
					if consumed.scrapped:
						continue
					if not consumed_data.get(consumed.product_id.id, False):
						consumed_data[consumed.product_id.id] = 0
					consumed_data[consumed.product_id.id] += consumed.product_qty

				for raw_product in production.move_lines:
					# qtys we have to consume
					#qty = total_consume - consumed_data.get(scheduled.product_id.id, 0.0)
					raw_product.action_consume(raw_product.product_qty, raw_product.location_id.id, context=context)
					stock_mov_obj.write(cr,uid,[raw_product.id],{'state': 'done'},context)
				
#				# Find product qty to be consumed and consume it
#				for scheduled in production.product_lines:
#					
#					# total qty of consumed product we need after this consumption
#					total_consume = ((production_qty + produced_qty) * scheduled.product_qty / production.product_qty)
#					print('total_consume')
#					print(total_consume)
#					# qty available for consume and produce
#					qty_avail = scheduled.product_qty - consumed_data.get(scheduled.product_id.id, 0.0)
#					print(qty_avail)
#					if float_compare(qty_avail, 0, precision_rounding=scheduled.product_id.uom_id.rounding) <= 0:
#						# there will be nothing to consume for this raw material
#						continue
#
#					#raw_products = [move for move in production.move_lines if move.product_id.id==scheduled.product_id.id]
#					#if raw_product:
#					for raw_product in production.move_lines:
#						# qtys we have to consume
#						
#						print('consumed')
#						print(total_consume)
#						#qty = total_consume - consumed_data.get(scheduled.product_id.id, 0.0)
#						qty = qty_avail
#						'''
#						if float_compare(qty, qty_avail, precision_rounding=scheduled.product_id.uom_id.rounding) == 1:
#							# if qtys we have to consume is more than qtys available to consume
#							prod_name = scheduled.product_id.name_get()[0][1]
#							raise osv.except_osv(_('Warning!'), _('You are going to consume total %s quantities of "%s".\nBut you can only consume up to total %s quantities.') % (qty, prod_name, qty_avail))
#						if float_compare(qty, 0, precision_rounding=scheduled.product_id.uom_id.rounding) <= 0:						
#							# we already have more qtys consumed than we need
#							continue
#						'''
#						
#						raw_product.action_consume(raw_product.product_qty, raw_product.location_id.id, context=context)
#						stock_mov_obj.write(cr,uid,[raw_product.id],{'state': 'done'},context)
						
			# raise osv.except_osv(_('Warning!'), 'aasssssssssssdf')
			if production_mode == 'consume_produce':
				print('consume_produce')
				# To produce remaining qty of final product
				#vals = {'state':'confirmed'}
				#final_product_todo = [x.id for x in production.move_created_ids]
				#stock_mov_obj.write(cr, uid, final_product_todo, vals)
				#stock_mov_obj.action_confirm(cr, uid, final_product_todo, context)
				produced_products = {}
				for produced_product in production.move_created_ids2:
					if produced_product.scrapped:
						continue
					if not produced_products.get(produced_product.product_id.id, False):
						produced_products[produced_product.product_id.id] = 0
					produced_products[produced_product.product_id.id] += produced_product.product_qty

				for produce_product in production.move_created_ids:
					produced_qty = produced_products.get(produce_product.product_id.id, 0)
					subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
					rest_qty = (subproduct_factor * production.product_qty) - produced_qty

					'''
					if rest_qty < (subproduct_factor * production_qty):
						prod_name = produce_product.product_id.name_get()[0][1]
						raise osv.except_osv(_('Warning!'), _('You are going to produce total %s quantities of "%s".\nBut you can only produce up to total %s quantities.') % ((subproduct_factor * production_qty), prod_name, rest_qty))
					'''
					if rest_qty > 0 :
						print 'producto',produce_product.name
						#self.pool.get('stock.move').write(cr,uid,[produce_product.id],{'product_uom_qty':production_qty},context)
						#stock_mov_obj.action_consume(cr, uid, [produce_product.id], (subproduct_factor * production_qty), context=context)
						stock_mov_obj.action_consume(cr, uid, [produce_product.id], produce_product.product_qty, context=context)
						stock_mov_obj.write(cr, uid, [produce_product.id], {'state': 'done'}, context=context)
						

#			for raw_product in production.move_lines2:
#				new_parent_ids = []
#				#self.pool.get('stock.move').write(cr,uid,[raw_product.id],{'product_uom_qty':production_qty},context)
#				parent_move_ids = [x.id for x in raw_product.move_history_ids]
#				for final_product in production.move_created_ids2:
#					if final_product.id not in parent_move_ids:
#						new_parent_ids.append(final_product.id)
#				for new_parent_id in new_parent_ids:
#					stock_mov_obj.write(cr, uid, [raw_product.id], {'move_history_ids': [(4,new_parent_id)]})

			wf_service.trg_validate(uid, 'mrp.production', production_id, 'button_produce_done', cr)
			#self.write(cr, uid, production_id,{'product_qty':production_qty} ,context=context)


			production =self.browse(cr, uid, production_id, context=context)
			print production, production.is_envasado, 'GG ya no mas'
			if production.is_envasado:
				print "entro raro"
				parametros_id = self.pool.get('main.parameter').search(cr,uid,[])
				parametros = self.pool.get('main.parameter').browse(cr,uid,parametros_id,context)

				fechaini = '20180101'
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = '20181231'


				for i in [production]:
					calc = 0
					if i.move_lines2 and i.move_lines2[0].id:
						print "paso 1"
						lst_products  = []
						lst_locations = []
						productos='{'
						almacenes='{'
						date_ini= fechaini.replace('-','')
						date_fin= fechafin.replace('-','')

						lst_products = self.pool.get('product.product').search(cr,uid,[])
						lst_locations = self.pool.get('stock.location').search(cr,uid,[]) 

						for producto in lst_products:
							productos=productos+str(producto)+','
						productos=productos[:-1]+'}'
						for location in lst_locations:
							almacenes=almacenes+str(location)+','
						almacenes=almacenes[:-1]+'}'




						cr.execute(""" 
										 select 
										cadquiere
										from get_kardex_v("""+ fecha_inianio + "," + fechafin + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[]) 
										where  stock_moveid = """ + str(i.move_lines2[0].id)  + """
									""")

						for wakanda in cr.fetchall():
							calc = wakanda[0] if wakanda[0] else 0
							

					if i.move_created_ids2 and i.move_created_ids2[0].id:
						print "paso 2"
						product_uom_salida = i.move_lines2[0].product_id.unidad_kardex if i.move_lines2[0].product_id.unidad_kardex else i.move_lines2[0].product_id.uom_id
						product_uom_entrada = i.move_created_ids2[0].product_uom

						total = calc
						print total, product_uom_entrada.name,product_uom_salida.name
						if product_uom_salida.uom_type == 'smaller':
							total = total * product_uom_salida.factor_inv
						if product_uom_salida.uom_type == 'bigger':
							total = total / product_uom_salida.factor_inv

						print total,product_uom_entrada.uom_type

						if product_uom_entrada.uom_type == 'smaller':
							total = total / product_uom_entrada.factor_inv
						if product_uom_entrada.uom_type == 'bigger':
							print "porque n lo hace",product_uom_entrada.factor_inv 
							total = total * product_uom_entrada.factor_inv

						print total
						

						i.move_created_ids2[0].precio_unitario_manual = total
						i.move_created_ids2[0].price_unit = total
						print "algo hace",total
						cr.execute("""
							update stock_move set precio_unitario_manual = """ +str(total)+ """ , price_unit = """ +str(total)+ """ 
							where id = """+str(i.move_created_ids2[0].id)+"""
							""")


			return True
		else:
			return super(mrp_production,self).action_produce(cr, uid, production_id, production_qty, production_mode, wiz, context)
			
mrp_production()





