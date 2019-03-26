# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp import http


class checkera_sequence(models.Model):
	_name = 'checkera.sequence'

	sequence_id = fields.Many2one('ir.sequence','Secuencia')
	journal_id = fields.Many2one('account.journal','Diario')
	_rec_name='sequence_id'


class account_move(models.Model):
	_inherit='account.move'
	
	checkera_sequence_id = fields.Many2one('checkera.sequence','Secuencia de Chequera')
	type_journal = fields.Selection(string='Tipo Journal', related='journal_id.type')


	@api.onchange('checkera_sequence_id')
	def onchange_checkera_sequence_id(self):
		if self.checkera_sequence_id.id:
			next_number = self.checkera_sequence_id.sequence_id.number_next_actual

			prefix = self.checkera_sequence_id.sequence_id.prefix if self.checkera_sequence_id.sequence_id.prefix else ''
			padding = self.checkera_sequence_id.sequence_id.padding
			self.ref = prefix + "0"*(padding - len(str(next_number))) + str(next_number)


	@api.one
	def button_validate(self):
		t = super(account_move,self).button_validate()
		if self.checkera_sequence_id.id:
			if self.checkera_sequence_id.sequence_id.id:
				if self.journal_id.type == 'bank':
					name=self.pool.get('ir.sequence').next_by_id(self.env.cr, self.env.uid, self.checkera_sequence_id.sequence_id.id, self.env.context)
		return t




class account_voucher(models.Model):
	_inherit = 'account.voucher'
	
	checkera_sequence_id = fields.Many2one('checkera.sequence','Secuencia de Chequera')
	type_journal = fields.Selection(string='Tipo Journal', related='journal_id.type')


	@api.onchange('checkera_sequence_id')
	def onchange_checkera_sequence_id(self):
		if self.checkera_sequence_id.id:
			next_number = self.checkera_sequence_id.sequence_id.number_next_actual

			prefix = self.checkera_sequence_id.sequence_id.prefix if self.checkera_sequence_id.sequence_id.prefix else ''
			padding = self.checkera_sequence_id.sequence_id.padding
			self.reference = prefix + "0"*(padding - len(str(next_number))) + str(next_number)


	@api.one
	def action_move_line_create(self):
		t = super(account_voucher,self).action_move_line_create()
		if self.checkera_sequence_id.id:
			if self.checkera_sequence_id.sequence_id.id:
				if self.journal_id.type == 'bank':
					name=self.pool.get('ir.sequence').next_by_id(self.env.cr, self.env.uid, self.checkera_sequence_id.sequence_id.id, self.env.context)
					self.move_id.write({'checkera_sequence_id':self.checkera_sequence_id.id})
		return t