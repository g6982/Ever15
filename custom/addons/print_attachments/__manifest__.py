# -*- coding: utf-8 -*-
{
    'name': 'Ourcustom Print Attachments',
    'version': '15.0.0.3',
    'license': 'OPL-1',
    'category': 'Extra Tools',
    'summary': '',

    'author': 'ENSWORK',
    'website': 'https://www.enswork.com/',
    #depends on sale to mark process as shipped
    #depends on ourcustom_ever cause it's the model that add process to sale
    'depends': ['base', 'stock', 'ourcustom_ever', 'sale'],
    'data': [
        'views/action_download_stock_multi_labels_view.xml',
    ],

    'assets': {
        'web._assets_bootstrap': [
            'ourcustom_ever/static/src/scss/style.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,

}
