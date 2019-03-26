# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
import time
import calendar
import helper
import datetime

class account_invoice(models.Model):
	_name='account.invoice'
	_inherit='account.invoice'

	def makeprintdoc(self,cr,uid,ids,context=None):
		active_id = ids[0]
		invoice = self.pool.get('account.invoice').browse(cr,uid,active_id,context)
		if invoice.type_document_id.code=="01":
			self.maketxtfactura(cr,uid,ids,context)	
		elif invoice.type_document_id.code=="03":
			self.maketxtboleta(cr,uid,ids,context)	
		else:
			raise osv.except_osv('Alerta', "Documento no controlado para impresión")	
		return True

	def maketxtboleta(self,cr,uid,ids,context=None):
		reporteador = self.pool.get('calquipa.factura')
		s = reporteador.get_head_bol_txt(cr,uid,ids,context)
		self.pool.get('make.txt').makefile(cr,uid,s,'bol',context)
		return True

	def maketxtfactura(self,cr,uid,ids,context=None):
		reporteador = self.pool.get('calquipa.factura')
		s = reporteador.get_head_txt(cr,uid,ids,context)
		self.pool.get('make.txt').makefile(cr,uid,s,'fac',context)
		return True


class calquipa_factura(models.Model):
	_name='calquipa.factura'

	def get_head_bol_txt(self, cr, uid, ids, context=None):
		result = []
		# raise osv.except_osv('Alerta', ids)
		active_id = ids[0]
		company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=context)
		invoice_obj = self.pool.get('account.invoice').browse(cr, uid, active_id)
#		c=helper.number_to_letter(str(invoice_obj.amount_total),invoice_obj.currency_id.name)
#		raise osv.except_osv('Alerta', c)
		company_attrs = helper.company(cr, uid, company_id) #atributos company
		ruc_partner=None

		if invoice_obj.partner_id.type_number!="":
			ruc_partner= invoice_obj.partner_id.type_number
		
		if ruc_partner==None:
			ruc_partner=" "
		# raise osv.except_osv('Alerta', invoice_obj.partner_id.vat[2:])
		c_ruc = company_attrs.ruc
		c_nombre = company_attrs.nombre
		c_street = company_attrs.street
		c_phone = company_attrs.phone
		c_email = company_attrs.email
		c_website = company_attrs.website
		c_city = company_attrs.city
		c_logo = company_attrs.logo
		c_nombre = c_nombre.upper()
		detalle_company = ""
		ruc_company = ""
		txt="" # variable para el txt
		result_detalle = []
		txt = txt+chr(27)+chr(15)+chr(27)+chr(48)
		
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"           "+invoice_obj.partner_id.name+"\n"
		if invoice_obj.partner_id.street:
			txt = txt+"           "+invoice_obj.partner_id.street+"\n"
		else:
			txt = txt+"\n"
		if ruc_partner:
			txt = txt+" "*11+ruc_partner
		else:
			txt = txt+" "*20

		fmt = '%H:%M:%S'
		f = datetime.datetime.today() - datetime.timedelta(hours=5)
		txt = txt+" "*22+invoice_obj.date_invoice+" "+f.strftime(fmt)+"\n"

		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+self.get_detail_bol_txt(cr, uid, ids, context)+"\r\n"
		
		c_descuento = 0.0
		for linea in invoice_obj.invoice_line:
			c_descuento = c_descuento + (linea.quantity * linea.price_unit * linea.discount / 100)
		if c_descuento>0:
			txt = txt+' '*5+'Dcto: S/.'+str("%0.3f" % c_descuento).rjust(7)+"\n"
		else:
			txt = txt+"\n"
		
		if invoice_obj.amount_perception>0:
			company=self.pool.get('res.users').browse(cr,uid,uid,context).company_id
			txt=txt+" "*5+company.glosa_percepcion[0:60]+"\n"
			txt=txt+" "*5+"Tasa: "+str("%0.2f" % invoice_obj.percent_perception)+"% Perc.: "+str("%0.2f" % invoice_obj.amount_perception)+" Tot.Inc.Perc.: "+str("%0.2f" % invoice_obj.total_cobar)+"\n"
		else:
			txt = txt+"\n"
			txt = txt+"\n"
		txt = txt+" "*48+str("%0.2f" % invoice_obj.amount_total).rjust(12)+"\n"
		txt = txt+chr(12)
		
		return txt
	def get_detail_bol_txt(self, cr, uid, ids, context=None):
		result = []
		active_id = ids[0]

		invoice_obj = self.pool.get('account.invoice').browse(cr, uid, active_id)
		concatena_col = ''
		concatena_col_dos = ''
		result_detalle = []
		txt=""
		n=0


		for items in invoice_obj.invoice_line:
			subtotal= items.price_subtotal

			for impuesto in items.invoice_line_tax_id:
				if not impuesto.price_include:
					subtotal=items.price_subtotal*(1+impuesto.amount)
			
			txt=txt+"      "+str("%0.2f" % items.quantity).rjust(6)
			txt=txt+"    "+items.product_id.name_template[0:20].ljust(20)
			if items.discount>0:
				txt=txt+"   "+str("%0.2f" % items.discount).rjust(5)+"%"
			else:
				txt=txt+" "*9
			txt=txt+"   "+str("%0.2f" % subtotal).rjust(12)+"\n"
			n=n+1
		if n<invoice_obj.serie_id.maxlines:
			for x in range(n,invoice_obj.serie_id.maxlines):
				txt=txt+"\n"
		return txt	
	def get_head_txt(self, cr, uid, ids, context=None):
		result = []
		# raise osv.except_osv('Alerta', ids)
		active_id = ids[0]
		company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=context)
		invoice_obj = self.pool.get('account.invoice').browse(cr, uid, active_id)
#		c=helper.number_to_letter(str(invoice_obj.amount_total),invoice_obj.currency_id.name)
#		raise osv.except_osv('Alerta', c)
		company_attrs = helper.company(cr, uid, company_id) #atributos company
		ruc_partner=""

		if invoice_obj.partner_id.type_number:
			# raise osv.except_osv('Alerta', invoice_obj.partner_id.doc_number)
			ruc_partner= invoice_obj.partner_id.type_number
			if invoice_obj.partner_id.is_company:
				if invoice_obj.partner_id.parent_id:
					if invoice_obj.partner_id.parent_id.type_number:
						ruc_partner= invoice_obj.partner_id.parent_id.type_number
					else:
						raise osv.except_osv('Empresa matriz no tiene RUC')
		'''
		else:
			if invoice_obj.partner_id.vat:				
				ruc_partner= invoice_obj.partner_id.vat[2:]
			else:
				if invoice_obj.partner_id.parent_id:
					if invoice_obj.partner_id.parent_id.doc_number:
						ruc_partner= invoice_obj.partner_id.parent_id.doc_number
					else:
						raise osv.except_osv('Empresa matriz no tiene RUC')
		'''
		if ruc_partner==None or ruc_partner==False:
			raise osv.except_osv('Empresa no tiene definido RUC')
		
		c_ruc = company_attrs.ruc
		c_nombre = company_attrs.nombre
		c_street = company_attrs.street
		c_phone = company_attrs.phone
		c_email = company_attrs.email
		c_website = company_attrs.website
		c_city = company_attrs.city
		c_logo = company_attrs.logo
		c_nombre = c_nombre.upper()
		detalle_company = ""
		ruc_company = ""
		txt="" # variable para el txt
		result_detalle = []
		cadpick=""
		for picking in invoice_obj.picking_ids:
			anumero = picking.name.split('-')
			if len(anumero)>1:
				cadpick=anumero[0]+"-"
			else:
				cadpick=""
				break

		for picking in invoice_obj.picking_ids:
			anumero = picking.name.split('-')
			if len(anumero)>1:
				numdoc=anumero[1]
			else:
				numdoc=anumero[0]
			# raise osv.except_osv('Alerta', numdoc)
			cadpick=cadpick+numdoc+","
		txt = txt+chr(27)+chr(15)+chr(27)+chr(48)
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		# raise osv.except_osv('Alerta', invoice_obj.date_invoice[8:])
		# txt = txt+' '.join([str[:38]])+invoice_obj.date_invoice.year()
		# txt = txt+' '.join([str[:12]])+invoice_obj.date_invoice.month()
		# txt = txt+' '.join([str[:18]])+invoice_obj.date_invoice.day()+"\n"
		txt = txt+"\n"
		txt = txt+'                                           '+invoice_obj.date_invoice[8:]
		txt = txt+'          '+invoice_obj.date_invoice[5:-3]
		txt = txt+'                  '+invoice_obj.date_invoice[:4]+"\n"
		txt = txt+"\n"
		#txt = txt+"\n"
		txt = txt+"                   "+invoice_obj.partner_id.name+"\n"
		if invoice_obj.partner_id.street:
			txt = txt+"                   "+invoice_obj.partner_id.street+"\n"
		else:
			raise osv.except_osv('Alerta partner no tiene direccion', invoice_obj.partner_id.name)
			#txt = txt+"\n"
		txt = txt+"                   "+ruc_partner +" "*24+cadpick+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+" "*84+"V.Vta.    Dcto %"+"\n"
		
		txt = txt+self.get_detail_txt(cr, uid, ids, context)+"\r\n"
		
		c_descuento = 0.0
		for linea in invoice_obj.invoice_line:
			c_descuento = c_descuento + (linea.quantity * linea.price_unit * linea.discount / 100)
		txt = txt+' '*38+'Total Descuento: S/.'+str("%0.3f" % c_descuento).rjust(12)+"\n"
		if invoice_obj.amount_perception>0:
			percent=0
			for linea in invoice_obj.invoice_line:
				if linea.percent_perception!=0:
					percent=linea.percent_perception
					break
			company=self.pool.get('res.users').browse(cr,uid,uid,context).company_id
			txt=txt+" "*8+company.glosa_percepcion+"   Tasa: "+str("%0.2f" % invoice_obj.percent_perception)+"% Percepcion: "+str("%0.2f" % invoice_obj.amount_perception)+chr(27)+chr(69)+" TOTAL A PAGAR CON PERCEPCION: "+str("%0.2f" % invoice_obj.total_cobar)+chr(27)+chr(70)+"\n"
		else:
			txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"                "+helper.number_to_letter(str(invoice_obj.amount_total),invoice_obj.currency_id.name)+"\n"
		txt = txt+' '*119+'S/.'+str("%0.2f" % invoice_obj.amount_untaxed).rjust(12)+"\n"
		txt = txt+' '*114+'18   S/.'+str("%0.2f" % invoice_obj.amount_tax).rjust(12)+"\n"
		txt = txt+"\n"
		txt = txt+' '*119+'S/.'+str("%0.2f" % invoice_obj.amount_total).rjust(12)+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		#txt = txt+chr(12)
		
		return txt
	def get_detail_txt(self, cr, uid, ids, context=None):
		result = []
		active_id = ids[0]

		invoice_obj = self.pool.get('account.invoice').browse(cr, uid, active_id)
		concatena_col = ''
		concatena_col_dos = ''
		result_detalle = []
		txt=""
		n=0
		for items in invoice_obj.invoice_line:
			txt=txt+"    "+str("%0.2f" % items.quantity).rjust(12)
			if items.product_id.default_code:
				txt=txt+"     "+items.product_id.default_code.ljust(12)
			else:
				txt=txt+"     "+" "*12
			txt=txt+"   "+items.product_id.name_template[0:36].ljust(36)
			txt=txt+" "+items.product_id.product_tmpl_id.uom_id.name[0:8].ljust(8)
			txt=txt+" "+str("%0.3f" % items.price_unit).rjust(9)
			f_pre_c_dct = 0.0
			if items.discount:
				txt=txt+"   "+str("%0.2f" % items.discount).rjust(5)
				f_pre_c_dct = items.price_unit*(100-items.discount)/100.0
			else:
				txt=txt+" "+' '.rjust(5)
				f_pre_c_dct = items.price_unit
			txt=txt+"        "+str("%0.3f" % f_pre_c_dct).rjust(9)			
			txt=txt+"        "+str("%0.2f" % items.price_subtotal).rjust(12)+"\n"
			n=n+1
		

		if n<invoice_obj.serie_id.maxlines:
			for x in range(n,invoice_obj.serie_id.maxlines):
				txt=txt+"\n"
		return txt	

