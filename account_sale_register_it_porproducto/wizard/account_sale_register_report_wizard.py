# -*- encoding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs
import pprint

class account_sale_register_report_wizard_detallado(osv.TransientModel):
	_name='account.sale.register.report.wizard.detallado'
	period_ini = fields.Many2one('account.period','Periodo Inicial',required=True)
	period_end = fields.Many2one('account.period','Periodo Final',required=True)
	fiscalyear_id = fields.Many2one('account.fiscalyear','Año Fiscal',required=True)



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
		
		filtro = []
		
		self.env.cr.execute("""
			select T.periodo,T.fechaemision,T.tipodocumento, T.serie || '-' || T. numero as numero, T.partner, pp.name_template as producto, aml.quantity as cantidad,
pu.name as unidadmedida,abs(aml.debit-aml.credit) / aml.quantity as PrecioUnitario, (-aml.debit+aml.credit) as subtotal,((-aml.debit+aml.credit)) / (coalesce(T.inafecto,0)+ coalesce(T.valorexp,0)+ coalesce(T.baseimp,0) ) *T.igv as igv, 

(-aml.debit+aml.credit) + coalesce(((-aml.debit+aml.credit)) / (coalesce(T.inafecto,0)+ coalesce(T.valorexp,0)+ coalesce(T.baseimp,0) ) *T.igv,0) as total 
, am.id,t.tipodecambio,t.divisa
from get_venta_1_1_1(false,periodo_num('""" + period_ini.code + """'),periodo_num('""" + period_end.code +"""')) T
inner join account_move am on am.id = T.am_id
inner join account_move_line aml on aml.move_id = am.id
left join product_product pp on aml.product_id = pp.id
left join product_uom pu on pu.id = aml.product_uom_id
inner join account_account aa on aml.account_id = aa.id and left(aa.code,1) in ('7','2')

		""")

		contenido = self.env.cr.fetchall()

		if True:

			import io
			from xlsxwriter.workbook import Workbook
			output = io.BytesIO()
			########### PRIMERA HOJA DE LA DATA EN TABLA
			#workbook = Workbook(output, {'in_memory': True})
			direccion = self.env['main.parameter'].search([])[0].dir_create_file
			workbook = Workbook( direccion + 'tempo_libroventas.xlsx')
			worksheet = workbook.add_worksheet("Registro Ventas")
			bold = workbook.add_format({'bold': True})
			normal = workbook.add_format()
			boldbord = workbook.add_format({'bold': True})
			boldbord.set_border(style=2)
			boldbord.set_align('center')
			boldbord.set_align('vcenter')
			boldbord.set_text_wrap()
			boldbord.set_font_size(9)
			boldbord.set_bg_color('#DCE6F1')


			title = workbook.add_format({'bold': True})
			title.set_align('center')
			title.set_align('vcenter')
			title.set_text_wrap()
			title.set_font_size(18)
			numbertres = workbook.add_format({'num_format':'0.000'})
			numberdos = workbook.add_format({'num_format':'0.00'})
			bord = workbook.add_format()
			bord.set_border(style=1)
			numberdos.set_border(style=1)
			numbertres.set_border(style=1)			
			x= 5				
			tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			tam_letra = 1.2
			import sys
			reload(sys)
			sys.setdefaultencoding('iso-8859-1')


			worksheet.merge_range(0,0,0,11,"REGISTRO DE VENTA",title)

			worksheet.write(1,0, "Registro Ventas:", bold)
			
			worksheet.write(1,1, self.period_ini.name, normal)
			
			worksheet.write(1,2, self.period_end.name, normal)
			
			worksheet.write(2,0, "Fecha:",bold)
			
			import datetime
			worksheet.write(2,1, str(datetime.datetime.today())[:10], normal)
			

			worksheet.write(4,0, "Periodo",boldbord)
			worksheet.write(4,1, "Fecha de Factura",boldbord)
			worksheet.write(4,2, "Tipo de Documento",boldbord)
			worksheet.write(4,3, "Nro de Factura",boldbord)
			worksheet.write(4,4, "Cliente",boldbord)
			worksheet.write(4,5, "Producto",boldbord)
			worksheet.write(4,6, "Cantidad",boldbord)
			worksheet.write(4,7, "Unidad De Medida",boldbord)
			worksheet.write(4,8, "Precio Unitario",boldbord)
			worksheet.write(4,9, "Subtotal",boldbord)
			worksheet.write(4,10, "IGV",boldbord)
			worksheet.write(4,11, "Total",boldbord)
			worksheet.write(4,12, "Tipo de Cambio",boldbord)
			worksheet.write(4,13, "Moneda",boldbord)

			for line in contenido:
				worksheet.write(x,0,line[0] if line[0] else '' ,bord )
				worksheet.write(x,1,line[1] if line[1] else '' ,bord )
				worksheet.write(x,2,line[2] if line[2] else '' ,bord )
				worksheet.write(x,3,line[3] if line[3] else '' ,bord )
				worksheet.write(x,4,line[4] if line[4] else '' ,bord )
				worksheet.write(x,5,line[5] if line[5] else '' ,bord )
				worksheet.write(x,6,line[6]  ,numberdos )
				worksheet.write(x,7,line[7] if line[7] else '' ,bord )
				worksheet.write(x,8,line[8]  ,numberdos )
				worksheet.write(x,9,line[9]  ,numberdos )
				worksheet.write(x,10,line[10]  ,numberdos )
				worksheet.write(x,11,line[11]  ,numberdos )
				worksheet.write(x,12,line[13]  ,numberdos )
				worksheet.write(x,13,line[14]  ,numberdos )

				x = x +1

			tam_col = [10,10,10,20,18,11,8,11,11,11,11,11,11,11,11,11,5,8,10,8,9]
			worksheet.set_row(0, 30)

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

			workbook.close()
			
			f = open(direccion + 'tempo_libroventas.xlsx', 'rb')
			
			
			sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
			vals = {
				'output_name': 'RegistroVentas.xlsx',
				'output_file': base64.encodestring(''.join(f.readlines())),		
			}

			mod_obj = self.env['ir.model.data']
			act_obj = self.env['ir.actions.act_window']
			sfs_id = self.env['export.file.save'].create(vals)
			result = {}
			view_ref = mod_obj.get_object_reference('account_contable_book_it', 'export_file_save_action')
			view_id = view_ref and view_ref[1] or False
			result = act_obj.read( [view_id] )
			print sfs_id
			return {
			    "type": "ir.actions.act_window",
			    "res_model": "export.file.save",
			    "views": [[False, "form"]],
			    "res_id": sfs_id.id,
			    "target": "new",
			}

		
