from odoo import api, fields, models, _
from odoo.exceptions import Warning


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    related_lots = fields.Char(string="Related Lots",compute='_compute_assigned_lots', copy=False)


    @api.depends('move_ids', 'move_ids.move_line_ids')
    def _compute_assigned_lots(self):
        for line in self:
            reserved_lots = []
            if line.move_ids:
                reserved_lots = [move.lot_id.name or '' for picking in
                                 line.mapped('move_ids').filtered(lambda x: x.state == 'done' and x.picking_code != 'incoming')
                                 for move in picking.mapped('move_line_ids').filtered(lambda x: x.qty_done > 0 and x.picking_id.sale_id.name == x.picking_id.origin,)]
            if reserved_lots:
                line.related_lots = ','.join(reserved_lots)
            else:
                line.related_lots = ''
            

    def _prepare_invoice_line(self):
        values = super(SaleOrderLine, self)._prepare_invoice_line()
        if self.product_id.tracking != 'none':
            values['related_reserved_lots'] = self.related_lots
        return values

