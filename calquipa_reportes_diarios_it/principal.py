# -*- encoding: utf-8 -*-
import base64
from openerp import models, fields, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp

class principal(models.Model):
	_name = 'principal'

	_rec_name = 'name'

	name = fields.Char('Menu Principal')