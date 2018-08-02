# -*- coding: utf-8 -*-
{
    'name': 'pp: sale',
    'summary': 'Prime Power: Quote/ Sales order',
    'description': """
    * Created a custom pdf quote/sales order
    * Note: in Website settings, enable variances, optional product and multiple images.
    """,
    'license': 'OEEL-1',
    'author': 'Odoo Inc',
    'version': '1.0',
    'depends': ['sale_management', 'website_sale', 'l10n_mx_edi', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users.xml',
        'views/res_company.xml',
        'views/res_bank.xml',
        'views/product_product.xml',
        'views/sale_order.xml',
        'report/report_saleorder_document_pp.xml'
    ],
}