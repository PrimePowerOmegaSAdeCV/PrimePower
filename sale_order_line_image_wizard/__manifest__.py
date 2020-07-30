# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Open Image Wizard ',
    'version': '13.1',
    'category': "",
    'description': """ 
    Crear restricción o condición que no permita cotizar productos y tarifas sin antes haber determinado el cliente al que se le realizará dicha cotización.
    """,
    'author':'Xmarts',
    'depends': ['base','sale','sale_stock','stock'],
    'data': [
	        "views/sale_order.xml",
            "views/product_image_template.xml",
             "views/assets.xml",
    ],
    'qweb': [
        "static/src/xml/sale_product_image.xml",
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
