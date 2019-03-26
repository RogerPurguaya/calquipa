# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_purchase_register_nodeducible(models.Model):
	_name = 'account.purchase.register.nodeducible'
	_auto = False

	periodo= fields.Char('Periodo', size=50)
	libro= fields.Char('Libro', size=50)
	voucher= fields.Char('Voucher', size=50)
	fecha = fields.Date('Fecha')

	type_number = fields.Char('RUC/DNI.', size=50)
	tdp = fields.Char('T.D.P.', size=50)
	empresa = fields.Char('Razon Social', size=50)
	tc = fields.Char('T.C')
	nro_comprobante = fields.Char('Nro. Comprobante', size=50)
	
	
	base1 = fields.Float('BIOGE', digits=(12,2))
	base2 = fields.Float('BIOGENG', digits=(12,2))
	base3 = fields.Float('BIONG', digits=(12,2))
	cng = fields.Float('CNG', digits=(12,2))
	isc = fields.Float('ISC', digits=(12,2))
	igv1 = fields.Float('IGVA', digits=(12,2))
	igv2 = fields.Float('IGVB', digits=(12,2))
	igv3 = fields.Float('IGVC', digits=(12,2))
	otros  = fields.Float('Otros', digits=(12,2))
	total  = fields.Float('Total', digits=(12,2))
	
	'''
	def init(self,cr):
		cr.execute("""
			create or replace view account_purchase_register as (

				select MOVE_ID as id,
t3.code as periodo,
t2.code as libro,
t1.name as voucher,
t1.date as fecha,
t5.type_number,
t6.code as tdp,
t5.name as empresa,
t4.code as tc,
t1.dec_reg_nro_comprobante as nro_comprobante,
base1,base2,base3,cng,igv1,igv2,igv3,otros,isc,total

	select * from vst_reg_compras_1_1_1


						)""")
	'''
