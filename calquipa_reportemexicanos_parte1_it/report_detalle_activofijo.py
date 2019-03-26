# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import magenta, red , black, white, blue, gray, Color, HexColor, PCMYKColor, PCMYKColorSep
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, A4, legal
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table
from reportlab.lib.units import  cm,mm
from reportlab.lib.utils import simpleSplit
from cgi import escape

import decimal


class resumen_rubro_peruano(models.Model):
	_name = 'resumen.rubro.peruano'

	#grupo = fields.Selection([('1','CAPITAL'),('2','CAPITAL ADICIONAL'),('3','PARTI. PATR. TRAB.'),('4','RESERVA LEGAL'),('5','OTRAS RESERVAS'),('6','RESULTADOS ACUMULADOS')],'Tipo Patrimonio Neto')
	grupo = fields.Char('Grupo')
	monto= fields.Float('Soles',digits=(12,2))
	monto_usd= fields.Float('USD',digits=(12,2))
	tc = fields.Float('Tipo de Cambio',digits=(12,2))
	activofijo_id = fields.Many2one('reporte.activofijo','Padre')


class resumen_activo_line(models.Model):
	_name = 'resumen.activo.line'

	#grupo = fields.Selection([('1','CAPITAL'),('2','CAPITAL ADICIONAL'),('3','PARTI. PATR. TRAB.'),('4','RESERVA LEGAL'),('5','OTRAS RESERVAS'),('6','RESULTADOS ACUMULADOS')],'Tipo Patrimonio Neto')
	grupo = fields.Char('Grupo')
	valor_soles= fields.Float('Soles',digits=(12,2))
	monto_usd= fields.Float('USD',digits=(12,2))
	pesos= fields.Float('Peso Mex.',digits=(12,2))
	activofijo_id = fields.Many2one('reporte.activofijo','Padre')

class resumen_depre_line(models.Model):
	_name = 'resumen.depre.line'

	grupo = fields.Char('Grupo')
	valor_soles= fields.Float('Soles',digits=(12,2))
	monto_usd= fields.Float('USD',digits=(12,2))
	pesos= fields.Float('Peso Mex.',digits=(12,2))
	activofijo_id = fields.Many2one('reporte.activofijo','Padre')	

class reporte_rubro_peruano(models.Model):
	_name = 'reporte.rubro.peruano'

	#grupo = fields.Selection([('1','CAPITAL'),('2','CAPITAL ADICIONAL'),('3','PARTI. PATR. TRAB.'),('4','RESERVA LEGAL'),('5','OTRAS RESERVAS'),('6','RESULTADOS ACUMULADOS')],'Tipo Patrimonio Neto')
	grupo = fields.Char('Grupo')
	monto= fields.Float('Soles',digits=(12,2))
	monto_usd= fields.Float('USD',digits=(12,2))
	tc = fields.Float('Tipo de Cambio',digits=(12,2))
	activofijo_id = fields.Many2one('reporte.activofijo','Padre')


class reporte_activo_line(models.Model):
	_name = 'reporte.activo.line'

	codigo_activo = fields.Char('Código Activo Fijo')
	porc_depre = fields.Float('Porc. Depreciacion')
	md_dolar = fields.Float('M.D. Dolar')
	codigo = fields.Char('Código')
	fecha_adq = fields.Date('Fecha ADQ')
	grupo = fields.Char('Grupo')
	descripcion = fields.Char('Descripción')
	valor_soles = fields.Float('Valor en Soles', digits=(12,2))
	t_c = fields.Float('T.C.',digits=(12,3))
	monto_usd = fields.Float('Monto USD', digits=(12,2))
	t_c_mex = fields.Float('T.C. MEX',digits=(12,3))
	pesos = fields.Float('Pesos Mex.',digits=(12,2))
	activofijo_id = fields.Many2one('reporte.activofijo','Padre')



	patrimony_type = fields.Char('Tipo Patrimonio Neto',compute="get_patrimony_type")

	@api.one
	def get_patrimony_type(self):
		cuenta = self.env['account.account'].search([('code','=',self.grupo)])
		if len(cuenta)>0:
			self.patrimony_type = cuenta[0].balance_type_mex_id.orden
		else:
			self.patrimony_type = False

class reporte_depre_line(models.Model):
	_name = 'reporte.depre.line'

	codigo = fields.Char('Código')
	fecha_adq = fields.Date('Fecha ADQ')
	grupo = fields.Char('Grupo')
	descripcion = fields.Char('Descripción')
	valor_soles = fields.Float('Depreciación ACM Soles', digits=(12,2))
	t_c = fields.Float('T.C.',digits=(12,3))
	monto_usd = fields.Float('Depreciación ACM USD', digits=(12,2))
	t_c_mex = fields.Float('T.C. MEX',digits=(12,3))
	pesos = fields.Float('Depreciación Pesos Mex.',digits=(12,2))
	activofijo_id = fields.Many2one('reporte.activofijo','Padre')

	patrimony_type = fields.Char('Tipo Patrimonio Neto',compute="get_patrimony_type")

	@api.one
	def get_patrimony_type(self):
		cuenta = self.env['account.account'].search([('code','=',self.grupo)])
		if len(cuenta)>0:
			self.patrimony_type = cuenta[0].balance_type_mex_id.orden
		else:
			self.patrimony_type = False


class reporte_activofijo(models.Model):
	_name = 'reporte.activofijo'

	fiscal_id = fields.Many2one('account.fiscalyear','Año Fiscal',required=True)
	name = fields.Many2one('account.period','Periodo',required=True)
	activo_ids = fields.One2many('reporte.activo.line','activofijo_id','Activo Fijo')
	peruano_ids = fields.One2many('reporte.rubro.peruano','activofijo_id','Rubro Peruano')
	depre_ids = fields.One2many('reporte.depre.line','activofijo_id','Depreciación Acumulada')
	r_activo_ids = fields.One2many('resumen.activo.line','activofijo_id','Resumen Activo Fijo')
	r_peruano_ids = fields.One2many('resumen.rubro.peruano','activofijo_id','Resumen Rubro Peruano')
	r_depre_ids = fields.One2many('resumen.depre.line','activofijo_id','Resumen Depreciación Acumulada')
	csv_import_af = fields.Binary('CSV Importación Activo Fijo')
	csv_import_d = fields.Binary('CSV Importación Depreciación')

	@api.one
	def import_csv(self):
		for i in self.activo_ids:
			i.unlink()
		for j in self.depre_ids:
			j.unlink()

		if self.csv_import_af:
			texto = base64.decodestring(self.csv_import_af)
			texto = texto.split('\n')

			for i in texto:
				obj = i.split('|')
				data = {
				'codigo_activo': obj[0],
				'codigo': obj[1],
				'fecha_adq': obj[2],
				'grupo': self.env['account.account'].search([('balance_type_mex_id.orden','=',obj[3])])[-1].code,
				'descripcion': obj[4],
				'valor_soles': float(obj[5]),
				't_c': float(obj[6]),
				'monto_usd': float(obj[7]),
				't_c_mex': float(obj[8]),
				'pesos': float(obj[9]),
				'activofijo_id': self.id,
				}
				v1 = 0
				v2 = 0

				if obj[0] and obj[0] != '':
					self.env.cr.execute("""
						select percent_depreciacion from 
						account_asset_asset aaa
						inner join account_asset_category aac on aaa.category_id = aac.id
						inner join account_asset_depreciation_line aadl on aadl.asset_id = aaa.id
						where aaa.codigo = '""" +obj[1]+ """'
						and aadl.period_id = '""" +self.name.code+ """'
						--juan antonio
					 """)
					aopst = self.env.cr.fetchall()

					if len(aopst)>0:
						for isa in aopst:
							v1 = isa[0]
							v2 = isa[0]*float(obj[7])

				data['porc_depre'] = v1
				data['md_dolar'] = v2
				self.env['reporte.activo.line'].create(data)

		if self.csv_import_d:
			texto = base64.decodestring(self.csv_import_d)
			texto = texto.split('\n')

			for i in texto:
				obj = i.split('|')
				data = {
				'codigo': obj[0],
				'fecha_adq': obj[1],
				'grupo': self.env['account.account'].search([('balance_type_mex_id.orden','=',obj[2])])[-1].code,
				'descripcion': obj[3],
				'valor_soles': float(obj[4]),
				't_c': float(obj[5]),
				'monto_usd': float(obj[6]),
				't_c_mex': float(obj[7]),
				'pesos': float(obj[8]),
				'activofijo_id': self.id,
				}
				self.env['reporte.depre.line'].create(data)

	@api.one
	def resumen_generate(self):
		for i in self.r_depre_ids:
			i.unlink()
		for j in self.r_activo_ids:
			j.unlink()
		for j in self.r_peruano_ids:
			j.unlink()

		tmp = None
		total_soles = 0
		total_usd = 0
		total_peso = 0



		self.env.cr.execute(""" 
				
				select 
				rm1.orden,
				sum(aaa.purchase_value),
				sum(aaa.bruto_doalres)

				 from 
				account_asset_asset aaa
				left join account_asset_category aac on aac.id = aaa.category_id
				left join account_account aa1 on aa1.id = aac.account_asset_id
				left join account_account aa2 on aa2.id = aac.account_depreciation_id
				left join rm_balance_config_mexicano_line rm1 on rm1.id = aa1.balance_type_mex_id
				left join rm_balance_config_mexicano_line rm2 on rm2.id = aa2.balance_type_mex_id
				where (aaa.f_baja is null or aaa.f_baja > '""" +str(self.name.date_stop)[:10]+ """')
				group by  rm1.orden

			""")

		lineas_inf = self.env.cr.fetchall()

		tpmo = self.env['tipo.cambio.mexicano'].search([('periodo_id','=',self.name.id)])
		tpm = 1
		if len(tpmo)>0:
			tpm = tpmo[0].t_cambio_mexicano

		for i in lineas_inf:
			data = {
			'grupo': i[0],
			'valor_soles': i[1],
			'monto_usd':i[2],
			'pesos': i[2]*tpm,
			'activofijo_id': self.id,
			}
			self.env['resumen.activo.line'].create(data)




		############# adios
		



		self.env.cr.execute(""" 
				
				select 
				rm2.orden,
				sum(
				CASE WHEN aaa.f_baja is null THEN aaa.deprec_mensual *  coalesce(aadl.mes ,0) ELSE
				    CASE WHEN aaa.f_baja <= '""" +str(self.name.date_stop)[:10]+ """'
				    THEN 0 else aaa.deprec_mensual *  coalesce(aadl.mes ,0) END
				END),

				sum(
				
				CASE WHEN aaa.f_baja is null THEN aaa.val_deprec_mensual_d *  coalesce(aadl.mes ,0) ELSE
				    CASE WHEN aaa.f_baja <= '""" +str(self.name.date_stop)[:10]+ """'
				    THEN 0 else aaa.val_deprec_mensual_d *  coalesce(aadl.mes ,0) END 
				    
				END)

				 from 
				account_asset_asset aaa
				left join account_asset_category aac on aac.id = aaa.category_id
				left join account_account aa1 on aa1.id = aac.account_asset_id
				left join account_account aa2 on aa2.id = aac.account_depreciation_id
				left join account_asset_depreciation_line aadl on aadl.asset_id = aaa.id and aadl.period_id = '"""+ str(self.name.code) +"""'
				left join rm_balance_config_mexicano_line rm1 on rm1.id = aa1.balance_type_mex_id
				left join rm_balance_config_mexicano_line rm2 on rm2.id = aa2.balance_type_mex_id
				where (aaa.f_baja is null or aaa.f_baja > '""" +str(self.name.date_stop)[:10]+ """')
				group by  rm2.orden

			""")

		lineas_inf = self.env.cr.fetchall()

		tpmo = self.env['tipo.cambio.mexicano'].search([('periodo_id','=',self.name.id)])
		tpm = 1
		if len(tpmo)>0:
			tpm = tpmo[0].t_cambio_mexicano

		for i in lineas_inf:
			data = {
			'grupo': i[0],
			'valor_soles': i[1],
			'monto_usd':i[2],
			'pesos': i[2]*tpm,
			'activofijo_id': self.id,
			}
			self.env['resumen.depre.line'].create(data)


		#### hola hola



		self.env.cr.execute(""" 
				
				select 
				aat.code,
				sum(aaa.purchase_value - (coalesce(rm3.mes,0) * (CASE WHEN aaa.f_baja is null THEN aaa.deprec_mensual ELSE
				    CASE WHEN aaa.f_baja <= '""" +str(self.name.date_stop)[:10]+ """'
				    THEN 0 else aaa.deprec_mensual END
				END) )) ,
				sum(aaa.bruto_doalres- ( coalesce(rm3.mes,0) * (CASE WHEN aaa.f_baja is null THEN aaa.val_deprec_mensual_d ELSE
				    CASE WHEN aaa.f_baja <= '""" +str(self.name.date_stop)[:10]+ """'
				    THEN 0 else aaa.val_deprec_mensual_d END
				END)))

				 from 
				account_asset_asset aaa
				left join account_asset_category aac on aac.id = aaa.category_id
				left join account_account aa1 on aa1.id = aac.account_asset_id
				left join account_account_type aat on aat.id = aa1.user_type
				left join account_account aa2 on aa2.id = aac.account_depreciation_id
				left join rm_balance_config_mexicano_line rm1 on rm1.id = aa1.balance_type_mex_id
				left join rm_balance_config_mexicano_line rm2 on rm2.id = aa2.balance_type_mex_id
				left join (
				select * from account_asset_depreciation_line where period_id   = '"""+ self.name.code +"""' )
				rm3 on rm3.asset_id=aaa.id
				where (aaa.f_baja is null or aaa.f_baja > '""" +str(self.name.date_stop)[:10]+ """')
				group by  aat.code

			""")

		lineas_inf = self.env.cr.fetchall()


		for i in lineas_inf:
			data = {
			'grupo': i[0],
			'monto': i[1],
			'monto_usd':i[2],
			'tc': i[1]/i[2] if i[2] !=0 else 0,
			'activofijo_id': self.id,
			}
			self.env['resumen.rubro.peruano'].create(data)


			
