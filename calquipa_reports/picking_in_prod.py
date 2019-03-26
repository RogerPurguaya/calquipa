# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv
import time
import pprint
from openerp.report import report_sxw
from openerp import pooler
import calendar
import helper

class calquipa_picking_in_prod(models.Model):
	_name="calquipa.picking.in.prod"
	
	def get_head_in(self, cr, uid, ids, context=None):
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
		if picking_out_obj.invoice_id.id == False:
			query = """
				SELECT picking_id, po.id FROM stock_picking p, stock_move m, purchase_order_line pol, purchase_order po
				WHERE p.id = """ + str(picking_out_obj.id) + """ and po.id = pol.order_id and pol.id = m.purchase_line_id and m.picking_id = p.id
				GROUP BY picking_id, po.id
			"""
			cr.execute(query)
			order_ids = cr.fetchall()
			order_id = False
			for pick_id, po_id in order_ids:
				order_id = po_id
			order = self.pool.get('purchase.order').browse(cr, uid, order_id, context)
			in_ids = order.invoice_ids
			#raise osv.except_osv('Alerta', 'Este elemento no está relacionado con una compra por lo que no se imprime\nla nota de ingreso')
			invoice_id=None
			if in_ids:
				invoice_id = in_ids[0].id
		else:
			invoice_id = picking_out_obj.invoice_id.id
		if invoice_id:
			facturas = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
		else:
			facturas=[]
		
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
		ntot=0
		detalle_company = ""
		ruc_company = ""
		for factura in facturas:
			if factura.type=="in_invoice" and factura.state!='cancel':
				if not factura.date_invoice:
					raise osv.except_osv('Alerta', 'La factura no tiene fecha, no se puede imprimir')   
				if factura.invoice_line!=[]:
					if factura.supplier_invoice_number:
						c_numfac=factura.supplier_invoice_number
				else:
					raise osv.except_osv('Alerta', 'Este elemento no tiene factura, no se puede imprimir')						   

				


				ntot=0
				# raise osv.except_osv('Alerta', self.get_detalle())
				for items in factura.invoice_line:
					ntot=ntot+items.price_subtotal
				tipo_cambio = 1.0
				if company_attrs.currency_id != factura.currency_id.id:
					if factura.date_invoice == False:
						raise osv.except_osv('Alerta!', 'La factura de este pedido debe tener una fecha configurada')
					rate_ids = self.pool.get('res.currency.rate').search(cr, uid, [('currency_id','=',factura.currency_id.id),('date_sunat', '=', factura.date_invoice)])
					if len(rate_ids) == 0:
						raise osv.except_osv('Alerta!', 'No existe un tipo de cambio para la fecha: ' + factura.date_invoice)
					rate_obj = self.pool.get('res.currency.rate').browse(cr, uid, rate_ids[0], context)
					tipo_cambio = rate_obj.type_sale
				#tipo_cambio = factura.currency_rate_mod if factura.currency_rate_mod != 0.00 else factura.currency_rate_auto
				
				#raise osv.except_osv('Alerta!', 'LOL')
				ntot = ntot*tipo_cambio
		ruccliente = picking_out_obj.partner_id.type_number
		result_detalle = []
		for items in picking_out_obj.move_lines:
			result_detalle.append(
					{
					"dest": items.partner_id.street,
					"origin": items.location_id.partner_id.street,
					}
				)
			break		
		if picking_out_obj.partner_id.is_company and not picking_out_obj.partner_id.supplier:
			ruccliente = picking_out_obj.partner_id.parent_id.type_number
		print 'street', picking_out_obj.partner_id.street
		if picking_out_obj.partner_id.street == False:
			raise osv.except_osv('Alerta', 'Debe configurar una direccion para el cliente ' + picking_out_obj.partner_id.name)
		if ntot==0:
			query = """
				SELECT picking_id, po.id FROM stock_picking p, stock_move m, purchase_order_line pol, purchase_order po
				WHERE p.id = """ + str(picking_out_obj.id) + """ and po.id = pol.order_id and pol.id = m.purchase_line_id and m.picking_id = p.id
				GROUP BY picking_id, po.id
			"""
			cr.execute(query)
			order_ids = cr.fetchall()
			order_id = False
			for pick_id, po_id in order_ids:
				order_id = po_id
			order = self.pool.get('purchase.order').browse(cr, uid, order_id, context)
			for line in order.order_line:
				ntot=ntot+line.price_subtotal
			tipo_cambio = 1.0
			if company_attrs.currency_id != order.currency_id.id:
				if factura.date_invoice == False:
					raise osv.except_osv('Alerta!', 'La factura de este pedido debe tener una fecha configurada')
				rate_ids = self.pool.get('res.currency.rate').search(cr, uid, [('currency_id','=',factura.currency_id.id),('date_sunat', '=', factura.date_invoice)])
				if len(rate_ids) == 0:
					raise osv.except_osv('Alerta!', 'No existe un tipo de cambio para la fecha: ' + factura.date_invoice)
				rate_obj = self.pool.get('res.currency.rate').browse(cr, uid, rate_ids[0], context)
				tipo_cambio = rate_obj.type_sale
			#tipo_cambio = factura.currency_rate_mod if factura.currency_rate_mod != 0.00 else factura.currency_rate_auto
			
			#raise osv.except_osv('Alerta!', 'LOL')
			ntot = ntot*tipo_cambio




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
				"refunds":self.get_refunds(cr,uid,ids,context),
				"total_refound":self.get_total(cr,uid,ids,context),
				"neto":round(ntot-self.get_total(cr,uid,ids,context),3)
				}
			)
		txt=""
		#txt=txt+chr(27)+chr(15)+chr(27)+chr(48)
		for r in result:
			txt=txt+r['name_company']+" "*14+'N O T A  D E  I N G R E S O'+" "*6+"Nro.: "+r['name']+"\n"
			txt=txt+"FECHA: "+r['date']+"\n"
			txt=txt+"Recibimos de: "+r['name_partner']+"\n"
			txt=txt+"Direccion: "+r['street_partner'][:90]+"\n"
			txt=txt+"Referencia: "+r['numfact']+"  Pedido: "+r['origin']+"\n"
			#txt=txt+"\n"
			if r['ruc_partner']:
				ruc = r['ruc_partner']
			else:
				ruc = ''
			txt=txt+"RUC: "+ruc+" "*5+"Tipo de Cambio: "
			if r['tipodecambio']:
				tcambio = str(r['tipodecambio']) 
			else:
				tcambio = ''
			txt=txt+tcambio+"\n"
			txt=txt+"Codigo"+" "*2+"Cantidad"+" "*3+"Unidad"+" "*3+"Descripcion"+" "*10+"V. Unitario"+" "+"Total"+"\n"
			txt=txt+"-"*80+"\n"
			t_total=0.00
			ntotcantidad=0
			for linea in r['lineas']:
				# raise osv.except_osv('Alerta', self.eliminarAcentos(linea["product_name"]))
				# raise osv.except_osv('Alerta', linea["product_name"].replace('ñ'.decode('utf-8'),'n'))
				c=str(round(linea["vunit"],6)).split('.')
				ct=str(round(linea["price_subtotal"],3)).split('.')
				cad=''
				cadt=''
				if len(c)>0:
					cad=cad+c[0]+'.'+c[1].ljust(6,'0')
				else:
					cad=str(round(linea["vunit"],6))
				if len(ct)>0:
					cadt=cadt+ct[0]+'.'+ct[1].ljust(3,'0')
				else:
					cadt=str(round(linea["price_subtotal"],3))
					
				txt=txt+str(linea["cod_product"]).ljust(8)+" "*2+str(linea["qty"]).rjust(8)+" "+str(linea["unit"]).ljust(8)+" "+unicode(linea["product_name"][0:30]).ljust(30)+" "+cad.rjust(12)+" "+cadt.rjust(12)+"\n"
				t_total=t_total+round(linea["price_subtotal"],3)
				ntotcantidad=ntotcantidad+linea["qty"]
			txt=txt+"\n"
			ct=str(round(t_total,3)).split('.')
			cadt=''
			if len(ct)>0:
				cadt=cadt+ct[0]+'.'+ct[1].ljust(3,'0')
			else:
				cadt=str(round(t_total,3))
			txt=txt+" "*2+"Total cant: "+str(ntotcantidad)+" "*45+" Total: "+cadt.rjust(12)+"\n"
			txt=txt+"\n"
			if len(r["refunds"])>0:
				txt=txt+"N O T A S   D E   C R E D I T O"+"\n"
				txt=txt+"Fecha"+" "*25+"Nro. Nota de credito"+" "*64+"Importe"+"\n"
				txt=txt+"-"*80+"\n"
				for refund in r["refunds"]:
					ct=str(round(refund["total"],3)).split('.')
					cadt=''
					if len(ct)>0:
						cadt=cadt+ct[0]+'.'+ct[1].ljust(3,'0')
					else:
						cadt=str(round(refund["total"],3))
					txt=txt+str(refund['fecha'])+" "*2+str(refund["numdoc"])+" "*2+cadt.rjust(12)+"\n"
			ct=str(round(r['total_refound'],3)).split('.')
			cadt=''
			if len(ct)>0:
				cadt=cadt+ct[0]+'.'+ct[1].ljust(3,'0')
			else:
				cadt=str(round(r['total_refound'],3))
			txt=txt+"\n"
			txt=txt+" "*62+"Total N/C:"+cadt.rjust(12)+"\n"
			txt=txt+"\n"
			ct=str(round(r['neto'],3)).split('.')
			cadt=''
			if len(ct)>0:
				cadt=cadt+ct[0]+'.'+ct[1].ljust(3,'0')
			else:
				cadt=str(round(r['neto'],3))
			txt=txt+" "*60+"Total NETO:"+cadt.rjust(12)+"\n"
			txt=txt+"\n"
			txt=txt+"\n"
			txt=txt+"\n"
			txt=txt+"\n"
			txt=txt+" -----------------  -----------------  -----------------  -----------------"+"\n"
			#txt=txt+" "+"Recibido almacen"+" "*15+"Entregado por:"+" "*15+"Revizado por:"+"\n"
			txt=txt+" "+"VoBo Felasac"+" "*10+"Vendedor"+" "*12+"Vigilancia"+" "*10+"Administracion"+"\n"
			#txt=txt+" "+"Nombre"+" "*18+"Nombre"+" "*18+"Nombre"+"\n"
			#txt=txt+chr(12)


		return unicode(txt)

	def get_total(self, cr, uid, ids, context=None):
		result = []
		active_id = ids[0]
		picking_out_obj = self.pool.get('stock.picking').browse(cr, uid, active_id)

		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		result1 = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree2')

		id = result1 and result1[1] or False
		result1 = act_obj.read(cr, uid, [id], context=context)[0]

		inv_ids = []
		
		
		if picking_out_obj.invoice_id.id == False:
			query = """
				SELECT picking_id, po.id FROM stock_picking p, stock_move m, purchase_order_line pol, purchase_order po
				WHERE p.id = """ + str(picking_out_obj.id) + """ and po.id = pol.order_id and pol.id = m.purchase_line_id and m.picking_id = p.id
				GROUP BY picking_id, po.id
			"""
			cr.execute(query)
			order_ids = cr.fetchall()
			order_id = False
			for pick_id, po_id in order_ids:
				order_id = po_id
			order = self.pool.get('purchase.order').browse(cr, uid, order_id, context)
			
			if len(order.invoice_ids)!=0:
				in_ids = order.invoice_ids
			else:
				return 0
			#raise osv.except_osv('Alerta', 'Este elemento no está relacionado con una compra por lo que no se imprime\nla nota de ingreso')
			invoice_id = in_ids[0].id
		else:
			invoice_id = picking_out_obj.invoice_id.id
		factura_ids = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
		
		'''
		if picking_out_obj.invoice_id.id == False:
			raise osv.except_osv('Alerta', 'Este elemento no está relacionado con una compra por lo que no se imprime\nla nota de ingreso')
			
		factura_ids = self.pool.get('account.invoice').browse(cr, uid, [picking_out_obj.invoice_id.id], context=context)
		'''
		#factura_id = self.pool.get('purchase.order').browse(cr, uid, [picking_out_obj.purchase_id.id], context=context)[0]
		#compra = self.pool.get('purchase.order').get_invoice(cr, uid, [picking_out_obj.purchase_id.id])
		#factura_ids = self.pool.get('account.invoice').browse(cr, uid, compra, context=context)
		
		tot_refound=0
		for factura in factura_ids:
			
			if factura.type=="in_refund":
				# raise osv.except_osv('Alerta', factura.supplier_invoice_number)
				# raise osv.except_osv('Alerta', compra)
				tot_refound=tot_refound+factura.amount_untaxed
		return tot_refound

	def get_refunds(self, cr, uid, ids, context=None):
		result = []
		active_id = ids[0]
		picking_out_obj = self.pool.get('stock.picking').browse(cr, uid, active_id)
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		result1 = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree2')
		id = result1 and result1[1] or False
		result1 = act_obj.read(cr, uid, [id], context=context)[0]
		inv_ids = []
		
		
		if picking_out_obj.invoice_id.id == False:
			query = """
				SELECT picking_id, po.id FROM stock_picking p, stock_move m, purchase_order_line pol, purchase_order po
				WHERE p.id = """ + str(picking_out_obj.id) + """ and po.id = pol.order_id and pol.id = m.purchase_line_id and m.picking_id = p.id
				GROUP BY picking_id, po.id
			"""
			cr.execute(query)
			order_ids = cr.fetchall()
			order_id = False
			for pick_id, po_id in order_ids:
				order_id = po_id
			order = self.pool.get('purchase.order').browse(cr, uid, order_id, context)
				
			if len(order.invoice_ids)!=0:
				in_ids = order.invoice_ids
			else:
				return result
			#raise osv.except_osv('Alerta', 'Este elemento no está relacionado con una compra por lo que no se imprime\nla nota de ingreso')
			invoice_id = in_ids[0].id
		else:
			invoice_id = picking_out_obj.invoice_id.id
		factura_ids = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
		
		'''
		if picking_out_obj.invoice_id.id == False:
			raise osv.except_osv('Alerta', 'Este elemento no está relacionado con una compra por lo que no se imprime\nla nota de ingreso')
			
		factura_ids = self.pool.get('account.invoice').browse(cr, uid, [picking_out_obj.invoice_id.id], context=context)
		'''
		#factura_id = self.pool.get('purchase.order').browse(cr, uid, [picking_out_obj.purchase_id.id], context=context)[0]
		#compra = self.pool.get('purchase.order').get_invoice(cr, uid, [picking_out_obj.purchase_id.id])
		#factura_ids = self.pool.get('account.invoice').browse(cr, uid, compra, context=context)
		# raise osv.except_osv('Alerta', len(factura_ids))
		# refund_ids = self.pool.get('account.invoice').search(cr,uid,[('')])
		for factura_r in factura_ids:
			tot_refound=0
			# factura_r = self.pool.get('account.invoice').browse(cr, uid,fact, context=context)					  
			# raise osv.except_osv('Alerta', factura_r.type)
			if factura_r.type!="in_refund":
				continue
			# raise osv.except_osv('Alerta', factura_r.type)
			result.append(
					{
					"fecha": factura_r.date_invoice,
					"numdoc": factura_r.supplier_invoice_number if factura_r.supplier_invoice_number else 'No especificado',
					"total": factura_r.amount_untaxed,
					}
				)
			tot_refound=tot_refound+factura_r.amount_untaxed
			#result.append(
			#			{
			#			"fecha": '',
			#			"numdoc": 'TOTAL de N/C',
			#			"total": tot_refound,
			#			}
			#		)
		# raise osv.except_osv('Alerta', result)
		return result


	def get_detalle(self, cr, uid, ids, context=None):

		result = []
		active_id = ids[0]

		picking_out_obj = self.pool.get('stock.picking').browse(cr, uid, active_id)
		company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=context)
		company_attrs = helper.company(cr, uid, company_id) #atributos company
		
		concatena_col = ''
		concatena_col_dos = ''

		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		result1 = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree2')

		id = result1 and result1[1] or False
		result1 = act_obj.read(cr, uid, [id], context=context)[0]

		inv_ids = []
		lfactura = False

		if picking_out_obj.invoice_id.id == False:
			query = """
				SELECT picking_id, po.id FROM stock_picking p, stock_move m, purchase_order_line pol, purchase_order po
				WHERE p.id = """ + str(picking_out_obj.id) + """ and po.id = pol.order_id and pol.id = m.purchase_line_id and m.picking_id = p.id
				GROUP BY picking_id, po.id
			"""

			cr.execute(query)
			order_ids = cr.fetchall()
			order_id = False
			for pick_id, po_id in order_ids:
				order_id = po_id
			order = self.pool.get('purchase.order').browse(cr, uid, order_id, context)
			in_ids = order.invoice_ids
			# raise osv.except_osv('Alerta',in_ids)
			if len(in_ids)!=0:
				lfactura = True
				invoice_id = in_ids[0].id
			else:
				lfactura = False
				invoice_id=None
		else:
			lfactura = True
			invoice_id = picking_out_obj.invoice_id.id
		facturas = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
		
		
		result_detalle = []
		uom_obj = self.pool.get('product.uom')
		# raise osv.except_osv('Alerta', compra)  
		
		for factura in facturas:
			lfactura = True
			if factura.type =="in_invoice" and factura.state!='cancel':
				for items in factura.invoice_line:
					tipo_cambio = 1.0
					if company_attrs.currency_id != factura.currency_id.id:
						if factura.date_invoice == False:
							raise osv.except_osv('Alerta!', 'La factura de este pedido debe tener una fecha configurada')
						rate_ids = self.pool.get('res.currency.rate').search(cr, uid, [('currency_id','=',factura.currency_id.id),('date_sunat', '=', factura.date_invoice)])
						if len(rate_ids) == 0:
							raise osv.except_osv('Alerta!', 'No existe un tipo de cambio para la fecha: ' + factura.date_invoice)
						rate_obj = self.pool.get('res.currency.rate').browse(cr, uid, rate_ids[0], context)
						tipo_cambio = rate_obj.type_sale
					
					
					#tipo_cambio = factura.currency_rate_mod if factura.currency_rate_mod != 0.00 else factura.currency_rate_auto
					precio_unitario = (items.price_subtotal/items.quantity)*tipo_cambio
					# raise osv.except_osv('Alerta', "%0.3f" % precio_unitario)  
					cantidad = uom_obj._compute_qty(cr, uid, items.uos_id.id, items.quantity,items.product_id.uom_id.id )
					preuni = uom_obj._compute_price(cr, uid, items.uos_id.id, precio_unitario,items.product_id.uom_id.id )
					if items.product_id.id:
						result_detalle.append(
							{
							"cod_product": items.product_id.default_code,
							"product_name": items.product_id.product_tmpl_id.name[:34],
							"qty": round(cantidad,3),
							"unit": items.product_id.uom_id.name,
							"vunit": preuni,
							"price_subtotal":round(preuni*cantidad,6),
							}
					)					



		if lfactura==False:
			query = """
				SELECT picking_id, po.id FROM stock_picking p, stock_move m, purchase_order_line pol, purchase_order po
				WHERE p.id = """ + str(picking_out_obj.id) + """ and po.id = pol.order_id and pol.id = m.purchase_line_id and m.picking_id = p.id
				GROUP BY picking_id, po.id
			"""
			cr.execute(query)
			order_ids = cr.fetchall()
			order_id = False
			for pick_id, po_id in order_ids:
				order_id = po_id
			order = self.pool.get('purchase.order').browse(cr, uid, order_id, context)
			

			tipo_cambio = 1.0
			if company_attrs.currency_id != order.currency_id.id:
				if factura.date_invoice == False:
					raise osv.except_osv('Alerta!', 'La factura de este pedido debe tener una fecha configurada')
				rate_ids = self.pool.get('res.currency.rate').search(cr, uid, [('currency_id','=',factura.currency_id.id),('date_sunat', '=', factura.date_invoice)])
				if len(rate_ids) == 0:
					raise osv.except_osv('Alerta!', 'No existe un tipo de cambio para la fecha: ' + factura.date_invoice)
				rate_obj = self.pool.get('res.currency.rate').browse(cr, uid, rate_ids[0], context)
				tipo_cambio = rate_obj.type_sale
			#tipo_cambio = factura.currency_rate_mod if factura.currency_rate_mod != 0.00 else factura.currency_rate_auto
			for items in order.order_line:
			#raise osv.except_osv('Alerta!', 'LOL')
				# ntot = ntot*tipo_cambio
				precio_unitario = (items.price_subtotal/items.product_qty)*tipo_cambio
				# raise osv.except_osv('Alerta', "%0.3f" % precio_unitario)  
				cantidad = uom_obj._compute_qty(cr, uid, items.product_uom.id, items.product_qty,items.product_id.uom_id.id )
				preuni = uom_obj._compute_price(cr, uid, items.product_uom.id, precio_unitario,items.product_id.uom_id.id )

				result_detalle.append(
						{
						"cod_product": items.product_id.default_code,
						"product_name": items.product_id.product_tmpl_id.name[:34],
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
	def	eliminarAcentos(self,cadena):

		d	=	{	'Á':'A',
			'É':'E',
			'Í':'I',
			'Ó':'O',
			'Ú':'U',
			'Ü':'U',
			'Ñ':'N',
			'Ç':'C',
			'í':'i',
			'ó':'o',
			'ñ':'n',
			'ç':'c',
			'á':'a',
			'à':'a',
			'ä':'a',
			'é':'e',
			'è':'e',
			'ë':'e',
			'í':'i',
			'ì':'i',
			'ï':'i',
			'ó':'o',
			'ò':'o',
			'ö':'o',
			'ù':'u',
			'ú':'u',
			'ü':'u',
		}
 		
		nueva_cadena=cadena
		# raise osv.except_osv('Alerta', nueva_cadena.replace('ñ','n'))
		for	c in d.keys():
			nueva_cadena=nueva_cadena.replace(c.decode('utf-8'),d[c])
		auxiliar	=	nueva_cadena.encode('utf-8')
		return	nueva_cadena