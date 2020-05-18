# -*- coding: utf-8 -*-
{
    'name': "Xmarts Reporte de ventas ",

    'summary': """
        Modelo para many o one en sale order""",

    'description': """

    """,

    'author': "Axel",
    'website': "",


    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
     "depends": [

        'sale','stock','account'

    ],

    # always loaded
    'data': [

        'views/vistaReporte.xml',
    'security/ir.model.access.csv',

    ],
    # only loaded in demonstration mode
    'demo': [
        '',
    ],
}
