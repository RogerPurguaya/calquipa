# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import models, fields, api

class main_parameter(models.Model):
	_inherit = 'main.parameter'
	
	partner_sunat = fields.Many2one('res.partner', 'Partner Sunat')
	retention_document_type = fields.Many2one('it.type.document', 'Documento Retenciones')
	tax_code_id = fields.Many2one('account.tax.code', 'Impuesto Retenciones')