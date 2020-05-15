{
    'name': 'Xmarts Tipo de Cambio ',
    'version': '13.0.3',
    'category': "",
    'description': """ get data from currency_id 
    """,
    'author':'Xmarts',
    'depends': ['account','sale','account_accountant'],
    'data': [
	'views/sale_order_view.xml',
	'views/invoice_view.xml',
	'views/purchase_order_view .xml',
	# 'report/reporte_sale.xml',
	  
    ],
    'qweb': [
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
