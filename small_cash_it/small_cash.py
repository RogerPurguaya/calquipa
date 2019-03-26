# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import models, fields, api

class small_cash(models.Model):
	_name = 'small.cash'

	STATE_SELECTION = [
		('draft', 'Borrador'),
		('done', 'Monitoreando'),
		('checked', 'Revisado Contable'),
		('cancel', 'Cancelado')
	]
	
	@api.one
	def checked(self):
		#self.state = 'done'
		#name_tmp = self.pool.get('ir.sequence').get(self.env.cr, self.env.uid, 'small.cash') or '/'
		self.write({'state': 'checked'})
		
	@api.one
	def aprove(self):
		#self.state = 'done'
		name_tmp = self.pool.get('ir.sequence').get(self.env.cr, self.env.uid, 'small.cash') or '/'
		self.write({'state': 'done', 'name': name_tmp})
	
	@api.one
	def action_cancel(self):
		self.write({'state': 'draft', 'name': 'Caja Borrador'})
		
	
	
	@api.multi
	def _get_lines(self):
		print 'Into', self
		for cash in self:
			if cash.state in ['done','checked']:
				#Borro todas las lineas de la caja
				ids = self.env['small.cash.line'].search([('line_id','=',cash.id)])
				ids.unlink()
				print 'ids', ids
				
				#Busco los ids de los asientos contables
				ids_moves = self.env['account.move'].search([('period_id','=',cash.period_id.id),('journal_id','=',cash.journal_id.id),('state','=','posted')]).mapped('id')
				print 'ids_moves', ids_moves
				
				moves_lines = self.env['account.move.line'].search([('move_id','in',ids_moves), ('account_id','=',cash.journal_id.default_debit_account_id.id)]).sorted(key=lambda r: r.date)
				print 'moves_lines', moves_lines
				
				new_lines = []
				total = cash.initial_amount
				for move_line in moves_lines:
					total += move_line.debit - move_line.credit
					state = ''
					if total > cash.journal_id.max_import_cash:
						state = 'Saldo Excedido'
					new_lines += self.env['small.cash.line'].create({'move_line_id': move_line.id, 'line_id': cash.id, 'result_amount': total, 'state': state})
					#print 'rs', rs
					#new_lines.append(rs)
				print 'new_lines', new_lines
				print 'end'
				#No sabemos porque funciona este false pero detiene el bucle infinito
				cash.lines_id = False
				cash.lines_id = [(6,0,[x['id'] for x in new_lines])]
	
	@api.depends('state')
	def _get_initial_amount(self):
		print 'Into 2'
		for cash in self:
			if cash.state in ['done', 'checked']:
				#Busco los ids de los asientos contables
				periods_ids = self.env['account.period'].search([('date_stop','<',cash.period_id.date_stop),('id', '!=', cash.period_id.id)]).mapped('id')
				ids_moves = self.env['account.move'].search([('period_id','in',periods_ids),('journal_id','=',cash.journal_id.id),('state','=','posted')]).mapped('id')
				moves_lines = self.env['account.move.line'].search([('move_id','in',ids_moves),('account_id','=',cash.journal_id.default_debit_account_id.id)]).sorted(key=lambda r: r.date)
				
				debit = 0.00
				credit = 0.00
				for move_line in moves_lines:
					debit += move_line.debit
					credit += move_line.credit
				cash.initial_amount = debit - credit
	
	name = fields.Char('Nombre',size=50, default='Caja Borrador')
	journal_id = fields.Many2one('account.journal','Caja Chica')
	user_id = fields.Many2one('res.users','Responsable')
	period_id = fields.Many2one('account.period','Periodo')
	initial_amount = fields.Float('Saldo Inicial', digits=(12,2), compute='_get_initial_amount')
	lines_id = fields.One2many('small.cash.line', 'line_id', string="Movimientos", compute='_get_lines')
	state = fields.Selection(STATE_SELECTION, 'Status', readonly=True, select=True, default='draft')
	
	
class small_cash_line(models.Model):
	_name = 'small.cash.line'
	_order = 'date'
	
	@api.depends('move_line_id', 'line_id')
	def _get_incoming_amount(self):
		for cash_line in self:
			cash_line.incoming_amount = cash_line.move_line_id.debit
	
	@api.depends('move_line_id', 'line_id')
	def _get_outcoming_amount(self):
		for cash_line in self:
			cash_line.outcoming_amount = cash_line.move_line_id.credit
	
	'''
	@api.depends('move_line_id', 'line_id')
	def _get_date(self):
		for cash_line in self:
			cash_line.date = cash_line.move_line_id.date
	'''
	
	def create(self, cr, uid, vals, context):
		if 'move_line_id' in vals:
			line = self.pool.get('account.move.line').browse(cr, uid, vals['move_line_id'], context)
			vals.update({'date':line.move_id.date})
		return super(small_cash_line, self).create(cr, uid, vals, context)
		
	@api.depends('move_line_id', 'line_id')
	def _get_voucher(self):
		for cash_line in self:
			cash_line.voucher = cash_line.move_line_id.move_id.name	
	
	@api.depends('move_line_id', 'line_id')
	def _get_nro_comprobante(self):
		for cash_line in self:
			cash_line.nro_comprobante = cash_line.move_line_id.nro_comprobante
	
	@api.depends('move_line_id', 'line_id')
	def _get_description(self):
		for cash_line in self:
			cash_line.description = cash_line.move_line_id.name

	'''
	@api.multi
	def _get_result_amount(self):
		total = None
		for cash_line in self:
			print 'total', total
			if total is None:
				print 'init', cash_line.line_id.initial_amount
				total = cash_line.line_id.initial_amount
			#cash_line.result_amount = total + cash_line.move_line_id.debit - cash_line.move_line_id.credit
			print 'incoming_amount', cash_line.incoming_amount
			print 'outcoming_amount', cash_line.outcoming_amount
			cash_line.result_amount = total + cash_line.incoming_amount - cash_line.outcoming_amount
			print 'result_amount', cash_line.result_amount
			total = cash_line.result_amount
	'''
	move_line_id = fields.Many2one('account.move.line', 'Apunte Contable')
	date = fields.Date('Fecha')
	voucher = fields.Char('Voucher', size=50, compute='_get_voucher')
	nro_comprobante = fields.Char('Comprobante', size=50, compute='_get_nro_comprobante')
	description = fields.Char('Descripcion', size=255, compute='_get_description')
	incoming_amount = fields.Float('Ingreso', digits=(12,2), compute='_get_incoming_amount')
	outcoming_amount = fields.Float('Egreso', digits=(12,2), compute='_get_outcoming_amount')
	result_amount = fields.Float('Saldo', digits=(12,2))
	state = fields.Char('Control', size=50)
	line_id = fields.Many2one('small.cash', 'Caja Chica')