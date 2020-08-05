# -*- coding: utf-8 -*-
{
    'name': "Sale Stock Extended",

    'summary': """
        Show Available qty and Reserved Qty Based on Configured Location """,

    'description': """ """,

    'category': 'Stock',
    'version': '0.1',

    'depends': ['sale_stock'],

    'data': [
        'views/sale_view.xml',
        'security/groups.xml',
    ],
    'installable': True,
    'application': False,
}
