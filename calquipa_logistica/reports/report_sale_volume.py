# -*- encoding: utf-8 -*-
import base64,codecs,pprint,string
from openerp import models, fields, api, exceptions
from datetime import datetime,timedelta

class ReportSaleVolumeWizard(models.TransientModel):
	_name='report.sale.volume.wizard'
	start_date = fields.Date(string='Fecha Inicio',default=datetime.now().date())
	end_date   = fields.Date(string='Fecha Fin',default=datetime.now().date())
	 
	@api.multi
	def do_rebuild(self):
		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		path = self.env['main.parameter'].search([])[0].dir_create_file
		file_name = u'Reporte de Ventas por Volúmenes.xlsx'
		path+=file_name
		workbook = Workbook(path)
		worksheet = workbook.add_worksheet("Reporte")
		worksheet.set_landscape() #Horizontal
		worksheet.set_paper(9) #A-4
		worksheet.set_margins(left=0.75, right=0.75, top=1, bottom=1)
		worksheet.fit_to_pages(1, 0)  # Ajustar por Columna	
		bold = workbook.add_format({'bold': True})
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(9)
		boldbord.set_bg_color('#DCE6F1')
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		bord = workbook.add_format()
		bord.set_border(style=1)
		bord.set_text_wrap()
		numberdos_bold = workbook.add_format({'num_format':'0.00','bold': True})
		numberdos_bold.set_border(style=1)
		numberdos_bold.set_bg_color('#DCE6F1')
		numbertres.set_border(style=1)	
		title = workbook.add_format({'bold': True})
		title.set_align('center')
		title.set_align('vcenter')
		title.set_text_wrap()
		title.set_font_size(20)
		worksheet.set_row(0,30)
		boldborda = workbook.add_format({'bold': True})
		boldborda.set_border(style=2)
		boldborda.set_align('center')
		boldborda.set_align('vcenter')
		boldborda.set_text_wrap()
		boldborda.set_font_size(9)
		boldborda.set_bg_color('#ffff40')

		x=5		
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		worksheet.merge_range(1,1,0,7, u"Reporte de Ventas por Volúmenes",title)
		worksheet.write(2,1, u"FECHA DEL:",bold)
		worksheet.write(2,2, self.start_date,bold)
		worksheet.write(2,3, u"AL",bold)
		worksheet.write(2,4, self.end_date,bold)
		worksheet.write(4,0, u"CLIENTE",boldbord)
		worksheet.write(4,1, u"PEDIDO DE VENTA",boldbord)
		worksheet.write(4,2, u"EXPORTACIÓN",boldbord)
		worksheet.write(4,3, u"FEC. PEDIDO DE VENTA",boldbord)
		worksheet.write(4,4, u"TIPO DE DOCUMENTO",boldbord)
		worksheet.write(4,5, u"FACTURA",boldbord)
		worksheet.write(4,6, u"FECHA FACTURA",boldbord)
		worksheet.write(4,7, u"PRODUCTO",boldbord)
		worksheet.write(4,8, u"PRECIO UNITARIO USD",boldbord)
		worksheet.write(4,9, u"CANTIDAD TRANSP.",boldbord)
		worksheet.write(4,10, u"UNIDAD",boldbord)
		worksheet.write(4,11, u"ALBARÁN DE SALIDA",boldbord)
		worksheet.write(4,12, u"GUIA REMISIÓN TRANSPORTISTA",boldbord)
		worksheet.write(4,13, u"TRANSPORTISTA",boldbord)
		worksheet.write(4,14, u"SERVICIO",boldbord)
		worksheet.write(4,15, u"RUTA",boldbord)
		worksheet.write(4,16, u"COSTO UNITARIO TRANSPORTE",boldbord)
		worksheet.write(4,17, u"SUBTOTAL",boldbord)
		worksheet.write(4,18, u"PROMEDIO",boldbord)

		invoices = self.env['account.invoice'].search([('date_invoice','<=',self.end_date),('date_invoice','>=',self.start_date),('state','in',('open','paid')),('type','=','out_invoice')])
		refund = self.env['account.invoice'].search([('type','=','out_refund'),('state','in',('open','paid'))])

		lines  = []
		resume = []
		for i in invoices.mapped('invoice_line'):
			lines.append(i)
			match = refund.filtered(lambda x: i.invoice_id.number in x.account_ids.mapped('comprobante'))
			if match:
				lines.append(match.mapped('invoice_line'))
		for line in lines:
			picks = self.env['stock.picking'].search([('name','=',line.invoice_id.origin)])
			if picks:
				for move in picks.mapped('move_lines').filtered(lambda x: x.product_id == line.product_id):
					vals = {}
					so=self.env['sale.order'].search([('name','=',move.picking_id.origin)])
					worksheet.write(x,0,line.invoice_id.partner_id.name)
					worksheet.write(x,1,so.name or '')
					worksheet.write(x,2,so.exportacion or '')
					worksheet.write(x,3,so.date_order[:10] or '')
					type_doc = line.invoice_id.type_document_id.code+'-'+line.invoice_id.type_document_id.description
					worksheet.write(x,4,type_doc)
					worksheet.write(x,5,line.invoice_id.number)
					worksheet.write(x,6,line.invoice_id.date_invoice[:10]) # fecha factura
					worksheet.write(x,7,line.product_id.name)
					price_unit1 = line.price_unit*1000
					if line.invoice_id.currency_id.name=='PEN':
						price_unit1 = self.get_exchange(line.invoice_id.date_invoice[:10],price_unit1)
					worksheet.write(x,8,price_unit1,numberdos)
					worksheet.write(x,9,move.product_qty,numberdos)
					
					vals['quantity'] = move.product_qty # add
					vals['amount']   = move.product_qty * price_unit1 # add
					vals['with_transp'] = True
					vals['product'] = line.product_id.name

					worksheet.write(x,10,move.product_id.uom_id.name)
					worksheet.write(x,11,move.picking_id.name)
					worksheet.write(x,12,move.picking_id.guia_remision or '')
					worksheet.write(x,13,move.picking_id.transportista_id.name or '')
					sotl = self.env['sale.order.transporte.linea'].search([('product_id','=',move.product_id.id),('order_id','=',so.id)])
					tarifa = self.env['logistica.transporte.tarifa'].search([('partner_id','=',so.partner_id.id)])
					
					lttl = self.env['logistica.transporte.tarifa.linea'].search([('transportista_id','=',move.picking_id.transportista_id.id),('transporte_tarifa_id','=',tarifa.id),('transporte_tipo_id','=',sotl.tipo_transporte_id.id),('ruta_id','=',sotl.ruta_nacional_id.id)])

					worksheet.write(x,14,lttl.descripcion if lttl.descripcion else '')
					origen = lttl.ruta_id.origen or ''
					destino = lttl.ruta_id.destino or ''
					worksheet.write(x,15,origen+' - '+destino)
					price_unit= lttl.precio_unitario or 0
					worksheet.write(x,16,price_unit*-1 if line.invoice_id.type == 'out_refund' else price_unit,numberdos)
					subtotal = price_unit*move.product_qty
					if line.invoice_id.type=='out_refund':
						subtotal = subtotal*-1
					worksheet.write(x,17,subtotal,numberdos)
					
					vals['trasp_cost'] = subtotal
					
					sl = so.order_line.filtered(lambda x: x.product_id == move.product_id)
					if lttl and sl:
						prom=float((sl.price_unit*1000*move.product_qty)-(price_unit*move.product_qty)) / move.product_qty
						worksheet.write(x,18,prom*-1 if line.invoice_id.type == 'out_refund' else prom,numberdos)
					resume.append(vals)
					x+=1

			else:
				vals = {}
				worksheet.write(x,0,line.invoice_id.partner_id.name)
				type_doc = line.invoice_id.type_document_id.code+'-'+line.invoice_id.type_document_id.description
				worksheet.write(x,4,type_doc)
				worksheet.write(x,5,line.invoice_id.number)
				worksheet.write(x,6,line.invoice_id.date_invoice[:10]) # fecha factura
				worksheet.write(x,7,line.product_id.name)
				price_unit1 = line.price_unit*1000
				if line.invoice_id.currency_id.name=='PEN':
					price_unit1 = self.get_exchange(line.invoice_id.date_invoice[:10],price_unit1)
				worksheet.write(x,8,price_unit1,numberdos)
				qty = float(line.quantity)/1000
				if line.invoice_id.type == 'out_refund':
					qty = qty*-1
				worksheet.write(x,9,qty,numberdos)
				vals['quantity'] = qty # add
				vals['amount']   = qty * price_unit1 # add
				vals['with_transp'] = False
				vals['product'] = line.product_id.name
				vals['trasp_cost'] = 0
				worksheet.write(x,10,line.product_id.uom_id.name)
				resume.append(vals)
				x+=1
				

		tam_col = [40,9,20,11,19,16,11,27,12,12,9,18,13,30,38,22,10,10,10]
		alpha = list(string.ascii_uppercase)
		for i,item in enumerate(tam_col):
			worksheet.set_column(alpha[i]+':'+alpha[i],item)

		# segunda parte del reporte
		worksheet = workbook.add_worksheet("RESUMEN")
		worksheet.set_landscape() #Horizontal
		worksheet.set_paper(9) #A-4
		worksheet.set_margins(left=0.75, right=0.75, top=1, bottom=1)
		worksheet.fit_to_pages(1, 0)  # Ajustar por Columna
		worksheet.merge_range(1,1,0,7, u"CALQUIPA S.A.C.",title)
		worksheet.write(2,2,U'EXPRESADO EN DÓLARES AMERICANOS')
		x=8
		worksheet.merge_range(6,1,7,1,u"Clasificación",boldbord)
		worksheet.merge_range(6,2,6,4,u"DEL "+self.start_date+' AL '+self.end_date,boldbord)
		worksheet.write(7,2, u"Importe TN",boldbord)
		worksheet.write(7,3, u"Importe USD",boldbord)
		worksheet.write(7,4, u"Precio Prom. USD",boldbord)
		
		allowed = ('OXID  PULVERIZADO','OXID  GRANULADO')# por si se jode
		
		other  = list(filter(lambda c: c['product'] not in allowed,resume))
		resume = list(filter(lambda c: c['product'] in allowed,resume))
		products = list(map(lambda x: x['product'],resume))
		products=set(products)
		total_qty = total_amount = 0 
		
		# primer total
		for prod in products:
			filt = list(filter(lambda x: x['product']==prod,resume))
			quantity = sum(map(lambda x: x['quantity'],filt))
			amount   = sum(map(lambda x: x['amount'],filt))
			prom     = float(amount)/quantity
			worksheet.write(x,1,prod)
			worksheet.write(x,2,quantity,numberdos)
			worksheet.write(x,3,amount,numberdos)
			worksheet.write(x,4,prom,numberdos)
			total_qty+=quantity
			total_amount+=amount
			x+=1

		worksheet.write(x,1,'TOTAL',boldbord)
		worksheet.write(x,2,total_qty,numberdos_bold)
		worksheet.write(x,3,total_amount,numberdos_bold)
		worksheet.write(x,4,float(total_amount)/total_qty,numberdos_bold)
		
		if any(other):
			x+=2
			worksheet.write(x,2,'Otros')
			other_amount=sum(map(lambda x: x['amount'],other))
			worksheet.write(x,3,other_amount,numberdos)
			x+=1
			worksheet.write(x,2,'TOTAL',bold)
			worksheet.write(x,3,other_amount+total_amount,numberdos)
		
		x+=6
		# segundo total
		worksheet.merge_range(x,1,x+1,1,u"Clasificación",boldbord)
		worksheet.merge_range(x,2,x,6,u"DEL "+self.start_date+' AL '+self.end_date,boldbord)
		worksheet.write(x+1,2, u"Condición",boldbord)
		worksheet.write(x+1,3, u"Volumen TN",boldbord)
		worksheet.write(x+1,4, u"Importe USD",boldbord)
		worksheet.write(x+1,5, u"Coste Transporte",boldbord)
		worksheet.write(x+1,6, u"Neto USD",boldbord)
		x+=2
		
		total_qty = total_amount = total_tansp_cost = 0 
		for prod2 in products:
			filt1 = list(filter(lambda x:x['product']==prod2 and x['with_transp'],resume))
			if not any(filt1):
				continue
			quantity   = sum(map(lambda x: x['quantity'],filt1))
			amount     = sum(map(lambda x: x['amount'],filt1))
			trasp_cost = sum(map(lambda x: x['trasp_cost'],filt1))
			neto = float(amount-trasp_cost)/quantity
			worksheet.write(x,1,prod2)
			worksheet.write(x,2,'con transporte')
			worksheet.write(x,3,quantity,numberdos)
			worksheet.write(x,4,amount,numberdos)
			worksheet.write(x,5,trasp_cost,numberdos)
			worksheet.write(x,6,neto,numberdos)
			total_qty+=quantity
			total_amount+=amount
			total_tansp_cost+=trasp_cost
			x+=1

		x+=2
		for prod3 in products:
			filt1 = list(filter(lambda x:x['product']==prod3 and not x['with_transp'],resume))
			if not any(filt1):
				continue
			quantity   = sum(map(lambda x: x['quantity'],filt1))
			amount     = sum(map(lambda x: x['amount'],filt1))
			trasp_cost = sum(map(lambda x: x['trasp_cost'],filt1))
			neto = float(amount)/quantity
			worksheet.write(x,1,prod3)
			worksheet.write(x,2,'sin transporte')
			worksheet.write(x,3,quantity,numberdos)
			worksheet.write(x,4,amount,numberdos)
			worksheet.write(x,6,neto,numberdos)
			total_qty+=quantity
			total_amount+=amount
			x+=1
		
		worksheet.merge_range(x,1,x,2,'TOTAL',boldbord)
		worksheet.write(x,3,total_qty,numberdos_bold)
		worksheet.write(x,4,total_amount,numberdos_bold)
		worksheet.write(x,5,total_tansp_cost,numberdos_bold)
		worksheet.write(x,6,float(total_amount-total_tansp_cost)/total_qty,numberdos_bold)
		if any(other):
			x+=2
			worksheet.write(x,3,'Otros')
			other_amount=sum(map(lambda x: x['amount'],other))
			worksheet.write(x,4,other_amount,numberdos)
			x+=1
			worksheet.write(x,3,'TOTAL',bold)
			worksheet.write(x,4,other_amount+total_amount,numberdos)
		
		tam_col = [8,32,15,15,15,15,15]
		alpha = list(string.ascii_uppercase)
		for i,item in enumerate(tam_col):
			worksheet.set_column(alpha[i]+':'+alpha[i],item)
		workbook.close()
		f = open( path, 'rb')
		sfs_id = self.env['export.file.save'].create({
			'output_name': file_name,
			'output_file': base64.encodestring(''.join(f.readlines())),		
		})
		return {
			"type": "ir.actions.act_window",
			"res_model": "export.file.save",
			"views": [[False, "form"]],
			"res_id": sfs_id.id,
			"target": "new",
		}

	def get_exchange(self,date,amount):
		exch = self.env['res.currency.rate'].search([('name','=',date),('currency_id.name','=','USD')])
		if not exch:
			raise exceptions.Warning(u'No se  ha encontrado tipo de cambio para la fecha '+date)
		return float(amount)/exch[0].type_sale
