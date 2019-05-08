# -*- encoding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs
from datetime import datetime

class reporte_costo_venta_wizard(osv.TransientModel):
	_name='reporte.costo.venta.wizard'
	config_product = fields.Many2one('config.products.costs.report','Config Product')
	period = fields.Many2one('account.period', string='Periodo')
	all_products = fields.Boolean('Todos los productos') 

	@api.multi
	def do_rebuild(self):		
		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion +'Reporte_Costo_Venta.xlsx')
		worksheet = workbook.add_worksheet("Reporte de Facturas y pagos")
		bold = workbook.add_format({'bold': True})
		normal = workbook.add_format()
		title1 = workbook.add_format({'bold':True})
		title1.set_align('center')
		title1.set_font_size(12)
		title1.set_bg_color('#ebebe0')
		title1.set_font_color('#3399FF')
		title1.set_text_wrap()
		title2 = workbook.add_format({'bold':True})
		title2.set_align('center')
		title2.set_font_size(10)
		title2.set_bg_color('#F2F2F2')
		title2.set_font_color('#3399FF')
		title2.set_text_wrap()
		title3 = workbook.add_format({'bold':True})
		title3.set_align('center')
		title3.set_font_size(10)
		title3.set_bg_color('#F2F2F2')
		title3.set_font_color('#b566ff')
		title3.set_text_wrap()
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		numberdos_b = workbook.add_format({'num_format':'0.00','bold':True})
		bord = workbook.add_format()
		bord.set_border(style=1)
		numberdos.set_border(style=1)
		numberdos_b.set_border(style=1)
		numbertres.set_border(style=1)			
		x= 5				
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		products = None
		date_ini = self.period.date_start
		date_fin = self.period.date_stop
		aux_width = 0
		worksheet.merge_range(1,0,1,1,'REPORTE COSTO DE VENTA', title1)
		worksheet.write(2,0,'PRODUCTO:', title1)
		worksheet.write(3,0,'MES:', title1)
		worksheet.write(3,1,self.period.code, title1)
		if self.all_products:
			products = self.env['config.products.costs.report'].search([]).mapped('product_id')
			worksheet.write(2,1,'TODOS', title1)
		else:
			products = self.config_product.product_id
			worksheet.merge_range(2,1,2,2,products.name, title1)
		for prod in products:
			self.env.cr.execute("""
			select 
			distinct sm.location_dest_id
			from
			stock_move sm 
			join stock_picking sp on sp.id = sm.picking_id
			join stock_location sl on sl.id = sm.location_dest_id
			where sm.product_id = """+str(prod.id)+""" 
			and sp.state = 'done'
			and sp.date::date >= '"""+date_ini+"""' 
			and sp.date::date <= '"""+date_fin+"""'
			and sl.usage = 'internal'
			union 
			select 
			distinct sm.location_id
			from
			stock_move sm 
			join stock_picking sp on sp.id = sm.picking_id
			join stock_location sl on sl.id = sm.location_id
			where sm.product_id = """+str(prod.id)+""" and sp.state = 'done'
			and sp.date::date >= '"""+date_ini+"""'
			and sp.date::date <= '"""+date_fin+"""'
			and sl.usage = 'internal'
			""")
			locations = self.env.cr.fetchall()
			conf = self.env['main.parameter'].search([])[0]
			acum_totales = [[0,0] for i in range(9)]
			locations = self.env['stock.location'].browse(map(lambda x: x[0],locations))
			worksheet.write(x,0,"ALMACEN", title2)
			worksheet.write(x+1,0,prod.name, title1)
			worksheet.write(x+2,0,"Inventario Inicial", normal)
			worksheet.write(x+3,0,"Produccion", normal)
			worksheet.write(x+4,0,"Ingreso por transferencias", normal)
			worksheet.write(x+5,0,"Disponible", normal)
			worksheet.write(x+6,0,"Traspaso a Micronizado", normal)
			worksheet.write(x+7,0,"COSTO DE VENTAS", bold)
			worksheet.write(x+8,0,"Otros", normal)
			worksheet.write(x+9,0,"Transferencias Internas", normal)
			worksheet.write(x+10,0,"Inventario Final", normal)
			aux = 1
			y = 0
			for loc in locations:
				ton,imp,prom = 0,0,0
				y = x + 1 # y caminador auxiliar
				ton_acum,imp_acum,prom_acum = 0,0,0
				worksheet.merge_range(x,aux,x,aux+3,self.get_name_location(loc.complete_name),title2)
				worksheet.write(y,aux,'Toneladas', title3)
				worksheet.write(y,aux+1,'Importe', title3)
				worksheet.write(y,aux+2,'Costo Promedio', title3)
				if aux_width < len(locations):
					aux_width = len(locations)
				
				y+=1
				ton,imp,prom = self.get_inv_ini(loc.id,prod.id,conf)
				worksheet.write(y,aux,ton, numberdos)
				worksheet.write(y,aux+1,imp, numberdos)
				worksheet.write(y,aux+2,prom, numberdos)
				ton_acum+=ton
				acum_totales[0][0]+=ton
				imp_acum+=imp
				acum_totales[0][1]+=imp

				y+=1
				ton,imp,prom = self.get_prod_data(loc.id,prod.id,conf)
				worksheet.write(y,aux,ton, numberdos)
				worksheet.write(y,aux+1,imp, numberdos)
				worksheet.write(y,aux+2,prom, numberdos)
				ton_acum+=ton
				acum_totales[1][0]+=ton
				imp_acum+=imp
				acum_totales[1][1]+=imp

				y+=1
				ton,imp,prom = self.get_ingre_trans(loc.id,prod.id,conf)
				worksheet.write(y,aux,ton, numberdos)
				worksheet.write(y,aux+1,imp, numberdos)
				worksheet.write(y,aux+2,prom, numberdos)
				ton_acum+=ton
				acum_totales[2][0]+=ton
				imp_acum+=imp
				acum_totales[2][1]+=imp

				# imprime ingresos:
				y+=1
				prom_acum = self.get_prom(ton_acum,imp_acum)
				worksheet.write(y,aux,ton_acum, numberdos_b)
				worksheet.write(y,aux+1,imp_acum, numberdos_b)
				worksheet.write(y,aux+2,prom_acum, numberdos_b)
				acum_totales[3][0]+=ton_acum
				acum_totales[3][1]+=imp_acum

				y+=1
				ton,imp,prom = self.get_transf_micro(loc.id,prod.id,conf)
				worksheet.write(y,aux,ton, numberdos)
				worksheet.write(y,aux+1,imp, numberdos)
				worksheet.write(y,aux+2,prom, numberdos)
				ton_acum-=ton
				acum_totales[4][0]+=ton
				imp_acum-=imp
				acum_totales[4][1]+=imp

				y+=1
				ton,imp,prom = self.get_costo_ventas(loc.id,prod.id,conf)
				worksheet.write(y,aux,ton, numberdos_b)
				worksheet.write(y,aux+1,imp, numberdos_b)
				worksheet.write(y,aux+2,prom, numberdos_b)
				ton_acum-=ton
				acum_totales[5][0]+=ton
				imp_acum-=imp
				acum_totales[5][1]+=imp

				y+=1
				ton,imp,prom = self.get_otros(loc.id,prod.id,conf)
				worksheet.write(y,aux,ton, numberdos)
				worksheet.write(y,aux+1,imp, numberdos)
				worksheet.write(y,aux+2,prom, numberdos)
				ton_acum-=ton
				acum_totales[6][0]+=ton
				imp_acum-=imp
				acum_totales[6][1]+=imp

				y+=1
				ton,imp,prom = self.get_transf_reali(loc.id,prod.id,conf)
				worksheet.write(y,aux,ton, numberdos)
				worksheet.write(y,aux+1,imp, numberdos)
				worksheet.write(y,aux+2,prom, numberdos)
				ton_acum-=ton
				acum_totales[7][0]+=ton
				imp_acum-=imp
				acum_totales[7][1]+=imp

				# imprime subtotales:
				y+=1
				prom_acum = self.get_prom(ton_acum,imp_acum)
				worksheet.write(y,aux,ton_acum, numberdos_b)
				worksheet.write(y,aux+1,imp_acum, numberdos_b)
				worksheet.write(y,aux+2,prom_acum, numberdos_b)
				acum_totales[8][0]+=ton_acum
				acum_totales[8][1]+=imp_acum
				aux += 4

			y = x+1 
			worksheet.merge_range(x,aux,x,aux+3,"TOTAL",title2)
			worksheet.write(y,aux,'Toneladas', title3)
			worksheet.write(y,aux+1,'Importe', title3)
			worksheet.write(y,aux+2,'Costo Promedio', title3)
			y+=1
			for i in acum_totales:
				worksheet.write(y,aux,i[0], numberdos_b)
				worksheet.write(y,aux+1,i[1], numberdos_b)
				worksheet.write(y,aux+2,self.get_prom(i[0],i[1]),numberdos_b)
				y+=1

			x+=13 # salto para el sig producto
		tam_col = [25,15,15,15,5] # adicional para los totales
		for i in range(aux_width):
			tam_col+=[15,15,15,5]
		while len(tam_col) < 21:
			tam_col.append(10)

		worksheet.set_column('A:A', tam_col[0])
		worksheet.set_column('B:B', tam_col[1])
		worksheet.set_column('C:C', tam_col[2])
		worksheet.set_column('D:D', tam_col[3])
		worksheet.set_column('E:E', tam_col[4])
		worksheet.set_column('F:F', tam_col[5])
		worksheet.set_column('G:G', tam_col[6])
		worksheet.set_column('H:H', tam_col[7])
		worksheet.set_column('I:I', tam_col[8])
		worksheet.set_column('J:J', tam_col[9])
		worksheet.set_column('K:K', tam_col[10])
		worksheet.set_column('L:L', tam_col[11])
		worksheet.set_column('M:M', tam_col[12])
		worksheet.set_column('N:N', tam_col[13])
		worksheet.set_column('O:O', tam_col[14])
		worksheet.set_column('P:P', tam_col[15])
		worksheet.set_column('Q:Q', tam_col[16])
		worksheet.set_column('R:R', tam_col[17])
		worksheet.set_column('S:S', tam_col[18])
		worksheet.set_column('T:T', tam_col[19])
		workbook.close()
		
		f = open(direccion + 'Reporte_Costo_Venta.xlsx', 'rb')
		
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'ReporteCostoVenta.xlsx',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		sfs_id = self.env['export.file.save'].create(vals)
		result = {}
		view_ref = mod_obj.get_object_reference('account_contable_book_it', 'export_file_save_action')
		view_id = view_ref and view_ref[1] or False
		result = act_obj.read( [view_id] )
	
		return {
			"type": "ir.actions.act_window",
			"res_model": "export.file.save",
			"views": [[False, "form"]],
			"res_id": sfs_id.id,
			"target": "new",
		}
	

	@api.multi
	def get_inv_ini(self,location,product,conf):
		ton,imp,prom = 0,0,0
		code_ant = self.period.code.split('/')
		mes = int(code_ant[0])
		anio = int(code_ant[1])
		if mes == 1:
			mes = 12
			anio -= 1
		else:
			mes -= 1
		code_ant = ("%2d"%mes).replace(' ','0') + '/' + str(anio)
		periodo_anterior = self.env['account.period'].search( [('code','=',code_ant)] )
		if mes == 12:
			fechaini = str(self.period.date_start).replace('-','')
			fechafin = str(self.period.date_stop).replace('-','')
			self.env.cr.execute(""" 
				SELECT
				round(saldof,2),
				round(saldov,2),
				CASE WHEN saldof != 0 
				THEN round(saldov/saldof,4) ELSE 0 END as cal
				 from get_kardex_v("""+fechaini+""","""+fechafin+""",
				'{""" + str(product) + """}',
				'{""" + str(conf.location_virtual_produccion.id) + """,
				""" + str(location) + """}') 
				where 
				(ubicacion_origen = """+str(conf.location_virtual_saldoinicial.id)+ """ and ubicacion_destino = """ + str(location) + """)
				or (ubicacion_origen = """+str(location) + """ and ubicacion_destino = """ + str(conf.location_virtual_saldoinicial.id) + """) 
				""")
			for i in self.env.cr.fetchall():
				ton = i[0]
				imp = i[1]
				prom = i[2]
		else:
			if len(periodo_anterior )>0:
				fechaini = str(periodo_anterior.date_start).replace('-','')
				fecha_inianio = fechaini[:4] + '0101'
				fechafin = str(periodo_anterior.date_stop).replace('-','')
				self.env.cr.execute("""
				SELECT
				round(saldof,2),
				round(saldov,2),
				CASE WHEN saldof != 0 
				THEN round(saldov/saldof,4) ELSE 0 END as cal
				 from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",
				'{""" + str(product) + """}',
				'{""" + str(conf.location_virtual_produccion.id) + """,
				""" + str(location) + """}') 
				where ubicacion_destino = """ + str(location) + """
				 or ubicacion_origen = """ + str(location) + """ 
				 """)
				for i in self.env.cr.fetchall():
					ton = i[0]
					imp = i[1]
					prom = i[2]

		ton = ton if ton else 0
		imp = imp if imp else 0
		prom = prom if prom else 0
		return ton,imp,prom

	# obtener valores produccion (solo para el almacen de calcinacion existencias)
	@api.multi
	def get_prod_data(self,location,product,conf):
		ton,imp,prom = 0,0,0
		if location != conf.location_existencias_calcinacion.id and location != conf.location_existencias_micronizado.id:
			return ton,imp,prom # esto se saca solo para calcinacion
		fechaini = str(self.period.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.period.date_stop).replace('-','')
		self.env.cr.execute(""" 
			SELECT  
			round(sum(ingreso),2),
			round(sum(debit),2),
			CASE WHEN sum(debit) != 0 
			THEN round(sum(debit)/sum(ingreso),4) ELSE 0 END as cal
			 from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",
			 '{""" + str(product) + """}',
			'{""" + str(conf.location_virtual_produccion.id) 
			+ """,""" + str(location) + """}') 
			where ((ubicacion_origen = """+str(conf.location_virtual_produccion.id) 
			+ """ and ubicacion_destino = """ + str(location) + """)
			or (ubicacion_destino = """ + str(conf.location_virtual_produccion.id) 
			+ """ and ubicacion_origen = """ + str(location) + """))
			and fecha >= '"""+str(self.period.date_start)
			+"""' and fecha <= '"""+str(self.period.date_stop)+"""'
			""")
		for i in self.env.cr.fetchall():
			ton = i[0]
			imp = i[1]
			prom = i[2]
		ton = ton if ton else 0
		imp = imp if imp else 0
		prom = prom if ton else 0
		return ton,imp,prom


	# new code
	@api.multi
	def get_ingre_trans(self,location,product,conf):
		location,product = str(location),str(product)
		ton,imp,prom = 0,0,0
		fechaini = str(self.period.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.period.date_stop).replace('-','')
		# las tansferencias recibidas
		self.env.cr.execute("""
		SELECT  
		round(SUM(ingreso),2) as ingreso,
		round(SUM(debit),2) as debit,
		CASE WHEN SUM(ingreso) != 0 
		THEN round(SUM(debit)/SUM(ingreso),4) ELSE 0 END as cal
		 from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",
		 '{"""+str(product)+"""}',
		 '{"""+str(location)+"""}') 
		 where  
		operation_type = '06'
		and ubicacion_destino = """+location+"""
		and fecha >= '"""+ str(self.period.date_start) +"""' 
		and fecha <= '"""+ str(self.period.date_stop) +"""'
		""")
		for i in self.env.cr.fetchall():
			ton = i[0]
			imp = i[1]
			prom = i[2]
		ton = ton if ton else 0
		imp = imp if imp else 0
		prom = prom if prom else 0
		return ton,imp,prom


	# new code
	@api.multi
	def get_transf_micro(self,location,product,conf):
		location,product = str(location),str(product)
		ton,imp,prom = 0,0,0
		fechaini = str(self.period.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.period.date_stop).replace('-','')
		# las tansferencias recibidas
		self.env.cr.execute("""
		select 
		round(sum(salida),2),
		round(sum(credit),2),
		CASE WHEN SUM(salida) != 0 
		THEN round(SUM(credit)/SUM(salida),4) ELSE 0 END as cal
		from 
		get_kardex_v("""+fecha_inianio+""","""+fechafin+""",'{"""+product+"""}',
		'{"""+str(conf.location_virtual_produccion.id)+""","""+location+"""}') 
		where ((ubicacion_origen = """+str(conf.location_virtual_produccion.id)
		+""" and ubicacion_destino = """+location+""")
		or (ubicacion_destino = """+str(conf.location_virtual_produccion.id)
		+""" and ubicacion_origen = """+location+""")) 
		and fecha >= '"""+ str(self.period.date_start) +"""'  
		and fecha <= '"""+ str(self.period.date_stop) +"""' 
		""")
		for i in self.env.cr.fetchall():
			ton = i[0]
			imp = i[1]
			prom = i[2]
		ton = ton if ton else 0
		imp = imp if imp else 0
		prom = prom if ton else 0
		return ton,imp,prom


	# new code
	@api.multi
	def get_costo_ventas(self,location,product,conf):
		location,product = str(location),str(product)
		ton,imp,prom = 0,0,0
		fechaini = str(self.period.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.period.date_stop).replace('-','')
		locations = self.env['stock.location'].search([('usage','=','customer')]).ids
		locations = ','.join(map(str,[location]+locations))
		self.env.cr.execute(""" 
		SELECT 
		round(SUM(ingreso),2),
		round(SUM(valor),2),
		CASE WHEN SUM(ingreso) != 0 
		THEN round(SUM(valor)/SUM(ingreso),2) ELSE 0 END as cal
		from (SELECT 
		(salida-ingreso) as ingreso,
		(credit-debit) as valor,
		ubicacion_origen,
		ubicacion_destino
		from get_kardex_v("""+fecha_inianio+""","""+fechafin+""",
		'{"""+str(product)+"""}',
		'{"""+locations+"""}') 
		where ((ubicacion_destino = """+str(location)+""") 
		or (ubicacion_origen = """+str(location)+"""))
		and fecha >= '"""+str(self.period.date_start)+"""'  
		and fecha <= '"""+str(self.period.date_stop)+"""')T
		where 
		ubicacion_origen in ("""+locations+""") 
		and ubicacion_destino in ("""+locations+""")
			""")
		for i in self.env.cr.fetchall():
			ton = i[0]
			imp = i[1]
			prom = i[2]
		ton = ton if ton else 0
		imp = imp if imp else 0
		prom = prom if ton else 0
		return ton,imp,prom

	@api.multi
	def get_otros(self,location,product,conf):
		location,product = str(location),str(product)
		ton,imp,prom = 0,0,0
		fechaini = str(self.period.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.period.date_stop).replace('-','')
		self.env.cr.execute(""" 
		SELECT 
		CASE WHEN sum(salida)>0 
		THEN round(sum(salida),2) ELSE 0 END as ingreso,
		CASE WHEN sum(credit)>0 
		THEN round(sum(credit),2) ELSE 0 END as credit,
		CASE WHEN SUM(salida) != 0 and SUM(credit) != 0
		THEN round(SUM(credit)/SUM(salida),2) ELSE 0 END as cal
		from get_kardex_v
		("""+str(fecha_inianio)+""","""+str(fechafin)+""",'{"""+product+"""}',
		'{"""+location+""","""+str(conf.location_perdidas_mermas.id)+"""}') 
		where (ubicacion_destino = """+location+"""
		or ubicacion_origen = """+location+""")
		and fecha >= '"""+str(self.period.date_start)+"""'  
		and fecha <= '"""+str(self.period.date_stop)+"""'
		and operation_type = '16'
		""")
		for i in self.env.cr.fetchall():
			ton = i[0]
			imp = i[1]
			prom = i[2]
		ton = ton if ton else 0
		imp = imp if imp else 0
		prom = prom if ton else 0
		return ton,imp,prom


	# new code
	@api.multi
	def get_transf_reali(self,location,product,conf):
		location,product = str(location),str(product)
		ton,imp,prom = 0,0,0
		fechaini = str(self.period.date_start).replace('-','')
		fecha_inianio = fechaini[:4] + '0101'
		fechafin = str(self.period.date_stop).replace('-','')
		self.env.cr.execute(""" 
			SELECT 
			round(SUM(salida),2),
			round(SUM(credit),2),
			CASE WHEN SUM(salida) != 0
			THEN round(SUM(credit)/SUM(salida),2) ELSE 0 END as cal
			from get_kardex_v("""+str(fecha_inianio)+""","""+str(fechafin)+""",
			'{"""+product+"""}','{"""+location+"""}')
			where operation_type = '06'
			and fecha >= '"""+str(self.period.date_start)+"""'   
			and fecha <= '"""+str(self.period.date_stop)+"""'
		""")
		for i in self.env.cr.fetchall():
			ton = i[0]
			imp = i[1]
			prom = i[2]
		ton = ton if ton else 0
		imp = imp if imp else 0
		prom = prom if ton else 0
		return ton,imp,prom

	@api.multi
	def get_prom(self,ton,imp):
		res = 0
		try:
			res = imp/ton
		except ZeroDivisionError as e:
			print('Error: ',e)
		return res

	@api.multi
	def get_name_location(self,name):
		name = name.split('/')
		if len(name) == 2 or len(name) == 3:
			return name[1]
		elif len(name)==1:
			return name[0]
		else:
			return ''

