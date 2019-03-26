# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import models, fields, api

import datetime

class stock_picking(models.Model):
	_inherit = 'stock.picking'

	@api.multi
	def fusionar(self):
		if len(self) < 2:
			raise osv.except_osv('Alerta!', u"Seleccione 2 o más albaranes para juntar.")

		msg_state = ""
		for picking in self:
			if picking.state != 'draft':
				msg_state += picking.name + " -> " + picking.state + "\n"

		if len(msg_state) > 0:
			raise osv.except_osv('Alerta!', u"Todos los albaranes saleccionados deben estar en estado 'Borrador'.\n"+"Albaran -> Estado\n"+msg_state)

		check_tipo_op = False
		check_motivo_guia = False
		check_date = False
		check_partner = False

		tmp_tipo_op = self[0].picking_type_id.id
		tmp_motivo_guia = self[0].motivo_guia
		tmp_date = datetime.datetime.strftime(datetime.datetime.strptime(self[0].date, "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d")
		tmp_partner = self[0].partner_id.id

		for i in range(1,len(self)):
			if self[i].picking_type_id.id != tmp_tipo_op:
				check_tipo_op = True
			if self[i].motivo_guia != tmp_motivo_guia:
				check_motivo_guia = True
			if datetime.datetime.strftime(datetime.datetime.strptime(self[i].date,"%Y-%m-%d %H:%M:%S"), "%Y-%m-%d") != tmp_date:
				check_date = True
			if self[i].partner_id.id != tmp_partner:
				check_partner = True

		msg_error = ""
		if check_tipo_op or check_motivo_guia or check_date or check_partner:
			for picking in self:
				msg_error += picking.name + " - " + (picking.picking_type_id.name if check_tipo_op else '') + " - " + (picking.motivo_guia if check_motivo_guia and picking.motivo_guia else '') + " - " + (datetime.datetime.strftime(datetime.datetime.strptime(picking.date,"%Y-%m-%d %H:%M:%S"), "%Y-%m-%d") if check_date else '') + " - " + (picking.partner_id.name if check_partner and picking.partner_id else '') + "\n"

		if len(msg_error) > 0:
			campos_error = []
			campos_error.append(u"Tipo de albarán") if check_tipo_op else False
			campos_error.append(u"Motivo guía") if check_motivo_guia else False
			campos_error.append(u"Fecha") if check_date else False
			campos_error.append(u"Empresa") if check_partner else False

			raise osv.except_osv('Alerta!', u"Todos los albaranes seleccionados deben tener las mismas características.\n"+u"Albarán - "+ ' - '.join(campos_error) + "\n" + msg_error)
		else:
			tmp_date = datetime.datetime.strptime(tmp_date,"%Y-%m-%d")
			tmp_date += datetime.timedelta(hours=5)
			vals = {
				'picking_type_id': tmp_tipo_op,
				'motivo_guia': tmp_motivo_guia,
				'date': tmp_date,
				'partner_id': tmp_partner,
			}
			sp = self.env['stock.picking'].create(vals)

			prod = {}
			for picking in self:
				for move in picking.move_lines:
					if move.product_id.id not in prod:
						prod[move.product_id.id] = {
							'product_id': move.product_id.id,
							'name': move.name,
							'price_unit': move.price_unit,
							'analitic_id': move.analitic_id.id,
							'product_uom_qty': move.product_uom_qty,
							'product_uom': move.product_uom.id,
							'location_id': move.location_id.id,
							'location_dest_id': move.location_dest_id.id,
							'invoice_id': move.invoice_id.id,
							'picking_id': sp.id,
						}
					else:
						prod[move.product_id.id]['product_uom_qty'] += move.product_uom_qty
					move.unlink()
				picking.unlink()

			for k,v in prod.items():
				sm = self.env['stock.move'].create(v)