from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_partner_edi_values(self):
        if self.partner_id:
            self.l10n_mx_edi_payment_method_id = self.partner_id.l10n_mx_edi_payment_method_id.id
            self.l10n_mx_edi_usage = self.partner_id.l10n_mx_edi_usage
        return

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self._get_partner_edi_values()
        return super(AccountMove, self)._onchange_partner_id()

    @api.model
    def create(self, vals):
        edi_fields = ['l10n_mx_edi_payment_method_id', 'l10n_mx_edi_usage']
        if any(fields not in vals for fields in edi_fields):
            move = self.new(vals)
            move._get_partner_edi_values()
            for field in edi_fields:
                if field not in vals and move[field]:
                    vals[field] = move._fields[
                        field].convert_to_write(move[field], move)
        return super(AccountMove, self).create(vals)