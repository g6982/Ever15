# -*- coding: utf-8 -*-
{
    'name': "OurCustom Serial Number",

    'summary': """OurCustom Serial Number in Lines""",

    'description': """
        This module helps to show serial number in lines.
    """,

    'author': "Technosolus",
    'website': "http://www.technosolus.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'stock'],

    # always loaded
    'data': [
        'views/account_move_views.xml',
        'views/stock_move_views.xml',
        'views/stock_move_line_views.xml',

    ],
    # only loaded in demonstration mode
#    'demo': [
#        'demo.xml',
#    ],
'installable': True,
'application': True,
'auto_install': False,
}
