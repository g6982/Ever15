# -*- coding: utf-8 -*-pack
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{

    # App information
    'name': 'DHL Express Shipping Integration',
    'category': 'Website',
    'version': '15.0.28.10.2021',
    'summary': """""",
    'description': """Using DHL EXPRESS Easily manage Shipping Operation in odoo.Export Order While Validate Delivery Order.Import Tracking From dhl to odoo.Generate Label in odoo.We also Provide the fedex,dhl parcel shipping integration.""",
    'license': 'OPL-1',

    # Dependencies
    'depends': ['delivery'],

    # Views
    'data': [
        'views/res_company.xml',
        'views/delivery_carrier_view.xml'],

    # Odoo Store Specific
    'images': ['static/description/cover.jpg'],

    # Author
    'author': 'Vraja Technologies',
    'website': 'https://www.vrajatechnologies.com',
    'maintainer': 'Vraja Technologies',

    # Technical
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'live_test_url': 'https://www.vrajatechnologies.com/contactus',
    'price': '99',
    'currency': 'EUR',

}

# version changelog
# 15.0.28.10.2021 #__ Initial version of the app(Migrate from odoo v14 By Shyam7636)

