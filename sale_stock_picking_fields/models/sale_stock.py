# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    tipo_entrega = fields.Many2one('stock.shipping.type', string="Tipo de entrega", copy=False, )
    pago_flete = fields.Many2one('stock.shipping.payer', string="Pago de Flete", copy=False, )


class StockMove(models.Model):
    _inherit = 'stock.move'

    tipo_entrega = fields.Many2one('stock.shipping.type', string="Tipo de entrega", copy=False, )
    pago_flete = fields.Many2one('stock.shipping.payer', string="Pago de Flete", copy=False, )

    def _assign_picking_post_process(self, new=False):
        res = super(StockMove, self)._assign_picking_post_process(new=new)
        if new:
            picking_id = self.mapped('picking_id')
            sale_order_ids = self.mapped('sale_line_id.order_id')
            for sale_order_id in sale_order_ids:
                picking_id.tipo_entrega = sale_order_id.shipping_type_id.id
                picking_id.pago_flete = sale_order_id.shipping_payer_id.id
        return res
