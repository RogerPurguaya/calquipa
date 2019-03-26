# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
from openerp import pooler

class company:
	"""get attr company"""
	def __init__(self, cr, uid, company_id):
		#print "=" * 10
		#print "En atributos de res.company"
		#print "=" * 10
		cr_dbname = cr.dbname
		res_company = pooler.get_pool(cr_dbname).get('res.company')
		res_company_obj = res_company.browse(cr, uid, company_id)

		self.nombre = res_company_obj.name
		self.currency_id = res_company_obj.currency_id.id
		self.currency = res_company_obj.currency_id
		self.ruc = company_bool = res_company_obj.vat if res_company_obj.vat else "--"
		self.street = res_company_obj.street if res_company_obj.street else "--"
		self.phone = res_company_obj.phone if res_company_obj.phone else "--"
		self.email = res_company_obj.email if res_company_obj.email else "--"
		self.website = res_company_obj.website if res_company_obj.website else "--"
		self.city = res_company_obj.city if res_company_obj.city else "--"
		self.logo = res_company_obj.logo if res_company_obj.logo else "--"

#Numeros expresado en letras
def number_to_letter(number, mi_moneda=None):
	UNIDADES = (
		'',
		'UN ',
		'DOS ',
		'TRES ',
		'CUATRO ',
		'CINCO ',
		'SEIS ',
		'SIETE ',
		'OCHO ',
		'NUEVE ',
		'DIEZ ',
		'ONCE ',
		'DOCE ',
		'TRECE ',
		'CATORCE ',
		'QUINCE ',
		'DIECISEIS ',
		'DIECISIETE ',
		'DIECIOCHO ',
		'DIECINUEVE ',
		'VEINTE '
	)

	DECENAS = (
		'VENTI',
		'TREINTA ',
		'CUARENTA ',
		'CINCUENTA ',
		'SESENTA ',
		'SETENTA ',
		'OCHENTA ',
		'NOVENTA ',
		'CIEN '
	)

	CENTENAS = (
		'CIENTO ',
		'DOSCIENTOS ',
		'TRESCIENTOS ',
		'CUATROCIENTOS ',
		'QUINIENTOS ',
		'SEISCIENTOS ',
		'SETECIENTOS ',
		'OCHOCIENTOS ',
		'NOVECIENTOS '
	)

	MONEDAS = (
		{'country': u'Colombia', 'currency': 'COP', 'singular': u'PESO COLOMBIANO', 'plural': u'PESOS COLOMBIANOS', 'symbol': u'$'},
		{'country': u'Estados Unidos', 'currency': 'USD', 'singular': u'DÓLAR', 'plural': u'DÓLARES', 'symbol': u'US$'},
		{'country': u'Europa', 'currency': 'EUR', 'singular': u'EURO', 'plural': u'EUROS', 'symbol': u'€'},
		{'country': u'México', 'currency': 'MXN', 'singular': u'PESO MEXICANO', 'plural': u'PESOS MEXICANOS', 'symbol': u'$'},
		{'country': u'Perú', 'currency': 'PEN', 'singular': u'SOL', 'plural': u'SOLES', 'symbol': u'S/.'},
		{'country': u'Reino Unido', 'currency': 'GBP', 'singular': u'LIBRA', 'plural': u'LIBRAS', 'symbol': u'£'}
	)
	# Para definir la moneda me estoy basando en los código que establece el ISO 4217
	# Decidí poner las variables en inglés, porque es más sencillo de ubicarlas sin importar el país
	# Si, ya sé que Europa no es un país, pero no se me ocurrió un nombre mejor para la clave.

	def __convert_group(n):
		"""Turn each group of numbers into letters"""
		output = ''

		if(n == '100'):
			output = "CIEN"
		elif(n[0] != '0'):
			output = CENTENAS[int(n[0]) - 1]

		k = int(n[1:])
		if(k <= 20):
			output += UNIDADES[k]
		else:
			if((k > 30) & (n[2] != '0')):
				output += '%sY %s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])
			else:
				output += '%s%s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])
		return output
	#raise osv.except_osv('Alerta', number)
	number=str(round(float(number),2))
	separate = number.split(".")
	number = int(separate[0])
	if mi_moneda != None:
		try:
			moneda = ""
			for moneda1 in MONEDAS:
				if moneda1['currency']==mi_moneda:
				# moneda = ifilter(lambda x: x['currency'] == mi_moneda, MONEDAS).next()
				# return "Tipo de moneda inválida"
					if number < 2:
						#raise osv.except_osv('Alerta', number)
						if float(number)==0:
							moneda = moneda1['plural']
						else:
							if int(separate[1]) > 0:
								moneda = moneda1['plural']
							else:
								moneda = moneda1['singular']
					else:
						moneda = moneda1['plural']
		except:
			return "Tipo de moneda inválida"
	else:
		moneda = ""

	if int(separate[1]) >= 0:
		moneda = "con " + str(separate[1]).ljust(2,'0') + "/" + "100 " + moneda

	"""Converts a number into string representation"""
	converted = ''
	
	if not (0 <= number < 999999999):
		raise osv.except_osv('Alerta', number)
		#return 'No es posible convertir el numero a letras'

	
	
	number_str = str(number).zfill(9)
	millones = number_str[:3]
	miles = number_str[3:6]
	cientos = number_str[6:]
	

	if(millones):
		if(millones == '001'):
			converted += 'UN MILLON '
		elif(int(millones) > 0):
			converted += '%sMILLONES ' % __convert_group(millones)

	if(miles):
		if(miles == '001'):
			converted += 'MIL '
		elif(int(miles) > 0):
			converted += '%sMIL ' % __convert_group(miles)

	if(cientos):
		if(cientos == '001'):
			converted += 'UN '
		elif(int(cientos) > 0):
			converted += '%s ' % __convert_group(cientos)
	if float(number_str)==0:
		converted += 'CERO '
	converted += moneda

	return converted.upper()
