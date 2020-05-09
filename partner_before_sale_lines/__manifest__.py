# -*- coding: utf-8 -*-
{
    'name': 'Xmarts Partner Before Sale Lines ',
    'version': '13.1',
    'category': "",
    'description': """ 
    Crear restricción o condición que no permita cotizar productos y tarifas sin antes haber determinado el cliente al que se le realizará dicha cotización.
    """,
    'author':'Xmarts',
    'depends': ['base','sale'],
    'data': [
	        "views/sale_order.xml"
    ],
    'qweb': [
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
