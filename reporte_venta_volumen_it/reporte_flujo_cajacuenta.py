# -*- coding: utf-8 -*-
from openerp import models, fields, api
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
from cgi import escape
import base64

class product_product(models.Model):
	_inherit = 'product.product'
	is_annulation= fields.Boolean(u'Usado para Anulación')

class reporte_venta_volumen_wizard(osv.TransientModel):
	_name='reporte.venta.volumen.wizard'

	fiscalyear_id = fields.Many2one('account.fiscalyear','Año Fiscal',required=True)
	period_id = fields.Many2one('account.period','Periodo',required=True)

	@api.multi
	def do_rebuild(self):	

		import io
		from xlsxwriter.workbook import Workbook
		from xlsxwriter.utility import xl_rowcol_to_cell

		product_unidad = self.env['product.uom'].search([('name','=','TN')])[0]
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')

		output = io.BytesIO()
		########### PRIMERA HOJA DE LA DATA EN TABLA
		#workbook = Workbook(output, {'in_memory': True})

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		if not direccion:
			raise osv.except_osv('Alerta!', u"No fue configurado el directorio para los archivos en Configuracion.")

		workbook = Workbook(direccion +'Reporte_state_efective.xlsx')
		worksheet = workbook.add_worksheet(u"Venta por Volumenes")
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
		numberdos = workbook.add_format({'num_format':'#,##0.00'})
		bord = workbook.add_format()
		bord.set_border(style=1)



		boldbordtitle = workbook.add_format({'bold': True})
		boldbordtitle.set_align('center')
		boldbordtitle.set_align('vcenter')
		#boldbordtitle.set_text_wrap()
		numbertresbold = workbook.add_format({'num_format':'0.000','bold': True})
		numberdosbold = workbook.add_format({'num_format':'#,##0.00','bold': True})
		numbercuatrobold = workbook.add_format({'num_format':'#,##0.0000','bold': True})
		numberdosbold.set_border(style=1)
		numbercuatrobold.set_border(style=1)
		numbertresbold.set_border(style=1)	

		numberdoscon = workbook.add_format({'num_format':'#,##0.00'})
		numbercuatrocon = workbook.add_format({'num_format':'#,##0.0000'})

		boldtotal = workbook.add_format({'bold': True})
		boldtotal.set_align('right')
		boldtotal.set_align('vright')

		merge_format = workbook.add_format({
											'bold': 1,
											'border': 1,
											'align': 'center',
											'valign': 'vcenter',
											})	
		merge_format.set_bg_color('#DCE6F1')
		merge_format.set_text_wrap()
		merge_format.set_font_size(9)


		worksheet.write(1,2, self.env["res.company"].search([])[0].name.upper(), boldbordtitle)
		worksheet.write(2,2, u"Volúmenes y Precios (Corporativo)", boldbordtitle)
		worksheet.write(3,2, u"(Expresado en Nuevos Soles)", boldbordtitle)
	

		colum = {
			1: "Enero",
			2: "Febrero",
			3: "Marzo",
			4: "Abril",
			5: "Mayo",
			6: "Junio",
			7: "Julio",
			8: "Agosto",
			9: "Septiembre",
			10: "Octubre",
			11: "Noviembre",
			12: "Diciembre",
		}




		#### INICIO

		x=7



		self.env.cr.execute(""" 

select A1.product_name ,
coalesce(P1.cantidad,0) as cantidad1,
coalesce(P1.monto,0) as monto1,
coalesce(P1.ac,0) as ac1,

coalesce(P2.cantidad,0) as cantidad1,
coalesce(P2.monto,0) as monto1,
coalesce(P2.ac,0) as ac1,

coalesce(P3.cantidad,0) as cantidad1,
coalesce(P3.monto,0) as monto1,
coalesce(P3.ac,0) as ac1,

coalesce(P4.cantidad,0) as cantidad1,
coalesce(P4.monto,0) as monto1,
coalesce(P4.ac,0) as ac1,

coalesce(P5.cantidad,0) as cantidad1,
coalesce(P5.monto,0) as monto1,
coalesce(P5.ac,0) as ac1,

coalesce(P6.cantidad,0) as cantidad1,
coalesce(P6.monto,0) as monto1,
coalesce(P6.ac,0) as ac1,

coalesce(P7.cantidad,0) as cantidad1,
coalesce(P7.monto,0) as monto1,
coalesce(P7.ac,0) as ac1,

coalesce(P8.cantidad,0) as cantidad1,
coalesce(P8.monto,0) as monto1,
coalesce(P8.ac,0) as ac1,

coalesce(P9.cantidad,0) as cantidad1,
coalesce(P9.monto,0) as monto1,
coalesce(P9.ac,0) as ac1,

coalesce(P10.cantidad,0) as cantidad1,
coalesce(P10.monto,0) as monto1,
coalesce(P10.ac,0) as ac1,

coalesce(P11.cantidad,0) as cantidad1,
coalesce(P11.monto,0) as monto1,
coalesce(P11.ac,0) as ac1,

coalesce(P12.cantidad,0) as cantidad1,
coalesce(P12.monto,0) as monto1,
coalesce(P12.ac,0) as ac1,

coalesce(P13.cantidad,0) as cantidad1,
coalesce(P13.monto,0) as monto1,
coalesce(P13.ac,0) as ac1,

coalesce(P14.cantidad,0) as cantidad1,
coalesce(P14.monto,0) as monto1,
coalesce(P14.ac,0) as ac1


from (
select distinct product_id, pp.name_template as product_name from account_move_line aml
inner join account_move am on am.id = aml.move_id
inner join account_journal  aj on aj.id = am.journal_id
inner join account_period ap on ap.id = am.period_id
inner join product_product pp on pp.id = aml.product_id
inner join account_account aa on aa.id = aml.account_id
where aj.type in ('sale','sale_refund') and product_id is not null and am.state != 'draft' and ( pp.is_annulation = false or pp.is_annulation is null ) ) as A1

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0) *(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END)) as monto, abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and ap.code = '01/""" +self.fiscalyear_id.name+ """'
group by product_id
) P1 on P1.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and ap.code = '02/""" +self.fiscalyear_id.name+ """'
group by product_id
) P2 on P2.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and ap.code = '03/""" +self.fiscalyear_id.name+ """'
group by product_id
) P3 on P3.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and ap.code = '04/""" +self.fiscalyear_id.name+ """'
group by product_id
) P4 on P4.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and ap.code = '05/""" +self.fiscalyear_id.name+ """'
group by product_id
) P5 on P5.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and ap.code = '06/""" +self.fiscalyear_id.name+ """'
group by product_id
) P6 on P6.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and ap.code = '07/""" +self.fiscalyear_id.name+ """'
group by product_id
) P7 on P7.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and ap.code = '08/""" +self.fiscalyear_id.name+ """'
group by product_id
) P8 on P8.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and ap.code = '09/""" +self.fiscalyear_id.name+ """'
group by product_id
) P9 on P9.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and ap.code = '10/""" +self.fiscalyear_id.name+ """'
group by product_id
) P10 on P10.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and ap.code = '11/""" +self.fiscalyear_id.name+ """'
group by product_id
) P11 on P11.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and ap.code = '12/""" +self.fiscalyear_id.name+ """'
group by product_id
) P12 on P12.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' and periodo_num(ap.code)>= periodo_num('01/""" +self.fiscalyear_id.name+ """') and periodo_num(ap.code)<= periodo_num('""" +self.period_id.code+ """') 
group by product_id
) P13 on P13.product_id = A1.product_id

left join  ( select aml.product_id, sum( CASE WHEN aml.credit != 0 THEN (aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ else (-aml.quantity/pu.factor)*""" + str(product_unidad.factor)+ """ END) as cantidad,
sum(aml.credit -aml.debit)- sum( coalesce(dvi.monto_flete,0)*(CASE WHEN rc.name = 'USD' THEN rcr.type_sale else 1 END))  as monto,  abs(sum(  CASE WHEN rc.name = 'USD' THEN aml.amount_currency else (aml.credit - aml.debit) / (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END ))- sum( CASE WHEN rc.name = 'USD' THEN coalesce(dvi.monto_flete,0) else coalesce(dvi.monto_flete,0)/ (CASE WHEN rcr.type_sale != 0 THEN rcr.type_sale ELSE 1 END  ) END )   as ac
from account_move am
inner join account_journal aj on aj.id = am.journal_id
inner join account_move_line aml on aml.move_id = am.id
inner join account_period ap on ap.id = am.period_id
inner join account_account aa on aa.id = aml.account_id
left join account_invoice ai on ai.move_id = am.id
left join detalle_venta_invoice dvi on dvi.invoice_id = ai.id and dvi.producto = aml.product_id
left join res_currency rc on rc.id = aml.currency_id or rc.name = (CASE WHEN aml.currency_id is null then 'PEN' else 'USD' END)
left join res_currency rct on rct.name = 'USD'
left join res_currency_rate rcr on rcr.currency_id = rct.id and rcr.name = am.date
inner join product_product pp on pp.id = aml.product_id
inner join product_template pt on pt.id = pp.product_tmpl_id
inner join product_uom pu on pu.id = aml.product_uom_id

where aj.type in ('sale','sale_refund') and aml.product_id is not null
and am.state != 'draft' 
and periodo_num(ap.code)>= periodo_num('01/""" + str(int(self.fiscalyear_id.name)-1) + """') and periodo_num(ap.code)<= periodo_num('12/""" + str(int(self.fiscalyear_id.name)-1) + """') 
group by product_id
) P14 on P14.product_id = A1.product_id



  """)
		contenedor_total = []
		for i in self.env.cr.fetchall():
			tmp = []
			for j in range(0,len(i)):
				tmp.append(i[j])
			contenedor_total.append( tmp )

		for j in range( (int(self.period_id.code.split('/')[0])+1) ,13):
			for m in contenedor_total:
				m[1+ ((j-1)*3)] = 0
				m[1+ ((j-1)*3)+1] = 0
				m[1+ ((j-1)*3)+2] = 0


		pos_saldo_inicial = x
		worksheet.merge_range(x-1,1,x,1, u"Clasificación", boldbord)
		worksheet.merge_range(x-1,2,x-1,5, u"Ene-" + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,6,x-1,9, u"Feb-" + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,10,x-1,13, u"Mar-" + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,14,x-1,17, u"Abr-" + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,18,x-1,21, u"May-" + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,22,x-1,25, u"Jun-" + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,26,x-1,29, u"Jul-" + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,30,x-1,33, u"Ago-" + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,34,x-1,37, u"Sep-" + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,38,x-1,41, u"Oct-" + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,42,x-1,45, u"Nov-" + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,46,x-1,49, u"Dic-" + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,50,x-1,53, u"Acumulado " + self.fiscalyear_id.name, boldbord)
		worksheet.merge_range(x-1,54,x-1,57, u"Acumulado " + str(int(self.fiscalyear_id.name)-1) , boldbord)

		for i in range(0,14):
			worksheet.write(x,2+(i*4)+0,'Volumen',boldbord)
			worksheet.write(x,2+(i*4)+1,'Importe',boldbord)
			worksheet.write(x,2+(i*4)+2,'Importe USD',boldbord)
			worksheet.write(x,2+(i*4)+3,'Precio Prom.',boldbord) 

		x += 1

		pos_inicio_todo = x
		for i in contenedor_total:
			worksheet.write(x,1,i[0])

			for j in range(0,14):
				worksheet.write(x,2+(j*4)+0,i[(j*3)+1],numbercuatrocon)
				worksheet.write(x,2+(j*4)+1,i[(j*3)+2],numberdoscon)
				worksheet.write(x,2+(j*4)+2,i[(j*3)+3],numberdoscon)
				worksheet.write_formula(x,2+(j*4)+3,'=IFERROR(' + xl_rowcol_to_cell(x,2+(j*4)+1) +'/' +xl_rowcol_to_cell(x,2+(j*4)+0) + ',0)' ,numberdoscon) 

			x +=1


		worksheet.write(x,1, u"TOTAL", bold)

		for j in range(0,14):
			if pos_inicio_todo == x:
				worksheet.write_formula(x,2+(j*4)+0,0,numbercuatrobold)
				worksheet.write_formula(x,2+(j*4)+1,0,numberdosbold)
				worksheet.write_formula(x,2+(j*4)+2,0,numberdosbold)
				worksheet.write_formula(x,2+(j*4)+3,'=IFERROR(' + xl_rowcol_to_cell(x,2+(j*4)+1) +'/' +xl_rowcol_to_cell(x,2+(j*4)+0) + ',0)' ,numberdosbold) 

			else:	
				worksheet.write_formula(x,2+(j*4)+0,'=sum(' + xl_rowcol_to_cell(pos_inicio_todo,2+(j*4)+0) +':' +xl_rowcol_to_cell(x-1,2+(j*4)+0) + ')',numbercuatrobold)
				worksheet.write_formula(x,2+(j*4)+1,'=sum(' + xl_rowcol_to_cell(pos_inicio_todo,2+(j*4)+1) +':' +xl_rowcol_to_cell(x-1,2+(j*4)+1) + ')',numberdosbold)
				worksheet.write_formula(x,2+(j*4)+2,'=sum(' + xl_rowcol_to_cell(pos_inicio_todo,2+(j*4)+2) +':' +xl_rowcol_to_cell(x-1,2+(j*4)+2) + ')',numberdosbold)
				worksheet.write_formula(x,2+(j*4)+3,'=IFERROR(' + xl_rowcol_to_cell(x,2+(j*4)+1) +'/' +xl_rowcol_to_cell(x,2+(j*4)+0) + ',0)' ,numberdosbold) 



		worksheet.set_column('B:B',31)
		worksheet.set_column('C:C',15)
		worksheet.set_column('D:BZ',15)

		#### FIN

		workbook.close()
		
		f = open(direccion + 'Reporte_state_efective.xlsx', 'rb')
		
		vals = {
			'output_name': 'VentaVolumenes.xlsx',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		sfs_id = self.env['export.file.save'].create(vals)
		return {
			"type": "ir.actions.act_window",
			"res_model": "export.file.save",
			"views": [[False, "form"]],
			"res_id": sfs_id.id,
			"target": "new",
		}

