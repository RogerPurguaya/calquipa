# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import models, fields, api

class pdb_currency_rate(models.Model):
	_name = 'pdb.currency.rate'
	_auto = False
	
	periodo = fields.Char('Periodo', size=50)
	tipo = fields.Char('Tipo', size=50)
	fecha = fields.Date('Fecha')
	compra = fields.Float('Compra', digits=(12,2))
	venta = fields.Float('Venta', digits=(12,2))
	
	
	def init(self,cr):
		cr.execute("""
			DROP FUNCTION IF EXISTS get_currency_rates(integer) CASCADE;
			CREATE OR REPLACE FUNCTION get_currency_rates(IN periodo_ini integer)
			  RETURNS TABLE(
				id bigint, 
				periodo character varying, 
				tipo character varying, 
				fecha date, 
				compra numeric, 
				venta numeric
				) 
			AS
			$BODY$
			BEGIN

			RETURN QUERY 
			SELECT row_number() OVER () AS id,* from 
			(
				(
				SELECT DISTINCT
					ap.name,
					ai.type,
					ai.date_invoice,
					rcr.type_sale,
					rcr.type_purchase
				FROM
					account_invoice AS ai JOIN
					res_currency AS rc ON ai.currency_id = rc.id JOIN
					res_company AS rcp ON ai.company_id = rcp.id JOIN
					res_currency_rate AS rcr ON rcr.currency_id = rc.id JOIN
					account_period AS ap ON ai.period_id = ap.id
				WHERE
					rcp.currency_id != ai.currency_id AND
					rcr.date_sunat = ai.date_invoice AND
					ai.state in ('paid','open') AND
					periodo_num(ap.name) = 201501
				) 

				UNION ALL
				(
					SELECT 
						ap.name,
						ai.type,
						ai.date_invoice,
						rcr.type_sale,
						rcr.type_purchase
					FROM 
						account_invoice AS ai JOIN
						res_currency AS rc ON ai.currency_id = rc.id JOIN
						res_company AS rcp ON ai.company_id = rcp.id JOIN
						res_currency_rate AS rcr ON rcr.currency_id = rc.id JOIN
						account_period AS ap ON ai.period_id = ap.id JOIN
						(
							SELECT 
								apc.father_invoice_id ,
								apc.comprobante AS nro_comprobante,
								apc.clienteproveedor AS cliente,
								apc.fecha AS fecha,
								apc.tipo_doc as tipo_doc
							FROM
								account_perception AS apc
							WHERE
								apc.father_invoice_id in 
								(
									SELECT 
										aii.id 
									FROM 
										account_invoice AS aii JOIN
										account_period AS app ON aii.period_id = app.id
									WHERE periodo_num(app.name) = 201501 AND aii.state in ('paid','open')
								)

						) 
					AS K ON ai.supplier_invoice_number = K.nro_comprobante AND ai.partner_id = K.cliente AND ai.type_document_id = K.tipo_doc 
					WHERE 
						rcp.currency_id != ai.currency_id AND
						rcr.date_sunat = ai.date_invoice AND
						ai.state in ('paid','open')
					)

				ORDER BY
					date_invoice
			) AS T;	

	END;
	$BODY$
	  LANGUAGE plpgsql VOLATILE
	  COST 100
	  ROWS 1000;

  """)
	