# -*- encoding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs
from datetime import datetime

class menu_principal_contabilidad(osv.TransientModel):
	_name='menu.principal.contabilidad'
	name = fields.Char('Nombre')
