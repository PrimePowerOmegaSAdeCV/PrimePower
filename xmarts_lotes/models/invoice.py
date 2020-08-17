from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move.line'

    related_reserved_lots = fields.Char(copy=False)
