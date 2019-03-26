# -*- coding: utf-8 -*-
from openerp.osv import osv
import base64

from openerp import models, fields, api
from datetime import datetime, timedelta

class costos_produccion(models.Model):
	_inherit = 'costos.produccion'
	

	@api.multi
	def export_excel_dolares(self):

		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		########### PRIMERA HOJA DE LA DATA EN TABLA
		#workbook = Workbook(output, {'in_memory': True})
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		if not direccion:
			raise osv.except_osv('Alerta!', "No fue configurado el directorio para los archivos en Configuración.")
		
		workbook = Workbook( direccion + 'tempo_calquipa_reporte_costeo_dolares.xlsx')

		worksheet = workbook.add_worksheet("Reporte Costeo")
		bold = workbook.add_format({'bold': True})
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		numberseis = workbook.add_format({'num_format':'0.000000'})
		bord = workbook.add_format()
		bord.set_border(style=1)
		numberdos.set_border(style=1)
		numbertres.set_border(style=1)	
		numberseis.set_border(style=1)		
		
		x= 6				
		tam_col = [12,20,12,12,14,12,20,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.1
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		
		# 3,11 esposicion 4B en escel
		worksheet.write(3,1 , u"EJERCICIO FISCAL",bold)
		worksheet.write(3,2 , self.fiscal.name,bold)
		worksheet.write(3,6 , u"Fecha",bold)
		worksheet.write(3,7 , self.fecha,bold)

		worksheet.write(4,1 , u"Periodo",bold)
		worksheet.write(4,2 , self.periodo.code,bold)
		worksheet.write(4,6 , u"Tipo de Cambio Cierre",bold)
		tipo_cam = 1.000
		top_tc = self.env['tipo.cambio.mexicano'].search([('periodo_id','=',self.periodo.id)])
		if len(top_tc)>0:
			top_tc = top_tc[0]
			tipo_cam = top_tc.t_cambio_venta
			
		worksheet.write(4,7 , "%.3f"%tipo_cam,bold)

		worksheet.write(6,1 , u"EXTRACCION",bold)
		
		worksheet.write(7,2 , u"Toneladas", boldbord)
		worksheet.write(7,3 , u"Importe PEN", boldbord)
		worksheet.write(7,4 , u"Costo Promedio PEN",boldbord)
		worksheet.write(7,6 , u"importe USD",boldbord)
		worksheet.write(7,7 , u"Costo Promedio USD",boldbord)
		worksheet.write(8,1 , u"Inventario Inicial",boldbord)
		worksheet.write(8,2 , self.extra_ini_ton,numberdos)
		worksheet.write(8,3 , self.extra_ini_imp,numberdos)
		worksheet.write(8,4 , self.extra_ini_cp,numberseis)
		worksheet.write(8,6 , self.extra_ini_imp/tipo_cam,numberdos)
		worksheet.write(8,7 , self.extra_ini_cp/tipo_cam,numberseis)
		worksheet.write(9,1 , u"Produccion",boldbord)
		worksheet.write(9,2 , self.extra_pro_ton,numberdos)
		worksheet.write(9,3 , self.extra_pro_imp,numberdos)
		worksheet.write(9,4 , self.extra_pro_cp,numberseis)
		worksheet.write(9,6 , self.extra_pro_imp/tipo_cam,numberdos)
		worksheet.write(9,7 , self.extra_pro_cp/tipo_cam,numberseis)
		worksheet.write(10,1 , u"Disponible",boldbord)
		worksheet.write(10,2 , self.extra_dis_ton,numberdos)
		worksheet.write(10,3 , self.extra_dis_imp,numberdos)
		worksheet.write(10,4 , self.extra_dis_cp,numberseis)
		worksheet.write(10,6 , self.extra_dis_imp/tipo_cam,numberdos)
		worksheet.write(10,7 , self.extra_dis_cp/tipo_cam,numberseis)
		worksheet.write(11,1 , u"Traspaso a trituracion",boldbord)
		worksheet.write(11,2 , self.extra_tt_ton,numberdos)
		worksheet.write(11,3 , self.extra_tt_imp,numberdos)
		worksheet.write(11,4 , self.extra_tt_cp,numberseis)
		worksheet.write(11,6 , self.extra_tt_imp/tipo_cam,numberdos)
		worksheet.write(11,7 , self.extra_tt_cp/tipo_cam,numberseis)
		worksheet.write(12,1 , u"Inventario Final",boldbord)
		worksheet.write(12,2 , self.extra_final_ton,numberdos)
		worksheet.write(12,3 , self.extra_final_imp,numberdos)
		worksheet.write(12,4 , self.extra_final_cp,numberseis)
		worksheet.write(12,6 , self.extra_final_imp/tipo_cam,numberdos)
		worksheet.write(12,7 , self.extra_final_cp/tipo_cam,numberseis)


		worksheet.write(15,1 , u"Trituracion",bold)
		
		worksheet.write(16,2 , u"Toneladas",boldbord)
		worksheet.write(16,3 , u"Importe PEN",boldbord)
		worksheet.write(16,4 , u"Costo Promedio PEN",boldbord)
		worksheet.write(16,6 , u"Importe USD",boldbord)
		worksheet.write(16,7 , u"Costo Promedio USD",boldbord)
		worksheet.write(17,1 , u"Inventario Inicial",boldbord)
		worksheet.write(17,2 , self.tritu_ini_ton,numberdos)
		worksheet.write(17,3 , self.tritu_ini_imp,numberdos)
		worksheet.write(17,4 , self.tritu_ini_cp,numberseis)
		worksheet.write(17,6 , self.tritu_ini_imp/tipo_cam,numberdos)
		worksheet.write(17,7 , self.tritu_ini_cp/tipo_cam,numberseis)
		worksheet.write(18,1 , u"Reproceso",boldbord)
		worksheet.write(18,2 , self.tritu_repro_ton,numberdos)
		worksheet.write(18,3 , self.tritu_repro_imp,numberdos)
		worksheet.write(18,4 , self.tritu_repro_cp,numberseis)
		worksheet.write(18,6 , self.tritu_repro_imp/tipo_cam,numberdos)
		worksheet.write(18,7 , self.tritu_repro_cp/tipo_cam,numberseis)
		worksheet.write(19,1 , u"Produccion",boldbord)
		worksheet.write(19,2 , self.tritu_pro_ton,numberdos)
		worksheet.write(19,3 , self.tritu_pro_imp,numberdos)
		worksheet.write(19,4 , self.tritu_pro_cp,numberseis)
		worksheet.write(19,6 , self.tritu_pro_imp/tipo_cam,numberdos)
		worksheet.write(19,7 , self.tritu_pro_cp/tipo_cam,numberseis)
		worksheet.write(20,1 , u"Disponible",boldbord)
		worksheet.write(20,2 , self.tritu_dis_ton,numberdos)
		worksheet.write(20,3 , self.tritu_dis_imp,numberdos)
		worksheet.write(20,4 , self.tritu_dis_cp,numberseis)
		worksheet.write(20,6 , self.tritu_dis_imp/tipo_cam,numberdos)
		worksheet.write(20,7 , self.tritu_dis_cp/tipo_cam,numberseis)
		worksheet.write(21,1 , u"Traspaso a HM",boldbord)
		worksheet.write(21,2 , self.tritu_tt_ton,numberdos)
		worksheet.write(21,3 , self.tritu_tt_imp,numberdos)
		worksheet.write(21,4 , self.tritu_tt_cp,numberseis)
		worksheet.write(21,6 , self.tritu_tt_imp/tipo_cam,numberdos)
		worksheet.write(21,7 , self.tritu_tt_cp/tipo_cam,numberseis)
		worksheet.write(22,1 , u"Reproceso",boldbord)
		worksheet.write(22,2 , self.tritu_repro_ton_d,numberdos)
		worksheet.write(22,3 , self.tritu_repro_imp_d,numberdos)
		worksheet.write(22,4 , self.tritu_repro_cp_d,numberseis)
		worksheet.write(22,6 , self.tritu_repro_imp/tipo_cam,numberdos)
		worksheet.write(22,7 , self.tritu_repro_cp_d/tipo_cam,numberseis)
		worksheet.write(23,1 , u"Ventas",boldbord)
		worksheet.write(23,2 , self.tritu_ven_ton,numberdos)
		worksheet.write(23,3 , self.tritu_ven_imp,numberdos)
		worksheet.write(23,4 , self.tritu_ven_cp,numberseis)
		worksheet.write(23,6 , self.tritu_ven_imp/tipo_cam,numberdos)
		worksheet.write(23,7 , self.tritu_ven_cp/tipo_cam,numberseis)
		worksheet.write(24,1 , u"Traspaso Final",boldbord)
		worksheet.write(24,2 , self.tritu_final_ton,numberdos)
		worksheet.write(24,3 , self.tritu_final_imp,numberdos)
		worksheet.write(24,4 , self.tritu_final_cp,numberseis)
		worksheet.write(24,6 , self.tritu_final_imp/tipo_cam,numberdos)
		worksheet.write(24,7 , self.tritu_final_cp/tipo_cam,numberseis)

		worksheet.write(27,1 , u"Almancen de Piedra HM",bold)
		
		worksheet.write(28,2 , u"Toneladas",boldbord)
		worksheet.write(28,3 , u"Importe PEN",boldbord)
		worksheet.write(28,4 , u"Costo Promedio PEN",boldbord)
		worksheet.write(28,6 , u"Importe USD",boldbord)
		worksheet.write(28,7 , u"Costo Promedio USD",boldbord)
		worksheet.write(29,1 , u"Inventario Inicial",boldbord)
		worksheet.write(29,2 , self.piedra_ini_ton,numberdos)
		worksheet.write(29,3 , self.piedra_ini_imp,numberdos)
		worksheet.write(29,4 , self.piedra_ini_cp,numberseis)
		worksheet.write(29,6 , self.piedra_ini_imp/tipo_cam,numberdos)
		worksheet.write(29,7 , self.piedra_ini_cp/tipo_cam,numberseis)
		worksheet.write(30,1 , u"Produccion",boldbord)
		worksheet.write(30,2 , self.piedra_pro_ton,numberdos)
		worksheet.write(30,3 , self.piedra_pro_imp,numberdos)
		worksheet.write(30,4 , self.piedra_pro_cp,numberseis)
		worksheet.write(30,6 , self.piedra_pro_imp/tipo_cam,numberdos)
		worksheet.write(30,7 , self.piedra_pro_cp/tipo_cam,numberseis)
		worksheet.write(31,1 , u"Disponible",boldbord)
		worksheet.write(31,2 , self.piedra_dis_ton,numberdos)
		worksheet.write(31,3 , self.piedra_dis_imp,numberdos)
		worksheet.write(31,4 , self.piedra_dis_cp,numberseis)
		worksheet.write(31,6 , self.piedra_dis_imp/tipo_cam,numberdos)
		worksheet.write(31,7 , self.piedra_dis_cp/tipo_cam,numberseis)
		worksheet.write(32,1 , u"Traspaso a calcinacion",boldbord)
		worksheet.write(32,2 , self.piedra_tt_ton,numberdos)
		worksheet.write(32,3 , self.piedra_tt_imp,numberdos)
		worksheet.write(32,4 , self.piedra_tt_cp,numberseis)
		worksheet.write(32,6 , self.piedra_tt_imp/tipo_cam,numberdos)
		worksheet.write(32,7 , self.piedra_tt_cp/tipo_cam,numberseis)
		worksheet.write(33,1 , u"Ventas",boldbord)
		worksheet.write(33,2 , self.piedra_ven_ton,numberdos)
		worksheet.write(33,3 , self.piedra_ven_imp,numberdos)
		worksheet.write(33,4 , self.piedra_ven_cp,numberseis)
		worksheet.write(33,6 , self.piedra_ven_imp/tipo_cam,numberdos)
		worksheet.write(33,7 , self.piedra_ven_cp/tipo_cam,numberseis)
		worksheet.write(34,1 , u"Inventario Final",boldbord)
		worksheet.write(34,2 , self.piedra_final_ton,numberdos)
		worksheet.write(34,3 , self.piedra_final_imp,numberdos)
		worksheet.write(34,4 , self.piedra_final_cp,numberseis)
		worksheet.write(34,6 , self.piedra_final_imp/tipo_cam,numberdos)
		worksheet.write(34,7 , self.piedra_final_cp/tipo_cam,numberseis)
		
		worksheet.write(37,1 , u"Calcinacion",bold)

		worksheet.write(38,2 , u"Toneladas",boldbord)
		worksheet.write(38,3 , u"Importe PEN",boldbord)
		worksheet.write(38,4 , u"Costo Promedio PEN",boldbord)
		worksheet.write(38,6 , u"Importe USD",boldbord)
		worksheet.write(38,7 , u"Costo Promedio USD",boldbord)
		worksheet.write(39,1 , u"Inventario Inicial",boldbord)
		worksheet.write(39,2 , self.calci_ini_ton,numberdos)
		worksheet.write(39,3 , self.calci_ini_imp,numberdos)
		worksheet.write(39,4 , self.calci_ini_cp,numberseis)
		worksheet.write(39,6 , self.calci_ini_imp/tipo_cam,numberdos)
		worksheet.write(39,7 , self.calci_ini_cp/tipo_cam,numberseis)
		worksheet.write(40,1 , u"Produccion",boldbord)
		worksheet.write(40,2 , self.calci_pro_ton,numberdos)
		worksheet.write(40,3 , self.calci_pro_imp,numberdos)
		worksheet.write(40,4 , self.calci_pro_cp,numberseis)
		worksheet.write(40,6 , self.calci_pro_imp/tipo_cam,numberdos)
		worksheet.write(40,7 , self.calci_pro_cp/tipo_cam,numberseis)
		worksheet.write(41,1 , u"Disponible",boldbord)
		worksheet.write(41,2 , self.calci_dis_ton,numberdos)
		worksheet.write(41,3 , self.calci_dis_imp,numberdos)
		worksheet.write(41,4 , self.calci_dis_cp,numberseis)
		worksheet.write(41,6 , self.calci_dis_imp/tipo_cam,numberdos)
		worksheet.write(41,7 , self.calci_dis_cp/tipo_cam,numberseis)
		worksheet.write(42,1 , u"Traspaso a Micronizado",boldbord)
		worksheet.write(42,2 , self.calci_tt_ton,numberdos)
		worksheet.write(42,3 , self.calci_tt_imp,numberdos)
		worksheet.write(42,4 , self.calci_tt_cp,numberseis)
		worksheet.write(42,6 , self.calci_tt_imp/tipo_cam,numberdos)
		worksheet.write(42,7 , self.calci_tt_cp/tipo_cam,numberseis)
		worksheet.write(43,1 , u"Ventas",boldbord)
		worksheet.write(43,2 , self.calci_ven_ton,numberdos)
		worksheet.write(43,3 , self.calci_ven_imp,numberdos)
		worksheet.write(43,4 , self.calci_ven_cp,numberseis)
		worksheet.write(43,6 , self.calci_ven_imp/tipo_cam,numberdos)
		worksheet.write(43,7 , self.calci_ven_cp/tipo_cam,numberseis)
		worksheet.write(44,1 , u"Otros",boldbord)
		worksheet.write(44,2 , self.calci_salida_ton,numberdos)
		worksheet.write(44,3 , self.calci_salida_imp,numberdos)
		worksheet.write(44,4 , self.calci_salida_cp,numberseis)
		worksheet.write(44,6 , self.calci_salida_imp/tipo_cam,numberdos)
		worksheet.write(44,7 , self.calci_salida_cp/tipo_cam,numberseis)
		worksheet.write(45,1 , u"Inventario Final",boldbord)
		worksheet.write(45,2 , self.calci_final_ton,numberdos)
		worksheet.write(45,3 , self.calci_final_imp,numberdos)
		worksheet.write(45,4 , self.calci_final_cp,numberseis)
		worksheet.write(45,6 , self.calci_final_imp/tipo_cam,numberdos)
		worksheet.write(45,7 , self.calci_final_cp/tipo_cam,numberseis)

		worksheet.write(48,1 , u"Micronizado",bold)

		worksheet.write(49,2 , u"Toneladas",boldbord)
		worksheet.write(49,3 , u"Importe PEN",boldbord)
		worksheet.write(49,4 , u"Costo Promedio PEN",boldbord)
		worksheet.write(49,6 , u"Importe USD",boldbord)
		worksheet.write(49,7 , u"Costo Promedio USD ",boldbord)
		worksheet.write(50,1 , u"Inventario Inicial",boldbord)
		worksheet.write(50,2 , self.micro_ini_ton,numberdos)
		worksheet.write(50,3 , self.micro_ini_imp,numberdos)
		worksheet.write(50,4 , self.micro_ini_cp,numberseis)
		worksheet.write(50,6 , self.micro_ini_imp/tipo_cam,numberdos)
		worksheet.write(50,7 , self.micro_ini_cp/tipo_cam,numberseis)
		worksheet.write(51,1 , u"Produccion",boldbord)
		worksheet.write(51,2 , self.micro_pro_ton,numberdos)
		worksheet.write(51,3 , self.micro_pro_imp,numberdos)
		worksheet.write(51,4 , self.micro_pro_cp,numberseis)
		worksheet.write(51,6 , self.micro_pro_imp/tipo_cam,numberdos)
		worksheet.write(51,7 , self.micro_pro_cp/tipo_cam,numberseis)
		worksheet.write(52,1 , u"Compra Mercaderia",boldbord)
		worksheet.write(52,2 , self.micro_merc_ton,numberdos)
		worksheet.write(52,3 , self.micro_merc_imp,numberdos)
		worksheet.write(52,4 , self.micro_merc_cp,numberseis)
		worksheet.write(52,6 , self.micro_merc_imp/tipo_cam,numberdos)
		worksheet.write(52,7 , self.micro_merc_cp/tipo_cam,numberseis)
		worksheet.write(53,1 , u"Disponible",boldbord)
		worksheet.write(53,2 , self.micro_dis_ton,numberdos)
		worksheet.write(53,3 , self.micro_dis_imp,numberdos)
		worksheet.write(53,4 , self.micro_dis_cp,numberseis)
		worksheet.write(53,6 , self.micro_dis_imp/tipo_cam,numberdos)
		worksheet.write(53,7 , self.micro_dis_cp/tipo_cam,numberseis)
		worksheet.write(54,1 , u"Ventas",boldbord)
		worksheet.write(54,2 , self.micro_ven_ton,numberdos)
		worksheet.write(54,3 , self.micro_ven_imp,numberdos)
		worksheet.write(54,4 , self.micro_ven_cp,numberseis)
		worksheet.write(54,6 , self.micro_ven_imp/tipo_cam,numberdos)
		worksheet.write(54,7 , self.micro_ven_cp/tipo_cam,numberseis)
		worksheet.write(55,1 , u"Inventario Final",boldbord)
		worksheet.write(55,2 , self.micro_final_ton,numberdos)
		worksheet.write(55,3 , self.micro_final_imp,numberdos)
		worksheet.write(55,4 , self.micro_final_cp,numberseis)
		worksheet.write(55,6 , self.micro_final_imp/tipo_cam,numberdos)
		worksheet.write(55,7 , self.micro_final_cp/tipo_cam,numberseis)




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


		workbook.close()
		
		f = open( direccion + 'tempo_calquipa_reporte_costeo_dolares.xlsx', 'rb')
		
		vals = {
			'output_name': 'CosteoDolares.xlsx',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		sfs_id = self.env['export.file.save'].create(vals)

		return {
		    "type": "ir.actions.act_window",
		    "res_model": "export.file.save",
		    "views": [[False, "form"]],
		    "res_id": sfs_id.id,
		    "target": "new",
		}


