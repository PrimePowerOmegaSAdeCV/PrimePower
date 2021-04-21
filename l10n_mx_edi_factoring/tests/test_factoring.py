# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from os import path

from lxml import objectify
from odoo.tools import misc
from odoo.tests.common import Form

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestMxEdiFactoring(InvoiceTransactionCase):
    def setUp(self):
        super(TestMxEdiFactoring, self).setUp()
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        for rep_line in self.tax_negative.invoice_repartition_line_ids:
            rep_line.tag_ids |= isr_tag

    def test_001_factoring(self):
        invoice = self.create_invoice()
        invoice.company_id.sudo().name = 'YourCompany'
        invoice.action_post()
        self.assertEqual(
            invoice.l10n_mx_edi_pac_status, "signed",
            invoice.message_ids.mapped('body'))
        factoring = invoice.partner_id.sudo().create({
            'name': 'Financial Factoring',
            'country_id': self.env.ref('base.mx').id,
            'type': 'invoice',
        })
        invoice.partner_id.sudo().commercial_partner_id.l10n_mx_edi_factoring_id = factoring.id  # noqa
        # Register the payment
        ctx = {'active_model': 'account.move', 'active_ids': invoice.ids,
               'force_ref': True}
        bank_journal = self.env['account.journal'].search([
            ('type', '=', 'bank')], limit=1)
        payment_register = Form(self.env['account.payment'].with_context(ctx))
        payment_register.payment_date = invoice.date
        payment_register.l10n_mx_edi_payment_method_id = self.env.ref(
            'l10n_mx_edi.payment_method_efectivo')
        payment_register.payment_method_id = self.env.ref(
            'account.account_payment_method_manual_in')
        payment_register.journal_id = bank_journal
        payment_register.communication = invoice.name
        payment_register.amount = invoice.amount_total
        payment_register.save().post()
        payment = invoice._get_reconciled_payments()
        self.assertTrue(invoice.l10n_mx_edi_factoring_id,
                        'Financial Factor not assigned')
        xml_expected_str = misc.file_open(path.join(
            'l10n_mx_edi_factoring', 'tests',
            'expected_payment.xml')).read().encode('UTF-8')
        xml_expected = objectify.fromstring(xml_expected_str)
        xml = payment.l10n_mx_edi_get_xml_etree()
        self.xml_merge_dynamic_items(xml, xml_expected)
        xml_expected.attrib['Folio'] = xml.attrib['Folio']
        self.assertEqualXML(xml, xml_expected)
