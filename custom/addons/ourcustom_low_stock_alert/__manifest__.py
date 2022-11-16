{
    'name': 'Ourcustom Low Stock Alert',
    'license': 'OPL-1',
    'category': 'Extra Tools',
    'summary': '',
    'version': '15.0.0.1',
    'description' : 'The main purpose of this module is to send email  notification to the inventory manager about low stock avaliability. '
                    'Plus add Interface to see list of all products that have stock bellow min qty : Sales/Products/Stock Bellow Min',

    'author': 'ENSWORK',
    'website': 'https://www.enswork.com/',
    'depends': ['base', 'product', 'mail', 'stock'],
    'data': [
        'views/stock_bellow_min_tree.xml',
        'views/product_view.xml',
        'templates/email_template.xml',
        'views/ir_cron.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,

}

