import base64
import logging
from odoo import models, fields, api,_
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    edi_uuid2 = fields.Char(string="uuid2")
    skip_mx_edi_invoice = fields.Boolean(string="No Timbrar", copy=False)

    @api.depends('l10n_mx_edi_cfdi_name','edi_uuid2')
    def _compute_cfdi_values(self):
        """Fill the invoice fields from the cfdi values."""
        for rec in self:
            attachment_id = rec.l10n_mx_edi_retrieve_last_attachment()
            attachment_id = attachment_id[0] if attachment_id else None
            # At this moment, the attachment contains the file size in its 'datas' field because
            # to save some memory, the attachment will store its data on the physical disk.
            # To avoid this problem, we read the 'datas' directly on the disk.
            datas = attachment_id._file_read(attachment_id.store_fname) if attachment_id else None
            rec.l10n_mx_edi_cfdi_uuid = None
            if not datas:
                if attachment_id:
                    _logger.exception('The CFDI attachment cannot be found')
                if rec.edi_uuid2:
                    rec.l10n_mx_edi_cfdi_uuid = rec.edi_uuid2
                rec.l10n_mx_edi_cfdi = None
                rec.l10n_mx_edi_cfdi_supplier_rfc = None
                rec.l10n_mx_edi_cfdi_customer_rfc = None
                continue
            rec.l10n_mx_edi_cfdi = datas
            tree = rec.l10n_mx_edi_get_xml_etree(base64.decodestring(datas))
            tfd_node = rec.l10n_mx_edi_get_tfd_etree(tree)
            if tfd_node is not None:
                rec.l10n_mx_edi_cfdi_uuid = tfd_node.get('UUID')
            else:
                rec.l10n_mx_edi_cfdi_uuid = rec.edi_uuid2

            rec.l10n_mx_edi_cfdi_supplier_rfc = tree.Emisor.get(
                'Rfc', tree.Emisor.get('rfc'))
            rec.l10n_mx_edi_cfdi_customer_rfc = tree.Receptor.get(
                'Rfc', tree.Receptor.get('rfc'))
            certificate = tree.get('noCertificado', tree.get('NoCertificado'))

    def l10n_mx_edi_is_required(self):
        self.ensure_one()
        if self.skip_mx_edi_invoice:
            return False
        else:
            return super(AccountPayment, self).l10n_mx_edi_is_required()