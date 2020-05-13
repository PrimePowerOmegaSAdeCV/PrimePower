from odoo import api, fields, models

class Invoice(models.Model):
    _inherit = 'account.move'

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", string="Almacen", required=False, )

    def l10n_mx_edi_amount_to_text_qweb_report(self):

        self.ensure_one()
        currency = self.currency_id.name.upper()
        # M.N. = Moneda Nacional (National Currency)
        # M.E. = Moneda Extranjera (Foreign Currency)
        currency_type = 'M.N' if currency == 'MXN' else 'M.E.'
        # Split integer and decimal part
        amount_i, amount_d = divmod(self.amount_total, 1)
        amount_d = round(amount_d, 2)
        amount_d = int(round(amount_d * 100, 2))
        words = self.currency_id.with_context(lang=self.partner_id.lang or 'es_ES').amount_to_text(amount_i).upper()
        if currency == "USD" and self.partner_id.lang not in 'en_US':
            currency_type = "USD"
            if words:
                words = words.replace("DOLLARS","DOLARES")
        invoice_words = '%(words)s %(amount_d)02d/100 %(curr_t)s' % dict(
            words=words, amount_d=amount_d, curr_t=currency_type)
        return invoice_words

