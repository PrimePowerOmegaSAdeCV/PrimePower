from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    tasadecambio = fields.Float(related='currency_id.rate_ids.rate')

    cambiobill = fields.Float(string='Tipo de Cambio',digits=(12,3),store=True,readonly=1)


    def action_view_invoice(self):
        # Add code here
        create_bill = self.env.context.get('create_bill', False)
        if create_bill:
            res = super(PurchaseOrder, self).action_view_invoice()

            res['context'].update({
                'default_cambio': self.cambiobill
            })
            return res
        else:
            return super(PurchaseOrder, self).action_view_invoice()

    @api.onchange('currency_id')
    def CalcularCambio(self):
        for record in self:
            if record.tasadecambio!=0:
                record['cambiobill'] = 1 / record.tasadecambio







