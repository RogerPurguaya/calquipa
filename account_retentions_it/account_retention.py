# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import models, fields, api

class account_retention(models.Model):
	_name = 'account.retention'
	_auto = False
	
	periodo = fields.Char('Periodo', size=50)
	ruc_proveedor = fields.Char('Ruc Proveedor', size=50)
	razon_social = fields.Char('Razon Social', size=255)
	apellido_paterno = fields.Char('A. Paterno', size=255)
	apellido_materno = fields.Char('A. Materno', size=255)
	nombres = fields.Char('Nombres', size=255)
	serie = fields.Char('Serie', size=50)
	numero = fields.Char('Numero', size=50)
	fecha_emision = fields.Date('F. Emision')
	monto_retention = fields.Float('Monto Ret.', digits=(12,2))
	tipo_doc = fields.Char('T.D.', size=50)
	serie_doc = fields.Char('Serie D.', size=50)
	numero_doc = fields.Char('Numero D.', size=50)
	fecha_doc = fields.Date('F. Doc')
	total_doc = fields.Float('Total Doc.', digits=(12,2))
	
	def init(self,cr):
		cr.execute("""
			DROP FUNCTION IF EXISTS get_retentions(integer) CASCADE;

			CREATE OR REPLACE FUNCTION get_retentions(IN periodo_ini integer)
			  RETURNS TABLE(id bigint, periodo character varying, ruc_proveedor character varying, razon_social character varying, apellido_paterno character varying, apellido_materno character varying, nombres character varying, serie character varying, numero character varying, fecha_emision date, monto_retention numeric, tipo_doc character varying, serie_doc character varying, numero_doc character varying, fecha_doc date, total_doc numeric) AS
			$BODY$
			BEGIN

			RETURN QUERY 
				SELECT row_number() OVER () AS id,* from (

				SELECT 
					ap.code as periodo,
					rp.type_number as ruc_proveedor,
					rp.name as razon_social,
					rp.last_name_f as apellido_paterno,
					rp.last_name_m as apellido_materno,
					rp.first_name as nombres,
					split_part(am.ref, '-', 1)::character varying as serie,
					split_part(am.ref, '-', 2)::character varying as numero,
					am.date::date as fecha_emision,
					am.com_ret_amount as monto_retention,
					td.code as tipo_doc,
					split_part(aml.nro_comprobante, '-', 1)::character varying as serie_doc,
					split_part(aml.nro_comprobante, '-', 2)::character varying as numero_doc,
					ai.date_invoice as fecha_doc,
					ai.amount_total as total_doc
				FROM 
					account_move_line AS aml JOIN
					account_move AS am ON aml.move_id = am.id JOIN
					account_period AS ap ON am.period_id = ap.id JOIN
					account_journal AS aj ON aml.journal_id = aj.id LEFT JOIN
					it_type_document AS td ON aml.type_document_id = td.id JOIN
					account_invoice AS ai ON ai.supplier_invoice_number = aml.nro_comprobante JOIN
					res_partner AS rp ON rp.id = ai.partner_id

				WHERE
					aj.is_retention = True AND
					periodo_num(ap.name) = $1

				ORDER BY ap.code,ai.date_invoice,am.date
				) AS T; 
			END;
			$BODY$
			  LANGUAGE plpgsql VOLATILE
			  COST 100
			  ROWS 1000;
			ALTER FUNCTION get_retentions(integer)
			  OWNER TO postgres;
		""")