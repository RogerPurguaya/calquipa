# -*- encoding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs
from datetime import datetime

class reporte_facturas_pagos_wizard(osv.TransientModel):
	_name='reporte.facturas.pagos.wizard'
	period_ini = fields.Many2one('account.period','Periodo Inicial')
	period_end = fields.Many2one('account.period','Periodo Final')
	#asientos =  fields.Selection([('posted','Asentados'),('draft','No Asentados'),('both','Ambos')], 'Asientos')
	moneda = fields.Many2one('res.currency','Moneda')
	cuentas = fields.Many2many('account.account', string='Cuentas')
	fiscalyear_id = fields.Many2one('account.fiscalyear','Año Fiscal')
	
	@api.onchange('fiscalyear_id')
	def onchange_fiscalyear(self):
		if self.fiscalyear_id:
			return {'domain':{'period_ini':[('fiscalyear_id','=',self.fiscalyear_id.id )], 'period_end':[('fiscalyear_id','=',self.fiscalyear_id.id )]}}
		else:
			return {'domain':{'period_ini':[], 'period_end':[]}}

	@api.onchange('period_ini')
	def _change_periodo_ini(self):
		if self.period_ini:
			self.period_end= self.period_ini

	@api.multi
	def do_rebuild(self):
		period_ini = self.period_ini
		period_end = self.period_end
		has_currency = self.moneda
		
		filtro = []
		
		currency = False
		if has_currency.id != False:
			user = self.env['res.users'].browse(self.env.uid)
			if user.company_id.id == False:
				raise osv.except_osv('Alerta!', "No existe una compañia configurada para el usuario actual.")
			if user.company_id.currency_id.id == False:
				raise osv.except_osv('Alerta!', "No existe una moneda configurada para la compañia del usuario actual.")
			
			if has_currency.id != user.company_id.currency_id.id:
				currency = True
				
		self.env.cr.execute("""
			CREATE OR REPLACE view reporte_facturas_pagos as 
			(SELECT * FROM get_reporte_facturas_pagos("""+ str(currency)+ 
			""",periodo_num('""" + period_ini.code + """'),periodo_num('""" + period_end.code +"""')) 
		)""")

		if self.cuentas:
			libros_list = ["Saldo Inicial"]
			for i in  self.cuentas:
				libros_list.append(i.code)
			filtro.append( ('cuenta','in',tuple(libros_list)) )
		
		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		########### PRIMERA HOJA DE LA DATA EN TABLA
		#workbook = Workbook(output, {'in_memory': True})

		direccion = self.env['main.parameter'].search([])[0].dir_create_file

		workbook = Workbook(direccion +'Reporte_facturas_pagos.xlsx')
		worksheet = workbook.add_worksheet("Reporte de Facturas y pagos")
		bold = workbook.add_format({'bold': True})
		normal = workbook.add_format()
		
		title = workbook.add_format({'bold':True})
		title.set_align('center')
		title.set_font_size(10)
		title.set_bg_color('#fff06d')
		title.set_font_color('#000000')
		title.set_text_wrap()

		total2 = workbook.add_format({'num_format':'0.00'})
		total2.set_align('center')
		total2.set_bg_color('#e3ccff')
		total2.set_font_color('#000000')
		
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(9)
		boldbord.set_bg_color('#DCE6F1')
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		bord = workbook.add_format()
		bord.set_border(style=1)
		numberdos.set_border(style=1)
		numbertres.set_border(style=1)

		x= 5				
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')

		worksheet.merge_range(0,0,0,4, "Reporte de facturas y pagos:", bold)
		worksheet.merge_range(1,0,1,3, self.period_ini.name, normal)
		worksheet.merge_range(2,0,2,3, self.period_end.name, normal)
		worksheet.write(3,0, "Fecha:",bold)
		worksheet.merge_range(3,1,3,3, str(datetime.today().date()), normal)
		
		worksheet.write(4,0, "Periodo",boldbord)
		worksheet.write(4,1, "Libro",boldbord)
		worksheet.write(4,2, u"Fecha Emisión y Pago",boldbord)
		worksheet.write(4,3, "Fecha Vencimiento",boldbord)
		worksheet.write(4,4, "Tipo Documento",boldbord)
		worksheet.write(4,5, u"Número",boldbord)
		worksheet.write(4,6, u"RUC",boldbord)
		worksheet.write(4,7, u"Partner",boldbord)
		worksheet.write(4,8, "Voucher",boldbord)
		worksheet.write(4,9, "Cuenta",boldbord)
		worksheet.write(4,10, u"Diarios",boldbord)
		worksheet.write(4,11, u"Medio de Pago",boldbord)
		worksheet.write(4,12, u"Número de operación",boldbord)
		worksheet.write(4,13, "Debe",boldbord)
		worksheet.write(4,14, "Haber",boldbord)
		worksheet.write(4,15, "Saldo",boldbord)
		worksheet.write(4,16, "Divisa",boldbord)
		worksheet.write(4,17, "Tipo Cambio",boldbord)
		worksheet.write(4,18, "Importe Divisa",boldbord)
		worksheet.write(4,19, u"Conciliación",boldbord)
		worksheet.write(4,20, u"Glosa",boldbord)
		saldo = 0
		totales = [0,0]
		tmp_numero = None
		for line in self.env['reporte.facturas.pagos'].search(filtro).sorted(key=lambda x:x.numero):
			
			if tmp_numero!=None and tmp_numero!=line.numero:
				worksheet.write(x,12,'Total',title)
				worksheet.write(x,13,totales[0],total2)
				worksheet.write(x,14,totales[1],total2)
				worksheet.write(x,15,totales[0]-totales[1],total2)
				totales = [0,0]
				saldo = 0
				x+=2


			tmp_numero = line.numero if line.numero else ''
			totales[0] += line.debe
			totales[1] += line.haber			

			worksheet.write(x,0,line.periodo if line.periodo else '' ,bord )
			worksheet.write(x,1,line.libro if line.libro  else '',bord )
			worksheet.write(x,2,line.fechaemision if line.fechaemision else '',bord)
			worksheet.write(x,3,line.fechavencimiento if line.fechavencimiento else '',bord)
			worksheet.write(x,4,line.tipodocumento if line.tipodocumento else '',bord)
			worksheet.write(x,5,line.numero if line.numero  else '',bord)				
			worksheet.write(x,6,line.ruc if line.ruc  else '',bord)
			worksheet.write(x,7,line.partner if line.partner  else '',bord)
			worksheet.write(x,8,line.voucher if line.voucher  else '',bord)
			worksheet.write(x,9,line.cuenta if line.cuenta  else '',bord)
			worksheet.write(x,10,line.diario if line.diario  else '',bord)
			worksheet.write(x,11,line.medio_pago if line.medio_pago  else '',bord)
			worksheet.write(x,12,line.ref_pago if line.ref_pago  else '',bord)
			worksheet.write(x,13,line.debe ,numberdos)
			worksheet.write(x,14,line.haber ,numberdos)

			saldo = saldo + line.debe - line.haber
			
			worksheet.write(x,15,saldo ,numberdos)
			worksheet.write(x,16,line.divisa if  line.divisa else '',bord)
			worksheet.write(x,17,line.tipocambio ,numbertres)
			worksheet.write(x,18,line.importedivisa ,numberdos)
			worksheet.write(x,19,line.conciliacion if line.conciliacion else '',bord)
			worksheet.write(x,20,line.glosa if line.glosa else '',bord)
			
			x+=1

		if tmp_numero!=None:
			worksheet.write(x,13,totales[0],numberdos)
			worksheet.write(x,14,totales[1],numberdos)
			worksheet.write(x,15,totales[0]-totales[1],numberdos)

		tam_col = [9,6,10,10,5,11,13,30,11,11,23,23,10,12,12,12,10,10,10,10,25]

		worksheet.set_column('A:A', tam_col[0])
		worksheet.set_column('B:B', tam_col[1])
		worksheet.set_column('C:C', tam_col[2])
		worksheet.set_column('D:D', tam_col[3])
		worksheet.set_column('E:E', tam_col[4])
		worksheet.set_column('F:F', tam_col[5])
		worksheet.set_column('G:G', tam_col[6])
		worksheet.set_column('H:H', tam_col[7])
		worksheet.set_column('I:I', tam_col[8])
		worksheet.set_column('J:J', tam_col[9])
		worksheet.set_column('K:K', tam_col[10])
		worksheet.set_column('L:L', tam_col[11])
		worksheet.set_column('M:M', tam_col[12])
		worksheet.set_column('N:N', tam_col[13])
		worksheet.set_column('O:O', tam_col[14])
		worksheet.set_column('P:P', tam_col[15])
		worksheet.set_column('Q:Q', tam_col[16])
		worksheet.set_column('R:R', tam_col[17])
		worksheet.set_column('S:S', tam_col[18])
		worksheet.set_column('T:T', tam_col[19])
		worksheet.set_column('U:U', tam_col[20])
		workbook.close()
		
		f = open(direccion + 'Reporte_facturas_pagos.xlsx', 'rb')
		
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'ReporteFacturasPagos.xlsx',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		#mod_obj = self.env['ir.model.data']
		#act_obj = self.env['ir.actions.act_window']
		sfs_id = self.env['export.file.save'].create(vals)
		# result = {}
		# view_ref = mod_obj.get_object_reference('account_contable_book_it', 'export_file_save_action')
		# view_id = view_ref and view_ref[1] or False
		# result = act_obj.read( [view_id] )
	
		return {
			"type": "ir.actions.act_window",
			"res_model": "export.file.save",
			"views": [[False, "form"]],
			"res_id": sfs_id.id,
			"target": "new",
		}
	

