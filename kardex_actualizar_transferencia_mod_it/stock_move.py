# -*- encoding: utf-8 -*-
from openerp.osv import osv
from openerp import models,fields ,api

class stock_picking(models.Model):
	_inherit = 'stock.picking'

	@api.one
	def calcular_valor_transferencia(self):

		prods = self.env['product.product'].search([('type','=','product')])
		locat = self.env['stock.location'].search([('usage','in',['internal','inventory','transit','procurement','production'])])

		import datetime

		lst_products  = prods.ids
		lst_locations = locat.ids
		productos='{'
		almacenes='{'
		hoy = str( datetime.datetime.now() )[:10]
		date_ini= hoy.split('-')[0] + '-01-01'
		date_fin= hoy
		fecha_arr = date_ini
		
		for producto in lst_products:
			productos=productos+str(producto)+','
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
		almacenes=almacenes[:-1]+'}'

		self.env.cr.execute(""" 
			update stock_move set
precio_unitario_manual = 0
where id in (
select sm.id from stock_move sm
inner join stock_location entrada on entrada.id = sm.location_id
inner join stock_location salida on salida.id = sm.location_dest_id
inner join stock_picking sp on sp.id = sm.picking_id
where entrada.usage = 'internal' and salida.usage = 'internal'
and sp.id = """ + str(self.id) + """
)
""")
		lineas = [-1,-1,-1,self.id]

		act = '{'
		for asd in lineas:
			act = act +str(asd)+','
		act = act[:-1]+'}'
		
		self.env.cr.execute(""" select * from get_kardex_v_actualizar_ids("""+ date_ini.replace("-","") + "," + date_fin.replace("-","") + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[],""" +fecha_arr.replace('-','')+ """, '""" + act + """'::INT[]) """)
		return


	@api.cr_uid_ids_context
	def do_transfer(self, cr, uid, picking_ids, context=None):
		t = super(stock_picking,self).do_transfer(cr, uid, picking_ids, context)
		picking_id = self.pool.get('stock.picking').browse(cr,uid,picking_ids,context)
		for i in picking_id:
			i.calcular_valor_transferencia()
		return t


class valor_unitario_produccion_mod(models.Model):
	_name = 'valor.unitario.produccion.mod'

	fecha_inicio = fields.Date('Fecha Inicio')
	fecha_final = fields.Date('Fecha Final')

	@api.one
	def do_valor(self):
		fechaini = str(self.fecha_inicio)
		fechaini = fechaini.replace('-','')
		fechafin = str(self.fecha_final)
		fechafin = fechafin.replace('-','')

		fecha_inianio = self.fecha_inicio.split('-')[0] + '-01-01'

		actualizaciones = self.env['mrp.production'].search([('date_planned','>=',self.fecha_inicio),('date_planned','<=',self.fecha_final),('is_mercaderia','=',True)])
		for i in actualizaciones:
			calc = 0
			if i.move_lines2 and i.move_lines2[0].id:
				lst_products  = []
				lst_locations = []
				productos='{'
				almacenes='{'
				date_ini= fechaini.replace('-','')
				date_fin= fechafin.replace('-','')

				lst_products = self.env['product.product'].search([]).ids
				lst_locations = self.env['stock.location'].search([]).ids

				for producto in lst_products:
					productos=productos+str(producto)+','
				productos=productos[:-1]+'}'
				for location in lst_locations:
					almacenes=almacenes+str(location)+','
				almacenes=almacenes[:-1]+'}'


				self.env.cr.execute(""" 
								 select 
								cadquiere
								from get_kardex_v("""+ fecha_inianio + "," + fechafin + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[]) 
								where stock_moveid = """ + str(i.move_lines2[0].id)  + """
							""")

				for wakanda in self.env.cr.fetchall():
					calc = wakanda[0] if wakanda[0] else 0
					
			if i.move_created_ids2 and i.move_created_ids2[0].id:
				i.move_created_ids2[0].precio_unitario_manual = calc
				i.move_created_ids2[0].price_unit = calc
				self.env.cr.execute("""
					update stock_move set precio_unitario_manual = """ +str(calc)+ """ , price_unit = """ +str(calc)+ """ 
					where id = """+str(i.move_created_ids2[0].id)+"""
					""")
			
				



class valor_unitario_kardex_mod(models.Model):
	_name='valor.unitario.kardex.mod'
	
	fecha_inicio = fields.Date('Fecha Inicio')
	fecha_final = fields.Date('Fecha Final')

	location_in = fields.Many2one('stock.location','Ubicacion Origen')
	location_out = fields.Many2one('stock.location','Ubicacion Destino')

	@api.one
	def do_valor(self):
		prods = self.env['product.product'].search([('type','=','product')])
		locat = self.env['stock.location'].search([('usage','in',['internal','inventory','transit','procurement','production'])])

		lst_products  = prods.ids
		lst_locations = locat.ids
		productos='{'
		almacenes='{'
		date_ini= self.fecha_inicio.split('-')[0] + '-01-01'
		date_fin= self.fecha_final
		fecha_arr = self.fecha_inicio
		
		for producto in lst_products:
			productos=productos+str(producto)+','
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
		almacenes=almacenes[:-1]+'}'

		self.env.cr.execute(""" 
			update stock_move set
precio_unitario_manual = 0
where id in (
select sm.id from stock_move sm
inner join stock_location entrada on entrada.id = sm.location_id
inner join stock_location salida on salida.id = sm.location_dest_id
inner join stock_picking sp on sp.id = sm.picking_id
where entrada.usage = 'internal' and salida.usage = 'internal'
and sp.date >='""" +str(self.fecha_inicio)+ """' and sp.date <='""" +str(self.fecha_final)+ """'
and entrada.id = """ + str(self.location_in.id) + """   and salida.id =   """ + str(self.location_out.id) + """ 
)
""")
	
		self.env.cr.execute(""" 			
select sm.id from stock_move sm
inner join stock_location entrada on entrada.id = sm.location_id
inner join stock_location salida on salida.id = sm.location_dest_id
inner join stock_picking sp on sp.id = sm.picking_id
where entrada.usage = 'internal' and salida.usage = 'internal'
and sp.date >='""" +str(self.fecha_inicio)+ """' and sp.date <='""" +str(self.fecha_final)+ """'
and entrada.id = """ + str(self.location_in.id) + """   and salida.id =   """ + str(self.location_out.id) + """ 

""")
		lineas = self.env.cr.fetchall()
		act = '{-1,-1,-1,-1,'
		for asd in lineas:
			act = act +str(asd[0])+','
		act = act[:-1]+'}'
		print act , 'OCAZO'
		
		self.env.cr.execute(""" select * from get_kardex_v_actualizar_ids("""+ date_ini.replace("-","") + "," + date_fin.replace("-","") + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[],""" +fecha_arr.replace('-','')+ """, '""" + act + """'::INT[]) """)
		return