# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64

class account_move(models.Model):
	_inherit = 'account.move'

	dec_rec_type_document_it = fields.Many2one(readonly=0)
	dec_reg_nro_comprobante = fields.Char(readonly=0)
	dec_reg_nro_comprobante_ant = fields.Char('Comprobante Anterior', size=30, readonly=1)