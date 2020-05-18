{
    'name': 'Credit limit approval',
    'version': '12.0.0',
    'summary': 'Envia la orden a un estado de aprovacion si se nesecita exceder',
    'description': 'Envie la orden a un estado de aprovacion si se nesecita exceder el credito disponible',
    'author': 'Axel de los Reyes',
    'website': 'www.xmarts.com',
    'depends': ['sale', 'account_accountant', 'contacts'],
    'data': [
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
       'wizards/partnert_statement_wizard_view.xml',
        'views/sale_order.xml',
        'security/groups.xml',
    ],
    'installable': True,
}
