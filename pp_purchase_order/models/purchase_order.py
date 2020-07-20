from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def amount_in_letter(self):
        """Method to transform a float amount to text words
        E.g. 100 - ONE HUNDRED
        :returns: Amount transformed to words mexican format for invoices
        :rtype: str
        """
        self.ensure_one()
        currency_type = self.currency_id.name.upper()
        amount_i, amount_d = divmod(self.amount_total, 1)
        amount_d = round(amount_d, 2)
        amount_d = int(round(amount_d * 100, 2))
        words = self.currency_id.with_context(lang=self.partner_id.lang or 'es_ES').amount_to_text(amount_i).upper()
        if currency_type == 'USD' and self.partner_id.lang == 'en_US':
            words = words.replace('DOLARES', 'DOLLARS')
        new_words = words.title()

        invoice_words = '%(words)s %(amount_d)02d/100 %(curr_t)s' % dict(
            words=new_words, amount_d=amount_d, curr_t=currency_type)
        return invoice_words
