# -*- coding: utf-8 -*-
{
    'name': "Sale extend for Prime Power",

    'summary': """
        Adds extra fields in sales orders""",

    'description': """
        Sale product detail
        Add extra fields needed when capturing a sale.
    """,

    'author': "Suriel",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp','sale','product','stock', 'website_sale_options'],

    # always loaded
    'data': [
        'security/sales_template_security.xml',
        'security/ir.model.access.csv',
        'report/work_order_mrp.xml',
        'report/work_order_template.xml',
        'report/work_order_report.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/sales_template_view.xml',
        'views/product_category_view.xml',
        'views/product_view.xml',
        'views/sale_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
