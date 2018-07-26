from odoo import fields, models

class AccountPartialReconcile(models.Model):
    
    _inherit = 'account.partial.reconcile'
    
    cb_move_ids = fields.One2many('account.move', 'tax_cash_basis_rec_id',  string='Cash basis entry')
