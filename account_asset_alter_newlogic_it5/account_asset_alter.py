# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import magenta, red , black , blue, gray, Color, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table
from reportlab.lib.units import  cm,mm
from reportlab.lib.utils import simpleSplit

class account_asset_asset(models.Model):
	_inherit = 'account.asset.asset'

	tipo_cambio_d = fields.Float('Tipo Cambio Dolares',digits=(12,3))
	porce_depreci = fields.Float('Porcentaje Depreciación',related='category_id.percent_depreciacion')
	deprec_anual = fields.Float('Depreciación Anual')
	deprec_mensual = fields.Float('Depreciación Mensual')
	bruto_doalres = fields.Float('Bruto Dolares')
	val_deprec_anual_d = fields.Float('Valor de Depreciación Anual en Dólares')
	val_deprec_mensual_d = fields.Float('Valor de Depreciación Mensual en Dolares')
	verif_origen = fields.Boolean('Verificacion',compute="get_verif_origen")

	@api.one
	def get_verif_origen(self):
		t = self.invoice_id.id
		if t:
			self.verif_origen = True
		else:
			self.verif_origen = False

class account_invoice_line(models.Model):
	_inherit = 'account.invoice.line'

	def asset_create(self, cr, uid, lines, context=None):
		context = context or {}
		asset_obj = self.pool.get('account.asset.asset')
		for line in lines:
			if line.asset_category_id:
				fecha_inicio = line.invoice_id.date_invoice
				date_inicio = fecha_inicio
				if fecha_inicio:
					year = int(str(fecha_inicio)[:4])
					mounth = int(str(fecha_inicio)[5:7]) +1
					day = int(str(fecha_inicio)[8:10])
					if mounth == 13:
						year +=1
						mounth= 1
					date_inicio = str(year) + '-' + ( str( mounth )if mounth>9 else ('0'+ str(mounth) )  ) + '-01'
				company_list = self.pool.get('res.company').search(cr,uid,[])
				currency_company = self.pool.get('res.company').browse(cr,uid,company_list)[0].currency_id.id
				vals = {
					'name': line.name,
					'code': line.invoice_id.supplier_invoice_number or line.invoice_id.number or False,
					'invoice_id': line.invoice_id.id,
					'category_id': line.asset_category_id.id,
					'purchase_value': line.price_subtotal * line.invoice_id.currency_rate_auto if line.invoice_id.currency_id.name != 'PEN' else line.price_subtotal,
					'period_id': line.invoice_id.period_id.id,
					'partner_id': line.invoice_id.partner_id.id,
					'company_id': line.invoice_id.company_id.id,
					'currency_id': currency_company,
					'purchase_date' : line.invoice_id.date_invoice,
					'date_start' : date_inicio,
				}
				changed_vals = asset_obj.onchange_category_id(cr, uid, [], vals['category_id'], context=context)
				vals.update(changed_vals['value'])
				asset_id = asset_obj.create(cr, uid, vals, context=context)
				if line.asset_category_id.open_asset:
					asset_obj.validate(cr, uid, [asset_id], context=context)


				vals_update=  {}
				vals_update['tipo_cambio_d'] = line.invoice_id.currency_rate_auto
				vals_update['deprec_anual'] = vals['purchase_value']* line.asset_category_id.percent_depreciacion /100.00
				vals_update['deprec_mensual'] = vals_update['deprec_anual'] / 12.00
				vals_update['bruto_doalres'] = line.price_subtotal  if line.invoice_id.currency_id.name != 'PEN' else vals['purchase_value'] / vals_update['tipo_cambio_d']
				vals_update['val_deprec_anual_d'] = vals_update['bruto_doalres']* line.asset_category_id.percent_depreciacion /100.00
				vals_update['val_deprec_mensual_d'] = vals_update['val_deprec_anual_d'] / 12.00

				asset_obj.write(cr,uid,[asset_id],vals_update,context=context)


		return True



class vista_activo_detraccion_dolar(models.Model):
	_name = 'vista.activo.detraccion.dolar'

	period_id = fields.Many2one('account.period','Periodo',required=True)


	@api.multi
	def do_rebuild(self):

		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		########### PRIMERA HOJA DE LA DATA EN TABLA
		#workbook = Workbook(output, {'in_memory': True})
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		if not direccion:
			raise osv.except_osv('Alerta!', "No fue configurado el directorio para los archivos en Configuración.")
		workbook = Workbook( direccion + 'tempo_depre_acti_dol.xlsx')
		worksheet = workbook.add_worksheet("Depreciacion Dolares")
		bold = workbook.add_format({'bold': True})
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		bord = workbook.add_format()
		bord.set_border(style=1)
		numberdos.set_border(style=1)
		numbertres.set_border(style=1)			
		x= 6				
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.1
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')

		worksheet.write(0,5, u"Depreciación Dolares", bold)

		worksheet.write(2,2, "Periodo:", bold)
		worksheet.write(2,3, self.period_id.code , normal)




		worksheet.write(5,0, "CODIGO ACTIVO",boldbord)
		worksheet.write(5,1, "NOMBRE",boldbord)
		worksheet.write(5,2, "CATEGORIA",boldbord)
		worksheet.write(5,3, "FECHA COMPRA",boldbord)
		worksheet.write(5,4, "FECHA INICIO",boldbord)
		worksheet.write(5,5, "FECHA BAJA",boldbord)
		worksheet.write(5,6, "% DEP",boldbord)
		worksheet.write(5,7, "CUENTA ACTIVO",boldbord)
		worksheet.write(5,8, "CUENTA DEPREC",boldbord)
		worksheet.write(5,9, "RUBRO ACTIVO",boldbord)
		worksheet.write(5,10, "RUBRO DEPREC",boldbord)
		worksheet.write(5,11, "VALOR SOLES",boldbord)
		worksheet.write(5,12, "VALOR USD",boldbord)
		worksheet.write(5,13, "DEPREC MENSUAL SOLES",boldbord)
		worksheet.write(5,14, "DEPREC MENSUAL USD",boldbord)
		worksheet.write(5,15, "NRO PERIODOS",boldbord)
		worksheet.write(5,16, "ACUMULADA SOLES",boldbord)
		worksheet.write(5,17, "ACUMULADA USD",boldbord)


		self.env.cr.execute(""" 
				
				select 
				aaa.codigo, 
				aaa.name,
				aac.name as categoria,
				aaa.purchase_date,
				aaa.date_start,
				aaa.f_baja,
				aac.percent_depreciacion , 
				aa1.code,
				aa2.code,
				rm1.concepto, 
				rm2.concepto,
				aaa.purchase_value,
				aaa.bruto_doalres,
				CASE WHEN aaa.f_baja is null THEN aaa.deprec_mensual ELSE
				    CASE WHEN aaa.f_baja <= '""" +str(self.period_id.date_stop)[:10]+ """'
				    THEN 0 else aaa.deprec_mensual END
				END,

				CASE WHEN aaa.f_baja is null THEN aaa.val_deprec_mensual_d ELSE
				    CASE WHEN aaa.f_baja <= '""" +str(self.period_id.date_stop)[:10]+ """'
				    THEN 0 else aaa.val_deprec_mensual_d END
				END,
				rm3.mes as nro_periodos,
				rm3.mes * (CASE WHEN aaa.f_baja is null THEN aaa.deprec_mensual ELSE
				    CASE WHEN aaa.f_baja <= '""" +str(self.period_id.date_stop)[:10]+ """'
				    THEN 0 else aaa.deprec_mensual END
				END) as acumulado_soles,

				rm3.mes * (CASE WHEN aaa.f_baja is null THEN aaa.val_deprec_mensual_d ELSE
				    CASE WHEN aaa.f_baja <= '""" +str(self.period_id.date_stop)[:10]+ """'
				    THEN 0 else aaa.val_deprec_mensual_d END
				END) as acumulado_dolares
				

				 from 
				account_asset_asset aaa
				left join account_asset_category aac on aac.id = aaa.category_id
				left join account_account aa1 on aa1.id = aac.account_asset_id
				left join account_account aa2 on aa2.id = aac.account_depreciation_id
				left join rm_balance_config_mexicano_line rm1 on rm1.id = aa1.balance_type_mex_id
				left join rm_balance_config_mexicano_line rm2 on rm2.id = aa2.balance_type_mex_id
				left join (
				select * from account_asset_depreciation_line where period_id   = '"""+ self.period_id.code +"""' )
				rm3 on rm3.asset_id=aaa.id

				where (aaa.f_baja is null or aaa.f_baja > '""" +str(self.period_id.date_stop)[:10]+ """')

			""")


		lineas_inf = self.env.cr.fetchall()

		for line in lineas_inf:
			worksheet.write(x,0,line[0] if line[0] else '' ,bord )
			worksheet.write(x,1,line[1] if line[1] else '',bord )
			worksheet.write(x,2,line[2] if line[2] else '',bord)
			worksheet.write(x,3,line[3] if line[3] else '',bord)
			worksheet.write(x,4,line[4] if line[4] else '',bord)
			worksheet.write(x,5,line[5] if line[5] else '',bord)
			worksheet.write(x,6,line[6] ,numberdos)
			worksheet.write(x,7,line[7] if line[7] else '',bord)
			worksheet.write(x,8,line[8] if line[8] else '',bord)
			worksheet.write(x,9,line[9] if line[9] else '',bord)
			worksheet.write(x,10,line[10] if line[10] else '',bord)
			worksheet.write(x,11,line[11],numberdos)
			worksheet.write(x,12,line[12],numberdos)
			worksheet.write(x,13,line[13],numberdos)
			worksheet.write(x,14,line[14],numberdos)
			worksheet.write(x,15,line[15],numberdos)
			worksheet.write(x,16,line[16],numberdos)
			worksheet.write(x,17,line[17],numberdos)

			x = x +1

		tam_col = [10,12,18,10,10,10,10,10,10,18,18,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]

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


		workbook.close()
		
		f = open( direccion + 'tempo_depre_acti_dol.xlsx', 'rb')
		
		
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'DepreciacionDolares.xlsx',
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


