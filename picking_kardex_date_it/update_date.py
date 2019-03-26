# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import models, fields, api
from datetime import datetime

class update_kardex_date(models.TransientModel):
	_name = 'update.kardex.date'

	start_date = fields.Date("Fecha Inicio")
	stop_date = fields.Date("Fecha Fin")
	show = fields.Boolean("Mostrar", default=False)

	@api.multi
	def show_pickings(self):
		picking_ids = self.env['stock.picking'].search([('date','>=',self.start_date),('date','<=',self.stop_date)])
		pickings = self.env['affected.pickings'].search([])
		for picking in pickings:
			picking.unlink()
		for picking in picking_ids:
			if picking.picking_type_id.name == 'Recepciones' and picking.invoice_id and picking.invoice_id.period_id and datetime.strptime(picking.date.split()[0], '%Y-%m-%d') > datetime.strptime(picking.invoice_id.period_id.date_stop, '%Y-%m-%d'):
				vals = {
					'picking_name'		: picking.name,
					'picking_date'		: picking.date,
					'invoice_name'		: picking.invoice_id.number,
					'invoice_date'		: picking.invoice_id.date_invoice,
					'use_kardex_date'	: picking.use_date,
				}
				self.env['affected.pickings'].create(vals)

		return {
			'name'			: 'Movimientos Afectados',
			'type'			: 'ir.actions.act_window',
			'view_type'		: 'tree',
			'view_mode'		: 'tree',
			'res_model'		: 'affected.pickings',
			'nodestroy'		: False,
			'target'		: 'current'
		}


	@api.one
	def update(self):
		picking_ids = self.env['stock.picking'].search([('date','>=',self.start_date),('date','<=',self.stop_date)])
		for picking in picking_ids:
			if picking.picking_type_id.name == 'Recepciones' and picking.invoice_id and picking.invoice_id.period_id and datetime.strptime(picking.date.split()[0], '%Y-%m-%d') > datetime.strptime(picking.invoice_id.period_id.date_stop, '%Y-%m-%d'):
				picking.use_date = True


class affected_pickings(models.TransientModel):
	_name = 'affected.pickings'

	picking_name = fields.Char("Movimiento")
	picking_date = fields.Date("Fecha Picking")
	invoice_name = fields.Char("Factura")
	invoice_date = fields.Date("Fecha Factura")
	use_kardex_date = fields.Boolean("Usar Fecha Kardex")