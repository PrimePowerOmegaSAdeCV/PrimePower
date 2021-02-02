# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re

class followers_disable_apps(models.TransientModel):
	_inherit = 'res.config.settings'

	disable_follower_sm = fields.Boolean("Disable Follower By Send Mail")
	disable_follower_so = fields.Boolean("Disable Follower By Confirm Sale")
	disable_follower_po = fields.Boolean("Disable Follower By Confirm Purchase")
	disable_follower_ai = fields.Boolean("Disable Follower By Invoice Bill")

	@api.model
	def get_values(self):
		res = super(followers_disable_apps, self).get_values()
		res['disable_follower_sm'] = (self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_sm', default=0))
		res['disable_follower_so'] = (self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_so', default=0))
		res['disable_follower_po'] = (self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_po', default=0))
		res['disable_follower_ai'] = (self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_ai', default=0))
		return res

	
	def set_values(self):		
		self.env['ir.config_parameter'].sudo().set_param('followers_disable_app.disable_follower_sm', self.disable_follower_sm)
		self.env['ir.config_parameter'].sudo().set_param('followers_disable_app.disable_follower_so', self.disable_follower_so)
		self.env['ir.config_parameter'].sudo().set_param('followers_disable_app.disable_follower_po', self.disable_follower_po)
		self.env['ir.config_parameter'].sudo().set_param('followers_disable_app.disable_follower_ai', self.disable_follower_ai)
		super(followers_disable_apps, self).set_values()

class followers_disable_sale_apps(models.Model):
	_inherit = 'sale.order'

	def action_confirm(self):
		if self._get_forbidden_state_confirm() & set(self.mapped('state')):
			raise UserError(_(
				'It is not allowed to confirm an order in the following states: %s'
			) % (', '.join(self._get_forbidden_state_confirm())))
		follow_so = self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_so')
		if not follow_so:
			for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
				order.message_subscribe([order.partner_id.id])
		self.write({
			'state': 'sale',
			'date_order': fields.Datetime.now()
		})
		self._action_confirm()
		if self.env.user.has_group('sale.group_auto_done_setting'):
			self.action_done()
		return True	

class followers_disable_invoice_apps(models.Model):
	_inherit = 'account.move'

	def post(self):
		for move in self:
			if not move.line_ids.filtered(lambda line: not line.display_type):
				raise UserError(_('You need to add a line before posting.'))
			if move.auto_post and move.date > fields.Date.today():
				date_msg = move.date.strftime(self.env['res.lang']._lang_get(self.env.user.lang).date_format)
				raise UserError(_("This move is configured to be auto-posted on %s" % date_msg))

			if not move.partner_id:
				if move.is_sale_document():
					raise UserError(_("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
				elif move.is_purchase_document():
					raise UserError(_("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

			if move.is_invoice(include_receipts=True) and float_compare(move.amount_total, 0.0, precision_rounding=move.currency_id.rounding) < 0:
				raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead. Use the action menu to transform it into a credit note or refund."))
			
			if not move.invoice_date and move.is_invoice(include_receipts=True):
				move.invoice_date = fields.Date.context_today(self)
				move.with_context(check_move_validity=False)._onchange_invoice_date()
			
			if (move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date) and (move.line_ids.tax_ids or move.line_ids.tag_ids):
				move.date = move.company_id.tax_lock_date + timedelta(days=1)
				move.with_context(check_move_validity=False)._onchange_currency()
		# Create the analytic lines in batch is faster as it leads to less cache invalidation.
		self.mapped('line_ids').create_analytic_lines()
		for move in self:
			if move.auto_post and move.date > fields.Date.today():
				raise UserError(_("This move is configured to be auto-posted on {}".format(move.date.strftime(self.env['res.lang']._lang_get(self.env.user.lang).date_format))))
			follow_ai = self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_ai')
			if not follow_ai:
				move.message_subscribe([p.id for p in [move.partner_id, move.commercial_partner_id] if p not in move.sudo().message_partner_ids])

			to_write = {'state': 'posted'}

			if move.name == '/':
				# Get the journal's sequence.
				sequence = move._get_sequence()
				if not sequence:
					raise UserError(_('Please define a sequence on your journal.'))

				# Consume a new number.
				to_write['name'] = sequence.next_by_id(sequence_date=move.date)

			move.write(to_write)

			# Compute 'ref' for 'out_invoice'.
			if move.type == 'out_invoice' and not move.invoice_payment_ref:
				to_write = {
					'invoice_payment_ref': move._get_invoice_computed_reference(),
					'line_ids': []
				}
				for line in move.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
					to_write['line_ids'].append((1, line.id, {'name': to_write['invoice_payment_ref']}))
				move.write(to_write)

			if move == move.company_id.account_opening_move_id and not move.company_id.account_bank_reconciliation_start:
				move.company_id.account_bank_reconciliation_start = move.date

		for move in self:
			if not move.partner_id: continue
			if move.type.startswith('out_'):
				field='customer_rank'
			elif move.type.startswith('in_'):
				field='supplier_rank'
			else:
				continue
			try:
				with self.env.cr.savepoint():
					self.env.cr.execute("SELECT "+field+" FROM res_partner WHERE ID=%s FOR UPDATE NOWAIT", (move.partner_id.id,))
					self.env.cr.execute("UPDATE res_partner SET "+field+"="+field+"+1 WHERE ID=%s", (move.partner_id.id,))
					self.env.cache.remove(move.partner_id, move.partner_id._fields[field])
			except psycopg2.DatabaseError as e:
				if e.pgcode == '55P03':
					_logger.debug('Another transaction already locked partner rows. Cannot update partner ranks.')
					continue
				else:
					raise e

class followers_disable_mail_composer(models.TransientModel):
	_inherit = 'mail.compose.message'

	def get_mail_values(self, res_ids):
		"""Generate the values that will be used by send_mail to create mail_messages
		or mail_mails. """
		res = super(followers_disable_mail_composer,self).get_mail_values(res_ids)
		follow_so = self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_sm')
		if follow_so:
			for key,value in res.items():
				del value['partner_ids']
		return res
