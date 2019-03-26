# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv

import time
from openerp.report import report_sxw
from openerp import pooler
import calendar
import helper

class calquipa_picking(models.Model):
	_name="calquipa.picking"
	#para la nota de salida valorizada
	def get_head(self,cr,uid,ids,context=None):
		result = []
		active_id = ids[0]
		company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=context)
		picking_out_obj = self.pool.get('stock.picking').browse(cr, uid, active_id)	  
		# raise osv.except_osv('Alerta', compra)
		company_attrs = helper.company(cr, uid, company_id) #atributos company
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		
		#cad = """
		#select account_invoice.id from account_invoice
		#inner join picking_invoice_rel on account_invoice.id=picking_invoice_rel.invoice_id
		#where picking_id="""+str(active_id)
		#cr.execute(cad)
		#v= cr.dictfetchall()		
		#if v==[] or not v :
		#	raise osv.except_osv('Alerta', 'Este elemento no esta relacionado con una factura de devolucion')	  
		# raise osv.except_osv('Alerta', v[0])
		#c=v[0]
		# raise osv.except_osv('Alerta', c['id'])
		
		if picking_out_obj.invoice_id.id == False:
			raise osv.except_osv('Alerta', 'Este elemento no esta relacionado con una factura de devolucion')	  
		
		factura = self.pool.get('account.invoice').browse(cr, uid, picking_out_obj.invoice_id.id, context=context)
		
		c_ruc = company_attrs.ruc
		c_nombre = company_attrs.nombre
		c_street = company_attrs.street
		c_phone = company_attrs.phone
		c_email = company_attrs.email
		c_website = company_attrs.website
		c_city = company_attrs.city
		c_logo = company_attrs.logo
		c_name = picking_out_obj.name
		c_nombre = c_nombre.upper()
		c_numfac=''
		if not factura.date_invoice:
			raise osv.except_osv('Alerta', 'La factura no tiene fecha, no se puede imprimir')   
		if factura.invoice_line!=[]:
			if factura.supplier_invoice_number:
				c_numfac=factura.supplier_invoice_number
		else:
			raise osv.except_osv('Alerta', 'Este elemento no tiene factura, no se puede imprimir')						   

		detalle_company = ""

		ruc_company = ""

		result_detalle = []
		for items in picking_out_obj.move_lines:
			result_detalle.append(
					{
					"dest": items.partner_id.street,
					"origin": items.location_id.partner_id.street,
					}
				)
			break
		ntot=0
		# raise osv.except_osv('Alerta', self.get_detalle())
		for items in factura.invoice_line:
			ntot=ntot+items.price_subtotal
		tipo_cambio = factura.currency_rate_mod if factura.currency_rate_mod != 0.00 else factura.currency_rate_auto
		ntot = ntot*tipo_cambio
		ruccliente = picking_out_obj.partner_id.type_number
		if picking_out_obj.partner_id.is_company:
			ruccliente = picking_out_obj.partner_id.parent_id.type_number
		result.append(
				{
				"logo": c_logo,
				"ruc_company": ruc_company,
				"name_company": c_nombre,
				"detalle_company": detalle_company,
				"name_partner": picking_out_obj.partner_id.name,
				"ruc_partner": ruccliente,
				"street_partner": picking_out_obj.partner_id.street,
				"nro_doc_partner": picking_out_obj.partner_id.type_number,
				"origin": picking_out_obj.origin,
				"date": picking_out_obj.date[:10],
				"ori": company_attrs.street,
				"dest": result_detalle[0]["dest"],
				"numfact": c_numfac,
				"total": round(ntot,3),
				"name":c_name,
				"lineas":self.get_detalle(cr,uid,ids,context),
				"tipodecambio":tipo_cambio,
				}
			)
		txt=""
		for r in result:
			txt=txt+" "*10+r['name_company']+" "*20+'NOTA DE SALIDA'+" "*15+"Nro.: "+r['name']+"\n"
			txt=txt+" "*10+"FECHA: "+r['date']+"\n"
			txt=txt+" "*10+"Enviado a: "+r['name_partner']+"\n"
			txt=txt+" "*10+"Direccion: "+r['street_partner']+"\n"
			if r['ruc_partner']:
				ruc = r['ruc_partner'] 
			else:
				ruc = ''
			txt=txt+" "*10+"RUC: "+ruc+""*5+"\n"
			txt=txt+" "*10+"Codigo"+" "*2+"Cantidad"+" "*4+"Unidad"+" "*20+"Descripcion"+" "*15+"V. Unitario"+" "*10+"Total"+"\n"
			txt=txt+" "*10+"-"*100+"\n"
			for linea in r['lineas']:
				txt=txt+" "*10+str(linea["cod_product"] or " ")+" "*2+str(linea["qty"])+" "*4+str(linea["unit"])+" "*20+str(linea["product_name"])+" "*20+str(linea["vunit"])+" "*10+str(linea["price_subtotal"])+"\n"
			txt=txt+"\n"
		# raise osv.except_osv('Alerta', result)			
		return txt

	def get_detalle(self,cr,uid,ids,context=None):

		result = []
		active_id = ids[0]

		picking_out_obj = self.pool.get('stock.picking').browse(cr, uid, active_id)

		concatena_col = ''
		concatena_col_dos = ''

		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		result1 = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree2')

		id = result1 and result1[1] or False
		result1 = act_obj.read(cr, uid, [id], context=context)[0]

		inv_ids = []
		#factura_id = self.pool.get('purchase.order').browse(cr, uid, [picking_out_obj.purchase_id.id], context=context)[0]
		#compra = self.pool.get('purchase.order').get_invoice(cr, uid, [picking_out_obj.purchase_id.id])
		factura = self.pool.get('account.invoice').browse(cr, uid, picking_out_obj.invoice_id.id, context=context)
		
		result_detalle = []
		uom_obj = self.pool.get('product.uom')

		for items in factura.invoice_line:
			tipo_cambio = factura.currency_rate_mod if factura.currency_rate_mod != 0.00 else factura.currency_rate_auto
			precio_unitario = (items.price_subtotal/items.quantity) * tipo_cambio
			# raise osv.except_osv('Alerta', "%0.3f" % precio_unitario)  
			cantidad = uom_obj._compute_qty(cr, uid, items.uos_id.id, items.quantity,items.product_id.uom_id.id )
			preuni = uom_obj._compute_price(cr, uid, items.uos_id.id, precio_unitario,items.product_id.uom_id.id )

			result_detalle.append(
					{
					"cod_product": items.product_id.default_code,
					"product_name": items.product_id.product_tmpl_id.name,
					"qty": round(cantidad,3),
					"unit": items.product_id.uom_id.name,
					"vunit": preuni,
					"price_subtotal":round(preuni*cantidad,6),
					}
				)	   
		result.append(
				{
				"result_detalle": result_detalle,
				}
			)
		return result_detalle 
	



	#para la nota de salida no valorizada
	def get_head_single(self,cr,uid,ids,context=None):
		result = []
		active_id = ids[0]
		company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=context)
		picking_out_obj = self.pool.get('stock.picking').browse(cr, uid, active_id)
		
		# raise osv.except_osv('Alerta', compra)
		company_attrs = helper.company(cr, uid, company_id) #atributos company
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		result1 = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree2')
		id = result1 and result1[1] or False
		result1 = act_obj.read(cr, uid, [id], context=context)[0]
		inv_ids = []
		
		c_ruc = company_attrs.ruc
		c_nombre = company_attrs.nombre
		c_street = company_attrs.street
		c_phone = company_attrs.phone
		c_email = company_attrs.email
		c_website = company_attrs.website
		c_city = company_attrs.city
		c_logo = company_attrs.logo
		c_name = picking_out_obj.name
		c_nombre = c_nombre.upper()
		detalle_company = ""

		ruc_company = ""

		result_detalle = []
		for items in picking_out_obj.move_lines:
			result_detalle.append(
					{
					"dest": items.partner_id.street,
					"origin": items.location_id.partner_id.street,
					}
				)
			break
		ntot=0
		ruccliente = picking_out_obj.partner_id.type_number
		if picking_out_obj.partner_id.parent_id:
			ruccliente = picking_out_obj.partner_id.parent_id.type_number
		
		result.append(
				{
				"logo": c_logo,
				"ruc_company": ruc_company,
				"name_company": c_nombre,
				"detalle_company": detalle_company,
				"name_partner": picking_out_obj.partner_id.name,
				"nro_doc_partner": ruccliente,
				"street_partner": picking_out_obj.partner_id.street,
				# "nro_doc_partner": picking_out_obj.partner_id.nro_documento,
				"origin": picking_out_obj.origin,
				"date": picking_out_obj.date[:10],
				"ori": company_attrs.street,
				"dest": result_detalle[0]["dest"],
				"name":c_name,
				"lineas":self.get_detalle_single(cr,uid,ids,context),
				}
			)
		txt=""
		ntotcantidad=0
		for r in result:
			txt=txt+" "*10+r['name_company']+" "*20+'NOTA DE SALIDA'+" "*15+"Nro.: "+r['name']+"\n"
			txt=txt+" "*10+"FECHA: "+r['date']+"\n"
			txt=txt+" "*10+"Enviado a: "+r['name_partner']+"\n"
			txt=txt+" "*10+"Direccion: "+r['street_partner']+"\n"
			if r['nro_doc_partner']:
				ruc = r['nro_doc_partner'] 
			else:
				ruc = ''
			txt=txt+" "*10+"RUC: "+ruc+""*5+"\n"
			txt=txt+" "*10+"Codigo"+" "*2+"Cantidad"+" "*4+"Unidad"+" "*20+"Descripcion"+" "*15+"\n"
			txt=txt+" "*10+"-"*100+"\n"
			for linea in r['lineas']:
				txt=txt+" "*10+str(linea["cod_product"] or " ")+" "*2+str(linea["qty"])+" "*4+str(linea["unit"])+" "*20+str(linea["product_name"])+"\n"
				ntotcantidad+=linea["qty"]
			txt=txt+"\n"
			txt=txt+" "*10+"Total cant: "+str(ntotcantidad)
			txt=txt+"\n"
			txt=txt+"\n"
			txt=txt+"\n"
			txt=txt+"\n"
			txt=txt+" "*10+"-------------------   ---------------------    ------------     ------------------"+"\n"
			#txt=txt+" "+"Recibido almacen"+" "*15+"Entregado por:"+" "*15+"Revizado por:"+"\n"
			txt=txt+" "*10+"VoBo Felasac-Emisor"+" "*3+"VoBo Felasac-Receptor"+" "*5+"Vigilancia"+" "*8+"Administracion"+"\n"
		# raise osv.except_osv('Alerta', result)			
		return txt

	def get_detalle_single(self,cr,uid,ids,context=None):

		result = []
		active_id = ids[0]
		picking_out_obj = self.pool.get('stock.picking').browse(cr, uid, active_id)
		concatena_col = ''
		concatena_col_dos = ''
		mod_obj = self.pool.get('ir.model.data')
		inv_ids = []
		result_detalle = []
		for items in picking_out_obj.move_lines:
			# raise osv.except_osv('Alerta', "%0.3f" % precio_unitario)  
			result_detalle.append(
					{
					"cod_product": items.product_id.default_code,
					"product_name": items.product_id.name_template,
					"qty": round(items.product_qty,3),
					"unit": items.product_uom.name,
					}
				)
		
		result.append(
				{
				"result_detalle": result_detalle,
				}
			)
		return result_detalle