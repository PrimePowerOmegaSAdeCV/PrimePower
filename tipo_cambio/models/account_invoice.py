from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    tasadecambio = fields.Float(related='currency_id.rate_ids.rate')
    cambio = fields.Float(string='Tipo de Cambio', digits=(12, 3), readonly=1)

    @api.onchange('currency_id', 'partner_id', 'invoice_date')
    def _onchange_currency_id(self):
        for record in self:
            if record.currency_id:
                if record.type in ['in_invoice', 'in_refund']:
                    date = record.invoice_date or fields.Date.today()
                else:
                    date = fields.Date.today()
                company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.company
                currency_rates = record.currency_id._get_rates(company, date)
                currency_rate = currency_rates.get(record.currency_id.id) or 1.0
                record['cambio'] = 1 / currency_rate
