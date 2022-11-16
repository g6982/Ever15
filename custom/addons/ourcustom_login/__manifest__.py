# -*- coding: utf-8 -*-
{
    'name': "OurCustom Login",

    'summary': """OurCustom Login Interface""",

    'description': """
      
    """,

    'author': "ENSWORK",
    'website': "http://www.enswork.com",

    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',],

    # always loaded
    'data': [
        'templates/login_page.xml',

    ],
    # only loaded in demonstration mode
#    'demo': [
#        'demo.xml',
#    ],
'installable': True,
'application': True,
'auto_install': False,
}
