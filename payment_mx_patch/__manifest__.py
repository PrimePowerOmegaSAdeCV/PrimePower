{
    'name': 'Payment Mx patch',
    'version': '13.0.0.1',
    'category': "",
    'description': """ Adds a patch to make payment10 template work correctly
    """,
    'author': 'Munin',
    'depends': ['base', 'l10n_mx_edi', 'account', 'account_payment'],
    'data': [
        'views/payment_10.xml',
        'views/account_account_views.xml',
    ],
    "post_load": "post_load",
    'installable': True,
    'application': True,
}
