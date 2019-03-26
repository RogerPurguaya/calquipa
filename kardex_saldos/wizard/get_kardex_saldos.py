# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import time
import openerp.addons.decimal_precision as dp
import base64
import codecs
from openerp.http import request

class get_kardex_saldos(osv.osv_memory):
	_name = "get.kardex.saldos"

	_columns = {
		'date': fields.date('Fecha'),
		'location_ids':fields.many2many('stock.location','rel_kardex_location1','location_id','kardex_id','Ubicacion',required=True)
	}
	
	def date_to_number(self, date):
		splited = date.split('-')
		return ''.join(splited)
	
	def action_procesar_resumen(self, cr, uid, ids, context=None):
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		
		if context is None:
			context = {}
		data = self.read(cr, uid, ids, [], context=context)[0]
		
		date = data['date']
		date = self.date_to_number(date)
		productos='{'
		almacenes='{'
		bd = str(request.session.db)

		date_ini='2015-01-01'
		if '2017' in bd:
			date_ini = '2017-01-01'
		if '2018' in bd:
			date_ini = '2018-01-01'
		if '2019' in bd:
			date_ini = '2019-01-01'
		if '2020' in bd:
			date_ini = '2020-01-01'
		if '2021' in bd:
			date_ini = '2021-01-01'
		if '2022' in bd:
			date_ini = '2022-01-01'

		date_fin=data['date']
		lst_locations = data['location_ids']
		lst_products=self.pool.get('product.product').search(cr,uid,[])
		for producto in lst_products:
			productos=productos+str(producto)+','
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
		almacenes=almacenes[:-1]+'}'
		filtro = []
		tipo='fisico'
		if tipo=='fisico':
			cadsql ="""
			copy (
			select 
			X1."Almacen",
			X1."Producto",
			X1."Codigo",
			X1."Unidad",
			X1."Categoria",
			X1."Ingreso",
			X1."Salida",
			X1."Saldo",
			pt.loc_rack as "Estante",
			pt.loc_row as "Fila"
			from (
			SELECT * from (
					select 
					almacen as "Almacen",
					name_template as "Producto",
					default_code as "Codigo",
					unidad as "Unidad",
					categoria as "Categoria",
					sum(ingreso) as "Ingreso",
					sum(salida) as "Salida",
					sum(ingreso)-sum(salida) as "Saldo",
					product_id as product_id
					from (
					select * from get_kardex_v("""+date_ini.replace("-","") + """,""" + date_fin.replace("-","") + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[]) order by location_id,product_id,fecha,esingreso,nro) 
					t group by name_template,product_id,almacen,default_code,unidad,categoria) g ) as X1
					inner join product_product pp on pp.id = X1.product_id
					inner join product_template pt on pt.id = pp.product_tmpl_id

					) to 'e:/PLES_ODOO/saldos.csv'  WITH DELIMITER ',' CSV HEADER"""			
		else:
			cadsql ="""
				copy (SELECT row_number() OVER () AS id,* from (
					select default_code as "Codigo",
					unidad as "Unidad",
					categoria as "Categoria",
					sum(ingreso) as "Ingreso",
					sum(salida) as "Salida",
					sum(ingreso)-sum(salida) as "Saldo",
					name_template as "Producto",
					almacen as "Almacen" from (
					select * from get_kardex_v("""+date_ini.replace("-","") + """,""" + date_fin.replace("-","") + ",'" + productos + "'::INT[], '" + almacenes + "'::INT[]) order by location_id,product_id,fecha,esingreso,nro) t group by name_template,product_id,almacen) g) to 'e:/PLES_ODOO/saldos.csv'  WITH DELIMITER ',' CSV HEADER"""			
			cadsql = """
			copy (
			select 
			X1."Almacen",
			X1."Producto",
			X1."Codigo",
			X1."Unidad",
			X1."Categoria",
			X1."Ingreso",
			X1."Salida",
			X1."Saldo",
			pt.loc_rack as "Estante",
			pt.loc_row as "Fila"
			from  (
			SELECT * from (
					select 
					almacen as "Almacen",
					name_template as "Producto",
					default_code as "Codigo",
					unidad as "Unidad",
					categoria as "Categoria",
					sum(ingreso) as "Ingreso",
					sum(salida) as "Salida",
					sum(ingreso)-sum(salida) as "Saldo",
					product_id as product_id
					from(
					select * from get_kardex_v("""+date_ini.replace("-","") + """,""" + date_fin.replace("-","") + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[]) order by location_id,product_id,fecha,esingreso,nro) 
					t group by name_template,product_id,almacen,default_code,unidad,categoria) g ) as X1
					inner join product_product pp on pp.id = X1.product_id
					inner join product_template pt on pt.id = pp.product_tmpl_id

					) to 'e:/PLES_ODOO/saldos.csv'  WITH DELIMITER ',' CSV HEADER
			"""
 		# raise osv.except_osv('Alerta', cadsql)		
		cr.execute(cadsql)
		f = open('e:/PLES_ODOO/saldos.csv', 'rb')

		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'saldos.csv',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		sfs_id = self.pool.get('export.file.save').create(cr,uid,vals)
		result = {}
		view_ref = mod_obj.get_object_reference(cr,uid,'account_contable_book_it', 'export_file_save_action')
		view_id = view_ref and view_ref[1] or False
		result = act_obj.read( cr,uid,[view_id],context )

		return {
		    "type": "ir.actions.act_window",
		    "res_model": "export.file.save",
		    "views": [[False, "form"]],
		    "res_id": sfs_id,
		    "target": "new",
		}

get_kardex_saldos()