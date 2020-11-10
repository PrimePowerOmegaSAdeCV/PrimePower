{
    'name': 'Prime Power Mrp Report',
    'version': '13',
    'category': "",
    'description': """ Mrp Custom Report 
    """,
    'author':'Xmarts',
    'depends': ['base','mrp'],
    'data': [
	    "report/mrp_report_temp.xml",
        "report/report_action.xml",
        "wizard/wizard_views.xml",
    ],
    'qweb': [
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
