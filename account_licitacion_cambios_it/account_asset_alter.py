# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv


class stock_traceability(models.Model):
	_name = 'stock.traceability'
	_auto = False

	entrada = fields.Many2one('stock.location','Almacen Entrada')
	salida = fields.Many2one('stock.location','Almacen Salida')
	usuario = fields.Char('Usuario',size=100)
	licitacion = fields.Char('Licitación',size=100)
	fecha_licitacion = fields.Date('Fecha Licitación')
	state_licitacion = fields.Selection([('draft', 'Borrador'), ('in_progress', 'Confirmado'),
                                   ('open', 'Selección de Licitador'), ('done', 'Petición de Compra Creada'),
                                   ('cancel', 'Cancelado')],'Estado de Licitación')
	pedidocompra = fields.Char('Pedido de Compra',size=100)
	fechacompra = fields.Date('Fecha Pedido Compra')
	state_pedido = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Petición Presupuesto'),
        ('bid', 'Licitación Recibida'),
        ('confirmed', 'Esperando Aprobación'),
        ('approved', 'Compra Confirmada'),
        ('except_picking', 'Excepción de Envio'),
        ('except_invoice', 'Excepción de Factura'),
        ('done', 'Realizado'),
        ('cancel', 'Cancelado')
    ],'Estado de Pedido')
	notaingreso = fields.Char('Nota de Ingreso',size=100)
	usuarionotaingreso = fields.Char('Usuario de Nota de Ingreso',size=100)
	fechanotaingreso = fields.Date('Fecha Nota Ingreso')
	state_nota = fields.Selection([
                ('draft', 'Borrador'),
                ('cancel', 'Cancelado'),
                ('waiting', 'Esperando Operación'),
                ('confirmed', 'Esperando Disponibilidad'),
                ('partially_available', 'Disponibilidad Parcial'),
                ('assigned', 'Listo a Transferir'),
                ('done', 'Transferido'),
                ],'Estado de Nota Ingreso')
	factura = fields.Char('Factura')
	fechafactura = fields.Date('Fecha Factura')
	proveedor = fields.Char('Proveedor')
	state_factura = fields.Selection([
            ('draft','Borrador'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Abierto'),
            ('paid','Pagado'),
            ('cancel','Cancelado'),
        ],'Estado de Factura')

	licitacion_detalle = fields.Char('Tipo de Licitación')
	diarios = fields.Char('Diario de Pago')

	def init(self,cr):
		cr.execute(""" 
			drop view if exists stock_traceability;
			create or replace view stock_traceability as (
SELECT row_number() OVER () AS id,  
smm.location_id as entrada, smm.location_dest_id as salida ,
rp.name as usuario,
CASE WHEN sub_detalle_pr.verify_pr is Null then '' else CASE WHEN sub_detalle_pr.verify_pr = True THEN 'Servicios' else 'Bienes' END END as licitacion_detalle,
pr.name as licitacion,

pr.create_date as fecha_licitacion,
pr.state as state_licitacion,
po.name as pedidocompra,
po.date_order as fechacompra, 
po.state as state_pedido,
sp.name as notaingreso,
rpp.name  as usuarionotaingreso,sp.date as fechanotaingreso,
sp.state as state_nota,
ai.number as factura,
ai.date_invoice as fechafactura,rpi.name as proveedor ,  
ai.state as state_factura,
uniones.id_fin as diarios
from purchase_requisition pr
full join purchase_order po on po.requisition_id = pr.id
full join purchase_invoice_rel pir on pir.purchase_id = po.id
full join account_invoice ai on ai.id = pir.invoice_id
left join res_partner rpi on rpi.id = ai.partner_id
left join res_users ru on ru.id = pr.user_id
left join res_partner rp on rp.id = ru.partner_id
full join (SELECT picking_id, po.id FROM stock_picking p, stock_move m, purchase_order_line pol, purchase_order po
            WHERE po.id = pol.order_id and pol.id = m.purchase_line_id and m.picking_id = p.id
            GROUP BY picking_id, po.id) T on T.id = po.id
LEFT JOIN stock_picking sp on sp.id = T.picking_id
LEFT JOIN res_users rup on rup.id = sp.create_uid
LEFT JOIN res_partner rpp on rpp.id = rup.partner_id
LEFT JOIN stock_move smm on smm.picking_id = sp.id
LEFT JOIN (select prl.requisition_id as pr_id, every(pt.type = 'service') as verify_pr ,string_agg(pt.type,',') as type_products from purchase_requisition_line prl
left join product_product pp on pp.id = prl.product_id
left join product_template pt on pt.id = pp.product_tmpl_id

group by requisition_id)sub_detalle_pr on sub_detalle_pr.pr_id = pr.id 

inner join account_move am on am.id = ai.move_id
inner join account_move_line aml on am.id = aml.move_id  and aml.account_id = ai.account_id 
left join (
select aml.id as id_ini, string_agg(distinct aj.name::varchar || (CASE WHEN dtp.id is null and sca.id is null THEN '' else ':' || (CASE WHEN dtp.id is not null THEN dtp.name ELSE sca.name END) END   ) ,',') as id_fin from account_move_line aml
inner join account_move_line amla on (amla.reconcile_id = aml.reconcile_id or amla.reconcile_partial_id = aml.reconcile_partial_id) and aml.id != amla.id
inner join account_move amp on amp.id = amla.move_id
inner join account_voucher av on av.move_id = amp.id
inner join account_journal aj on aj.id = av.journal_id
left join deliveries_to_pay dtp on av.rendicion = dtp.id
left join small_cash_another sca on sca.id = av.small_cash
group by aml.id
) uniones on uniones.id_ini = aml.id
group by  uniones.id_fin,sub_detalle_pr.verify_pr,pr.state, po.state, sp.state, ai.state, smm.location_id  , smm.location_dest_id  ,rp.name  ,pr.name  ,pr.create_date  ,po.name  ,po.date_order  , sp.name  ,rpp.name   ,sp.date  ,ai.number  ,ai.date_invoice  ,rpi.name  

            )


			""")