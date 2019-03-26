# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw
import openerp


class account_journal(models.Model):
	_inherit = 'account.journal'

	check_credit_card = fields.Boolean('Cobranzas Tarjeta Crédito')
