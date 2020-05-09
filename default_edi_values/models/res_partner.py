from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'res.partner'

    def _default_edi_usage(self):
        return self.env.ref('l10n_mx_edi.payment_method_otros').id

    l10n_mx_edi_payment_method_id = fields.Many2one('l10n_mx_edi.payment.method', string='Payment Method',
                                                    default=lambda self: self._default_edi_usage())
    l10n_mx_edi_usage = fields.Selection(
        lambda self: self.env['account.move'].fields_get().get(
            'l10n_mx_edi_usage').get('selection'), 'Usage', default='P01',
        help='This usage will be used instead of the default one for invoices.'
    )
