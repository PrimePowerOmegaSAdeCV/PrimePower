from odoo import api, models, fields
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    class SaleOrderLine(models.Model):
        _inherit = "sale.order.line"



        # Funcion para validar modificacion de precios
        @api.onchange('product_id')
        def _onchange_compute_user_editable(self):
            self._compute_user_editable()

        @api.depends('product_id')
        def _compute_user_editable(self):
            #IF TRUE PRICE UNIT IS EDITABLE
            for rec in self:
                if not rec.product_id:
                    rec.is_price_editable = True
                if rec.product_id.type in ('consu', 'service') or self.user_has_groups('sale_price_block.sale_price_modify'):
                #if rec.product_id.type in ('consu', 'service') or rec._uid in (2, 66, 67, 68, 85, 9, 69):
                    rec.is_price_editable = True
                else:
                    rec.is_price_editable = False

        is_price_editable = fields.Boolean(string="is_price_editable", compute="_compute_user_editable")

