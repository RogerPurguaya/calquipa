# -*- coding: utf-8 -*-
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import time
import openerp.addons.decimal_precision as dp
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs
values = {}

class make_kardex(osv.TransientModel):
	_inherit = "make.kardex"




	@api.v7
	def do_csv(self,cr,uid,ids,context=None):
		data = self.read(cr, uid, ids, [], context=context)[0]	
		cad=""	

		lst_products  = data['products_ids']
		lst_locations = data['location_ids']
		productos='{'
		almacenes='{'
		date_ini=data['fini']
		date_fin=data['ffin']
		if 'allproducts' in data:
			if data['allproducts']:
				lst_products  = self.pool.get('product.product').search(cr,uid,[])
			else:
				lst_products  = data['products_ids']
		else:
			if data['products_ids']==[]:
				raise osv.except_osv('Alerta','No existen productos seleccionados')
				return
			lst_products  = data['products_ids']


		for producto in lst_products:
			productos=productos+str(producto)+','
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
		almacenes=almacenes[:-1]+'}'
		# raise osv.except_osv('Alertafis',[almacenes,productos])
		print 'tipo',context['tipo']
		if context['tipo']=='valorado':
			cadf="""
				copy (select 
				*
				from get_kardex_v("""+date_ini.replace("-","") + "," + date_fin.replace("-","") + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[]) order by location_id,product_id,fecha,esingreso,nro) to 'e:/PLES_ODOO/kardex.csv'  WITH DELIMITER ',' CSV HEADER 
				"""
		else:
			if context['tipo']=='fisico':
				cadf="""
				copy (select 
					origen as "Origen",
					destino as "Destino",
				almacen AS "Almacen",
				categoria as "Categoria",
				name_template as "Producto",
				fecha as "Fecha",
				periodo as "Periodo",
				ctanalitica as "Cta. Analitica",
				account_analytic_account.name as "C. Costo",				
				stock_doc as "Doc. Almacén",
				serial as "Serie",
				nro as "Nro. Documento",
				operation_type as "Tipo de operacion",
				get_kardex_v.name as "Proveedor",
				ingreso as "Ingreso Fisico",
				salida as "Salida Fisico",
				saldof as "Saldo Fisico",
				default_code as "Codigo",unidad as "Unidad",
				mrpname as "Ord. Prodc.",
				documento_partner as "Guia de remision",
				responsable as "Entregado a"
				from get_kardex_v("""+date_ini.replace("-","") + "," + date_fin.replace("-","") + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[]) 
				left join account_analytic_account on get_kardex_v.ctanalitica =account_analytic_account.code
				order by location_id,product_id,fecha,esingreso,nro) to 'e:/PLES_ODOO/kardex.csv'  WITH DELIMITER ',' CSV HEADER 
				"""
			else:
				cadf="select * from get_kardex_fis_sumi("+date_ini.replace("-","") + "," + date_fin.replace("-","") + ",'" + productos + "'::INT[], '" + almacenes + "'::INT[]) order by location_id,product_id,fecha,esingreso,nro"							
		# raise osv.except_osv('Alertafis',cadf)

		cr.execute(cadf)
		

		f = open('e:/PLES_ODOO/kardex.csv', 'rb')
			
			
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'kardex.csv',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		sfs_id = self.pool.get('export.file.save').create(cr,uid,vals)
		result = {}
		view_ref = mod_obj.get_object_reference(cr,uid,'account_contable_book_it', 'export_file_save_action')
		view_id = view_ref and view_ref[1] or False
		result = act_obj.read( cr,uid,[view_id],context )
		print sfs_id

		#import os
		#os.system('c:\\eSpeak2\\command_line\\espeak.exe -ves-f1 -s 170 -p 100 "Se Realizo La exportación exitosamente Y A EDWARD NO LE GUSTA XDXDXDXDDDDDDDDDDDD" ')

		return {
		    "type": "ir.actions.act_window",
		    "res_model": "export.file.save",
		    "views": [[False, "form"]],
		    "res_id": sfs_id,
		    "target": "new",
		}