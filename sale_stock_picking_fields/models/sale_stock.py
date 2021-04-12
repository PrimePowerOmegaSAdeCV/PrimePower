# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    tipo_entrega = fields.Many2one('stock.shipping.type', string="Tipo de entrega", copy=False,
                                   compute="_get_sales_values")
    pago_flete = fields.Many2one('stock.shipping.payer', string="Pago de Flete", copy=False,
                                 compute="_get_sales_values")

    @api.depends('move_lines.pago_flete', 'move_lines.tipo_entrega')
    def _get_sales_values(self):
        for record in self:
            record.tipo_entrega = record.move_lines.tipo_entrega or False
            record.pago_flete = record.move_lines.pago_flete or False


class StockMove(models.Model):
    _inherit = 'stock.move'

    tipo_entrega = fields.Many2one('stock.shipping.type', string="Tipo de entrega", copy=False, )
    pago_flete = fields.Many2one('stock.shipping.payer', string="Pago de Flete", copy=False, )


#
# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     is_cargo_cliente = fields.Boolean(string="Pagado", copy=False, )


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        res['tipo_entrega'] = self.order_id.shipping_type_id.id
        res['pago_flete'] = self.order_id.shipping_payer_id.id
        return res


class StockRuleInherit(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom,
                               location_id, name, origin, company_id, values):
        res = super(StockRuleInherit, self)._get_stock_move_values(product_id=product_id, product_qty=product_qty,
                                                                   product_uom=product_uom, location_id=location_id,
                                                                   name=name, origin=origin, company_id=company_id,
                                                                   values=values)
        res['tipo_entrega'] = values.get('tipo_entrega')
        res['pago_flete'] = values.get('pago_flete')
        return res
