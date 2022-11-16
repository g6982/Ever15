# -*- coding: utf-8 -*-
# © 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# © 2013 Camptocamp SA (author: Guewen Baconnier)
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Order Sequence Separation ',
    'version': '15.0',
    'category': 'Sales Management',
    'description': """
    This Module allows you to differentiate between the numbering of the Quotation and the Sale Order
    """,
    'license': 'AGPL-3',
    'author': "Odoo Tips, Othmane Ghandi, Mouad GHANDI",
    'images': ['images/main_screenshot.png'],
    'website': '',
    'depends': ['sale', 'sale_management'],
    'data': [
        'data/ir_sequence_data.xml',
        'views/sale_view.xml',
    ],
    'installable': True,
}
