# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv


class licitacion_traceability(models.Model):
	_name = 'licitacion.traceability'
	_auto = False

	lici_id = fields.Many2one('purchase.requisition',u'Licitación')
	name_sec = fields.Char('Referencia')
	responsable = fields.Many2one('res.users','Responsable')
	fecha = fields.Date('Fecha Creación')
	state_licitacion = fields.Selection([('draft', 'Borrador'), ('in_progress', 'Confirmado'),
							('open', 'Selección de Licitador'), ('done', 'Petición de Compra Creada'),
							('cancel', 'Cancelado')],'Estado de Licitación' )

	lici_line_id = fields.Many2one('purchase.requisition.line','Lineas')
	producto = fields.Many2one('product.product','Producto')
	tipo_producto = fields.Selection([
		('product', 'Almacenable'),
		('consu', 'Consumible'),
		('service', 'Servicio')
	],'Tipo Producto')
	cantidad = fields.Float('Cantidad',related='lici_line_id.product_qty')
	unidad = fields.Many2one('product.uom','Unidad',related='lici_line_id.product_uom_id')


	def init(self,cr):
		cr.execute(""" 
			drop view if exists licitacion_traceability;
			create or replace view licitacion_traceability as (
SELECT row_number() OVER () AS id, * from ( 
select 
pr.id as lici_id, prl.id as lici_line_id, pr.create_date as fecha,
pr.name_sec as name_sec, pr.user_id as responsable, pr.state as state_licitacion, prl.product_id as producto,pt.type as tipo_producto
from purchase_requisition pr
inner join purchase_requisition_line prl on pr.id = prl.requisition_id
left join product_product pp on pp.id = prl.product_id
left join product_template pt on pt.id = pp.product_tmpl_id
order by  pr.id,prl.id ) as T
            )


			""")