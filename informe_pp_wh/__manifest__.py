{
    'name': 'Prime Power Picking Informe',
    'version': '13.0.0.1',
    'category': "",
    'description': """ Reporte warehouse.
    """,
    'author':'Munin',
    'depends': ['base','stock'],
    'data': [
        "report/pp_picking.xml",
        "views/stock_picking_view.xml",
    ],
    'qweb': [
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
