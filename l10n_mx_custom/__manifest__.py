# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'EDI custom for Mexico ',
    'version': '0.1',
    'category': 'Hidden',
    'summary': 'Improvements for EDI Mexican Localization',
    'description': """
Apply required fields to invoice pdf, enable fields for vendor bills to upload xml
""",
    'depends': [
        'l10n_mx_edi',
        'l10n_mx_reports',
    ],
    'external_dependencies' : {
    },
    'data': [
            "views/l10n_mx_edi_report_invoice_document.xml",
            "views/account_invoice_view.xml"
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
