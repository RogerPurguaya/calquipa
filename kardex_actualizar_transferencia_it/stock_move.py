# -*- encoding: utf-8 -*-
from openerp.osv import osv
from openerp import models,fields ,api


class valor_unitario_kardex(models.Model):
	_name='valor.unitario.kardex'
	
	fecha_inicio = fields.Date('Fecha Inicio')
	fecha_final = fields.Date('Fecha Final')

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
)
""")

		self.env.cr.execute(""" select * from get_kardex_v_actualizar("""+ date_ini.replace("-","") + "," + date_fin.replace("-","") + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[],""" +fecha_arr.replace('-','')+ """) """)
		return