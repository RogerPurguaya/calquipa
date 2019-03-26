# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv


class obra_curso(models.Model):
	_name = 'obra.curso'

	code = fields.Char(required=True, string="Código",size=50)
	descripcion = fields.Char(required=True, string="Descripción",size=200)
	fecha_inicio = fields.Date('Fecha Inicio',required=True)
	fecha_fin = fields.Date('Fecha Fin',required=True)

	_order = 'code'
	_rec_name='code'



class expediente_importacion(models.Model):
	_name = 'expediente.importacion'

	code = fields.Char(required=True, string="Código",size=50)
	descripcion = fields.Char(required=True, string="Descripción",size=200)
	fecha_inicio = fields.Date('Fecha Inicio',required=True)
	fecha_fin = fields.Date('Fecha Fin',required=True)

	_order = 'code'
	_rec_name='code'


class account_move_line(models.Model):
	_inherit = 'account.move.line'
	
	obra_curso_id = fields.Many2one('obra.curso','Obras Curso')
	expediente_importacion_id = fields.Many2one('expediente.importacion','Expediente Importación')


class account_invoice(models.Model):
	_inherit='account.invoice'
	
	obra_curso_id = fields.Many2one('obra.curso','Obras Curso')
	expediente_importacion_id = fields.Many2one('expediente.importacion','Expediente Importación')


	@api.one
	def action_number(self):
		t = super(account_invoice,self).action_number()

		for i in self.move_id.line_id:
			if self.obra_curso_id.id:
				i.obra_curso_id = self.obra_curso_id
			if self.expediente_importacion_id.id:
				i.expediente_importacion_id = self.expediente_importacion_id
		return t



class purchase_order(models.Model):
	_inherit= 'purchase.order'

	obra_curso_id = fields.Many2one('obra.curso','Obras Curso')
	expediente_importacion_id = fields.Many2one('expediente.importacion','Expediente Importación')

	@api.multi
	def action_invoice_create(self):
		t = super(purchase_order,self).action_invoice_create()
		invoice_obj = self.env['account.invoice'].search([('id','=',t)])[0]
		
		if self.obra_curso_id.id:
			invoice_obj.obra_curso_id = self.obra_curso_id
		if self.expediente_importacion_id.id:
			invoice_obj.expediente_importacion_id = self.expediente_importacion_id
		return t

class purchase_requisition(models.Model):
	_inherit = 'purchase.requisition'


	obra_curso_id = fields.Many2one('obra.curso','Obras Curso')
	expediente_importacion_id = fields.Many2one('expediente.importacion','Expediente Importación')

	def _prepare_purchase_order(self, cr, uid, requisition, supplier, context=None):
		t = super(purchase_requisition,self)._prepare_purchase_order(cr, uid, requisition, supplier, context)
		if requisition.obra_curso_id:
			t['obra_curso_id']=requisition.obra_curso_id.id
		if requisition.expediente_importacion_id:
			t['expediente_importacion_id']=requisition.expediente_importacion_id.id
		return t




class account_analytic_book_major(models.Model):
	_inherit = 'account.analytic.book.major'
	
	obra_curso = fields.Char('Obras Curso',size=200)
	expediente_importacion = fields.Char('Expediente Importación',size=200)



class account_move_line_book(models.Model):
	_inherit = 'account.move.line.book'
	obra_curso = fields.Char('Obras Curso',size=200)
	expediente_importacion = fields.Char('Expediente Importación',size=200)



class account_move_line_book_report(models.Model):
	_inherit = 'account.move.line.book.report'
	obra_curso = fields.Char('Obras Curso',size=200)
	expediente_importacion = fields.Char('Expediente Importación',size=200)

	

class account_analytic_book_major_mexico(models.Model):
	_inherit = 'account.analytic.book.major.mexico'
	obra_curso = fields.Char('Obras Curso',size=200)
	expediente_importacion = fields.Char('Expediente Importación',size=200)
	


class account_move_line_book_mexico(models.Model):
	_inherit = 'account.move.line.book.mexico'
	obra_curso = fields.Char('Obras Curso',size=200)
	expediente_importacion = fields.Char('Expediente Importación',size=200)


class account_move_line_book_report_mexico(models.Model):
	_inherit = 'account.move.line.book.report.mexico'
	obra_curso = fields.Char('Obras Curso',size=200)
	expediente_importacion = fields.Char('Expediente Importación',size=200)
	


class libro_mayor_actualizador(models.Model):
	_name='libro.mayor.actualizador'
	_auto =False

	def init(self,cr):


		libromayor = """
		DROP FUNCTION IF EXISTS get_libro_mayor(boolean, integer, integer) cascade;
CREATE OR REPLACE FUNCTION get_libro_mayor(IN has_currency boolean, IN periodo_ini integer, IN periodo_fin integer)
	RETURNS TABLE(id bigint ,periodo character varying, libro character varying, voucher character varying, cuenta character varying, descripcion character varying, debe numeric, haber numeric, divisa character varying, tipocambio numeric, importedivisa numeric, conciliacion character varying, fechaemision date, fechavencimiento date, tipodocumento character varying, numero character varying, ruc character varying, partner character varying, glosa character varying, analitica character varying, ordenamiento integer, cuentaname character varying, aml_id integer, state varchar, expediente_importacion varchar, obra_curso varchar) AS
$BODY$
BEGIN

IF $3 is Null THEN
		$3 := $2;
END IF;

RETURN QUERY 
SELECT row_number() OVER () AS id,* from ( (SELECT ap.name AS periodo,
										aj.code AS libro,
										am.name AS voucher,
										aa.code AS cuenta,
										aa.name AS descripcion,
										CASE WHEN $1 THEN aml.debit_me ELSE aml.debit END AS debe,
			CASE WHEN $1 THEN aml.credit_me ELSE aml.credit END AS haber,
										rc.name AS divisa,

						CASE WHEN $1 THEN aml.currency_rate_it
						ELSE
										CASE WHEN rc.name = 'USD' THEN aml.currency_rate_it ELSE Null::numeric END END AS tipocambio,
										aml.amount_currency AS importedivisa,
										aml.reconcile_ref AS conciliacion,
										aml.date AS fechaemision,
										aml.date_maturity AS fechavencimiento,
										itd.code AS tipodocumento,
										aml.nro_comprobante AS numero,
										rp.type_number AS ruc,
										rp.name AS partner,
										aml.name AS glosa,
										aaa.code AS analitica,
										1 AS ordenamiento,
												CASE
														WHEN "position"(aa.name::varchar, '-'::varchar) = 0 THEN aa.name::varchar
														ELSE "substring"(aa.name::varchar, 0, "position"(aa.name::varchar, '-'::varchar))::varchar
												END AS cuentaname,
										aml.id as aml_id,
										case when am.state = 'draft' then 'Borrador'::varchar else 'Asentado'::varchar END as state,
										expediente_importacion.code as expediente_importacion_id ,obra_curso.code as obra_curso_id  
									 FROM account_move_line aml
										 JOIN account_journal aj ON aml.journal_id = aj.id
										 JOIN account_move am ON aml.move_id = am.id
										 JOIN account_account aa ON aml.account_id = aa.id
										 JOIN account_period ap ON ap.id = aml.period_id
										 LEFT JOIN res_currency rc ON aml.currency_id = rc.id

										 LEFT JOIN obra_curso on aml.obra_curso_id = obra_curso.id
										 LEFT JOIN expediente_importacion on expediente_importacion.id = aml.expediente_importacion_id

						 LEFT JOIN it_type_document itd ON itd.id = aml.type_document_id
										 LEFT JOIN res_partner rp ON rp.id = aml.partner_id
										 LEFT JOIN account_analytic_account aaa ON aaa.id = aml.analytic_account_id
									 WHERE periodo_num(ap.name) >= $2 and periodo_num(ap.name) <= $3
									 and am.state != 'draft')
	
									UNION ALL
									(
		SELECT  
			periodo_string($2) as periodo,  
			Null::varchar as libro,
			Null::varchar as voucher, 
			aa.code as Cuenta, 
			aa.name as descripcion,
			 CASE WHEN $1 THEN (CASE WHEN sum(aml.debit_me) - sum(aml.credit_me) >0 THEN sum(aml.debit_me) - sum(aml.credit_me) ELSE 0 END) ELSE (CASE WHEN sum(aml.debit) - sum(aml.credit) >0 THEN sum(aml.debit) - sum(aml.credit) ELSE 0 END) END AS debe,
			CASE WHEN $1 THEN (CASE WHEN sum(aml.credit_me) - sum(aml.debit_me) >0 THEN sum(aml.credit_me) - sum(aml.debit_me) ELSE 0 END) ELSE (CASE WHEN sum(aml.credit) - sum(aml.debit) >0 THEN sum(aml.credit) - sum(aml.debit) ELSE 0 END) END AS haber,
		
			 Null::varchar as divisa,
			 Null::numeric as tipocambio,
			 Null::numeric as importedivisa,
			 Null::varchar as conciliacion,
			 Null::date as fechaemision,
			 Null::date as fechavencimiento,
			 Null::varchar as tipodocumento,
			 Null::varchar as numero,
			 Null::varchar as ruc,
			 Null::varchar as partner,
			 'Saldo Inicial'::varchar as glosa,
			 Null::varchar as analitica,
			 0 as ordenamiento,
			 Null::varchar as cuentaname,
			 Null::integer as aml_id,
			 'Asentado'::varchar as state,
			 Null::varchar as expediente_importacion_id,
			 Null::varchar as obra_curso_id
		FROM
			account_move_line aml
			INNER JOIN account_journal aj ON (aml.journal_id = aj.id)
			INNER JOIN account_move am ON (aml.move_id = am.id)
			INNER JOIN account_account aa ON (aml.account_id = aa.id)
			INNER JOIN account_period ap_1 ON (ap_1.id = aml.period_id)
			LEFT OUTER JOIN res_currency rc ON (aml.currency_id = rc.id)
			LEFT OUTER JOIN res_partner rp ON (rp.id = aml.partner_id)
			LEFT OUTER JOIN account_analytic_account aaa ON (aaa.id = aml.analytic_account_id)
		WHERE periodo_num(ap_1.name) < $2 
		and am.state != 'draft'
		group by aa.code, aa.name) 
		order by cuenta,ordenamiento,periodo,fechaemision) AS T; 

END;
$BODY$
	LANGUAGE plpgsql VOLATILE
	COST 100
	ROWS 1000;
		"""


		librodiario = """ 
		DROP FUNCTION IF EXISTS get_libro_diario(boolean, integer, integer) cascade;
CREATE OR REPLACE FUNCTION get_libro_diario(IN has_currency boolean, IN periodo_ini integer, IN periodo_fin integer)
	RETURNS TABLE(id bigint, periodo varchar, libro varchar, voucher varchar, cuenta varchar, descripcion varchar, debe numeric, haber numeric, divisa varchar, tipodecambio numeric, importedivisa numeric, codigo varchar, partner varchar, tipodocumento varchar, numero varchar, fechaemision date, fechavencimiento date, glosa varchar, ctaanalitica varchar, refconcil varchar, statefiltro varchar, aml_id integer, aj_id integer, ap_id integer, am_id integer, aa_id integer, rc_id integer, rp_id integer, itd_id integer, aaa_id integer ,state varchar, expediente_importacion varchar, obra_curso varchar) AS
$BODY$
BEGIN

IF $3 is Null THEN
		$3 := $2;
END IF;

RETURN QUERY 
SELECT row_number() OVER () AS id,*
	 FROM ( SELECT ap.name AS periodo,
						aj.code AS libro,
						am.name AS voucher,
						aa.code AS cuenta,
						aa.name AS descripcion,
						CASE WHEN $1 THEN aml.debit_me ELSE aml.debit END AS debe,
						CASE WHEN $1 THEN aml.credit_me ELSE aml.credit END AS haber,
						rc.name AS divisa,
						CASE WHEN $1 THEN aml.currency_rate_it
						ELSE
						CASE WHEN rc.name ='USD' THEN aml.currency_rate_it ELSE Null::numeric END END AS tipodecambio,
						aml.amount_currency AS importedivisa,
						rp.type_number AS codigo,
						rp.name AS partner,
						itd.code AS tipodocumento,
						aml.nro_comprobante AS numero,
						aml.date AS fechaemision,
						aml.date_maturity AS fechavencimiento,
						aml.name AS glosa,
						aaa.name AS ctaanalitica,
						aml.reconcile_ref AS refconcil,
						am.state AS statefiltro,
						aml.id AS aml_id,
						aj.id AS aj_id,
						ap.id AS ap_id,
						am.id AS am_id,
						aa.id AS aa_id,
						rc.id AS rc_id,
						rp.id AS rp_id,
						itd.id AS itd_id,
						aaa.id AS aaa_id,
						case when am.state = 'posted'::varchar then 'Asentado'::varchar ELSE 'Borrador'::varchar END as state,
										expediente_importacion.code as expediente_importacion_id ,obra_curso.code as obra_curso_id  
					 FROM account_move_line aml
						 JOIN account_journal aj ON aj.id = aml.journal_id
						 JOIN account_period ap ON ap.id = aml.period_id
						 JOIN account_move am ON am.id = aml.move_id
						 JOIN account_account aa ON aa.id = aml.account_id
						 LEFT JOIN res_currency rc ON rc.id = aml.currency_id
						 LEFT JOIN res_partner rp ON rp.id = aml.partner_id

										 LEFT JOIN obra_curso on aml.obra_curso_id = obra_curso.id
										 LEFT JOIN expediente_importacion on expediente_importacion.id = aml.expediente_importacion_id

						 LEFT JOIN it_type_document itd ON itd.id = aml.type_document_id
						 LEFT JOIN account_analytic_account aaa ON aaa.id = aml.analytic_account_id
						 where am.state != 'draft'
					ORDER BY ap.id, aj.code, am.name) t
					where periodo_num(t.periodo) >= $2 and periodo_num(t.periodo)<=$3;

END;
$BODY$
	LANGUAGE plpgsql VOLATILE
	COST 100
	ROWS 1000;
 """



		librodiariomexico = """ 
		DROP FUNCTION IF EXISTS get_libro_diario_mexico(boolean, integer, integer) cascade;
CREATE OR REPLACE FUNCTION get_libro_diario_mexico(IN has_currency boolean, IN periodo_ini integer, IN periodo_fin integer)
	RETURNS TABLE(id bigint, periodo varchar, libro varchar, voucher varchar, cuenta varchar, descripcion varchar, debe numeric, haber numeric, divisa varchar, tipodecambio numeric, importedivisa numeric, codigo varchar, partner varchar, tipodocumento varchar, numero varchar, fechaemision date, fechavencimiento date, glosa varchar, ctaanalitica varchar, refconcil varchar, statefiltro varchar, aml_id integer, aj_id integer, ap_id integer, am_id integer, aa_id integer, rc_id integer, rp_id integer, itd_id integer, aaa_id integer ,state varchar, expediente_importacion varchar, obra_curso varchar) AS
$BODY$
BEGIN

IF $3 is Null THEN
		$3 := $2;
END IF;

RETURN QUERY 
SELECT row_number() OVER () AS id,*
	 FROM ( SELECT ap.name AS periodo,
						aj.code AS libro,
						am.name AS voucher,
						itm.code AS cuenta,
						itm.nomenclatura AS descripcion,
						CASE WHEN $1 THEN aml.debit_me ELSE aml.debit END AS debe,
						CASE WHEN $1 THEN aml.credit_me ELSE aml.credit END AS haber,
						rc.name AS divisa,
						CASE WHEN $1 THEN aml.currency_rate_it
						ELSE
						CASE WHEN rc.name ='USD' THEN aml.currency_rate_it ELSE Null::numeric END END AS tipodecambio,
						aml.amount_currency AS importedivisa,
						rp.type_number AS codigo,
						rp.name AS partner,
						itd.code AS tipodocumento,
						aml.nro_comprobante AS numero,
						aml.date AS fechaemision,
						aml.date_maturity AS fechavencimiento,
						aml.name AS glosa,
						aaa.name AS ctaanalitica,
						aml.reconcile_ref AS refconcil,
						am.state AS statefiltro,
						aml.id AS aml_id,
						aj.id AS aj_id,
						ap.id AS ap_id,
						am.id AS am_id,
						aa.id AS aa_id,
						rc.id AS rc_id,
						rp.id AS rp_id,
						itd.id AS itd_id,
						aaa.id AS aaa_id,
						case when am.state = 'posted'::varchar then 'Asentado'::varchar ELSE 'Borrador'::varchar END as state,
										expediente_importacion.code as expediente_importacion_id ,obra_curso.code as obra_curso_id  
					 FROM account_move_line aml
						 JOIN account_journal aj ON aj.id = aml.journal_id
						 JOIN account_period ap ON ap.id = aml.period_id
						 JOIN account_move am ON am.id = aml.move_id
						 JOIN account_account aa ON aa.id = aml.account_id
						 LEFT JOIN it_account_mexicana itm on itm.id = aa.code_mexicana
						 LEFT JOIN res_currency rc ON rc.id = aml.currency_id
						 LEFT JOIN res_partner rp ON rp.id = aml.partner_id

										 LEFT JOIN obra_curso on aml.obra_curso_id = obra_curso.id
										 LEFT JOIN expediente_importacion on expediente_importacion.id = aml.expediente_importacion_id

						 LEFT JOIN it_type_document itd ON itd.id = aml.type_document_id
						 LEFT JOIN account_analytic_account aaa ON aaa.id = aml.analytic_account_id
						 where am.state != 'draft'
					ORDER BY ap.id, aj.code, am.name) t
					where periodo_num(t.periodo) >= $2 and periodo_num(t.periodo)<=$3;

END;
$BODY$
	LANGUAGE plpgsql VOLATILE
	COST 100
	ROWS 1000;
 """


		libromayormexico = """
		DROP FUNCTION IF EXISTS get_libro_mayor_mexico(boolean, integer, integer) cascade;
CREATE OR REPLACE FUNCTION get_libro_mayor_mexico(IN has_currency boolean, IN periodo_ini integer, IN periodo_fin integer)
	RETURNS TABLE(id bigint ,periodo character varying, libro character varying, voucher character varying, cuenta character varying, descripcion character varying, debe numeric, haber numeric, divisa character varying, tipocambio numeric, importedivisa numeric, conciliacion character varying, fechaemision date, fechavencimiento date, tipodocumento character varying, numero character varying, ruc character varying, partner character varying, glosa character varying, analitica character varying, ordenamiento integer, cuentaname character varying, aml_id integer, state varchar, expediente_importacion varchar, obra_curso varchar) AS
$BODY$
BEGIN

IF $3 is Null THEN
		$3 := $2;
END IF;

RETURN QUERY 
SELECT row_number() OVER () AS id,* from ( (SELECT ap.name AS periodo,
										aj.code AS libro,
										am.name AS voucher,
										itm.code AS cuenta,
										itm.nomenclatura AS descripcion,
										CASE WHEN $1 THEN aml.debit_me ELSE aml.debit END AS debe,
			CASE WHEN $1 THEN aml.credit_me ELSE aml.credit END AS haber,
										rc.name AS divisa,

						CASE WHEN $1 THEN aml.currency_rate_it
						ELSE
										CASE WHEN rc.name = 'USD' THEN aml.currency_rate_it ELSE Null::numeric END END AS tipocambio,
										aml.amount_currency AS importedivisa,
										aml.reconcile_ref AS conciliacion,
										aml.date AS fechaemision,
										aml.date_maturity AS fechavencimiento,
										itd.code AS tipodocumento,
										aml.nro_comprobante AS numero,
										rp.type_number AS ruc,
										rp.name AS partner,
										aml.name AS glosa,
										aaa.code AS analitica,
										1 AS ordenamiento,
												CASE
														WHEN "position"(aa.name::varchar, '-'::varchar) = 0 THEN aa.name::varchar
														ELSE "substring"(aa.name::varchar, 0, "position"(aa.name::varchar, '-'::varchar))::varchar
												END AS cuentaname,
										aml.id as aml_id,
										case when am.state = 'draft' then 'Borrador'::varchar else 'Asentado'::varchar END as state,
										expediente_importacion.code as expediente_importacion_id ,obra_curso.code as obra_curso_id  
									 FROM account_move_line aml
										 JOIN account_journal aj ON aml.journal_id = aj.id
										 JOIN account_move am ON aml.move_id = am.id
										 JOIN account_account aa ON aml.account_id = aa.id
										 JOIN account_period ap ON ap.id = aml.period_id

						 				LEFT JOIN it_account_mexicana itm on itm.id = aa.code_mexicana
										 LEFT JOIN res_currency rc ON aml.currency_id = rc.id

										 LEFT JOIN obra_curso on aml.obra_curso_id = obra_curso.id
										 LEFT JOIN expediente_importacion on expediente_importacion.id = aml.expediente_importacion_id

						 LEFT JOIN it_type_document itd ON itd.id = aml.type_document_id
										 LEFT JOIN res_partner rp ON rp.id = aml.partner_id
										 LEFT JOIN account_analytic_account aaa ON aaa.id = aml.analytic_account_id
									 WHERE periodo_num(ap.name) >= $2 and periodo_num(ap.name) <= $3
									 and am.state != 'draft')
	
									UNION ALL
									(
		SELECT  
			periodo_string($2) as periodo,  
			Null::varchar as libro,
			Null::varchar as voucher, 
										itm.code AS cuenta,
										itm.nomenclatura AS descripcion,
			 CASE WHEN $1 THEN (CASE WHEN sum(aml.debit_me) - sum(aml.credit_me) >0 THEN sum(aml.debit_me) - sum(aml.credit_me) ELSE 0 END) ELSE (CASE WHEN sum(aml.debit) - sum(aml.credit) >0 THEN sum(aml.debit) - sum(aml.credit) ELSE 0 END) END AS debe,
			CASE WHEN $1 THEN (CASE WHEN sum(aml.credit_me) - sum(aml.debit_me) >0 THEN sum(aml.credit_me) - sum(aml.debit_me) ELSE 0 END) ELSE (CASE WHEN sum(aml.credit) - sum(aml.debit) >0 THEN sum(aml.credit) - sum(aml.debit) ELSE 0 END) END AS haber,
		
			 Null::varchar as divisa,
			 Null::numeric as tipocambio,
			 Null::numeric as importedivisa,
			 Null::varchar as conciliacion,
			 Null::date as fechaemision,
			 Null::date as fechavencimiento,
			 Null::varchar as tipodocumento,
			 Null::varchar as numero,
			 Null::varchar as ruc,
			 Null::varchar as partner,
			 'Saldo Inicial'::varchar as glosa,
			 Null::varchar as analitica,
			 0 as ordenamiento,
			 Null::varchar as cuentaname,
			 Null::integer as aml_id,
			 'Asentado'::varchar as state,
			 Null::varchar as expediente_importacion_id,
			 Null::varchar as obra_curso_id
		FROM
			account_move_line aml
			INNER JOIN account_journal aj ON (aml.journal_id = aj.id)
			INNER JOIN account_move am ON (aml.move_id = am.id)
			INNER JOIN account_account aa ON (aml.account_id = aa.id)
			INNER JOIN account_period ap_1 ON (ap_1.id = aml.period_id)
			
						 LEFT JOIN it_account_mexicana itm on itm.id = aa.code_mexicana
			LEFT OUTER JOIN res_currency rc ON (aml.currency_id = rc.id)
			LEFT OUTER JOIN res_partner rp ON (rp.id = aml.partner_id)
			LEFT OUTER JOIN account_analytic_account aaa ON (aaa.id = aml.analytic_account_id)
		WHERE periodo_num(ap_1.name) < $2 
		and am.state != 'draft'
		group by itm.code, itm.nomenclatura) 
		order by cuenta,ordenamiento,periodo,fechaemision) AS T; 

END;
$BODY$
	LANGUAGE plpgsql VOLATILE
	COST 100
	ROWS 1000;
		"""

		cr.execute(libromayor + librodiario + libromayormexico + librodiariomexico)


class account_analytic_book_major_wizard(osv.TransientModel):
	_inherit = 'account.analytic.book.major.wizard'


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
			CREATE OR REPLACE view account_analytic_book_major as (SELECT * FROM get_libro_mayor("""+ str(currency)+ """,periodo_num('""" + period_ini.code + """'),periodo_num('""" + period_end.code +"""')) 
		)""")

		if self.cuentas:
			libros_list = ["Saldo Inicial"]
			for i in  self.cuentas:
				libros_list.append(i.code)
			filtro.append( ('cuenta','in',tuple(libros_list)) )
		
		if self.type_show == 'pantalla':
			mod_obj = self.env['ir.model.data']
			act_obj = self.env['ir.actions.act_window']

			result = mod_obj.get_object_reference('account_analytic_bookmajor_it', 'action_account_analytic_book_major_it')
			
			id = result and result[1] or False
			print id
			return {
				'domain' : filtro,
				'type': 'ir.actions.act_window',
				'res_model': 'account.analytic.book.major',
				'view_mode': 'tree',
				'view_type': 'form',
				'res_id': id,
				'views': [(False, 'tree')],
			}
		
		if self.type_show == 'excel':

			import io
			from xlsxwriter.workbook import Workbook
			output = io.BytesIO()
			########### PRIMERA HOJA DE LA DATA EN TABLA
			#workbook = Workbook(output, {'in_memory': True})

			direccion = self.env['main.parameter'].search([])[0].dir_create_file

			workbook = Workbook(direccion +'tempo_libromayor.xlsx')
			worksheet = workbook.add_worksheet("Libro Mayor")
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

			worksheet.write(0,0, "Libro Mayor:", bold)
			tam_col[0] = tam_letra* len("Libro Mayor:") if tam_letra* len("Libro Mayor:")> tam_col[0] else tam_col[0]

			worksheet.write(0,1, self.period_ini.name, normal)
			tam_col[1] = tam_letra* len(self.period_ini.name) if tam_letra* len(self.period_ini.name)> tam_col[1] else tam_col[1]

			worksheet.write(0,2, self.period_end.name, normal)
			tam_col[2] = tam_letra* len(self.period_end.name) if tam_letra* len(self.period_end.name)> tam_col[2] else tam_col[2]

			worksheet.write(1,0, "Fecha:",bold)
			tam_col[0] = tam_letra* len("Fecha:") if tam_letra* len("Fecha:")> tam_col[0] else tam_col[0]

			#worksheet.write(1,1, total.date.strftime('%Y-%m-%d %H:%M'),bord)
			import datetime
			worksheet.write(1,1, str(datetime.datetime.today())[:10], normal)
			tam_col[1] = tam_letra* len(str(datetime.datetime.today())[:10]) if tam_letra* len(str(datetime.datetime.today())[:10])> tam_col[1] else tam_col[1]
			

			worksheet.write(3,0, "Periodo",boldbord)
			tam_col[0] = tam_letra* len("Periodo") if tam_letra* len("Periodo")> tam_col[0] else tam_col[0]
			worksheet.write(3,1, "Libro",boldbord)
			tam_col[1] = tam_letra* len("Libro") if tam_letra* len("Libro")> tam_col[1] else tam_col[1]
			worksheet.write(3,2, "Voucher",boldbord)
			tam_col[2] = tam_letra* len("Voucher") if tam_letra* len("Voucher")> tam_col[2] else tam_col[2]
			worksheet.write(3,3, "Cuenta",boldbord)
			tam_col[3] = tam_letra* len("Cuenta") if tam_letra* len("Cuenta")> tam_col[3] else tam_col[3]
			worksheet.write(3,4, u"Descripción",boldbord)
			tam_col[4] = tam_letra* len(u"Descripción") if tam_letra* len(u"Descripción")> tam_col[4] else tam_col[4]
			worksheet.write(3,5, "Debe",boldbord)
			tam_col[5] = tam_letra* len("Debe") if tam_letra* len("Debe")> tam_col[5] else tam_col[5]
			worksheet.write(3,6, "Haber",boldbord)
			tam_col[6] = tam_letra* len("Haber") if tam_letra* len("Haber")> tam_col[6] else tam_col[6]
			worksheet.write(3,7, "Saldo",boldbord)
			tam_col[7] = tam_letra* len("Saldo") if tam_letra* len("Saldo")> tam_col[7] else tam_col[7]
			worksheet.write(3,8, "Divisa",boldbord)
			tam_col[8] = tam_letra* len("Divisa") if tam_letra* len("Divisa")> tam_col[8] else tam_col[8]
			worksheet.write(3,9, "Tipo Cambio",boldbord)
			tam_col[9] = tam_letra* len("Tipo Cambio") if tam_letra* len("Tipo Cambio")> tam_col[9] else tam_col[9]
			worksheet.write(3,10, "Importe Divisa",boldbord)
			tam_col[10] = tam_letra* len("Importe Divisa") if tam_letra* len("Importe Divisa")> tam_col[10] else tam_col[10]
			worksheet.write(3,11, u"Conciliación",boldbord)
			tam_col[11] = tam_letra* len(u"Conciliación") if tam_letra* len(u"Conciliación")> tam_col[11] else tam_col[11]
			worksheet.write(3,12, u"Analítica",boldbord)
			tam_col[12] = tam_letra* len(u"Analítica") if tam_letra* len(u"Analítica")> tam_col[12] else tam_col[12]

			worksheet.write(3,13, u"Expediente Importación",boldbord)
			worksheet.write(3,14, u"Obras Curso",boldbord)
			

			worksheet.write(3,15, u"Fecha Emisión",boldbord)
			worksheet.write(3,16, "Fecha Vencimiento",boldbord)
			worksheet.write(3,17, "Tipo Documento",boldbord)
			worksheet.write(3,18, u"Número",boldbord)
			worksheet.write(3,19, u"RUC",boldbord)
			worksheet.write(3,20, u"Partner",boldbord)
			worksheet.write(3,21, u"Glosa",boldbord)
			
			for line in self.env['account.analytic.book.major'].search(filtro):
				worksheet.write(x,0,line.periodo if line.periodo else '' ,bord )
				worksheet.write(x,1,line.libro if line.libro  else '',bord )
				worksheet.write(x,2,line.voucher if line.voucher  else '',bord)
				worksheet.write(x,3,line.cuenta if line.cuenta  else '',bord)
				worksheet.write(x,4,line.descripcion if line.descripcion  else '',bord)
				worksheet.write(x,5,line.debe ,numberdos)
				worksheet.write(x,6,line.haber ,numberdos)
				worksheet.write(x,7,line.saldo ,numberdos)
				worksheet.write(x,8,line.divisa if  line.divisa else '',bord)
				worksheet.write(x,9,line.tipocambio ,numbertres)
				worksheet.write(x,10,line.importedivisa ,numberdos)
				worksheet.write(x,11,line.conciliacion if line.conciliacion else '',bord)
				worksheet.write(x,12,line.analitica if line.analitica else '',bord)

				worksheet.write(x,13,line.expediente_importacion if line.expediente_importacion else '',bord)
				worksheet.write(x,14,line.obra_curso if line.obra_curso else '',bord)

				worksheet.write(x,15,line.fechaemision if line.fechaemision else '',bord)
				worksheet.write(x,16,line.fechavencimiento if line.fechavencimiento else '',bord)
				worksheet.write(x,17,line.tipodocumento if line.tipodocumento else '',bord)
				worksheet.write(x,18,line.numero if line.numero  else '',bord)				
				worksheet.write(x,19,line.ruc if line.ruc  else '',bord)
				worksheet.write(x,20,line.partner if line.partner  else '',bord)
				worksheet.write(x,21,line.glosa if line.glosa else '',bord)


				tam_col[0] = tam_letra* len(line.periodo if line.periodo else '' ) if tam_letra* len(line.periodo if line.periodo else '' )> tam_col[0] else tam_col[0]
				tam_col[1] = tam_letra* len(line.libro if line.libro  else '') if tam_letra* len(line.libro if line.libro  else '')> tam_col[1] else tam_col[1]
				tam_col[2] = tam_letra* len(line.voucher if line.voucher  else '') if tam_letra* len(line.voucher if line.voucher  else '')> tam_col[2] else tam_col[2]
				tam_col[3] = tam_letra* len(line.cuenta if line.cuenta  else '') if tam_letra* len(line.cuenta if line.cuenta  else '')> tam_col[3] else tam_col[3]
				tam_col[4] = tam_letra* len(line.descripcion if line.descripcion  else '') if tam_letra* len(line.descripcion if line.descripcion  else '')> tam_col[4] else tam_col[4]
				tam_col[5] = tam_letra* len("%0.2f"%line.debe ) if tam_letra* len("%0.2f"%line.debe )> tam_col[5] else tam_col[5]
				tam_col[6] = tam_letra* len("%0.2f"%line.haber ) if tam_letra* len("%0.2f"%line.haber )> tam_col[6] else tam_col[6]
				tam_col[7] = tam_letra* len("%0.2f"%line.saldo ) if tam_letra* len("%0.2f"%line.saldo )> tam_col[7] else tam_col[7]
				tam_col[8] = tam_letra* len(line.divisa if  line.divisa else '') if tam_letra* len(line.divisa if  line.divisa else '')> tam_col[8] else tam_col[8]
				tam_col[9] = tam_letra* len("%0.3f"%line.tipocambio ) if tam_letra* len("%0.3f"%line.tipocambio )> tam_col[9] else tam_col[9]
				tam_col[10] = tam_letra* len("%0.2f"%line.importedivisa ) if tam_letra* len("%0.2f"%line.importedivisa )> tam_col[10] else tam_col[10]
				tam_col[11] = tam_letra* len(line.conciliacion if line.conciliacion else '') if tam_letra* len(line.conciliacion if line.conciliacion else '')> tam_col[11] else tam_col[11]
				tam_col[12] = tam_letra* len(line.analitica if line.analitica else '') if tam_letra* len(line.analitica if line.analitica else '')> tam_col[12] else tam_col[12]
				tam_col[13] = tam_letra* len(line.fechaemision if line.fechaemision else '') if tam_letra* len(line.fechaemision if line.fechaemision else '')> tam_col[13] else tam_col[13]
				tam_col[14] = tam_letra* len(line.fechavencimiento if line.fechavencimiento else '') if tam_letra* len(line.fechavencimiento if line.fechavencimiento else '')> tam_col[14] else tam_col[14]
				tam_col[15] = tam_letra* len(line.tipodocumento if line.tipodocumento else '') if tam_letra* len(line.tipodocumento if line.tipodocumento else '')> tam_col[15] else tam_col[15]
				tam_col[16] = tam_letra* len(line.numero if line.numero  else '') if tam_letra* len(line.numero if line.numero  else '')> tam_col[16] else tam_col[16]
				tam_col[17] = tam_letra* len(line.ruc if line.ruc  else '') if tam_letra* len(line.ruc if line.ruc  else '')> tam_col[17] else tam_col[17]
				tam_col[18] = tam_letra* len(line.partner if line.partner  else '') if tam_letra* len(line.partner if line.partner  else '')> tam_col[18] else tam_col[18]
				tam_col[19] = tam_letra* len(line.glosa if line.glosa else '') if tam_letra* len(line.glosa if line.glosa else '')> tam_col[19] else tam_col[19]

				x = x +1

			tam_col = [11,6,8.8,7.14,38,11,11,11,10,11,14,10,11,14,14,14,14,10,16,16,20,36]


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
			worksheet.set_column('V:V', tam_col[21])

			workbook.close()
			
			f = open(direccion + 'tempo_libromayor.xlsx', 'rb')
			
			
			sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
			vals = {
				'output_name': 'LibroMayor.xlsx',
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
		


class account_move_line_book_report_wizard(osv.TransientModel):
	_inherit='account.move.line.book.report.wizard'
	

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
			CREATE OR REPLACE view account_move_line_book_report as (
				SELECT * 
				FROM get_libro_diario("""+ str(currency)+ """,periodo_num('""" + period_ini.code + """'),periodo_num('""" + period_end.code +"""')) 
		)""")

		filtro.append( ('statefiltro','=','posted') )
		
		if self.type_show == 'pantalla':

			mod_obj = self.env['ir.model.data']
			act_obj = self.env['ir.actions.act_window']

			result = mod_obj.get_object_reference('account_contable_book_it', 'action_account_moves_all_report_it')
			id = result and result[1] or False
			print id
			
			return {
				'domain' : filtro,
				'type': 'ir.actions.act_window',
				'res_model': 'account.move.line.book.report',
				'view_mode': 'tree',
				'view_type': 'form',
				'res_id': id,
				'views': [(False, 'tree')],
			}



		if self.type_show == 'excel':

			import io
			from xlsxwriter.workbook import Workbook
			output = io.BytesIO()
			########### PRIMERA HOJA DE LA DATA EN TABLA
			#workbook = Workbook(output, {'in_memory': True})
			direccion = self.env['main.parameter'].search([])[0].dir_create_file
			workbook = Workbook( direccion + 'tempo_librodiario.xlsx')
			worksheet = workbook.add_worksheet("Libro Diario")
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
			tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			tam_letra = 1.2
			import sys
			reload(sys)
			sys.setdefaultencoding('iso-8859-1')

			worksheet.write(0,0, "Libro Diario:", bold)
			tam_col[0] = tam_letra* len("Libro Diario:") if tam_letra* len("Libro Diario:")> tam_col[0] else tam_col[0]

			worksheet.write(0,1, self.period_ini.name, normal)
			tam_col[1] = tam_letra* len(self.period_ini.name) if tam_letra* len(self.period_ini.name)> tam_col[1] else tam_col[1]

			worksheet.write(0,2, self.period_end.name, normal)
			tam_col[2] = tam_letra* len(self.period_end.name) if tam_letra* len(self.period_end.name)> tam_col[2] else tam_col[2]

			worksheet.write(1,0, "Fecha:",bold)
			tam_col[0] = tam_letra* len("Fecha:") if tam_letra* len("Fecha:")> tam_col[0] else tam_col[0]

			#worksheet.write(1,1, total.date.strftime('%Y-%m-%d %H:%M'),bord)
			import datetime
			worksheet.write(1,1, str(datetime.datetime.today())[:10], normal)
			tam_col[1] = tam_letra* len(str(datetime.datetime.today())[:10]) if tam_letra* len(str(datetime.datetime.today())[:10])> tam_col[1] else tam_col[1]
			

			worksheet.write(3,0, "Periodo",boldbord)
			tam_col[0] = tam_letra* len("Periodo") if tam_letra* len("Periodo")> tam_col[0] else tam_col[0]
			worksheet.write(3,1, "Libro",boldbord)
			tam_col[1] = tam_letra* len("Libro") if tam_letra* len("Libro")> tam_col[1] else tam_col[1]
			worksheet.write(3,2, "Voucher",boldbord)
			tam_col[2] = tam_letra* len("Voucher") if tam_letra* len("Voucher")> tam_col[2] else tam_col[2]
			worksheet.write(3,3, "Cuenta",boldbord)
			tam_col[3] = tam_letra* len("Cuenta") if tam_letra* len("Cuenta")> tam_col[3] else tam_col[3]
			worksheet.write(3,4, "Debe",boldbord)
			tam_col[4] = tam_letra* len("Debe") if tam_letra* len("Debe")> tam_col[4] else tam_col[4]
			worksheet.write(3,5, "Haber",boldbord)
			tam_col[5] = tam_letra* len("Haber") if tam_letra* len("Haber")> tam_col[5] else tam_col[5]
			worksheet.write(3,6, "Divisa",boldbord)
			tam_col[6] = tam_letra* len("Divisa") if tam_letra* len("Divisa")> tam_col[6] else tam_col[6]
			worksheet.write(3,7, "Tipo Cambio",boldbord)
			tam_col[7] = tam_letra* len("Tipo Cambio") if tam_letra* len("Tipo Cambio")> tam_col[7] else tam_col[7]
			worksheet.write(3,8, "Importe Divisa",boldbord)
			tam_col[8] = tam_letra* len("Importe Divisa") if tam_letra* len("Importe Divisa")> tam_col[8] else tam_col[8]
			worksheet.write(3,9, u"Código",boldbord)
			tam_col[9] = tam_letra* len(u"Código") if tam_letra* len(u"Código")> tam_col[9] else tam_col[9]
			worksheet.write(3,10, "Partner",boldbord)
			tam_col[10] = tam_letra* len("Partner") if tam_letra* len("Partner")> tam_col[10] else tam_col[10]
			worksheet.write(3,11, "Tipo Documento",boldbord)
			tam_col[11] = tam_letra* len("Tipo Documento") if tam_letra* len("Tipo Documento")> tam_col[11] else tam_col[11]
			worksheet.write(3,12, u"Número",boldbord)
			tam_col[12] = tam_letra* len(u"Número") if tam_letra* len(u"Número")> tam_col[12] else tam_col[12]
			worksheet.write(3,13, u"Fecha Emisión",boldbord)
			tam_col[13] = tam_letra* len(u"Fecha Emisión") if tam_letra* len(u"Fecha Emisión")> tam_col[13] else tam_col[13]
			worksheet.write(3,14, "Fecha Vencimiento",boldbord)
			tam_col[14] = tam_letra* len("Fecha Vencimiento") if tam_letra* len("Fecha Vencimiento")> tam_col[14] else tam_col[14]
			worksheet.write(3,15, "Glosa",boldbord)
			tam_col[15] = tam_letra* len("Glosa") if tam_letra* len("Glosa")> tam_col[15] else tam_col[15]
			worksheet.write(3,16, u"Cta. Analítica",boldbord)

			worksheet.write(3,17, u"Expediente Importación",boldbord)
			worksheet.write(3,18, u"Obras Curso",boldbord)

			tam_col[16] = tam_letra* len(u"Cta. Analítica") if tam_letra* len(u"Cta. Analítica")> tam_col[16] else tam_col[16]

			worksheet.write(3,19, u"Referencia Conciliación",boldbord)
			tam_col[17] = tam_letra* len(u"Referencia Conciliación") if tam_letra* len(u"Referencia Conciliación")> tam_col[17] else tam_col[17]

			worksheet.write(3,20, u"Estado",boldbord)
			tam_col[18] = tam_letra* len(u"Estado") if tam_letra* len(u"Estado")> tam_col[18] else tam_col[18]

			for line in self.env['account.move.line.book.report'].search(filtro):
				worksheet.write(x,0,line.periodo if line.periodo else '' ,bord )
				worksheet.write(x,1,line.libro if line.libro  else '',bord )
				worksheet.write(x,2,line.voucher if line.voucher  else '',bord)
				worksheet.write(x,3,line.cuenta if line.cuenta  else '',bord)
				worksheet.write(x,4,line.debe ,numberdos)
				worksheet.write(x,5,line.haber ,numberdos)
				worksheet.write(x,6,line.divisa if  line.divisa else '',bord)
				worksheet.write(x,7,line.tipodecambio ,numbertres)
				worksheet.write(x,8,line.importedivisa ,numberdos)
				worksheet.write(x,9,line.codigo if line.codigo else '',bord)
				worksheet.write(x,10,line.partner if line.partner else '',bord)
				worksheet.write(x,11,line.tipodocumento if line.tipodocumento else '',bord)
				worksheet.write(x,12,line.numero if line.numero  else '',bord)
				worksheet.write(x,13,line.fechaemision if line.fechaemision else '',bord)
				worksheet.write(x,14,line.fechavencimiento if line.fechavencimiento else '',bord)
				worksheet.write(x,15,line.glosa if line.glosa else '',bord)
				worksheet.write(x,16,line.ctaanalitica if line.ctaanalitica  else '',bord)

				worksheet.write(x,17,line.expediente_importacion if line.expediente_importacion  else '',bord)
				worksheet.write(x,18,line.obra_curso if line.obra_curso  else '',bord)

				worksheet.write(x,19,line.refconcil if line.refconcil  else '',bord)
				worksheet.write(x,20,line.state if line.state  else '',bord)

				tam_col[0] = tam_letra* len(line.periodo if line.periodo else '' ) if tam_letra* len(line.periodo if line.periodo else '' )> tam_col[0] else tam_col[0]
				tam_col[1] = tam_letra* len(line.libro if line.libro  else '') if tam_letra* len(line.libro if line.libro  else '')> tam_col[1] else tam_col[1]
				tam_col[2] = tam_letra* len(line.voucher if line.voucher  else '') if tam_letra* len(line.voucher if line.voucher  else '')> tam_col[2] else tam_col[2]
				tam_col[3] = tam_letra* len(line.cuenta if line.cuenta  else '') if tam_letra* len(line.cuenta if line.cuenta  else '')> tam_col[3] else tam_col[3]
				tam_col[4] = tam_letra* len("%0.2f"%line.debe ) if tam_letra* len("%0.2f"%line.debe )> tam_col[4] else tam_col[4]
				tam_col[5] = tam_letra* len("%0.2f"%line.haber ) if tam_letra* len("%0.2f"%line.haber )> tam_col[5] else tam_col[5]
				tam_col[6] = tam_letra* len(line.divisa if  line.divisa else '') if tam_letra* len(line.divisa if  line.divisa else '')> tam_col[6] else tam_col[6]
				tam_col[7] = tam_letra* len("%0.3f"%line.tipodecambio ) if tam_letra* len("%0.3f"%line.tipodecambio )> tam_col[7] else tam_col[7]
				tam_col[8] = tam_letra* len("%0.2f"%line.importedivisa ) if tam_letra* len("%0.2f"%line.importedivisa )> tam_col[8] else tam_col[8]
				tam_col[9] = tam_letra* len(line.codigo if line.codigo else '') if tam_letra* len(line.codigo if line.codigo else '')> tam_col[9] else tam_col[9]
				tam_col[10] = tam_letra* len(line.partner if line.partner else '') if tam_letra* len(line.partner if line.partner else '')> tam_col[10] else tam_col[10]
				tam_col[11] = tam_letra* len(line.tipodocumento if line.tipodocumento else '') if tam_letra* len(line.tipodocumento if line.tipodocumento else '')> tam_col[11] else tam_col[11]
				tam_col[12] = tam_letra* len(line.numero if line.numero  else '') if tam_letra* len(line.numero if line.numero  else '')> tam_col[12] else tam_col[12]
				tam_col[13] = tam_letra* len(line.fechaemision if line.fechaemision else '') if tam_letra* len(line.fechaemision if line.fechaemision else '')> tam_col[13] else tam_col[13]
				tam_col[14] = tam_letra* len(line.fechavencimiento if line.fechavencimiento else '') if tam_letra* len(line.fechavencimiento if line.fechavencimiento else '')> tam_col[14] else tam_col[14]
				tam_col[15] = tam_letra* len(line.glosa if line.glosa else '') if tam_letra* len(line.glosa if line.glosa else '')> tam_col[15] else tam_col[15]
				tam_col[16] = tam_letra* len(line.ctaanalitica if line.ctaanalitica  else '') if tam_letra* len(line.ctaanalitica if line.ctaanalitica  else '')> tam_col[16] else tam_col[16]
				tam_col[17] = tam_letra* len(line.refconcil if line.refconcil  else '') if tam_letra* len(line.refconcil if line.refconcil  else '')> tam_col[17] else tam_col[17]
				tam_col[18] = tam_letra* len(line.state if line.state  else '') if tam_letra* len(line.state if line.state  else '')> tam_col[18] else tam_col[18]
				x = x +1


			tam_col = [11.2,10,8.8,7.14,11,11,7,10,11,13,36,7.29,14.2,14,14,25,16,10,12,12,10,10]

			worksheet.set_row(3, 60)
			
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
			
			f = open( direccion + 'tempo_librodiario.xlsx', 'rb')
			
			
			sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
			vals = {
				'output_name': 'LibroDiario.xlsx',
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









class account_move_line_book_wizard(osv.TransientModel):
	_inherit='account.move.line.book.wizard'
	

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
			CREATE OR REPLACE view account_move_line_book as (
				SELECT * 
				FROM get_libro_diario("""+ str(currency)+ """,periodo_num('""" + period_ini.code + """'),periodo_num('""" + period_end.code +"""')) 
		)""")

		if self.asientos:
			if self.asientos == 'posted':
				filtro.append( ('statefiltro','=','posted') )
			if self.asientos == 'draft':
				filtro.append( ('statefiltro','=','draft') )
		
		if self.libros:
			libros_list = []
			for i in  self.libros:
				libros_list.append(i.code)
			filtro.append( ('libro','in',tuple(libros_list)) )
		
		if self.type_show == 'pantalla':
			mod_obj = self.env['ir.model.data']
			act_obj = self.env['ir.actions.act_window']

			result = mod_obj.get_object_reference('account_contable_book_it', 'action_account_moves_all_it')
			
			id = result and result[1] or False
			print id
			return {
				'domain' : filtro,
				'type': 'ir.actions.act_window',
				'res_model': 'account.move.line.book',
				'view_mode': 'tree',
				'view_type': 'form',
				'res_id': id,
				'views': [(False, 'tree')],
			}

		if self.type_show == 'excel':

			import io
			from xlsxwriter.workbook import Workbook
			output = io.BytesIO()
			########### PRIMERA HOJA DE LA DATA EN TABLA
			#workbook = Workbook(output, {'in_memory': True})
			direccion = self.env['main.parameter'].search([])[0].dir_create_file
			workbook = Workbook( direccion + 'tempo_librodiario.xlsx')
			worksheet = workbook.add_worksheet("Libro Diario")
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
			tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			tam_letra = 1.2
			import sys
			reload(sys)
			sys.setdefaultencoding('iso-8859-1')

			worksheet.write(0,0, "Libro Diario:", bold)
			tam_col[0] = tam_letra* len("Libro Diario:") if tam_letra* len("Libro Diario:")> tam_col[0] else tam_col[0]

			worksheet.write(0,1, self.period_ini.name, normal)
			tam_col[1] = tam_letra* len(self.period_ini.name) if tam_letra* len(self.period_ini.name)> tam_col[1] else tam_col[1]

			worksheet.write(0,2, self.period_end.name, normal)
			tam_col[2] = tam_letra* len(self.period_end.name) if tam_letra* len(self.period_end.name)> tam_col[2] else tam_col[2]

			worksheet.write(1,0, "Fecha:",bold)
			tam_col[0] = tam_letra* len("Fecha:") if tam_letra* len("Fecha:")> tam_col[0] else tam_col[0]

			#worksheet.write(1,1, total.date.strftime('%Y-%m-%d %H:%M'),bord)
			import datetime
			worksheet.write(1,1, str(datetime.datetime.today())[:10], normal)
			tam_col[1] = tam_letra* len(str(datetime.datetime.today())[:10]) if tam_letra* len(str(datetime.datetime.today())[:10])> tam_col[1] else tam_col[1]
			

			worksheet.write(3,0, "Periodo",boldbord)
			tam_col[0] = tam_letra* len("Periodo") if tam_letra* len("Periodo")> tam_col[0] else tam_col[0]
			worksheet.write(3,1, "Libro",boldbord)
			tam_col[1] = tam_letra* len("Libro") if tam_letra* len("Libro")> tam_col[1] else tam_col[1]
			worksheet.write(3,2, "Voucher",boldbord)
			tam_col[2] = tam_letra* len("Voucher") if tam_letra* len("Voucher")> tam_col[2] else tam_col[2]
			worksheet.write(3,3, "Cuenta",boldbord)
			tam_col[3] = tam_letra* len("Cuenta") if tam_letra* len("Cuenta")> tam_col[3] else tam_col[3]
			worksheet.write(3,4, "Debe",boldbord)
			tam_col[4] = tam_letra* len("Debe") if tam_letra* len("Debe")> tam_col[4] else tam_col[4]
			worksheet.write(3,5, "Haber",boldbord)
			tam_col[5] = tam_letra* len("Haber") if tam_letra* len("Haber")> tam_col[5] else tam_col[5]
			worksheet.write(3,6, "Divisa",boldbord)
			tam_col[6] = tam_letra* len("Divisa") if tam_letra* len("Divisa")> tam_col[6] else tam_col[6]
			worksheet.write(3,7, "Tipo Cambio",boldbord)
			tam_col[7] = tam_letra* len("Tipo Cambio") if tam_letra* len("Tipo Cambio")> tam_col[7] else tam_col[7]
			worksheet.write(3,8, "Importe Divisa",boldbord)
			tam_col[8] = tam_letra* len("Importe Divisa") if tam_letra* len("Importe Divisa")> tam_col[8] else tam_col[8]
			worksheet.write(3,9, u"Código",boldbord)
			tam_col[9] = tam_letra* len(u"Código") if tam_letra* len(u"Código")> tam_col[9] else tam_col[9]
			worksheet.write(3,10, "Partner",boldbord)
			tam_col[10] = tam_letra* len("Partner") if tam_letra* len("Partner")> tam_col[10] else tam_col[10]
			worksheet.write(3,11, "Tipo Documento",boldbord)
			tam_col[11] = tam_letra* len("Tipo Documento") if tam_letra* len("Tipo Documento")> tam_col[11] else tam_col[11]
			worksheet.write(3,12, u"Número",boldbord)
			tam_col[12] = tam_letra* len(u"Número") if tam_letra* len(u"Número")> tam_col[12] else tam_col[12]
			worksheet.write(3,13, u"Fecha Emisión",boldbord)
			tam_col[13] = tam_letra* len(u"Fecha Emisión") if tam_letra* len(u"Fecha Emisión")> tam_col[13] else tam_col[13]
			worksheet.write(3,14, "Fecha Vencimiento",boldbord)
			tam_col[14] = tam_letra* len("Fecha Vencimiento") if tam_letra* len("Fecha Vencimiento")> tam_col[14] else tam_col[14]
			worksheet.write(3,15, "Glosa",boldbord)
			tam_col[15] = tam_letra* len("Glosa") if tam_letra* len("Glosa")> tam_col[15] else tam_col[15]
			worksheet.write(3,16, u"Cta. Analítica",boldbord)

			worksheet.write(3,17, u"Expediente Importación",boldbord)
			worksheet.write(3,18, u"Obras Curso",boldbord)

			tam_col[16] = tam_letra* len(u"Cta. Analítica") if tam_letra* len(u"Cta. Analítica")> tam_col[16] else tam_col[16]
			worksheet.write(3,19, u"Referencia Conciliación",boldbord)
			tam_col[17] = tam_letra* len(u"Referencia Conciliación") if tam_letra* len(u"Referencia Conciliación")> tam_col[17] else tam_col[17]

			worksheet.write(3,20, u"Estado",boldbord)
			tam_col[18] = tam_letra* len(u"Estado") if tam_letra* len(u"Estado")> tam_col[18] else tam_col[18]

			for line in self.env['account.move.line.book'].search([]):
				worksheet.write(x,0,line.periodo if line.periodo else '' ,bord )
				worksheet.write(x,1,line.libro if line.libro  else '',bord )
				worksheet.write(x,2,line.voucher if line.voucher  else '',bord)
				worksheet.write(x,3,line.cuenta if line.cuenta  else '',bord)
				worksheet.write(x,4,line.debe ,numberdos)
				worksheet.write(x,5,line.haber ,numberdos)
				worksheet.write(x,6,line.divisa if  line.divisa else '',bord)
				worksheet.write(x,7,line.tipodecambio ,numbertres)
				worksheet.write(x,8,line.importedivisa ,numberdos)
				worksheet.write(x,9,line.codigo if line.codigo else '',bord)
				worksheet.write(x,10,line.partner if line.partner else '',bord)
				worksheet.write(x,11,line.tipodocumento if line.tipodocumento else '',bord)
				worksheet.write(x,12,line.numero if line.numero  else '',bord)
				worksheet.write(x,13,line.fechaemision if line.fechaemision else '',bord)
				worksheet.write(x,14,line.fechavencimiento if line.fechavencimiento else '',bord)
				worksheet.write(x,15,line.glosa if line.glosa else '',bord)
				worksheet.write(x,16,line.ctaanalitica if line.ctaanalitica  else '',bord)

				worksheet.write(x,17,line.expediente_importacion if line.expediente_importacion  else '',bord)
				worksheet.write(x,18,line.obra_curso if line.obra_curso  else '',bord)

				worksheet.write(x,19,line.refconcil if line.refconcil  else '',bord)
				worksheet.write(x,20,line.state if line.state  else '',bord)

				tam_col[0] = tam_letra* len(line.periodo if line.periodo else '' ) if tam_letra* len(line.periodo if line.periodo else '' )> tam_col[0] else tam_col[0]
				tam_col[1] = tam_letra* len(line.libro if line.libro  else '') if tam_letra* len(line.libro if line.libro  else '')> tam_col[1] else tam_col[1]
				tam_col[2] = tam_letra* len(line.voucher if line.voucher  else '') if tam_letra* len(line.voucher if line.voucher  else '')> tam_col[2] else tam_col[2]
				tam_col[3] = tam_letra* len(line.cuenta if line.cuenta  else '') if tam_letra* len(line.cuenta if line.cuenta  else '')> tam_col[3] else tam_col[3]
				tam_col[4] = tam_letra* len("%0.2f"%line.debe ) if tam_letra* len("%0.2f"%line.debe )> tam_col[4] else tam_col[4]
				tam_col[5] = tam_letra* len("%0.2f"%line.haber ) if tam_letra* len("%0.2f"%line.haber )> tam_col[5] else tam_col[5]
				tam_col[6] = tam_letra* len(line.divisa if  line.divisa else '') if tam_letra* len(line.divisa if  line.divisa else '')> tam_col[6] else tam_col[6]
				tam_col[7] = tam_letra* len("%0.3f"%line.tipodecambio ) if tam_letra* len("%0.3f"%line.tipodecambio )> tam_col[7] else tam_col[7]
				tam_col[8] = tam_letra* len("%0.2f"%line.importedivisa ) if tam_letra* len("%0.2f"%line.importedivisa )> tam_col[8] else tam_col[8]
				tam_col[9] = tam_letra* len(line.codigo if line.codigo else '') if tam_letra* len(line.codigo if line.codigo else '')> tam_col[9] else tam_col[9]
				tam_col[10] = tam_letra* len(line.partner if line.partner else '') if tam_letra* len(line.partner if line.partner else '')> tam_col[10] else tam_col[10]
				tam_col[11] = tam_letra* len(line.tipodocumento if line.tipodocumento else '') if tam_letra* len(line.tipodocumento if line.tipodocumento else '')> tam_col[11] else tam_col[11]
				tam_col[12] = tam_letra* len(line.numero if line.numero  else '') if tam_letra* len(line.numero if line.numero  else '')> tam_col[12] else tam_col[12]
				tam_col[13] = tam_letra* len(line.fechaemision if line.fechaemision else '') if tam_letra* len(line.fechaemision if line.fechaemision else '')> tam_col[13] else tam_col[13]
				tam_col[14] = tam_letra* len(line.fechavencimiento if line.fechavencimiento else '') if tam_letra* len(line.fechavencimiento if line.fechavencimiento else '')> tam_col[14] else tam_col[14]
				tam_col[15] = tam_letra* len(line.glosa if line.glosa else '') if tam_letra* len(line.glosa if line.glosa else '')> tam_col[15] else tam_col[15]
				tam_col[16] = tam_letra* len(line.ctaanalitica if line.ctaanalitica  else '') if tam_letra* len(line.ctaanalitica if line.ctaanalitica  else '')> tam_col[16] else tam_col[16]
				tam_col[17] = tam_letra* len(line.refconcil if line.refconcil  else '') if tam_letra* len(line.refconcil if line.refconcil  else '')> tam_col[17] else tam_col[17]
				tam_col[18] = tam_letra* len(line.state if line.state  else '') if tam_letra* len(line.state if line.state  else '')> tam_col[18] else tam_col[18]
				x = x +1


			tam_col = [11.2,10,8.8,7.14,11,11,7,10,11,13,36,7.29,14.2,14,14,25,16,10,12,12,10,10]

			worksheet.set_row(3, 60)
			
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
			
			f = open( direccion + 'tempo_librodiario.xlsx', 'rb')
			
			
			sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
			vals = {
				'output_name': 'LibroDiario.xlsx',
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




class account_analytic_book_major_mexico_wizard(osv.TransientModel):
	_inherit='account.analytic.book.major.mexico.wizard'


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
			CREATE OR REPLACE view account_analytic_book_major_mexico as (SELECT * FROM get_libro_mayor_mexico("""+ str(currency)+ """,periodo_num('""" + period_ini.code + """'),periodo_num('""" + period_end.code +"""')) 
		)""")

		if self.cuentas:
			libros_list = ["Saldo Inicial"]
			for i in  self.cuentas:
				libros_list.append(i.code)
			filtro.append( ('cuenta','in',tuple(libros_list)) )
		
		if self.type_show == 'pantalla':
			mod_obj = self.env['ir.model.data']
			act_obj = self.env['ir.actions.act_window']

			result = mod_obj.get_object_reference('account_analytic_bookmajor_mexico_it', 'action_account_analytic_book_major_mexico_it')
			
			id = result and result[1] or False
			print id
			return {
				'domain' : filtro,
				'type': 'ir.actions.act_window',
				'res_model': 'account.analytic.book.major.mexico',
				'view_mode': 'tree',
				'view_type': 'form',
				'res_id': id,
				'views': [(False, 'tree')],
			}
		
		if self.type_show == 'excel':

			import io
			from xlsxwriter.workbook import Workbook
			output = io.BytesIO()
			########### PRIMERA HOJA DE LA DATA EN TABLA
			#workbook = Workbook(output, {'in_memory': True})

			direccion = self.env['main.parameter'].search([])[0].dir_create_file

			workbook = Workbook(direccion +'tempo_libromayor.xlsx')
			worksheet = workbook.add_worksheet("Libro Mayor")
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

			worksheet.write(0,0, "Libro Mayor:", bold)
			tam_col[0] = tam_letra* len("Libro Mayor:") if tam_letra* len("Libro Mayor:")> tam_col[0] else tam_col[0]

			worksheet.write(0,1, self.period_ini.name, normal)
			tam_col[1] = tam_letra* len(self.period_ini.name) if tam_letra* len(self.period_ini.name)> tam_col[1] else tam_col[1]

			worksheet.write(0,2, self.period_end.name, normal)
			tam_col[2] = tam_letra* len(self.period_end.name) if tam_letra* len(self.period_end.name)> tam_col[2] else tam_col[2]

			worksheet.write(1,0, "Fecha:",bold)
			tam_col[0] = tam_letra* len("Fecha:") if tam_letra* len("Fecha:")> tam_col[0] else tam_col[0]

			#worksheet.write(1,1, total.date.strftime('%Y-%m-%d %H:%M'),bord)
			import datetime
			worksheet.write(1,1, str(datetime.datetime.today())[:10], normal)
			tam_col[1] = tam_letra* len(str(datetime.datetime.today())[:10]) if tam_letra* len(str(datetime.datetime.today())[:10])> tam_col[1] else tam_col[1]
			

			worksheet.write(3,0, "Periodo",boldbord)
			tam_col[0] = tam_letra* len("Periodo") if tam_letra* len("Periodo")> tam_col[0] else tam_col[0]
			worksheet.write(3,1, "Libro",boldbord)
			tam_col[1] = tam_letra* len("Libro") if tam_letra* len("Libro")> tam_col[1] else tam_col[1]
			worksheet.write(3,2, "Voucher",boldbord)
			tam_col[2] = tam_letra* len("Voucher") if tam_letra* len("Voucher")> tam_col[2] else tam_col[2]
			worksheet.write(3,3, "Cuenta",boldbord)
			tam_col[3] = tam_letra* len("Cuenta") if tam_letra* len("Cuenta")> tam_col[3] else tam_col[3]
			worksheet.write(3,4, u"Descripción",boldbord)
			tam_col[4] = tam_letra* len(u"Descripción") if tam_letra* len(u"Descripción")> tam_col[4] else tam_col[4]
			worksheet.write(3,5, "Debe",boldbord)
			tam_col[5] = tam_letra* len("Debe") if tam_letra* len("Debe")> tam_col[5] else tam_col[5]
			worksheet.write(3,6, "Haber",boldbord)
			tam_col[6] = tam_letra* len("Haber") if tam_letra* len("Haber")> tam_col[6] else tam_col[6]
			worksheet.write(3,7, "Saldo",boldbord)
			tam_col[7] = tam_letra* len("Saldo") if tam_letra* len("Saldo")> tam_col[7] else tam_col[7]
			worksheet.write(3,8, "Divisa",boldbord)
			tam_col[8] = tam_letra* len("Divisa") if tam_letra* len("Divisa")> tam_col[8] else tam_col[8]
			worksheet.write(3,9, "Tipo Cambio",boldbord)
			tam_col[9] = tam_letra* len("Tipo Cambio") if tam_letra* len("Tipo Cambio")> tam_col[9] else tam_col[9]
			worksheet.write(3,10, "Importe Divisa",boldbord)
			tam_col[10] = tam_letra* len("Importe Divisa") if tam_letra* len("Importe Divisa")> tam_col[10] else tam_col[10]
			worksheet.write(3,11, u"Conciliación",boldbord)
			tam_col[11] = tam_letra* len(u"Conciliación") if tam_letra* len(u"Conciliación")> tam_col[11] else tam_col[11]
			worksheet.write(3,12, u"Analítica",boldbord)

			worksheet.write(3,13, u"Expediente Importación",boldbord)
			worksheet.write(3,14, u"Obras Curso",boldbord)			

			tam_col[12] = tam_letra* len(u"Analítica") if tam_letra* len(u"Analítica")> tam_col[12] else tam_col[12]
			worksheet.write(3,15, u"Fecha Emisión",boldbord)
			tam_col[13] = tam_letra* len(u"Fecha Emisión") if tam_letra* len(u"Fecha Emisión")> tam_col[13] else tam_col[13]
			worksheet.write(3,16, "Fecha Vencimiento",boldbord)
			tam_col[14] = tam_letra* len("Fecha Vencimiento") if tam_letra* len("Fecha Vencimiento")> tam_col[14] else tam_col[14]
			worksheet.write(3,17, "Tipo Documento",boldbord)
			tam_col[15] = tam_letra* len("Tipo Documento") if tam_letra* len("Tipo Documento")> tam_col[15] else tam_col[15]
			worksheet.write(3,18, u"Número",boldbord)
			tam_col[16] = tam_letra* len(u"Número") if tam_letra* len(u"Número")> tam_col[16] else tam_col[16]
			worksheet.write(3,19, u"RUC",boldbord)
			tam_col[17] = tam_letra* len(u"RUC") if tam_letra* len(u"RUC")> tam_col[17] else tam_col[17]
			worksheet.write(3,20, u"Partner",boldbord)
			tam_col[18] = tam_letra* len(u"Partner") if tam_letra* len(u"Partner")> tam_col[18] else tam_col[18]
			worksheet.write(3,21, u"Glosa",boldbord)
			tam_col[19] = tam_letra* len(u"Glosa") if tam_letra* len(u"Glosa")> tam_col[19] else tam_col[19]

			for line in self.env['account.analytic.book.major.mexico'].search(filtro):
				worksheet.write(x,0,line.periodo if line.periodo else '' ,bord )
				worksheet.write(x,1,line.libro if line.libro  else '',bord )
				worksheet.write(x,2,line.voucher if line.voucher  else '',bord)
				worksheet.write(x,3,line.cuenta if line.cuenta  else '',bord)
				worksheet.write(x,4,line.descripcion if line.descripcion  else '',bord)
				worksheet.write(x,5,line.debe ,numberdos)
				worksheet.write(x,6,line.haber ,numberdos)
				worksheet.write(x,7,line.saldo ,numberdos)
				worksheet.write(x,8,line.divisa if  line.divisa else '',bord)
				worksheet.write(x,9,line.tipocambio ,numbertres)
				worksheet.write(x,10,line.importedivisa ,numberdos)
				worksheet.write(x,11,line.conciliacion if line.conciliacion else '',bord)
				worksheet.write(x,12,line.analitica if line.analitica else '',bord)

				worksheet.write(x,13,line.expediente_importacion if line.expediente_importacion else '',bord)
				worksheet.write(x,14,line.obra_curso if line.obra_curso else '',bord)

				worksheet.write(x,15,line.fechaemision if line.fechaemision else '',bord)
				worksheet.write(x,16,line.fechavencimiento if line.fechavencimiento else '',bord)
				worksheet.write(x,17,line.tipodocumento if line.tipodocumento else '',bord)
				worksheet.write(x,18,line.numero if line.numero  else '',bord)				
				worksheet.write(x,19,line.ruc if line.ruc  else '',bord)
				worksheet.write(x,20,line.partner if line.partner  else '',bord)
				worksheet.write(x,21,line.glosa if line.glosa else '',bord)

				tam_col[0] = tam_letra* len(line.periodo if line.periodo else '' ) if tam_letra* len(line.periodo if line.periodo else '' )> tam_col[0] else tam_col[0]
				tam_col[1] = tam_letra* len(line.libro if line.libro  else '') if tam_letra* len(line.libro if line.libro  else '')> tam_col[1] else tam_col[1]
				tam_col[2] = tam_letra* len(line.voucher if line.voucher  else '') if tam_letra* len(line.voucher if line.voucher  else '')> tam_col[2] else tam_col[2]
				tam_col[3] = tam_letra* len(line.cuenta if line.cuenta  else '') if tam_letra* len(line.cuenta if line.cuenta  else '')> tam_col[3] else tam_col[3]
				tam_col[4] = tam_letra* len(line.descripcion if line.descripcion  else '') if tam_letra* len(line.descripcion if line.descripcion  else '')> tam_col[4] else tam_col[4]
				tam_col[5] = tam_letra* len("%0.2f"%line.debe ) if tam_letra* len("%0.2f"%line.debe )> tam_col[5] else tam_col[5]
				tam_col[6] = tam_letra* len("%0.2f"%line.haber ) if tam_letra* len("%0.2f"%line.haber )> tam_col[6] else tam_col[6]
				tam_col[7] = tam_letra* len("%0.2f"%line.saldo ) if tam_letra* len("%0.2f"%line.saldo )> tam_col[7] else tam_col[7]
				tam_col[8] = tam_letra* len(line.divisa if  line.divisa else '') if tam_letra* len(line.divisa if  line.divisa else '')> tam_col[8] else tam_col[8]
				tam_col[9] = tam_letra* len("%0.3f"%line.tipocambio ) if tam_letra* len("%0.3f"%line.tipocambio )> tam_col[9] else tam_col[9]
				tam_col[10] = tam_letra* len("%0.2f"%line.importedivisa ) if tam_letra* len("%0.2f"%line.importedivisa )> tam_col[10] else tam_col[10]
				tam_col[11] = tam_letra* len(line.conciliacion if line.conciliacion else '') if tam_letra* len(line.conciliacion if line.conciliacion else '')> tam_col[11] else tam_col[11]
				tam_col[12] = tam_letra* len(line.analitica if line.analitica else '') if tam_letra* len(line.analitica if line.analitica else '')> tam_col[12] else tam_col[12]
				tam_col[13] = tam_letra* len(line.fechaemision if line.fechaemision else '') if tam_letra* len(line.fechaemision if line.fechaemision else '')> tam_col[13] else tam_col[13]
				tam_col[14] = tam_letra* len(line.fechavencimiento if line.fechavencimiento else '') if tam_letra* len(line.fechavencimiento if line.fechavencimiento else '')> tam_col[14] else tam_col[14]
				tam_col[15] = tam_letra* len(line.tipodocumento if line.tipodocumento else '') if tam_letra* len(line.tipodocumento if line.tipodocumento else '')> tam_col[15] else tam_col[15]
				tam_col[16] = tam_letra* len(line.numero if line.numero  else '') if tam_letra* len(line.numero if line.numero  else '')> tam_col[16] else tam_col[16]
				tam_col[17] = tam_letra* len(line.ruc if line.ruc  else '') if tam_letra* len(line.ruc if line.ruc  else '')> tam_col[17] else tam_col[17]
				tam_col[18] = tam_letra* len(line.partner if line.partner  else '') if tam_letra* len(line.partner if line.partner  else '')> tam_col[18] else tam_col[18]
				tam_col[19] = tam_letra* len(line.glosa if line.glosa else '') if tam_letra* len(line.glosa if line.glosa else '')> tam_col[19] else tam_col[19]

				x = x +1

			tam_col = [11,6,8.8,7.14,38,11,11,11,10,11,14,10,11,14,14,14,14,10,16,16,20,36]


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
			worksheet.set_column('V:V', tam_col[21])

			workbook.close()
			
			f = open(direccion + 'tempo_libromayor.xlsx', 'rb')
			
			
			sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
			vals = {
				'output_name': 'LibroMayor.xlsx',
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
		




class account_move_line_book_report_mexico_wizard(osv.TransientModel):
	_inherit='account.move.line.book.report.mexico.wizard'
	
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
			CREATE OR REPLACE view account_move_line_book_report_mexico as (
				SELECT * 
				FROM get_libro_diario_mexico("""+ str(currency)+ """,periodo_num('""" + period_ini.code + """'),periodo_num('""" + period_end.code +"""')) 
		)""")

		filtro.append( ('statefiltro','=','posted') )
		
		if self.type_show == 'pantalla':

			mod_obj = self.env['ir.model.data']
			act_obj = self.env['ir.actions.act_window']

			result = mod_obj.get_object_reference('account_contable_book_mexico_it', 'action_account_moves_all_report_mexico_it')
			id = result and result[1] or False
			print id
			
			return {
				'domain' : filtro,
				'type': 'ir.actions.act_window',
				'res_model': 'account.move.line.book.report.mexico',
				'view_mode': 'tree',
				'view_type': 'form',
				'res_id': id,
				'views': [(False, 'tree')],
			}



		if self.type_show == 'excel':

			import io
			from xlsxwriter.workbook import Workbook
			output = io.BytesIO()
			########### PRIMERA HOJA DE LA DATA EN TABLA
			#workbook = Workbook(output, {'in_memory': True})
			direccion = self.env['main.parameter'].search([])[0].dir_create_file
			workbook = Workbook( direccion + 'tempo_librodiario.xlsx')
			worksheet = workbook.add_worksheet("Libro Diario")
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
			tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			tam_letra = 1.2
			import sys
			reload(sys)
			sys.setdefaultencoding('iso-8859-1')

			worksheet.write(0,0, "Libro Diario:", bold)
			tam_col[0] = tam_letra* len("Libro Diario:") if tam_letra* len("Libro Diario:")> tam_col[0] else tam_col[0]

			worksheet.write(0,1, self.period_ini.name, normal)
			tam_col[1] = tam_letra* len(self.period_ini.name) if tam_letra* len(self.period_ini.name)> tam_col[1] else tam_col[1]

			worksheet.write(0,2, self.period_end.name, normal)
			tam_col[2] = tam_letra* len(self.period_end.name) if tam_letra* len(self.period_end.name)> tam_col[2] else tam_col[2]

			worksheet.write(1,0, "Fecha:",bold)
			tam_col[0] = tam_letra* len("Fecha:") if tam_letra* len("Fecha:")> tam_col[0] else tam_col[0]

			#worksheet.write(1,1, total.date.strftime('%Y-%m-%d %H:%M'),bord)
			import datetime
			worksheet.write(1,1, str(datetime.datetime.today())[:10], normal)
			tam_col[1] = tam_letra* len(str(datetime.datetime.today())[:10]) if tam_letra* len(str(datetime.datetime.today())[:10])> tam_col[1] else tam_col[1]
			

			worksheet.write(3,0, "Periodo",boldbord)
			tam_col[0] = tam_letra* len("Periodo") if tam_letra* len("Periodo")> tam_col[0] else tam_col[0]
			worksheet.write(3,1, "Libro",boldbord)
			tam_col[1] = tam_letra* len("Libro") if tam_letra* len("Libro")> tam_col[1] else tam_col[1]
			worksheet.write(3,2, "Voucher",boldbord)
			tam_col[2] = tam_letra* len("Voucher") if tam_letra* len("Voucher")> tam_col[2] else tam_col[2]
			worksheet.write(3,3, "Cuenta",boldbord)
			tam_col[3] = tam_letra* len("Cuenta") if tam_letra* len("Cuenta")> tam_col[3] else tam_col[3]
			worksheet.write(3,4, "Debe",boldbord)
			tam_col[4] = tam_letra* len("Debe") if tam_letra* len("Debe")> tam_col[4] else tam_col[4]
			worksheet.write(3,5, "Haber",boldbord)
			tam_col[5] = tam_letra* len("Haber") if tam_letra* len("Haber")> tam_col[5] else tam_col[5]
			worksheet.write(3,6, "Divisa",boldbord)
			tam_col[6] = tam_letra* len("Divisa") if tam_letra* len("Divisa")> tam_col[6] else tam_col[6]
			worksheet.write(3,7, "Tipo Cambio",boldbord)
			tam_col[7] = tam_letra* len("Tipo Cambio") if tam_letra* len("Tipo Cambio")> tam_col[7] else tam_col[7]
			worksheet.write(3,8, "Importe Divisa",boldbord)
			tam_col[8] = tam_letra* len("Importe Divisa") if tam_letra* len("Importe Divisa")> tam_col[8] else tam_col[8]
			worksheet.write(3,9, u"Código",boldbord)
			tam_col[9] = tam_letra* len(u"Código") if tam_letra* len(u"Código")> tam_col[9] else tam_col[9]
			worksheet.write(3,10, "Partner",boldbord)
			tam_col[10] = tam_letra* len("Partner") if tam_letra* len("Partner")> tam_col[10] else tam_col[10]
			worksheet.write(3,11, "Tipo Documento",boldbord)
			tam_col[11] = tam_letra* len("Tipo Documento") if tam_letra* len("Tipo Documento")> tam_col[11] else tam_col[11]
			worksheet.write(3,12, u"Número",boldbord)
			tam_col[12] = tam_letra* len(u"Número") if tam_letra* len(u"Número")> tam_col[12] else tam_col[12]
			worksheet.write(3,13, u"Fecha Emisión",boldbord)
			tam_col[13] = tam_letra* len(u"Fecha Emisión") if tam_letra* len(u"Fecha Emisión")> tam_col[13] else tam_col[13]
			worksheet.write(3,14, "Fecha Vencimiento",boldbord)
			tam_col[14] = tam_letra* len("Fecha Vencimiento") if tam_letra* len("Fecha Vencimiento")> tam_col[14] else tam_col[14]
			worksheet.write(3,15, "Glosa",boldbord)
			tam_col[15] = tam_letra* len("Glosa") if tam_letra* len("Glosa")> tam_col[15] else tam_col[15]
			worksheet.write(3,16, u"Cta. Analítica",boldbord)

			worksheet.write(3,17, u"Expediente Importación",boldbord)
			worksheet.write(3,18, u"Obras Curso",boldbord)			

			tam_col[16] = tam_letra* len(u"Cta. Analítica") if tam_letra* len(u"Cta. Analítica")> tam_col[16] else tam_col[16]
			worksheet.write(3,19, u"Referencia Conciliación",boldbord)
			tam_col[17] = tam_letra* len(u"Referencia Conciliación") if tam_letra* len(u"Referencia Conciliación")> tam_col[17] else tam_col[17]

			worksheet.write(3,20, u"Estado",boldbord)
			tam_col[18] = tam_letra* len(u"Estado") if tam_letra* len(u"Estado")> tam_col[18] else tam_col[18]

			for line in self.env['account.move.line.book.report.mexico'].search(filtro):
				worksheet.write(x,0,line.periodo if line.periodo else '' ,bord )
				worksheet.write(x,1,line.libro if line.libro  else '',bord )
				worksheet.write(x,2,line.voucher if line.voucher  else '',bord)
				worksheet.write(x,3,line.cuenta if line.cuenta  else '',bord)
				worksheet.write(x,4,line.debe ,numberdos)
				worksheet.write(x,5,line.haber ,numberdos)
				worksheet.write(x,6,line.divisa if  line.divisa else '',bord)
				worksheet.write(x,7,line.tipodecambio ,numbertres)
				worksheet.write(x,8,line.importedivisa ,numberdos)
				worksheet.write(x,9,line.codigo if line.codigo else '',bord)
				worksheet.write(x,10,line.partner if line.partner else '',bord)
				worksheet.write(x,11,line.tipodocumento if line.tipodocumento else '',bord)
				worksheet.write(x,12,line.numero if line.numero  else '',bord)
				worksheet.write(x,13,line.fechaemision if line.fechaemision else '',bord)
				worksheet.write(x,14,line.fechavencimiento if line.fechavencimiento else '',bord)
				worksheet.write(x,15,line.glosa if line.glosa else '',bord)
				worksheet.write(x,16,line.ctaanalitica if line.ctaanalitica  else '',bord)

				worksheet.write(x,17,line.expediente_importacion if line.expediente_importacion  else '',bord)
				worksheet.write(x,18,line.obra_curso if line.obra_curso  else '',bord)

				worksheet.write(x,19,line.refconcil if line.refconcil  else '',bord)
				worksheet.write(x,20,line.state if line.state  else '',bord)

				tam_col[0] = tam_letra* len(line.periodo if line.periodo else '' ) if tam_letra* len(line.periodo if line.periodo else '' )> tam_col[0] else tam_col[0]
				tam_col[1] = tam_letra* len(line.libro if line.libro  else '') if tam_letra* len(line.libro if line.libro  else '')> tam_col[1] else tam_col[1]
				tam_col[2] = tam_letra* len(line.voucher if line.voucher  else '') if tam_letra* len(line.voucher if line.voucher  else '')> tam_col[2] else tam_col[2]
				tam_col[3] = tam_letra* len(line.cuenta if line.cuenta  else '') if tam_letra* len(line.cuenta if line.cuenta  else '')> tam_col[3] else tam_col[3]
				tam_col[4] = tam_letra* len("%0.2f"%line.debe ) if tam_letra* len("%0.2f"%line.debe )> tam_col[4] else tam_col[4]
				tam_col[5] = tam_letra* len("%0.2f"%line.haber ) if tam_letra* len("%0.2f"%line.haber )> tam_col[5] else tam_col[5]
				tam_col[6] = tam_letra* len(line.divisa if  line.divisa else '') if tam_letra* len(line.divisa if  line.divisa else '')> tam_col[6] else tam_col[6]
				tam_col[7] = tam_letra* len("%0.3f"%line.tipodecambio ) if tam_letra* len("%0.3f"%line.tipodecambio )> tam_col[7] else tam_col[7]
				tam_col[8] = tam_letra* len("%0.2f"%line.importedivisa ) if tam_letra* len("%0.2f"%line.importedivisa )> tam_col[8] else tam_col[8]
				tam_col[9] = tam_letra* len(line.codigo if line.codigo else '') if tam_letra* len(line.codigo if line.codigo else '')> tam_col[9] else tam_col[9]
				tam_col[10] = tam_letra* len(line.partner if line.partner else '') if tam_letra* len(line.partner if line.partner else '')> tam_col[10] else tam_col[10]
				tam_col[11] = tam_letra* len(line.tipodocumento if line.tipodocumento else '') if tam_letra* len(line.tipodocumento if line.tipodocumento else '')> tam_col[11] else tam_col[11]
				tam_col[12] = tam_letra* len(line.numero if line.numero  else '') if tam_letra* len(line.numero if line.numero  else '')> tam_col[12] else tam_col[12]
				tam_col[13] = tam_letra* len(line.fechaemision if line.fechaemision else '') if tam_letra* len(line.fechaemision if line.fechaemision else '')> tam_col[13] else tam_col[13]
				tam_col[14] = tam_letra* len(line.fechavencimiento if line.fechavencimiento else '') if tam_letra* len(line.fechavencimiento if line.fechavencimiento else '')> tam_col[14] else tam_col[14]
				tam_col[15] = tam_letra* len(line.glosa if line.glosa else '') if tam_letra* len(line.glosa if line.glosa else '')> tam_col[15] else tam_col[15]
				tam_col[16] = tam_letra* len(line.ctaanalitica if line.ctaanalitica  else '') if tam_letra* len(line.ctaanalitica if line.ctaanalitica  else '')> tam_col[16] else tam_col[16]
				tam_col[17] = tam_letra* len(line.refconcil if line.refconcil  else '') if tam_letra* len(line.refconcil if line.refconcil  else '')> tam_col[17] else tam_col[17]
				tam_col[18] = tam_letra* len(line.state if line.state  else '') if tam_letra* len(line.state if line.state  else '')> tam_col[18] else tam_col[18]
				x = x +1


			tam_col = [11.2,10,8.8,7.14,11,11,7,10,11,13,36,7.29,14.2,14,14,25,16,10,12,12,10,10]

			worksheet.set_row(3, 60)
			
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
			
			f = open( direccion + 'tempo_librodiario.xlsx', 'rb')
			
			
			sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
			vals = {
				'output_name': 'LibroDiario.xlsx',
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




class account_move_line_book_mexico_wizard(osv.TransientModel):
	_inherit='account.move.line.book.mexico.wizard'
	

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
			CREATE OR REPLACE view account_move_line_book_mexico as (
				SELECT * 
				FROM get_libro_diario_mexico("""+ str(currency)+ """,periodo_num('""" + period_ini.code + """'),periodo_num('""" + period_end.code +"""')) 
		)""")

		if self.asientos:
			if self.asientos == 'posted':
				filtro.append( ('statefiltro','=','posted') )
			if self.asientos == 'draft':
				filtro.append( ('statefiltro','=','draft') )
		
		if self.libros:
			libros_list = []
			for i in  self.libros:
				libros_list.append(i.code)
			filtro.append( ('libro','in',tuple(libros_list)) )
		
		if self.type_show == 'pantalla':
			mod_obj = self.env['ir.model.data']
			act_obj = self.env['ir.actions.act_window']

			result = mod_obj.get_object_reference('account_contable_book_mexico_it', 'action_account_moves_all_mexico_it')
			
			id = result and result[1] or False

			print id
			return {
				'domain' : filtro,
				'type': 'ir.actions.act_window',
				'res_model': 'account.move.line.book.mexico',
				'view_mode': 'tree',
				'view_type': 'form',
				'res_id': id,
				'views': [(False, 'tree')],
			}

		if self.type_show == 'excel':

			import io
			from xlsxwriter.workbook import Workbook
			output = io.BytesIO()
			########### PRIMERA HOJA DE LA DATA EN TABLA
			#workbook = Workbook(output, {'in_memory': True})
			direccion = self.env['main.parameter'].search([])[0].dir_create_file
			workbook = Workbook( direccion + 'tempo_librodiario.xlsx')
			worksheet = workbook.add_worksheet("Libro Diario")
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
			tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			tam_letra = 1.2
			import sys
			reload(sys)
			sys.setdefaultencoding('iso-8859-1')

			worksheet.write(0,0, "Libro Diario:", bold)
			tam_col[0] = tam_letra* len("Libro Diario:") if tam_letra* len("Libro Diario:")> tam_col[0] else tam_col[0]

			worksheet.write(0,1, self.period_ini.name, normal)
			tam_col[1] = tam_letra* len(self.period_ini.name) if tam_letra* len(self.period_ini.name)> tam_col[1] else tam_col[1]

			worksheet.write(0,2, self.period_end.name, normal)
			tam_col[2] = tam_letra* len(self.period_end.name) if tam_letra* len(self.period_end.name)> tam_col[2] else tam_col[2]

			worksheet.write(1,0, "Fecha:",bold)
			tam_col[0] = tam_letra* len("Fecha:") if tam_letra* len("Fecha:")> tam_col[0] else tam_col[0]

			#worksheet.write(1,1, total.date.strftime('%Y-%m-%d %H:%M'),bord)
			import datetime
			worksheet.write(1,1, str(datetime.datetime.today())[:10], normal)
			tam_col[1] = tam_letra* len(str(datetime.datetime.today())[:10]) if tam_letra* len(str(datetime.datetime.today())[:10])> tam_col[1] else tam_col[1]
			

			worksheet.write(3,0, "Periodo",boldbord)
			tam_col[0] = tam_letra* len("Periodo") if tam_letra* len("Periodo")> tam_col[0] else tam_col[0]
			worksheet.write(3,1, "Libro",boldbord)
			tam_col[1] = tam_letra* len("Libro") if tam_letra* len("Libro")> tam_col[1] else tam_col[1]
			worksheet.write(3,2, "Voucher",boldbord)
			tam_col[2] = tam_letra* len("Voucher") if tam_letra* len("Voucher")> tam_col[2] else tam_col[2]
			worksheet.write(3,3, "Cuenta",boldbord)
			tam_col[3] = tam_letra* len("Cuenta") if tam_letra* len("Cuenta")> tam_col[3] else tam_col[3]
			worksheet.write(3,4, "Debe",boldbord)
			tam_col[4] = tam_letra* len("Debe") if tam_letra* len("Debe")> tam_col[4] else tam_col[4]
			worksheet.write(3,5, "Haber",boldbord)
			tam_col[5] = tam_letra* len("Haber") if tam_letra* len("Haber")> tam_col[5] else tam_col[5]
			worksheet.write(3,6, "Divisa",boldbord)
			tam_col[6] = tam_letra* len("Divisa") if tam_letra* len("Divisa")> tam_col[6] else tam_col[6]
			worksheet.write(3,7, "Tipo Cambio",boldbord)
			tam_col[7] = tam_letra* len("Tipo Cambio") if tam_letra* len("Tipo Cambio")> tam_col[7] else tam_col[7]
			worksheet.write(3,8, "Importe Divisa",boldbord)
			tam_col[8] = tam_letra* len("Importe Divisa") if tam_letra* len("Importe Divisa")> tam_col[8] else tam_col[8]
			worksheet.write(3,9, u"Código",boldbord)
			tam_col[9] = tam_letra* len(u"Código") if tam_letra* len(u"Código")> tam_col[9] else tam_col[9]
			worksheet.write(3,10, "Partner",boldbord)
			tam_col[10] = tam_letra* len("Partner") if tam_letra* len("Partner")> tam_col[10] else tam_col[10]
			worksheet.write(3,11, "Tipo Documento",boldbord)
			tam_col[11] = tam_letra* len("Tipo Documento") if tam_letra* len("Tipo Documento")> tam_col[11] else tam_col[11]
			worksheet.write(3,12, u"Número",boldbord)
			tam_col[12] = tam_letra* len(u"Número") if tam_letra* len(u"Número")> tam_col[12] else tam_col[12]
			worksheet.write(3,13, u"Fecha Emisión",boldbord)
			tam_col[13] = tam_letra* len(u"Fecha Emisión") if tam_letra* len(u"Fecha Emisión")> tam_col[13] else tam_col[13]
			worksheet.write(3,14, "Fecha Vencimiento",boldbord)
			tam_col[14] = tam_letra* len("Fecha Vencimiento") if tam_letra* len("Fecha Vencimiento")> tam_col[14] else tam_col[14]
			worksheet.write(3,15, "Glosa",boldbord)
			tam_col[15] = tam_letra* len("Glosa") if tam_letra* len("Glosa")> tam_col[15] else tam_col[15]
			worksheet.write(3,16, u"Cta. Analítica",boldbord)


			worksheet.write(3,17, u"Expediente Importación",boldbord)
			worksheet.write(3,18, u"Obras Curso",boldbord)

			tam_col[16] = tam_letra* len(u"Cta. Analítica") if tam_letra* len(u"Cta. Analítica")> tam_col[16] else tam_col[16]
			worksheet.write(3,19, u"Referencia Conciliación",boldbord)
			tam_col[17] = tam_letra* len(u"Referencia Conciliación") if tam_letra* len(u"Referencia Conciliación")> tam_col[17] else tam_col[17]

			worksheet.write(3,20, u"Estado",boldbord)
			tam_col[18] = tam_letra* len(u"Estado") if tam_letra* len(u"Estado")> tam_col[18] else tam_col[18]

			for line in self.env['account.move.line.book.mexico'].search([]):
				worksheet.write(x,0,line.periodo if line.periodo else '' ,bord )
				worksheet.write(x,1,line.libro if line.libro  else '',bord )
				worksheet.write(x,2,line.voucher if line.voucher  else '',bord)
				worksheet.write(x,3,line.cuenta if line.cuenta  else '',bord)
				worksheet.write(x,4,line.debe ,numberdos)
				worksheet.write(x,5,line.haber ,numberdos)
				worksheet.write(x,6,line.divisa if  line.divisa else '',bord)
				worksheet.write(x,7,line.tipodecambio ,numbertres)
				worksheet.write(x,8,line.importedivisa ,numberdos)
				worksheet.write(x,9,line.codigo if line.codigo else '',bord)
				worksheet.write(x,10,line.partner if line.partner else '',bord)
				worksheet.write(x,11,line.tipodocumento if line.tipodocumento else '',bord)
				worksheet.write(x,12,line.numero if line.numero  else '',bord)
				worksheet.write(x,13,line.fechaemision if line.fechaemision else '',bord)
				worksheet.write(x,14,line.fechavencimiento if line.fechavencimiento else '',bord)
				worksheet.write(x,15,line.glosa if line.glosa else '',bord)
				worksheet.write(x,16,line.ctaanalitica if line.ctaanalitica  else '',bord)

				worksheet.write(x,17,line.ctaanalitica if line.ctaanalitica  else '',bord)
				worksheet.write(x,18,line.ctaanalitica if line.ctaanalitica  else '',bord)

				worksheet.write(x,19,line.refconcil if line.refconcil  else '',bord)
				worksheet.write(x,20,line.state if line.state  else '',bord)

				tam_col[0] = tam_letra* len(line.periodo if line.periodo else '' ) if tam_letra* len(line.periodo if line.periodo else '' )> tam_col[0] else tam_col[0]
				tam_col[1] = tam_letra* len(line.libro if line.libro  else '') if tam_letra* len(line.libro if line.libro  else '')> tam_col[1] else tam_col[1]
				tam_col[2] = tam_letra* len(line.voucher if line.voucher  else '') if tam_letra* len(line.voucher if line.voucher  else '')> tam_col[2] else tam_col[2]
				tam_col[3] = tam_letra* len(line.cuenta if line.cuenta  else '') if tam_letra* len(line.cuenta if line.cuenta  else '')> tam_col[3] else tam_col[3]
				tam_col[4] = tam_letra* len("%0.2f"%line.debe ) if tam_letra* len("%0.2f"%line.debe )> tam_col[4] else tam_col[4]
				tam_col[5] = tam_letra* len("%0.2f"%line.haber ) if tam_letra* len("%0.2f"%line.haber )> tam_col[5] else tam_col[5]
				tam_col[6] = tam_letra* len(line.divisa if  line.divisa else '') if tam_letra* len(line.divisa if  line.divisa else '')> tam_col[6] else tam_col[6]
				tam_col[7] = tam_letra* len("%0.3f"%line.tipodecambio ) if tam_letra* len("%0.3f"%line.tipodecambio )> tam_col[7] else tam_col[7]
				tam_col[8] = tam_letra* len("%0.2f"%line.importedivisa ) if tam_letra* len("%0.2f"%line.importedivisa )> tam_col[8] else tam_col[8]
				tam_col[9] = tam_letra* len(line.codigo if line.codigo else '') if tam_letra* len(line.codigo if line.codigo else '')> tam_col[9] else tam_col[9]
				tam_col[10] = tam_letra* len(line.partner if line.partner else '') if tam_letra* len(line.partner if line.partner else '')> tam_col[10] else tam_col[10]
				tam_col[11] = tam_letra* len(line.tipodocumento if line.tipodocumento else '') if tam_letra* len(line.tipodocumento if line.tipodocumento else '')> tam_col[11] else tam_col[11]
				tam_col[12] = tam_letra* len(line.numero if line.numero  else '') if tam_letra* len(line.numero if line.numero  else '')> tam_col[12] else tam_col[12]
				tam_col[13] = tam_letra* len(line.fechaemision if line.fechaemision else '') if tam_letra* len(line.fechaemision if line.fechaemision else '')> tam_col[13] else tam_col[13]
				tam_col[14] = tam_letra* len(line.fechavencimiento if line.fechavencimiento else '') if tam_letra* len(line.fechavencimiento if line.fechavencimiento else '')> tam_col[14] else tam_col[14]
				tam_col[15] = tam_letra* len(line.glosa if line.glosa else '') if tam_letra* len(line.glosa if line.glosa else '')> tam_col[15] else tam_col[15]
				tam_col[16] = tam_letra* len(line.ctaanalitica if line.ctaanalitica  else '') if tam_letra* len(line.ctaanalitica if line.ctaanalitica  else '')> tam_col[16] else tam_col[16]
				tam_col[17] = tam_letra* len(line.refconcil if line.refconcil  else '') if tam_letra* len(line.refconcil if line.refconcil  else '')> tam_col[17] else tam_col[17]
				tam_col[18] = tam_letra* len(line.state if line.state  else '') if tam_letra* len(line.state if line.state  else '')> tam_col[18] else tam_col[18]
				x = x +1


			tam_col = [11.2,10,8.8,7.14,11,11,7,10,11,13,36,7.29,14.2,14,14,25,16,10,12,12,10,10]

			worksheet.set_row(3, 60)
			
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
			
			f = open( direccion + 'tempo_librodiario.xlsx', 'rb')
			
			
			sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
			vals = {
				'output_name': 'LibroDiario.xlsx',
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

