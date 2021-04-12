# -*- coding: utf-8 -*-
{
    'name': "Sale Quantity Extended",
    'summary': """Adds to group qty""",

    'category': 'sale',
    'version': '13.1',

    'depends': ['sale','base'],

    'data': [
        'views/sale_view.xml',
        'security/groups.xml',
    ],
    'installable': True,
    'application': False,
}
