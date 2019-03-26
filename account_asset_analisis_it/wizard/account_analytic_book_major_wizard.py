# -*- encoding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs


class account_asset_analisis2f_wizard(osv.TransientModel):
	_name='account.asset.analisis2f.wizard'

	ejercicio_id = fields.Many2one('account.fiscalyear','Ejercicio',required=True)
	period_id = fields.Many2one('account.period','Periodo',required=True)

	@api.multi
	def do_rebuild(self):

		if True:

			import io
			from xlsxwriter.workbook import Workbook
			output = io.BytesIO()
			########### PRIMERA HOJA DE LA DATA EN TABLA
			#workbook = Workbook(output, {'in_memory': True})

			direccion = self.env['main.parameter'].search([])[0].dir_create_file

			workbook = Workbook(direccion +'analisis_activos.xlsx')
			worksheet = workbook.add_worksheet("Analisis Activo")
			bold = workbook.add_format({'bold': True})
			normal = workbook.add_format()
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
			x= 4				
			tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			tam_letra = 1.2
			import sys
			reload(sys)
			sys.setdefaultencoding('iso-8859-1')

			worksheet.write(0,0, u"ANALISIS DE ACTIVO FIJO POR PERIODO", bold)
			worksheet.write(1,0, u"EJERCICIO: " + self.ejercicio_id.name , bold)
			worksheet.write(2,0, u"PERIODO" + self.period_id.code, bold)
		
			#worksheet.write(1,1, total.date.strftime('%Y-%m-%d %H:%M'),bord)
			import datetime
			

			worksheet.write(3,0, u"Código",boldbord)
			worksheet.write(3,1, "Padre",boldbord)
			worksheet.write(3,2, "Fecha Compra",boldbord)
			worksheet.write(3,3, "Fecha Uso",boldbord)
			worksheet.write(3,4, "Factura",boldbord)
			worksheet.write(3,5, "Activo",boldbord)
			worksheet.write(3,6, "Valor Compra",boldbord)
			worksheet.write(3,7, "Dep. Ejer. Anterior",boldbord)
			worksheet.write(3,8, u"Enero",boldbord)
			worksheet.write(3,9, "Febrero",boldbord)
			worksheet.write(3,10, "Marzo",boldbord)
			worksheet.write(3,11, "Abril",boldbord)
			worksheet.write(3,12, "Mayo",boldbord)
			worksheet.write(3,13, "Junio",boldbord)
			worksheet.write(3,14, "Julio",boldbord)
			worksheet.write(3,15, u"Agosto",boldbord)
			worksheet.write(3,16, u"Septiembre",boldbord)
			worksheet.write(3,17, u"Octubre",boldbord)
			worksheet.write(3,18, "Noviembre",boldbord)
			worksheet.write(3,19, "Diciembre",boldbord)
			worksheet.write(3,20, u"Dep. Acumulada",boldbord)
			worksheet.write(3,21, u"Valor menos Depreciación",boldbord)
			worksheet.write(3,22, u"Cuenta Activo",boldbord)
			worksheet.write(3,23, u"Cuenta Depreciación",boldbord)
			worksheet.write(3,24, u"Cuenta Analítica",boldbord)
			worksheet.write(3,25, u"Distribución",boldbord)
			
				
			self.env.cr.execute("""
				select 
	aaa.codigo as codigo,
	padre.name as padre, 
	aaa.purchase_date as fechacompra,
	aaa.date_start as fechainicio,
	CASE WHEN aaa.invoice_id is not null THEN ai.supplier_invoice_number ELSE aaa.code END as nro_comprobante,
	aaa.name as activo,
	aaa.purchase_value as valor,
	coalesce(asdlA.depreciated_value,0) as dep_ejer_anterior,
	coalesce(asdl1.depreciated_value,0) as enero,
	coalesce(asdl2.depreciated_value,0) as febrero,
	coalesce(asdl3.depreciated_value,0) as marzo,
	coalesce(asdl4.depreciated_value,0) as abril,
	coalesce(asdl5.depreciated_value,0) as mayo,
	coalesce(asdl6.depreciated_value,0) as junio,
	coalesce(asdl7.depreciated_value,0) as julio,
	coalesce(asdl8.depreciated_value,0) as agosto,
	coalesce(asdl9.depreciated_value,0) as septiembre,
	coalesce(asdl10.depreciated_value,0) as octubre,
	coalesce(asdl11.depreciated_value,0) as noviembre,
	coalesce(asdl12.depreciated_value,0) as diciembre,


	coalesce(asdlA.depreciated_value,0) +
	coalesce(asdl1.depreciated_value,0) +
	coalesce(asdl2.depreciated_value,0) +
	coalesce(asdl3.depreciated_value,0) +
	coalesce(asdl4.depreciated_value,0) +
	coalesce(asdl5.depreciated_value,0) +
	coalesce(asdl6.depreciated_value,0) +
	coalesce(asdl7.depreciated_value,0) +
	coalesce(asdl8.depreciated_value,0) +
	coalesce(asdl9.depreciated_value,0) +
	coalesce(asdl10.depreciated_value,0) +
	coalesce(asdl11.depreciated_value,0) +
	coalesce(asdl12.depreciated_value,0) as total,
aaa.purchase_value - (	coalesce(asdlA.depreciated_value,0) +
	coalesce(asdl1.depreciated_value,0) +
	coalesce(asdl2.depreciated_value,0) +
	coalesce(asdl3.depreciated_value,0) +
	coalesce(asdl4.depreciated_value,0) +
	coalesce(asdl5.depreciated_value,0) +
	coalesce(asdl6.depreciated_value,0) +
	coalesce(asdl7.depreciated_value,0) +
	coalesce(asdl8.depreciated_value,0) +
	coalesce(asdl9.depreciated_value,0) +
	coalesce(asdl10.depreciated_value,0) +
	coalesce(asdl11.depreciated_value,0) +
	coalesce(asdl12.depreciated_value,0)) as valormenos,
aa1.code as cu_activo,
aa2.code as cu_depre,
aya.name as cu_analitica,
aypl.name as cu_distrib


	from account_asset_asset aaa
	left join account_asset_asset padre on padre.id =aaa.parent_id
	left join account_asset_category aac on aac.id = aaa.category_id
	left join res_partner rp on rp.id = aaa.partner_id
	left join (select asset_id,sum(depreciated_value) as depreciated_value from account_asset_depreciation_line where periodo_num(period_id) < """ + self.ejercicio_id.name + """00  group by asset_id) asdlA on asdlA.asset_id = aaa.id
	left join (select asset_id,depreciated_value,depreciation_acum,period_id from account_asset_depreciation_line  inner join account_asset_asset on account_asset_asset.id = account_asset_depreciation_line.asset_id where period_id='01/""" + self.ejercicio_id.name + """' and periodo_num(period_id)<= periodo_num('""" +self.period_id.code+ """') and ( CASE WHEN account_asset_asset.f_baja is not Null THEN account_asset_asset.f_baja > '01/01/""" + self.ejercicio_id.name + """' else True END)) asdl1 on asdl1.asset_id = aaa.id
	left join (select asset_id,depreciated_value,depreciation_acum,period_id from account_asset_depreciation_line  inner join account_asset_asset on account_asset_asset.id = account_asset_depreciation_line.asset_id where period_id='02/""" + self.ejercicio_id.name + """' and periodo_num(period_id)<= periodo_num('""" +self.period_id.code+ """') and ( CASE WHEN account_asset_asset.f_baja is not Null THEN account_asset_asset.f_baja > '01/02/""" + self.ejercicio_id.name + """' else True END)) asdl2 on asdl2.asset_id = aaa.id
	left join (select asset_id,depreciated_value,depreciation_acum,period_id from account_asset_depreciation_line  inner join account_asset_asset on account_asset_asset.id = account_asset_depreciation_line.asset_id where period_id='03/""" + self.ejercicio_id.name + """' and periodo_num(period_id)<= periodo_num('""" +self.period_id.code+ """') and ( CASE WHEN account_asset_asset.f_baja is not Null THEN account_asset_asset.f_baja > '01/03/""" + self.ejercicio_id.name + """' else True END)) asdl3 on asdl3.asset_id = aaa.id
	left join (select asset_id,depreciated_value,depreciation_acum,period_id from account_asset_depreciation_line  inner join account_asset_asset on account_asset_asset.id = account_asset_depreciation_line.asset_id where period_id='04/""" + self.ejercicio_id.name + """' and periodo_num(period_id)<= periodo_num('""" +self.period_id.code+ """') and ( CASE WHEN account_asset_asset.f_baja is not Null THEN account_asset_asset.f_baja > '01/04/""" + self.ejercicio_id.name + """' else True END)) asdl4 on asdl4.asset_id = aaa.id
	left join (select asset_id,depreciated_value,depreciation_acum,period_id from account_asset_depreciation_line  inner join account_asset_asset on account_asset_asset.id = account_asset_depreciation_line.asset_id where period_id='05/""" + self.ejercicio_id.name + """' and periodo_num(period_id)<= periodo_num('""" +self.period_id.code+ """') and ( CASE WHEN account_asset_asset.f_baja is not Null THEN account_asset_asset.f_baja > '01/05/""" + self.ejercicio_id.name + """' else True END)) asdl5 on asdl5.asset_id = aaa.id
	left join (select asset_id,depreciated_value,depreciation_acum,period_id from account_asset_depreciation_line  inner join account_asset_asset on account_asset_asset.id = account_asset_depreciation_line.asset_id where period_id='06/""" + self.ejercicio_id.name + """' and periodo_num(period_id)<= periodo_num('""" +self.period_id.code+ """') and ( CASE WHEN account_asset_asset.f_baja is not Null THEN account_asset_asset.f_baja > '01/06/""" + self.ejercicio_id.name + """' else True END)) asdl6 on asdl6.asset_id = aaa.id
	left join (select asset_id,depreciated_value,depreciation_acum,period_id from account_asset_depreciation_line  inner join account_asset_asset on account_asset_asset.id = account_asset_depreciation_line.asset_id where period_id='07/""" + self.ejercicio_id.name + """' and periodo_num(period_id)<= periodo_num('""" +self.period_id.code+ """') and ( CASE WHEN account_asset_asset.f_baja is not Null THEN account_asset_asset.f_baja > '01/07/""" + self.ejercicio_id.name + """' else True END)) asdl7 on asdl7.asset_id = aaa.id
	left join (select asset_id,depreciated_value,depreciation_acum,period_id from account_asset_depreciation_line  inner join account_asset_asset on account_asset_asset.id = account_asset_depreciation_line.asset_id where period_id='08/""" + self.ejercicio_id.name + """' and periodo_num(period_id)<= periodo_num('""" +self.period_id.code+ """') and ( CASE WHEN account_asset_asset.f_baja is not Null THEN account_asset_asset.f_baja > '01/08/""" + self.ejercicio_id.name + """' else True END)) asdl8 on asdl8.asset_id = aaa.id
	left join (select asset_id,depreciated_value,depreciation_acum,period_id from account_asset_depreciation_line  inner join account_asset_asset on account_asset_asset.id = account_asset_depreciation_line.asset_id where period_id='09/""" + self.ejercicio_id.name + """' and periodo_num(period_id)<= periodo_num('""" +self.period_id.code+ """') and ( CASE WHEN account_asset_asset.f_baja is not Null THEN account_asset_asset.f_baja > '01/09/""" + self.ejercicio_id.name + """' else True END)) asdl9 on asdl9.asset_id = aaa.id
	left join (select asset_id,depreciated_value,depreciation_acum,period_id from account_asset_depreciation_line  inner join account_asset_asset on account_asset_asset.id = account_asset_depreciation_line.asset_id where period_id='10/""" + self.ejercicio_id.name + """' and periodo_num(period_id)<= periodo_num('""" +self.period_id.code+ """') and ( CASE WHEN account_asset_asset.f_baja is not Null THEN account_asset_asset.f_baja > '01/10/""" + self.ejercicio_id.name + """' else True END)) asdl10 on asdl10.asset_id = aaa.id
	left join (select asset_id,depreciated_value,depreciation_acum,period_id from account_asset_depreciation_line  inner join account_asset_asset on account_asset_asset.id = account_asset_depreciation_line.asset_id where period_id='11/""" + self.ejercicio_id.name + """' and periodo_num(period_id)<= periodo_num('""" +self.period_id.code+ """') and ( CASE WHEN account_asset_asset.f_baja is not Null THEN account_asset_asset.f_baja > '01/11/""" + self.ejercicio_id.name + """' else True END)) asdl11 on asdl11.asset_id = aaa.id
	left join (select asset_id,depreciated_value,depreciation_acum,period_id from account_asset_depreciation_line  inner join account_asset_asset on account_asset_asset.id = account_asset_depreciation_line.asset_id where period_id='12/""" + self.ejercicio_id.name + """' and periodo_num(period_id)<= periodo_num('""" +self.period_id.code+ """') and ( CASE WHEN account_asset_asset.f_baja is not Null THEN account_asset_asset.f_baja > '01/12/""" + self.ejercicio_id.name + """' else True END)) asdl12 on asdl12.asset_id = aaa.id
	left join account_account aa1 on aa1.id = aac.account_asset_id
	left join account_account aa2 on aa2.id = aac.account_depreciation_id
	left join account_account aa3 on aa3.id = aac.account_expense_depreciation_id
	left join account_account aa4 on aa4.id = aac.account_retire
	left join account_analytic_account aya on aya.id = aac.account_analytic_id
	left join account_analytic_plan_instance aypl on aypl.id = aac.account_analytics_id  
	left join account_invoice ai on ai.id = aaa.invoice_id
	order by aaa.name
			""")
			for line in self.env.cr.fetchall():
				worksheet.write(x,0,line[0] if line[0] else '' ,bord )
				worksheet.write(x,1,line[1] if line[1]  else '',bord )
				worksheet.write(x,2,line[2] if line[2]  else '',bord)
				worksheet.write(x,3,line[3] if line[3]  else '',bord)
				worksheet.write(x,4,line[4] if line[4]  else '',bord)
				worksheet.write(x,5,line[5] if line[5]  else '',bord)
				worksheet.write(x,6,line[6] ,numberdos)
				worksheet.write(x,7,line[7] ,numberdos)
				worksheet.write(x,8,line[8] ,numberdos)
				worksheet.write(x,9,line[9] ,numberdos)
				worksheet.write(x,10,line[10] ,numberdos)
				worksheet.write(x,11,line[11] ,numberdos)
				worksheet.write(x,12,line[12] ,numberdos)
				worksheet.write(x,13,line[13] ,numberdos)
				worksheet.write(x,14,line[14] ,numberdos)
				worksheet.write(x,15,line[15] ,numberdos)
				worksheet.write(x,16,line[16] ,numberdos)
				worksheet.write(x,17,line[17] ,numberdos)
				worksheet.write(x,18,line[18] ,numberdos)
				worksheet.write(x,19,line[19] ,numberdos)
				worksheet.write(x,20,line[20] ,numberdos)
				worksheet.write(x,21,line[21] ,numberdos)
				worksheet.write(x,22,line[22] if line[22]  else '',bord)
				worksheet.write(x,23,line[23] if line[23]  else '',bord)
				worksheet.write(x,24,line[24] if line[24]  else '',bord)
				worksheet.write(x,25,line[25] if line[25]  else '',bord)
				x = x +1

			tam_col = [25,25,14,14,25,25,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14]


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

			workbook.close()
			
			f = open(direccion + 'analisis_activos.xlsx', 'rb')
			
			
			sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
			vals = {
				'output_name': 'AnalisisActivoFijo.xlsx',
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

			#import os
			#os.system('c:\\eSpeak2\\command_line\\espeak.exe -ves-f1 -s 170 -p 100 "Se Realizo La exportación exitosamente Y A EDWARD NO LE GUSTA XDXDXDXDDDDDDDDDDDD" ')

			return {
			    "type": "ir.actions.act_window",
			    "res_model": "export.file.save",
			    "views": [[False, "form"]],
			    "res_id": sfs_id.id,
			    "target": "new",
			}
		