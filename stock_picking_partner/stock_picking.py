# -*- encoding: utf-8 -*-
import pprint

from openerp import fields, models, api, _
from openerp.osv import osv

class stock_picking(models.Model):
	_inherit='stock.picking'

	partner_require_id = fields.Many2one('res.partner', 'Solicitado por', domain=[('employee', '=', True)])
	partner_deliver_id = fields.Many2one('res.partner', 'Entregado a', domain=[('employee', '=', True)])

	documento_partner = fields.Char('Documento Proveedor',size=200)
