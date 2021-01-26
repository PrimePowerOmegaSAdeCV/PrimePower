from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.payment'

    cambio = fields.Float(string='Tipo de Cambio USD', digits=(12, 3), readonly=1, compute="_compute_cambio")

    @api.depends('currency_id', 'payment_date')
    def _compute_cambio(self):
        for record in self:
            if record.currency_id:
                usd = self.env.ref('base.USD')
                date = record.payment_date or fields.Date.today()
                company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.company
                currency_rates = usd._get_rates(company, date)
                currency_rate = currency_rates.get(usd.id) or 1.0
                record['cambio'] = 1 / currency_rate
