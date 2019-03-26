# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
import time
import calendar
import helper

import datetime
from dateutil import relativedelta as rdelta

class calquipa_guiarem(models.Model):
	_name='calquipa.guiarem'
	def to_unicode_or_bust(
			obj, encoding='utf-8'):
		if isinstance(obj, basestring):
			if not isinstance(obj, unicode):
				obj = unicode(obj, encoding)
		return obj
	def selector(self, cr, uid, ids, context=None):
		if context['logistica']==False:
			self.get_head_txt(cr, uid, ids, context)
		else:
			self.get_head_txt_log(cr, uid, ids, context)

	# funciones para guia de VENTAS
	def get_head_txt(self, cr, uid, ids, context=None):
		result = []
		active_id = ids[0]
		
		company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=context)
		picking_out_obj = self.pool.get('stock.picking').browse(cr, uid, active_id)
	   
		# raise osv.except_osv('Alerta', compra)
		company_attrs = helper.company(cr, uid, company_id) #atributos company
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

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

		detalle_company = ""

		ruc_company = ""
		txt=""
		txt += chr(27) + chr(15) + chr(27) +chr(48)
		txt += "\n"*12

		fe = (datetime.datetime.strptime(picking_out_obj.date, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=5)) if picking_out_obj.date else False
		ft = (datetime.datetime.strptime(picking_out_obj.date_done, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=5)) if picking_out_obj.date_done else False
		
		if fe:
			txt += " "*28 + format(fe.day, "02") + " "*4 + format(fe.month, "02") + " "*4 + str(fe.year)[2:]
		else:
			txt += ""
		if ft:
			txt += " "*25 + format(ft.day, "02") + " "*5 + format(ft.month, "02") + " "*5 + str(ft.year)[2:]
		else:
			txt += ""
			
		txt += "\n"*4
		txt += " "*6 + (c_street.ljust(45) if c_street else " ".ljust(45))

		ruccliente = picking_out_obj.partner_id.type_number
		if picking_out_obj.partner_id.is_company:
			if picking_out_obj.partner_id.parent_id:
				if picking_out_obj.partner_id.parent_id.type_number:
					ruccliente = picking_out_obj.partner_id.parent_id.type_number
				else:
					ruccliente = picking_out_obj.partner_id.parent_id.vat[2:]
			else:
				if picking_out_obj.partner_id.type_number:
					ruccliente = picking_out_obj.partner_id.type_number
				else:
					ruccliente = picking_out_obj.partner_id.vat[2:]

		if picking_out_obj.partner_id.is_company:
			if picking_out_obj.partner_id.parent_id:
				direcciondetino = picking_out_obj.partner_id.parent_id.street
			else:
				direcciondetino = picking_out_obj.partner_id.street
		
		direcciondetino = picking_out_obj.partner_id.street
		txt += " "*30+(direcciondetino[:62].ljust(62) if direcciondetino else " ".ljust(62))
		txt += "\n"*5
		txt += " "*19 + picking_out_obj.partner_id.name if picking_out_obj.partner_id.name else ""
		txt += " "*60 + picking_out_obj.trans_marca if picking_out_obj.trans_marca else ""
		txt += " "*2 + picking_out_obj.trans_placa if picking_out_obj.trans_placa else ""
		txt += "\n"*2
		txt += " "*47 + (ruccliente.ljust(11) if ruccliente else "".ljust(11))
		txt += " "*55 + (picking_out_obj.trans_inscriptor.ljust(13) if picking_out_obj.trans_inscriptor else "".ljust(13))
		txt += "\n"
		txt += " "*113 + picking_out_obj.trans_licencia if picking_out_obj.trans_licencia else ""
		txt += "\n"*4

		txt += self.get_detail_txt(cr, uid, ids, context)
		
		txt += " "*14 + (picking_out_obj.trans_name[:19].ljust(19) if picking_out_obj.trans_name else "".ljust(19))
		txt += "\n"*2
		txt += " "*14 + (picking_out_obj.trans_ruc[:13].ljust(13) if picking_out_obj.trans_ruc else "".ljust(13))
		txt += "\n"*3
		txt += " "*8 + (picking_out_obj.trans_tipo_comprobante[:18].ljust(18) if picking_out_obj.trans_tipo_comprobante else "".ljust(18))
		txt += " "*9 + picking_out_obj.trans_nro_comprobante[:9].ljust(9) if picking_out_obj.trans_nro_comprobante else "".ljust(9)
		txt += chr(12)
		return txt

	def get_detail_txt(self, cr, uid, ids, context=None):
		result = []
		active_id = ids[0]

		picking_out_obj = self.pool.get('stock.picking').browse(cr, uid, active_id)	
		uom_obj = self.pool.get('product.uom')
		txt =""
		n=0
		for items in picking_out_obj.move_lines:
			# raise osv.except_osv('Alerta', "%0.3f" % precio_unitario)  
			cantidad = items.product_qty
			
			if items.product_id.default_code:
				txt += " "*6+items.product_id.default_code.ljust(6)
			else:
				txt += " ".ljust(12)
			txt += items.product_id.name_template[:50].ljust(101)
			txt += items.product_uom.name.ljust(9)
			txt += " "*4 + ("%0.2f" % cantidad).rjust(9)+"\n"
			n += 1

		cgp_id = self.pool.get('calquipa.guiarem.parameters').search(cr, uid, [])
		cgp = self.pool.get('calquipa.guiarem.parameters').browse(cr, uid, cgp_id)[0]

		if n<cgp.maxlines:
			for x in range(n,cgp.maxlines):
				txt=txt+"\n"
		return txt	



	# funciones para guia de LOGISTICA
	def get_head_txt_log(self, cr, uid, ids, context=None):
		result = []
		active_id = ids[0]
		
		company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=context)
		picking_out_obj = self.pool.get('stock.picking').browse(cr, uid, active_id)
	   
		# raise osv.except_osv('Alerta', compra)
		company_attrs = helper.company(cr, uid, company_id) #atributos company
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

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

		detalle_company = ""

		ruc_company = ""
		txt=""
		txt = txt+chr(27)+chr(15)+chr(27)+chr(48)
		txt = txt+"Log.\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt=txt+" "*28+c_street+"\n"

		ruccliente = picking_out_obj.partner_id.type_number
		if picking_out_obj.partner_id.is_company:
			if picking_out_obj.partner_id.parent_id:
				if picking_out_obj.partner_id.parent_id.type_number:
					ruccliente = picking_out_obj.partner_id.parent_id.type_number
			else:
				if picking_out_obj.partner_id.type_number:
					ruccliente = picking_out_obj.partner_id.type_number

		if picking_out_obj.partner_id.is_company:
			if picking_out_obj.partner_id.parent_id:
				direcciondetino = picking_out_obj.partner_id.parent_id.street
			else:
				direcciondetino = picking_out_obj.partner_id.street
		
		direcciondetino = picking_out_obj.partner_id.street
		for items in picking_out_obj.move_lines:
			txt=txt+" "*28+picking_out_obj.partner_id.name+"\n"
			if ruccliente:
				txt=txt+" "*28+ruccliente+"\n"
			else:
				txt=txt+"\n"
			if direcciondetino:
				txt=txt+" "*38+direcciondetino[:64]+"\n"
			else:
				txt=txt+"\n"
			break

		
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		#txt = txt+"\n"
		#txt = txt+"\n"		
		txt=txt+" "*24+picking_out_obj.date[:10]+" "*50+picking_out_obj.min_date[:10]+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt=txt+" "*114
		if picking_out_obj.motivo_guia:
			txt=txt+picking_out_obj.motivo_guia+"\n"
		else:
			txt=txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"
		txt = txt+"\n"		
		txt=txt+self.get_detail_txt_log(cr, uid, ids, context)+"\n"
		txt = txt+"\n"
		#txt = txt+"\n"
		#txt = txt+"\n"
		carrier = picking_out_obj.carrier_id
		if carrier.marca and carrier.placa:
			txt=txt+" "*32+(carrier.marca+" - "+carrier.placa).ljust(76)
		else:
			espacio = " "
			txt=txt+espacio.ljust(76)
		if carrier.partner_id.name:
			txt=txt+"     "+carrier.partner_id.name[:28]+"\n"
		else:
			txt=txt+"\n"
		if carrier.mtc:
			txt=txt+" "*32+carrier.mtc.ljust(76)
		else:
			espacio = " "
			txt=txt+espacio.ljust(76)
		if carrier.partner_id.street:
			txt=txt+"     "+carrier.partner_id.street[:28]+"\n"
		else:
			txt=txt+"\n"
		if carrier.licencia:
			txt=txt+" "*32+carrier.licencia.ljust(76)
		else:
			espacio = " "
			txt=txt+espacio.ljust(76)

		
		ructranporte = carrier.partner_id.type_number

		if carrier.partner_id.is_company:
			if carrier.partner_id.parent_id:	
				# raise osv.except_osv('Alerta',ructranporte)
				ructranporte = carrier.partner_id.parent_id.type_number
		if carrier.partner_id.type_number:
			txt=txt+"     " + ructranporte
		txt = txt+chr(12)
		return txt

	def get_detail_txt_log(self, cr, uid, ids, context=None):

		result = []
		active_id = ids[0]

		picking_out_obj = self.pool.get('stock.picking').browse(cr, uid, active_id)	
		uom_obj = self.pool.get('product.uom')
		txt =""
		n=0
		for items in picking_out_obj.move_lines:
			# raise osv.except_osv('Alerta', "%0.3f" % precio_unitario)  
			cantidad = items.product_qty
			
			txt=txt+" "*8+str("%0.2f" % cantidad).rjust(9)
			txt=txt+"      "+items.product_uom.name.ljust(10)
			if items.product_id.default_code:
				txt=txt+"  "+items.product_id.default_code.ljust(6)
			else:
				txt=txt+' '.ljust(8)
			txt=txt+" "+items.product_id.product_tmpl_id.name+"\n"
			n=n+1

		cgp_id = self.pool.get('calquipa.guiarem.parameters').search(cr, uid, [])
		print cgp_id, "*"*21

		if n<picking_out_obj.picking_type_id.maxlines:
			for x in range(n,picking_out_obj.picking_type_id.maxlines):
				txt=txt+"\n"
		return txt	

class calquipa_guiarem_parameters(models.Model):
	_name='calquipa.guiarem.parameters'
	_rec_name = 'name'

	name = fields.Char('Nombre',size=50, default='Parametros Generales')
	maxlines = fields.Integer(u'Máximo de Lineas de Guía de Remisión')

	def init(self, cr):
		cr.execute('select id from res_users')
		uid = cr.dictfetchall()
		cr.execute('select id from calquipa_guiarem_parameters')
		ids = cr.fetchall()
		
		if len(ids) == 0:
			cr.execute("""INSERT INTO calquipa_guiarem_parameters  (create_uid, name) VALUES (""" + str(uid[0]['id']) + """, 'Parametros Generales');""")