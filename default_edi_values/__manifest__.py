{
    'name': 'Edi MX Default Values',
    'version': '13',
    'category': '',
    'description': """ get data from partner  and fill in the Invoice.
    """,
    'author':'Xmarts',
    'depends': ['base','account','l10n_mx','l10n_mx_edi'],
    'data': [
	'views/partner_view.xml',
    ],
    'qweb': [
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
