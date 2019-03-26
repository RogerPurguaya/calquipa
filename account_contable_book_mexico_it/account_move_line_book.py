# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_move_line_book_mexico(models.Model):
	_name = 'account.move.line.book.mexico'
	_auto = False

	statefiltro = fields.Char('StateFiltro',size=50)
	periodo= fields.Char('Periodo', size=50)
	libro= fields.Char('Libro', size=50)
	voucher= fields.Char('Voucher', size=50)
	cuenta= fields.Char('Cuenta', size=200)
	descripcion = fields.Char('Descripción',size=200)
	debe = fields.Float('Debe', digits=(12,2))
	haber = fields.Float('Haber', digits=(12,2))
	divisa= fields.Char('Divisa', size=50)
	tipodecambio  = fields.Float('Tipo Cambio', digits=(12,3))
	importedivisa  = fields.Float('Importe Divisa', digits=(12,2))
	codigo= fields.Char('Código', size=50)
	partner= fields.Char('Partner', size=50)
	tipodocumento= fields.Char('Tipo de Documento', size=50)
	numero= fields.Char('Número', size=50)
	fechaemision = fields.Date('Fecha Emisión')
	fechavencimiento = fields.Date('Fecha Vencimiento')
	glosa = fields.Char('Glosa', size=50)
	ctaanalitica= fields.Char('Cta. Analítica', size=50)
	refconcil= fields.Char('Referencia Conciliación', size=50)
	aml_id = fields.Many2one('account.move.line', 'aml id')
	aj_id = fields.Many2one('account.journal', 'journal id')
	ap_id = fields.Many2one('account.period','period id')
	am_id = fields.Many2one('account.move','move id')
	aa_id = fields.Many2one('account.account', 'account id')
	rc_id = fields.Many2one('res.currency', 'currency id')
	rp_id = fields.Many2one('res.partner' , 'partner id')
	itd_id = fields.Many2one('it.type.document', 'typo document id')
	aaa_id = fields.Many2one('account.analytic.account','analytic id')
	state = fields.Char('Estado',size=50)





class account_move_line_book_report_mexico(models.Model):
	_name = 'account.move.line.book.report.mexico'
	_auto = False

	statefiltro = fields.Char('StateFiltro',size=50)
	periodo= fields.Char('Periodo', size=50)
	libro= fields.Char('Libro', size=50)
	voucher= fields.Char('Voucher', size=50)
	cuenta= fields.Char('Cuenta', size=200)
	descripcion = fields.Char('Descripción',size=200)
	debe = fields.Float('Debe', digits=(12,2))
	haber = fields.Float('Haber', digits=(12,2))
	divisa= fields.Char('Divisa', size=50)
	tipodecambio  = fields.Float('Tipo Cambio', digits=(12,3))
	importedivisa  = fields.Float('Importe Divisa', digits=(12,2))
	codigo= fields.Char('Código', size=50)
	partner= fields.Char('Partner', size=50)
	tipodocumento= fields.Char('Tipo de Documento', size=50)
	numero= fields.Char('Número', size=50)
	fechaemision = fields.Date('Fecha Emisión')
	fechavencimiento = fields.Date('Fecha Vencimiento')
	glosa = fields.Char('Glosa', size=50)
	ctaanalitica= fields.Char('Cta. Analítica', size=50)
	refconcil= fields.Char('Referencia Conciliación', size=50)
	state = fields.Char('Estado',size=50)



class store_procedure_base_mexico(models.Model):
	_name = 'store.procedure.base.mexico'
	_auto = False

	def init(self,cr):


		librodiario = """ 
		DROP FUNCTION IF EXISTS get_libro_diario_mexico(boolean, integer, integer) cascade;
CREATE OR REPLACE FUNCTION get_libro_diario_mexico(IN has_currency boolean, IN periodo_ini integer, IN periodo_fin integer)
	RETURNS TABLE(id bigint, periodo varchar, libro varchar, voucher varchar, cuenta varchar, descripcion varchar, debe numeric, haber numeric, divisa varchar, tipodecambio numeric, importedivisa numeric, codigo varchar, partner varchar, tipodocumento varchar, numero varchar, fechaemision date, fechavencimiento date, glosa varchar, ctaanalitica varchar, refconcil varchar, statefiltro varchar, aml_id integer, aj_id integer, ap_id integer, am_id integer, aa_id integer, rc_id integer, rp_id integer, itd_id integer, aaa_id integer ,state varchar) AS
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
						case when am.state = 'posted'::varchar then 'Asentado'::varchar ELSE 'Borrador'::varchar END as state
					 FROM account_move_line aml
						 JOIN account_journal aj ON aj.id = aml.journal_id
						 JOIN account_period ap ON ap.id = aml.period_id
						 JOIN account_move am ON am.id = aml.move_id
						 JOIN account_account aa ON aa.id = aml.account_id
						 LEFT JOIN it_account_mexicana itm on itm.id = aa.code_mexicana
						 LEFT JOIN res_currency rc ON rc.id = aml.currency_id
						 LEFT JOIN res_partner rp ON rp.id = aml.partner_id
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


		libromayor = """
		DROP FUNCTION IF EXISTS get_libro_mayor_mexico(boolean, integer, integer) cascade;
CREATE OR REPLACE FUNCTION get_libro_mayor_mexico(IN has_currency boolean, IN periodo_ini integer, IN periodo_fin integer)
	RETURNS TABLE(id bigint ,periodo character varying, libro character varying, voucher character varying, cuenta character varying, descripcion character varying, debe numeric, haber numeric, divisa character varying, tipocambio numeric, importedivisa numeric, conciliacion character varying, fechaemision date, fechavencimiento date, tipodocumento character varying, numero character varying, ruc character varying, partner character varying, glosa character varying, analitica character varying, ordenamiento integer, cuentaname character varying, aml_id integer, state varchar) AS
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
										case when am.state = 'draft' then 'Borrador'::varchar else 'Asentado'::varchar END as state
									 FROM account_move_line aml
										 JOIN account_journal aj ON aml.journal_id = aj.id
										 JOIN account_move am ON aml.move_id = am.id
										 JOIN account_account aa ON aml.account_id = aa.id
										 JOIN account_period ap ON ap.id = aml.period_id

						 				LEFT JOIN it_account_mexicana itm on itm.id = aa.code_mexicana
										 LEFT JOIN res_currency rc ON aml.currency_id = rc.id
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
			 'Asentado'::varchar as state
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
		cr.execute(librodiario + libromayor)