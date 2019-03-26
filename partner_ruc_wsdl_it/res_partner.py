# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions , _
from suds.client import Client
from openerp.osv import osv
import re

class registro_consulta_wsdl(models.Model):
	_name = 'registro.consulta.wsdl'

	usuario  = fields.Many2one('res.users','Usuario')
	ruc = fields.Char('RUC de consulta')

class res_partner(models.Model):
	_inherit = 'res.partner'

	@api.one
	def verify_ruc(self):
		client = Client("http://ws.insite.pe/sunat/ruc.php?wsdl",faults=False,cachingpolicy= 1, location= "http://ws.insite.pe/sunat/ruc.php?wsdl")
		result = client.service.consultaRUC(self.type_number,"jtejada@itgrupo.net","ZDI-9DJ-YA8-D8C","plain")
		texto = result[1].split('|')
		print texto,"verify jean"
		flag = False
		self.env['registro.consulta.wsdl'].create({'usuario':self.env.uid,'ruc':self.type_number})
		for i in texto:
			tmp = i.split('=')
			if tmp[0] == 'status_msg' and tmp[1] == 'OK/1':
				flag = True

		print flag,"flag"
		if flag:
			for j in texto:
				tmp = j.split('=')
				if tmp[0] == 'n1_alias':
					print tmp, "entro caso 1"
					self.name = tmp[1]
				if tmp[0] == 'n1_direccion':

					print tmp, "entro caso 2"
					self.street = tmp[1]
		else:
			self.name = "El RUC es invalido."	
