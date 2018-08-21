# -*- coding: utf-8 -*-
{
    'name': 'PP: Sale',
    'summary': 'Prime Power: Quote/ Sales order',
    'description': """
    * Created a custom pdf quote/sales order
    * Functional Notes: 
        1. In Website settings, enable optional product and multiple images.
        2. Company's Text Quote, Relevant Information, Pesos and Dollars accounts, SO Footer image fields are under Settings/Company Setup/Sales.
        3. Salesperson's custom signature is under Users/<User>/Preferences.
        4. SO fields (Contact Customer, LAB Prices) and SO Line field (Delivery Time) are on SO form view.
        5. Product Variance fields (Product Specification) can be found under Product Variances/<Product>/General Information.
    """,
    'license': 'OEEL-1',
    'author': 'Odoo Inc',
    'version': '1.0',
    'depends': ['sale_management', 'website_sale', 'website_quote', 'l10n_mx_edi', 'contacts', 'sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users.xml',
        'views/res_company.xml',
        'views/res_partner_bank.xml',
        'views/product_product.xml',
        'views/sale_order.xml',
        'report/report_saleorder_document_pp.xml'
    ],
}