from odoo import _, api, fields, models, tools

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    cash_basis_entry_ids = fields.Many2many('account.move', column1='account_invoice_id', column2='account_move_id', string='Taxes journal entries')
    payment_entry_ids = fields.Many2many('account.move', column1='account_invoice_id', column2='account_move_id', string='Payment journal entries')
    
    def action_get_journal_entries(self):
        for record in self:
            entry_ids = []
            cash_basis_entry_ids = []
            for payment in record.payment_ids:
                for move_line in payment.move_line_ids:
                    entry_id = move_line.move_id.id
                if entry_id not in entry_ids:
                    entry_ids.append(entry_id)
                if move_line.full_reconcile_id:
                    for partial_id in move_line.full_reconcile_id.partial_reconcile_ids:
                        for cb_id in partial_id.cb_move_ids:
                            if cb_id.id not in cash_basis_entry_ids:
                                cash_basis_entry_ids.append(cb_id.id)
            record['cash_basis_entry_ids'] = [(6,0,cash_basis_entry_ids)]
            record['payment_entry_ids'] = [(6,0,entry_ids)]
            
        
