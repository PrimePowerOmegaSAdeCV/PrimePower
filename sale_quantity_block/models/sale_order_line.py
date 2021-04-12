from odoo import api, models, fields
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends_context('uid')
    def _get_qty_editable_user(self):
        # IF TRUE The User can Edit the qty, let the view handle the state
        for record in self:
            record.has_qty_edit_group = self.user_has_groups('sale_quantity_block.sale_qty_modify')

    has_qty_edit_group = fields.Boolean(string="Can Edit on Sale", compute="_get_qty_editable_user")
