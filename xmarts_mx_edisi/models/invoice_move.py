import base64

from odoo import models, fields, api, _


class Accountmove(models.Model):
    _inherit = 'account.move'

    edi_uuid2 = fields.Char(string="uuid2", copy=False)
    l10n_mx_edi_cfdi_name = fields.Char(string='CFDI name', copy=False, readonly=True,
                                        help='The attachment name of the CFDI.')
    skip_mx_edi_invoice = fields.Boolean(string="No Timbrar", copy=False)

    @api.depends('l10n_mx_edi_cfdi_name', 'edi_uuid2')
    def _compute_cfdi_values(self):

        for inv in self:
            attachment_id = inv.l10n_mx_edi_retrieve_last_attachment()
            inv.l10n_mx_edi_cfdi_uuid = None
            if not attachment_id:
                inv.l10n_mx_edi_cfdi = None
                inv.l10n_mx_edi_cfdi_supplier_rfc = None
                inv.l10n_mx_edi_cfdi_customer_rfc = None
                inv.l10n_mx_edi_cfdi_amount = None
                if inv.edi_uuid2:
                    inv.l10n_mx_edi_cfdi_uuid = inv.edi_uuid2
                continue

            datas = attachment_id._file_read(attachment_id.store_fname)
            inv.l10n_mx_edi_cfdi = datas
            cfdi = base64.decodestring(datas).replace(
                b'xmlns:schemaLocation', b'xsi:schemaLocation')
            tree = inv.l10n_mx_edi_get_xml_etree(cfdi)
            # if already signed, extract uuid
            tfd_node = inv.l10n_mx_edi_get_tfd_etree(tree)
            if tfd_node is not None:
                if not inv.edi_uuid2:
                    inv.l10n_mx_edi_cfdi_uuid = tfd_node.get('UUID')
                else:
                    inv.l10n_mx_edi_cfdi_uuid = inv.edi_uuid2

            inv.l10n_mx_edi_cfdi_amount = tree.get('Total', tree.get('total'))
            inv.l10n_mx_edi_cfdi_supplier_rfc = tree.Emisor.get(
                'Rfc', tree.Emisor.get('rfc'))
            inv.l10n_mx_edi_cfdi_customer_rfc = tree.Receptor.get(
                'Rfc', tree.Receptor.get('rfc'))
            certificate = tree.get('noCertificado', tree.get('NoCertificado'))

    def l10n_mx_edi_is_required(self):
        self.ensure_one()
        return (self.is_sale_document() and self.company_id.country_id == self.env.ref(
            'base.mx') and not self.skip_mx_edi_invoice)
