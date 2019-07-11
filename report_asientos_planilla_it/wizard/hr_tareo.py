# -*- encoding: utf-8 -*-
import base64,sys,os,string
from openerp import models, fields, api,exceptions
from datetime import datetime

class HrTareo(models.Model):
	_inherit='hr.tareo'

	@api.multi
	def print_account_report(self):
		objs = self._context.get('active_ids',False)
		if not objs or len(objs) > 1:
			raise exceptions.Warning(u'Sólo puede imprimir un reporte a la vez!')
		this = self.browse(objs[0])
		if not this.d_asiento:
			raise exceptions.Warning(u'No ha generado un asiento distribuido!')

		from xlsxwriter.workbook import Workbook
		path = self.env['main.parameter'].search([])[0].dir_create_file
		now = fields.Datetime.context_timestamp(self,datetime.now())
		label = str(now)[:19].replace(':','_')
		file_name = 'Reporte Asiento Contable-Planilla '+label+'.xlsx'
		path+=file_name
		workbook = Workbook(path)
		worksheet = workbook.add_worksheet("Reporte")

		bold = workbook.add_format({'bold': True})
		boldtop = workbook.add_format({'bold': True,'top':1})
		boldbot = workbook.add_format({'bold': True,'bottom':1})
		boldcenter = workbook.add_format({'bold': True})
		boldcenter.set_align('center')
		boldcenter.set_align('vcenter')
		title = workbook.add_format({'bold': True})
		title.set_align('center')
		title.set_align('vcenter')
		title.set_font_size(font_size=26)
		boldcenterbot = workbook.add_format({'bold': True,'bottom':1})
		boldcenterbot.set_align('center')
		boldcenterbot.set_align('vcenter')
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(9)
		boldbord.set_bg_color('#DCE6F1')
		boldbords = workbook.add_format({'bold': True})
		boldbords.set_border(style=2)
		boldbords.set_align('center')
		boldbords.set_align('vcenter')
		boldbords.set_text_wrap()
		boldbords.set_font_size(9)
		boldbords.set_bg_color('#DCE6F1')
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'#,##0.00'})
		numbertress = workbook.add_format({'num_format':'0.000'})
		numberdoss = workbook.add_format({'num_format':'#,##0.00'})
		numberdoss.set_bg_color('#DCE6F1')
		numberdoss.set_border(style=2)
		numbertrestop = workbook.add_format({'num_format':'0.000'})
		numbertrestop.set_top(1)
		numberdostop = workbook.add_format({'num_format':'#,##0.00'})
		numberdostop.set_top(1)
		bord = workbook.add_format()
		bords = workbook.add_format()
		bord.set_border(style=1)
		#numberdos.set_border(style=1)
		numbertres.set_border(style=1)	
		boldtotal = workbook.add_format({'bold': True})
		boldtotal.set_align('right')
		boldtotal.set_align('vright')
		worksheet.set_row(7,100)
		x=15
		y=8
		widths = 0
		sys.setdefaultencoding('iso-8859-1')
		

		try:
			com = self.env['res.company'].search([],limit=1)[0]
		except IndexError:
			raise exceptions.Warning(u'No ha configurado su compañía')

		if com.logo:
			from StringIO import StringIO
			file = base64.b64decode(com.logo)
			worksheet.insert_image('M4','calidra.png',{'image_data':StringIO(file)})
		worksheet.merge_range(1,0,1,30, u'CALQUIPA S.A.C', title)
		worksheet.merge_range(2,0,2,30, u'REPORTE DE PLANILLA POR ASIENTO', title)
		worksheet.merge_range(13,0,14,0,u"Periodo",boldbord)
		worksheet.merge_range(13,1,14,1,u"Tipo documento",boldbord)
		worksheet.merge_range(13,2,14,2,u"Nro Documento",boldbord)
		worksheet.merge_range(13,3,14,3,u"Código",boldbord)
		worksheet.merge_range(13,4,14,4,u"Nombre",boldbord)
		worksheet.merge_range(13,5,14,5,u"Cargo",boldbord)
		worksheet.merge_range(13,6,14,6,u"Afiliación",boldbord)
		worksheet.merge_range(13,7,14,7,u"Tipo Comisión",boldbord)

		accounts = this.d_asiento.line_id.mapped('account_id')
		totals = [0 for i in range(len(accounts))]
		for account in accounts:
			worksheet.write(13,y,account.code,boldbord)
			worksheet.write(14,y,account.name,boldbord)
			widths+=1
			y+=1
		
		employees = this.d_asiento.line_id.mapped('employees_src_ids').mapped('employee_id')
		
		for emp in employees:
			worksheet.write(x,0,this.periodo.code,normal)
			worksheet.write(x,1,emp.type_document_id.code,normal)
			worksheet.write(x,2,emp.identification_id,normal)
			worksheet.write(x,3,emp.codigo_trabajador,normal)
			name=' '.join([emp.first_name_complete,emp.last_name_father,emp.last_name_mother])
			worksheet.write(x,4,name,normal)
			worksheet.write(x,5,emp.job_id.name or '',normal)
			worksheet.write(x,6,emp.afiliacion.name,normal)
			worksheet.write(x,7,'SI COM. MIXTA' if emp.c_mixta else 'NO COM. MIXTA',normal)
			y = 8
			for j,account in enumerate(accounts):
				line = this.d_asiento.line_id.filtered(lambda x: x.account_id==account)
				record = line.employees_src_ids.filtered(lambda x: x.employee_id==emp)
				if record:
					amount = record.amount if line.debit > 0 else record.amount*-1
					worksheet.write(x,y,amount,numberdos)
					totals[j]+=amount
				else:
					worksheet.write(x,y,0.0,numberdos)
				y+=1
			x+=1

		y = 8
		for i in totals:
			worksheet.write(x,y,i,numberdoss)
			y+=1

		tam_col = [10,10,10,10,35,28,12,13]+[11 for i in range(len(totals))]
		alpha,prev,acum = list(string.ascii_uppercase),'',0
		for i,item in enumerate(tam_col):
			worksheet.set_column(prev+alpha[i%26]+':'+prev+alpha[i%26],item)
			if i==26:
				prev = alpha[acum]
				acum+=1
		workbook.close()
		f = open(path, 'rb')
		sfs_id = self.env['export.file.save'].create({
			'output_name': file_name,
			'output_file': base64.encodestring(''.join(f.readlines())),		
		})
		f.close()
		if os._exists(path):
			os.remove(path)
		return {
			"type": "ir.actions.act_window",
			"res_model": "export.file.save",
			"views": [[False, "form"]],
			"res_id": sfs_id.id,
			"target": "new",
		}

		