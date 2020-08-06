from odoo import fields, models, api

class LotSerialNumberEPT(models.Model):
    _inherit = "stock.production.lot"

    claim_line_id = fields.Many2one('claim.line.ept', string="Claim line")
