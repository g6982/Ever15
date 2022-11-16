# -*- coding: utf-8 -*-
{
    'name': 'Ourcustom Auto Payment Reminder',
    'license': 'OPL-1',
    'category': 'Accounting',
    'summary': '',
    'version': '15.0.0.2',

    'author': 'ENSWORK',
    'website': 'https://www.enswork.com/',
    'depends': ['base', 'dev_payment_reminder', 'mail', 'account'],
    'data': [
        'templates/mail_templates.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,

}

