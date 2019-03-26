# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw
import openerp


class account_voucher(models.Model):
	_inherit = 'account.voucher'

	credit_card_id = fields.Many2one('voucher.credit.card','Tarjeta de Crédito')
	check_verify_card = fields.Boolean('Verificar Voucher', related='journal_id.check_credit_card')

	def first_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
		t = super(account_voucher,self).first_move_line_get(cr, uid, voucher_id, move_id, company_currency, current_currency, context)
		voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
		if voucher.journal_id.check_credit_card == True:
			if voucher.credit_card_id:
				t['partner_id']= voucher.credit_card_id.entity.id
				print voucher.credit_card_id.entity
		return t

	@api.onchange('credit_card_id')
	def onchange_credit_card_id(self):
		if self.credit_card_id:
			self.means_payment_id = self.credit_card_id.means_payment_id.id
