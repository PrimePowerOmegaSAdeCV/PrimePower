{
    'name': 'Xmarts edi UUID2 ',
    'version': '13',
    'category': "",
    'description': """ Adds  UUID2 in invoice
    """,
    'author':'Xmarts',
    'depends': ['base','l10n_mx_edi','account','account_payment'],
    'data': [
    'views/account_invoice_view.xml',
    ],
    'qweb': [
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
