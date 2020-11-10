from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        inv = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        inv.cambio = order.cambio
        return inv
