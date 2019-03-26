# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv

class stock_picking(models.Model):
	_inherit="stock.picking"

	trans_marca = fields.Char(u'Marca')
	trans_placa = fields.Char(u'Placa')
	trans_inscriptor = fields.Char(u'Nº de Constancia de Inscripción')
	trans_licencia = fields.Char(u'Licencia de Conducir Nº (S)')

	trans_name = fields.Char(u'Nombre')
	trans_ruc = fields.Char(u'RUC')
	trans_tipo_comprobante = fields.Char(u'Tipo')
	trans_nro_comprobante = fields.Char(u'Número de Comprobante')