# -*- coding: utf-8 -*-

from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs

import datetime

class stock_move_clean_wizard(models.TransientModel):
	_name = 'stock.move.clean.wizard'

	aviso = fields.Char('Aviso', default="¿Estas seguro de eliminar?. Se eliminarán los productos en estado de espera")

	@api.multi
	def do_rebuild(self):
		sp = self.env['stock.picking'].search([('id','=',self.env.context['clean_id'])])[0]
		print sp
		return sp.clean_confirmed_action()

class stock_move(models.Model):
	_inherit='stock.move'

	@api.one
	def compute_disponibilidad(self):
		fecha_k = datetime.datetime.strptime(self.picking_id.date, "%Y-%m-%d %H:%M:%S")

		mnth = "%2d"%fecha_k.month
		mnth = mnth.replace(' ','0')
		fecha_query = "{0}-{1}-{2}".format(fecha_k.year, mnth, fecha_k.day)
		fecha_query = str(fecha_query)

		if self.location_id.usage == 'internal':
			self.env.cr.execute("""
			select sum(qty) as qty
			from vst_existencias_dispo
			where location_id = """ + str(self.location_id.id) + """ and product_id = """ + str (self.product_id.id) +
			""" and date_picking <= '""" + fecha_query + """'
			""")
			res = self.env.cr.fetchall()[0]
			self.disponibilidad = res[0]
	disponibilidad = fields.Float('Disponibilidad', compute="compute_disponibilidad")

	@api.one
	def write(self, vals):
		t = super(stock_move,self).write(vals)
		self.refresh()
		if 'product_uom_qty' in vals:
			self.write({'state':'confirmed'})
		return t



class stock_picking(models.Model):
	_inherit = 'stock.picking'

	@api.one
	def get_forzar_disponibilidad(self):
		all_groups=self.env['res.groups']
		all_users =self.env['res.users']
		
		g1_ids = all_groups.search([('name','=',u'Permite Utilizar Forzar Disponibilidad')])

		if not g1_ids: 
			raise osv.except_osv('Alerta!', "No existe el grupo 'Editar Cuenta, Analítica y Diario' creada.")

		if self.state == 'draft' or self.state == 'confirmed' or self.state == 'partially_available':
			if not g1_ids in all_users.search([('id','=',self.env.uid)])[0].groups_id:
				self.forzar = False
			else:
				self.forzar = True

			print self.forzar
	forzar = fields.Boolean('Forzar Disponibilidad', compute="get_forzar_disponibilidad")

	@api.one
	def get_disponibilidad(self):		
		fecha_k = datetime.datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S")

		mnth = "%2d"%fecha_k.month
		mnth = mnth.replace(' ','0')
		fecha_query = "{0}-{1}-{2}".format(fecha_k.year, mnth, fecha_k.day)
		fecha_query = str(fecha_query)

		for i in self.move_lines:

			if i.location_id.usage == 'internal':
				self.env.cr.execute("""
				select sum(qty) as qty
				from vst_existencias_dispo
				where location_id = """ + str(i.location_id.id) + """ and product_id = """ + str (i.product_id.id) +
				""" and date_picking <= '""" + fecha_query + """'
				""")

				res = self.env.cr.fetchall()[0]
				print self.move_lines, i.location_id.id, i.product_id.id, i.product_uom_qty, res[0], "aa", res

				#i.disponibilidad = res[0]

				if i.product_uom_qty <= i.disponibilidad:
					i.state = 'assigned'
				else:
					raise osv.except_osv('Alerta!', 'La cantidad solicitada del producto '+i.product_id.name+' es '+str(i.product_uom_qty)+', y es mayor a su disponibilidad')
			else:
				i.state = 'assigned'

	@api.multi
	def clean_confirmed(self):
		return {
			"context": {"clean_id": self.id},
			"type": "ir.actions.act_window",
			"res_model": "stock.move.clean.wizard",
			"view_type": "form",
			"view_mode": "form",
			"target": "new",
		}

	@api.one
	def clean_confirmed_action(self):
		for i in self.move_lines:
			if i.state != 'assigned':
				i.state = 'draft'
				i.unlink()


class stock_transfer_details(models.TransientModel):
	_inherit = 'stock.transfer_details'

	stock_picking_id = fields.Many2one('stock.picking','id picking')

	@api.multi
	def wizard_view(self):
		if 'active_model' in self.env.context and 'active_id' in self.env.context:
			if self.env.context['active_model'] == 'stock.picking':
				self.write({'stock_picking_id':self.env.context['active_id']})
		t = super(stock_transfer_details,self).wizard_view()
		return t

	@api.one
	def do_detailed_transfer(self):
		sp = self.stock_picking_id if self.stock_picking_id.id else self.env.context['active_id']

		prod = set()
		for i in sp.move_lines:
			prod.add(i.name)
		prod_dispon = dict.fromkeys(list(prod),0)
		for i in sp.move_lines:
			prod_dispon[i.name] += i.product_uom_qty + i.disponibilidad

		print prod_dispon

		for i in self.item_ids:
			sm = self.env['stock.move'].search([('picking_id','=',sp.id),('product_id','=',i.product_id.id)])
			if len(sm) > 0:
				prod_dispon[sm[0].name] -= i.quantity

		print prod_dispon

		#for k,v in prod_dispon.items():
		#	if v < 0:
		#	
		#		#raise osv.except_osv('Alerta!', 'El producto '+k+' no tiene disponible la cantidad solicitada '+str(v))
		return super(stock_transfer_details,self).do_detailed_transfer()