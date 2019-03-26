# -*- encoding: utf-8 -*-
import base64
from openerp import models, fields, api 
from openerp.osv import osv

class hr_planilla1(models.Model):
	_name = 'hr.planilla1'

	periodo           = fields.Many2one('account.period','Periodo')
	employee_id		  = fields.Many2one('hr.employee', 'Empleado')
	dni               = fields.Char('Nro Documento', size=9)
	codigo_trabajador = fields.Char(u'Código',size=10)
	type_doc          = fields.Char('Tipo Documento', size=2)
	nombre_tra        = fields.Char('Nombres', size=30, readonly=1)
	cargo             = fields.Many2one('hr.job','Cargo', size=50, readonly=1)
	afiliacion        = fields.Many2one('hr.table.membership','Afiliación')
	tipo_comision     = fields.Boolean('Tipo Comisión')

class hr_planilla_wizard(models.TransientModel):
	_name='hr.planilla.wizard'

	period_id = fields.Many2one('account.period','Periodo',required=True)

	@api.multi
	def do_rebuild(self):
		hlc = self.env['hr.lista.conceptos'].search([]).sorted(key=lambda r: r.position)

		ht = self.env['hr.tareo'].search([('periodo','=',self.period_id.id)])
		if len(ht):
			all_concepts_ids = []
			ht = ht[0]
			for t_line in ht.detalle:
				hcl = self.env['hr.concepto.line'].search([('tareo_line_id','=',t_line.id)])
				for con in hcl:
					if con.concepto_id.id not in all_concepts_ids:
						all_concepts_ids.append(con.concepto_id.id)

			hlc = self.env['hr.lista.conceptos'].search([('id','in',all_concepts_ids)]).sorted(key=lambda r: r.position)

		str_cross  = ""
		str_select = ""
		for item in hlc:
			str_cross  += '"x_'+item.code + '" double precision,'
			str_select += 'conceptos."x_'+item.code + '",'

		if len(str_cross) > 0:
			str_cross  = str_cross[:-1]
			str_select = str_select[:-1]

		sql_de_la_vida = """
		SELECT 
		ht.periodo as periodo,
		itdp.code as type_doc,
		htl.employee_id as employee_id,
		htl.dni as dni,
		htl.codigo_trabajador as codigo_trabajador,
		he.name_related as nombre_tra,
		he.job_id as cargo,
		htl.afiliacion as afiliacion,
		he.c_mixta as tipo_comision,
		"""+str_select+"""
		FROM
		(SELECT *
		FROM crosstab(
			'
			SELECT htl.employee_id, hlc.name, hcl.monto
			FROM hr_tareo ht
			LEFT JOIN hr_tareo_line htl ON htl.tareo_id = ht.id
			LEFT JOIN hr_concepto_line hcl ON hcl.tareo_line_id = htl.id
			LEFT JOIN hr_lista_conceptos hlc ON hcl.concepto_id = hlc.id
			LEFT JOIN account_period ap ON ht.periodo = ap.id
			WHERE ht.periodo = """+str(self.period_id.id)+""" AND hlc.id in ("""+str(hlc.ids)[1:-1]+""")
			ORDER BY 1,hlc.position
			',
			'
			SELECT name FROM hr_lista_conceptos
			WHERE id in ("""+str(hlc.ids)[1:-1]+""")
			ORDER BY position
			'
			) as ct (employee_id integer, """+str_cross+""")) conceptos
		INNER JOIN hr_tareo_line htl ON htl.employee_id = conceptos.employee_id
		LEFT JOIN hr_tareo ht ON htl.tareo_id = ht.id
		LEFT JOIN hr_employee he ON conceptos.employee_id = he.id
		LEFT JOIN it_type_document_partner itdp ON he.type_document_id = itdp.id
		WHERE ht.periodo = """+str(self.period_id.id)+"""
		"""

		# file = open('C:/Users/Manager/Desktop/sqldelavida.txt','w')
		# file.write(sql_de_la_vida)
		#print sql_de_la_vida
		# file.close()
		
		self.env.cr.execute(sql_de_la_vida)
		data = self.env.cr.dictfetchall()

		for l in self.env['hr.planilla1'].search([]):
			l.unlink()
		for reg in data:
			self.env['hr.planilla1'].create(reg)
		model_data = self.env['ir.model.data']
		search_view = model_data.get_object_reference('hr_nomina_it', 'view_hr_planilla1_filter')
		return {
			'type'          : 'ir.actions.act_window',
			'res_model'     : 'hr.planilla1',
			'view_type'     : 'form',
			'view_mode'     : 'tree',
			'target'		: 'current',
			# 'search_view_id': search_view and search_view[1] or False,
			# 'views'         : [(False, 'tree')],
		}