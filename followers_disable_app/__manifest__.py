# -*- coding: utf-8 -*-

{
    'name' : 'Disable/Hide Followers Options on Sales,Purchase, Invoice and Send by Email App',
    'author': "Edge Technologies",
    'version' : '13.0.1.0',
    'live_test_url':'https://youtu.be/1wfYuvYHaYA',
    "images":['static/description/main_screenshot.png'],
    'summary' : 'Disable follower on sales order disable follower on purchase order disable follower in invoice disable follower on send by email hide follower on chatter disable follower on chatter disable follower mail follower disable option for follower on chatter',
    'description' : """
        App helps to disable the followers on Sale Order Confirmation
        Disable/Hide Followers Options on Sales Purchase Invoice and Send by Email App
        Disable follower on sales order disable follower on purchase order disable follower in invoice disable follower on send by email
Odoo Disable follower apps helps user disable the followers when confirming the sale order, creating a invoice 
and by sending E-mail. This disable option is configurable which can configure from the setting menu easily 
and once its configure all documents for the sales order, invoice and purchase order's followers option 
will be disable and each option will have different settings i.e sales, purchase, invoice ete 
hide follower on sales order hide follower on purchase order hide follower in invoice hide follower on send by email
         Purchase Order Confirmation, Invoice Validate, Send order by E-mail""",
    'depends' : ['base','sale_management', 'account'],
    "license" : "OPL-1",
    'data' : [
        'views/followers_disable_app.xml', 
    ],
    'installable' : True,
    'auto_install' : False,
    'price': 15,
    "post_load": "post_load",
    'currency': "EUR",
    'category' : 'Extra Tools',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
