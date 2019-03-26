# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv
from openerp import netsvc

class tabla_2_reporte_control_factura(models.Model):
	_name = 'tabla.2.reporte.control.factura'

	move_id = fields.Many2one('account.move','Factura relacionada')

	fecha_recepcion_oficina = fields.Date(string='Fecha Recepcion Oficina')
	fecha_envio_lima  = fields.Date(string='Fecha Envio A Lima')
	fecha_recepcion_dante_anaya = fields.Date(string='Fecha Recepcion Dante Anaya')
	fecha_recepcion_cliente = fields.Date(string='Fecha Recepcion Cliente')
	dias_desde_f_emision_hasta_f_cliente = fields.Date(string='Dias desde F. Emision Hasta F. Cliente')
	dias_desde_recepcion_d_anaya_hasta_f_cliente = fields.Date(string='Dias Desde Recepcion D. Anaya Hasta F. Cliente')
	fecha_30_dias_recepcion_cliente  = fields.Date(string='Fecha a 30 Días De Recepción Por El Cliente')


class control_facturas_ventas_reporte_linea_it(models.Model):
	_name = 'control.facturas.ventas.reporte.linea.it'
	
	fecha_emision = fields.Date(string='F. Emision')
	fecha_ven = fields.Date(string='F. Vencimiento')
	plazo= fields.Char('Plazo')

	nro_comprobante = fields.Char(string='Número',size=200)
	empresa = fields.Char(string='Empresa',size=200)

	tipo = fields.Char('TD')
	cuenta = fields.Char(string='Cuenta',size=200)
	moneda = fields.Char('Moneda')
	saldo_me = fields.Float('Saldo_ME', digits=(12,2))
	por_vencer = fields.Float('Vencidas', digits=(12,2))
	hasta_15 = fields.Float('De 1 a 15', digits=(12,2))
	hasta_30 = fields.Float('De 16 a 30', digits=(12,2))
	hasta_60 = fields.Float('De 46 a 60', digits=(12,2))
	hasta_90 = fields.Float('De 61 a 90', digits=(12,2))
	hasta_180 = fields.Float('De 91 a 180', digits=(12,2))
	mas_de_180 = fields.Float('Mas de 180', digits=(12,2))

	fecha_recepcion_oficina = fields.Date(string='Fecha Recepcion Oficina')
	fecha_envio_lima  = fields.Date(string='Fecha Envio A Lima')
	fecha_recepcion_dante_anaya = fields.Date(string='Fecha Recepcion Dante Anaya')
	fecha_recepcion_cliente = fields.Date(string='Fecha Recepcion Cliente')
	dias_desde_f_emision_hasta_f_cliente = fields.Date(string='Dias desde F. Emision Hasta F. Cliente')
	dias_desde_recepcion_d_anaya_hasta_f_cliente = fields.Date(string='Dias Desde Recepcion D. Anaya Hasta F. Cliente')
	fecha_30_dias_recepcion_cliente  = fields.Date(string='Fecha a 30 Días De Recepción Por El Cliente')

	move_id = fields.Many2one('account.move','Factura relacionada')
	
	padre = fields.Many2one('control.facturas.ventas.reporte.it','Padre')

	@api.model
	def create(self,vals):
		t = super(control_facturas_ventas_reporte_linea_it,self).create(vals)
		datos = self.env['tabla.2.reporte.control.factura'].search([('move_id','=',t.move_id.id)])
		if len(datos) == 0:
			self.env['tabla.2.reporte.control.factura'].create({'move_id':t.move_id.id})
		else:
			datos = datos[0]
			t.write({
				'fecha_recepcion_oficina':datos.fecha_recepcion_oficina,
				'fecha_envio_lima':datos.fecha_envio_lima,
				'fecha_recepcion_dante_anaya':datos.fecha_recepcion_dante_anaya,
				'fecha_recepcion_cliente':datos.fecha_recepcion_cliente,
				'dias_desde_f_emision_hasta_f_cliente':datos.dias_desde_f_emision_hasta_f_cliente,
				'dias_desde_recepcion_d_anaya_hasta_f_cliente':datos.dias_desde_recepcion_d_anaya_hasta_f_cliente,
				'fecha_30_dias_recepcion_cliente':datos.fecha_30_dias_recepcion_cliente,
				'check_v':1,
				})
		return t


	@api.one
	def write(self,vals):
		t = super(control_facturas_ventas_reporte_linea_it,self).write(vals)
		self.refresh()
		if True:
			datos = self.env['tabla.2.reporte.control.factura'].search([('move_id','=',self.move_id.id)])
			datos = datos[0]
			datos.write({
					'fecha_recepcion_oficina':self.fecha_recepcion_oficina,
					'fecha_envio_lima':self.fecha_envio_lima,
					'fecha_recepcion_dante_anaya':self.fecha_recepcion_dante_anaya,
					'fecha_recepcion_cliente':self.fecha_recepcion_cliente,
					'dias_desde_f_emision_hasta_f_cliente':self.dias_desde_f_emision_hasta_f_cliente,
					'dias_desde_recepcion_d_anaya_hasta_f_cliente':self.dias_desde_recepcion_d_anaya_hasta_f_cliente,
					'fecha_30_dias_recepcion_cliente':self.fecha_30_dias_recepcion_cliente,
					})


		if 'check_v' not in vals:
			actualizacion = self.env['control.facturas.ventas.reporte.linea.it'].search([('move_id','=',self.move_id.id),('id','!=',self.id)])
			for act in actualizacion:
				act.write({
						'fecha_recepcion_oficina':self.fecha_recepcion_oficina,
						'fecha_envio_lima':self.fecha_envio_lima,
						'fecha_recepcion_dante_anaya':self.fecha_recepcion_dante_anaya,
						'fecha_recepcion_cliente':self.fecha_recepcion_cliente,
						'dias_desde_f_emision_hasta_f_cliente':self.dias_desde_f_emision_hasta_f_cliente,
						'dias_desde_recepcion_d_anaya_hasta_f_cliente':self.dias_desde_recepcion_d_anaya_hasta_f_cliente,
						'fecha_30_dias_recepcion_cliente':self.fecha_30_dias_recepcion_cliente,
						'check_v': 1,
						})
		return t
		


class control_facturas_ventas_reporte_it(models.Model):
	_name = 'control.facturas.ventas.reporte.it'
	
	date = fields.Date('Fecha del Reporte')
	date_ini = fields.Date('Fecha Inicial')
	date_fin = fields.Date('Fecha Final')
	lineas = fields.One2many('control.facturas.ventas.reporte.linea.it','padre','Detalle')
	factura = fields.Many2one('account.invoice','Factura')

	_rec_name = 'date'

	@api.one
	def unlink(self):
		for i in self.lineas:
			i.unlink()

	@api.multi
	def excel(self):
		if True:
			import io
			from xlsxwriter.workbook import Workbook
			output = io.BytesIO()
			########### PRIMERA HOJA DE LA DATA EN TABLA
			#workbook = Workbook(output, {'in_memory': True})
			direccion = self.env['main.parameter'].search([])[0].dir_create_file
			workbook = Workbook( direccion + 'tempo_vencimientopayable.xlsx')
			worksheet = workbook.add_worksheet("Control de Factura")
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


			worksheet.merge_range(0,0,0,15,u"Análisis de Vencimiento Cuentas por Pagar",title)

			worksheet.write(1,0, "Fecha:", bold)
			
			worksheet.write(1,1, self.date, normal)
							
			#worksheet.write(1,1, total.date.strftime('%Y-%m-%d %H:%M'),bord)
			
			worksheet.write(4,0, "F. Emi.",boldbord)

			
			worksheet.write(4,1, "Fecha Recepcion Oficina",boldbord)
			worksheet.write(4,2, "Fecha Envio A Lima",boldbord)
			worksheet.write(4,3, "Fecha Recepcion Dante Anaya",boldbord)
			worksheet.write(4,4, "Fecha Recepcion Cliente",boldbord)
			worksheet.write(4,5, "Dias desde F. Emision Hasta F. Cliente",boldbord)
			worksheet.write(4,6, "Dias Desde Recepcion D. Anaya Hasta F. Cliente",boldbord)


			worksheet.write(4,7, "F. Ven.",boldbord)

			worksheet.write(4,8, "Fecha a 30 Días De Recepción Por El Cliente",boldbord)

			worksheet.write(4,9, "Plazo",boldbord)
			worksheet.write(4,10, "Empresa",boldbord)
			worksheet.write(4,11, "TD",boldbord)				
			worksheet.write(4,12, u"Número",boldbord)

			worksheet.write(4,13, u"Moneda",boldbord)
			worksheet.write(4,14, u"Saldo Me",boldbord)
			worksheet.write(4,15, "Cuenta",boldbord)

			worksheet.write(4,16, "Por Vencer",boldbord)
			worksheet.write(4,17, u"Hasta 15",boldbord)
			worksheet.write(4,18, u"Hasta 30",boldbord)
			worksheet.write(4,19, u"Hasta 60",boldbord)
			worksheet.write(4,20, u"Hasta 90",boldbord)
			worksheet.write(4,21, u"Hasta 180",boldbord)
			worksheet.write(4,22, u"Mas de 180",boldbord)


			for line in self.lineas:
				worksheet.write(x,0,line.fecha_emision if line.fecha_emision else '' ,bord )


				worksheet.write(x,1,line.fecha_recepcion_oficina if line.fecha_recepcion_oficina else '' ,bord )
				worksheet.write(x,2,line.fecha_envio_lima if line.fecha_envio_lima else '' ,bord )
				worksheet.write(x,3,line.fecha_recepcion_dante_anaya if line.fecha_recepcion_dante_anaya else '' ,bord )
				worksheet.write(x,4,line.fecha_recepcion_cliente if line.fecha_recepcion_cliente else '' ,bord )
				worksheet.write(x,5,line.dias_desde_f_emision_hasta_f_cliente if line.dias_desde_f_emision_hasta_f_cliente else '' ,bord )
				worksheet.write(x,6,line.dias_desde_recepcion_d_anaya_hasta_f_cliente if line.dias_desde_recepcion_d_anaya_hasta_f_cliente else '' ,bord )


				worksheet.write(x,7,line.fecha_ven if line.fecha_ven  else '',bord )

				worksheet.write(x,8,line.fecha_30_dias_recepcion_cliente if line.fecha_30_dias_recepcion_cliente  else '',bord )
				worksheet.write(x,9,line.plazo if line.plazo  else '',bord)
				worksheet.write(x,10,line.empresa if line.empresa  else '',bord)
				worksheet.write(x,11,line.tipo if line.tipo  else '',bord)
				worksheet.write(x,12,line.nro_comprobante if line.nro_comprobante else '',bord)
				worksheet.write(x,13,line.moneda if line.moneda else '',bord)
				worksheet.write(x,14,line.saldo_me if line.moneda else '',bord)
				worksheet.write(x,15,line.cuenta if line.cuenta else '',bord)
				worksheet.write(x,16,line.por_vencer ,numberdos)
				worksheet.write(x,17,line.hasta_15 ,numberdos)
				worksheet.write(x,18,line.hasta_30 ,numberdos)
				worksheet.write(x,19,line.hasta_60 ,numberdos)
				worksheet.write(x,20,line.hasta_90 ,numberdos)
				worksheet.write(x,21,line.hasta_180 ,numberdos)
				worksheet.write(x,22,line.mas_de_180 ,numberdos)

				x = x +1


			tam_col = [16,7,10,13,16,16,16,20,14]
			worksheet.set_row(0, 30)

			worksheet.set_column('A:A', tam_col[0])
			worksheet.set_column('B:B', tam_col[1])
			worksheet.set_column('C:C', tam_col[2])
			worksheet.set_column('D:D', tam_col[3])
			worksheet.set_column('E:E', tam_col[4])
			worksheet.set_column('F:F', tam_col[5])
			worksheet.set_column('G:G', tam_col[6])
			worksheet.set_column('H:H', tam_col[7])
			worksheet.set_column('I:Z', tam_col[8])
			workbook.close()
			
			f = open(direccion + 'tempo_vencimientopayable.xlsx', 'rb')
			
			
			vals = {
				'output_name': 'AnalisisVencimientoPayable.xlsx',
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




	@api.one
	def actualizar(self):
		for i in self.lineas:
			i.unlink()

		condicion = ""
		if self.factura.id:
			condicion = 'and ft.id = ' + str(self.factura.id)
		self.env.cr.execute(""" 
		select 
id, 
fecha_emision, 
fecha_ven,
plazo,
empresa,
tipo,
nro_comprobante ,
case when divisa is not null then divisa else 'PEN' end as moneda,
saldo_me,
code as cuenta,

CASE WHEN atraso <= 0 OR atraso is null then saldo else 0 end  as por_vencer,
CASE WHEN atraso > 0  and atraso < 16  then saldo else 0 end  as hasta_15,
CASE WHEN atraso > 15  and atraso < 31  then saldo else 0 end  as hasta_30,
CASE WHEN atraso > 30  and atraso < 61  then saldo else 0 end  as hasta_60,
CASE WHEN atraso > 60  and atraso < 91  then saldo else 0 end  as hasta_90,
CASE WHEN atraso > 90  and atraso < 181  then saldo else 0 end  as hasta_180,
CASE WHEN atraso > 180  then saldo else 0 end  as mas_de_180,
move_id



from
(
select 
aml.id as id,
ap.code as periodo,
lib.name as libro,
am.name as voucher,
am.date as fecha_emision,
aml.date_maturity as fecha_ven,
jj.value as plazo,
rp.name as empresa,
aa.code,
itd.code as tipo,
aml.nro_comprobante as nro_comprobante,
abs(T.saldo) as saldo,
rc.name as divisa,
abs(saldo_me) as saldo_me,
'"""+ str(self.date) +"""'::date - aml.date_maturity as atraso,
am.state as estado,
am.id as move_id


from (
select concat(account_move_line.partner_id,account_id,type_document_id,nro_comprobante) as identifica,min(account_move_line.id),sum(debit)as debe,sum(credit) as haber, sum(debit)-sum(credit) as saldo, sum(amount_currency) as saldo_me from account_move_line
inner join account_move ami on ami.id = account_move_line.move_id
inner join account_period api on api.id = ami.period_id
left join account_account on account_account.id=account_move_line.account_id
where  left(account_account.code ,2) = '12' and  ami.period_id in ( select id from account_period where periodo_num(code)>=201700 )

group by identifica
having sum(debit)-sum(credit) != 0 
) as T
inner join account_move_line aml on aml.id = T.min
inner join account_move am on am.id = aml.move_id
inner join account_period ap on ap.id = am.period_id
left join res_partner rp on rp.id = aml.partner_id
left join it_type_document itd on itd.id = aml.type_document_id
left join res_currency rc on rc.id = aml.currency_id
left join account_account aa on aa.id = aml.account_id
left join account_journal lib on lib.id=am.journal_id
left join account_invoice ft on ft.move_id=am.id
left join account_payment_term hh on hh.id=ft.payment_term
left join ir_translation jj on jj.res_id=hh.id and jj.name='account.payment.term,name'

where am.state='posted'  and lib.type in ('sale','sale_refund') and left(aa.code ,2) = '12'
""" + condicion + """
and am.date >= '""" +str(self.date_ini)+ """' and am.date <= '""" +str(self.date_fin)+ """'
order by empresa, code, nro_comprobante
) T

					
					
					""")


		for i in self.env.cr.dictfetchall():
			data = {
			'fecha_emision': i['fecha_emision'],
			'fecha_ven': i['fecha_ven'],
			'plazo': i['plazo'],
			'nro_comprobante': i['nro_comprobante'],
			'empresa': i['empresa'],
			'tipo': i['tipo'],
			'cuenta': i['cuenta'],
			'moneda': i['moneda'],
			'saldo_me': i['saldo_me'],
			'por_vencer': i['por_vencer'],
			'hasta_15': i['hasta_15'],
			'hasta_30': i['hasta_30'],
			'hasta_60': i['hasta_60'],
			'hasta_90': i['hasta_90'],
			'hasta_180': i['hasta_180'],
			'mas_de_180': i['mas_de_180'],
			'move_id': i['move_id'],
			'padre':self.id,
			}
			self.env['control.facturas.ventas.reporte.linea.it'].create(data)

