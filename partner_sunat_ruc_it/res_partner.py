# -*- encoding: utf-8 -*-
from openerp import models, fields, api,exceptions , _
from openerp.osv import osv



class res_partner(models.Model):
	_name='res.partner'
	_inherit='res.partner'
	
	type_contribuyente = fields.Char('Tipo Contribuyente',size=200)
	type_documento = fields.Char('Tipo de Documento',size=200)
	type_nombre_comercial = fields.Char('Nombre Comercial',size=200)
	type_fecha_inscripcion = fields.Char('Fecha de Inscripción',size=200)
	type_estado_contribuyente = fields.Char('Estado del Contribuyente',size=200)
	type_condicion_contribuyente = fields.Char('Condición del Contribuyente',size=200)
	type_direccion_domicilio = fields.Char('Dirección del Domicilio Fiscal',size=200)
	type_emision_comprobante = fields.Char('Sistema de Emisión de Comprobante',size=200)
	type_sistema_contabilidad = fields.Char('Sistema de Contabilidad',size=200)
	type_actividad_economica = fields.Char('Actividad(es) Económica(s)',size=200)
	type_comprobante_pago_impreso = fields.Char('Comprobante de Pago c/aut. de impresión F. 806 u 816',size=200)
	type_emision_electronica = fields.Char('Sistema de Emisión Electrónica',size=200)
	type_emisor_electronico_desde = fields.Char('Emisor Electrónico desde',size=200)
	type_comprobante_electronico = fields.Char('Comprobantes Electrónicos',size=200)
	type_afiliado_ple = fields.Char('Afiliado al PLE desde',size=200)
	type_padrones = fields.Char('Padrones',size=200)

	type_fecha_baja = fields.Char('Fecha Baja',size=50)
	type_inicio_actividades = fields.Char('Fecha de Inicio de Actividades',size=200)
	type_comercio_exterior = fields.Char('Actividad de Comercio Exterior',size=200)

	bucle= 0
	@api.one
	def extraer_sunat(self):
		if self.bucle >5:
			raise  osv.except_osv('Alerta!', "La conexión con Sunat esta fallando! Revise su conexión con internet del servidoro de la página de Sunat.")
		""" esto es prueba"""
		from selenium import webdriver
		from selenium.webdriver.support.ui import WebDriverWait
		from selenium.webdriver.common.by import By
		from selenium.webdriver.support import expected_conditions as EC
		browser = webdriver.Firefox()
		browser.get('http://www.sunat.gob.pe/cl-ti-itmrconsruc/frameCriterioBusqueda.jsp')

		try:
			element = WebDriverWait(browser, 5).until( EC.presence_of_element_located((By.ID, "s2"))  )
		except:
			pass
		
		browser.save_screenshot('prueba.png')
		from PIL import Image
		im = Image.open('prueba.png')
		reg = im.crop((715,40,833,75))
		reg.save('prueba2.png','JPEG')
		import pytesseract
		print "---------------ESTO ES:---------------"

		try:
			element = WebDriverWait(browser, 3).until( EC.presence_of_element_located((By.ID, "s2"))  )
		except:
			pass

		catpcha = pytesseract.image_to_string(Image.open('prueba2.png'))
		print catpcha
		try:
			catpcha_visual= browser.find_element_by_name('codigo')
		except:
			flag= False
			while flag:
				try:
					exec(raw_input("Ingresa: "))
				except Exception as inst:
					print "Te webiaste:", inst
			browser.close()
			return self.extraer_sunat()
		catpcha_visual.send_keys(catpcha)


		catpcha_visual= browser.find_element_by_name('search1')
		catpcha_visual.send_keys(self.type_number)

		browser.find_element_by_class_name('form-button').click()

		if len(browser.window_handles) == 1:
			
			tt = browser.switch_to_alert()
			if tt:


				flag= False
				while flag:
					try:
						exec(raw_input("Ingresa: "))
					except Exception as inst:
						print "Te webiaste:", inst
				if tt.text== 'Por favor, ingrese numero de RUC valido.':
					tt.accept()
					browser.close()
					raise osv.except_osv('Alerta!', "El número de RUC no es valido.")
				else:
					tt.accept()
					browser.close()
					return self.extraer_sunat()
			browser.close()
			return self.extraer_sunat()
		browser.switch_to_window(browser.window_handles[1])

		datos = []
		for i in browser.find_elements_by_tag_name('td'):
			print i.text
			datos.append(i.text)

		if len(datos) < 2:
			t_handles = browser.window_handles
			for i_h in t_handles:
				browser.switch_to_window(i_h)
				browser.close()
			return self.extraer_sunat()

		if datos[1][:16] == u'El n\xfamero de RUC':
			t_handles = browser.window_handles
			for i_h in t_handles:
				browser.switch_to_window(i_h)
				browser.close()
			raise osv.except_osv('Alerta!', "El número de RUC no es valido o no existe en los registros de SUNAT.")

		for i in range(len(datos)):
			if datos[i] == u'N\xfamero de RUC:': 

				self.name= datos[i+1].split('-')[1].strip()

			if datos[i] == u'Tipo Contribuyente:':
				self.type_contribuyente =datos[i+1] 
				
			if datos[i] == u'Nombre Comercial:':
				self.type_nombre_comercial = datos[i+1]

			if datos[i] == u'Fecha de Inscripci\xf3n:':
				self.type_fecha_inscripcion = datos[i+1]

			if datos[i] == u'Estado del Contribuyente:':
				self.type_estado_contribuyente = datos[i+1]

			if datos[i] == u'Fecha de Baja:':
				self.type_fecha_baja = datos[i+1]

			if datos[i] == u'Condici\xf3n del Contribuyente:':
				self.type_condicion_contribuyente = datos[i+1]

			if datos[i] == u'Direcci\xf3n del Domicilio Fiscal:':
				self.type_direccion_domicilio = datos[i+1]

			if datos[i] == u'Sistema de Emisi\xf3n de Comprobante:':
				self.type_emision_comprobante = datos[i+1]

			if datos[i] == u'Sistema de Contabilidad:':
				self.type_sistema_contabilidad = datos[i+1]

			if datos[i] == u'Actividad(es) Econ\xf3mica(s):':
				self.type_actividad_economica = datos[i+1]

			if datos[i] == u'Comprobantes de Pago c/aut. de impresi\xf3n (F. 806 u 816):':
				self.type_comprobante_pago_impreso = datos[i+1]

			if datos[i] == u'Sistema de Emision Electronica:':
				self.type_emision_electronica = datos[i+1]

			if datos[i] == u'Emisor electr\xf3nico desde:':
				self.type_emisor_electronico_desde = datos[i+1]

			if datos[i] == u'Comprobantes Electr\xf3nicos:':
				self.type_comprobante_electronico = datos[i+1]

			if datos[i] == u'Afiliado al PLE desde:':
				self.type_afiliado_ple = datos[i+1]

			if datos[i] == u'Padrones :':
				self.type_padrones = datos[i+1]

			if datos[i] == u'Fecha de Inicio de Actividades:':
				self.type_inicio_actividades = datos[i+1]

			if datos[i] == u'Actividad de Comercio Exterior:':
				self.type_comercio_exterior = datos[i+1]


		flag= False
		while flag:
			try:
				exec(raw_input("Ingresa: "))
			except Exception as inst:
				print "Te webiaste:", inst

		t_handles = browser.window_handles
		for i_h in t_handles:
			browser.switch_to_window(i_h)
			browser.close()
	
		self.bucle = 0

		return True
