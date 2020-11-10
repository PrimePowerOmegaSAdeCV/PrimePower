from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tasadecambio = fields.Float(related='currency_id.rate_ids.rate')
    cambio = fields.Float(string='Tipo de Cambio', digits=(12, 3), store=True, readonly=1, default='1')

    @api.onchange('currency_id')
    def _onchange_currency_id_rate(self):
        for record in self:
            if record.tasadecambio != 0:
                record['cambio'] = 1 / record.tasadecambio

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['cambio'] = self.cambio
        return res
