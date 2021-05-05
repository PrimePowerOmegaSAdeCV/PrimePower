# -*- coding: utf-8 -*-
{
    'name': "Sale Quantity Block",
    'summary': """Adds group to modify qty in sale""",

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
