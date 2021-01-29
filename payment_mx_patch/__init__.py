from . import models


def post_load():
    can_patch = True
    from odoo.tools import float_is_zero
    try:
        from odoo.addons.l10n_mx_edi.models.account_payment import AccountPayment
    except ImportError:
        can_patch = False

    def _l10n_mx_edi_get_payment_write_off(self):
        self.ensure_one()
        res = {}
        for invoice in self.invoice_ids:
            foreign_currency = invoice.currency_id if invoice.currency_id != invoice.company_id.currency_id else False

            pay_term_line_ids = invoice.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            partials = pay_term_line_ids.mapped('matched_debit_ids') + pay_term_line_ids.mapped('matched_credit_ids')
            for partial in partials:
                counterpart_lines = partial.debit_move_id + partial.credit_move_id
                counterpart_line = counterpart_lines.filtered(lambda line: line not in invoice.line_ids)
                if counterpart_line.journal_id != invoice.company_id.currency_exchange_journal_id:
                    continue

                if foreign_currency and partial.currency_id == foreign_currency:
                    if self.skip_payment_patch:
                        amount = partial.amount_currency
                    else:
                        amount = partial.credit_move_id.amount_currency
                else:
                    amount = partial.company_currency_id._convert(partial.amount, invoice.currency_id,
                                                                  invoice.company_id, invoice.date)

                if float_is_zero(amount, precision_rounding=invoice.currency_id.rounding):
                    continue
                res[invoice.id] = amount
        return res

    if can_patch:
        AccountPayment._l10n_mx_edi_get_payment_write_off = _l10n_mx_edi_get_payment_write_off
