# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import time
import openerp.addons.decimal_precision as dp
import base64
import codecs

class get_kardex_invoice_notin(osv.osv_memory):
	_name = "get.kardex.invoice.notin"

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
		date_ini='2015-01-01'
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
		cadsql ="""
		copy (
				select distinct account_invoice.name as "Origen",
				account_invoice.supplier_invoice_number as "Factura",res_partner.name as "Proveedor/Cliente",
				account_invoice.date_invoice as "Fecha"
				from account_invoice 
				inner join account_invoice_line on account_invoice.id = account_invoice_line.invoice_id
				inner join product_product on account_invoice_line.product_id = product_product.id
				inner join product_template on product_product.product_tmpl_id = product_template.id
				inner join res_partner on account_invoice.partner_id =res_partner.id
				where product_template.type = 'product' and account_invoice.state in ('open','paid')
				and account_invoice.id not in (
				select distinct account_invoice.id
				from stock_move
				inner join product_product on stock_move.product_id = product_product.id
				inner join product_template on product_product.product_tmpl_id = product_template.id
				inner join stock_picking on stock_move.picking_id = stock_picking.id
				inner join account_invoice on stock_move.invoice_id = account_invoice.id
				where (stock_picking.invoice_id is not null or stock_move.invoice_id is not null) and 
				product_template.type = 'product'
				union
				select distinct account_invoice.id
				from stock_move
				inner join product_product on stock_move.product_id = product_product.id
				inner join product_template on product_product.product_tmpl_id = product_template.id
				inner join stock_picking on stock_move.picking_id = stock_picking.id
				inner join account_invoice on stock_picking.invoice_id = account_invoice.id
				where (stock_picking.invoice_id is not null or stock_move.invoice_id is not null) and 
				product_template.type = 'product'
				) and account_invoice.date_invoice<='"""+date_fin+"""' 
			) to 'e:/PLES_ODOO/saldos_cuenta.csv'  WITH DELIMITER ',' CSV HEADER"""			
 		# raise osv.except_osv('Alerta', cadsql)		
		cr.execute(cadsql)
		f = open('e:/PLES_ODOO/saldos_cuenta.csv', 'rb')

		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'saldos_cuenta.csv',
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

get_kardex_invoice_notin()