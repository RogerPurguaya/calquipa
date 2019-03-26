# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions , _


class account_move_line(models.Model):
	_inherit = 'account.move.line'
	type_document_id = fields.Many2one('it.type.document', string="Tipo de Documento",index=True,ondelete='restrict')
	nro_comprobante = fields.Char('Comprobante', size=30)


