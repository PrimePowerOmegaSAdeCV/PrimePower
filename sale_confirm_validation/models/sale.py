from odoo import api, fields, models, _
from odoo.exceptions import Warning,UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        lines = self.order_line.filtered(lambda x: x.product_id.categ_id)
        category_lines = lines.mapped('product_id.categ_id')
        required_category = self.env['product.category'].sudo().with_context(lang="es_MX").search(
            [('display_name', '=', 'Placa Plana')], limit=1).id
        if required_category not in category_lines.ids:
            raise UserError("No se tiene la categoría  requerida: Conectores")
        return super(SaleOrder, self).action_confirm()
