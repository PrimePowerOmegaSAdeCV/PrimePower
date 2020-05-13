from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        for record in self:
            res.update({
                'warehouse_id': record.warehouse_id.id,
            })
        return res
